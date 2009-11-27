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


from api import WhatsNew
from ropy.client import RopyClient, ServerReportedException
from ropy.server import Formatter
from ropy.query import ConnectionFactory

from setup import *

class BusinessTests(unittest.TestCase):
    
    def setUp(self):
        self.whats_new = WhatsNew(connectionFactory)
    
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
    
        organismIDs = []
        organismHash = {}
        for organism_details in organism_list:
            organism_details["count"] = 0
            organismIDs.append(organism_details["organism_id"])
            organismHash [organism_details["organism_id"]] = organism_details
    
        counts = self.whats_new.countAllChangedFeaturesForOrganisms(since, organismIDs)
    
        for count in counts:
            organismID = str(count[0])
            print organismID
            org = organismHash[organismID]
            org["count"] = count[1]
    
        data = {
            "response" : {
                "name" : "genomes/changes",
                "since" : since,
                "results" : organismHash.values()
            }
        }
    
        formatter = Formatter(data, os.path.dirname(__file__) + "/../tpl/")
        print formatter.formatTemplate('genomes_changed.xml.tpl')


    def testCountAllOrganisms(self):
        since = "2009-06-01"
        organismIDs = [12, 14, 15, 20]
    
        result = self.whats_new.countAllChangedFeaturesForOrganisms(since, organismIDs)
        print result


    def testGetSourceFeatureSequence(self):
        rows = self.whats_new.getSourceFeatureSequence("Pf3D7_01")
        row = rows[0]
        
        length = row["length"]
        start = 1
        end = 10
        
        dna = row["dna"]
        dna = dna[start-1:end-1]
        
        data = {
            "response" : {
                "name" : "source_feature/sequence",
                "sequence" :  {
                    "start" : start,
                    "end" : end,
                    "length" : length,
                    "dna" : dna
                }
            }
        }
        
        formatter = Formatter(data, os.path.dirname(__file__) + "/../tpl/")
        print formatter.formatJSON()

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
	unittest.main(argv=['charpy'])

