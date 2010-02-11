SELECT feature.uniquename, cvterm.name, featureprop.value, featureprop.rank 
FROM featureprop 
LEFT JOIN cvterm on cvterm.cvterm_id = featureprop.type_id 
LEFT JOIN feature on featureprop.feature_id = feature.feature_id
WHERE uniquename in %(uniquenames)s;