#!/usr/bin/env python
# encoding: utf-8
"""
crawl.py

Created by Giles Velarde on 2010-03-03.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import inspect
import ropy.query
import ropy.server
import util.password
import crawl.api.db
import crawl.api.controllers

import logging
logger = logging.getLogger("crawl")

BASIC_USAGE = """
Usage:  python crawler.py -query path/function [options] -database host:5432/database?user
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


def method_usage(method):
    usage = ""
    for arg_key, arg_doc in method.arguments.items():
        usage += "-" + arg_key
        usage += "\t" + arg_doc
    return usage

def call_method(api, method_name, args):
    
    if hasattr(api, method_name):
        method= getattr(api, method_name)
        if inspect.ismethod(method):
            try:
                return method(**args)
            except ropy.server.ServerException, se: #@UnusedVariable
                if se.info == None:
                    se.info = method_usage(method)
                else:
                    se.info += method_usage(method)
                raise se
            except Exception,e:
                logger.error(e)
                raise ropy.server.ServerException(str(e), ropy.server.ERROR_CODES["MISC_ERROR"], method_usage())
        else:
            raise ropy.server.ServerException("%s is not a query of %s." % (method_name, api.__class__.__name__.lower()), ropy.server.ERROR_CODES["UNKOWN_QUERY"], print_methods(api))
    else:
        raise ropy.server.ServerException("%s is not a query of %s." % (method_name, api.__class__.__name__.lower()), ropy.server.ERROR_CODES["UNKOWN_QUERY"], print_methods(api))
    

def get_classes():
    attrs = []
    for attr_tuple in inspect.getmembers(crawl.api.controllers):
        attr_key = attr_tuple[0]
        attr = attr_tuple[1]
        if inspect.isclass(attr) and attr_key != "BaseController":
            attrs.append(attr)
    return attrs

def print_classes():
    s = "Available sets are:\n"
    for the_class in get_classes():
        s+= "\n\t" + the_class.__name__.lower()
    return s
def get_methods(obj):
    methods = []
    for member_info in inspect.getmembers(obj):
        member_name = member_info[0] #@UnusedVariable
        member = member_info[1]
        if inspect.ismethod(member) and hasattr(member, "exposed"):
            methods.append(member_info)
    return methods

def print_methods(obj):
    s="" "Available %s queries are: \n" % obj.__class__.__name__.lower()
    for member_info in get_methods(obj):
        member_name = member_info[0]
        member = member_info[1] #@UnusedVariable
        s+= "\n\t" + member_name
    return s

def get_api(path):
    api = None
    for the_class in get_classes():
        if the_class.__name__.lower() == path:
            api = the_class()
            break

    if api == None:
        raise ropy.server.ServerException("Could not find a path of %s.\n" % path,  ropy.server.ERROR_CODES["UNKOWN_QUERY"], print_classes())

    if not isinstance(api, crawl.api.controllers.BaseController):
        raise ropy.server.ServerException("The path %s must specify a class that inherits from BaseController.\n" % path,  ropy.server.ERROR_CODES["UNKOWN_QUERY"], print_classes())
    return api

def parse_database_uri(uri):
    
    host = ""
    port = 0
    database = ""
    user = ""
    
    if "/" not in uri:
        raise ropy.server.ServerException("Invalid database uri '%s'. Please provide a database uri in the form of 'localhost:5432/database?user'." % uri,  ropy.server.ERROR_CODES["MISC_ERROR"])
    
    split = uri.split("/")
    
    host = split[0]
    if ":" in split[0]:
        (host, port) = split[0].split(":")
    
    
    if "?" in split[1]:
        (database, user) = split[1].split("?")
    else:
        raise ropy.server.ServerException("Must provide a user name in '%s'. Please provide a database uri in the form of 'localhost:5432/database?user'." % uri,  ropy.server.ERROR_CODES["MISC_ERROR"])
    
    return (host, port, database, user)
    

def execute(path, function, args, database_uri, password):
    
    (host, port, database, user) = parse_database_uri(database_uri)
    logger.debug ("host %s port %s database %s user %s" % (host, port, database, user))
    
    api = get_api(path)
    connectionFactory = ropy.query.ConnectionFactory(host, database, user, password)
    api.queries = crawl.api.db.Queries(connectionFactory)
    
    # make the call
    result = call_method(api, function, args)
    
    # tidy up
    api.queries.conn.close()
    
    return ropy.server.Formatter(result).formatJSON()
    

def main(database = None):
    
    try:
        
        password = util.password.get_password("password")
        
        args = get_args()
        
        if database == None: 
            if "database" not in args: 
                database = DEFAULT_URL
            else:
                database = args["database"]
                del args["database"]
        
        if "query" not in args:
            raise ropy.server.ServerException("Please provide a -query argument, e.g. '-query genes/list'.", ropy.server.ERROR_CODES["UNKOWN_QUERY"], print_classes())
        else:
            query = args["query"]
            del args["query"]
        
        if "/" not in query:
            api = get_api(query)
            raise ropy.server.ServerException("Please provide 2 parts to the -query argument, the path and the function, separated by a '/', e.g. '-query genes/list'.", ropy.server.ERROR_CODES["UNKOWN_QUERY"], print_methods(api))
            
        (path, function) = query.split("/", 2)
    
        print execute(path, function, args, database, password)
    except ropy.server.ServerException, e:
        print e.value
        print BASIC_USAGE
        if e.info != None: print e.info
        sys.exit(e.code + 1)
    except Exception, e:
        print str(e)
        #import traceback   
        #traceback.print_exc()
        sys.exit(BASIC_USAGE)
        

if __name__ == '__main__':
    main()
