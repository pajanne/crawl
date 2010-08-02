SELECT 
    
    min(fmin) as start, 
    max(fmax) as end 
    
FROM feature f

JOIN featureloc fl ON (f.feature_id = fl.feature_id AND fl.srcfeature_id = %(regionid)s )


WHERE f.type_id in (select cvterm.cvterm_id from cvterm join cv on cvterm.cv_id = cv.cv_id and cv.name = 'sequence' and cvterm.name  in  ('gene', 'pseudogene') )
AND (
    (fl.fmin BETWEEN %(start)s AND %(end)s ) 
    OR (fl.fmax BETWEEN %(start)s AND %(end)s ) 
    OR ( fl.fmin <= %(start)s AND fl.fmax >= %(end)s ) 
)


