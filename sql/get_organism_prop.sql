SELECT o.common_name, cv.name as vocubulary, cvterm.name as term, op.value 
FROM organismprop op
JOIN organism o ON op.organism_id = o.organism_id
JOIN cvterm ON op.type_id = cvterm_id
JOIN cv ON cvterm.cv_id = cv.cv_id
WHERE op.organism_id = %(organism_id)s


