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

"""Main module for the triggertrap shell command.
"""

import argparse
import ConfigParser
import logging
from logging.handlers import SysLogHandler
import time

import os
import sys
import re
import json

from jsonrpclib import Server
from subprocess import call
import pprint


LOGGING_FACILITY = __name__
# EOS unix socket for syslog
SYSLOG = '/dev/log'
syslog_manager = None   #pylint: disable=C0103
log_level = 'DEBUG'   #pylint: disable=C0103
snmp_settings = None   #pylint: disable=C0103

SYSTEM_ID = None
def log(msg, level='info', error=False):
    """Logging facility setup.

    args:
        msg (str): The message to log.
        error (bool): Flag if this is an error condition.

    """
    if SYSTEM_ID:
        syslog_msg = '%s: %s' % (SYSTEM_ID, msg)
    else:
        syslog_msg = msg

    if error:
        print 'ERROR: %s' % syslog_msg

    if syslog_manager:
        send_log = 'syslog_manager.log.' + level + '(syslog_msg)'
        eval(send_log)

def parse_cmd_line():
    """Parse the command line options and return an args dict.

    Get any CLI options from the user.

    Returns:
        dict: A dictionary of CLI arguments.

    """
    parser = argparse.ArgumentParser(
        description=(
            'Poll switches with eAPI then send SNMP trap on changes in'
            ' interface error counters.'))

    parser.add_argument('--config',
                        type=str,
                        default='/persist/sys/triggertrap.conf',
                        help='Specifies the configuration file to load' + \
                        '(Default: /persist/sys/triggertrap.conf)'
                        )

    parser.add_argument('--log',
                        action='store',
                        default='WARNING',
                        choices=['debug', 'info', 'warning', 'error',
                                 'critical'],
                        help='Set logging level: debug, info, warning,' + \
                        ' error, critical (default: INFO)')
    # TODO: This is not being used at this time.   Need to fix.

    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Send debug information to the console')

    # Hidden options used for testing
    # Values:
    #   parse_only   Only parse the command line.
    #   get          Get one set of interface stats and dump to console.
    #   send         Send a test snmp trap.
    parser.add_argument('--test',
                        type=str,
                        default='',
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    global log_level
    # assuming level is bound to the string value obtained from the
    # command line argument. Convert to upper case to allow the user to
    # specify --log=DEBUG or --log=debug
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    log_level = args.log.upper()
    #logging.basicConfig(level=numeric_level)

    return vars(args)


def remove_unneded_keys(keys, this_dict):
    """Remove any key in the keys list from sections in this_dict.

    ConfigParser has a helpful way to specify defaults for keys.   However, it
    does so for every section in the config.  This removes some of the extra
    entries from the base config.

    Args:
        keys (list): List of keys to remove.
        this_dict (dict): A dictionary of dictionaries to be cleaned.

    Returns:
        Undefined: This acts on the dictionary passed, directly.

    """

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='debug')
    #print "cleaning up keys"
    for section in this_dict:
        #print "    cleaning up section {0}".format(section)
        for key in keys:
            #print "        looking for {0}".format(key)
            key = key.lower()
            if key in this_dict[section]:
                #print "        Found a match... deleting"
                #del this_dict[section][key]
                this_dict[section].pop(key, None)

