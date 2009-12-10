SELECT 
    cv.name AS type, 
    fl.fmin + 1 AS start, 
    fl.fmax AS end, 
    fl.strand, 
    fl.phase, 
    f.seqlen, 
    f.name, 
    f.uniquename
    FROM feature f
    LEFT JOIN featureloc fl ON f.feature_id = fl.feature_id
    LEFT JOIN cvterm cv ON f.type_id = cv.cvterm_id
    WHERE fl.srcfeature_id = %s
    AND (fl.fmin + 1) >= %s
    AND fl.fmax <= %s
    ORDER BY fl.fmin, fl.fmax
