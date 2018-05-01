# 1.1.1 (April 2018)

* Fix issue #8 by clearing the jsonrpclib history on each run to prevent a
  possible memory issue.

# 1.1.0 (March 2016)

* Fix SysUptime string in SNMP traps
* Fix layered defaults for config parameters
* Fix linkStatus reporting when interfaces are down
* Add systemd config file which can be used on linux workstations to start/stop
  the rphm service. Must be installed manually.

# 1.0.0 (September 2014)

* Initial public release

# 0.1.2 (September 2014)

* Add total packets during a period to the SNMP message

# 0.1.1 (August 2014)

* Skip interfaces that are not "up"
* Handle fuzzy interface names: e2, eth 4/3, Et3/8, etc
* Remove quotes around the username/password in the config
* When monitoring "localhost" to provide a better hostname in the alerts

# 0.1.0 (August 2014)

* Initial beta delivery
