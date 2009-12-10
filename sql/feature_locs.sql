SELECT f.feature_id, sf.uniquename AS ref, dbx.accession AS source, cv.name AS type, fl.fmin + 1 AS fstart, fl.fmax AS fend, af.significance AS score, fl.strand, fl.phase, f.seqlen, f.name, f.organism_id, f.uniquename
    FROM feature f
    LEFT JOIN featureloc fl ON f.feature_id = fl.feature_id
    LEFT JOIN feature sf ON fl.srcfeature_id = sf.feature_id  
    LEFT JOIN feature_dbxref fd ON f.feature_id = fd.feature_id
    LEFT JOIN dbxref dbx ON dbx.dbxref_id = fd.dbxref_id AND 
        (dbx.db_id IN 
            ( SELECT db.db_id FROM db WHERE db.name::text = 'GFF_source'::text
        ))
    LEFT JOIN cvterm cv ON f.type_id = cv.cvterm_id
    LEFT JOIN analysisfeature af ON f.feature_id = af.feature_id
    WHERE fl.srcfeature_id = %s
    AND (fl.fmin + 1) >= %s
    AND fl.fmax <= %s
    ORDER BY fl.fmin, fl.fmax