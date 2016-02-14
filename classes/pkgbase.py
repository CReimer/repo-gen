class PkgBase:
    def __init__(self):
        self.name = ''
        self.srcdir = ''
        self.packages = []
        self.depends = []
        self.makedepends = []
        self.checkdepends = []

    @staticmethod
    def _uniq(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def add_depends(self, depends):
        self.depends.append(depends)
        self._uniq(self.depends)

    def add_makedepends(self, depends):
        self.makedepends.append(depends)
        self._uniq(self.makedepends)

    def add_checkdepends(self, depends):
        self.checkdepends.append(depends)
        self._uniq(self.checkdepends)

    def add_provides(self, provides):
        for package in self.packages:
            package.add_provides(provides)

    def set_name(self, name):
        self.name = name

    def set_srcdir(self, srcdir):
        self.srcdir = srcdir

    def append_package(self, package):
        self.packages.append(package)

    def set_pkgver(self, pkgver):
        for package in self.packages:
            package.set_pkgver(pkgver)

    def set_pkgrel(self, pkgrel):
        for package in self.packages:
            package.set_pkgrel(pkgrel)

    def set_epoch(self, epoch):
        for package in self.packages:
            package.set_epoch(epoch)

    def add_arch(self, arch):
        for package in self.packages:
            package.add_arch(arch)

    def get_expected_pkgnames(self, arch):
        temp_array = []
        for package in self.packages:
            expected_pkgname = package.get_expected_pkgname(arch)
            if expected_pkgname:
                temp_array.append(expected_pkgname)
        return temp_array

    def get_expected_dbgnames(self, arch):
        temp_array = []
        for package in self.packages:
            expected_pkgname = package.get_expected_dbgname(arch)
            if expected_pkgname:
                temp_array.append(expected_pkgname)
        return temp_array

    def get_expected_pkgsignames(self, arch):
        temp_array = []
        for package in self.packages:
            expected_pkgname = package.get_expected_pkgname(arch)
            if expected_pkgname:
                temp_array.append(expected_pkgname + '.sig')
        return temp_array

    def get_expected_dbgsignames(self, arch):
        temp_array = []
        for package in self.packages:
            expected_dbgname = package.get_expected_dbgname(arch)
            if expected_dbgname:
                temp_array.append(expected_dbgname + '.sig')
        return temp_array

    def get_expected_db_pkgnames(self):
        temp_array = []
        for package in self.packages:
            temp_array.append(package.get_expected_db_pkgname())
        return temp_array

    def get_expected_db_dbgnames(self):
        temp_array = []
        for package in self.packages:
            temp_array.append(package.get_expected_db_dbgname())
        return temp_array

    def get_pkgnames(self):
        temp_array = []
        for package in self.packages:
            temp_array.append(package.name)
        return temp_array

    def get_provides(self):
        temp_array = []
        for package in self.packages:
            temp_array = temp_array + package.provides
        return temp_array

    def get_srcdir(self):
        return self.srcdir
