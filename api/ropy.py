"""
ropy.py

Created by Giles Velarde on 2009-11-08.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.


8888888b.   .d88888b.  8888888b. Y88b   d88P     .d8888b.  
888   Y88b d88P" "Y88b 888   Y88b Y88b d88P     d88P  Y88b 
888    888 888     888 888    888  Y88o88P             888 
888   d88P 888     888 888   d88P   Y888P            .d88P 
8888888P"  888     888 8888888P"     888         .od888P"  
888 T88b   888     888 888           888        d88P"      
888  T88b  Y88b. .d88P 888           888        888"       
888   T88b  "Y88888P"  888           888        888888888  
                                                     
                                                           
A spiritual successor to Ropy 1 (http://code.google.com/p/ropy/), 
which is a lightweight RESTful Python server. This second version 
strings together: 

- the CherryPy server (http://www.cherrypy.org/) 
- Cheetah for XML templating (http://www.cheetahtemplate.org/)
- psycopg2 (http://initd.org/projects/psycopg2)
- Enum (http://pypi.python.org/pypi/enum/)

All of which must be installed on your system to run. 

This module defines some utilities for defining RESTful resources 
powered by database calls and deploying them. 

PS - the fontage above is http://www.network-science.de/ascii/ | colossal.


"""

from Cheetah.Template import Template
from Cheetah.Filters import Filter
from xml.sax.saxutils import quoteattr
import cherrypy
import inspect
import os
import sys
import logging

import types 

import xml.dom.minidom

logger = logging.getLogger("ropy")

try:
    import simplejson as json
except ImportError:
    import json

# an enum-type list of error codes, to standardise error responses
ERROR_CODES = {
    "INVALID_DATE" : 1,
    "BAD_PARAMETER" : 2,
    "DATA_NOT_FOUND" : 3,
    "MISSING_PARAMETER" : 4,
    "UNKOWN_QUERY" : 5,
    "MISC_ERROR" : 6,
    "DATA_PARSING_ERROR" : 7,
}


class ServerException(Exception):
    """
        Ideally, all errors should be raised with this (or a subclass of), so that the
        server can always report back a consistent error message to the client.
    """
    def __init__(self, value, code, info = None):
        self.value = value
        self.code = code
        self.info = info
    
    def __str__(self):
        return repr({ "value": self.value , "code" : self.code, "info": self.info})
    
    def __repr__(self):
        return "<ServerException(%s,%s,%s)" % (self.value, self.code, self.info)


serving = False
def serve():
    globals()["serving"] = True
def unserve():
    globals()["serving"] = False

