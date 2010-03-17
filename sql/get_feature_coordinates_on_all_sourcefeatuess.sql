SELECT sf.uniquename AS sourcefeature, f.uniquename AS feature, fl.fmin, fl.fmax 
FROM feature f
JOIN featureloc fl ON f.feature_id = fl.feature_id 
JOIN feature sf ON fl.srcfeature_id = sf.feature_id
WHERE f.uniquename in %(features)s;
