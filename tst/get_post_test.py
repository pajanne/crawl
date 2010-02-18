#!/usr/bin/env python
# encoding: utf-8
"""
post_test.py

Created by Giles Velarde on 2010-02-17.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import os
try:
    import simplejson as json
except ImportError:
    import json

import logging, logging.config

logger = logging.getLogger("charpy")
logging.config.fileConfig(os.path.dirname(__file__) + "/logging.conf")

from ropy.client import RopyClient, ServerReportedException

def main():
    client = RopyClient("http://localhost:7777/")
    
    # a POST request using the u array parameter
    parameters = {
        "u[]": ["PFA0290w:exon:2", "PFA0300c:exon:1"]
    }
    response = json.dumps(client.request("genes/featureproperties.json", parameters), indent=1)
    logger.info(response)
    
    
    # a POST request using the us splittable string parameter
    parameters2 = {
        "us": "PFA0290w:exon:2,PFA0300c:exon:1"
    }
    response2 = json.dumps(client.request("genes/featureproperties.json", parameters2), indent=1)
    logger.info(response2)
    
    
    # the GET request
    parameters3 = {
        "u": ["PFA0290w:exon:2", "PFA0300c:exon:1"]
    }
    response3 = json.dumps(client.request("genes/featureproperties.json", parameters, False), indent=1)
    logger.info(response3)
    
    
    assert response == response2 == response3
    
    
    # a GET request, not parsing the data, must return a string
    parameters4 = {
        "uniqueNames": ["PFA0290w:exon:2", "PFA0300c:exon:1"]
    }
    response4 = client.request("genes/featureproperties.json", parameters, False, False)
    logger.info(response4)
    
    assert isinstance(response4, str)
    


if __name__ == '__main__':
    main()

