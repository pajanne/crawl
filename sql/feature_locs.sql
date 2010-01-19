SELECT 
    cv.name AS type, 
    fl.fmin + 1 AS start, 
    fl.fmax AS end, 
    fl.strand, 
    fl.phase, 
    fl.fmax - fl.fmin as seqlen, 
    f.name, 
    f.uniquename,
    f.feature_id,
    fr.object_id as parent_id,
    pr.uniqueName as parent,
    fr.subject_id
    FROM feature f
    LEFT JOIN featureloc fl ON f.feature_id = fl.feature_id
    LEFT JOIN cvterm cv ON f.type_id = cv.cvterm_id
    LEFT OUTER JOIN feature_relationship fr ON f.feature_id = fr.subject_id
    LEFT OUTER JOIN feature pr ON fr.object_id = pr.feature_id
    WHERE fl.srcfeature_id = %s
    AND ( (fl.fmin BETWEEN %s AND %s ) OR (fl.fmax BETWEEN %s AND %s ) )
    ORDER BY fl.fmin, fl.fmax
