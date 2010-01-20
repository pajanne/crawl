import cherrypy
import ConfigParser
import os
import sys
import logging

import ropy

from high_level_api import FeatureAPI, OrganismAPI
from ropy.server import RopyServer, RESTController, Root
from ropy.query import ConnectionFactory

from setup import *

logger = logging.getLogger("charpy")

def setup_connection(thread_index):
    from setup import host, database, user, password
    cherrypy.thread_data.connectionFactory = ConnectionFactory(host, database, user, password)
    logger.info ("setup connection in thread " + str(thread_index) + " ... is in thread_data? " + str(hasattr(cherrypy.thread_data, "connectionFactory")) )


def close_connection(thread_index):
    logger.info ("attempting to close connection in thread " + str(thread_index))
    if hasattr(cherrypy.thread_data, "connectionFactory"):
        cherrypy.thread_data.connectionFactory.closeConnection()
    else:
        logger.info ("no connection to close in thread " + str(thread_index))

class FeatureController(RESTController):
    """
        Feature related queries.
    """
    
    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
    
    def init_handler(self):
        self.api = FeatureAPI(cherrypy.thread_data.connectionFactory)
        super(FeatureController, self).init_handler()
    
    @cherrypy.expose
    def changes_xml(self, since, taxonomyID):
        return self.changes(since, taxonomyID)
    
    @cherrypy.expose
    @ropy.server.jsonp
    def changes_json(self, since, taxonomyID):
        return self.changes(since, taxonomyID)
    
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
    @ropy.server.jsonp
    def annotation_changes_json(self, taxonomyID):
        return self.annotation_changes(taxonomyID)
    
    @cherrypy.expose
    def annotation_changes_xml(self, taxonomyID):
        return self.annotation_changes(taxonomyID)
    
    @cherrypy.expose
    def annotation_changes(self, taxonomyID, since):
        """
            Reports all the genes that have been highlighted as having annotation changes.
        """
        self.init_handler()
        data = self.api.annotation_changes(taxonomyID, since)
        return self.format(data, "private_annotations");
    annotation_changes.arguments = { "since" : "date formatted as YYYY-MM-DD", "taxonomyID" : "the NCBI taxonomy ID" }
    
    
class SourceFeatureController(RESTController):
    """
        Source feature related queries.
    """
    
    def __init__(self):
       self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
    
    def init_handler(self):
       self.api = FeatureAPI(cherrypy.thread_data.connectionFactory)
       super(SourceFeatureController, self).init_handler()
       
    @cherrypy.expose
    def sequence_xml(self, uniqueName, start, end):
        return self.sequence(uniqueName, start, end)
    
    @cherrypy.expose
    @ropy.server.jsonp
    def sequence_json(self, uniqueName, start, end):
        return self.sequence(uniqueName, start, end)
    
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
    def featureloc_xml(self, uniqueName, start, end):
        return self.featureloc(uniqueName, start, end)
    
    @cherrypy.expose
    @ropy.server.jsonp
    def featureloc_json(self, uniqueName, start, end):
        return self.featureloc(uniqueName, start, end)
    
    @cherrypy.expose
    def featureloc(self, uniqueName, start, end):
        """
            Returns information about all the features located on a source feature within min and max boundaries.
        """
        self.init_handler()
        logger.debug(uniqueName + " : " + str(start) + " - " + str(end))
        data = self.api.getFeatureLoc(uniqueName, start, end)
        return self.format(data, "featureloc");
    featureloc.arguments = { 
        "uniqueName" : "the uniqueName of the source feature" ,
        "start" : "the start position of the feature locations that you wish to retrieve (counting from 1)",
        "end" : "the end position of the features locations that you wish to retrieve (counting from 1)"
    }
        

class OrganismController(RESTController):
    """
        Organism related queries.
    """
    
    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
    
    def init_handler(self):
        self.api = OrganismAPI(cherrypy.thread_data.connectionFactory)
        super(OrganismController, self).init_handler()
    
    @cherrypy.expose
    @ropy.server.jsonp
    def changes_json(self, since):
        return self.changes(since)
    
    @cherrypy.expose
    def changes_xml(self, since):
        return self.changes(since)
    
    @cherrypy.expose
    def changes(self, since):
        """
            Reports all the organisms, their taxononmyIDs and a count of how many features have changed since a certain date.
        """
        self.init_handler()
        data = self.api.changes(since)
        return self.format(data, "genomes_changed");
    changes.arguments = { "since" : "date formatted as YYYY-MM-DD" }
    

class WikiController(RESTController):
    """
        Wiki page extraction functions.
    """
    
    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
    
    @cherrypy.expose
    def page_xml(self, name):
        return self.page(name)
    
    
    @cherrypy.expose
    @ropy.server.jsonp
    def page_json(self, name):
        return self.page(name)
    
    @cherrypy.expose
    def page(self, name):
        """
            Returns the contents of a wiki page.
        """
        self.init_handler()
        from wiki.wikipy import getPage
        data = { 
            "response" : {
                "name" : "wiki/page",
                "page" : name,
                "data" : getPage(name)
            }
        }
        return self.format(data, None);
    page.arguments = { "name" : "the name of the page" }
    


config = None
if production == "True":
    logger.info("Going into production")
    config = {
        "environment": "production",
        "server.socket_port": 6666,
        "server.thread_pool": 10,
        "log.screen": False,
        "log.error_file": error_log,
        "log.access_file": access_log
    }


# the object construction tree defines the URL paths
root = Root()
root.genes = FeatureController()
root.organisms = OrganismController()
root.sourcefeatures = SourceFeatureController()
root.wiki = WikiController()

RopyServer(root, config, setup_connection, close_connection)



