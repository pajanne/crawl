SELECT

f.uniquename as f,
ftype.name as ftype,
f2.uniquename as f2,
ftype2.name as ftype2,
f3.uniquename as f3,
ftype3.name as ftype3

FROM feature f
JOIN cvterm ftype ON f.type_id = ftype.cvterm_id 

LEFT JOIN feature_relationship fr ON fr.subject_id = f.feature_id and fr.type_id IN (42, 69)
LEFT JOIN feature f2 ON fr.object_id = f2.feature_id
LEFT JOIN cvterm ftype2 ON f2.type_id = ftype2.cvterm_id 

LEFT JOIN feature_relationship fr2 ON fr2.subject_id = fr.object_id and fr2.type_id IN (42, 69)
LEFT JOIN feature f3 ON fr2.object_id = f3.feature_id AND f3.type_id IN ('792', '423')
LEFT JOIN cvterm ftype3 ON f3.type_id = ftype3.cvterm_id 

WHERE f.uniquename in %(features)s


