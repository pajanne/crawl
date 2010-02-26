#!/usr/bin/env python
# encoding: utf-8
"""
business_tests.py

Created by Giles Velarde on 2009-10-27.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import ConfigParser
import os
try:
    import simplejson as json
except ImportError:
    import json
import sys
import unittest
import optparse


from charpy.api.db import Queries

import ropy.query
from ropy.client import RopyClient, ServerReportedException
from ropy.server import Formatter



parser = optparse.OptionParser()
parser.add_option("-c", "--conf", dest="conf", action="store", help="the path to the configuration file")
(options, args) = parser.parse_args()
if options.conf == None: sys.exit("Please supply a conf parameter.")

config = ConfigParser.ConfigParser()
config.read(options.conf)

# cherrypy file-configs must be valid python expressions, they get eval()ed
host=eval(config.get('Connection', 'host'))
database=eval(config.get('Connection', 'database'))
user=eval(config.get('Connection', 'user'))
password=eval(config.get('Connection', 'password'))

connectionFactory = ropy.query.ConnectionFactory(host, database, user, password)

class FeatureLengthTest(unittest.TestCase):
    
    def setUp(self):
        self.queries = Queries(connectionFactory)
    
    def test1(self):
        result = self.queries.getFeatureLength("Pf3D7_01")
        print Formatter(result).formatJSON()



class GeneTests(unittest.TestCase):
     
    def setUp(self):
        self.queries = Queries(connectionFactory)
     
    def test1(self):
        print dir(self.queries)
        gene_results = self.queries.getCDSs(22)
        print Formatter(gene_results).formatJSON()[1:10000]
         
        genes = []
        for gene_result in gene_results:
            genes.append(gene_result["gene"])
        
        mrnas = self.queries.getMRNAs(genes)
        print Formatter(mrnas).formatJSON()[1:10000]
        
        peps = self.queries.getPEPs(genes)
        print Formatter(peps).formatJSON()[1:10000]


class BusinessTests(unittest.TestCase):
    
    def setUp(self):
        self.queries = Queries(connectionFactory)
    
    def testGetSourceFeatureSequence(self):
        data = self.queries.getFeatureLocs(1, 1, 100000, [42, 69])
        formatter = Formatter(data)
        # print formatter.formatJSON()
    
    def testGetTopLevel(self):
        taxonomy_id = 420245
        
        data = self.queries.getTopLevel(14)
        formatter = Formatter(data)
        print formatter.formatJSON()
    

class BusinessTests2(unittest.TestCase):
    
    def setUp(self):
        self.queries = Queries(connectionFactory)
    
    def testAllChanged(self):
            since = "2009-06-01"
            organism_id = 14
            taxonomy_id = 420245
            changed_features = self.queries.getAllChangedFeaturesForOrganism(since, organism_id)
        
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
            formatter.formatXML("changes.xml.tpl")
        
    def testGetOrganismFromTaxon(self):
        taxonID = self.queries.getOrganismFromTaxon('420245')
        self.assertEquals(taxonID, 14)
    
    def testGetGenesWithPrivateAnnotationChanges(self):
        since = "2009-06-01"
        rows = self.queries.getGenesWithPrivateAnnotationChanges(14, since)
    
        data = {
            "response" : {
                "name" : "genome/recorded_annotation_changes",
                "taxonID" : "420245",
                "count" : len(rows),
                "results" : rows
            }
        }
    
        formatter = Formatter(data, os.path.dirname(__file__) + "/../tpl/")
        formatter.formatXML('private_annotations.xml.tpl')
        formatter.formatJSON()
    
    
    def testAllOrganisms(self):
        since = "2009-06-01"
    
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
        print formatter.formatXML('genomes_changed.xml.tpl')
    
    
    def testCountAllOrganisms(self):
        since = "2009-06-01"
        organismIDs = [12, 14, 15, 20]
    
        result = self.queries.countAllChangedFeaturesForOrganisms(since, organismIDs)
        print result
    
    
    def testGetSourceFeatureSequence(self):
        rows = self.queries.getSourceFeatureSequence("Pf3D7_01")
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

    def testGetFeatureLocs(self):
        json_data = self.queries.getFeatureLocs(1, 1, 10000, [42, 69])
        print  json.dumps(json_data, sort_keys=True, indent=4)
        
    def testGetID(self):
        print self.queries.getFeatureID("Pf3D7_01")

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
    
    


if __name__ == '__main__':
    unittest.main(argv=['charpy'])

