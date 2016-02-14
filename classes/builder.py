import os
import subprocess
from classes.messageprinter import MessagePrinter


class Builder:
    def __init__(self, _repopath, _reponame, _arch):
        self.repopath = _repopath
        self.reponame = _reponame
        self.arch = _arch

        self.tmp_name = "temporary-repo-gen-" + self.arch
        self.image_name = "repo-gen-" + self.arch

        subprocess.call(['docker', 'rm', self.tmp_name])
        subprocess.call(['docker', 'run', '--name=' + self.tmp_name, self.image_name, 'setarch', self.arch,
                         'bash', '-c',
                         'pacman -Syu --noconfirm; pacman -Sc --noconfirm'])
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
                MessagePrinter.print_error("Build failed for " + pkgbase.name)
                exit()

    def move_to_repo(self, pkgbase, _repo):
            for filename in pkgbase.get_expected_pkgnames():
                _repo.add_file(self.repopath + '/' + filename)
            for filename in pkgbase.get_expected_dbgnames():
                try:
                    _repo.add_file(self.repopath + '/' + filename)
                except OSError:
                    MessagePrinter.print_warning("There's no debugfile: " + filename)
