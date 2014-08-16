# TriggerTrap extension for Arista EOS

## Overview
The triggertrap extension monitors interface counters, then generates an SNMP trap whenever such counters exceed given thresholds.

## License

 This is licensed under the [BSD3 license](../blob/master/LICENSE).

## Requirements

- net-snmp: ‘snmptrap’ MUST be in the PATH
- jsonrpclib: for access to eAPI

Building and testing require additional packages:

- mock
- rpmbuild

## Build

Python package:

    make sdist

RPM package:

    make rpm

## Install
Triggertrap can be installed directly on one or more EOS switches and run as a daemon, there, or centrally on a linux system to monitor multiple switches from one place.  While running it centrally reduces the load put on a switch, it also requires that eAPI on the switch be allowed from that workstation.   When run directly on a switch, eAPI may be restricted to localhost-only.  Additionally, SNMP traps will be sourced from the switch’s IP address.

### On an EOS device
```
EOS#copy scp://username@10.10.10.1/src/triggertrap/rpmbuild/triggertrap-0.1.0-1.rpm extension:
Password:
triggertrap-0.1.0-1.rpm                       100%   17KB  17.0KB/s   00:00    
Copy completed successfully.
EOS#show extensions 
Name                                       Version/Release           Status RPMs
------------------------------------------ ------------------------- ------ ----
triggertrap-0.1.0-1.rpm                    0.1.0/1                   A, NI     1

A: available | NA: not available | I: installed | NI: not installed | F: forced
EOS#extension triggertrap-0.1.0-1.rpm
EOS#show extensions
Name                                       Version/Release           Status RPMs
------------------------------------------ ------------------------- ------ ----
triggertrap-0.1.0-1.rpm                    0.1.0/1                   A, I      1

A: available | NA: not available | I: installed | NI: not installed | F: forced
vEOS-1#
```

### On a linux system
    rpm -Uvh rpmbuild/triggertrap-0.1.0-1.rpm

### Configuration
The configuration file contains SNMP settings, the poll timer, and information on which switch(es) and counter(s) to monitor.

The default location for the config file is `/persist/sys/triggertrap.conf`.

## Usage

```
usage: triggertrap [-h] [--config CONFIG] [--debug]

Poll switches with eAPI then send SNMP trap on changes in interface error counters.

optional arguments:
-h, --help       show this help message and exit
--config CONFIG  Specifies the configuration file to load(Default:
                   /persist/sys/triggertrap.conf)
--debug          Send debug information to the console

--test {parse_only, get, trap, snmp}  Testing options:
          parse_only  Parse the command_line and config, then exit.
          get         Get one set of interface statistics and dump to console.
          trap        Send a single test snmptrap then exit.
          snmp        Add a random integer to each counter on each pass to
                      simulate trap-able conditions.
```

## EOS Configuration

EOS eAPI must be configured on each monitored device.  At a minimum, this requires:

```
EOS#configure terminal
EOS(config)#username arista privilege 15 secret arista
EOS(config)#management api http-commands
EOS(config-mgmt-api-http-cmds)#no shutdown
```

To execute triggertrap directly on the switch, add the following:

```
EOS(config)#daemon triggertrap
EOS(config-daemon-triggertrap)#command /usr/bin/triggertrap --test=snmp
EOS(config)#end
```

## Monitoring

### EOS

```
EOS#show processes | include trigger
10159  0.1  1.4 ?        S    03:21:23 00:00:00 triggertrap     -d -i --dlopen -p -f  -l libLoadDynamicLibs.so procmgr libProcMgrSetup.so --daemonize
```

## Uninstall

### EOS

```
EOS#config termintal
EOS(config)#no daemon triggertrap
EOS(config)#end
EOS#no extension triggertrap-0.1.0-1.rpm
```

### Linux

```
rpm -e triggertrap-0.1.0-1.rpm
```


# Demo

1. Copy snmptrapd-start and snmptrapd.conf to the receiver host, then execute

    ./snmptrapd-start

2. On the client, in triggertrap.conf, enter the traphost and select which snmp version you with to use.  Then check your switch settings.   Defaults to https://arista:arista@localhost/command-api

3. Verify your SNMP configuration with

    triggertrap --config=triggertrap.conf --test=trap

4. Run triggertrap in demo-mode where counters are randomly mangled to generate traps:

    triggertrap --config=triggertrap.conf --test=snmp [--debug]

