#!/usr/bin/python3

import os
from optparse import OptionParser
from classes.builder import Builder
from classes.config import Config
from classes.messageprinter import MessagePrinter
from classes.repo import Repo

from classes.buildorder import BuildOrder


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

buildorder = BuildOrder(config.skip_directories)

repopath = options.target + '/' + config.reponame + '/os/' + options.arch

repo = Repo(repopath, config.reponame)

pkgbases = buildorder.pkgbase_in_buildorder

MessagePrinter.print_msg('Unexpected files in repo: ' +
                         str(repo.get_unexpected_files(pkgbases, options.arch).__len__()))
for unexpected_file in repo.get_unexpected_files(pkgbases, options.arch):
    repo.remove_file(unexpected_file)

MessagePrinter.print_msg('Unexpected files in db: ' +
                         str(repo.get_unexpected_dbfiles(pkgbases).__len__()))
for unexpected_dbfile in repo.get_unexpected_dbfiles(pkgbases):
    repo.remove_dbfile(unexpected_dbfile)

MessagePrinter.print_msg('Missing signature files: ' +
                         str(repo.get_missing_sigfiles(pkgbases, options.arch).__len__()))

MessagePrinter.print_msg('Unfinished pkgbases: ' +
                         str(repo.get_unfinished_pkgbases(pkgbases, options.arch).__len__()))

if repo.get_unfinished_pkgbases(pkgbases, options.arch).__len__() > 0:
    builder = Builder(repopath, config.reponame, options.arch)

while repo.get_unfinished_pkgbases(pkgbases, options.arch).__len__() > 0:
    current_pkgbase = repo.get_unfinished_pkgbases(pkgbases, options.arch)[0]
    builder.build(current_pkgbase)
    builder.move_to_repo(current_pkgbase, repo)

for missing_signature in repo.get_missing_sigfiles(pkgbases, options.arch):
    repo.sign_file(missing_signature)
