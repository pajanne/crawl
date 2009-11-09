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

from api import WhatsNew
from ropy.util import dolog

class FeatureAPI(object):
    
    def __init__(self, host, database, user, password):
        self.api = WhatsNew(host, database, user, password)
    
    def changes(self, since, taxonID):
        dolog(since)
        dolog(taxonID)
        organism_id = self.api.getOrganismFromTaxon(taxonID)
        changed_features = self.api.getAllChangedFeaturesForOrganism(since, organism_id)
        data = {
            "response" : {
                "name" : "genome/changes",
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
                "name" : "genome/annotation_changes",
                "taxonomyID" : taxonID,
                "count" : len(rows),
                "results" : rows
            }
        }
        return data




class OrganismAPI(object):
    
    def __init__(self, host, database, user, password):
        self.api = WhatsNew(host, database, user, password)
    
    def changes(self, since):
        dolog(since)
        
        organism_list = self.api.getAllOrganismsAndTaxonIDs()
        for organism_details in organism_list:
            organism_details["count"] = self.api.countAllChangedFeaturesForOrganism(organism_details["organism_id"], since)
        
        data = {
            "response" : {
                "name" : "genomes/changes",
                "since" : since,
                "results" : organism_list
            }
        }
        return data

def main():
    pass


if __name__ == '__main__':
    main()

