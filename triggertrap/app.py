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
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
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

''' Main module for the devops shell command. '''

import argparse
import os

import json
import logging

def cmd_line_parser():
    ''' Parse the command line options and return an args dict. '''
    parser = argparse.ArgumentParser(description=('Command line configuration '
                                                  'for EOS'))
    parser.add_argument('--cmdtimeout',
                        type=int,
                        default=60,
                        help='Timeout in secs for a single command to EOS')

    parser.add_argument('--config',
                        type=str,
                        default='/persist/sys/devops.conf',
                        help='Specifies the configuration file to load')

    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Send debug information to the console')

    parser.add_argument('--logfile',
                        type=str,
                        help='Specifies the file to log debug output to')

    # Hidden options used for testing
    # Values:
    #   parse_only   Only parse the command line.
    parser.add_argument('--test',
                        type=str,
                        default='',
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    return vars(args)

def main():
    ''' main execution routine for devops command. Parse the command
        line options, build the RESTful request, send it to stdlib,
        and then process the response.
    '''

    args = cmd_line_parser()

    if args['test'] == 'parse_only':
        return 0

    #default_config = Config()
    #conf = get_config(args['config'])
    logging.info("Started up successfully")


