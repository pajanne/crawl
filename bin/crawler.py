#!/usr/bin/env python
# encoding: utf-8
"""
crawl.py

Created by Giles Velarde on 2010-03-03.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import inspect
from util.password import get_password

try:
    import simplejson as json
except ImportError:
    import json #@UnusedImport

import ropy.query
import ropy.server

import crawl.api.db
import crawl.api.controllers

import logging
logger = logging.getLogger("crawl")

BASIC_USAGE = """
Usage:  python crawler.py -set [set_name] -query [query_name] [options] -database host:5432/database?user
"""

DEFAULT_URL = "localhost:5432/pathogens?pathdb"

def get_args():
    args = {}
    key = None
    for arg in sys.argv:
        if arg[0] == "-": key = arg[1:len(arg)]
        else:
            if key !=None:
                if key not in args: 
                    args[key] = []
                args[key].append(arg)
    for k,v in args.items():
        if len(v) == 1:
            args[k] = v[0]
    return args


def call_method(api, method_name, args):
    
    if hasattr(api, method_name):
        method= getattr(api, method_name)
        if inspect.ismethod(method):
            
            try:
                return method(**args)
            except ropy.server.ServerException, se: #@UnusedVariable
                print se.value
                
                for arg_key, arg_doc in method.arguments.items():
                    print BASIC_USAGE
                    print "-" + arg_key
                    print "\t" + arg_doc
                
                # make sure the script status code is not 0
                sys.exit(se.code+1)
            
        else:
            raise Exception("%s is not a method of the API." % method_name)
    else:
        raise Exception("%s is not an attribute of the API." % method_name)
    

def get_classes():
    attrs = []
    for attr_tuple in inspect.getmembers(crawl.api.controllers):
        attr_key = attr_tuple[0]
        attr = attr_tuple[1]
        if inspect.isclass(attr) and attr_key != "BaseController":
            attrs.append(attr)
    return attrs

def print_classes():
    print "Available sets are:\n"
    for the_class in get_classes():
        print "\t" + the_class.__name__.lower()

def get_methods(obj):
    methods = []
    for member_info in inspect.getmembers(obj):
        member_name = member_info[0] #@UnusedVariable
        member = member_info[1]
        if inspect.ismethod(member) and hasattr(member, "exposed"):
            methods.append(member_info)
    return methods

def print_methods(obj):
    print "Available %s queries are: \n" % obj.__class__.__name__.lower()
    for member_info in get_methods(obj):
        member_name = member_info[0]
        member = member_info[1] #@UnusedVariable
        print "\t" + member_name

def get_api(path):
    api = None
    for the_class in get_classes():
        if the_class.__name__.lower() == path:
            api = the_class()
            break

    if api == None:
        print "Could not find a path of %s.\n" % path
        print_classes()
        sys.exit(BASIC_USAGE)

    if not isinstance(api, crawl.api.controllers.BaseController):
        print "The class must be a BaseController instance.\n"
        print_classes()
        sys.exit(BASIC_USAGE)
    return api

def execute(path, function, args, database_uri):
    #"localhost:port/database?user"
    
    ((host, port), (database, user)) = [database_uri.split("/")[0].split(":"), database_uri.split("/")[1].split("?")]
    logger.debug ("host %s port %s database %s user %s" % (host, port, database, user))
    
    password = get_password("password")
    
    api = get_api(path)
    connectionFactory = ropy.query.ConnectionFactory(host, database, user, password)
    api.queries = crawl.api.db.Queries(connectionFactory)
    
    result = call_method(api, function, args)
    
    return ropy.server.Formatter(result).formatJSON()
    

def main():
    
    args = get_args()
    
    if "database" not in args: 
        database = DEFAULT_URL
    else:
        database = args["database"]
        del args["database"]
            
    if "set" not in args:
        print "Please provide a -set argument."
        print_classes()
        sys.exit(BASIC_USAGE)
    else:
        set = args["set"]
        del args["set"]
    
    if "query" not in args:
        print "Please provide a -query argument."
        api = get_api(set)
        print_methods(api)
        sys.exit(BASIC_USAGE)
    else:
        query = args["query"]
        del args["query"]
    
    print execute(set, query, args, database)
    

if __name__ == '__main__':
    main()

