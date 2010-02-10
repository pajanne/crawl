SELECT cvterm.name, featureprop.value, featureprop.rank 
FROM featureprop 
LEFT JOIN cvterm on cvterm.cvterm_id = featureprop.type_id 
WHERE feature_id = %(featureid)s;