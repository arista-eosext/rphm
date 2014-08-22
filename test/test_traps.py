#!/usr/bin/env python
#
# Copyright (c) 2014, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#  - Neither the name of Arista Networks nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
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

#pylint: disable=R0904,F0401,W0232,E1101

#sys.path.append(os.path.join('..', 'triggertrap'))
import unittest
from triggertrap import app


class StatMonTests(unittest.TestCase):
    """Unittests for triggertrap
    """

    def setUp(self):
        self.device = {'alignmenterrors': '1',
                       'authpassword': '',
                       'authprotocol': 'SHA',
                       'collisions': '1',
                       'community': 'public',
                       'contextname': '',
                       'counters': ['inUcastPkts', 'inDiscards'],
                       'deferredtransmissions': '1',
                       'fcserrors': '1',
                       'giantframes': '1',
                       'hostname': '10.10.10.11',
                       'indiscards': '1',
                       'interfaces': ['Management 1'],
                       'inucastpkts': '1',
                       'latecollisions': '1',
                       'name': 'vEOS-1',
                       'password': 'arista',
                       'port': '443',
                       'privpassword': '',
                       'privprotocol': 'AES',
                       'protocol': 'https',
                       'runtframes': '1',
                       'rxpause': '1',
                       'seclevel': 'authPriv',
                       'symbolerrors': '1',
                       'traphost': 'localhost',
                       'txpause': '1',
                       'url': 'https://arista:arista@10.10.10.11:443/command-api',
                       'username': 'arista',
                       'version': '2c'}

        self.reference = {'Management 1': {u'autoNegotiate': u'success',
                                         u'bandwidth': 100000000,
                                         u'burnedInAddress': u'08:00:27:72:f6:77',
                                         u'description': u'My mgmt descr',
                                         u'duplex': u'duplexFull',
                                         u'forwardingModel': u'routed',
                                         u'hardware': u'ethernet',
                                         u'interfaceAddress': [{u'broadcastAddress': u'255.255.255.255',
                                                                u'primaryIp': {u'address': u'10.10.10.11',
                                                                               u'maskLen': 24},
                                                                u'secondaryIps': {},
                                                                u'secondaryIpsOrderedList': []}],
                                         u'interfaceCounters': {u'counterRefreshTime': 1407725658.76,
                                                                u'inBroadcastPkts': 0,
                                                                u'inDiscards': 0,
                                                                u'inMulticastPkts': 0,
                                                                u'inOctets': 0,
                                                                u'inUcastPkts': 0,
                                                                u'inputErrorsDetail': {u'alignmentErrors': 0,
                                                                                       u'fcsErrors': 0,
                                                                                       u'giantFrames': 0,
                                                                                       u'runtFrames': 0,
                                                                                       u'rxPause': 0,
                                                                                       u'symbolErrors': 0},
                                                                u'linkStatusChanges': 3,
                                                                u'outBroadcastPkts': 0,
                                                                u'outDiscards': 0,
                                                                u'outMulticastPkts': 0,
                                                                u'outOctets': 0,
                                                                u'outUcastPkts': 0,
                                                                u'outputErrorsDetail': {u'collisions': 0,
                                                                                        u'deferredTransmissions': 0,
                                                                                        u'lateCollisions': 0,
                                                                                        u'txPause': 0},
                                                                u'totalInErrors': 0,
                                                                u'totalOutErrors': 0},
                                         u'interfaceStatistics': {u'inBitsRate': 0.0,
                                                                  u'inPktsRate': 0.0,
                                                                  u'outBitsRate': 0.0,
                                                                  u'outPktsRate': 0.0,
                                                                  u'updateInterval': 300.0},
                                         u'interfaceStatus': u'connected',
                                         u'lastStatusChangeTimestamp': 1407724637.35,
                                         u'lineProtocolStatus': u'up',
                                         u'mtu': 1500,
                                         u'name': u'Management1',
                                         u'physicalAddress': u'08:00:27:72:f6:77'}}
        self.current = {'Management 1': {u'autoNegotiate': u'success',
                                         u'bandwidth': 100000000,
                                         u'burnedInAddress': u'08:00:27:72:f6:77',
                                         u'description': u'My mgmt descr',
                                         u'duplex': u'duplexFull',
                                         u'forwardingModel': u'routed',
                                         u'hardware': u'ethernet',
                                         u'interfaceAddress': [{u'broadcastAddress': u'255.255.255.255',
                                                                u'primaryIp': {u'address': u'10.10.10.11',
                                                                               u'maskLen': 24},
                                                                u'secondaryIps': {},
                                                                u'secondaryIpsOrderedList': []}],
                                         u'interfaceCounters': {u'counterRefreshTime': 1407725658.76,
                                                                u'inBroadcastPkts': 0,
                                                                u'inDiscards': 0,
                                                                u'inMulticastPkts': 0,
                                                                u'inOctets': 0,
                                                                u'inUcastPkts': 0,
                                                                u'inputErrorsDetail': {u'alignmentErrors': 0,
                                                                                       u'fcsErrors': 0,
                                                                                       u'giantFrames': 0,
                                                                                       u'runtFrames': 0,
                                                                                       u'rxPause': 0,
                                                                                       u'symbolErrors': 0},
                                                                u'linkStatusChanges': 3,
                                                                u'outBroadcastPkts': 0,
                                                                u'outDiscards': 0,
                                                                u'outMulticastPkts': 0,
                                                                u'outOctets': 0,
                                                                u'outUcastPkts': 0,
                                                                u'outputErrorsDetail': {u'collisions': 0,
                                                                                        u'deferredTransmissions': 0,
                                                                                        u'lateCollisions': 0,
                                                                                        u'txPause': 0},
                                                                u'totalInErrors': 0,
                                                                u'totalOutErrors': 0},
                                         u'interfaceStatistics': {u'inBitsRate': 0.0,
                                                                  u'inPktsRate': 0.0,
                                                                  u'outBitsRate': 0.0,
                                                                  u'outPktsRate': 0.0,
                                                                  u'updateInterval': 300.0},
                                         u'interfaceStatus': u'connected',
                                         u'lastStatusChangeTimestamp': 1407724637.35,
                                         u'lineProtocolStatus': u'up',
                                         u'mtu': 1500,
                                         u'name': u'Management1',
                                         u'physicalAddress': u'08:00:27:72:f6:77'}}

        self.good_result = {'Management1': {u'inDiscards': {'found': 0, 'threshold': '1'},
                                            u'inUcastPkts': {'found': 0, 'threshold': '1'}}}

        self.equal_result = {}

    def test_remove_unneded_keys(self):
        input_dict = {'section 1': {'a': 0,
                                    'b': 1,
                                    'c': 2},
                      'section 2': {'a': 3,
                                    'b': 4,
                                    'c': 5}}
        extrakeys = ['a', 'c']
        expected_dict = {'section 1': {'b': 1},
                         'section 2': {'b': 4}}

        app.remove_unneded_keys(extrakeys, input_dict)

        self.assertEqual(input_dict, expected_dict)

    def test_compare_counters_equal(self):
        result = app.compare_counters(self.device, self.reference,
                                      self.reference)
        self.assertEqual(result, {})

    def test_compare_counters_missing_interface(self):
        current = dict(self.current)
        current.pop('Management 1')
        result = app.compare_counters(self.device, self.reference, current)
        self.assertEqual(result, {})

    def test_compare_counters_difference(self):
        device = dict(self.device)
        current = dict(self.current)

        #Add a counter to test and set a threshold for it.
        counter = 'giantFrames'
        device['counters'].append(counter)
        thresh = '1'
        # must be all lowercase due to ConfigParser
        device[counter.lower()] = thresh

        # Add a rnd number to the reference for that counter and store it
        #   in current.
        from random import randrange
        val = randrange(int(thresh), 20)
        print "Tried random increment of {0}".format(val)

        current['Management 1'][u'interfaceCounters'][u'inputErrorsDetail']\
            [counter] = int(self.reference['Management 1']\
                                   [u'interfaceCounters'][u'inputErrorsDetail']\
                                   [counter]) + val

        # Call the routine
        result = app.compare_counters(device, self.reference, current)
        self.assertEqual(result, {'Management 1': {counter: {'found': val, 'threshold': int(thresh)}}})

    def test_is_delta_significant_equal(self):
        device = dict(self.device)

        #Add a counter to test and set a threshold for it.
        counter = 'giantFrames'
        device['counters'].append(counter)
        thresh = '1'
        # must be all lowercase due to ConfigParser
        device[counter.lower()] = thresh

        from random import randrange
        val = randrange(20)
        print "Selected increment of {0}".format(val)

        # Call the routine
        result = app.is_delta_significant(device, counter, val, val)
        self.assertEqual(result, None)

    def test_is_delta_significant_invalid_counter_name(self):
        device = dict(self.device)

        #Add a counter to test and set a threshold for it.
        counter = 'giantFrogs'
        #device['counters'].append(counter)
        thresh = '1'
        # must be all lowercase due to ConfigParser
        device[counter.lower()] = thresh

        from random import randrange
        val = randrange(20)
        print "Selected increment of {0}".format(val)

        # Call the routine
        result = app.is_delta_significant(device, counter, val, val)
        self.assertEqual(result, None)

    def test_is_delta_significant_difference(self):
        device = dict(self.device)
        #current = dict(self.current)

        #Add a counter to test and set a threshold for it.
        counter = 'giantFrames'
        device['counters'].append(counter)
        thresh = '1'
        # must be all lowercase due to ConfigParser
        device[counter.lower()] = thresh

        # Add a rnd number to the reference for that counter and store it
        #   in current.
        from random import randrange
        val = randrange(int(thresh), 20)
        print "Selected increment of {0}".format(val)

        ref = int(self.reference['Management 1'][u'interfaceCounters']\
                  [u'inputErrorsDetail'][counter])
        cur = ref + val

        # Call the routine
        result = app.is_delta_significant(device, counter, ref, cur)
        self.assertEqual(result, {'found': val, 'threshold': int(thresh)})



