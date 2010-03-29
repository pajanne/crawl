SELECT
	f.uniqueName as gene, 
	cv.name as gene_type, 
	
	f2.uniqueName as rna, 
	cv2.name as rna_type, 
	
	f3.uniqueName as peptide, 
	cv3.name as petdide_type,
	
	f4.uniqueName as domain,
	fl4.fmin as fmin, 
	fl4.fmax as fmax,
	cv4.name as domain_type,
	dx.accession as domain_accession,
	dx.version as domain_accession_version,
    db.name as domain_accession_db
	
FROM feature f

LEFT JOIN cvterm cv ON f.type_id = cv.cvterm_id

LEFT OUTER JOIN feature_relationship fr ON (f.feature_id = fr.object_id AND (fr.type_id in %(relationships)s ))
LEFT OUTER JOIN feature f2 ON fr.subject_id = f2.feature_id
LEFT OUTER JOIN cvterm cv2 ON f2.type_id = cv2.cvterm_id

LEFT OUTER JOIN feature_relationship fr2 ON (f2.feature_id = fr2.object_id AND (fr2.type_id in %(relationships)s ) )
LEFT OUTER JOIN feature f3 ON fr2.subject_id = f3.feature_id
LEFT OUTER JOIN cvterm cv3 ON f3.type_id = cv3.cvterm_id 

JOIN featureloc fl4 ON (fl4.srcfeature_id = f3.feature_id )
JOIN feature f4 ON (fl4.feature_id = f4.feature_id)
JOIN cvterm cv4 ON f4.type_id = cv4.cvterm_id 
LEFT JOIN dbxref dx ON f4.dbxref_id = dx.dbxref_id
LEFT JOIN db ON dx.db_id = db.db_id

WHERE f.uniqueName in %(genes)s


