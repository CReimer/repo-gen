class Package:
    def __init__(self):

        self.name = ''
        self.arch = []
        self.pkgver = ''
        self.pkgrel = ''
        self.epoch = ''
        self.provides = []
        self.arch_any = False

    def set_name(self, name):
        self.name = name

    def add_arch(self, arch):
        if not self.arch_any:
            self.arch.append(arch)

    def add_provides(self, arch):
        self.provides.append(arch)

    def set_arch_any(self):
        self.arch_any = True
        self.arch = ['any']

    def set_pkgver(self, pkgver):
        self.pkgver = pkgver

    def set_pkgrel(self, pkgrel):
        self.pkgrel = pkgrel

    def set_epoch(self, epoch):
        self.epoch = epoch + ':'

    def get_expected_pkgname(self, arch):
        if self.arch[0] == 'any':
            arch = 'any'
        return "%s-%s%s-%s-%s.pkg.tar.xz" % (self.name, self.epoch, self.pkgver, self.pkgrel, arch)

    def get_expected_dbgname(self, arch):
        if not self.arch[0] == 'any':
            return "%s-debug-%s%s-%s-%s.pkg.tar.xz" % (self.name, self.epoch, self.pkgver, self.pkgrel, arch)

    def get_expected_db_pkgname(self):
        return "%s-%s%s-%s" % (self.name, self.epoch, self.pkgver, self.pkgrel)

    def get_expected_db_dbgname(self):
        if not self.arch == 'any':
            return "%s-debug-%s%s-%s" % (self.name, self.epoch, self.pkgver, self.pkgrel)
