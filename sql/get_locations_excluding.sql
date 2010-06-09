SELECT
	f.uniqueName as feature, 
	type.name as type, 
	fl.fmin, 
	fl.fmax, 
	fl.strand,
	fl.phase,
	f.is_obsolete
	
FROM feature f

JOIN cvterm type ON f.type_id = type.cvterm_id 
JOIN featureloc fl ON (f.feature_id = fl.feature_id AND fl.srcfeature_id = %(regionid)s )

WHERE 
    (
    (fl.fmin BETWEEN %(start)s AND %(end)s ) OR (fl.fmax BETWEEN %(start)s AND %(end)s ) OR ( fl.fmin <= %(start)s AND fl.fmax >= %(end)s ) 
)
AND type.name NOT IN %(exclude)s
    
ORDER BY fl.fmin, fl.fmax;
