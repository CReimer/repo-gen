import re
import os
import subprocess


class SrcPackage:
    def __init__(self, directory):
        self.__values = {
            'packages': {},
            'provides': [],
            'depends': [],
            'makedepends': [],
            'checkdepends': []
        }
        self.enqueued = False

        srcinfo_path = directory + '/.SRCINFO'
        pkgbuild_path = directory + '/PKGBUILD'
        if not os.path.isfile(srcinfo_path) or os.path.getmtime(srcinfo_path) < os.path.getmtime(pkgbuild_path):
            curdir = os.path.abspath('.')
            os.chdir(directory)
            subprocess.call(['mksrcinfo'])
            os.chdir(curdir)

        with open(srcinfo_path) as f:
            lines = f.readlines()
            targetobj = self.__values
            for line in lines:
                try:
                    try:
                        key = re.sub('\t', '', line.split('= ')[0].rstrip())
                    except TypeError:
                        key = line.split('= ')[0].rstrip()

                    value = line.split('= ')[1].rstrip()
                    if key == 'pkgname':
                        self.__values['packages'][value] = {}
                        targetobj = self.__values['packages'][value]
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

    def get_expected_pkgfile_names(self, _arch):
        temp_array = []

        try:
            epoch = self.__values['epoch'][0] + ':'
        except KeyError:
            epoch = ''

        for name in self.__values['packages']:
            try:
                arch = self.__values['packages'][name]['arch'][0]
            except KeyError:
                if self.__values['arch'][0] == 'any':
                    arch = 'any'
                elif _arch in self.__values['arch']:
                    arch = _arch
                else:
                    continue
            temp_array.append(
                "%s-%s%s-%s-%s.pkg.tar.xz" % (
                name, epoch, self.__values['pkgver'][0], self.__values['pkgrel'][0], arch))

        return temp_array

    def get_expected_dbgfile_names(self, _arch):
        temp_array = []

        try:
            epoch = self.__values['epoch'][0] + ':'
        except KeyError:
            epoch = ''

        for name in self.__values['packages']:
            try:
                arch = self.__values['packages'][name]['arch'][0]
            except KeyError:
                if self.__values['arch'][0] == 'any':
                    arch = 'any'
                else:
                    arch = _arch

            if not arch == 'any':
                temp_array.append(
                    "%s-debug-%s%s-%s-%s.pkg.tar.xz" % (
                        name, epoch, self.__values['pkgver'][0], self.__values['pkgrel'][0], arch))

        return temp_array

    def get_expected_pkgsigfile_names(self, arch):
        temp_array = []
        for name in self.get_expected_pkgfile_names(arch):
            temp_array.append(name + '.sig')
        return temp_array

    def get_expected_dbgsigfile_names(self, arch):
        temp_array = []
        for name in self.get_expected_dbgfile_names(arch):
            temp_array.append(name + '.sig')
        return temp_array

    def get_packages(self):
        return list(self.__values['packages'].keys())

    def get_provides(self):
        provides = self.__values['provides']
        for package in self.__values['packages'].keys():
            try:
                for provide in self.__values['packages'][package]['provides']:
                    provides.append(provide)

            except KeyError:
                continue
        return provides

    def get_depends(self):
        return self.__values['depends'] + self.__values['makedepends'] + self.__values['checkdepends']

    def get_pkgbase(self):
        return self.__values['pkgbase'][0]
