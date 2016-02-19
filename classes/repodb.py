import os
import tarfile
import tempfile
import shutil
import re
from classes.package import Package
from classes.messageprinter import MessagePrinter


class Repodb:
    def __init__(self, path, name):
        self.compression = 'gz'
        self.path = path
        self.name = name

        self.tempdir = {'db': tempfile.mkdtemp(),
                        'files': tempfile.mkdtemp()}

        for dbtype in self.tempdir:
            tarpath = self.path + '/' + self.name + '.' + dbtype + '.tar.' + self.compression

            try:
                tar = tarfile.open(tarpath)
            except FileNotFoundError:
                MessagePrinter.print_warning("Cannot read " + tarpath)
                tar = tarfile.open(tarpath, 'w:' + self.compression)
            tar.extractall(self.tempdir[dbtype])
            tar.close()

    def finalize(self):
        for dbtype in self.tempdir:
            tarpath = self.path + '/' + self.name + '.' + dbtype + '.tar.' + self.compression
            os.remove(tarpath)
            tar = tarfile.open(tarpath, 'w:gz')

            for _file in os.listdir(self.tempdir[dbtype]):
                tar.add(self.tempdir[dbtype] + '/' + _file, recursive=True, arcname=_file)
            tar.close()

            symlinkpath = self.path + '/' + self.name + '.' + dbtype

            try:
                os.symlink(tarpath, symlinkpath)
            except FileExistsError:
                os.remove(symlinkpath)
                os.symlink(os.path.basename(tarpath), symlinkpath)

    def add_package(self, file):
        for dbtype in self.tempdir:
            package = Package(file)

            abs_path = self.tempdir[dbtype] + '/' + package.get_dbname()

            try:
                os.mkdir(abs_path)
            except FileExistsError:
                shutil.rmtree(abs_path)
                os.mkdir(abs_path)

            desc = open(abs_path + '/desc', 'w')
            desc.write(package.get_desc_file())
            desc.close()

            depends = open(abs_path + '/depends', 'w')
            depends.write(package.get_depends_file())
            depends.close()

            if dbtype == 'files':
                files = open(abs_path + '/files', 'w')
                files.write(package.get_files_file())
                files.close()

    def remove_package(self, dbfile):
        for dbtype in self.tempdir:
            dirname = self.tempdir[dbtype] + '/' + dbfile
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)

    def get_missing_sigfiles(self, filelist):
        dbtype = 'db'
        tarpath = self.path + '/' + self.name + '.' + dbtype + '.tar.' + self.compression
        tar = tarfile.open(tarpath)
        names = tar.getnames()

        pkgnames_by_dbnames = {}
        for file in filelist:
            if re.search('\.sig', file) or not re.search('\.pkg\.tar\.xz', file):
                continue

            dbname = re.match(r"(.*)(-.*?)", file).group(1)
            pkgnames_by_dbnames[dbname] = file

        db_files = []
        for name in names:
            if not re.search('/', name):
                db_files.append(name)

        temp_array = []
        for file in db_files:
            if 'PGPSIG' not in open(self.tempdir[dbtype] + '/' + file + '/desc').read():
                temp_array.append(pkgnames_by_dbnames[file])

        MessagePrinter.print_msg2('Missing signatures in database: ' +
                                  str(temp_array.__len__()))

        return temp_array

    def get_missing_files(self, filelist):
        dbtype = 'db'
        tarpath = self.path + '/' + self.name + '.' + dbtype + '.tar.' + self.compression
        tar = tarfile.open(tarpath)
        names = tar.getnames()

        temp_array = []
        for file in filelist:
            if re.search('\.sig', file) or not re.search('\.pkg\.tar\.xz', file):
                continue

            expected_file = re.match(r"(.*)(-.*?)", file).group(1)
            if expected_file not in names:
                temp_array.append(file)

        MessagePrinter.print_msg2('Missing files in database: ' +
                                  str(temp_array.__len__()))
        return temp_array

    def get_unexpected_files(self, filelist):
        dbtype = 'db'
        tarpath = self.path + '/' + self.name + '.' + dbtype + '.tar.' + self.compression
        tar = tarfile.open(tarpath)
        names = tar.getnames()

        db_files = []
        for name in names:
            if not re.search('/', name):
                db_files.append(name)

        expected_files = []
        for file in filelist:
            if not re.search('\.sig', file) and re.search('\.pkg\.tar\.xz', file):
                expected_files.append(re.match(r"(.*)(-.*?)", file).group(1))

        temp_array = []
        for file in db_files:
            if file not in expected_files:
                temp_array.append(file)

        MessagePrinter.print_msg2('Unexpected files in database: ' +
                                  str(temp_array.__len__()))

        return temp_array
