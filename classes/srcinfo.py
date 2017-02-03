import re
import os


class Srcinfo:
    def __init__(self, filename):
        self.values = {
            'packages': {},
            'provides': [],
            'depends': [],
            'makedepends': [],
            'checkdepends': []
        }
        self.directory = os.path.dirname(filename)

        with open(filename) as f:
            lines = f.readlines()
            targetobj = self.values
            for line in lines:
                try:
                    try:
                        key = re.sub('\t', '', line.split('= ')[0].rstrip())
                    except TypeError:
                        key = line.split('= ')[0].rstrip()

                    value = line.split('= ')[1].rstrip()
                    if key == 'pkgname':
                        self.values['packages'][value] = {}
                        targetobj = self.values['packages'][value]
                        continue

                    if key in ['depends', 'makedepends', 'checkdepends', 'provides']:
                        try:
                            targetobj[key].append(re.sub('[><=].*', '', value))
                        except KeyError:
                            targetobj[key] = []
                            targetobj[key].append(re.sub('[><=].*', '', value))
                        continue

                    try:
                        targetobj[key].append(value)
                    except KeyError:
                        targetobj[key] = []
                        targetobj[key].append(value)
                except IndexError:
                    continue

    def get_expected_pkgnames(self, _arch):
        temp_array = []

        try:
            epoch = self.values['epoch'][0] + ':'
        except KeyError:
            epoch = ''

        for name in self.values['packages']:
            try:
                arch = self.values['packages'][name]['arch'][0]
            except KeyError:
                if self.values['arch'][0] == 'any':
                    arch = 'any'
                elif _arch in self.values['arch']:
                    arch = _arch
                else:
                    continue
            temp_array.append(
                "%s-%s%s-%s-%s.pkg.tar.xz" % (name, epoch, self.values['pkgver'][0], self.values['pkgrel'][0], arch))

        return temp_array

    def get_expected_dbgnames(self, _arch):
        temp_array = []

        try:
            epoch = self.values['epoch'][0] + ':'
        except KeyError:
            epoch = ''

        for name in self.values['packages']:
            try:
                arch = self.values['packages'][name]['arch'][0]
            except KeyError:
                if self.values['arch'][0] == 'any':
                    arch = 'any'
                else:
                    arch = _arch

            if not arch == 'any':
                temp_array.append(
                    "%s-debug-%s%s-%s-%s.pkg.tar.xz" % (
                        name, epoch, self.values['pkgver'][0], self.values['pkgrel'][0], arch))

        return temp_array

    def get_expected_pkgsignames(self, arch):
        temp_array = []
        for name in self.get_expected_pkgnames(arch):
            temp_array.append(name + '.sig')
        return temp_array

    def get_expected_dbgsignames(self, arch):
        temp_array = []
        for name in self.get_expected_dbgnames(arch):
            temp_array.append(name + '.sig')
        return temp_array
