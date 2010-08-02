SELECT 
    
    min(fmin) as start, 
    max(fmax) as end 
    
FROM feature f

JOIN featureloc fl ON (f.feature_id = fl.feature_id AND fl.srcfeature_id = %(regionid)s )

WHERE f.type_id in %(types)s 

AND (
    (fl.fmin BETWEEN %(start)s AND %(end)s ) 
    OR (fl.fmax BETWEEN %(start)s AND %(end)s ) 
    OR ( fl.fmin <= %(start)s AND fl.fmax >= %(end)s ) 
)


