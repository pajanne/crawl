SELECT organism_id, organismprop.value 
FROM organismprop
JOIN cvterm ON organismprop.type_id = cvterm_id
JOIN cv ON cvterm.cv_id = cv.cv_id
WHERE cv.name = %(cv_name)s
AND cvterm.name = %(cvterm_name)s
AND organism_id in %(organism_ids)s;
