#!/usr/bin/env python
# encoding: utf-8
"""
controllers.py

Classes in this module are for exposure as web or command line services. They inherit from ropy.server.RESTController, and their methods are 
decorated to expose them. 

Created by Giles Velarde on 2010-02-04.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import os
import cherrypy

import logging

logger = logging.getLogger("crawl")

import ropy.server
import db

class BaseController(ropy.server.RESTController):
    """
        An abstract class with common methods shared by crawl controllers. Not to be instantiated directly.
    """
    
#   
    def __init__(self):
        self.templateFilePath = os.path.dirname(__file__) + "/../tpl/"
        
        # declaring an instance variable, which will be called by most methods, must set if the controller is instantiated out of a server context
        # designed to be a db.Queries instance
        self.queries = None
        
    
    def init_handler(self):
        self.queries = db.Queries(cherrypy.thread_data.connectionFactory)
        #self.api = api.API(cherrypy.thread_data.connectionFactory)
        super(BaseController, self).init_handler()
    
class Genes(BaseController):
    """
        Feature related queries.
    """
    
    @cherrypy.expose
    @ropy.server.service_format("changes")
    def changes(self, since, taxonomyID):
        """
            Reports all the features that have changed since a certain date.
        """
        organism_id = self.queries.getOrganismFromTaxon(taxonomyID)
        changed_features = self.queries.getAllChangedFeaturesForOrganism(since, organism_id)
        data = {
            "response" : {
                "name" : "genes/changes",
                "taxonID" : taxonomyID,
                "count" : len(changed_features),
                "since" : since,
                "results" : changed_features
            }
        }
        #data = self.api.gene_changes(since, taxonomyID)
        return data
    
    changes.arguments = { 
        "since" : "date formatted as YYYY-MM-DD", 
        "taxonomyID" : "the NCBI taxonomy ID"  
    }
    
    @cherrypy.expose
    @ropy.server.service_format("private_annotations")
    def annotation_changes(self, taxonomyID, since):
        """
            Reports all the genes that have been highlighted as having annotation changes.
        """
        organism_id = self.queries.getOrganismFromTaxon(taxonomyID)
        # print organism_id
        rows = self.queries.getGenesWithPrivateAnnotationChanges(organism_id, since)
        
        # bring in the new style changes
        # eventually, once all the privates have been migrated, we can remove the query above
        rows_history = self._getGenesWithHistoryChanges(organism_id, since)
        for row_history in rows_history:
            rows.append(row_history)
        
        data = {
            "response" : {
                "name" : "genes/annotation_changes",
                "taxonomyID" : taxonomyID,
                "count" : len(rows),
                "since" : since,
                "results" : rows
            }
        }
        #data = self.api.annotation_changes(taxonomyID, since)
        return data
    
    annotation_changes.arguments = { 
        "since" : "date formatted as YYYY-MM-DD", 
        "taxonomyID" : "the NCBI taxonomy ID" 
    }
    
    def _getGenesWithHistoryChanges(self, organism_id, since):

        cvterm_infos = self._getHistoryCvtermPropTypeIDs()

        qualifier_type_id = cvterm_infos[0]["id"]
        curatorName_type_id = cvterm_infos[1]["id"]
        date_type_id = cvterm_infos[2]["id"]

        results = self.queries.getGenesWithHistoryChanges(organism_id, since, date_type_id, curatorName_type_id, qualifier_type_id)

        return results
    
    def _getHistoryCvtermPropTypeIDs(self):
        cvterm_infos = (
            { "cv" : "genedb_misc",         "cvterm" : "qualifier" }, 
            { "cv" : "genedb_misc",         "cvterm" : "curatorName" }, 
            { "cv" : "feature_property",    "cvterm" : "date" }
        )
        
        for cvterm_info in cvterm_infos:
            cvterm_info["id"] = self.queries.getCvtermID( cvterm_info["cv"], [cvterm_info["cvterm"]] )[0]
        
        return cvterm_infos
    
    
    @cherrypy.expose
    @ropy.server.service_format()
    def top(self, taxonID):
        """
            Returns a list of top level features for an organism.
        """
        organism_id = self.queries.getOrganismFromTaxon(taxonID)
        results = self.queries.getTopLevel(organism_id)
        
        data = {
           "response" : {
               "name" : "genes/top",
               "taxonId" : taxonID,
               "features" : results
           }
        }
        #data = self.api.getTopLevel(taxonID)
        return data
    
    top.arguments = {
        "taxonID" : "the taxonID of the organism you want to browse"
    }
    
    
    
    @cherrypy.expose
    @ropy.server.service_format()
    def featureproperties(self, **kwargs):
        """
            Returns featureprops for a given set of uniqueNames.
        """
        
        # build the uniqueNames array from different possilble kwargs
        uniqueNames = ropy.server.get_array_from_hash("uniqueNames", kwargs)
        uniqueNames2 = ropy.server.get_array_from_hash("u", kwargs)
        
        if len(uniqueNames2) > 0: uniqueNames.extend(uniqueNames2)
        
        # special case of arrays being passed using the us parameter, with the delimiter
        delimiter = kwargs["delimiter"] if "delimiter" in kwargs else ","
        if "us" in kwargs: uniqueNames.extend(kwargs["us"].split(delimiter))
        
        logger.debug(uniqueNames)
        
        if len(uniqueNames) == 0: 
            raise ropy.server.ServerException("Please provide at least one uniqueNames / u / us parameter.", ropy.server.ERROR_CODES["MISSING_PARAMETER"])
        
        
        results = self.queries.getFeatureProps(uniqueNames)
        
        prop_dict = {}
        prop_list = []
        
        for r in results:
            uniquename = r.pop("uniquename")
            
            if uniquename not in prop_dict:
                prop_dict[uniquename] = {
                    "uniquename" : uniquename,
                    "props" : []
                }
                prop_list.append(prop_dict[uniquename])
            
            this_feature_prop = prop_dict[uniquename]
            this_feature_prop["props"].append(r)
            
        
        prop_dict = None
        
        data = {
            "response" : {
                "name" : "genes/featureproperties",
                "features" : prop_list
            }
        }
        #data = self.api.getFeatureProps(uniqueNames)
        return data
    
    featureproperties.arguments = {
        "uniqueName" : "the uniqueName of the feature whose properties you're after",
        "u" : "shorthand for the uniqueName parameter",
        "us" : "a single string making up a list of uniqueNames, delimmited by the delimiter parameter",
        "delimiter" : "instructs how to split strings, defaults to a comma(,)"
    }
    
    @cherrypy.expose
    @ropy.server.service_format()
    def list(self, taxonID):
        """
            Returns a list of genes in an organism.
        """
        organism_id = self.queries.getOrganismFromTaxon(taxonID)
        results = self.queries.getCDSs(organism_id)
        data = {
            "response" : {
                "name" : "genes/list",
                "genes" : results
            }
        }
        return data
        #return self.api.getCDSs(taxonID)
    list.arguments = {
        "taxonID" : "the taxonID of the organism you wish to obtain genes from"
    }
    
    @cherrypy.expose
    @ropy.server.service_format()
    def residues(self, sourcefeature, **kwargs):
        """
            Returns the sequences of features mapped onto a source feature.
        """
        features = ropy.server.get_array_from_hash("features", kwargs, True)
        logger.debug(features)
        #return self.api.getFeatureResiduesFromSourceFeature(sourcefeature, features)
        results = self.queries.getFeatureResiduesFromSourceFeature(sourcefeature, features)
        data = {
            "response" : {
                "name" : "genes/residues",
                "residues" : results
            }
        }
        return data
    residues.arguments = {
        "sourcefeature" : "the uniquename of a sourcefeature, i.e. one of the entries returned by /top.",
        "features" : "a list of features located on the source features, whose sequences you wish to retrieve"
    }
    
    @cherrypy.expose
    @ropy.server.service_format()
    def mrnaresidues(self, **kwargs):
        """
            Returns a mRNA sequences for a list of genes.
        """
        genenames = ropy.server.get_array_from_hash("genenames", kwargs)
        results = self.queries.getMRNAs(genenames)
        data = {
            "response" : {
                "name" : "genes/mrnaresidues",
                "mrnas" : results
            }
        }
        return data
        #return self.api.getMRNAs(genenames)
    mrnaresidues.arguments = {
        "genenames" : "a list of genenames, for instance as supplied by the /genes endpoint"
    }
    
    
    @cherrypy.expose
    @ropy.server.service_format()
    def polypeptideresidues(self, **kwargs):
        """
            Returns a polypeptide sequences for a list of genes.
        """
        genenames = ropy.server.get_array_from_hash("genenames", kwargs)
        results = self.queries.getPEPs(genenames)
        data = {
            "response" : {
                "name" : "genes/polypeptideresidues",
                "polypeptides" : results
            }
        }
        return data
#        return self.api.getPEPs(genenames)
    polypeptideresidues.arguments = {
        "genenames" : "a list of genenames, for instance as supplied by the /genes endpoint"
    }
    
    
    @cherrypy.expose
    @ropy.server.service_format()
    def length(self, uniquename):
        """
            Returns the length of a feature.
        """
        results = self.queries.getFeatureLength(uniquename)
        data = {
            "response" : {
                "name" :"genes/length",
                "length" : results
            }
        }
        return data
        #return self.api.getFeatureLength(uniquename)
    length.arguments = { "uniquename" : "the uniquename of the feature" }
    
    @cherrypy.expose
    @ropy.server.service_format()
    def featurecvterm(self, **kwargs):
        """
            Returns cvterms of type cv_names associated with list of features.
        """
        #return self.api.getFeatureCVTerm(features, cvnames)
        features = ropy.server.get_array_from_hash("features", kwargs)
        
        if len (features) == 0: raise ropy.server.ServerException("Please supply at least one feature parameter", ropy.server.ERROR_CODES["MISSING_PARAMETER"])
        
        cvs = ropy.server.get_array_from_hash("cvs", kwargs)
        results = self.queries.getFeatureCVTerm(features, cvs)
        
        to_return = []
        feature_store = {}
        cvterm_store = {}
        
        for result in results:
            if result["feature"] not in feature_store:
                feature_store[result["feature"]] =  {
                    "feature" : result["feature"],
                    "terms" : []
                }
                to_return.append (feature_store[result["feature"]])
                
            if result["cv"] != None:
                cvterm_store_key = result["feature"] + result["cvterm"]
                
                if cvterm_store_key not in cvterm_store:
                    cvterm_store[cvterm_store_key] = {
                        "cvterm" : result["cvterm"],
                        "cv" : result["cv"],
                        "props" : [],
                        "pubs": self.queries.getFeatureCVTermPub(result["feature_cvterm_id"]),
                        "dbxrefs" : self.queries.getFeatureCVTermDbxrefs(result["feature_cvterm_id"])
                    }
                    
                    
                    feature_store[result["feature"]]["terms"].append(cvterm_store[cvterm_store_key])
                
                if "prop" in result and result["prop"] != "None":
                    cvterm_store[cvterm_store_key]["props"].append ({
                        "prop" : result["prop"],
                        "proptype" : result["proptype"],
                        "proptypecv" : result["proptypecv"]
                    })
            
        feature_store = None
        cvterm_store = None
        
        data = {
            "response" : {
                "name" :"genes/featurecvterms",
                "features" : to_return
            }
        }
        return data
    featurecvterm.arguments = { 
        "features" : "the uniquenames of the features", 
        "cvs": "the names of the cvs" 
    }
    
    def historyeventtypes(self):
        """
            Returns the types of history events.
        """
        return self.queries.getAnnotationChangeCvterms();
    historyeventtypes.arguments = { }
    
    
    def featurecoordinates(self, sourcefeature, features):
        results = self.queries.getFeatureCoordinates(sourcefeature, features)
        
        data = {
            "response" : {
                "name" :"genes/featurecoordinates",
                "coordinates" : results
            }
        }
        return data
    featurecoordinates.arguments = {
        "sourcefeature" : "the sourcefeature upon which the features are located", 
        "features": "the features" 
    }

    def exoncoordinates(self, sourcefeature, genes):
        results = self.queries.getExonCoordinates(sourcefeature, genes)
        data = {
            "response" : {
                "name" :"genes/exoncoordinates",
                "coordinates" : results
            }
        }
        return data
    featurecoordinates.arguments = {
        "sourcefeature" : "the sourcefeature upon which the genes are located", 
        "features": "the gene features" 
    }
    
    def annotationchangecvterms(self):
        data = {
            "response" : {
                "name" :"genes/annotationchangecvterms",
                "coordinates" : self.queries.getAnnotationChangeCvterms()
            }
        }
        return data
    annotationchangecvterms.arguments = {}




class SourceFeatures(BaseController):
    """
        Source feature related queries.
    """
    @cherrypy.expose
    @ropy.server.service_format()
    def sequence(self, uniqueName, start, end):
        """
            Returns the sequence of a source feature.
        """
        rows = self.queries.getSourceFeatureSequence(uniqueName)
        row = rows[0]

        length = row["length"]
        dna = row["dna"]
        dna = dna[int(start)-1:int(end)-1]

        data = {
            "response" : {
                "name" : "sourcefeatures/sequence",
                "sequence" :  [{
                    "uniqueName" : uniqueName,
                    "start" : start,
                    "end" : end,
                    "length" : length,
                    "dna" : dna
                }]
            }
        }
        #data = self.api.getSoureFeatureSequence(uniqueName, start, end)
        return data
    
    sequence.arguments = { 
        "uniqueName" : "the uniqueName of the source feature" ,
        "start" : "the start position in the sequence that you wish to retrieve (counting from 1)",
        "end" : "the end position in the sequence that you wish to retrieve (counting from 1)"
    }
    
    
    @cherrypy.expose
    @ropy.server.service_format()
    def featureloc(self, uniqueName, start, end, **kwargs):
        """
            Returns information about all the features located on a source feature within min and max boundaries.
        """
        
        relationships = ropy.server.get_array_from_hash("relationships", kwargs)
        # logger.debug(relationships)
        
        if len(relationships) == 0: 
            relationships = ["part_of", "derives_from"]
        
        logger.debug(relationships)
        logger.debug(uniqueName + " : " + str(start) + " - " + str(end))
        
        #data = self.api.getFeatureLoc(uniqueName, start, end, relationships)
        
        #relationships = []
        
        
        
        
        
        sourceFeatureID = self.queries.getFeatureID(uniqueName)
        
        relationship_ids = []
        
        """
            part_of is currently stored in a different CV term to the rest :
            select count(type_id), cvterm.name, cv.name from feature_relationship join cvterm on feature_relationship.type_id = cvterm.cvterm_id join cv on cvterm.cv_id = cv.cv_id group by cvterm.name, cv.name;
              count  |      name      |     name     
            ---------+----------------+--------------
              510619 | derives_from   | sequence
              406534 | orthologous_to | sequence
                 341 | paralogous_to  | sequence
             1929818 | part_of        | relationship
            
            so we need to make sure that its cvterm_id is fetched from the right cv!
        """
        if "part_of" in relationships:
            relationships.remove("part_of")
            relationship_ids = self.queries.getCvtermID("sequence", relationships)
            part_of_id = self.queries.getCvtermID("relationship", ["part_of"])[0]
            relationship_ids.append(part_of_id)
        else:
            relationship_ids = self.queries.getCvtermID("sequence", relationships)
        
        
        if len(relationship_ids) == 0:
            raise ropy.server.ServerException("Could not find any cvterms " + str(relationships) + " in the relationship cv.", ropy.server.ERROR_CODES["DATA_NOT_FOUND"])
        
        # logger.debug(relationships)
        # logger.debug(relationship_ids)
        
        rows = self.queries.getFeatureLocs(sourceFeatureID, start, end, relationship_ids)
        
        # an to place the root level results
        featurelocs = []
        
        # a temporary hash store, keyed on uniquename, that keeps track of what features have
        # been generated so far... 
        result_map = {}
        
        for r in rows:
            
            root = None
            if r['l1_uniquename'] in result_map:
                root = result_map[r['l1_uniquename']]
            else:
                root = {
                    "uniquename" : r["l1_uniquename"],
                    "start" : r["l1_fmin"],
                    "end" : r["l1_fmax"],
                    "strand" : r["l1_strand"],
                    "phase" : r["l1_phase"],
                    "seqlen" : r["l1_seqlen"],
                    "relationship_type" : "",
                    "type" : r["l1_type"],
                    "is_obsolete" : r["l1_is_obsolete"],
                    "feature_id" : r["l1_feature_id"],
                    "parent" : "",
                    "features" : []
                }
                result_map[r['l1_uniquename']] = root
                featurelocs.append(root)
            
            if r['l2_uniquename'] != "None": 
                # logger.debug(r['l2_uniquename'])
                if r['l2_uniquename'] in result_map:
                    l2 = result_map[r['l2_uniquename']]
                else:
                    l2 = {
                        "uniquename" : r["l2_uniquename"],
                        "start" : r["l2_fmin"],
                        "end" : r["l2_fmax"],
                        "strand" : r["l2_strand"],
                        "phase" : r["l2_phase"],
                        "seqlen" : r["l2_seqlen"],
                        "relationship_type" : r["l2_reltype"],
                        "type" : r["l2_type"],
                        "is_obsolete" : r["l2_is_obsolete"],
                        "feature_id" : r["l2_feature_id"],
                        "parent" : root["uniquename"],
                        "features" : []
                    }
                    root["features"].append(l2)
                    result_map[r['l2_uniquename']] = l2
            
            if r['l3_uniquename'] != "None": 
                if r['l3_uniquename'] in result_map:
                    l3 = result_map[r['l3_uniquename']]
                else:
                    l3 = {
                        "uniquename" : r["l3_uniquename"],
                        "start" : r["l3_fmin"],
                        "end" : r["l3_fmax"],
                        "strand" : r["l3_strand"],
                        "phase" : r["l3_phase"],
                        "seqlen" : r["l3_seqlen"],
                        "relationship_type" : r["l3_reltype"],
                        "type" : r["l3_type"],
                        "is_obsolete" : r["l2_is_obsolete"],
                        "feature_id" : r["l2_feature_id"],
                        "parent" : l2["uniquename"],
                        "features" : []
                    }
                    l2["features"].append(l3)
                    result_map[r['l3_uniquename']] = l3
        
        result_map = None
        
        data = {
            "response" : {
                "name" : "sourcefeatures/featureloc", 
                "uniqueName" : uniqueName,
                "features" : featurelocs
            }
        }
        
        
        return data
        
    featureloc.arguments = { 
        "uniqueName" : "the uniqueName of the source feature" ,
        "start" : "the start position of the feature locations that you wish to retrieve (counting from 1)",
        "end" : "the end position of the features locations that you wish to retrieve (counting from 1)",
        "relationships" : "an optional array (i.e. it can be specified several times) detailing the relationship types you want to have, the defaults are [part_of, derives_from]"
    }
    
    
    
    
    
    
    
    # use example of how to make an alchemy controller...
    # @cherrypy.expose
    #     def test(self):
    #         from ropy.alchemy.sqlalchemy_tool import session
    #         dbs = session.query(Db)
    #         s = []
    #         for db in dbs:
    #             s.append(db.name + "\n")
    #         return s

class Organisms(BaseController):
    """
        Organism related queries.
    """
    
    
    @cherrypy.expose
    @ropy.server.service_format()
    def changes(self, since):
        """
            Reports all the organisms, their taxononmyIDs and a count of how many features have changed since a certain date.
        """
        logger.debug(since)
        
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
            # logger.debug (organismID)
            org = organismHash[organismID]
            org["count"] = count[1]
        
        data = {
            "response" : {
                "name" : "organisms/changes",
                "since" : since,
                "results" : organismHash.values()
            }
        }
        return data
        
    changes.arguments = { "since" : "date formatted as YYYY-MM-DD" }
    
    
    @cherrypy.expose
    @ropy.server.service_format()
    def list(self):
        """
            Lists all organisms and their taxonomyIDs. 
        """
        logger.debug("?")
        organism_list = self.queries.getAllOrganismsAndTaxonIDs()
        logger.debug(organism_list)
        data = {
            "response" : {
                "name" : "organisms/list",
                "organisms" : organism_list
            }
        }
        logger.debug("?")
        return data
    
    list.arguments = {}
    



class Testing(BaseController):
    """
        Test related queries.
    """

    
    
    @cherrypy.expose
    @ropy.server.service_format()
    def forceclose(self):
        """
            Forces the connection to be closed for testing.
        """
        cherrypy.thread_data.connectionFactory.getSingleConnection().close()
        data = {
            "response" : {
                "closed" : "true"
            }
        }
        return data
    
    forceclose.arguments = {}
    
    @cherrypy.expose
    @ropy.server.service_format()
    def test(self):
        """
            Runs a query.
        """
        data = self.api.getAllOrganismsAndTaxonIDs()
        return data
    
    test.arguments = {}
    