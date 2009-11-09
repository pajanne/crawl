#!/usr/bin/env python
# encoding: utf-8
"""
bulk_export.py

Created by Giles Velarde on 2009-10-30.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import os


import ConfigParser

from sys import exc_info

from business.api import WhatsNew
from ropy.util import dolog
from ropy.server import Formatter
from ropy.util import LogConf

config = ConfigParser.ConfigParser()
config.read(os.path.dirname(__file__) + '/../conf/config.ini')

host=config.get('Connection', 'host')
database=config.get('Connection', 'database')
user=config.get('Connection', 'user')
password=config.get('Connection', 'password')

LogConf.logpath=config.get('Logging', 'path')

def main():
    
    print host
    print database
    
    whats_new = WhatsNew(host, database, user, password)

    organism_list = whats_new.getAllOrganismsAndTaxonIDs()
    for organism_details in organism_list:
        rows = whats_new.getGenesWithPrivateAnnotationChanges(organism_details["organism_id"])
        
        count = len(rows)
        
        if count > 0:
            
            data = {
                "response" : {
                    "name" : "genome/recorded_annotation_changes",
                    "taxonomyID" : str(organism_details["taxonomyid"]),
                    "count" : count,
                    "results" : rows
                }
            }
            
            formatter = Formatter(data)
            
            formatted = formatter.formatTemplate('private_annotations.xml.tpl')
            
            fileName = organism_details["name"].replace('/', '' )
            fileName = fileName.replace(' ', '_')
            fileName = os.path.dirname(__file__) + '/../tmp/' + fileName 
            
            print fileName
            
            f = open(fileName + ".xml", 'w')
            f.write(str(formatter.formatTemplate('private_annotations.xml.tpl')))
            f.close()
            
            f2 = open(fileName + ".json", 'w')
            f2.write(str(formatter.formatJSON()))
            f2.close()



if __name__ == '__main__':
    main()

