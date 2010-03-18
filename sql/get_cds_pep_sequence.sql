SELECT gene.uniqueName AS gene, pep.uniqueName AS polypeptide, pep.residues as sequence
FROM feature gene

-- we do right joins here because we don't want empty gene fields in the output
RIGHT JOIN feature_relationship fr ON gene.feature_id = fr.object_id  AND (fr.type_id IN (42,69))
RIGHT JOIN feature mrna ON fr.subject_id = mrna.feature_id AND mrna.type_id = 321

RIGHT JOIN feature_relationship fr2 ON mrna.feature_id = fr2.object_id AND (fr2.type_id IN (42,69))
RIGHT JOIN feature pep ON fr2.subject_id = pep.feature_id AND pep.type_id = 191

WHERE gene.type_id IN (792, 423)
AND gene.uniqueName IN  %(genenames)s

;