def service_format(format_name = None):
    """
        A decorator maker (see http://stackoverflow.com/questions/739654/understanding-python-decorators). This extra function nesting is to allow
        setting the format_name at the method level, by permitting the methods to be decorated with parameters. For example:
        
            @ropy.server.service_format("changes")
            def changes(self, since, taxonomyID):
                ...
        The format_name parameter tells is passed on by the wrapper to the RESTController.format method. 
        
    """
    def service_decorator(func):
        """
            The decorator, which passes the func parameter onto the wrapper.
        """
        def wrapper(self, *args, **kwargs):
            """
                Generates the appropriate headers, determines the format_type, calls the exposed method, and wraps the response in a 
                JSONP callback if the appropriate parameter is present. 
            """
            
            # remove any [] from array keys
            for k, v in kwargs.items():
                if k.endswith("[]"):
                    del kwargs[k]
                    new_k = k[0:len(k)-2]
                    kwargs[new_k] = v
            
            logger.debug("args : " + str(args))
            logger.debug("kwargs : " + str(kwargs))
            logger.debug("format_name : " + str(format_name))
            
            # check the supplied arguments for missing arguments
            argspec = inspect.getargspec(func)
            
            logger.debug(argspec)
            
            funcargs = argspec[0]
            
            # the func does not have the arguments attribute attached to it, but the method does, so get the method
            # method = getattr(self, func.func_name)
            # add any arguments declared in the method arguments attribute to the list of arguments to check for
            # for m_argname, m_argval in method.arguments.items():
            #     if m_argname not in funcargs: funcargs.append(m_argname)
            
            
            # ArgSpec(args=['self', 'features', 'cvs'], varargs=None, keywords=None, defaults=(['x', 'y'], []))
            defaults = argspec[3]
            arg_defaults = {}
            # logger.debug(defaults)
            if defaults != None:
                index_diff = len(funcargs) - len(defaults)
                for defindex in range(len(defaults)):
                    default = defaults[defindex]
                    funcargindex = defindex + index_diff
                    funcarg = funcargs[funcargindex]
                    logger.debug ([defindex, funcargindex, default, funcarg])
                    arg_defaults[funcarg] = default
            
            
            
            missing = ""
            missingsep = ""
            for funcarg in funcargs:
                if funcarg != "self" and funcarg not in kwargs and funcarg not in arg_defaults:
                    missing += missingsep + funcarg
                    missingsep = ", "
        
            if len(missing) > 0:
                raise ServerException("missing args: " + missing, ERROR_CODES["MISSING_PARAMETER"])
            
            
            # just execute if the server is not serving
            if serving == False:
                data = func(self, *args, **kwargs)
                return data
                

            # a keyword argument with the callBack name, we need this
            callback = None

            # I think this injected by JQuery, probably to prevent caching
            _ = None
        
            # get these values from the kwargs, if present, and pop them from the kwargs before sending onto the exposed methods
            if 'callback' in kwargs:
                callback = kwargs['callback']
                del kwargs['callback']

            if '_' in kwargs:
                _ = kwargs['_']
                del kwargs['_']

            # set the appropriate headers
            self.init_handler()
            
            # get the desired format_type (by looking at the URL), and set the appropriate headers
            format_type = self.get_format_type()
            self.set_headers(format_type)
            
            data = func(self, *args, **kwargs)
            
            # format the data
            returned = self.format(data, format_type, format_name)
            
            # assign a JSONP callback if needed
            if callback is not None:
                if format_type == "json":
                    returned = '%s(%s)' % (callback, returned)
                else:
                    returned = '%s(\'xml\' : { \'%s\' })' % (callback, returned.replace("'", "\'"))
        
            return returned
        
        # assign the docstring as being the same as the function's
        # required by the reflection based service description function in RESTController.index()
        wrapper.__doc__ = func.__doc__
    
        return wrapper
        
        service_decorator.__doc__ = wrapper.__doc__
    return service_decorator


def generate_error_data():
    """
        Tries to extract error information from sys.exc_info, and if it's a ServerException, extracts its error code too. 
    """
    exc = sys.exc_info()
    message = "A runtime error occured"
    error_type = "runtime_error"
    code = "-1"

    if exc != (None, None, None):
        if exc[1] != None:

            exception = exc[1]

            logger.error(exception)

            if isinstance(exception, ServerException):

                try:
                    for code_type in ERROR_CODES:
                        code_value = ERROR_CODES[code_type]
                        if code_value == exception.code:
                            code = code_type
                            break
                except Exception, e:
                    logger.error(e)
                    logger.error( "could not set error code for " + str(code_value) )

                try:
                    error_type = str(exception.code)
                except:
                    logger.error( "could not set error type: " + str(exception) )

                try:
                    message = str(exception.value)
                except:
                    logger.error( "could not set error message " + str(exception) )

            else:
                if hasattr(exception, "message"):
                    message = getattr(exception, "message")


    data = {
        "response" : {
            "error" : {
                "type" : error_type,
                "code" : code,
                "message" : message
            }
        }
    }
    return data


def handle_error():
    """
        Handle's exceptions thrown by the application.
    """
    logger.error ("error detected in handle_error()")
    data = generate_error_data()

    handler = ErrorController()
    format_type = handler.get_format_type()
    # handler.init_handler()
    handler.set_headers(format_type)
    formatted = handler.format(data, format_type, "error")
    # formatted = handler.error(data)

    cherrypy.response.body = [formatted]

def error_page_default(status, message, traceback, version):
    """
        A fallback for errors not thrown by the application, but somewhere else on the server. 
    """
    logger.error ("error routed to error_page_default()")
    data = {
        "response" : {
            "error" : {
                "type" : status,
                "code" : 0,
                "message" : message 
            }
        }
    }

    handler = ErrorController()
    # handler.init_handler()
    format_type = handler.get_format_type()
    handler.set_headers(format_type)
    formatted = handler.format(data, format_type, "error")
    return formatted


