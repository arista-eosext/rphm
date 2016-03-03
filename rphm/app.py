# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# Copyright (c) 2016, Arista Networks, Inc.
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

"""Main module for the rphm shell command.
"""

import argparse
import ConfigParser
import time
import os
import sys
import syslog
from pprint import pprint
from jsonrpclib import Server
from jsonrpclib import ProtocolError
from subprocess import call

SNMP_SETTINGS = None   #pylint: disable=C0103
DEBUG = False   #pylint: disable=C0103

class EapiException(Exception):
    """ An EapiException can be raised when there is a communication issue with
    Arista eAPI on a switch. This mechanism is used to skip switches that may
    not be accessible or configured properly, then automatically start
    accessing them once they become available instead of failing.
    """

    pass

def log(msg, level='INFO', error=False):
    """Logging facility setup.

    args:
        msg (str): The message to log.
        level (str): The priority level for the message. (Default: INFO)
                    See :mod:`syslog` for more options.
        error (bool): Flag if this is an error condition.

    """

    if error:
        level = "ERR"
        print "ERROR: {0} ({1}) {2}".format(os.path.basename(sys.argv[0]),
                                            level, msg)

    if DEBUG:
        # Print to console
        print "{0} ({1}) {2}".format(os.path.basename(sys.argv[0]), level, msg)
    else:
        if level == 'DEBUG':
            # Don't send DEBUG messages unless --debug was also set.
            return

    priority = ''.join(["syslog.LOG_", level])
    syslog.syslog(eval(priority), msg)

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
                        default='/persist/sys/rphm.conf',
                        help='Specifies the configuration file to load' + \
                        '(Default: /persist/sys/rphm.conf)'
                       )

    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Send debug information to the console')

    # Hidden options used for testing
    # Values:
    #   parse_only   Only parse the command line.
    #   get          Get one set of interface stats and dump to console.
    #   trap         Send a test snmp trap.
    #   snmp         Add random number to counters to rphm snmptraps
    #                  and display args sent to snmptrap command
    parser.add_argument('--test',
                        type=str,
                        default='',
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

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

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='DEBUG')
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
    """ Read the config file (Default: /persist/sys/rphm.conf)

    Read in settings from the config file.  The default:
        /persist/sys/rphm.conf, is set in parse_cli().

    Args:
        filename (str): The path to the config file.

    Returns:
        dict: A dictionary of configuration and switch definitions.

    """

    if not filename:
        filename = "/persist/sys/rphm.conf"

    setting = {}
    defaults = {
        'protocol': 'https',
        'username': 'arista',
        'password': 'arista',
        'url': '%(protocol)s://%(username)s:%(password)s@%(hostname)s:%(port)s'\
               '/command-api',
        'interfaceList': 'Management 1',
        'counterList': 'alignmentErrors,fcsErrors,symbolErrors',
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

    default_port = '443'

    os.path.isfile(filename)
    if not os.access(filename, os.R_OK):
        log("Unable to read config file {0}".format(filename))
        raise IOError("Unable to read config file {0}".format(filename))

    config = ConfigParser.SafeConfigParser(defaults)
    config.read(filename)

    for section in ['switches', 'snmp', 'counters']:
        try:
            options = config.options(section)
        except ConfigParser.NoSectionError, err:
            log("Required section missing from config file {0}: ({1})".
                format(filename, err))
            raise IOError(
                "Required section missing from config file {0}: ({1})".
                format(filename, err))

        setting[section] = {}
        if 'hostname' not in options:
            config.set(section, 'hostname', 'localhost')
        if 'port' not in options:
            config.set(section, 'port', default_port)
        for option in options:
            setting[section][option] = config.get(section, option)


        # Remove standard sections so all we have left are switch customizations
        config.remove_section(section)

    # Clean up the switchOnly defaults that ConfigParser put in non-switch
    #   sections. There will still be other unnecessary entries based on the
    #   defaults but this is a little easier to read, if troubleshooting.
    remove_unneded_keys(switchkeys, setting)
    #TODO: Do similar to above for the switch sections, too.

    # Convert switchList from a string to config sections with defaults
    #  then make sure a section exists for each one in the event that this
    #  is the only place this switch is included in the config.
    #  Thsi has the added effect of picking up the defaults.
    if 'switchlist' in setting['switches']:
        for line in setting['switches']['switchlist'].split("\n"):
            for device in line.split(","):
                device = device.strip('" \t')
                if device:
                    known_list = config.sections()
                    for section in config.sections():
                        options = config.options(section)
                        if 'hostname' not in options:
                            config.set(section, 'hostname', device)
                        known_list.append(config.get(section, 'hostname'))
                    if device not in known_list:
                        config.add_section(device)
                        config.set(device, 'hostname', device)

    # Any section remaining, should being a switch definition
    setting['switches'] = []
    for section in config.sections():
        switch = {}
        config.set(section, 'name', section)
        options = config.options(section)

        if 'port' not in options:
            proto = config.get(section, 'protocol')
            if proto == 'http':
                default_port = '80'
            elif proto == 'https':
                default_port = '443'
            config.set(section, 'port', default_port)

        for option in config.options(section):
            switch[option] = config.get(section, option)

        # unmangle counterlist from a string to a list
        switch['counters'] = []
        for line in switch['counterlist'].split("\n"):
            for item in line.split(","):
                if item:
                    switch['counters'].append(item.strip('" \t'))
        switch.pop('counterlist')

        # unmangle interfacelist from a string to a list
        switch['interfaces'] = []
        for line in switch['interfacelist'].split("\n"):
            for item in line.split(","):
                if item:
                    switch['interfaces'].append(item.strip('" \t'))
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

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='DEBUG')
    response = switch.runCmds(1, ["show interfaces status"])
    # Unable to connect raises
    #    raise err
    #    error: [Errno 60] Operation timed out

    return response[0][u'interfaceStatuses']

