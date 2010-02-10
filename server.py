
import optparse
import os
import sys

import logging
import logging.config

import cherrypy
from cherrypy.process import plugins

import ropy
from ropy.server import Root, handle_error, error_page_default, generate_mappings
from ropy.query import ConnectionFactory


import api.controllers

logger = logging.getLogger("charpy")

# note, should these two listeners might be moved into the ropy.server module? the setup depends on cherrypy.config['Connection'], which may be considered to be an app specific setting.
def setup_connection(thread_index):
    """
        make one connection per thread at startup
    """
    # expecting to find a Connection in section in the config 
    connection_details = cherrypy.config['Connection'] # connection_details = cherrypy.config.app['Connection']
    host = connection_details['host']
    database = connection_details["database"]
    user = connection_details["user"]
    password = connection_details["password"]

    cherrypy.thread_data.connectionFactory = ConnectionFactory(host, database, user, password)
    logger.debug ("setup connection in thread " + str(thread_index) + " ... is in thread_data? " + str(hasattr(cherrypy.thread_data, "connectionFactory")) )


def close_connection(thread_index):
    """
        close the connections when the server stops
    """
    logger.info ("attempting to close connection in thread " + str(thread_index))
    if hasattr(cherrypy.thread_data, "connectionFactory"):
        cherrypy.thread_data.connectionFactory.closeConnection()
    else:
        logger.debug ("no connection to close in thread " + str(thread_index))




def main():
    
    # get the options
    parser = optparse.OptionParser()
    parser.add_option("-a", "--appconf", dest="appconf", action="store", help="the path to the application configuration file")
    parser.add_option("-s", "--serverconf", dest="serverconf", action="store", help="the path to the server configuration file")
    parser.add_option("-l", "--logconf", dest="logconf", action="store", help="the path to the logging configuration file")
    parser.add_option('-d', action="store_true", dest='daemonize', help="run as daemon")
    parser.add_option('-p', '--pidfile', dest='pidfile', default=None, help="store the process id in the given file")
    parser.add_option('-t', '--test', dest='test', action="store_true", default=False, help="switch on testing controllers")
    
    
    (options, args) = parser.parse_args()
    
    for option in ['appconf', 'serverconf', 'logconf']:
        if getattr(options, option) == None:
            print "Please supply a --%s parameter.\n" % (option)
            parser.print_help()
            sys.exit()
    
    try:
        logging.config.fileConfig(options.logconf, disable_existing_loggers=False)
    except Exception, e:
        print "Warning: could not setup logging with disable_existing_loggers=False flag."
        logging.config.fileConfig(options.logconf)
    
    # make a tree of controller instances
    root = Root()
    root.genes = api.controllers.FeatureController()
    root.organisms = api.controllers.OrganismController()
    root.sourcefeatures = api.controllers.SourceFeatureController()
    
    if options.test == True:
        root.testing = api.controllers.TestController()
    
    # we want to use a custom dispatcher that's configured to know about .json and .xml extensions
    mapper = cherrypy.dispatch.RoutesDispatcher()
    generate_mappings(root, mapper)
    
    
    # global settings that should be in the conf file
    cherrypy.config.update(options.appconf)
    
    # global settings that should not be in the config file
    cherrypy.config.update({
        'request.error_response' : handle_error,
        'error_page.default' : error_page_default,
    })
    
    
    
    # app specific settings
    cherrypy.config.update(options.serverconf)
    
    # app specific settings
    appconfig = {
        '/' : {
            'request.dispatch' : mapper,
            # 'tools.SATransaction.on' : True,
            # 'tools.SATransaction.echo' : False,
            # 'tools.SATransaction.convert_unicode' : True,
            'tools.PGTransaction.on' : True
        }
    }
    
    
    # assign these listeners to manage connections per thread
    cherrypy.engine.subscribe('start_thread', setup_connection)
    cherrypy.engine.subscribe('stop_thread', close_connection)
    
    # import the tools before starting the server
    # import ropy.alchemy.sqlalchemy_tool
    import ropy.psy.psycopg2_tool
    
    # cherrypy.log.access_log.setLevel(logging.DEBUG)
    
    # cherrypy.quickstart(root, "/", options.conf)
    app = cherrypy.tree.mount(root, "/", appconfig)
    
    engine = cherrypy.engine
    
    if options.daemonize:
        cherrypy.config.update({'log.screen': False})
        plugins.Daemonizer(engine).subscribe()

    if options.pidfile:
        plugins.PIDFile(engine, options.pidfile).subscribe()
    
    if hasattr(engine, "signal_handler"):
        engine.signal_handler.subscribe()
    if hasattr(engine, "console_control_handler"):
        engine.console_control_handler.subscribe()
    
    logger.info ("Starting")
    
    try:
        engine.start()
    except:
        sys.exit(1)
    else:
        engine.block()
    
    

if __name__ == '__main__':
    main()

