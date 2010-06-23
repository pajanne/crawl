import optparse
import os
import sys
import imp

import logging
import util.logconfig

import cherrypy
from cherrypy.process import plugins

from ropy.server import Root, handle_error, error_page_default, generate_mappings
from ropy.query import ConnectionFactory

import api.controllers

logger = logging.getLogger("crawl")

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
    port = connection_details["port"]

    cherrypy.thread_data.connectionFactory = ConnectionFactory(host, database, user, password, port)
    logger.debug ("setup connection in thread " + str(thread_index) + " ... is in thread_data? " + str(hasattr(cherrypy.thread_data, "connectionFactory")) )


def close_connection(thread_index):
    """
        close the connections when the server stops
    """
    logger.info ("attempting to close connection in thread " + str(thread_index))
    if hasattr(cherrypy.thread_data, "connectionFactory"):
        cherrypy.thread_data.connectionFactory.close()
    else:
        logger.warn ("no connection factory to close in thread " + str(thread_index))


class StaticRoot(object):
    pass
    # @cherrypy.expose
    #     def index(self):
    #         return "hello <a href='testing/index.html'>testing....</a> "

def main():
    
    # get the options
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", dest="config", action="store", help="the path to the server configuration file")
    parser.add_option("-l", "--logging", dest="logging", action="store", help="the path to the logging configuration file")
    parser.add_option('-d', "--daemonize", dest='daemonize', action="store_true", help="run as daemon")
    parser.add_option('-p', '--pidfile', dest='pidfile', default=None, help="store the process id in the given file")
    parser.add_option('-t', '--test', dest='test', action="store_true", default=False, help="switch on testing controllers")
    
    (options, args) = parser.parse_args()
    for option in ['config', 'logging']:
          if getattr(options, option) == None:
              print "Please supply a --%s parameter.\n" % (option)
              parser.print_help()
              sys.exit()	
    
    # load the configuration
    config = imp.load_source("config" , options.config)
    
    try:
        import logging.config
        logging.config.fileConfig(options.logging, disable_existing_loggers=False)
        #util.logconfig.setup().add(config.log).apply()
        
    except Exception, e:
        print e
        print "Warning: could not setup logging with disable_existing_loggers=False flag."
        logging.config.fileConfig(options.logging)
    
    # make a tree of controller instances
    root = Root("Chado Restful Access Webservice Layer")
    root.genes = api.controllers.Genes()
    root.features = api.controllers.Features();
    root.organisms = api.controllers.Organisms()
    root.regions = api.controllers.Regions()
    root.histories = api.controllers.Histories()
    root.terms = api.controllers.Terms()
    
    if sys.platform[:4] != 'java':
        # currently the graph module depends on numpy
        root.graphs = api.controllers.Graphs()
    
    if options.test == True:
        root.testing = api.controllers.Testing()
    
    # we want to use a custom dispatcher that's configured to know about .json and .xml extensions
    mapper = cherrypy.dispatch.RoutesDispatcher()
    generate_mappings(root, mapper)
    
    
    # global settings that should be in the config file
    cherrypy.config.update(config.crawl)
    
    # global settings that should not be in the config file
    cherrypy.config.update({
        'request.error_response' : handle_error,
        'error_page.default' : error_page_default,
        'tools.proxy.on': True
    })
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # app specific settings, that we don't want set in the config file
    appconfig = {
        '/' : {
            'request.dispatch' : mapper,
            # 'tools.SATransaction.on' : True,
            # 'tools.SATransaction.echo' : False,
            # 'tools.SATransaction.convert_unicode' : True,
            'tools.PGTransaction.on' : True
        }
    }
    
    appconfig2 = {
        '/' : {
            'tools.staticdir.on': True,
            'tools.staticdir.index' : 'index.html',
            'tools.staticdir.dir': os.path.join(current_dir, 'htm/')
        }
    }
    
    #logger.debug(os.path.join(current_dir, 'htm/'))
    
    # assign these listeners to manage connections per thread
    cherrypy.engine.subscribe('start_thread', setup_connection)
    cherrypy.engine.subscribe('stop_thread', close_connection)
    
    # import the tools before starting the server
    # import ropy.alchemy.sqlalchemy_tool
    import ropy.psy.psycopg2_tool #@UnusedImport
    
    if sys.platform[:4] == 'java':
        cherrypy.config.update({'server.nodelay': False})
    
    ropy.server.serve()
    
    app = cherrypy.tree.mount(root, "/", appconfig)
    app2 = cherrypy.tree.mount(StaticRoot(), "/htm", appconfig2)
    
    #logger.debug(app)
    #logger.debug(app2)
    
    engine = cherrypy.engine
    
    if options.daemonize:
        cherrypy.config.update({'log.screen': False})
        plugins.Daemonizer(engine).subscribe()

    if options.pidfile:
        plugins.PIDFile(engine, options.pidfile).subscribe()
    
    # for some reason, accessing the signal handler currently breaks in Jython
    if hasattr(engine, "signal_handler") and sys.platform[:4] != 'java':
        engine.signal_handler.subscribe()
    
    if hasattr(engine, "console_control_handler"):
        engine.console_control_handler.subscribe()
    
    #logger.info ("Starting")
    
    try:
        engine.start()
    except:
        sys.exit(1)
    else:
        engine.block()
    
    

if __name__ == '__main__':
    main()

