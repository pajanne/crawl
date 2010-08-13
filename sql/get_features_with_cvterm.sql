SELECT 
    f.uniquename as feature, 
    ct.name as term,
    c.name as cv,
    fc.is_not, 
    d.accession, 
    
    ARRAY (select feature_cvtermprop.value from feature_cvtermprop where feature_cvtermprop.feature_cvterm_id = fc.feature_cvterm_id) as term_properties,
    ARRAY (select cvterm.name from feature_cvtermprop, cvterm where feature_cvtermprop.feature_cvterm_id = fc.feature_cvterm_id and cvterm.cvterm_id = feature_cvtermprop.type_id) as term_property_types,
    ARRAY (select cv.name from feature_cvtermprop, cvterm, cv where feature_cvtermprop.feature_cvterm_id = fc.feature_cvterm_id and cvterm.cvterm_id = feature_cvtermprop.type_id and cvterm.cv_id=cv.cv_id) as term_property_type_vocabularies
    
FROM feature f
JOIN feature_cvterm fc ON f.feature_id = fc.feature_id
JOIN cvterm ct ON fc.cvterm_id = ct.cvterm_id 
JOIN dbxref d ON ct.dbxref_id = d.dbxref_id

JOIN cv c ON c.cv_id = ct.cv_id 

