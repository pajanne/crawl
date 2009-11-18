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
    
    
    def annotation_changes(self, taxonID):
        organism_id = self.api.getOrganismFromTaxon(taxonID)
        
        rows = self.api.getGenesWithPrivateAnnotationChanges(organism_id)
        
        data = {
            "response" : {
                "name" : "genes/annotation_changes",
                "taxonomyID" : taxonID,
                "count" : len(rows),
                "results" : rows
            }
        }
        return data




class OrganismAPI(object):
    
    def __init__(self, connectionFactory):
        self.api = WhatsNew(connectionFactory)
    
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
            print organismID
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

