SELECT sf.uniquename AS sourcefeature, gene.uniquename AS gene, exon.uniquename AS exon, fl.fmin, fl.fmax
FROM feature gene

JOIN feature_relationship fr ON gene.feature_id = fr.object_id  AND (fr.type_id IN (42,69))
JOIN feature mrna ON fr.subject_id = mrna.feature_id AND mrna.type_id = 321

JOIN feature_relationship fr2 ON mrna.feature_id = fr2.object_id AND (fr2.type_id IN (42,69))
JOIN feature exon ON fr2.subject_id = exon.feature_id AND exon.type_id = 234

JOIN featureloc fl ON exon.feature_id = fl.feature_id 
JOIN feature sf ON sf.feature_id = fl.srcfeature_id AND sf.uniquename = %(sourcefeature)s

WHERE gene.type_id IN (792, 423)
AND gene.uniquename IN  %(genenames)s

;