def read_config(filename):
    """ Read the config file (Default: /mnt/persistent/triggertrap.conf)

    Read in settings from the config file.  The default:
        /mnt/persistent/triggertrap.conf, is set in parse_cli().

    Args:
        filename (str): The path to the config file.

    Returns:
        dict: A dictionary of configuration and switch definitions.

    """

    if not filename:
        filename = "/mnt/persistent/triggertrap.conf"

    setting = {}
    defaults = {
        'hostname': 'localhost',
        'protocol': 'https',
        'port': '443',
        'username': 'arista',
        'password': 'arista',
        'url': '%(protocol)s://%(username)s:%(password)s@%(hostname)s:%(port)s/command-api',
        'interfaceList': 'Management 1',
        'counterList': 'alignmentErrors',
        'traphost' : 'localhost',
        'version' : '2c',
        'community' : 'public',
        'secLevel' : 'authPriv',
        'contextName' : '',
        'authProtocol' : 'SHA',
        'authPassword' : '',
        'privProtocol' : 'AES',
        'privPassword' : '%(authPassword)s',
        'inUcastPkts' : '1',
        'inDiscards' : '1',
        'alignmentErrors' : '1',
        'fcsErrors' : '1',
        'giantFrames' : '1',
        'runtFrames' : '1',
        'rxPause' : '1',
        'symbolErrors' : '1',
        'collisions' : '1',
        'deferredTransmissions' : '1',
        'lateCollisions' : '1',
        'txPause' : '1'
    }
    switchkeys = (
        'hostname',
        'protocol',
        'port',
        'username',
        'password',
        'url',
        'interfaceList',
        'counterList',
        'inUcastPkts',
        'inDiscards',
        'alignmentErrors',
        'fcsErrors',
        'giantFrames',
        'runtFrames',
        'rxPause',
        'symbolErrors',
        'collisions',
        'deferredTransmissions',
        'lateCollisions',
        'txPause'
    )
    #config = ConfigParser.ConfigParser()
    #config = ConfigParser.SafeConfigParser()
    config = ConfigParser.SafeConfigParser(defaults)
    config.read(filename)

    #for section in ['DEFAULT', 'snmp', 'counters']:
    for section in ['switches', 'snmp', 'counters']:
        options = config.options(section)

        setting[section] = {}
        for option in options:
            setting[section][option] = config.get(section, option)


        # Remove standard sections so all we have left are switch customizations
        config.remove_section(section)

    # Clean up the switchOnly defaults that ConfigParser put in non-switch
    #   sections. There will still be other unnecessary entries based on the
    #   defaults but this is a little easier to read, now.
    remove_unneded_keys(switchkeys, setting)

    # Convert value of switchList to a python list
    # TODO: remove [default][switchList]


    # Any section remaining, should be a switch parameter override.
    setting['switches'] = []
    for section in config.sections():
        switch = {}
        #config.set(section, 'hostname', section)
        config.set(section, 'name', section)

        for option in config.options(section):
            #switch[option] = config.get(section, option, 0, defaults)
            switch[option] = config.get(section, option)

        # unmangle counterlist from a string to a list
        switch['counters'] = []
        for item in switch['counterlist'].split("\n"):
            switch['counters'].append(item.strip('," \t'))
        switch.pop('counterlist')

        setting['switches'].append(switch)

        # unmangle interfacelist from a string to a list
        switch['interfaces'] = []
        for item in switch['interfacelist'].split("\n"):
            switch['interfaces'].append(item.strip('," \t'))
        switch.pop('interfacelist')

        setting['switches'].append(switch)


    return setting

def get_interfaces(switch):
    """Get all of the interfaces on a switch.

    Get summary info on all of the interfaces in a switch and return a
        dictionary keyed on interface name.  NOTE: the interfaceIDs are
        missing the space between the interface type and the number.

    args:
        switch (object): A :class:`jsonrpclib` Server object

    returns:
        dict: Dictionary, keyed on interface name (without space), of interface
            summary information."

    Example:
        {u'Ethernet1': {u'autoNegotigateActive': False,
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
                                            u'vlanId': 1}}
    """

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='debug')
    response = switch.runCmds(1, ["show interfaces status"])
    #print"Interface Status: "
    #pprint.pprint(response[0])

    return response[0][u'interfaceStatuses']

def get_intf_counters(switch, interface="Management 1"):
    """Get interface details for an interface

    Get detailed information on the specified interface.

    args:
        switch (object): A :class:`jsonrpclib` Server object
        interface (str): A complete interface name to lookup.

    returns:
        dict: Dictionary, of detailed interface information/stats.

    example:
        {u'autoNegotiate': u'success',
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
         u'interfaceCounters': {u'counterRefreshTime': 1407407226.21,
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
         u'lastStatusChangeTimestamp': 1407387888.23,
         u'lineProtocolStatus': u'up',
         u'mtu': 1500,
         u'name': u'Management1',
         u'physicalAddress': u'08:00:27:72:f6:77'}}}

    """
    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='debug')
    response = switch.runCmds(1, ["show interfaces {0}".format(interface)])
    #pprint.pprint(response[0])
    return response[0][u'interfaces'][interface.replace(" ", "")]

def get_device_counters(device):
    """ Get counters from a device and return a dict of results

    """
    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='debug')

    counters = {}
    for interface in device['interfaces']:
        switch = Server(device['url'])
        get_interfaces(switch)
        counters[interface] = get_intf_counters(switch, interface=interface)

    return counters

