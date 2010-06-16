SELECT
    
    f1.uniquename as f1,
    af.uniquename as match, 
    f2.uniquename as f2, 
    
    analysis.name as analysis, 
    analysis.program, 
    analysisfeature.normscore as score, 
    
    fl1.fmin as fmin1, 
    fl1.fmax as fmax1, 
    
    fl2.fmin as fmin2, 
    fl2.fmax as fmax2,
    
    fl1.strand as f1strand,
    fl2.strand as f2strand

FROM feature f1 

JOIN featureloc fl1 ON f1.feature_id = fl1.srcfeature_id AND f1.uniquename = %(f1)s

JOIN feature af ON fl1.feature_id = af.feature_id AND af.is_analysis = true 
JOIN analysisfeature ON af.feature_id = analysisfeature.feature_id 
JOIN analysis ON analysisfeature.analysis_id = analysis.analysis_id

JOIN featureloc fl2 ON af.feature_id = fl2.feature_id AND fl2.srcfeature_id != f1.feature_id
JOIN feature f2 ON fl2.srcfeature_id = f2.feature_id AND f2.uniquename = %(f2)s

WHERE (( 
    (fl1.fmin BETWEEN %(start1)s AND %(end1)s ) OR (fl1.fmax BETWEEN %(start1)s AND %(end1)s ) 
) OR ( 
    (fl2.fmin BETWEEN %(start2)s AND %(end2)s ) OR (fl2.fmax BETWEEN %(start2)s AND %(end2)s ) 
))
