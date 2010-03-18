SELECT 
    src.uniquename as region, 
    substr(src.residues, fl.fmin, fl.fmax) AS sequence,
    f.uniquename as feature
FROM feature src 
JOIN featureloc fl ON src.feature_id = fl.srcfeature_id
JOIN feature f ON fl.feature_id = f.feature_id AND f.uniquename IN %(features)s
WHERE src.uniquename = %(region)s
;