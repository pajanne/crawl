SELECT

target.uniquename as feature,
child.uniquename as uniquename,
child.name as name,
'child' as relationship,
relationship_type.name as relationship_type,
type.name as type

FROM feature target

JOIN feature_relationship fr2 ON fr2.object_id = target.feature_id and fr2.type_id IN %(relationships)s
JOIN feature child ON fr2.subject_id = child.feature_id
JOIN cvterm relationship_type ON fr2.type_id = relationship_type.cvterm_id
JOIN cvterm type ON child.type_id = type.cvterm_id

WHERE target.uniquename in %(features)s

