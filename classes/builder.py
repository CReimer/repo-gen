import os
import subprocess
from classes.messageprinter import MessagePrinter


class Builder:
    def __init__(self, _repopath, _config, _arch, _directory):
        self.repopath = _repopath
        self.config = _config
        self.arch = _arch
        self.srcdir = _directory
        self.pkgcache = _directory + '/repo-gen-cache/' + _arch
        try:
            os.makedirs(self.pkgcache)
        except FileExistsError:
            pass

        self.tmp_name = "temporary-repo-gen-" + self.arch
        self.image_name = "repo-gen-" + self.arch

        fnull = open(os.devnull, 'w')
        subprocess.call(['docker', 'stop', self.tmp_name], stdout=fnull, stderr=subprocess.STDOUT)
        subprocess.call(['docker', 'rm', self.tmp_name], stdout=fnull, stderr=fnull)

        subprocess.call(['docker', 'run', '-t',
                         '-v', os.path.abspath(self.pkgcache) + ':/var/cache/pacman/pkg',
                         '--name=' + self.tmp_name, self.image_name, 'setarch', self.arch,
                         'bash', '-c',
                         'pacman -Syu --noconfirm; pacman -Sc --noconfirm'])

        subprocess.call(['bash', '-c',
                         'docker export ' + self.tmp_name + '|' +
                         'docker import - ' + self.image_name], stdout=fnull, stderr=subprocess.STDOUT)

        subprocess.call(['docker', 'rm', self.tmp_name], stdout=fnull, stderr=fnull)
        subprocess.call(['bash', '-c', "docker images --quiet --filter=dangling=true | " +
                                       "xargs --no-run-if-empty docker rmi"], stdout=fnull, stderr=subprocess.STDOUT)
        fnull.close()

    def build(self, pkgbase):
            MessagePrinter.print_msg('Building ' + pkgbase.directory)
            fnull = open(os.devnull, 'w')
            subprocess.call(['docker', 'rm', self.tmp_name], stdout=fnull, stderr=fnull)
            fnull.close()
            exitcode = subprocess.call(['docker', 'run', '--rm', '-t',
                                        '-v', os.path.abspath(self.pkgcache) + ':/var/cache/pacman/pkg',
                                        '-v', os.path.abspath(pkgbase.directory) + ':/startdir:ro',
                                        '-v', os.path.abspath(self.repopath) + ':/pkgdest',
                                        '--name=' + self.tmp_name,
                                        self.image_name,
                                        'setarch', self.arch,
                                        'bash', '-c',
                                        'echo [' + self.config.reponame + '] >> /etc/pacman.conf;' +
                                        'echo SigLevel = Never >> /etc/pacman.conf;' +
                                        'echo Server = file:///pkgdest >> /etc/pacman.conf;' +
                                        'pacman -Sy --noconfirm > /dev/null;' +
                                        'su builduser -c "cd /startdir; makepkg -sfc --noconfirm"'
                                        ])

            if exitcode > 0:
                MessagePrinter.print_error("Build failed for " + pkgbase.values['pkgbase'][0])
                exit(1)

    def move_to_repo(self, pkgbase, _repo):
            for filename in pkgbase.get_expected_pkgnames(self.arch):
                _repo.add_file(self.repopath + '/' + filename)
            for filename in pkgbase.get_expected_dbgnames(self.arch):
                try:
                    _repo.add_file(self.repopath + '/' + filename)
                except OSError:
                    MessagePrinter.print_warning("There's no debugfile: " + filename)
