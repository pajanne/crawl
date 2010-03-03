SELECT cvterm.name, cvterm.cvterm_id 
FROM cvterm, cv 
WHERE cvterm.cv_id = cv.cv_id 
AND cv.name = 'annotation_change';