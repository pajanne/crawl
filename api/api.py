#!/usr/bin/env python
# encoding: utf-8
"""
api.py

Created by Giles Velarde on 2009-10-27.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.

This module defines low-level API calls. Methods here usually only do one SQL query, and return simple lists
or dictionaries.

"""


import os
import sys
import time
import logging

from ropy.query import QueryProcessor
from ropy.server import ServerException, RopyServer

logger = logging.getLogger("charpy")

class WhatsNew(QueryProcessor):
    
    def __init__(self, connectionFactory):
        super(WhatsNew, self).__init__(connection=connectionFactory, single=True)
        
        
        # reset the path to this the sql subfolder at the location class
        self.setSQLFilePath(os.path.dirname(__file__) + "/../sql/")
        
        self.addQueryFromFile("all_changed", "all_changed_features_for_organism.sql")
        self.addQueryFromFile("get_organism_from_taxon", "get_organism_id_from_taxon_id.sql")
        self.addQueryFromFile("get_all_privates_with_dates", "get_all_privates_with_dates.sql")
        self.addQueryFromFile("count_changed_features_organism", "count_changed_features_organism.sql")
        self.addQueryFromFile("get_all_organisms_and_taxon_ids", "get_all_organisms_and_taxon_ids.sql")
        
        self.addQueryFromFile("count_all_changed_features", "count_all_changed_features.sql")
        self.addQueryFromFile("source_feature_sequence", "source_feature_sequence.sql")
        self.addQueryFromFile("feature_locs", "feature_locs.sql")
        self.addQueryFromFile("get_feature_id_from_uniquename", "get_feature_id_from_uniquename.sql")
        self.addQueryFromFile("get_cvterm_id", "get_cvterm_id.sql")
        
        self.addQueryFromFile("get_top_level", "get_top_level.sql")
        
    
    def getAllChangedFeaturesForOrganism(self, date, organism_id):
        self.validateDate(date)
        rows = self.runQueryAndMakeDictionary("all_changed", (date, organism_id, date, organism_id, date, organism_id))
        return rows
    
    def getOrganismFromTaxon(self, taxonID):
        rows = self.runQuery("get_organism_from_taxon", (taxonID, ))
        try:
            # return the first value of the first row... 
            return rows[0][0]
        except:
            raise ServerException("Could not find organism for taxonID " + taxonID, RopyServer.ERROR_CODES["DATA_NOT_FOUND"])
    
    def getGenesWithPrivateAnnotationChanges(self, organism_id, since):
        returned = self.runQueryAndMakeDictionary("get_all_privates_with_dates", ("%curator_%", organism_id, 'date_%' ))
        sinceDate = time.strptime(since,"%Y-%m-%d")
        results = []
        for result in returned:
            resultDate = time.strptime(result["changedate"] ,"%Y-%m-%d")
            # print time.strftime("%Y-%m-%d",resultDate) + ">=" + time.strftime("%Y-%m-%d",sinceDate) + " = " + str(resultDate >= sinceDate)
            if (resultDate >= sinceDate):
                results.append(result)
        return results
    
    def countAllChangedFeaturesForOrganism(self, organism_id, since):
        self.validateDate(since)        
        rows = self.runQuery("count_changed_features_organism", (organism_id, since))
        count = rows[0][0]
        logger.debug ( str(organism_id) + " - " + since + " - " + str(count) )
        return count
    
    def countAllChangedFeaturesForOrganisms(self, since, organismIDs):
        ids = tuple (organismIDs) # must convert arrays to tuples
        rows = self.runQuery("count_all_changed_features", (since, ids) );
        return rows
    
    def getAllOrganismsAndTaxonIDs(self):
        return self.runQueryAndMakeDictionary("get_all_organisms_and_taxon_ids")
    
    
    def getSourceFeatureSequence(self, uniqueName):
        rows = self.runQueryAndMakeDictionary("source_feature_sequence", (uniqueName, ))
        return rows
    
    def getCvtermID(self, cvname, cvtermname ):
        args = {"cvtermname" : cvtermname, "cvname" : cvname }
        rows = self.runQuery("get_cvterm_id", args)
        return rows[0][0]
    
    def getFeatureLocs(self, source_feature_id, start, end, relationships):
        args = {
            "sourcefeatureid": source_feature_id,
            "start":start,
            "end":end,
            "relationships":tuple(relationships), # must convert arrays to tuples
        }
        rows = self.runQueryAndMakeDictionary("feature_locs", args)
        
        # the returned results
        results = []
        
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
                    "parent" : "",
                    "features" : []
                }
                result_map[r['l1_uniquename']] = root
                results.append(root)
            
            if r['l2_uniquename'] != None: 
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
                        "parent" : root["uniquename"],
                        "features" : []
                    }
                    root["features"].append(l2)
                    result_map[r['l2_uniquename']] = l2
            
            if r['l3_uniquename'] != None: 
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
                        "parent" : l2["uniquename"],
                        "features" : []
                    }
                    l2["features"].append(l3)
                    result_map[r['l3_uniquename']] = l3
        
        results_map = None
        return results
    
    def getTopLevel(self, organism_id):
        rows = self.runQuery("get_top_level", (organism_id, ))
        
        results = []
        for r in rows:
            results.append(r[0])
        
        return results

    def getFeatureID(self, uniqueName):
        try:
            rows = self.runQuery("get_feature_id_from_uniquename", (uniqueName, ))
            return rows[0][0]
        except Exception, e:
            logger.error(e)
            se = ServerException("Could not find a feature with uniqueName of " + uniqueName + ".", RopyServer.ERROR_CODES["DATA_NOT_FOUND"])
            raise ServerException, se
    
    def validateDate(self, date):
        try:
            c = time.strptime(date,"%Y-%m-%d")
        except Exception, e:
            # print "date " + date
            logger.error(e)
            se = ServerException("Invalid date: please supply a valid date markes in 'YYYY-MM-DD' format.", RopyServer.ERROR_CODES["INVALID_DATE"])
            raise ServerException, se


def main():
    pass


if __name__ == '__main__':
    main()

