'''
Created on Nov 21, 2010

@author: gv1
'''

import datetime
import logging
import types
import sys

logger = logging.getLogger("ropy")

if sys.platform[:4] == 'java':
    
    from com.ziclix.python.sql import zxJDBC as driver
    
    class FormattingCursor(object):
        """
           This class is a facade to the zxJDBC cursor, so that we can hook in the formatting necessary to transform the query parameter styles from
           the psycopg2 default pyformat style to the JDBC prepared statement style. 
        """
        def __init__(self, cursor):
            self.cursor = cursor
        
        def execute(self, query, params):
            query_string = self.make_query_string(query, params)
            self.cursor.execute(query_string)
            self.description = self.cursor.description
        
        def __iter__(self):
            return self.cursor
        
        def next(self):
            return self.cursor.next()
        
        def fetchall(self):
            return self.cursor.fetchall()
        
        def fetchone(self):
            return self.cursor.fetchone()
        
        def param_to_array(self, params):
            mogrified = []
            for param in params:
                param = self.stringify(param)
                mogrified.append(param)
            return " ( " + " , ".join(mogrified) + " ) "
        
        # note, we should add SQL escaping here
        def stringify(self, param):
            if type(param) is types.StringType or type(param) is types.UnicodeType:
                param = "'%s'" % param
            else:
                param = str(param)
            return param

        def make_query_string(self, query_string, params = None):

            if params != None:
                modified_parameters = None
                if type(params) is types.ListType or type(params) is types.TupleType:
                    modified_parameters = []
                    for param in params:
                        if type(param) is types.ListType:
                            param = self.param_to_array(param)
                        else:
                            param = self.stringify(param)
                        modified_parameters.append(param)
                    modified_parameters=tuple(modified_parameters)

                elif type(params) is types.DictType:
                    modified_parameters = {}
                    for param_key, param in params.items():
                        if type(param) is types.ListType or type(param) is types.TupleType:
                            param = self.param_to_array(param)
                        else:
                            param = self.stringify(param)
                        modified_parameters[param_key] = param

                logger.debug (query_string)
                logger.debug(params)
                logger.debug (modified_parameters)

                query_string = query_string % modified_parameters

                logger.info (query_string)

            return query_string
    
else:
    import psycopg2 as driver #@UnusedImport
    
    # even though nothing "appears" to use this, psycopg2.extensions are necessary 
    # to import the lib for tuple-based "SELECT * FROM IN %s" queries
    import psycopg2.extensions
    
    class LoggingCursor(psycopg2.extensions.cursor):
        """
           This class extends the psycopg2 cursor, so we can log the statements.
        """
        def execute(self, sql, args=None):
            try:
                logger.debug("\n" + self.mogrify(sql, args))
                psycopg2.extensions.cursor.execute(self, sql, args) #@UndefinedVariable
            except Exception, exc:
                #logger.debug(self.mogrify(sql, args))
                logger.error("%s: %s" % (exc.__class__.__name__, exc))
                raise








