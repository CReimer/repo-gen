#!/usr/bin/python3

import os
from optparse import OptionParser
from classes.builder import Builder
from classes.config import Config
from classes.messageprinter import MessagePrinter
from classes.repo import Repo
from classes.buildorder import BuildOrder
from classes.repodb import Repodb


parser = OptionParser()
parser.add_option('-C', '--directory', dest="directory", default=os.getcwd(),
                  help="Change to directory before reading repo-make.conf or doing anything else.")
parser.add_option('-t', '--target', dest="target", default='./repo',
                  help="Sets the target path where the finished packages are placed to.")
parser.add_option('-a', '--arch', dest="arch", default='x86_64')

(options, args) = parser.parse_args()
options.directory = os.path.abspath(options.directory)
os.chdir(options.directory)
options.target = os.path.abspath(options.target)


config = Config('repo-gen.json')

buildorder = BuildOrder(config)

for arch in ['i686', 'x86_64']:
    MessagePrinter.print_msg("Building packages for " + arch)

    repopath = options.target + '/' + config.reponame + '/os/' + arch
    pkgbases = buildorder.pkgbase_in_buildorder

    repo = Repo(repopath, config, arch)
    repo_unexpected = repo.get_unexpected_files(pkgbases)
    # repo_missing = repo.get_missing_files(pkgbases)
    repo_missingsig = repo.get_missing_sigfiles()
    repo_unfinished = repo.get_unfinished_pkgbases(pkgbases)

    for unexpected_file in repo_unexpected:
        repo.remove_file(unexpected_file)

    repodb = Repodb(repopath, config)
    repodb_unexpected = repodb.get_unexpected_files(repo.pkglist)
    repodb_missing = repodb.get_missing_files(repo.pkglist)
    # repodb_missingsig = repodb.get_missing_sigfiles(repo.pkglist)

    for missing_dbfile in repodb_missing:
        repodb.add_package(repopath + '/' + missing_dbfile)

    for unexpected_dbfile in repodb_unexpected:
        repodb.remove_package(unexpected_dbfile)

    repodb.finalize()

    builder = ''
    if repo_unfinished.__len__() > 0:
        builder = Builder(repopath, config, arch, options.directory)

    while repo_unfinished.__len__() > 0:
        current_pkgbase = repo_unfinished[0]
        builder.build(current_pkgbase)
        repo.parse()
        repo_unfinished = repo.get_unfinished_pkgbases(pkgbases)
        repodb_missing = repodb.get_missing_files(repo.pkglist)

        for missing_dbfile in repodb_missing:
            repodb.add_package(repopath + '/' + missing_dbfile)
        repodb.finalize()

    for missing_signature in repo.get_missing_sigfiles():
        repo.sign_file(missing_signature)

    repo.parse()
    for missing_dbfile in repodb.get_missing_sigfiles(repo.pkglist):
        repodb.add_package(repopath + '/' + missing_dbfile)
    repodb.finalize()
    repo.sign_db()
