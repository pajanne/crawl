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
        super(Queries, self).__init__(connection=connectionFactory)
        
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
        returned = self.runQueryAndMakeDictionary("get_all_privates_with_dates", ("curator_%", organism_id, 'date_%' ))
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
    
    def getGenesWithHistoryChangesAnywhere(self, organism_id, since, date_type_id, curatorName_type_id, qualifier_type_id):
        returned = self.runQueryAndMakeDictionary("get_history_changes_anywhere", {
            "organism_id" : organism_id,
            "since" : since,
            "date_type_id" : date_type_id,
            "curatorName_type_id" : curatorName_type_id,
            "qualifier_type_id" : qualifier_type_id
        })

        return returned
    
    def getGeneForFeature(self, features):
        return self.runQueryAndMakeDictionary("get_gene_for_feature", { "features" : tuple(features) })
    
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
    
    
    def getRegionSequence(self, uniqueName):
        return self.runQueryAndMakeDictionary("region_sequence", (uniqueName, ))
    
    def getCvtermID(self, cvname, cvtermnames ):
        args = {"cvtermnames" : tuple(cvtermnames), "cvname" : cvname }
        rows = self.runQuery("get_cvterm_id", args)
        results=[]
        for r in rows:
            results.append(r[0])
        return results
    
    def getFeatureLocs(self, region_id, start, end, relationships):
        args = {
            "regionid": region_id,
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
    
    
    def getFeatureLocations(self, region_id, start, end, exclude = []):
        args = {
            "regionid": region_id,
            "start": start,
            "end": end
        }
        if len(exclude) > 0:
            args["exclude"] = tuple(exclude)
            return self.runQueryAndMakeDictionary("get_locations_excluding", args)
        return self.runQueryAndMakeDictionary("get_locations", args)
    
    
    def getFeatureLocationsMaxAndMinBoundaries(self, region_id, start, end, types):
        args = {
            "regionid": region_id,
            "start": start,
            "end": end, 
            "types" : tuple(types)
        }
        return self.runQueryAndMakeDictionary("get_location_min_and_max_boundaries", args)

    
    
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
        return self.runQueryAndMakeDictionary("get_cds_mrna_sequence", { "genenames": tuple(gene_unique_names) } )
    
    def getPEPs(self, gene_unique_names):
        return self.runQueryAndMakeDictionary("get_cds_pep_sequence", { "genenames": tuple(gene_unique_names) } )
    
    def getGeneSequence(self, region, genes):
        if len(genes) == 0:
            return self.runQueryAndMakeDictionary("get_gene_sequence_all", { 'region': region})
        return self.runQueryAndMakeDictionary("get_gene_sequence", { 'region': region, "genes" : tuple(genes)})
    
    def getFeatureSequenceFromRegion(self, region, features):
        return self.runQueryAndMakeDictionary("get_feature_sequence", { 'region': region, 'features' : tuple(features)})
    
    def getFeatureLength(self, uniquename):
        try:
            return self.runQueryExpectingSingleRow("feature_length", (uniquename, ))[0][0]
        except QueryProcessorException, qpe:
            raise ServerException(qpe.value, ERROR_CODES["DATA_NOT_FOUND"])
    
    def getOrganismProp(self, organism_id, cv, cvterm):
        query_string = self.getQuery("get_organism_prop")
        
        args = {
            "organism_id" : organism_id
        }
        
        if cv is not None and len(cv) > 0:
            query_string += " AND cv.name = %(cv)s "
            args["cv"] = cv
        
        if cvterm is not None and len(cvterm) > 0:
            query_string += " AND cvterm.name = %(cvterm)s "
            args["cvterm"] = cvterm
        
        return self.runQueryStringAndMakeDictionary(query_string, args)
    
    def getOrganismIDFromCommonName(self, common_name):
        result = self.runQueryStringAndMakeDictionary(
            "SELECT organism_id FROM organism WHERE organism.common_name = %(common_name)s", 
            {"common_name" : common_name})
        if len(result) > 0:
            return result[0]["organism_id"]
        raise ServerException("Could not find organism with common_name " + common_name, ERROR_CODES["DATA_NOT_FOUND"])
    
    def getOrganismIDFromOrganismID(self, organism_id):
        result = self.runQueryStringAndMakeDictionary(
            "SELECT organism_id FROM organism WHERE organism.organism_id = %(organism_id)s", 
            {"organism_id" : organism_id})
        if len(result) > 0:
            return result[0]["organism_id"]
        raise ServerException("Could not find organism with organism_id " + organism_id, ERROR_CODES["DATA_NOT_FOUND"])
        
    def getGenes(self, region):
        return self.runQueryAndMakeDictionary("get_genes", {"region" : region } )
    
    def getFeatureCoordinates(self, features, region = None):
        if region ==  None:
            return self.runQueryAndMakeDictionary("get_feature_coordinates_on_all_sourcefeatuess", { "features" : tuple(features) } )
        return self.runQueryAndMakeDictionary("get_feature_coordinates", {"region" : region, "features" : tuple(features) } )
    
    def getExons(self, region, genes):
        if len(genes) == 0:
            return self.runQueryAndMakeDictionary("get_exons_all", { "region" : region })
        return self.runQueryAndMakeDictionary("get_exons", {"region" : region, "genenames" : tuple(genes) })
    
    def getFeatureCVTerm(self, features, cvs):
        if cvs == None or len(cvs) == 0:
            return self.runQueryAndMakeDictionary("get_feature_cvterms_all", {"features" : tuple(features) })
        return self.runQueryAndMakeDictionary("get_feature_cvterms", {"features" : tuple(features), "cvs" : tuple(cvs) })
    
    def getFeatureWithCVTerm(self, cvterm, cv = None, regex = False, region = None):
        query_string = self.getQuery("get_features_with_cvterm")
        
        args =  {"cvterm" : cvterm }
        
        if cv is not None and len(cv) > 0:
            query_string += " AND c.name = %(cv)s "
            args["cv"] = cv
        
        if region is not None and len(region) > 0:
            query_string += " JOIN featureloc fl ON fl.feature_id = f.feature_id AND srcfeature_id=(SELECT feature_id FROM feature WHERE uniquename= %(region)s) "
            args["region"] = region
        
        # add the where
        if regex is True:
            query_string += " WHERE ct.name ~* %(cvterm)s "
        else:
            query_string += " WHERE ct.name = %(cvterm)s "
        
        return self.runQueryStringAndMakeDictionary(query_string, args)
        
    
    def getTermsInOrganism(self, cvs, organism_id):
        return self.runQueryAndMakeDictionary("get_features_with_all_cvterms_of_type_in_organism", {"cvs" : tuple(cvs), "organism_id" : organism_id})
        
    def getTermPathParents(self, cv, terms):
        return self.runQueryAndMakeDictionary("get_cvterm_path_parents", { "cv" : cv, "terms" : tuple(terms) } )
    
    def getFeatureWithProp(self, value, type = None, regex = False, region = None):
        query_string = self.getQuery("get_features_with_prop")
        
        args = {"value" : value}
        
        # must put this join before the where clause
        if region is not None and len(region) > 0:
            query_string += " JOIN featureloc fl ON fl.feature_id = f.feature_id AND srcfeature_id=(SELECT feature_id FROM feature WHERE uniquename= %(region)s) "
            args["region"] = region
        
        # add the where
        if regex is True:
            query_string += "WHERE fp.value ~* %(value)s "
        else:
            query_string += "WHERE fp.value = %(value)s "
        
        if type is not None and len(type) > 0:
            query_string += " AND ct.name = %(type)s "
            args ["type"] = type
        
        return self.runQueryStringAndMakeDictionary(query_string, args)
        
    
    def getFeatureCVTermPub(self, feature_cvterm_id):
        results = self.runQuery("get_feature_cvterm_pubs", {"feature_cvterm_id" : feature_cvterm_id })
        to_return = []
        for result in results:
            if result[0] != "null":
                split = result[0].split(":")
                to_return.append({"database" : split[0], "accession" : split[1]})
        return to_return
    
    def getFeatureCVTermDbxrefs(self, feature_cvterm_id):
        results = self.runQuery("get_feature_cvterm_dbxrefs", {"feature_cvterm_id" : feature_cvterm_id })
        to_return = []
        for result in results:
            to_return.append(result[0])
        return to_return
    
    def getAnnotationChangeCvterms(self):
        return self.runQueryAndMakeDictionary("get_annotation_change_cvterms")
    
    def getOrthologues(self, features):
        return self.runQueryAndMakeDictionary("get_orthologue", {"features" : tuple(features)})
    
    def getOrthologueClusters(self, orthologues):
        return self.runQueryAndMakeDictionary("get_orthologue_clusters", {"orthologues" : tuple(orthologues)})
    
    def getOrthologuesInOrganism(self, organism_id):
        return self.runQueryAndMakeDictionary("get_orthologues_inorganism", {"organism_id" : organism_id})
        
    def getDomains(self, genes, relationships):
        return self.runQueryAndMakeDictionary("get_domains", {
            "genes" : tuple(genes), 
            "relationships" : tuple(relationships) 
        })
    
    def getWithDomains(self, domains, relationships):
        return self.runQueryAndMakeDictionary("get_with_domains", {
            "domains" : tuple(domains),
            "relationships" : tuple(relationships)
        })
    
    def getRelationships(self, features, relationships):
        return self.runQueryAndMakeDictionary("get_relationships", {
            "features" : tuple(features),
            "relationships" : tuple(relationships)
        })
    
    def getRelationshipsParents(self, features, relationships):
        return self.runQueryAndMakeDictionary("get_relationships_parents", {
            "features" : tuple(features),
            "relationships" : tuple(relationships)
        })
    
    def getRelationshipsChildren(self, features, relationships):
        return self.runQueryAndMakeDictionary("get_relationships_children", {
            "features" : tuple(features),
            "relationships" : tuple(relationships)
        })
    
    def getFeatureNameFromUniqueNames(self, uniquenames):
        return self.runQueryAndMakeDictionary("get_feature_name_from_uniquename", {"uniquenames" : tuple(uniquenames)})
    
    def getFeaturePub(self, features):
        return self.runQueryAndMakeDictionary("get_feature_pubs", {
            "features" : tuple(features)
        })
    
    def getFeatureDbxrefs(self, features):
        return self.runQueryAndMakeDictionary("get_feature_dbxrefs", {
            "features" : tuple(features)
        })
    
    def getCV(self):
        return self.runQueryAndMakeDictionary("get_cv")
    
    def getCvterms(self, cvs):
        return self.runQueryAndMakeDictionary("get_cvterms_from_cv", { "cvs" : tuple(cvs) })
    
    def getFeatureWithNameLike(self, term, regex = False, region = None):
        query_string = self.getQuery("get_feature_like")
        
        args = {"term" : term}
        
        
        results = results1 + results2
        
        return results
        
    def getFeatureLike(self, term, regex = False, region = None):
        query_string = self.getQuery("get_feature_like")
        
        args = {"term" : term}
        
         # must put this join before the where clause
        if region is not None and len(region) > 0:
            query_string += " JOIN featureloc fl ON fl.feature_id = f.feature_id AND srcfeature_id=(SELECT feature_id FROM feature WHERE uniquename= %(region)s) "
            args["region"] = region
        
        # add the where
        if regex is True:
            query_string += "WHERE f.uniquename ~* %(term)s or f.name ~* %(term)s "
        else:
            query_string += "WHERE f.uniquename = %(term)s or f.name = %(term)s "
        
        return self.runQueryStringAndMakeDictionary(query_string, args)
        
    
    def getSynonymLike(self, term, regex = False, region = None):
        query_string = self.getQuery("get_synonym_like")
        
        args = {"term" : term}
        
         # must put this join before the where clause
        if region is not None and len(region) > 0:
            query_string += " JOIN featureloc fl ON fl.feature_id = f.feature_id AND srcfeature_id=(SELECT feature_id FROM feature WHERE uniquename= %(region)s) "
            args["region"] = region
        
        # add the where
        if regex is True:
            query_string += "WHERE synonym.name ~* %(term)s "
        else:
            query_string += "WHERE synonym.name = %(term)s "
        
        return self.runQueryStringAndMakeDictionary(query_string, args)
        
        
    def getFeatureLocsWithNameLike(self, regionID, start, end, term):
        return self.runQueryAndMakeDictionary("feature_locs_like", {
            "regionid": regionID,
            "start":start,
            "end":end,
            "term":term
        })
    
    def getAnlysis(self, features):
        return self.runQueryAndMakeDictionary("get_analysis", { "features" : tuple(features) })
    
    def getSynonym(self, uniquenames, types):
        if types is not None and len(types) > 0:
            return self.runQueryAndMakeDictionary("get_synonym_of_type", {"uniquenames" : tuple(uniquenames), "types" : tuple(types) })
        return self.runQueryAndMakeDictionary("get_synonym", {"uniquenames" : tuple(uniquenames)})
    
    def getBlastMatch(self, subject, start, end, target = None, score = None):
        query_string = self.getQuery("get_blast_match")
        
        args = {
            "subject" : subject,
            "start" : start, 
            "end" : end, 
        }
        
        if target is not None:
            args["target"] = target
            query_string += "\n AND q.uniquename = %(target)s "
            
        if score is not None:
            args["score"] = float(score)
            query_string += "\n AND analysisfeature.normscore <= %(score)s "
        
        logger.debug(query_string)
        logger.debug(args)
        
        return self.runQueryStringAndMakeDictionary(query_string, args)
    
    def getBlastMatchPair(self, f1, start1, end1, f2, start2, end2, length = None, normscore = None):
        query_string = self.getQuery("get_blast_match_pairs")
        
        args = {
            "f1":f1,
            "start1":start1,
            "end1":end1,
            "f2":f2,
            "start2":start2,
            "end2":end2, 
            "length":length
        }
        
        if normscore is not None:
            args["normscore"] = float(normscore)
            query_string += "\n AND analysisfeature.normscore <= %(normscore)s "
        
        if length is not None:
            args["length"] = float(length)
            query_string += "\n AND ( (fl1.fmax - fl1.fmin >= %(length)s ) AND (fl2.fmax - fl2.fmin >= %(length)s )) "
        
        logger.debug(query_string)
        logger.debug(args)
        
        return self.runQueryStringAndMakeDictionary(query_string, args)
    
    def getGraphList(self):
        return self.runQueryAndMakeDictionary("get_graph_list")
    
    
    def getGraphData(self, id):
        
        plots = self.runQuery("get_graph_data", (int(id), ))
        
        row = plots[0]
        
        graph_id = row[0]
        feature_name = row[1]
        graph_name = row[2]
        loid = row[3]
        
        logger.debug((graph_id, feature_name, graph_name, loid))
        
        lobj = self.getConnection().lobject(loid)
        logger.debug(lobj)
        
        logger.debug(lobj.tell())
        data1 = lobj.read()
        logger.debug(lobj.tell())
        
        from cStringIO import StringIO
        from gzip import GzipFile
        
        data_unzipped = GzipFile('','r',0,StringIO(data1))
        
        # logger.debug(data_unzipped)
        
        return {
            "id" : graph_id,
            "feature": feature_name,
            "name" : graph_name, 
            "data" : data_unzipped
        }
    
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

