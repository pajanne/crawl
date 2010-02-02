#!/usr/bin/env python
# encoding: utf-8
"""
high_level_api.py

Created by Giles Velarde on 2009-11-06.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.

This module defines high-level API calls, i.e. ones that string together one or more queries and return
the results back in a complex json-like structure.

"""

import sys
import os
import logging
from api import WhatsNew

logger = logging.getLogger("charpy")

class FeatureAPI(object):
    
    def __init__(self, connectionFactory):
        self.api = WhatsNew(connectionFactory)
    
    def changes(self, since, taxonID):
        logger.debug(since)
        logger.debug(taxonID)
        organism_id = self.api.getOrganismFromTaxon(taxonID)
        changed_features = self.api.getAllChangedFeaturesForOrganism(since, organism_id)
        data = {
            "response" : {
                "name" : "genes/changes",
                "taxonID" : taxonID,
                "count" : len(changed_features),
                "since" : since,
                "results" : changed_features
            }
        }
        return data
    
    
    def annotation_changes(self, taxonID, since):
        organism_id = self.api.getOrganismFromTaxon(taxonID)
        
        rows = self.api.getGenesWithPrivateAnnotationChanges(organism_id, since)
        
        data = {
            "response" : {
                "name" : "genes/annotation_changes",
                "taxonomyID" : taxonID,
                "count" : len(rows),
                "since" : since,
                "results" : rows
            }
        }
        return data
    
    def getSoureFeatureSequence(self, uniqueName, start, end):
        rows = self.api.getSourceFeatureSequence(uniqueName)
        row = rows[0]

        length = row["length"]
        dna = row["dna"]
        dna = dna[int(start)-1:int(end)-1]

        data = {
            "response" : {
                "name" : "sourcefeatures/sequence",
                "sequence" :  [{
                    "uniqueName" : uniqueName,
                    "start" : start,
                    "end" : end,
                    "length" : length,
                    "dna" : dna
                }]
            }
        }
        
        return data
    
    def getFeatureLoc(self, sourceFeatureUniqueName, start, end, relationships, root_types):
        sourceFeatureID = self.api.getFeatureID(sourceFeatureUniqueName)
        
        relationship_ids = []
        for relationship in relationships:
            relationship_ids.append(self.api.getCvtermID("relationship", relationship))
        
        featurelocs = self.api.getFeatureLocs(sourceFeatureID, start, end, relationship_ids, root_types)
        
        data = {
            "response" : {
                "name" : "sourcefeatures/featureloc", 
                "uniqueName" : sourceFeatureUniqueName,
                "features" : featurelocs
            }
        }
        return data

    def getTopLevel(self, taxonID):
       organism_id = self.api.getOrganismFromTaxon(taxonID)
       results = self.api.getTopLevel(organism_id)
       
       data = {
           "response" : {
               "name" : "genes/top",
               "taxonId" : taxonID,
               "features" : results
           }
       }
       
       return data


class OrganismAPI(object):
    
    def __init__(self, connectionFactory):
        self.api = WhatsNew(connectionFactory)
    
    def getAllOrganismsAndTaxonIDs(self):
        organism_list = self.api.getAllOrganismsAndTaxonIDs()
        
        data = {
            "response" : {
                "name" : "organisms/list",
                "organisms" : organism_list
            }
        }
        return data
    
    def changes(self, since):
        logger.debug(since)
        
        organism_list = self.api.getAllOrganismsAndTaxonIDs()
        
        organismIDs = []
        organismHash = {}
        for organism_details in organism_list:
            organism_details["count"] = 0
            organismIDs.append(organism_details["organism_id"])
            organismHash [organism_details["organism_id"]] = organism_details
        
        counts = self.api.countAllChangedFeaturesForOrganisms(since, organismIDs)
        
        for count in counts:
            organismID = str(count[0])
            # logger.debug (organismID)
            org = organismHash[organismID]
            org["count"] = count[1]
        
        data = {
            "response" : {
                "name" : "organisms/changes",
                "since" : since,
                "results" : organismHash.values()
            }
        }
        
        return data

def main():
    pass


if __name__ == '__main__':
    main()

