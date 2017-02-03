from classes.repopackage import RepoPackage
from collections import OrderedDict
import os
import hashlib
import base64
import tarfile


class Package:
    def __init__(self, filename):
        self.filename = filename
        self.descmapping = OrderedDict([
            ("pkgname", "NAME"),
            ("pkgbase", "BASE"),
            ("pkgver", "VERSION"),
            ("pkgdesc", "DESC"),
            ("groups", "GROUPS"),
            ("size", "ISIZE"),
            ("url", "URL"),
            ("license", "LICENSE"),
            ("arch", "ARCH"),
            ("builddate", "BUILDDATE"),
            ("packager", "PACKAGER"),
            ("replaces", "REPLACES")
        ])
        self.dependsmapping = OrderedDict([
            ("depend", "DEPENDS"),
            ("conflict", "CONFLICTS"),
            ("provides", "PROVIDES"),
            ("optdepend", "OPTDEPENDS"),
            ("makedepend", "MAKEDEPENDS"),
            ("checkdepends", "CHECKDEPENDS")
        ])

        self.pkginfo = RepoPackage(filename)

    def get_depends_file(self):
        return_string = ''
        for key in self.dependsmapping:
            targetname = self.dependsmapping[key]
            try:
                values = self.pkginfo.values[key]
                return_string += '%' + targetname + '%\n'
                for value in values:
                    return_string += value + '\n'
                return_string += '\n'
            except KeyError:
                continue

        return return_string

    def get_desc_file(self):
        return_string = ''
        for key in self.descmapping:
            targetname = self.descmapping[key]
            try:
                values = self.pkginfo.values[key]
                return_string += '%' + targetname + '%\n'
                for value in values:
                    return_string += value + '\n'
                return_string += '\n'
            except KeyError:
                continue

        try:
            size = os.path.getsize(self.filename)
            return_string += '%CSIZE%\n'
            return_string += str(size) + '\n\n'

            md5 = hashlib.md5(open(self.filename, 'rb').read()).hexdigest()
            return_string += '%MD5SUM%\n'
            return_string += md5 + '\n\n'

            sha256 = hashlib.sha256(open(self.filename, 'rb').read()).hexdigest()
            return_string += '%SHA256SUM%\n'
            return_string += sha256 + '\n\n'
        except FileNotFoundError:
            exit(1)

        try:
            pgpsig = base64.b64encode(open(self.filename + '.sig', 'rb').read())
            return_string += '%PGPSIG%\n'
            return_string += pgpsig.decode() + '\n\n'
        except FileNotFoundError:
            pass

        return_string += '%FILENAME%\n'
        return_string += os.path.basename(self.filename)

        return return_string

    def get_files_file(self):
        return_string = '%FILES%\n'
        names = tarfile.open(self.filename).getnames()
        for name in names:
            if not name.startswith('.'):
                return_string += name + '\n'
        return return_string

    def get_dbname(self):
        return "%s-%s" % (self.pkginfo.values['pkgname'][0], self.pkginfo.values['pkgver'][0])
