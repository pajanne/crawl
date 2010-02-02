#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Giles Velarde on 2009-11-17.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import os

import sys
import os
import ConfigParser
from ropy.log import LogSetup
from ropy.util import getArg
from ropy.query import ConnectionFactory

try:
    conf = getArg("conf", raiseOnEmpty = True)
except Exception, e:
    print e
    print "Please supply a path to a conf file using the conf parameter (-conf)."
    sys.exit(1)

try:
    config = ConfigParser.ConfigParser()
    config.read(conf)
except Exception, e:
    print ("Could not read this file " + conf)
    sys.exit(1)

try:
    
    logsetup = LogSetup()
    logsetup.logname = "charpy"
    logsetup.logpath = config.get('Logging', 'path')
    logsetup.setupLogging()
    logger = logsetup.logger
except Exception, e:
    print e
    print "Could not set up the logging, is the path set in the conf file correct?"
    sys.exit(1)

production = getArg("production", raiseOnEmpty = False)
access_log = config.get('Logging', 'access_log')
error_log = config.get('Logging', 'error_log')


host=config.get('Connection', 'host')
database=config.get('Connection', 'database')
user=config.get('Connection', 'user')
password=config.get('Connection', 'password')

# connectionFactory = ConnectionFactory(host, database, user, password)


def main():
    pass


if __name__ == '__main__':
    main()

