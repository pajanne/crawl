#!/usr/bin/env python
# encoding: utf-8
"""
api.py

Created by Giles Velarde on 2009-10-27.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.

This module defines low-level API calls. Methods here usually only do one SQL query, and return simple lists
or dictionaries.

"""


import os
import time
import logging

from ropy.query import QueryProcessor, QueryProcessorException
from ropy.server import ServerException, ERROR_CODES

logger = logging.getLogger("crawl")

class Queries(QueryProcessor):
    
    def __init__(self, connectionFactory):
        super(Queries, self).__init__(connection=connectionFactory, single=True)
        
        # reset the path to this the sql subfolder at the location class
        self.setSQLFilePath(os.path.dirname(__file__) + "/../sql/")
        
        # load the SQL files fom the sql folder
        for file in os.listdir(self.sqlPath):
            if file.endswith(".sql"): self.addQueryFromFile(file.replace(".sql", ""), file )
    
    def getAllChangedFeaturesForOrganism(self, date, organism_id):
        self.validateDate(date)
        rows = self.runQueryAndMakeDictionary("all_changed_features_for_organism", (date, organism_id, date, organism_id, date, organism_id))
        return rows
    
    def getOrganismFromTaxon(self, taxonID):
        rows = self.runQuery("get_organism_id_from_taxon_id", (taxonID, ))
        try:
            # return the first value of the first row... 
            return rows[0][0]
        except:
            raise ServerException("Could not find organism for taxonID " + taxonID, ERROR_CODES["DATA_NOT_FOUND"])
    
    def getGenesWithPrivateAnnotationChanges(self, organism_id, since, show_curator = False):
        # print organism_id
        returned = self.runQueryAndMakeDictionary("get_all_privates_with_dates", ("%curator_%", organism_id, 'date_%' ))
        # print returned
        sinceDate = time.strptime(since,"%Y-%m-%d")
        results = []
        for result in returned:
            
            if show_curator == False:
                del result["changecurator"] 
            
            # insert a tag so we know which query made it
            result["source"] = "private"
            
            resultDate = time.strptime(result["changedate"] ,"%Y-%m-%d")
            # print time.strftime("%Y-%m-%d",resultDate) + ">=" + time.strftime("%Y-%m-%d",sinceDate) + " = " + str(resultDate >= sinceDate)
            if (resultDate >= sinceDate):
                results.append(result)
        return results
    
    def getGenesWithHistoryChanges(self, organism_id, since, date_type_id, curatorName_type_id, qualifier_type_id):
        returned = self.runQueryAndMakeDictionary("get_history_changes", {
            "organism_id" : organism_id,
            "since" : since,
            "date_type_id" : date_type_id,
            "curatorName_type_id" : curatorName_type_id,
            "qualifier_type_id" : qualifier_type_id
        })
        
        for result in returned:
            result["source"] = "history"
        
        return returned
    
    def countAllChangedFeaturesForOrganism(self, organism_id, since):
        self.validateDate(since)        
        rows = self.runQuery("count_changed_features_organism", (organism_id, since))
        count = rows[0][0]
        logger.debug ( str(organism_id) + " - " + since + " - " + str(count) )
        return count
    
    def countAllChangedFeaturesForOrganisms(self, since, organismIDs):
        ids = tuple (organismIDs) # must convert arrays to tuples
        rows = self.runQuery("count_all_changed_features", (since, ids) );
        return rows
    
    def getAllOrganismsAndTaxonIDs(self):
        return self.runQueryAndMakeDictionary("get_all_organisms_and_taxon_ids")
    
    
    def getSourceFeatureSequence(self, uniqueName):
        rows = self.runQueryAndMakeDictionary("source_feature_sequence", (uniqueName, ))
        return rows
    
    def getCvtermID(self, cvname, cvtermnames ):
        args = {"cvtermnames" : tuple(cvtermnames), "cvname" : cvname }
        rows = self.runQuery("get_cvterm_id", args)
        results=[]
        for r in rows:
            results.append(r[0])
        return results
    
    def getFeatureLocs(self, source_feature_id, start, end, relationships):
        args = {
            "sourcefeatureid": source_feature_id,
            "start":start,
            "end":end,
            "relationships":tuple(relationships), # must convert arrays to tuples
        }
        
        rows = self.runQueryAndMakeDictionary("feature_locs", args)
        
        # import json
        # logger.debug(json.dumps(rows, indent=4, sort_keys=True))
        # for r in rows:
        #     logger.debug(json.dumps(r, indent=4))
        
        return rows
    
    def getTopLevelTypeID(self):
        rows = self.runQueryExpectingSingleRow("get_top_level_type_id")
        return rows[0][0]
    
    def getTopLevel(self, organism_id):
        top_level_type = self.getTopLevelTypeID()
        rows = self.runQuery("get_top_level", (organism_id, top_level_type))
        
        results = []
        for r in rows:
            results.append(r[0])
        
        return results

    def getFeatureID(self, uniqueName):
        try:
            return self.runQueryExpectingSingleRow("get_feature_id_from_uniquename", (uniqueName, ))[0][0]
        except QueryProcessorException, qpe:
            raise ServerException(qpe.value, ERROR_CODES["DATA_NOT_FOUND"])
    
    def getFeatureProps(self, uniqueNames):
        return self.runQueryAndMakeDictionary("get_featureprop",  {"uniquenames" : tuple(uniqueNames) })

    
    def getCDSs(self, organism_id):
        logger.info(organism_id)
        return self.runQueryAndMakeDictionary("get_all_cds_features_for_organism", (organism_id, ))
    
    def getMRNAs(self, gene_unique_names):
        return self.runQueryAndMakeDictionary("get_cds_mrna_residues", { "genenames": tuple(gene_unique_names) } )
    
    def getPEPs(self, gene_unique_names):
        return self.runQueryAndMakeDictionary("get_cds_pep_residues", { "genenames": tuple(gene_unique_names) } )
    
    def getFeatureResiduesFromSourceFeature(self, sourcefeature, features):
        return self.runQueryAndMakeDictionary("get_feature_sequence", { 'sourcefeature': sourcefeature, 'features' : tuple(features)})
    
    def getFeatureLength(self, uniquename):
        try:
            return self.runQueryExpectingSingleRow("feature_length", (uniquename, ))[0][0]
        except QueryProcessorException, qpe:
            raise ServerException(qpe.value, ERROR_CODES["DATA_NOT_FOUND"])
    
    def getOrganismProp(self, organism_ids, cvterm_name, cv_name):
        return self.runQueryAndMakeDictionary("get_organism_prop", { "organism_ids" : tuple(organism_ids), "cvterm_name" : cvterm_name, "cv_name" : cv_name  } )
        
    def getFeatureCoordinates(self, sourcefeature, features):
        return self.runQueryAndMakeDictionary("get_feature_coordinates", {"sourcefeature" : sourcefeature, "features" : tuple(features) } )
    
    def getExonCoordinates(self, sourcefeature, genes):
        return self.runQueryAndMakeDictionary("get_exon_coordinates", {"sourcefeature":sourcefeature, "genenames":tuple(genes)} )
    
    def getFeatureCVTerm(self, features, cv_names):
        return self.runQueryAndMakeDictionary("get_feature_cvterms", {"features" : tuple(features), "cv" : tuple(cv_names) })
    
    def getAnnotationChangeCvterms(self):
        return self.runQueryAndMakeDictionary("get_annotation_change_cvterms")
    
    def validateDate(self, date):
        try:
            time.strptime(date,"%Y-%m-%d")
        except Exception, e:
            # print "date " + date
            logger.error(e)
            se = ServerException("Invalid date: please supply a valid date markes in 'YYYY-MM-DD' format.", ERROR_CODES["INVALID_DATE"])
            raise ServerException, se


def main():
    pass


if __name__ == '__main__':
    main()

