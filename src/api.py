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
from ropy.server import RopyServer, ServerException

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
        ids = tuple (organismIDs)
        rows = self.runQuery("count_all_changed_features", (since, ids) );
        return rows
    
    def getAllOrganismsAndTaxonIDs(self):
        return self.runQueryAndMakeDictionary("get_all_organisms_and_taxon_ids")
    
    
    def getSourceFeatureSequence(self, uniqueName):
        rows = self.runQueryAndMakeDictionary("source_feature_sequence", (uniqueName, ))
        return rows
    
    def getFeatureLocs(self, sourceFeatureID, start, end, relationships):
        rows = self.runQueryAndMakeDictionary("feature_locs", (sourceFeatureID, start, end, start, end))
        
        ht = {}
        
        # make a hashtable of each row
        for r in rows:
            r["features"] = []
            ht[r["uniquename"]] = r
            
            
        # use the hash to nest children
        newRows = []
        for r in rows:
            
            add = False
            
            if r["relationship_type"] == "None":
                add = True
            elif str(r["relationship_type"]) in relationships:
                add = True
            
            if add == False:
                continue
            
            if r["parent"] in ht:
                if str(r["relationship_type"]) in relationships:
                    parent = ht[r["parent"]]
                    parent["features"].append(r)
                else:
                    s.append("NOT")
            else:
                newRows.append(r)
                
            
        ht = None
        rows = None
        
        return newRows
    
    def getFeatureID(self, uniqueName):
        try:
            rows = self.runQuery("get_feature_id_from_uniquename", (uniqueName, ))
            return rows[0][0]
        except Exception, e:
            logger.error(e)
            se = ServerException("Could not find a source feature with uniqueName of " + uniqueName + ".", RopyServer.ERROR_CODES["DATA_NOT_FOUND"])
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

