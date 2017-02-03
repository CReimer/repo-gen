import glob
import os
from classes.srcpackage import SrcPackage
from collections import OrderedDict


class CircularDepException(Exception):
    pass


class BuildOrder:
    def __init__(self, config):
        self.__pkgbase_by_name = OrderedDict()
        self.pkgbase_in_buildorder = []

        pkgbuilds = []
        if len(config.only_directories) > 0:
            for directory in config.only_directories:
                pkgbuilds += glob.glob(directory + '/**/PKGBUILD', recursive=True)
        else:
            pkgbuilds += glob.glob('./**/PKGBUILD', recursive=True)

        for filename in pkgbuilds:
            skip = False
            for skip_directory in config.skip_directories:
                if filename.startswith('./' + skip_directory):
                    skip = True
            if skip:
                continue

            pkgbase = SrcPackage(os.path.dirname(filename))

            for name in pkgbase.get_packages() + pkgbase.get_provides():
                # We have provides in here. So one pkgname could be resolved by multiple pkgbases.
                try:
                    self.__pkgbase_by_name[name].append(pkgbase)
                except KeyError:
                    self.__pkgbase_by_name[name] = [pkgbase]

        for name in self.__pkgbase_by_name:
            for pkgbase in self.__pkgbase_by_name[name]:
                try:
                    self.pkgbase_in_buildorder += self.collect_dependencies(pkgbase)
                except CircularDepException as e:
                    for f in e.args[1]:
                        print(f.get_pkgbase() + ' --> ', end='')
                    print(e.args[0].get_pkgbase())

    def collect_dependencies(self, base_pkgbase, circular_reference=None):
        if circular_reference is None:
            circular_reference = []
        dependencies = []
        if base_pkgbase.enqueued:
            return []

        for dependency in base_pkgbase.get_depends():
            try:
                for pkgbase in self.__pkgbase_by_name[dependency]:
                    if pkgbase.enqueued:
                        continue  # It's already in the buildqueue so it's not interesting anymore
                    if pkgbase in circular_reference:
                        # We've been here before. Looks like we have a circular dependency here.
                        raise CircularDepException(pkgbase, circular_reference)
                    circular_reference.append(pkgbase)
                    dependencies += self.collect_dependencies(pkgbase, circular_reference)

            except KeyError:
                continue  # Everything that's not in this directory is expected to be already reachable for pacman
        dependencies.append(base_pkgbase)
        base_pkgbase.enqueued = True
        return dependencies
