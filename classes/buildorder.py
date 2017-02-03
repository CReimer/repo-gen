import glob
import os
from classes.srcpackage import SrcPackage


class BuildOrder:
    def __init__(self, config):
        pkgbase_by_name = {}
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
            self.pkgbases.append(pkgbase)

            provides = pkgbase.values['provides']

            for name in pkgbase.values['packages']:
                pkgbase_by_name[name] = pkgbase
                try:
                    provides += pkgbase.values['packages'][name]['provides']
                except KeyError:
                    continue

            for name in provides:
                pkgbase_by_name[name] = pkgbase

        buildorder = []
        pkgbase_by_name_copy = dict(pkgbase_by_name)

        while len(pkgbase_by_name_copy) > 0:
            for name in pkgbase_by_name_copy:
                pkgbase = pkgbase_by_name_copy[name]
                append = False
                only_external_deps = True
                for pkgname in pkgbase.values['depends'] + \
                        pkgbase.values['makedepends'] + \
                        pkgbase.values['checkdepends']:
                    if pkgname in pkgbase_by_name_copy.keys():
                        only_external_deps = False
                        if pkgname in buildorder:
                            append = True
                        else:
                            append = False
                if append or only_external_deps:
                    pkgbase_by_name_copy.pop(name)
                    buildorder.append(name)
                    if not pkgbase_by_name[name] in self.pkgbase_in_buildorder:
                        self.pkgbase_in_buildorder.append(pkgbase_by_name[name])
                    break
