#!/usr/bin/env python
# encoding: utf-8
"""
bulk_export.py

Created by Giles Velarde on 2009-10-30.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import os
import logging

import ConfigParser

from sys import exc_info

from api import WhatsNew

from ropy.server import Formatter
from ropy.util import LogConf

from setup import *

logger = logging.getLogger("charpy")

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
            
            logger.info (fileName)
            
            f = open(fileName + ".xml", 'w')
            f.write(str(formatter.formatTemplate('private_annotations.xml.tpl')))
            f.close()
            
            f2 = open(fileName + ".json", 'w')
            f2.write(str(formatter.formatJSON()))
            f2.close()



if __name__ == '__main__':
    main()

