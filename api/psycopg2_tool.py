#!/usr/bin/env python
# encoding: utf-8
"""
psycopg2_tool.py

Created by Giles Velarde on 2010-02-04.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import sys
import os
import cherrypy
from cherrypy import request
from sys import exc_info
import logging

logger=logging.getLogger("PGTransaction")

class PGTransaction(cherrypy.Tool):
    """
        Similar to the alchemy.sqlalchemy_tool, designed to catch exceptions and rollback if necessary. 
        Needs testing.
    """
    def __init__(self):
        self._name = 'PGTransaction'
        self._point = 'on_start_resource'
        self._priority = 100

    def _setup(self):
        cherrypy.request.hooks.attach('on_end_resource', self.on_end_resource)
        cherrypy.Tool._setup(self)

    def callable(self):
        logger.debug (cherrypy.thread_data.connectionFactory.getConnection())
        if cherrypy.thread_data.connectionFactory.getConnection().closed == True:
            logger.warn("Connection has been found to be closed. Trying to reset...")
            try:
                cherrypy.thread_data.connectionFactory.reset()
                logger.warn("Reset.")
            except Exception, e:
                logger.error("Could not reset connection")
    
    
    
    def on_end_resource(self):

        typ, value, trace = sys.exc_info()
        if value is not None:
            logger.error("Exception detected.")
            logger.error(typ)
            logger.error(value)
            logger.error(trace)

            # try to recover from whatever caused the problem
            try:
                cherrypy.thread_data.connectionFactory.getConnection().rollback()
            except Exception, e:
                logger.error("failed rollback")
                logger.error(e)
        
        logger.debug (cherrypy.thread_data.connectionFactory.getConnection())


cherrypy.tools.PGTransaction = PGTransaction()