SELECT fc.feature_cvterm_id, fc.is_not, d.accession, f.uniquename as feature, ct.name as cvterm, c.name as cv, fcp.value as prop, fcpct.name as proptype, fcpc.name as proptypecv
FROM feature f
JOIN feature_cvterm fc ON f.feature_id = fc.feature_id
JOIN cvterm ct ON fc.cvterm_id = ct.cvterm_id
JOIN cv c ON c.cv_id = ct.cv_id AND c.name in %(cvs)s
JOIN dbxref d ON ct.dbxref_id = d.dbxref_id
LEFT OUTER JOIN feature_cvtermprop fcp on fc.feature_cvterm_id = fcp.feature_cvterm_id
LEFT OUTER JOIN cvterm fcpct on fcp.type_id = fcpct.cvterm_id 
LEFT OUTER JOIN cv fcpc ON fcpct.cv_id = fcpc.cv_id
WHERE f.uniquename in %(features)s;