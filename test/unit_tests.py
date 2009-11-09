#!/usr/bin/env python
# encoding: utf-8
"""
business_tests.py

Created by Giles Velarde on 2009-10-27.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import ConfigParser
import os
import json
import sys
import unittest


from business.api import WhatsNew
from ropy.client import RopyClient, ServerReportedException
from ropy.server import Formatter
from ropy.util import LogConf


config = ConfigParser.ConfigParser()
config.read(os.path.dirname(__file__) + '/../conf/config.ini')

host=config.get('Connection', 'host')
database=config.get('Connection', 'database')
user=config.get('Connection', 'user')
password=config.get('Connection', 'password')

LogConf.logpath=config.get('Logging', 'path')

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
        
        formatter = Formatter(data, os.path.dirname(__file__) + "/../tpl/")
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
        
        formatter = Formatter(data, os.path.dirname(__file__) + "/../tpl/")
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
        
        formatter = Formatter(data, os.path.dirname(__file__) + "/../tpl/")
        formatter.formatJSON()

class ClientServerTests(unittest.TestCase):
    
    def test1(self):
        
        client = RopyClient("http://localhost:6666/", os.path.dirname(__file__) + "/../view/")
        
        parameters = {
            "since" : "2009-06-10",
            "taxonomyID" : "420245"
        }
        
        xml_data =  client.request("genes/changes.xml", parameters)
        
        print xml_data.toxml()
        
        json_data = client.request("genes/changes.json", parameters)
        
        print json.dumps(json_data, sort_keys=True, indent=4)

    def testErrors(self):
        
        client = RopyClient("http://localhost:6666/")
        
        parameters = {
            "since" : "222222009-06-10",
            "taxonomyID" : "420245"
        }
        
        try:
            client.request("genes/changes.json", parameters)
            
        except ServerReportedException, se:
            
            json_data = se.value
            
            response = json_data['response']
            
            self.assertTrue("error" in response)
            
        except:
            self.fail("should throw a server reported exception")
    
    

def main():
	pass


if __name__ == '__main__':
	unittest.main()

