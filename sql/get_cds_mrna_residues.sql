SELECT gene.uniquename AS gene, mrna.uniquename AS mrna, mrna.residues 
FROM feature gene

-- we do right joins here because we don't want empty gene fields in the output
RIGHT JOIN feature_relationship fr ON gene.feature_id = fr.object_id AND (fr.type_id IN (42,69))
RIGHT JOIN feature mrna ON fr.subject_id = mrna.feature_id AND mrna.type_id = 321

WHERE gene.type_id IN (792, 423)
AND gene.uniqueName IN %(genenames)s

;