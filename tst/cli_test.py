#!/usr/bin/env python
# encoding: utf-8
"""
cli+test.py

Created by Giles Velarde on 2010-03-03.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import optparse
import ConfigParser

try:
    import simplejson as json
except ImportError:
    import json #@UnusedImport

import ropy.query
import ropy.server

from crawl.api.api import API


def main():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--conf", dest="conf", action="store", help="the path to the configuration file")
    
    (options, args) = parser.parse_args() #@UnusedVariable
    if options.conf == None: sys.exit("Please supply a conf parameter.")

    config = ConfigParser.ConfigParser()
    config.read(options.conf)

    # cherrypy file-configs must be valid python expressions, they get eval()ed
    host=eval(config.get('Connection', 'host'))
    database=eval(config.get('Connection', 'database'))
    user=eval(config.get('Connection', 'user'))
    password=eval(config.get('Connection', 'password'))

    connectionFactory = ropy.query.ConnectionFactory(host, database, user, password)
    
    api = API(connectionFactory)
    result = api.annotation_changes('5671', '2009-10-03')
    
    print ropy.server.Formatter(result).formatJSON()


if __name__ == '__main__':
    main()