def get_device_status(device):
    """Get interface uptime and model information

    Updates device Uptime and Model information in 'devices'.  This
    gets run on every pass in case the device uptime has changed.

    args:
        device (dict): The device config dictionary

    """

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='DEBUG')
    response = device['eapi_obj'].runCmds(1, ["show version"])
    device['modelName'] = response[0]['modelName']
    device['bootupTimestamp'] = response[0][u'bootupTimestamp']

    if device['name'] == "localhost":
        hostname = device['eapi_obj'].runCmds(1, ["show hostname"])
        print "Hostname:"
        pprint(hostname)
        device['name'] = hostname[0]['hostname']

def get_intf_counters(switch, interface="Management1"):
    """Get interface details for an interface

    Get detailed information on the specified interface.

    args:
        switch (object): A :class:`jsonrpclib` Server object
        interface (str): A complete interface name to lookup.

    returns:
        tuple: Normalized interface name and a dictionary, of detailed
             interface information/stats or None if the interface name
             is invalid.

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
    log("Entering {0}: {1}.".format(sys._getframe().f_code.co_name,
                                    interface), level='DEBUG')
    conn_error = False

    commands = ["show interfaces {0}".format(interface)]

    response = None

    try:
        response = switch.runCmds(1, commands)
    except ProtocolError, err:
        (errno, msg) = err[0]
        # 1002: invalid command
        if errno == 1002:
            log("Invalid EOS interface name ({0})".format(commands), error=True)
        else:
            conn_error = True
            log("ProtocolError while retrieving {0} ([{1}] {2})".
                format(commands, errno, msg),
                error=True)
    except Exception, err:
        conn_error = True
        #   60: Operation timed out
        #   61: Connection refused (http vs https?)
        #  401: Unauthorized
        #  405: Method Not Allowed (bad URL)
        if hasattr(err, 'errno'):
            if err.errno == 60:
                log("Connection timed out: Incorrect hostname/IP or eAPI"
                    " not configured on the switch.", error=True)
            elif err.errno == 61:
                log("Connection refused: http instead of https selected or"
                    " eAPI not configured on the switch.", error=True)
            else:
                log("General Error retrieving {0} ({1})".format(commands,
                                                                err),
                    error=True)
        else:
            # Parse the string manually
            msg = str(err)
            msg = msg.strip('<>')
            err = msg.split(': ')[-1]

            if "401 Unauthorized" in err:
                log("ERROR: Bad username or password")
            elif "405 Method" in err:
                log("ERROR: Incorrect URL")
            else:
                log("HTTP Error retrieving {0} ({1})".format(commands,
                                                             err),
                    error=True)

    if conn_error:
        raise EapiException("Connection error with eAPI")

    if isinstance(response, list):
        # Normalize the interface name.  This ensures that, internally, we
        #   use "formal" names for the interfaces as returned in JSON.
        interface = response[0][u'interfaces'].keys()[0]
        return (interface, response[0][u'interfaces'][interface])
    else:
        return (interface, None)

def get_device_counters(device):
    """ Get counters from a device and return a dict of results

    """
    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='DEBUG')

    counters = {}
    for index, interface in enumerate(device['interfaces']):
        try:
            (propername, counters[interface]) = get_intf_counters(
                device['eapi_obj'], interface=interface)
        except EapiException:
            raise

        if counters[interface] is None:
            # Can't connect to
            counters.pop(interface)
        if interface != propername:
            device['interfaces'][index] = propername

    return counters

def compare_counters(device, reference, current, test=None):
    """Compare the counters in 2 sets and return only differences

    Any interface not in up/up state will be skipped.

    Args:
        device (dict): A device config from the config_file
        reference (dict): The previous iteration's stats
        current (dict): The current iteration's stats
        test (string): If test exists, automatically add a value to the counters

    Returns:
        dict: A dictionary of alert-able deltas for this device.

    """

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='DEBUG')
    diffs = {}

    input_counters = ['alignmentErrors',
                      'fcsErrors',
                      'giantFrames',
                      'runtFrames',
                      'rxPause',
                      'symbolErrors',
                      'inBroadcastPkts',
                      'inDiscards',
                      'inMulticastPkts',
                      'inOctets',
                      'inUcastPkts',
                      'totalInErrors']
    output_counters = ['collisions',
                       'deferredTransmissions',
                       'lateCollisions',
                       'txPause',
                       'outBroadcastPkts',
                       'outDiscards',
                       'outMulticastPkts',
                       'outOctets',
                       'outUcastPkts',
                       'totalOutErrors']
    # linkStatusChanges don't fall in to either category, exactly.

    for interface in reference:
        log("Checking interface: {0}.".format(interface), level='DEBUG')

        try:
            ref = reference[interface][u'interfaceCounters']
        except KeyError:
            log("Interface counters for [{0}] are not in reference dataset".
                format(interface))
            continue

        try:
            cur = current[interface][u'interfaceCounters']
        except KeyError:
            log("Interface counters for [{0}] are not in current dataset".
                format(interface))
            continue

        diffs[interface] = {}

        if 'linkStatusChanges' in device['counters']:
            ref_counter = list(get_all(ref, 'linkStatusChanges'))
            cur_counter = list(get_all(cur, 'linkStatusChanges'))
            tmp = is_delta_significant(device,
                                       'linkStatusChanges',
                                       ref_counter[0],
                                       cur_counter[0],
                                       cur_counter[0],
                                       'in')
            if tmp is not None:
                diffs[interface][counter] = tmp
                diffs[interface][counter]['current'] = current[interface][u'lineProtocolStatus']

        # Skip interfaces not in Up state.
        if current[interface][u'lineProtocolStatus'] != u'up':
            # Remove the interface entry if there were no linkStatusChanges found
            if not diffs[interface].keys():
                diffs.pop(interface)
            log("Interface [{0}] is not up. Skipping counters...".
                format(interface))
            continue

        total_in = list(get_all(ref, 'inUcastPkts'))[0] + \
            list(get_all(ref, 'inMulticastPkts'))[0] + \
            list(get_all(ref, 'inBroadcastPkts'))[0]

        total_out = list(get_all(ref, 'outUcastPkts'))[0] + \
            list(get_all(ref, 'outMulticastPkts'))[0] + \
            list(get_all(ref, 'outBroadcastPkts'))[0]

        for counter in device['counters']:
            if counter == 'linkStatusChanges':
                # This counter checked separately
                continue

            ref_counter = list(get_all(ref, counter))
            cur_counter = list(get_all(cur, counter))

            if not ref_counter or not cur_counter:
                log("Counter [{0}] missing from Reference or Current data" \
                    " set. Skipping.".format(counter), error=True)
                continue

            #Check counter direction
            if counter in input_counters:
                direction = "in"
                total = total_in
            if counter in output_counters:
                direction = "out"
                total = total_out
            else:
                #direction = "NA"
                # linkStatusChanges don't fall in to either category, exactly.
                direction = "in"
                total = total_in

            if test:
                from random import randrange
                val = int(ref_counter[0]) + randrange(10)
                cur_counter[0] = int(ref_counter[0]) + val
                log("TEST: incremented {0} by {1}".format(counter, val))

            tmp = is_delta_significant(device,
                                       counter,
                                       ref_counter[0],
                                       cur_counter[0],
                                       total,
                                       direction)
            if tmp is not None:
                diffs[interface][counter] = tmp

        # Remove the interface entry if there were no results to report
        if not diffs[interface].keys():
            diffs.pop(interface)

    return diffs

def get_all(data, key):
    """Return all values of a key in a multi-level dictionary

    Args:
        data (dict): The dict in which to lookup a key
        key (str): The key to find

    Returns:
        (itterable): A list of values for the specified key.

    """

    sub_iter = []
    if isinstance(data, dict):
        if key in data:
            yield data[key]
        sub_iter = data.itervalues()
    if isinstance(data, list):
        sub_iter = data
    for subset in sub_iter:
        for obj in get_all(subset, key):
            yield obj

def is_delta_significant(device, counter, ref, cur, total=0, direction="in"):
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

    delta = cur - ref
    try:
        threshold = int(device[counter.lower()])
    except KeyError:
        log("No threshold set for {0} in the config file. Skipping.".
            format(counter), error=True)
        return None

    log("Comparing {0}[{1}]: REF [{2}], CUR [{3}]. "
        "expecting < {4}".format(device['name'], counter, ref, cur,
                                 device[counter.lower()]),
        level='DEBUG')

    if delta >= threshold:
        return {'threshold': threshold, 'found': delta, 'total': total, 'direction': direction}
    else:
        return None

def do_actions(device, changes, interval):
    """ Perform actions for each delta noted in "changes"

    Actions currently consist of send_trap() to send an SNMP-trap.  Future
    possibilities could include sending an email, additional syslogs, or
    taking action on-device, such as shutting down an LAG member with
    undesirable performance characteristics.

    Args:
        device (string): The friendly-name/hostname of the node.
        changes (dict): A dictionary by port consisting of the counter that
        changed, the amount it changed, the threshold it crossed, and the
        total traffic on the interface during that same interval.
        interval (int): The interval in seconds between port health checks

    """

    # 'localhost' isn't very meaningful at a central traphost so
    # try do present something more meaningful.  device['name']
    # will either be user-specified in the config or, if localhost,
    # we will fill that in with the hostname configured on the switch.
    if device['hostname'] == "localhost":
        hostname = device['name']
    else:
        hostname = device['hostname']

    for interface in changes:
        for counter in changes[interface]:

            if counter == 'linkStatusChanges':
                trap_content = "Device {0} {1}, interface {2}: {3}"\
                    " increasing at > {4} in {5} seconds. Found {6}/{7} changes."\
                    " Currently {8}".\
                format(hostname,
                       device['modelName'],
                       interface,
                       counter,
                       changes[interface][counter]['threshold'],
                       interval,
                       changes[interface][counter]['found'],
                       changes[interface][counter]['total'],
                       changes[interface][counter]['current'])
            else:
                trap_content = "Device {0} {1}, interface {2}: {3} increasing"\
                    " at > {4} per {5} seconds. Found {6}/{7} packets {8}".\
                format(hostname,
                       device['modelName'],
                       interface,
                       counter,
                       changes[interface][counter]['threshold'],
                       interval,
                       changes[interface][counter]['found'],
                       changes[interface][counter]['total'],
                       changes[interface][counter]['direction'])

            # system uptime
            send_trap(trap_content, uptime=int(device['bootupTimestamp']))

def send_trap(message, uptime='', test=False):
    """ Send an Arista enterprise-specific SNMP trap containing message.

    Args:
        message (string): The message to include in the trap
        uptime (string): The device's uptime for the SNMP trap.
        test (bool): Sent a sample trap message? (Default: False)

    """

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='DEBUG')

    log("Sending SNMPTRAP to {0}: {1}".format(SNMP_SETTINGS['traphost'],
                                              message))

    # NOTE: snmptrap caveat: Generates an error when run as unprivileged user.
    #    Failed to create the persistent directory for
    #    /var/net-snmp/snmpapp.conf
    #    http://sourceforge.net/p/net-snmp/bugs/1706/
    #

    # Build the arguments to snmptrap
    #trap_args = ['snmptrap']
    trap_args = ['snmptrap']
    trap_args.append('-v')
    trap_args.append(SNMP_SETTINGS['version'])

    if SNMP_SETTINGS['version'] == '2c':
        trap_args.append('-c')
        trap_args.append(SNMP_SETTINGS['community'])

    elif SNMP_SETTINGS['version'] == '3':
        # Send v3 snmp-inform rathern than a trap
        trap_args.append('-Ci')

        trap_args.append('-l')
        trap_args.append(SNMP_SETTINGS['seclevel'])
        trap_args.append('-u')
        trap_args.append(SNMP_SETTINGS['secname'])

        if SNMP_SETTINGS['seclevel'] in ['authNoPriv', 'authPriv']:
            trap_args.append('-a')
            trap_args.append(SNMP_SETTINGS['authprotocol'])
            trap_args.append('-A')
            trap_args.append(SNMP_SETTINGS['authpassword'])

        if SNMP_SETTINGS['seclevel'] == 'authPriv':
            trap_args.append('-x')
            trap_args.append(SNMP_SETTINGS['privprotocol'])
            trap_args.append('-X')
            trap_args.append(SNMP_SETTINGS['privpassword'])
    else:
        log("Unknown snmp version '{0}' specified in the config file.".
            format(SNMP_SETTINGS['version']))
    trap_args.append(SNMP_SETTINGS['traphost'])

    #.iso.org.dod.internet.private. .arista
    # enterprises.30065
    enterprise_oid = '.1.3.6.1.4.1.30065'
    # enterpriseSpecific = 6
    generic_trapnum = '6'
    trap_oid = '.'.join([enterprise_oid, generic_trapnum])

    trap_args.append(str(uptime))
    trap_args.append(enterprise_oid)
    trap_args.append(trap_oid)
    trap_args.append('s')

    if test == "trap":
        message = "Device TEST-Device, interface Management 1:" \
            " FAKEalignmentErrors increasing at > 1 per 5 seconds. Found 7/2401 packets in"
        log("Sending SNMPTRAP to {0} with arguments: {1}".
            format(SNMP_SETTINGS['traphost'], trap_args), level='DEBUG')

    trap_args.append(message)

    if test == "trap":
        print "snmptrap_args:"
        pprint(trap_args)

    call(trap_args)

def main():
    ''' main execution routine for devops command. Parse the command
        line options, build the RESTful request, send it to stdlib,
        and then process the response.
    '''

    global SNMP_SETTINGS
    global DEBUG

    args = parse_cmd_line()
    DEBUG = args['debug']

    log("Entering {0}.".format(sys._getframe().f_code.co_name), level='DEBUG')

    config = read_config(args['config'])

    SNMP_SETTINGS = config['snmp']

    if args['test'] == 'parse_only':
        print "\nargs:"
        pprint(args)
        print "\nconfig:"
        pprint(config)
        return 0

    elif args['test'] == 'trap':
        send_trap('', test='trap')
        return 0

    elif args['test'] == 'get':
        print "Connecting to eAPI at {0}".format(config['switches'][0]['url'])
        switch = Server(config['switches'][0]['url'])
        (interface, counters) = get_intf_counters(switch, interface="Management1")
        print "\nTest=get: received the following counters from Management 1:"
        pprint(counters)
        print "Test=get: --------------------------\n"
        return 0

    log("Started up successfully. Entering main loop...")

    reference = {}

    while True:

        for device in config['switches']:
            log("Polling {0} with eAPI".format(device['name']))
            current = {}

            # Create the Server object on the first round
            if device.get('eapi_obj', None) is None:
                device['eapi_obj'] = Server(device['url'])

            try:
                current = get_device_counters(device)
            except EapiException:
                log("Connection error with eAPI.  Will retry device next pass",
                    error=True)
                # Remove stale data
                reference.pop(device['hostname'], None)
                continue

            if reference.get(device['hostname'], None) is None:
                # Have not contacted this device since startup or
                # this is the first contact.  Continue to next device/itter.
                log("Established contact with {0}".format(device['name']))
                reference[device['hostname']] = dict(current)
                continue

            get_device_status(device)
            changes = compare_counters(device, reference[device['hostname']],
                                       current, test=args['test'])

            do_actions(device, changes, int(config['counters']['poll']))

            # Copy current stats-->reference to reset the "deltas" for the
            #   next run.
            reference[device['hostname']] = dict(current)

        log("---sleeping for {0} seconds.".format(config['counters']['poll']),
            level='DEBUG')
        time.sleep(int(config['counters']['poll']))

