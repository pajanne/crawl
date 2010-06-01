SELECT
    -- f.uniquename as subject, 
    af.uniquename as match, 
    q.uniquename as target, 
    analysis.name as analysis, 
    analysis.program, 
    analysisfeature.normscore as score, 
    fl.fmin as subject_fmin, 
    fl.fmax as subject_fmax, 
    fl2.fmin as target_fmin, 
    fl2.fmax as target_fmax 

FROM feature f 

JOIN featureloc fl ON f.feature_id = fl.srcfeature_id AND f.uniquename = %(subject)s
JOIN feature af ON fl.feature_id = af.feature_id AND af.is_analysis = true 

JOIN analysisfeature ON af.feature_id = analysisfeature.feature_id 
JOIN analysis ON analysisfeature.analysis_id = analysis.analysis_id

JOIN featureloc fl2 ON af.feature_id = fl2.feature_id AND fl2.srcfeature_id != f.feature_id
JOIN feature q ON fl2.srcfeature_id = q.feature_id 

AND ( 
    (fl.fmin BETWEEN %(start)s AND %(end)s ) 
    OR (fl.fmax BETWEEN %(start)s AND %(end)s ) 
    OR ( fl.fmin <= %(start)s AND fl.fmax >= %(end)s ) 
)
