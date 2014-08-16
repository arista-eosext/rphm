# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# Copyright (c) 2014, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

''' The setup script is the center of all activity in building,
    distributing, and installing modules using the Distutils. The
    main purpose of the setup script is to describe your module
    distribution to the Distutils, so that the various commands
    that operate on your modules do the right thing.
'''

import os

from glob import glob
#from distutils.core import setup
from setuptools import setup, find_packages

from triggertrap import __version__, __author__

def find_modules(pkg):
    ''' Find the modules that belong in this package. '''
    modules = [pkg]
    for dirname, dirnames, _ in os.walk(pkg):
        for subdirname in dirnames:
            modules.append(os.path.join(dirname, subdirname))
    return modules

INSTALL_ROOT = os.getenv('VIRTUAL_ENV', '')
CONF_PATH = INSTALL_ROOT + '/persist/sys'
#INSTALL_REQUIREMENTS = open('requirements.txt').read().split('\n')
INSTALL_REQUIREMENTS = [
    'jsonrpclib'
    ]

TEST_REQUIREMENTS = [
    'mock'
    ]


setup(
      name='triggertrap',
      version=__version__,
      description='EOS extension to generate SNMP traps based on counter thresholds',
      long_description=open('README.md').read(),
      author=__author__,
      author_email='eosplus-dev@aristanetworks.com',
      url='http://eos.aristanetworks.com',
      license='BSD-3',
      install_requires=INSTALL_REQUIREMENTS,
      tests_require=TEST_REQUIREMENTS,
      packages=find_modules('triggertrap'),
      scripts=glob('bin/*'),
      data_files=[
          (CONF_PATH, ['conf/triggertrap.conf'])
      ]
)

