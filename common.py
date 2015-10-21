#!/usr/bin/env python

from __future__ import print_function
import os
from os.path import join
import logging
import subprocess
import sys
import itertools
from string import Template
from pprint import pprint
import shlex

VERBOSE = len(sys.argv) <= 1
logging.basicConfig()

class LocalConfig(object):
    def __init__(self):
        # define directories
        self.basedir = os.path.abspath(join(os.path.dirname(sys.argv[0]), '..', '..'))
        self.install_prefix = os.environ.get('INSTALL_PREFIX', join(self.basedir, 'local'))
        self.srcdir = join(self.install_prefix, 'src')
        try:
            os.makedirs(self.srcdir)
        except OSError as os_error:
            if os_error.errno != os.errno.EEXIST:
                raise os_error

        self.external_libraries_cfg_filename = join(self.basedir, 'external-libraries.cfg')
        self.dune_modules_cfg_filename = join(self.basedir, 'dune-modules.cfg')
        self.demos_cfg_filename = join(self.basedir, 'demos.cfg')

        self.cc = ''
        self.cxx = ''
        self.f77 = ''
        self.cxx_flags = ''
        self.config_opts_filename = ''
        self.boost_toolsets = {'gcc-{}.{}'.format(i, j): 'gcc' for i,j in itertools.product(range(4,7), range(10))}
        self.boost_toolsets.update({'icc': 'intel-linux', 'clang': 'clang'})
        self._parse_config_opts()

    def _parse_config_opts(self):
        # get CC from environment
        if not os.environ.has_key('CC'):
            raise Exception('ERROR: missing environment variable \'CC\'!')
        self.config_opts = self._get_config_opts(os.environ)

        # then read CC, CXX and F77
        def find_opt(string, default):
            cc = os.environ.get(string, default)
            tokens = list(shlex.shlex(self.config_opts, posix=True))
            for i, possible in enumerate(tokens):
                if possible == string:
                    return tokens[i+2]
            return cc

        self.cc = find_opt('CC', default='gcc')
        self.cxx = find_opt('CXX', default='g++')
        self.f77 = find_opt('F77', default='gfortran')

    def _try_opts(self, env):
        cc = os.path.basename(env['CC'])
        search_dirs = (self.basedir, join(self.basedir, 'opts'), join(self.basedir, 'config.opts'))
        prefixes = ('config.opts.', '',)
        for filename in (join(dirname, pref + cc) for dirname, pref in
                         itertools.product(search_dirs, prefixes)):
            try:
                return filename, open(filename).read()
            except IOError:
                continue
        else:
            raise IOError('No suitable opts file for CC {} in anyof {} x {}'.format(cc, search_dirs, prefixes))


    def _get_config_opts(self, env):
        try:
            self.config_opts_filename, config_opts = env['OPTS'], open(env['OPTS']).read()
        except (IOError, KeyError):
            self.config_opts_filename, config_opts = self._try_opts(env)

        def _extract_from(parts, flag_arg):
            configure_flags = parts[i + 2]
            for arg in [f for f in shlex.split(configure_flags, posix=True) if f != '\n']:
                if arg.startswith(flag_arg):
                    self.cxx_flags = shlex.split(arg[2:], posix=True)[2].join(' ')
                    return ' '.join(configure_flags)

        parts = list(shlex.shlex(config_opts, posix=True))
        for i, token in enumerate(parts):
            if token == 'CONFIGURE_FLAGS':
                flag_arg = 'CXXFLAGS'
                return _extract_from(parts, flag_arg)
            if token == 'CMAKE_FLAGS':
                flag_arg = '-DCMAKE_CXX_FLAGS'
                return _extract_from(parts, flag_arg)
        raise Exception('found neither CMAKE_FLAGS nor CONFIGURE_FLAGS in opts file {}'.format(self.config_opts_filename))


    def make_env(self):
        env = os.environ.copy()
        env['CC'] = self.cc
        env['CXX'] = self.cxx
        env['F77'] = self.f77
        env['CXXFLAGS'] = self.cxx_flags
        env['basedir'] = self.basedir
        env['BASEDIR'] = self.basedir
        env['SRCDIR'] = self.srcdir
        env['INSTALL_PREFIX'] = self.install_prefix
        env['BOOST_TOOLSET'] = self.boost_toolsets.get(os.path.basename(self.cc), 'gcc')
        env['BOOST_ROOT'] = env['INSTALL_PREFIX']
        path = join(self.install_prefix, 'bin')
        if 'PATH' in env:
            path += ':' + env['PATH']
        env['PATH'] = path
        ld_library_path = join(self.install_prefix, 'lib')
        if 'LD_LIBRARY_PATH' in env:
            ld_library_path += ':' + env['LD_LIBRARY_PATH']
        env['LD_LIBRARY_PATH'] = ld_library_path
        pkg_config_path = join(self.install_prefix, 'lib', 'pkgconfig')
        if 'PKG_CONFIG_PATH' in env:
            pkg_config_path += ':' + env['PKG_CONFIG_PATH']
        env['PKG_CONFIG_PATH'] = pkg_config_path
        return env

    def command_sep(self):
        return '\n'


def _prep_build_command(verbose, local_config, build_command):
    build_command = build_command.lstrip().rstrip()
    if not (build_command[0] == '\'' and build_command[-1] == '\''):
        if verbose:
            print('build commands have to be of the form \'command_1\' (is {cmd}), aborting!'.format(cmd=build_command))
    build_command = Template(build_command[1:-1].lstrip().rstrip())
    subst = local_config.make_env()
    build_command = build_command.substitute(subst)
    return build_command


def get_logger(name=__file__):
    log = logging.getLogger(name)
    log_lvl = logging.DEBUG if VERBOSE else logging.INFO
    log.setLevel(log_lvl)
    return log


def process_commands(local_config, commands, cwd):
    ret = 0
    log = get_logger('process_commands')
    for build_command in commands.split(local_config.command_sep()):
        build_command = _prep_build_command(VERBOSE, local_config, build_command)
        log.debug('  calling \'{build_command}\':'.format(build_command=build_command))
        with open(os.devnull, "w") as devnull:
            err = sys.stderr if VERBOSE else devnull
            out = sys.stdout if VERBOSE else devnull
            ret += subprocess.call(build_command,
                                   shell=True,
                                   env=local_config.make_env(),
                                   cwd=cwd,
                                   stdout=out,
                                   stderr=err)
        if ret != 0:
            return not bool(ret)
    return not bool(ret)
