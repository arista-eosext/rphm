To demo or test rphm, you can use the default config/rphm.conf, changing only the traphost, to send SNMP traps to this test config of snmptrapd.

If needed, copy snmptrapd-start and snmptrapd.conf from this directory to the receiver host, then execute

./snmptrapd-start

This will exeture snmptrapd in the foreground, configured to accept snmp v2c or v3 traffic from the example rphm.conf file.
