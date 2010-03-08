SELECT dbxref.accession, db.name
FROM feature_cvterm
JOIN feature_cvterm_dbxref ON feature_cvterm.feature_cvterm_id = feature_cvterm_dbxref.feature_cvterm_id
JOIN dbxref ON feature_cvterm_dbxref.dbxref_id = dbxref.dbxref_id
JOIN db ON dbxref.db_id = db.db_id
WHERE feature_cvterm.feature_cvterm_id = %(feature_cvterm_id)s
;