def compare_counters(device, reference, current):
    """Compare the counters in 2 sets and return only differences

    Args:
        device (dict): A device config from the config_file
        reference (dict): The previous iteration's stats
        current (dict): The current iteration's stats

    Returns:
        dict: A dictionary of alert-able deltas for this device.

    """

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='debug')
    diffs = {}
    for interface in reference:
        log("Checking interface: {0}.".format(interface), level='debug')

        # Key interest areas: u'interfaceCounters' and u'interfaceStatistics'

        try:
            ref = reference[interface][u'interfaceCounters']
        except KeyError:
            log("Interface counters for [{0}] are not in reference dataset".format(interface))
            continue

        try:
            cur = current[interface][u'interfaceCounters']
        except KeyError:
            log("Interface counters for [{0}] are not in current dataset".format(interface))
            continue

        diffs[interface] = {}
        for key in ref:

            if key not in cur:
                log("Key [{0}] in Reference not found in Current data set".format(key))

            if type(ref[key]) is dict:
                for subkey in ref[key]:
                    if subkey not in cur[key]:
                        log("Key [{0}] in Reference not found in Current data set".format(subkey))
                    else:
                        if subkey not in device['counters']:
                            # This counter is in the list we're checking
                            continue
                        tmp = is_delta_significant(device,
                                                   subkey,
                                                   ref[key][subkey],
                                                   cur[key][subkey])
                        if tmp is not None:
                            diffs[interface][subkey] = tmp
            else:
                if key not in device['counters']:
                    # This counter is in the list we're checking
                    continue
                tmp = is_delta_significant(device,
                                           key,
                                           ref[key],
                                           cur[key])
                if tmp is not None:
                    diffs[interface][key] = tmp

        # Remove the interface entry if there were no results to report
        if not diffs[interface].keys():
            diffs.pop(interface)

    return diffs

def is_delta_significant(device, counter, ref, cur):
    """Verify whether the difference in a counter value, if any, between two
    checks is equal to or greater than the set rate threshold for that counter.

    If the delta of a counter between two readings is equal to or exceeds
        the threshold value for that counter in the device config, then
        send an SNMP trap.

    Args:
        device (dict): A device (switch) entry from the config file.
        counter (str): The name of the counter being checked
        ref (int): The reference value from the previous check
        cur (int): The current reading

    Returns:
        dict: The counter containing the threshold and delta found
            or None if the threshold was not exceeded.

    Example:
        {'collisions': {'threshold': 2,
                        'found': 4}}

    """

    log("Comparing {0}[{1}]: REF [{2}], CUR [{3}]. "
        "expecting < {4}".format(device['name'], counter, ref, cur,
                                 device[counter.lower()]),
        level='debug')
    delta = cur - ref
    #if delta < int(device[counter.lower()]):
    if delta >= int(device[counter.lower()]):
        return {'threshold': device[counter.lower()],
                'found': delta}
    else:
        return None

def send_traps(device, changes, interval):
    """ Send SNMP traps for each delta noted in "changes"
    """

    for interface in changes:
        for counter in changes[interface]:
            send_trap(device, interface, counter, changes[interface], interval)

def send_trap(device, interface, counter, changes, interval, test=False):
    """ Send an SNMP trap

    """

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='debug')
    if test:
        call(["snmptrap", "-v", "2c", "-c", "eosplus", "localhost", "''",
              "NOTIFICATION-TEST-MIB::demo-notif", "SNMPv2-MIB::sysLocation.0",
              "s", "just here - v2"])

    trap_content = "Host {0}, interface {1}: {2} increasing at > {3}/{4}sec [{5}]"\
    .format(device['hostname'],
            interface,
            counter,
            changes[counter]['threshold'],
            interval,
            changes[counter]['found'])
    print "TRAP: %s" % trap_content

    enterprise_oid = '1.3.6.1.4.1.30065'
    generic_trapnum = 6
    specific_trapnum = 1
    trap_oid = '1.3.6.1.4.1.30065.0.1'
    print "Trapinfo: {0} {1} {2} {3}".format(enterprise_oid,
                                             generic_trapnum,
                                             specific_trapnum,
                                             trap_oid)

