SELECT 
    feature.uniquename,
    dbxref.accession,
    db.name
FROM feature
JOIN feature_dbxref ON feature_dbxref.feature_id = feature.feature_id
JOIN dbxref ON dbxref.dbxref_id = feature_dbxref.dbxref_id
JOIN db ON db.db_id = dbxref.db_id
WHERE feature.uniquename IN %(features)s
UNION
SELECT 
    feature.uniquename,
    dbxref.accession,
    db.name
FROM feature
JOIN dbxref ON dbxref.dbxref_id = feature.dbxref_id
JOIN db ON db.db_id = dbxref.db_id
WHERE feature.uniquename IN %(features)s