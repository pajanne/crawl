SELECT
    f.uniquename as feature, 
    ct.name as term,
    c.name as cv,
    fp.value
FROM featureprop fp
JOIN feature f ON fp.feature_id = f.feature_id
JOIN cvterm ct ON fp.type_id = ct.cvterm_id 
JOIN cv c ON ct.cv_id = c.cv_id 



