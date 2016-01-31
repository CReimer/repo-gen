#!/usr/bin/python3

import os
import re
import subprocess
import tarfile
import tempfile
import shutil
from optparse import OptionParser


def print_plain(x):
    print(TermColor.BOLD + '    ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)


def print_msg(x):
    print(TermColor.BOLD_GREEN + '==> ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)


def print_msg2(x):
    print(TermColor.BOLD_BLUE + ' -> ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)


def print_warning(x):
    print(TermColor.BOLD_YELLOW + '==> ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)


def print_error(x):
    print(TermColor.BOLD_RED + '==> ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)


class TermColor:
    BOLD = '\033[1m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    RESET = '\033[0m'


class Config:
    def __init__(self, filename):

        self.list = []
        self.reponame = ''
        self.checkscript = ''

        f = open(filename)

        line = f.readline()
        while line:
            if not line.startswith('#') and not line.startswith('\n'):
                if line.startswith('REPONAME'):
                    self.reponame = re.split('=', line)[1].rstrip()
                elif line.startswith('CHECKSCRIPT'):
                    self.checkscript = re.split('=', line)[1].rstrip()
                else:
                    self.list.append(line.rstrip())

            line = f.readline()
        f.close()

    def get_list(self):
        return self.list


class SrcinfoParser:
    def __init__(self, dirname, arch):

        if not os.path.isfile(dirname + "/.SRCINFO"):
            current_dir = os.getcwd()
            os.chdir(dirname)
            subprocess.call('mksrcinfo')
            os.chdir(current_dir)

        f = open(dirname + '/.SRCINFO')

        self.pkgbase = PkgBase()
        self.pkgbase.set_srcdir(dirname)

        line = f.readline()

        currentpkg = ''

        while line:
            if line.startswith('pkgname'):
                currentpkg = Package()
                currentpkg.set_name(line.split('= ')[1].rstrip())
            elif not currentpkg == '' and line.startswith('\tarch'):
                currentpkg.set_arch(line.split('= ')[1].rstrip())
            elif not currentpkg == '' and line.startswith('\n'):
                self.pkgbase.append_package(currentpkg)
                currentpkg = ''

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
            elif line.startswith('\tarch = any'):
                self.pkgbase.set_arch('any')
            elif line.startswith('\tarch = ' + arch):
                self.pkgbase.set_arch(arch)

            line = f.readline()
        f.close()

    def get_pkgbase(self):
        return self.pkgbase


class Package:
    def __init__(self):

        self.name = ''
        self.arch = ''
        self.pkgver = ''
        self.pkgrel = ''
        self.epoch = ''

    def set_name(self, name):
        self.name = name

    def set_arch(self, arch):
        self.arch = arch

    def set_pkgver(self, pkgver):
        self.pkgver = pkgver

    def set_pkgrel(self, pkgrel):
        self.pkgrel = pkgrel

    def set_epoch(self, epoch):
        self.epoch = epoch + ':'

    def get_expected_pkgname(self):
        return "%s-%s%s-%s-%s.pkg.tar.xz" % (self.name, self.epoch, self.pkgver, self.pkgrel, self.arch)

    def get_expected_dbgname(self):
        if not self.arch == 'any':
            return "%s-debug-%s%s-%s-%s.pkg.tar.xz" % (self.name, self.epoch, self.pkgver, self.pkgrel, self.arch)

    def get_expected_db_pkgname(self):
        return "%s-%s%s-%s" % (self.name, self.epoch, self.pkgver, self.pkgrel)

    def get_expected_db_dbgname(self):
        if not self.arch == 'any':
            return "%s-debug-%s%s-%s" % (self.name, self.epoch, self.pkgver, self.pkgrel)


class PkgBase:
    def __init__(self):
        self.name = ''
        self.srcdir = ''
        self.packages = []

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

    def set_arch(self, arch):
        for package in self.packages:
            if package.arch == '':
                package.set_arch(arch)

    def get_expected_pkgnames(self):
        temp_array = []
        for package in self.packages:
            expected_pkgname = package.get_expected_pkgname()
            if expected_pkgname:
                temp_array.append(expected_pkgname)
        return temp_array

    def get_expected_dbgnames(self):
        temp_array = []
        for package in self.packages:
            expected_pkgname = package.get_expected_dbgname()
            if expected_pkgname:
                temp_array.append(expected_pkgname)
        return temp_array

    def get_expected_pkgsignames(self):
        temp_array = []
        for package in self.packages:
            expected_pkgname = package.get_expected_pkgname()
            if expected_pkgname:
                temp_array.append(expected_pkgname + '.sig')
        return temp_array

    def get_expected_dbgsignames(self):
        temp_array = []
        for package in self.packages:
            expected_dbgname = package.get_expected_dbgname()
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

    def get_srcdir(self):
        return self.srcdir


class Source:
    def __init__(self):

        self.pkgbases = []

    def read_srcdir(self, srclist, arch):
        for dirname in srclist:
            srcinfoparser = SrcinfoParser(dirname, arch)
            pkgbase = srcinfoparser.get_pkgbase()

            self.pkgbases.append(pkgbase)


class Builder:
    def __init__(self, _repopath, _reponame, _arch):
        self.repopath = _repopath
        self.reponame = _reponame
        self.arch = _arch

        self.tmp_name = "temporary-repo-gen-" + self.arch
        self.image_name = "repo-gen-" + self.arch

        subprocess.call(['docker', 'rm', self.tmp_name])
        subprocess.call(['docker', 'run', '--name=' + self.tmp_name, self.image_name, 'setarch', self.arch,
                         'pacman', '-Syu', '--noconfirm'])
        subprocess.call(['docker', 'commit', self.tmp_name, 'repo-gen'])
        subprocess.call(['docker', 'rm', self.tmp_name])

    def build(self, pkgbase):

            exitcode = subprocess.call(['docker', 'run', '--rm', '-i',
                                        '-v', os.path.abspath(pkgbase.get_srcdir()) + ':/startdir',
                                        '-v', os.path.abspath(self.repopath) + ':/pkgdest',
                                        self.image_name,
                                        'setarch', self.arch,
                                        'bash', '-c',
                                        'echo [' + self.reponame + '] >> /etc/pacman.conf;' +
                                        'echo SigLevel = Never >> /etc/pacman.conf;' +
                                        'echo Server = file:///pkgdest >> /etc/pacman.conf;' +
                                        'pacman -Sy --noconfirm;' +
                                        'su builduser -c "cd /startdir; makepkg -sfc --noconfirm"'
                                        ])

            if exitcode > 0:
                print_error("Build failed for " + pkgbase.name)
                exit()

    def move_to_repo(self, pkgbase, _repo):
            for filename in pkgbase.get_expected_pkgnames():
                _repo.add_file(self.repopath + '/' + filename)
            for filename in pkgbase.get_expected_dbgnames():
                try:
                    _repo.add_file(self.repopath + '/' + filename)
                except OSError:
                    print_warning("There's no debugfile: " + filename)


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
            print_warning("Cannot read " + self.dbfile)
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
        filepath = repopath + '/' + file
        try:
            os.remove(filepath)
        except OSError:
            print_warning("Cannot remove " + filepath)

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

    def get_unexpected_files(self, pkgbases):
        expected_files = [self.reponame + '.db', self.reponame + '.db.tar.gz',
                          self.reponame + '.files', self.reponame + '.files.tar.gz',
                          self.reponame + '.db.sig', self.reponame + '.db.tar.gz.sig',
                          self.reponame + '.files.sig', self.reponame + '.files.tar.gz.sig']
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_pkgnames() + pkgbase.get_expected_dbgnames()
            expected_files += pkgbase.get_expected_pkgsignames() + pkgbase.get_expected_dbgsignames()

        temp_array = []
        for file in self.pkglist:
            if file not in expected_files:
                temp_array.append(file)

        return temp_array

    def get_missing_files(self, pkgbases):
        expected_files = [self.reponame + '.db', self.reponame + '.db.tar.gz',
                          self.reponame + '.files', self.reponame + '.files.tar.gz',
                          self.reponame + '.db.sig', self.reponame + '.db.tar.gz.sig',
                          self.reponame + '.files.sig', self.reponame + '.files.tar.gz.sig']
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_pkgnames() + pkgbase.get_expected_dbgnames()
            expected_files += pkgbase.get_expected_pkgsignames() + pkgbase.get_expected_dbgsignames()

        temp_array = []
        for file in expected_files:
            if file not in self.pkglist:
                temp_array.append(file)

        return temp_array

    def get_missing_sigfiles(self, pkgbases):
        expected_files = [self.reponame + '.db.sig', self.reponame + '.db.tar.gz.sig',
                          self.reponame + '.files.sig', self.reponame + '.files.tar.gz.sig']
        for pkgbase in pkgbases:
            expected_files += pkgbase.get_expected_pkgsignames() + pkgbase.get_expected_dbgsignames()

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

    def get_unfinished_pkgbases(self, pkgbases):
        temp_array = []
        for pkgbase in pkgbases:
            unfinished = False
            for file in pkgbase.get_expected_pkgnames() + pkgbase.get_expected_dbgnames():
                if file not in self.pkglist:
                    unfinished = True
            if unfinished:
                temp_array.append(pkgbase)
        return temp_array

parser = OptionParser()
parser.add_option('-C', '--directory', dest="directory", default=os.getcwd(),
                  help="Change to directory before reading repo-make.conf or doing anything else.")
parser.add_option('-t', '--target', dest="target", default='./repo',
                  help="Sets the target path where the finished packages are placed to.")
parser.add_option('-a', '--arch', dest="arch", default='x86_64')

(options, args) = parser.parse_args()
os.chdir(os.path.abspath(options.directory))

config = Config('repo-make.conf')
reponame = config.reponame

repopath = os.path.abspath(options.target + '/' + config.reponame + '/os/' + options.arch)

packagelist = Source()
packagelist.read_srcdir(config.list, options.arch)
repo = Repo(repopath, reponame)

repo.get_missing_files(packagelist.pkgbases)

print_msg('Unexpected files in repo: ' +
          str(repo.get_unexpected_files(packagelist.pkgbases).__len__()))
for unexpected_file in repo.get_unexpected_files(packagelist.pkgbases):
    repo.remove_file(unexpected_file)

print_msg('Unexpected files in db: ' +
          str(repo.get_unexpected_dbfiles(packagelist.pkgbases).__len__()))
for unexpected_dbfile in repo.get_unexpected_dbfiles(packagelist.pkgbases):
    repo.remove_dbfile(unexpected_dbfile)

print_msg('Missing signature files: ' +
          str(repo.get_missing_sigfiles(packagelist.pkgbases).__len__()))

print_msg('Unfinished pkgbases: ' +
          str(repo.get_unfinished_pkgbases(packagelist.pkgbases).__len__()))

if repo.get_unfinished_pkgbases(packagelist.pkgbases).__len__() > 0:
    builder = Builder(repopath, reponame, options.arch)

while repo.get_unfinished_pkgbases(packagelist.pkgbases).__len__() > 0:
    current_pkgbase = repo.get_unfinished_pkgbases(packagelist.pkgbases)[0]
    builder.build(current_pkgbase)
    builder.move_to_repo(current_pkgbase, repo)

for missing_signature in repo.get_missing_sigfiles(packagelist.pkgbases):
    repo.sign_file(missing_signature)
