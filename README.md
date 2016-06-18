python-zcli
===============
THS TOOL HAS BEEN DEPRECATED.  Use this instead: https://github.com/teriyakichild/zabbixctl

Copyright © 2014 Rackspace
Written by: Tony Rogers <tony.rogers@rackspace.com>
Extended by: Nick Shobe <nick.shobe@rackspace.com>
License: Apache Software License (ASL) 2.0 

Description
===============

CLI tool that wraps the zabbix API

Usage
===============

zcli -u https://zabbix.example.com -U username method 'template.get' -a 'output=extend' -a 'templateids=[6]' -a 'selectHttpTests=extend' -a 'selectTriggers=extend'

Config
===============

/etc/zcli.conf

INSTALLATION
===============

See INSTALL

How to report bugs
===============
Visit http://github.com/teriyakichild/python-zcli/issues
