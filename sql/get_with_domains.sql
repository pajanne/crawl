SELECT
    domain.uniquename as domain,
    peptide.uniquename as peptide,
    gene.uniquename as gene,
    dx.accession as domain_accession,
	dx.version as domain_accession_version,
    db.name as domain_accession_db
    
FROM feature domain

JOIN featureloc fl ON fl.feature_id = domain.feature_id 

JOIN feature_relationship peptide_mrna ON peptide_mrna.subject_id = fl.srcfeature_id AND (peptide_mrna.type_id in %(relationships)s ) 
JOIN feature peptide ON peptide_mrna.subject_id = peptide.feature_id 
JOIN feature_relationship mrna_gene ON mrna_gene.subject_id = peptide_mrna.object_id  AND (mrna_gene.type_id in %(relationships)s )
JOIN feature gene ON gene.feature_id = mrna_gene.object_id

LEFT JOIN dbxref dx ON domain.dbxref_id = dx.dbxref_id
LEFT JOIN db ON dx.db_id = db.db_id

WHERE domain.uniqueName in %(domains)s
