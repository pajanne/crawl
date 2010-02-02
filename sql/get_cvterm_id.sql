SELECT cvterm_id from cvterm 
LEFT JOIN cv on cvterm.cv_id = cv.cv_id
where cvterm.name = %(cvtermname)s
and cv.name = %(cvname)s