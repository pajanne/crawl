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


from ropy.query import QueryProcessor
from ropy.util import dolog
from ropy.server import RopyServer, ServerException



class WhatsNew(QueryProcessor):
    
    def __init__(self, host, database, user, password):
        super(WhatsNew, self).__init__(host, database, user, password)
        
        # reset the path to this the sql subfolder at the location class
        self.setSQLFilePath(os.path.dirname(__file__) + "/sql/")
        
        self.addQueryFromFile("all_changed", "all_changed_features_for_organism.sql")
        self.addQueryFromFile("get_organism_from_taxon", "get_organism_id_from_taxon_id.sql")
        self.addQueryFromFile("get_all_privates_with_dates", "get_all_privates_with_dates.sql")
        self.addQueryFromFile("count_changed_features_organism", "count_changed_features_organism.sql")
        self.addQueryFromFile("get_all_organisms_and_taxon_ids", "get_all_organisms_and_taxon_ids.sql")
    
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
            raise Exception("Could not find organism for taxonID " + taxonID)
    
    def getGenesWithPrivateAnnotationChanges(self, organism_id):
        return self.runQueryAndMakeDictionary("get_all_privates_with_dates", ("%curator_%", organism_id, 'date_%' ))
    
    def countAllChangedFeaturesForOrganism(self, organism_id, since):
        self.validateDate(since)        
        rows = self.runQuery("count_changed_features_organism", (organism_id, since))
        count = rows[0][0]
        dolog ( str(organism_id) + " - " + since + " - " + str(count) )
        return count
    
    def getAllOrganismsAndTaxonIDs(self):
        return self.runQueryAndMakeDictionary("get_all_organisms_and_taxon_ids")
    
    
    def validateDate(self, date):
        try:
            c = time.strptime(date,"%Y-%m-%d")
        except Exception, e:
            print "date " + date
            se = ServerException("Invalid date: please supply a valid date markes in 'YYYY-MM-DD' format.", RopyServer.ERROR_CODES.INVALID_DATE)
            raise ServerException, se


def main():
    pass


if __name__ == '__main__':
    main()

