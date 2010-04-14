SELECT 

target.uniquename as feature,
parent.uniquename as relation,
'parent' as relationship,
cvterm.name as type

FROM feature target

JOIN feature_relationship fr ON fr.subject_id = target.feature_id and fr.type_id IN %(relationships)s
JOIN feature parent ON fr.object_id = parent.feature_id
JOIN cvterm ON fr.type_id = cvterm.cvterm_id

WHERE target.uniquename in %(features)s

UNION

SELECT

target.uniquename as feature,
child.uniquename as relation,
'child' as relationship,
cvterm.name as type

FROM feature target

JOIN feature_relationship fr2 ON fr2.object_id = target.feature_id and fr2.type_id IN %(relationships)s
JOIN feature child ON fr2.subject_id = child.feature_id
JOIN cvterm ON fr2.type_id = cvterm.cvterm_id

WHERE target.uniquename in %(features)s