class GetDataTests(unittest.TestCase):
    """Unittests for triggertrap
    """

    def setUp(self):
        """ Test the get_interfaces stuff
        """

        self.device = {'alignmenterrors': '1',
                       'authpassword': '',
                       'authprotocol': 'SHA',
                       'collisions': '1',
                       'community': 'public',
                       'contextname': '',
                       'counters': ['inUcastPkts', 'inDiscards'],
                       'deferredtransmissions': '1',
                       'fcserrors': '1',
                       'giantframes': '1',
                       'hostname': '10.10.10.11',
                       'indiscards': '1',
                       'interfaces': ['Management 1'],
                       'inucastpkts': '1',
                       'latecollisions': '1',
                       'name': 'vEOS-1',
                       'password': 'arista',
                       'port': '443',
                       'privpassword': '',
                       'privprotocol': 'AES',
                       'protocol': 'https',
                       'runtframes': '1',
                       'rxpause': '1',
                       'seclevel': 'authPriv',
                       'symbolerrors': '1',
                       'traphost': 'localhost',
                       'txpause': '1',
                       'url': 'https://arista:arista@10.10.10.11:443/command-api',
                       'username': 'arista',
                       'version': '2c'}

        self.reference = {'Management1': {u'autoNegotiate': u'success',
                                          u'bandwidth': 100000000,
                                          u'burnedInAddress': u'08:00:27:72:f6:77',
                                          u'description': u'My mgmt descr',
                                          u'duplex': u'duplexFull',
                                          u'forwardingModel': u'routed',
                                          u'hardware': u'ethernet',
                                          u'interfaceAddress': [{u'broadcastAddress': u'255.255.255.255',
                                                                 u'primaryIp': {u'address': u'10.10.10.11',
                                                                                u'maskLen': 24},
                                                                 u'secondaryIps': {},
                                                                 u'secondaryIpsOrderedList': []}],
                                          u'interfaceCounters': {u'counterRefreshTime': 1407725658.76,
                                                                 u'inBroadcastPkts': 0,
                                                                 u'inDiscards': 0,
                                                                 u'inMulticastPkts': 0,
                                                                 u'inOctets': 0,
                                                                 u'inUcastPkts': 0,
                                                                 u'inputErrorsDetail': {u'alignmentErrors': 0,
                                                                                        u'fcsErrors': 0,
                                                                                        u'giantFrames': 0,
                                                                                        u'runtFrames': 0,
                                                                                        u'rxPause': 0,
                                                                                        u'symbolErrors': 0},
                                                                 u'linkStatusChanges': 3,
                                                                 u'outBroadcastPkts': 0,
                                                                 u'outDiscards': 0,
                                                                 u'outMulticastPkts': 0,
                                                                 u'outOctets': 0,
                                                                 u'outUcastPkts': 0,
                                                                 u'outputErrorsDetail': {u'collisions': 0,
                                                                                         u'deferredTransmissions': 0,
                                                                                         u'lateCollisions': 0,
                                                                                         u'txPause': 0},
                                                                 u'totalInErrors': 0,
                                                                 u'totalOutErrors': 0},
                                          u'interfaceStatistics': {u'inBitsRate': 0.0,
                                                                   u'inPktsRate': 0.0,
                                                                   u'outBitsRate': 0.0,
                                                                   u'outPktsRate': 0.0,
                                                                   u'updateInterval': 300.0},
                                          u'interfaceStatus': u'connected',
                                          u'lastStatusChangeTimestamp': 1407724637.35,
                                          u'lineProtocolStatus': u'up',
                                          u'mtu': 1500,
                                          u'name': u'Management1',
                                          u'physicalAddress': u'08:00:27:72:f6:77'}}

        self.int_status = {u'Ethernet1': {u'autoNegotigateActive': False,
                                          u'bandwidth': 10000000000,
                                          u'description': u'',
                                          u'duplex': u'duplexFull',
                                          u'interfaceType': u'EbraTestPhyPort',
                                          u'linkStatus': u'connected',
                                          u'vlanInformation': {u'interfaceForwardingModel': u'bridged',
                                                               u'interfaceMode': u'bridged',
                                                               u'vlanId': 1}},
                           u'Ethernet2': {u'autoNegotigateActive': False,
                                          u'bandwidth': 10000000000,
                                          u'description': u'',
                                          u'duplex': u'duplexFull',
                                          u'interfaceType': u'EbraTestPhyPort',
                                          u'linkStatus': u'connected',
                                          u'vlanInformation': {u'interfaceForwardingModel': u'bridged',
                                                               u'interfaceMode': u'bridged',
                                                               u'vlanId': 1}}}

        self.counter_error = {"jsonrpc": "2.0",
                              "id": "CapiExplorer-123",
                              "error": {"data": [{"errors": ["Invalid input (at token 3: '1')"]}],
                                        "message": "CLI command 1 of 1 'show interfaces Mac 1' failed: invalid command",
                                        "code": 1002}
                             }

        self.sh_ver = {"modelName": "vEOS",
                       "internalVersion": "4.13.6F-1754895.4136F.1",
                       "systemMacAddress": "08:00:27:27:8a:18",
                       "serialNumber": "",
                       "memTotal": 1001208,
                       "bootupTimestamp": 1408034881.09,
                       "memFree": 15100,
                       "version": "4.13.6F",
                       "architecture": "i386",
                       "internalBuildId": "3372c53e-4d0d-4a40-9183-6051aa07c429",
                       "hardwareRevision": ""}

    def test_get_device_status_good(self):
        """ Test get_device_status happy path
        """
        from mock import MagicMock
        from jsonrpclib import Server
        device = dict(self.device)
        sh_ver = dict(self.sh_ver)

        # Arbitrary test valuse
        model = "Monkey-bot"
        timestamp = 1408034881.09

        sh_ver['modelName'] = model
        sh_ver['bootupTimestamp'] = timestamp
        response = []
        response.append(sh_ver)

        device['eapi_obj'] = Server('https://arista:arista@10.10.10.11:443/command-api')
        device['eapi_obj'].runCmds = MagicMock(return_value=response)

        #response = []
        #response.append({})
        #response[0][u'interfaceStatuses'] = self.int_status

        app.get_device_status(device)
        self.assertEqual(device['modelName'], model)
        self.assertEqual(device['bootupTimestamp'], timestamp)


    def test_get_interfaces_good(self):
        """ Test get_interfaces happy path
        """
        from mock import MagicMock
        from jsonrpclib import Server
        switch = Server('https://arista:arista@10.10.10.11:443/command-api')
        response = []
        response.append({})
        response[0][u'interfaceStatuses'] = self.int_status
        switch.runCmds = MagicMock(return_value=response)

        interfaces = app.get_interfaces(switch)
        self.assertEqual(interfaces, self.int_status)

    def test_get_intf_counters_default(self):
        """ Test get_intf_counters with no interface specified
        """
        from mock import MagicMock
        from jsonrpclib import Server
        switch = Server('https://arista:arista@10.10.10.11:443/command-api')
        response = []
        response.append({})
        response[0][u'interfaces'] = self.reference

        switch.runCmds = MagicMock(return_value=response)
        counters = app.get_intf_counters(switch)
        self.assertDictEqual(counters, self.reference['Management1'])

if __name__ == '__main__':
    unittest.main()

