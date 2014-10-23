#!/usr/bin/env python2.7

from __future__ import print_function
from os.path import join

import common as common

if __name__ == '__main__':
    local_config = common.LocalConfig()
    with open(join(local_config.basedir, 'PATH.sh'), 'w') as pathfile:
        pathfile.write('export BASEDIR={}\n'.format(local_config.basedir))
        pathfile.write('export PATH=${BASEDIR}/local/bin:$PATH\n')
        pathfile.write('export LD_LIBRARY_PATH=${BASEDIR}/local/lib64:${BASEDIR}/local/lib:$LD_LIBRARY_PATH\n')
        pathfile.write(
            'export PKG_CONFIG_PATH=${BASEDIR}/local/lib64/pkgconfig:${BASEDIR}/local/lib/pkgconfig:${BASEDIR}/local/share/pkgconfig:$PKG_CONFIG_PATH\n')
        pathfile.write('export CC={CC}\n'.format(CC=local_config.cc))
        pathfile.write('export CXX={CXX}\n'.format(CXX=local_config.cxx))
        pathfile.write('export F77={F77}\n'.format(F77=local_config.f77))
        pathfile.write('export PYTHON_VERSION=2.7\n')
        pathfile.write('[ -e $BASEDIR/virtualenv/bin/activate ] && . $BASEDIR/virtualenv/bin/activate\n')
        pathfile.write('export SIMDB_PATH=$BASEDIR/DATA\n')
        pathfile.write('export SIMDB_GIT_REPOS=$BASEDIR/configs:$BASEDIR/dune-common:$BASEDIR/dune-fem:$BASEDIR/dune-gdt:$BASEDIR/dune-geometry:$BASEDIR/dune-grid:$BASEDIR/dune-grid-multiscale:$BASEDIR/dune-hdd:$BASEDIR/dune-istl:$BASEDIR/dune-localfunctions:$BASEDIR/dune-pdelab:$BASEDIR/dune-pymor:$BASEDIR/dune-stuff:$BASEDIR/dune-typetree:$BASEDIR/local/bin:$BASEDIR/pymor:$BASEDIR/simdb:$BASEDIR\n')
