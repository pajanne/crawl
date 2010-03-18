SELECT
	f.uniqueName as l1_uniqueName, 
	cv.name as l1_type, 
	fl.fmin as l1_fmin, 
	fl.fmax as l1_fmax, 
	fl.strand as l1_strand,
	fl.phase as l1_phase,
	fl.fmax - fl.fmin as l1_seqlen, 
	f.is_obsolete as l1_is_obsolete,
	f.feature_id as l1_feature_id,
	
	f2.uniqueName as l2_uniqueName, 
	fl2.fmin as l2_fmin, 
	fl2.fmax as l2_fmax, 
	cv2.name as l2_type, 
	fl2.strand as l2_strand,
	fl2.phase as l2_phase,
	fl2.fmax - fl2.fmin as l2_seqlen, 
	flt.name as l2_reltype,
	f2.is_obsolete as l2_is_obsolete,
	f2.feature_id as l2_feature_id,
	
	f3.uniqueName as l3_uniqueName, 
	fl3.fmin as l3_fmin, 
	fl3.fmax as l3_fmax, 
	cv3.name as l3_type,
	fl3.strand as l3_strand,
	fl3.phase as l3_phase,
	fl3.fmax - fl3.fmin as l3_seqlen,
	flt2.name as l3_reltype,
	f3.is_obsolete as l3_is_obsolete,
	f3.feature_id as l3_feature_id
	
FROM feature f

LEFT JOIN cvterm cv ON f.type_id = cv.cvterm_id
LEFT JOIN featureloc fl ON (f.feature_id = fl.feature_id AND fl.srcfeature_id = %(regionid)s )

LEFT JOIN feature_relationship nfr ON (f.feature_id = nfr.subject_id AND (nfr.type_id in %(relationships)s ))

LEFT OUTER JOIN feature_relationship fr ON (f.feature_id = fr.object_id AND (fr.type_id in %(relationships)s ))
LEFT OUTER JOIN feature f2 ON fr.subject_id = f2.feature_id
LEFT OUTER JOIN cvterm cv2 ON f2.type_id = cv2.cvterm_id
LEFT OUTER JOIN featureloc fl2 ON (f2.feature_id = fl2.feature_id AND fl2.srcfeature_id = %(regionid)s )
LEFT OUTER JOIN cvterm flt on fr.type_id = flt.cvterm_id

LEFT OUTER JOIN feature_relationship fr2 ON (f2.feature_id = fr2.object_id AND (fr2.type_id in %(relationships)s ))
LEFT OUTER JOIN feature f3 ON fr2.subject_id = f3.feature_id
LEFT OUTER JOIN cvterm cv3 ON f3.type_id = cv3.cvterm_id
LEFT OUTER JOIN featureloc fl3 ON (f3.feature_id = fl3.feature_id AND fl3.srcfeature_id = %(regionid)s )
LEFT OUTER JOIN cvterm flt2 on fr2.type_id = flt2.cvterm_id

WHERE nfr.subject_id IS NULL

AND ( 
    (fl.fmin BETWEEN %(start)s AND %(end)s ) 
    OR (fl.fmax BETWEEN %(start)s AND %(end)s ) 
    OR ( fl.fmin <= %(start)s AND fl.fmax >= %(end)s ) 
)




ORDER BY fl.fmin, fl.fmax;
