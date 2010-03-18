SELECT sf.uniquename AS region, gene.uniquename AS gene, fl.fmin, fl.fmax
FROM feature gene

JOIN featureloc fl ON gene.feature_id = fl.feature_id 
JOIN feature sf ON sf.feature_id = fl.srcfeature_id AND sf.uniquename = %(region)s

WHERE gene.type_id IN (792, 423)
;