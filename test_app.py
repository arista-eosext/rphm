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

''' Test the devops command parsing. The command is executed using
    the os.system() call and the exit code is verified.
'''

import os
import unittest

class TestDevopsCmd(unittest.TestCase):
    ''' Test the devops command parsing. The command is executed using
        the os.system() call and the exit code is verified.
        The tests are data driven by a test table.
    '''

    def _run_tests(self, test_params):
        ''' Run a test for each entry in the test parameters list verifying
            that the actual results equal the expected results.
        '''
        cmd = 'bin/devops --test=parse_only'
        for i in range(len(test_params)):
            cmd_line, exp_ret_code = test_params[i]
            cmd_line = '%s %s' % (cmd, cmd_line)

            ret_code = os.system(cmd_line)

            # Build the error reporting string here and plug in params
            params = 'test params: %s' % test_params[i]
            mesg = '\n INCORRECT %%s\n  exp: %%s\n' \
                   ' actual: %%s\n %s' % params
            self.assertEqual(exp_ret_code, ret_code,
                mesg % ('Return Code', exp_ret_code, ret_code))

    def test_positive_optional_params(self):
        ''' Test optional command line parameters that should succeed '''

        # Test Table
        # cmd_line_param  exp_return_value
        #
        test_params = [
            ['--debug --protocol=http --host=tm203 --port=80 show vlans',
             0],
        ]
        self._run_tests(test_params)

if __name__ == '__main__':
    unittest.main()

