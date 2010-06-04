SELECT
    subject.name as term,
    type.name as relationship,
    cvtermpath.pathdistance as distance,
    object.name as object,
    object_cv.name as object_cv,
    dbxref.accession
FROM cvterm subject
JOIN cv subject_cv ON subject.cv_id = subject_cv.cv_id AND subject_cv.name = %(cv)s
JOIN cvtermpath ON subject.cvterm_id = cvtermpath.subject_id AND cvtermpath.pathdistance > 0
JOIN cvterm object ON cvtermpath.object_id = object.cvterm_id 
JOIN cv object_cv ON object.cv_id = object_cv.cv_id 
JOIN cvterm type ON cvtermpath.type_id = type.cvterm_id
JOIN dbxref ON object.dbxref_id = dbxref.dbxref_id
WHERE subject.name in %(terms)s
ORDER BY cvtermpath.pathdistance
