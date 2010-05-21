SELECT
	f.uniqueName as uniqueName, 
	cv.name as type, 
	fl.fmin as fmin, 
	fl.fmax as fmax, 
	fl.strand as strand,
	fl.phase as phase,
	fl.fmax - fl.fmin as seqlen, 
	f.is_obsolete as is_obsolete,
	f.feature_id as feature_id
	
FROM feature f

LEFT JOIN cvterm cv ON f.type_id = cv.cvterm_id
LEFT JOIN featureloc fl ON f.feature_id = fl.feature_id AND fl.srcfeature_id = %(regionid)s 

LEFT JOIN feature_relationship nfr ON f.feature_id = nfr.subject_id 

WHERE nfr.subject_id IS NULL

AND ( 
    (fl.fmin BETWEEN %(start)s AND %(end)s ) 
    OR (fl.fmax BETWEEN %(start)s AND %(end)s ) 
    OR ( fl.fmin <= %(start)s AND fl.fmax >= %(end)s ) 
)

AND f.uniquename like %(term)s 

ORDER BY fl.fmin, fl.fmax
