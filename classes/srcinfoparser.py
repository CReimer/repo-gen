import os
import subprocess
from classes.package import Package
from classes.pkgbase import PkgBase


class SrcinfoParser:
    def __init__(self, filename):

        # TODO Timestamp check
        if not os.path.isfile(filename):
            current_dir = os.getcwd()
            os.chdir(os.path.dirname(filename))
            subprocess.call('mksrcinfo')
            os.chdir(current_dir)

        f = open(filename)

        self.pkgbase = PkgBase()
        self.pkgbase.set_srcdir(os.path.dirname(filename))

        line = f.readline()

        currentpkg = ''

        while line:
            if line.startswith('pkgname'):
                currentpkg = Package()
                currentpkg.set_name(line.split('= ')[1].rstrip())
            elif not currentpkg == '':
                if line.startswith('\tarch = any'):
                    currentpkg.set_arch_any()
                elif line.startswith('\n'):
                    self.pkgbase.append_package(currentpkg)
                    currentpkg = ''
                elif line.startswith('\tprovides'):
                    currentpkg.add_provides(line.split('= ')[1].rstrip())

            line = f.readline()

        f.seek(0)
        line = f.readline()

        while not line.startswith('pkgname'):
            if line.startswith('pkgbase'):
                self.pkgbase.set_name(line.split('= ')[1].rstrip())
            elif line.startswith('\tpkgver'):
                self.pkgbase.set_pkgver(line.split('= ')[1].rstrip())
            elif line.startswith('\tpkgrel'):
                self.pkgbase.set_pkgrel(line.split('= ')[1].rstrip())
            elif line.startswith('\tepoch'):
                self.pkgbase.set_epoch(line.split('= ')[1].rstrip())
            elif line.startswith('\tarch'):
                self.pkgbase.add_arch(line.split('= ')[1].rstrip())
            elif line.startswith('\tdepends'):
                self.pkgbase.add_depends(line.split('= ')[1].rstrip())
            elif line.startswith('\tmakedepends'):
                self.pkgbase.add_makedepends(line.split('= ')[1].rstrip())
            elif line.startswith('\tcheckdepends'):
                self.pkgbase.add_checkdepends(line.split('= ')[1].rstrip())
            elif line.startswith('\tprovides'):
                self.pkgbase.add_provides(line.split('= ')[1].rstrip())

            line = f.readline()
        f.close()

    def get_pkgbase(self):
        return self.pkgbase
