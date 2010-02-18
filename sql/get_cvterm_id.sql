SELECT cvterm_id from cvterm 
LEFT JOIN cv on cvterm.cv_id = cv.cv_id
where cvterm.name in %(cvtermnames)s
and cv.name = %(cvname)s