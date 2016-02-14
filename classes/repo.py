import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from classes.messageprinter import MessagePrinter


class Repo:
    def __init__(self, dirname, name):
        self.repopath = dirname
        self.reponame = name
        self.dbfile = dirname + '/' + name + '.db.tar.gz'

        self.dbpkglist = []
        self.pkglist = []

        self.parse()

    def parse(self):
        if not os.path.exists(self.repopath):
            os.makedirs(self.repopath)

        self.__parse_db()
        self.__parse_repodir()

    def __parse_db(self):
        self.dbpkglist = []
        try:
            tar = tarfile.open(self.dbfile)

            names = tar.getnames()
            tar.close()

            for name in names:
                if not re.search('/', name):
                    self.dbpkglist.append(name)
        except IOError:
            MessagePrinter.print_warning("Cannot read " + self.dbfile)
            tar = tarfile.open(self.dbfile, 'w:gz')
            tar.close()
            os.symlink(self.reponame + '.db.tar.gz', os.path.dirname(self.dbfile) + '/' + self.reponame + '.db')

            self.__parse_db()

    def __parse_repodir(self):
        self.pkglist = []

        for packagename in os.listdir(self.repopath):
            self.pkglist.append(packagename)

    def remove_dbfile(self, dbfile):
        tempdir = tempfile.mkdtemp()
        tar = tarfile.open(self.dbfile)
        tar.extractall(tempdir)
        tar.close()

        dirname = tempdir + '/' + dbfile
        if os.path.isdir(dirname):
            shutil.rmtree(dirname)

        os.remove(self.dbfile)
        tar = tarfile.open(self.dbfile, 'w:gz')

        for file in os.listdir(tempdir):
            tar.add(tempdir + '/' + file, recursive=True, arcname=file)
        tar.close()

    def remove_file(self, file):
        filepath = self.repopath + '/' + file
        try:
            os.remove(filepath)
        except OSError:
            MessagePrinter.print_warning("Cannot remove " + filepath)

        self.parse()

    def add_file(self, filepath):
        # os.rename(filepath, self.repopath + '/' + os.path.basename(filepath))

        subprocess.call(['repo-add',
                         self.dbfile,
                         self.repopath + '/' + os.path.basename(filepath)])

        self.parse()

    def sign_file(self, filepath):
        subprocess.call(['gpg',
                         '--detach-sign',
                         self.repopath + '/' + re.split('(.*?)\.sig', filepath)[1]])
        self.add_file(self.repopath + '/' + re.split('(.*?)\.sig', filepath)[1])

    def get_unsigned_files(self):
        temp_array = []
        for package in self.pkglist:
            if not os.path.isfile(self.repopath + '/' + package + '.sig'):
                temp_array.append(package)
        return temp_array

    def get_unexpected_files(self, pkgbases, arch):
        expected_files = [self.reponame + '.db', self.reponame + '.db.tar.gz',
                          self.reponame + '.files', self.reponame + '.files.tar.gz',
                          self.reponame + '.db.sig', self.reponame + '.db.tar.gz.sig',
                          self.reponame + '.files.sig', self.reponame + '.files.tar.gz.sig']
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_pkgnames(arch) + pkgbase.get_expected_dbgnames(arch)
            expected_files += pkgbase.get_expected_pkgsignames(arch) + pkgbase.get_expected_dbgsignames(arch)

        temp_array = []
        for file in self.pkglist:
            if file not in expected_files:
                temp_array.append(file)

        return temp_array

    def get_missing_files(self, pkgbases, arch):
        expected_files = [self.reponame + '.db', self.reponame + '.db.tar.gz',
                          self.reponame + '.files', self.reponame + '.files.tar.gz',
                          self.reponame + '.db.sig', self.reponame + '.db.tar.gz.sig',
                          self.reponame + '.files.sig', self.reponame + '.files.tar.gz.sig']
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_pkgnames(arch) + pkgbase.get_expected_dbgnames(arch)
            expected_files += pkgbase.get_expected_pkgsignames(arch) + pkgbase.get_expected_dbgsignames(arch)

        temp_array = []
        for file in expected_files:
            if file not in self.pkglist:
                temp_array.append(file)

        return temp_array

    def get_missing_sigfiles(self, pkgbases, arch):
        expected_files = [self.reponame + '.db.sig', self.reponame + '.db.tar.gz.sig',
                          self.reponame + '.files.sig', self.reponame + '.files.tar.gz.sig']
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_pkgsignames(arch) + pkgbase.get_expected_dbgsignames(arch)

        temp_array = []
        for file in expected_files:
            if file not in self.pkglist:
                temp_array.append(file)

        return temp_array

    def get_unexpected_dbfiles(self, pkgbases):
        expected_files = []
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_db_pkgnames() + pkgbase.get_expected_db_dbgnames()

        temp_array = []
        for file in self.dbpkglist:
            if file not in expected_files:
                temp_array.append(file)

        return temp_array

    def get_missing_dbfiles(self, pkgbases):
        expected_files = []
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_db_pkgnames() + pkgbase.get_expected_db_dbgnames()

        temp_array = []
        for file in expected_files:
            if file and file not in self.dbpkglist:
                temp_array.append(file)

        return temp_array

    def get_unfinished_pkgbases(self, pkgbases, arch):
        temp_array = []
        for pkgbase in pkgbases:
            unfinished = False
            for file in pkgbase.get_expected_pkgnames(arch) + pkgbase.get_expected_dbgnames(arch):
                if file not in self.pkglist:
                    unfinished = True
            if unfinished:
                temp_array.append(pkgbase)
        return temp_array
