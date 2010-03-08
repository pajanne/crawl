SELECT pub.uniquename 
FROM feature_cvterm 
JOIN feature_cvterm_pub ON feature_cvterm.feature_cvterm_id = feature_cvterm_pub.feature_cvterm_id
JOIN pub on feature_cvterm_pub.pub_id = pub.pub_id
WHERE feature_cvterm.feature_cvterm_id = %(feature_cvterm_id)s
UNION
SELECT pub.uniquename
FROM feature_cvterm 
JOIN pub on feature_cvterm.pub_id = pub.pub_id
WHERE feature_cvterm.feature_cvterm_id = %(feature_cvterm_id)s