def generate_mappings(obj, mapper, path = ""):
    """
        Recursively maps a tree of RESTController objects onto a cherrypy.dispatch.RoutesDispatcher() mapper object. Assigns .xml and .json paths for them too.
    """
    for member_info in inspect.getmembers(obj):
        member_name = member_info[0]
        member = member_info[1]
        
        if inspect.ismethod(member):
            if hasattr(member, "exposed") and member_name != "default":
                logger.debug (obj.__class__.__name__ + "." + member_name + " :: " + path + "/" + member_name)
                
                endpoint = member_name
                if member_name == "index":
                    endpoint = ""
                
                mapper.connect(
                    path + "/" + member_name,
                    path + "/" + endpoint, 
                    action=member_name, 
                    controller=obj,
                    conditions=dict(method=['POST', 'GET']))
                
                mapper.connect(
                    path + "/" + member_name,
                    path + "/" + endpoint + ".xml", 
                    action=member_name, 
                    controller=obj,
                    conditions=dict(method=['POST', 'GET']))
                
                mapper.connect(
                    path + "/" + member_name,
                    path + "/" + endpoint + ".json", 
                    action=member_name, 
                    controller=obj,
                    conditions=dict(method=['POST', 'GET']))
                    
        elif isinstance(member, RESTController):
            generate_mappings(member, mapper, path + "/" + member_name)


def to_array(obj = None):
    arr = []
    if obj != None:
        if type(obj) is types.ListType: arr.extend(obj)
        else: arr.append(obj)
    return arr

def to_bool(obj = None):
    if obj != None:
        logger.debug("Not None! " + str(type(obj)))
        if type(obj) is types.BooleanType:
            logger.debug("Bool!")
            return obj
        if type(obj) is types.StringType or type(obj) is types.UnicodeType:
            logger.debug("String ! " + obj)
            if len(obj) > 0:
                if obj == "True" or obj == "true":
                    return True
    return False
            

class RESTController(object):
    """
        A base controller for REST services.
    """
    
    def init_handler(self):
        """
            An abstract hook called by the service decorator before each method call, designed to be overriden. 
        """
        pass
    
    def get_format_type(self):
        path_info = cherrypy.request.path_info
        format_type = "json" if path_info.find(".json") != -1 else "xml"
        return format_type
    
    def set_headers(self, responseType):
        """
            Sets up the appropriate request headers.
        """
        if responseType == "xml":
            cherrypy.response.headers['Content-Type'] = "text/xml"
        elif responseType == "json":
            cherrypy.response.headers['Content-Type'] = "application/json"

    def format(self, data, format_type, name = None):
        # print self.templateFilePath
        templateFilePath = self.templateFilePath or os.path.dirname(__file__)
        
        formatter = Formatter(data, templateFilePath)
        if (format_type == "json"):
            return str(formatter.formatJSON())
        else:
            if name != None:
                return str(formatter.formatXML(name + ".xml.tpl"))
            else:
                return str(formatter.formatXML())

    @cherrypy.expose
    @service_format("info")
    def index(self):
        """
            Produces a report of the methods exposed by the RESTController subclass.
        """
        
        resources = []

        for member_info in inspect.getmembers(self):
            member_name = member_info[0]
            member = member_info[1]
            # print member_name
            
            if inspect.ismethod(member):
                if hasattr(member, "exposed") and member_name != "default" and member_name != "index":
                    
                    arguments_spec = inspect.getargspec(member)
                    arguments = arguments_spec[0]
                    arguments.pop(0)
                    
                    doc = inspect.getdoc(member)
                    
                    method_info = {
                        "name" : member_name,
                        "arguments" : arguments,
                        "description" : doc
                    }
                    
                    if hasattr(member, "arguments"):
                        method_info["arguments"] = getattr(member, "arguments")
                    
                    resources.append(method_info)


        data = {
            "response" : {
                "resources" : resources,
                "name" : cherrypy.request.path_info.split(".")[0], #@UndefinedVariable
                "description" : inspect.getdoc(self)
            }
        }

        return data



class ErrorController(RESTController):
    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"


