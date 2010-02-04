import cherrypy
import optparse
import os
import sys
import logging
import logging.config
import logging.handlers

from logging.config import fileConfig

import ropy

from api.high_level_api import FeatureAPI, OrganismAPI
from ropy.server import RopyServer, RESTController, Root, handle_error, error_page_default

from ropy.query import ConnectionFactory

from ropy.alchemy.automapped import *

logger = logging.getLogger("charpy")







class FeatureController(RESTController):
    """
        Feature related queries.
    """
    
    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "tpl/"
    
    def init_handler(self):
        self.api = FeatureAPI(cherrypy.thread_data.connectionFactory)
        super(FeatureController, self).init_handler()
    
    
    @cherrypy.expose
    def changes(self, since, taxonomyID):
        """
            Reports all the features that have changed since a certain date.
        """
        self.init_handler()
        data = self.api.changes(since, taxonomyID)
        return self.format(data, "changes");
    changes.arguments = { "since" : "date formatted as YYYY-MM-DD", "taxonomyID" : "the NCBI taxonomy ID"  }
    
    
    @cherrypy.expose
    def annotation_changes(self, taxonomyID, since):
        """
            Reports all the genes that have been highlighted as having annotation changes.
        """
        self.init_handler()
        data = self.api.annotation_changes(taxonomyID, since)
        return self.format(data, "private_annotations");
    annotation_changes.arguments = { "since" : "date formatted as YYYY-MM-DD", "taxonomyID" : "the NCBI taxonomy ID" }
    
    
    @cherrypy.expose
    def top(self, taxonID):
        """
            Returns a list of top level features for an organism.
        """
        self.init_handler()
        
        data = self.api.getTopLevel(taxonID)
        return self.format(data)
    top.arguments = {
        "taxonID" : "the taxonID of the organism you want to browse"
    }
    
class SourceFeatureController(RESTController):
    """
        Source feature related queries.
    """
    
    def __init__(self):
       self.templateFilePath = os.path.dirname(__file__) + "tpl/"
    
    def init_handler(self):
       self.api = FeatureAPI(cherrypy.thread_data.connectionFactory)
       super(SourceFeatureController, self).init_handler()
       
    
    @cherrypy.expose
    def sequence(self, uniqueName, start, end):
        """
            Returns the sequence of a source feature.
        """
        self.init_handler()
        data = self.api.getSoureFeatureSequence(uniqueName, start, end)
        return self.format(data, "source_feature_sequence");
    sequence.arguments = { 
        "uniqueName" : "the uniqueName of the source feature" ,
        "start" : "the start position in the sequence that you wish to retrieve (counting from 1)",
        "end" : "the end position in the sequence that you wish to retrieve (counting from 1)"
    }
    
    
    @cherrypy.expose
    def featureloc(self, uniqueName, start, end, **kwargs):
        """
            Returns information about all the features located on a source feature within min and max boundaries.
        """
        self.init_handler()
        
        relationships = ["part_of", "derives_from"]
        
        relationships = self._make_array_from_kwargs("relationships", ["part_of", "derives_from"], **kwargs)
        
        logger.debug(uniqueName + " : " + str(start) + " - " + str(end))
        data = self.api.getFeatureLoc(uniqueName, start, end, relationships)
        return self.format(data, "featureloc");
    featureloc.arguments = { 
        "uniqueName" : "the uniqueName of the source feature" ,
        "start" : "the start position of the feature locations that you wish to retrieve (counting from 1)",
        "end" : "the end position of the features locations that you wish to retrieve (counting from 1)",
        "relationships" : "an optional array (i.e. it can be specified several times) detailing the relationship types you want to have, the defaults are [part_of, derives_from]"
    }
    
    
    
    
    
    def _make_array_from_kwargs(self, kw, default_array, **kwargs):
        import types
        if kw in kwargs:
            arr = kwargs[kw]
            if type(arr) is not types.ListType:
                arr = [arr]
        else:
            arr = default_array
        return arr
    
    # @cherrypy.expose
    #     def test(self):
    #         from ropy.alchemy.sqlalchemy_tool import session
    #         dbs = session.query(Db)
    #         s = []
    #         for db in dbs:
    #             s.append(db.name + "\n")
    #         return s

