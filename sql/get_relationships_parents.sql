SELECT 

target.uniquename as feature,
parent.uniquename as relation,
'parent' as relationship,
relationship_type.name as relationship_type,
type.name as type

FROM feature target

JOIN feature_relationship fr ON fr.subject_id = target.feature_id and fr.type_id IN %(relationships)s
JOIN feature parent ON fr.object_id = parent.feature_id
JOIN cvterm relationship_type ON fr.type_id = relationship_type.cvterm_id
JOIN cvterm type ON parent.type_id = type.cvterm_id

WHERE target.uniquename in %(features)s