class QueryProcessorException(Exception):
    """
        Ideally, all errors should be raised with this (or a subclass of), so that the
        server can always report back a consistent error message to the client.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ConnectionFactory(object):
    
    def __init__(self, host, database, user, password, port=5432):
        self.host = host
        self.database = database
        self.port = port
        self.user = user
        self.password = password
        
        self.single_connection = None
        
        self.connections = {}
        self.connection = None
    
    def _connect(self):
        if sys.platform[:4] == 'java':
            conn = driver.connect("jdbc:postgresql://%s:%s/%s" % (self.host, self.port, self.database), self.user, self.password, "org.postgresql.Driver")

        else:
            connect_cmd = "dbname='%s' user='%s' host='%s'" % (self.database, self.user, self.host)
            if self.password:
                # required to handle trusted connection without password
                connect_cmd = connect_cmd + " password='%s'" % self.password

            if self.port:
                # required to connect to non-default postgresql port value e.g. pathdbsrv1b.internal.sanger.ac.uk:10120/bigtest5
                connect_cmd = connect_cmd + " port=%s" % self.port

            conn = driver.connect(connect_cmd);
        return conn
    
    def getConnection(self, name = "DEFAULT"):
        if name not in self.connections:
            logger.debug ("Can't find connection '%s'. Creating." % name)
            self.connections[name] = self._connect()
        if self.connections[name].closed != 0:
            logger.debug ("Connection '%s' is closed. Reopening." % name)
            self.connections[name] = self._connect()
        return self.connections[name]
    
    def close(self, name = "DEFAULT"):
        if self.getConnection(name).closed != 1:
            self.getConnection(name).close()
            del self.connections[name]
    
    def reset(self, name = "DEFAULT"):
        self.close(name)
        return self.getConnection(name)
    
    def __repr__(self):
        s = ""
        comma=""
        for att in self.__dict__:
            if att == 'password': continue
            s+= comma + att + ' = "' + str(self.__dict__[att]) + '"'
            comma=", "
        s= "<ConnectionFactory(" + s + ")>"
        return s

class QueryProcessor(object):
    """
        A base class for manaing postgres queries. 
    """
    def __init__(self, **kwargs):
        
        self.queries = {}
        
        if "connection" in kwargs:
            self.connectionFactory = kwargs["connection"]
            
        else:
            
            if not "host" in kwargs:     raise QueryProcessorException("Please supply a 'host' keyword arg if not supplying a connection")
            if not "database" in kwargs: raise QueryProcessorException("Please supply a 'database' keyword arg if not supplying a connection")
            if not "user" in kwargs:     raise QueryProcessorException("Please supply a 'user' keyword arg if not supplying a connection")
            if not "password" in kwargs: raise QueryProcessorException("Please supply a 'password' keyword arg if not supplying a connection")
            if not "port" in kwargs:     port = "5432"
            
            host = kwargs["host"]
            database = kwargs["database"]
            user = kwargs["user"]
            password = kwargs["password"]
            
            self.connectionFactory = ConnectionFactory(host, database, user, password, port)
        
        # self.conn = self.connectionFactory.getConnection()
        
    
    def getConnection(self):
        return self.connectionFactory.getConnection()
    
    def getCursor(self):
        if sys.platform[:4] == 'java':
            return FormattingCursor(self.getConnection().cursor())
        else:
            return self.getConnection().cursor(cursor_factory=LoggingCursor)
    
    def setSQLFilePath(self, sqlPath):
        self.sqlPath = sqlPath
    
    def addQueryFromFile(self, queryName, fileName):
        sqlFileContents = open(self.sqlPath + fileName, 'r').read()
        self.queries[queryName] = sqlFileContents
        
    def addQueryFromString(self, queryName, queryString):
        self.queries[queryName] = queryString
    
    def getQuery(self, queryName):
        return self.queries.get(queryName)
    
    def commit(self):
        self.getConnection().commit() 
    
    def rollback(self):
        self.getConnection().rollback() 
    
    def runWriteQuery(self, queryName, args = None):
        # print query % args
        
        cursor = self.getCursor()
        cursor.execute(self.queries[queryName], args)
        #self.commit() 
    
    def runQueryExpectingSingleRow(self, queryName, args = None):
        rows = self.runQuery(queryName, args)
        if rows == None:
            raise QueryProcessorException("Could not find a result!")
        if len(rows) != 1:
            raise QueryProcessorException("Expecting exactly one result, found " + str(len(rows)) + "!")
        return rows
    
    
    def runQuery(self, queryName, args = None):
        cursor = self.getCursor()
        cursor.execute(self.queries[queryName], args)
        rows = cursor.fetchall()
        return rows
    
    def runQueryString(self, query_string, args = None):
        cursor = self.getCursor()
        cursor.execute(query_string, args)
        rows = cursor.fetchall()
        return rows
    
    def runQueryStringAndMakeDictionary(self, query_string, args = None):
        cursor = self.getCursor()
        cursor.execute(query_string, args)
        return self.makeDictionary(cursor)
        
    def runQueryAndMakeDictionary(self, queryName, args = None):
        cursor = self.getCursor()
        cursor.execute(self.queries[queryName], args)
        return self.makeDictionary(cursor)
        
        
    def makeDictionary(self, cursor):
        result = []
        for currow in cursor:
            rowdict = {}
            for curcol in range(0,len(cursor.description)):
                val = currow[curcol]
                if isinstance(val, datetime.datetime):
                    val = val.strftime("%Y-%m-%d")
                elif type(val) is types.ListType:
                    pass
                else: 
                    val = str(val) 
                rowdict[cursor.description[curcol][0]] = val
            result.append(rowdict)
        return result
    