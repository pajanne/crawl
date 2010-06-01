SELECT 
    f.uniquename as feature, 
    ct.name as term,
    c.name as vocabulary,
    fc.is_not, 
    d.accession
    
FROM feature f 
JOIN feature_cvterm fc ON f.feature_id = fc.feature_id
JOIN cvterm ct ON fc.cvterm_id = ct.cvterm_id 
JOIN cv c ON c.cv_id = ct.cv_id AND c.name in %(cvs)s
JOIN dbxref d ON ct.dbxref_id = d.dbxref_id

WHERE f.organism_id = %(organism_id)s

