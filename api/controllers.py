#!/usr/bin/env python
# encoding: utf-8
"""
controllers.py

Created by Giles Velarde on 2010-02-04.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import os
import cherrypy

import logging

logger = logging.getLogger("charpy.controllers")

from ropy.server import RESTController, jsonp
from api import FeatureAPI, OrganismAPI



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
    @jsonp
    def changes(self, since, taxonomyID):
        """
            Reports all the features that have changed since a certain date.
        """
        self.init_handler()
        data = self.api.changes(since, taxonomyID)
        return self.format(data, "changes");
    changes.arguments = { "since" : "date formatted as YYYY-MM-DD", "taxonomyID" : "the NCBI taxonomy ID"  }
    
    
    @cherrypy.expose
    @jsonp
    def annotation_changes(self, taxonomyID, since):
        """
            Reports all the genes that have been highlighted as having annotation changes.
        """
        self.init_handler()
        data = self.api.annotation_changes(taxonomyID, since)
        return self.format(data, "private_annotations");
    annotation_changes.arguments = { "since" : "date formatted as YYYY-MM-DD", "taxonomyID" : "the NCBI taxonomy ID" }
    
    
    @cherrypy.expose
    @jsonp
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
       self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
    
    def init_handler(self):
       self.api = FeatureAPI(cherrypy.thread_data.connectionFactory)
       super(SourceFeatureController, self).init_handler()
       
    
    @cherrypy.expose
    @jsonp
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
    @jsonp
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
    
    # use example of how to make an alchemy controller...
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
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
    
    def init_handler(self):
        self.api = OrganismAPI(cherrypy.thread_data.connectionFactory)
        super(OrganismController, self).init_handler()
    
    
    @cherrypy.expose
    @jsonp
    def changes(self, since):
        """
            Reports all the organisms, their taxononmyIDs and a count of how many features have changed since a certain date.
        """
        self.init_handler()
        data = self.api.changes(since)
        return self.format(data, "genomes_changed");
    changes.arguments = { "since" : "date formatted as YYYY-MM-DD" }
    
    
    @cherrypy.expose
    @jsonp
    def list(self):
        """
            Lists all organisms and their taxonomyIDs. 
        """
        self.init_handler()
        data = self.api.getAllOrganismsAndTaxonIDs()
        return self.format(data)
    list.arguments = {}
    



class TestController(RESTController):
    """
        Test related queries.
    """

    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"

    def init_handler(self):
        self.api = OrganismAPI(cherrypy.thread_data.connectionFactory)
        super(TestController, self).init_handler()

    
    @cherrypy.expose
    @jsonp
    def forceclose(self):
        """
            Forces the connection to be closed for testing.
        """
        self.init_handler()
        cherrypy.thread_data.connectionFactory.getSingleConnection().close()
        
        data = {
            "response" : {
                "closed" : "true"
            }
        }
        return self.format(data)
    forceclose.arguments = {}
    
    @cherrypy.expose
    @jsonp
    def test(self):
        """
            Runs a query.
        """
        self.init_handler()
        data = self.api.getAllOrganismsAndTaxonIDs()
        return self.format(data)
    test.arguments = {}
    