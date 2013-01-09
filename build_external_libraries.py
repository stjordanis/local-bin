#!/usr/bin/env python

from __future__ import print_function
import ConfigParser
import os
from os.path import join
import subprocess
import sys

import common

filename = common.external_libraries_cfg_filename


def build_library(library, build_commands):
    src_dir = join(common.SRCDIR(), library)
    if not os.path.isdir(src_dir):
        raise Exception('\'{path}\' is not a directory (did you forget to run \'./local/bin/download_external_libraries.py\'?)!'.format(path=src_dir))
    for build_command in build_commands.split(','):
        build_command = build_command.lstrip().rstrip()
        if not (build_command[0] == '\'' and build_command[-1] == '\''):
            raise Exception('build commands have to be of the form \'command_1\' (is {cmd})!'.format(cmd=build_command))
        build_command = build_command[1:-1].lstrip().rstrip()
        build_command = build_command.replace('$BASEDIR', '{BASEDIR}'.format(BASEDIR=common.BASEDIR()))
        build_command = build_command.replace('$SRCDIR', '{SRCDIR}'.format(SRCDIR=common.SRCDIR()))
        build_command = build_command.replace('$CXXFLAGS', '\'{CXXFLAGS}\''.format(CXXFLAGS=common.CXXFLAGS()))
        build_command = build_command.replace('$CC', '{CC}'.format(CC=common.CC()))
        build_command = build_command.replace('$CXX', '{CXX}'.format(CXX=common.CXX()))
        build_command = build_command.replace('$F77', '{F77}'.format(F77=common.F77()))
#        build_command = build_command[1:-1].lstrip().rstrip().split()
#        for ii in range(len(build_command)):
#            build_command[ii] = build_command[ii].replace('$BASEDIR', '{BASEDIR}'.format(BASEDIR=common.BASEDIR()))
#            build_command[ii] = build_command[ii].replace('$SRCDIR', '{SRCDIR}'.format(SRCDIR=common.SRCDIR()))
#            build_command[ii] = build_command[ii].replace('$CXXFLAGS', '{CXXFLAGS}'.format(CXXFLAGS=common.CXXFLAGS()))
#            build_command[ii] = build_command[ii].replace('$CC', '{CC}'.format(CC=common.CC()))
#            build_command[ii] = build_command[ii].replace('$CXX', '{CXX}'.format(CXX=common.CXX()))
#            build_command[ii] = build_command[ii].replace('$F77', '{F77}'.format(F77=common.F77()))
        print('  calling \'{build_command}\':'.format(build_command=build_command))
        subprocess.call(build_command,
                        shell=True,
                        cwd=src_dir,
                        stdout=sys.stdout,
                        stderr=sys.stderr)
# build_library

# main
print('reading \'{filename}\': '.format(filename=filename.split('/')[-1]), end='')
config = ConfigParser.ConfigParser()
try:
    config.readfp(open(filename))
except:
    raise Exception('Could not open \'{filename}\' with configparser!'.format(filename=filename))
libraries = config.sections()
if len(libraries) == 0:
    print(' no external libraries specified')
    exit
else:
    for library in libraries:
        print(library + ' ', end='')
    print('')

for library in libraries:
    print(library + ':')
    if not config.has_option(library, 'build'):
        raise Exception('missing \'build=\'list_of\', \'some_commands\'\' in section \'{library]\''.format(library=library))
    build_library(library, config.get(library, 'build'))

## eigen
#print('building eigen:')
#common.extract_in_srcdir('eigen-3.1.0.tar.gz', 'eigen-eigen-ca142d0540d3', 'eigen')
#eigen_buildir = join(common.SRCDIR(), 'eigen', 'build')
#try:
#    os.mkdir(eigen_buildir)
#except OSError, os_error:
#    if os_error.errno != 17:
#        raise os_error
#eigen_cmake = ['cmake', '..',
#               '-DCMAKE_INSTALL_PREFIX=' + join(common.BASEDIR(), 'local'),
#               '-DCMAKE_CXX_COMPILER=' + common.CXX()]
#subprocess.call(eigen_cmake,
#                cwd=eigen_buildir,
#                stdout=sys.stdout, stderr=sys.stderr)
#subprocess.call(['make'],
#                cwd=eigen_buildir,
#                stdout=sys.stdout, stderr=sys.stderr)
#subprocess.call(['make', 'install'],
#                cwd=eigen_buildir,
#                stdout=sys.stdout, stderr=sys.stderr)