class OrganismController(RESTController):
    """
        Organism related queries.
    """
    
    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "tpl/"
    
    def init_handler(self):
        self.api = OrganismAPI(cherrypy.thread_data.connectionFactory)
        super(OrganismController, self).init_handler()
    
    
    @cherrypy.expose
    def changes(self, since):
        """
            Reports all the organisms, their taxononmyIDs and a count of how many features have changed since a certain date.
        """
        self.init_handler()
        data = self.api.changes(since)
        return self.format(data, "genomes_changed");
    changes.arguments = { "since" : "date formatted as YYYY-MM-DD" }
    
    
    @cherrypy.expose
    def list(self):
        """
            Lists all organisms and their taxonomyIDs. 
        """
        self.init_handler()
        data = self.api.getAllOrganismsAndTaxonIDs()
        return self.format(data)
    list.arguments = {}
    




def setup_connection(thread_index):

    connection_details = cherrypy.request.app.config['Connection']
    host = connection_details['host']
    database = connection_details["database"]
    user = connection_details["user"]
    password = connection_details["password"]

    # print host, database, user, password

    cherrypy.thread_data.connectionFactory = ConnectionFactory(host, database, user, password)
    logger.info ("setup connection in thread " + str(thread_index) + " ... is in thread_data? " + str(hasattr(cherrypy.thread_data, "connectionFactory")) )
    # print "setup " + str(thread_index)




def close_connection(thread_index):
    logger.info ("attempting to close connection in thread " + str(thread_index))
    if hasattr(cherrypy.thread_data, "connectionFactory"):
        cherrypy.thread_data.connectionFactory.closeConnection()
    else:
        logger.info ("no connection to close in thread " + str(thread_index))
    logger.info( "closing " + str(thread_index))


class PGTransaction(cherrypy.Tool):
    def __init__(self):
        self._name = 'PGTransaction'
        self._point = 'on_start_resource'
        self._priority = 100
        
    def _setup(self):
        cherrypy.request.hooks.attach('on_end_resource', self.on_end_resource)
        cherrypy.Tool._setup(self)

    def callable(self):
        logger.info (cherrypy.thread_data.connectionFactory.getSingleConnection())
        
    
    def on_end_resource(self):
        
        typ, value, trace = sys.exc_info()
        if value is not None:
            logger.error("exception detected")
            logger.error(typ)
            logger.error(value)
            logger.error(trace)
            logger.error(cherrypy.thread_data.connectionFactory.getSingleConnection())
            
            try:
                cherrypy.thread_data.connectionFactory.getSingleConnection().rollback()
            except Exception, e:
                logger.error("failed rollback")
                logger.error(e)
        else:
            logger.info (cherrypy.thread_data.connectionFactory.getSingleConnection())



def main():
    
    parser = optparse.OptionParser()
    parser.add_option("-c", "--conf", dest="conf", action="store", help="the path to the server configuration file")
    parser.add_option("-l", "--log", dest="log", action="store", help="the path to the logging configuration file")
    
    (options, args) = parser.parse_args()
    if options.conf == None: 
        print ("Please supply a --conf parameter.\n")
        sys.exit(parser.print_help())
        
    if options.log == None: 
        print ("Please supply a --log parameter.\n")
        sys.exit(parser.print_help())
    
    
    fileConfig(str(options.log))
    logger = logging.getLogger("loader")
    
    # the object construction tree defines the URL paths
    root = Root()
    root.genes = FeatureController()
    root.organisms = OrganismController()
    root.sourcefeatures = SourceFeatureController()
    
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 6666,
        'request.error_response' : handle_error,
        'error_page.default' : error_page_default
    })
    
    cherrypy.engine.subscribe('start_thread', setup_connection)
    cherrypy.engine.subscribe('stop_thread', close_connection)
    
    # import the tools before starting the server
    import ropy.alchemy.sqlalchemy_tool
    cherrypy.tools.PGTransaction = PGTransaction()
    
    # print cherrypy.config.get('server.environment')
    
    cherrypy.quickstart(root, "/", options.conf)
    
    
    
    

if __name__ == '__main__':
    main()

