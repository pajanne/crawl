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
from db import Queries

logger = logging.getLogger("charpy")

class FeatureAPI(object):
    
    def __init__(self, connectionFactory):
        self.queries = Queries(connectionFactory)
    
    def changes(self, since, taxonID):
        logger.debug(since)
        logger.debug(taxonID)
        organism_id = self.queries.getOrganismFromTaxon(taxonID)
        changed_features = self.queries.getAllChangedFeaturesForOrganism(since, organism_id)
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
        organism_id = self.queries.getOrganismFromTaxon(taxonID)
        print organism_id
        rows = self.queries.getGenesWithPrivateAnnotationChanges(organism_id, since)
        
        print rows
        
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
        rows = self.queries.getSourceFeatureSequence(uniqueName)
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
    
    def getFeatureLoc(self, sourceFeatureUniqueName, start, end, relationships):
        sourceFeatureID = self.queries.getFeatureID(sourceFeatureUniqueName)
        
        relationship_ids = []
        for relationship in relationships:
            relationship_ids.append(self.queries.getCvtermID("relationship", relationship))
        
        rows = self.queries.getFeatureLocs(sourceFeatureID, start, end, relationship_ids)
        
        # an to place the root level results
        featurelocs = []
        
        # a temporary hash store, keyed on uniquename, that keeps track of what features have
        # been generated so far... 
        result_map = {}
        
        for r in rows:
            
            root = None
            if r['l1_uniquename'] in result_map:
                root = result_map[r['l1_uniquename']]
            else:
                root = {
                    "uniquename" : r["l1_uniquename"],
                    "start" : r["l1_fmin"],
                    "end" : r["l1_fmax"],
                    "strand" : r["l1_strand"],
                    "phase" : r["l1_phase"],
                    "seqlen" : r["l1_seqlen"],
                    "relationship_type" : "",
                    "type" : r["l1_type"],
                    "is_obsolete" : r["l1_is_obsolete"],
                    "feature_id" : r["l1_feature_id"],
                    "parent" : "",
                    "features" : []
                }
                result_map[r['l1_uniquename']] = root
                featurelocs.append(root)
            
            if r['l2_uniquename'] != "None": 
                logger.debug(r['l2_uniquename'])
                if r['l2_uniquename'] in result_map:
                    l2 = result_map[r['l2_uniquename']]
                else:
                    l2 = {
                        "uniquename" : r["l2_uniquename"],
                        "start" : r["l2_fmin"],
                        "end" : r["l2_fmax"],
                        "strand" : r["l2_strand"],
                        "phase" : r["l2_phase"],
                        "seqlen" : r["l2_seqlen"],
                        "relationship_type" : r["l2_reltype"],
                        "type" : r["l2_type"],
                        "is_obsolete" : r["l2_is_obsolete"],
                        "feature_id" : r["l2_feature_id"],
                        "parent" : root["uniquename"],
                        "features" : []
                    }
                    root["features"].append(l2)
                    result_map[r['l2_uniquename']] = l2
            
            if r['l3_uniquename'] != "None": 
                if r['l3_uniquename'] in result_map:
                    l3 = result_map[r['l3_uniquename']]
                else:
                    l3 = {
                        "uniquename" : r["l3_uniquename"],
                        "start" : r["l3_fmin"],
                        "end" : r["l3_fmax"],
                        "strand" : r["l3_strand"],
                        "phase" : r["l3_phase"],
                        "seqlen" : r["l3_seqlen"],
                        "relationship_type" : r["l3_reltype"],
                        "type" : r["l3_type"],
                        "is_obsolete" : r["l2_is_obsolete"],
                        "feature_id" : r["l2_feature_id"],
                        "parent" : l2["uniquename"],
                        "features" : []
                    }
                    l2["features"].append(l3)
                    result_map[r['l3_uniquename']] = l3
        
        results_map = None
        
        data = {
            "response" : {
                "name" : "sourcefeatures/featureloc", 
                "uniqueName" : sourceFeatureUniqueName,
                "features" : featurelocs
            }
        }
        return data

    def getTopLevel(self, taxonID):
       organism_id = self.queries.getOrganismFromTaxon(taxonID)
       results = self.queries.getTopLevel(organism_id)
       
       data = {
           "response" : {
               "name" : "genes/top",
               "taxonId" : taxonID,
               "features" : results
           }
       }
       
       return data
    
    def getFeatureProps(self, uniquenames):
        
        results = self.queries.getFeatureProps(uniquenames)
        
        prop_dict = {}
        prop_list = []
        
        for r in results:
            uniquename = r.pop("uniquename")
            
            if uniquename not in prop_dict:
                prop_dict[uniquename] = {
                    "uniquename" : uniquename,
                    "props" : []
                }
                prop_list.append(prop_dict[uniquename])
            
            this_feature_prop = prop_dict[uniquename]
            this_feature_prop["props"].append(r)
            
        
        prop_dict = None
        
        data = {
            "response" : {
                "name" : "genes/featureproperties",
                "features" : prop_list
            }
        }
        return data
    

class OrganismAPI(object):
    
    def __init__(self, connectionFactory):
        self.queries = Queries(connectionFactory)
    
    def getAllOrganismsAndTaxonIDs(self):
        organism_list = self.queries.getAllOrganismsAndTaxonIDs()
        
        data = {
            "response" : {
                "name" : "organisms/list",
                "organisms" : organism_list
            }
        }
        return data
    
    def changes(self, since):
        logger.debug(since)
        
        organism_list = self.queries.getAllOrganismsAndTaxonIDs()
        
        organismIDs = []
        organismHash = {}
        for organism_details in organism_list:
            organism_details["count"] = 0
            organismIDs.append(organism_details["organism_id"])
            organismHash [organism_details["organism_id"]] = organism_details
        
        counts = self.queries.countAllChangedFeaturesForOrganisms(since, organismIDs)
        
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

