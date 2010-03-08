#!/usr/bin/env python
# encoding: utf-8
"""
crawl.py

Created by Giles Velarde on 2010-03-03.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import optparse
import ConfigParser
import inspect

try:
    import simplejson as json
except ImportError:
    import json #@UnusedImport

import ropy.query
import ropy.server

import crawl.api.controllers
import crawl.api.db

def generate_optparser():
    parser = optparse.OptionParser()
    parser.usage = parser.usage.replace("[options]", "config class method [options]")
    return parser

def call_method(api, method_name):
    
    if hasattr(api, method_name):
        method= getattr(api, method_name)
        if inspect.ismethod(method):
            
            parser = generate_optparser()
                        
            for argument, description in method.arguments.items():
                parser.add_option(
                    "-" + argument[0],
                    "--" + argument,
                    dest=argument,
                    action="store", 
                    help=description
                )
            
            (options, args) = parser.parse_args() #@UnusedVariable
            
            arg_values = {}
            for argument in method.arguments.keys():
                arg_value = getattr(options, argument)
                if arg_value != None:
                    arg_values[argument] = arg_value
            
            try:
                return method(**arg_values)
            except ropy.server.ServerException, se: #@UnusedVariable
                return ropy.server.generate_error_data()
                
            
        else:
            raise Exception("%s is not a method of the API." % method_name)
    else:
        raise Exception("%s is not an attribute of the API." % method_name)
    

#def get_class( kls ):
#    parts = kls.split('.')
#    module = ".".join(parts[:-1])
#    m = __import__( module )
#    for comp in parts[1:]:
#        m = getattr(m, comp)            
#    return m

def main():
    
    
    if len(sys.argv) < 2:
        print "Please provide a path to the conf file as your first argument."
        parser = generate_optparser()
        parser.print_help()
        sys.exit()
    else:
        conf = sys.argv[1]
    
    if len(sys.argv) < 3:
        print "Please provide the class as your second argument."
        parser = generate_optparser()
        parser.print_help()
        sys.exit()
    else:
        class_name = sys.argv[2]
    
    if len(sys.argv) < 4:
        print "Please provide the method as your third argument."
        parser = generate_optparser()
        parser.print_help()
        sys.exit()
    else:
        method_name = sys.argv[3]
    
    config = ConfigParser.ConfigParser()
    config.read(conf)

    # cherrypy file-configs must be valid python expressions, they get eval()ed
    host=eval(config.get('Connection', 'host'))
    database=eval(config.get('Connection', 'database'))
    user=eval(config.get('Connection', 'user'))
    password=eval(config.get('Connection', 'password'))

    connectionFactory = ropy.query.ConnectionFactory(host, database, user, password)
    
    api = None
    for attr_tuple in inspect.getmembers(crawl.api.controllers):
        attr_key = attr_tuple[0] #@UnusedVariable
        attr = attr_tuple[1]
        if inspect.isclass(attr):
            if attr.__name__.lower() == class_name:
                api = attr()
                break
                
    if api == None:
        print "Could not find an api of " + class_name
        parser = generate_optparser()
        parser.print_help()
        sys.exit()
        
    if not isinstance(api, crawl.api.controllers.BaseController):
        print "The class must be a BaseController instance."
        parser = generate_optparser()
        parser.print_help()
        sys.exit()
    
    api.queries = crawl.api.db.Queries(connectionFactory)
    result = call_method(api, method_name)
    
    print ropy.server.Formatter(result).formatJSON()
    

if __name__ == '__main__':
    main()