class SyslogManager(object):

    def __init__(self):
        self.log = logging.getLogger(__name__)
        #logging.basicConfig(level=logging.DEBUG)
        global log_level
        level = log_level
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % level)
        logging.basicConfig(level=numeric_level)
        self.log.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('ERRMON - %(levelname)s: '
                                           '%(message)s')

        # syslog to localhost enabled by default, if we are on EOS
        if os.path.isfile('/mnt/flash/startup-config'):
            self._add_syslog_handler()

    #def setLevel(self, level):
    #    # assuming level is bound to the string value obtained from the
    #    # command line argument. Convert to upper case to allow the user to
    #    # specify --log=DEBUG or --log=debug
    #    numeric_level = getattr(logging, level.upper(), None)
    #    if not isinstance(numeric_level, int):
    #        raise ValueError('Invalid log level: %s' % level)
    #    logging.basicConfig(level=numeric_level)
    #    #handler.setLevel(level=logging.DEBUG)


    def _add_handler(self, handler, level=None):
        if level is None:
            #level = 'DEBUG'
            global log_level
            level = log_level

        try:
            handler.setLevel(logging.getLevelName(level))
        except ValueError:
            log('SyslogManager: unknown logging level (%s) - using '
                'log.DEFAULT instead' % level, error=True)
            handler.setLevel(logging.DEBUG)

        handler.setFormatter(self.formatter)
        self.log.addHandler(handler)

    def _add_syslog_handler(self):
        log('SyslogManager: adding localhost handler')
        self._add_handler(SysLogHandler(address=SYSLOG))

    def _add_file_handler(self, filename, level=None):
        log('SyslogManager: adding file handler (%s - level:%s)' %
            (filename, level))
        self._add_handler(logging.FileHandler(filename), level)

    def _add_remote_syslog_handler(self, host, port, level=None):
        log('SyslogManager: adding remote handler (%s:%s - level:%s)' %
            (host, port, level))
        self._add_handler(SysLogHandler(address=(host, port)), level)

    def add_handlers(self, handler_config):
        for entry in handler_config:
            match = re.match('^file:(.+)',
                             entry['destination'])
            if match:
                self._add_file_handler(match.groups()[ 0 ],
                                       entry['level'])
            else:
                match = re.match('^(.+):(.+)',
                                 entry['destination'])
                if match:
                    self._add_remote_syslog_handler(match.groups()[ 0 ],
                                                    int(match.groups()[ 1 ]),
                                                    entry['level'])
                else:
                    log('SyslogManager: Unable to create syslog handler for'
                        ' %s' % str(entry), error=True)

def main():
    ''' main execution routine for devops command. Parse the command
        line options, build the RESTful request, send it to stdlib,
        and then process the response.
    '''

    global syslog_manager
    global snmp_settings

    args = parse_cmd_line()
    syslog_manager = SyslogManager()


    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='debug')

    config = read_config(args['config'])

    snmp_settings = config['snmp']

    if args['test'] == 'parse_only':
        print "\nargs:"
        pprint.pprint(args)
        print "\nconfig:"
        pprint.pprint(config)
        return 0

    elif args['test'] == 'send':
        send_trap(test=True)
        return 0

    elif args['test'] == 'get':
        #logger.debug("Connecting to {config['switches'][0]['url']}")
        #logger.debug("Connecting to {0}".format(config['switches'][0]['url']))
        print"Connecting to {0}".format(config['switches'][0]['url'])
        switch = Server(config['switches'][0]['url'])
        counters = get_intf_counters(switch, interface="Management 1")
        print "\nTest=get: received the following counters from Management 1:"
        pprint.pprint(counters)
        print "Test=get: --------------------------\n"
        return 0

    log("Started up successfully", level='debug')

    reference = {}

    log("Getting baseline counters from each device.")
    for device in config['switches']:
        log("Connecting to {config['switches'][0]['url']}")
        reference[device['hostname']] = get_device_counters(device)

    # TODO: temporary for debugging
    with open('tmp_reference.json', 'w') as outfile:
        json.dump(reference, outfile)

    log("Entering main loop.")
    while True:
        log("---sleeping for {0} seconds.".format(config['counters']['poll']))
        time.sleep(int(config['counters']['poll']))

        for device in config['switches']:
            log("Polling {0}".format(device['name']))
            current = {}
            current = get_device_counters(device)
            changes = compare_counters(device, reference[device['hostname']], current)


            send_traps(device, changes, int(config['counters']['poll']))

        # Just once through for initial testing
        break

