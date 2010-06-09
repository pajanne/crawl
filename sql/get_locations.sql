SELECT
	f.uniqueName as feature, 
	type.name as type, 
	fl.fmin, 
	fl.fmax, 
	fl.strand,
	fl.phase,
	f.is_obsolete,
	f2.uniquename as part_of
	
FROM feature f

JOIN cvterm type ON f.type_id = type.cvterm_id
JOIN featureloc fl ON (f.feature_id = fl.feature_id AND fl.srcfeature_id = %(regionid)s )

LEFT OUTER JOIN feature_relationship fr ON f.feature_id = fr.subject_id AND fr.type_id = (select cvterm_id from cvterm where name = 'part_of')
LEFT OUTER JOIN feature f2 ON fr.subject_id = f2.feature_id

WHERE 
    (fl.fmin BETWEEN %(start)s AND %(end)s ) 
    OR (fl.fmax BETWEEN %(start)s AND %(end)s ) 
    OR ( fl.fmin <= %(start)s AND fl.fmax >= %(end)s ) 

ORDER BY fl.fmin, fl.fmax;
