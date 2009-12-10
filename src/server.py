import sys
import os
import ConfigParser

from high_level_api import FeatureAPI, OrganismAPI
from ropy.server import RopyServer, RESTController, Root
from ropy.query import ConnectionFactory

from setup import *

class FeatureController(RESTController):
    """
        Feature related queries.
    """
    
    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
        self.api = FeatureAPI(connectionFactory)
    
    def changes_xml(self, since, taxonomyID):
        return self.changes(since, taxonomyID)
    changes_xml.exposed = True
    
    def changes_json(self, since, taxonomyID):
        return self.changes(since, taxonomyID)
    changes_json.exposed = True
    

    def changes(self, since, taxonomyID):
        """
            Reports all the features that have changed since a certain date.
        """
        self.init_handler()
        data = self.api.changes(since, taxonomyID)
        return self.format(data, "changes");
    changes.exposed = True
    changes.arguments = { "since" : "date formatted as YYYY-MM-DD", "taxonomyID" : "the NCBI taxonomy ID"  }
    
    
    def annotation_changes_json(self, taxonomyID):
        return self.annotation_changes(taxonomyID)
    annotation_changes_json.exposed = True
    
    def annotation_changes_xml(self, taxonomyID):
        return self.annotation_changes(taxonomyID)
    annotation_changes_xml.exposed = True
    
    def annotation_changes(self, taxonomyID, since):
        """
            Reports all the genes that have been highlighted as having annotation changes.
        """
        self.init_handler()
        data = self.api.annotation_changes(taxonomyID, since)
        return self.format(data, "private_annotations");
    annotation_changes.exposed = True
    annotation_changes.arguments = { "since" : "date formatted as YYYY-MM-DD", "taxonomyID" : "the NCBI taxonomy ID" }
    
    
class SourceFeatureController(RESTController):
    """
        Source feature related queries.
    """
    
    def __init__(self):
       self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
       self.api = FeatureAPI(connectionFactory)
       
    def sequence_xml(self, uniqueName, start, end):
        return self.sequence(uniqueName, start, end)
    sequence_xml.exposed = True
    def sequence_json(self, uniqueName, start, end):
        return self.sequence(uniqueName, start, end)
    sequence_json.exposed = True
       
    def sequence(self, uniqueName, start, end):
        """
            Returns the sequence of a source feature.
        """
        self.init_handler()
        data = self.api.getSoureFeatureSequence(uniqueName, start, end)
        return self.format(data, "source_feature_sequence");
    sequence.exposed = True
    sequence.arguments = { 
        "uniqueName" : "the uniqueName of the source feature" ,
        "start" : "the start position in the sequence that you wish to retrieve (counting from 1)",
        "end" : "the end position in the sequence that you wish to retrieve (counting from 1)"
    }
    
    
    def featureloc_xml(self, uniqueName, start, end):
        return self.featureloc(uniqueName, start, end)
    featureloc_xml.exposed = True
    def featureloc_json(self, uniqueName, start, end):
        return self.featureloc(uniqueName, start, end)
    featureloc_json.exposed = True
    
    def featureloc(self, uniqueName, start, end):
        """
            Returns information about all the features located on a source feature within min and max boundaries.
        """
        self.init_handler()
        data = self.api.getFeatureLoc(uniqueName, start, end)
        return self.format(data, "featureloc");
    featureloc.exposed = True
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
        self.api = OrganismAPI(connectionFactory)
    
    def changes_json(self, since):
        return self.changes(since)
    changes_json.exposed = True
    
    def changes_xml(self, since):
        return self.changes(since)
    changes_xml.exposed = True
    
    def changes(self, since):
        """
            Reports all the organisms, their taxononmyIDs and a count of how many features have changed since a certain date.
        """
        self.init_handler()
        data = self.api.changes(since)
        return self.format(data, "genomes_changed");
    changes.exposed = True
    changes.arguments = { "since" : "date formatted as YYYY-MM-DD" }
    

config = None
if production == "True":
    print "Going into production"
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

RopyServer(root, config)



