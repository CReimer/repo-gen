import os
import re
import subprocess
from classes.messageprinter import MessagePrinter


class Repo:
    def __init__(self, dirname, config, arch):
        name = config.reponame
        self.config = config
        self.repopath = dirname
        self.reponame = name
        self.arch = arch
        self.compression = 'gz'
        self.dbfileext = '.tar.' + self.compression
        self.dbfile = dirname + '/' + name + '.db' + self.dbfileext

        self.pkglist = []

        self.parse()

    def parse(self):
        if not os.path.exists(self.repopath):
            os.makedirs(self.repopath)

        # self.__parse_db()
        self.__parse_repodir()

    # def __parse_db(self):
    #     self.dbpkglist = []
    #     try:
    #         tar = tarfile.open(self.dbfile)
    #     except FileNotFoundError:
    #         MessagePrinter.print_warning("Cannot read " + self.dbfile)
    #         tar = tarfile.open(self.dbfile, 'w:' + self.compression)
    #         os.symlink(self.reponame + '.db' + self.dbfileext,
    #                    os.path.dirname(self.dbfile) + '/' + self.reponame + '.db')
    #
    #     names = tar.getnames()
    #     tar.close()
    #
    #     for name in names:
    #         if not re.search('/', name):
    #             self.dbpkglist.append(name)

    def __parse_repodir(self):
        self.pkglist = []

        for packagename in os.listdir(self.repopath):
            if packagename.endswith('.pkg.tar.xz'):
                self.pkglist.append(packagename)

    def remove_file(self, file):
        filepath = self.repopath + '/' + file
        try:
            os.remove(filepath)
        except OSError:
            MessagePrinter.print_warning("Cannot remove " + filepath)

        self.parse()

    def sign_file(self, filepath):
        if not self.config.sign:
            return
        source_path = self.repopath + '/' + re.split('(.*?)\.sig', filepath)[1]
        target_path = self.repopath + '/' + filepath
        if not os.path.isfile(target_path) or os.path.getmtime(target_path) < os.path.getmtime(source_path):
            subprocess.call(['gpg',
                             '--detach-sign',
                             '--yes',
                             source_path])

    def get_unsigned_files(self):
        temp_array = []
        for package in self.pkglist:
            if not os.path.isfile(self.repopath + '/' + package + '.sig'):
                temp_array.append(package)
        return temp_array

    def get_unexpected_files(self, pkgbases):
        expected_files = [self.reponame + '.db', self.reponame + '.db' + self.dbfileext,
                          self.reponame + '.files', self.reponame + '.files' + self.dbfileext,
                          self.reponame + '.db.sig', self.reponame + '.db' + self.dbfileext + '.sig',
                          self.reponame + '.files.sig', self.reponame + '.files' + self.dbfileext + '.sig']
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_pkgnames(self.arch) + pkgbase.get_expected_dbgnames(self.arch)
            expected_files += pkgbase.get_expected_pkgsignames(self.arch) + pkgbase.get_expected_dbgsignames(self.arch)

        temp_array = []
        for file in self.pkglist:
            if file not in expected_files:
                temp_array.append(file)

        MessagePrinter.print_msg2('Unexpected files in repo: ' +
                                  str(temp_array.__len__()))
        return temp_array

    def get_missing_files(self, pkgbases):
        expected_files = [self.reponame + '.db', self.reponame + '.db' + self.dbfileext,
                          self.reponame + '.files', self.reponame + '.files' + self.dbfileext,
                          self.reponame + '.db.sig', self.reponame + '.db' + self.dbfileext + '.sig',
                          self.reponame + '.files.sig', self.reponame + '.files' + self.dbfileext + '.sig']
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_pkgnames(self.arch)
            expected_files += pkgbase.get_expected_pkgsignames(self.arch)

        temp_array = []
        for file in expected_files:
            if file not in os.listdir(self.repopath):
                temp_array.append(file)

        MessagePrinter.print_msg2('Missing files in repo: ' +
                                  str(temp_array.__len__()))
        return temp_array

    def get_missing_sigfiles(self):
        if not self.config.sign:
            return []
        expected_files = []
        for file in self.pkglist:
            expected_files.append(file + '.sig')

        temp_array = []
        for file in expected_files:
            if file not in os.listdir(self.repopath):
                temp_array.append(file)

        MessagePrinter.print_msg2('Missing sigfiles in repo: ' +
                                  str(temp_array.__len__()))
        return temp_array

    def sign_db(self):
        if not self.config.sign:
            return
        expected_files = [self.reponame + '.db.sig', self.reponame + '.db' + self.dbfileext + '.sig',
                          self.reponame + '.files.sig', self.reponame + '.files' + self.dbfileext + '.sig']
        for file in expected_files:
            self.sign_file(file)

    def get_unfinished_pkgbases(self, pkgbases):
        temp_array = []
        for pkgbase in pkgbases:
            unfinished = False
            # Do not check for missing debug packages. There's no distinct indicator for when there is a debug package
            for file in pkgbase.get_expected_pkgnames(self.arch):
                if file not in self.pkglist:
                    unfinished = True
            if unfinished:
                temp_array.append(pkgbase)

        MessagePrinter.print_msg2('Unfinished pkgbases: ' +
                                  str(temp_array.__len__()))

        return temp_array
