#!/usr/bin/env python
# encoding: utf-8
"""
business_tests.py

Created by Giles Velarde on 2009-10-27.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import os
import unittest
import ConfigParser

from business.api import WhatsNew
from view.formatter import Formatter



config = ConfigParser.ConfigParser()
config.read(os.path.dirname(__file__) + '/../conf/config.ini')

host=config.get('Connection', 'host')
database=config.get('Connection', 'database')
user=config.get('Connection', 'user')
password=config.get('Connection', 'password')


class BusinessTests(unittest.TestCase):
    
    def setUp(self):
        self.whats_new = WhatsNew(host, database, user, password)
    
    def testAllChanged(self):
        since = "2009-06-01"
        organism_id = 14
        taxonomy_id = 420245
        changed_features = self.whats_new.getAllChangedFeaturesForOrganism(since, organism_id)
        
        data = {
            "response" : {
                "name" : "genome/changes",
                "taxonID" : "420245",
                "count" : len(changed_features),
                "since" : since,
                "results" : changed_features
            }
        }
        
        formatter = Formatter(data)
        formatter.formatJSON()
        formatter.formatTemplate("changes.xml.tpl")
        
    def testGetOrganismFromTaxon(self):
        taxonID = self.whats_new.getOrganismFromTaxon('420245')
        self.assertEquals(taxonID, 14)
    
    def testGetGenesWithPrivateAnnotationChanges(self):
        rows = self.whats_new.getGenesWithPrivateAnnotationChanges(14)
        
        data = {
            "response" : {
                "name" : "genome/recorded_annotation_changes",
                "taxonID" : "420245",
                "count" : len(rows),
                "results" : rows
            }
        }
        
        formatter = Formatter(data)
        formatter.formatTemplate('private_annotations.xml.tpl')
        formatter.formatJSON()
    
    def testAllOrganisms(self):
        since = "2009-06-01"
        
        organism_list = self.whats_new.getAllOrganismsAndTaxonIDs()
        for organism_details in organism_list:
            organism_details["count"] = self.whats_new.countAllChangedFeaturesForOrganism(organism_details["organism_id"], since)
        
        data = {
            "response" : {
                "name" : "genomes/changes",
                "since" : since,
                "results" : organism_list
            }
        }
        
        formatter = Formatter(data)
        formatter.formatJSON()

def main():
	pass


if __name__ == '__main__':
	unittest.main()

