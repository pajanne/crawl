#!/usr/bin/env python
# encoding: utf-8
"""
batch_test.py

Created by Giles Velarde on 2010-01-15.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import os
import json
import threading
import random

from ropy.client import RopyClient, ServerReportedException

class BatchTest ( threading.Thread ):

   def run ( self ):
        client = RopyClient("http://localhost:6666/", os.path.dirname(__file__) + "/../tpl/")
        
        parameters = {
            "start" : self.startValue,
            "end" : self.endValue,
            "uniqueName" : "Pf3D7_01"
        }
        
        json_data = client.request("sourcefeatures/featureloc.json", parameters)
        
        print json.dumps(json_data, indent=4)

def main():
    
    # we want to replicate several users calling from different Ajax clients at the same time
    # to make this test as asynchronous as possible, we start a new thread for each client call
    for i in range(1,100):
        
        span = random.randint(1, 4000)
        
        batchTest = BatchTest()
        batchTest.startValue = (i* span ) - (span-1)
        batchTest.endValue = batchTest.startValue + span
        batchTest.start()


if __name__ == '__main__':
    main()