class Root(RESTController):
    """
        A standard RESTController designed to display a list of child RESTControllers in the top level index.
    """
    def __init__(self, name):
        self.name = name
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
        self.exclude_members = []
        self.exclude_members.append("templateFilePath")
    
    
    @cherrypy.expose
    @service_format()
    def index(self):
        
        services = []

        for member_info in inspect.getmembers(self):
            member_name = member_info[0]
            member = member_info[1]
            
            if member_name in self.exclude_members:
                continue
            
            if not inspect.ismethod(member) and member_name.find("_") == -1 :
                services.append("/"+member_name +"/")
            
        services.append("/error_codes")
            
        data = {
            "response" : {
                "name" : self.name,
                "services" : services
            }
        }        
        return data
    
    
    
    @cherrypy.expose
    @service_format("error_codes")
    def error_codes(self):
        """
            A special web method for displaying to the users valid error codes. 
        """
        codes = []
        
        codes.append ( { "type" : "RUNTIME_ERROR", "code" : -1  } )
        codes.append ( { "type" : "SERVER_ERROR", "code" : 0 } )
        
        for code_type in ERROR_CODES:
            code_value = ERROR_CODES[code_type]
            codes.append ( {"type" : code_type, "code" : code_value })
        
        data = {
            "response" : {
                "name" : "error_codes",
                "error_codes" : codes
            }
        }
        return data


class XMLFilter(Filter):
    
    def __init__(self, template=None):
        super(XMLFilter, self).__init__(template)
    
    def filter(self, val, encoding=None, str=str, **kw):
        unquoted = super(XMLFilter, self).filter(val, encoding, str, **kw)
        return quoteattr(unquoted)
    

class Formatter(object):
    """
        A class to handle all the formatting, invoked by web methods after they have generated their data structures. 
    """
    
    def __init__(self, data, templateFilePath = None):
        self.data = data
        
        self.templateFilePaths = []
        self.templateFilePaths.append (os.path.dirname(__file__) + "/../tpl/")
        
        if templateFilePath != None and templateFilePath not in self.templateFilePaths:
            self.templateFilePaths.append(templateFilePath)
    
    def formatJSON(self):
        return json.dumps(self.data, indent=4, sort_keys=True) 
        
    def formatXML(self, templateFile = None):
        
        if templateFile != None:
            logger.debug("Using template file %s" % templateFile)
            for templateFilePath in self.templateFilePaths:
                tplfile = templateFilePath + templateFile
                # print tplfile
                if os.path.isfile(tplfile):
                    tpl = Template(file=tplfile, searchList=self.data, filter=XMLFilter)
                    return tpl
            logger.error("Could not find template file %s" % tplfile)
            logger.error("Falling back to generic XML generation.")
        
        
        # logger.debug(json.dumps(self.data, indent=4, sort_keys=True))
        
        # we know that the error XMLs have a template, so we don't need to worry about this
        # code not working for error data structures - because error data structures are
        # slightly different to results data structures
        # if that changes, then this will have to change too
        
        # if no template could be found, do it generically
        impl = xml.dom.minidom.getDOMImplementation()
        self.xml = impl.createDocument(None, None, None)
        
        root = self.xml.createElement("response")
        root.attributes["name"] = self.data["response"]["name"]
        self.xml.childNodes.append(root)
        
        results_container = self.xml.createElement("results")
        root.childNodes.append(results_container)
        
        for k,v in self.data["response"].items():
            if k != "name":
                self._parseXML(results_container, v, k)
        
        # print (self.xml.toprettyxml())
        return self.xml.toxml()
    
    
    def _parseXML(self, node, data, node_name, attribute = False):
        
        if type(data) is types.ListType:
            
            sub = self.xml.createElement(node_name)
            node.childNodes.append(sub)
            
            for val in data:
                sub_node_name = self._singularize(node_name)
                self._parseXML(sub, val, sub_node_name )
                
        elif type(data) is types.DictType:
            
            sub = self.xml.createElement(node_name)
            node.childNodes.append(sub)
            
            for key, val in data.items():
                self._parseXML(sub, val, key, True)
                
        else:
            
            if attribute is True:
                node.attributes[node_name] = str(data)
            else:
                
                sub = self.xml.createElement(node_name)
                node.childNodes.append(sub)
                
                t = self.xml.createTextNode(str(data))
                sub.childNodes.append(t)
        
        
    def _singularize(self, plural):
        """
           A highly simplistic plural to singular conversion attempt. Add to it as needed.
        """
        singular = plural
        if plural.endswith("s"):
            singular = plural[0 : len(plural) -1]
        elif plural == "children":
            singular = "child"
        else:
            singular = plural + "_item"
        return singular
    


def main():
    pass


if __name__ == '__main__':
    main()

