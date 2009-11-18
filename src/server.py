import sys
import os
import ConfigParser

from high_level_api import FeatureAPI, OrganismAPI
from ropy.server import RopyServer, RESTController, Root
from ropy.query import ConnectionFactory

from setup import *

class FeatureController(RESTController):
    """
        Queries for feature related queries.
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
    
    def annotation_changes(self, taxonomyID):
        """
            Reports all the genes that have been highlighted as having annotation changes.
        """
        self.init_handler()
        data = self.api.annotation_changes(taxonomyID)
        return self.format(data, "private_annotations");
    annotation_changes.exposed = True
    annotation_changes.arguments = { "taxonomyID" : "the NCBI taxonomy ID"  }
    
    
    

class OrganismController(RESTController):
    """
        Queries for organism related queries.
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

RopyServer(root, config)



