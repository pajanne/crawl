SELECT
f.uniquename AS cluster_name,
cv_f.name AS cluster_cvterm,
f1.uniquename AS subject,
cv_fr.name AS relationship,
common_name AS subject_organism,
cv_f1.name AS subject_type,
rawscore, normscore, significance, identity, 
a.analysis_id,
a.name, 
description, 
program, programversion, algorithm, sourcename, sourceversion,sourceuri, timeexecuted,
organismprop.value as subject_taxonID,
ARRAY (
    SELECT fcc.name from feature_cvterm fc 
    JOIN cvterm fcc ON fc.cvterm_id = fcc.cvterm_id 
    JOIN cv fccc ON fccc.cv_id = fcc.cv_id AND fccc.name = 'genedb_products' 
    WHERE fc.feature_id = f.feature_id 
) as orthoproduct

FROM feature f

LEFT JOIN feature_relationship fr ON  f.feature_id=fr.object_id
LEFT JOIN analysisfeature af ON f.feature_id=af.feature_id
LEFT JOIN analysis a ON af.analysis_id=a.analysis_id
LEFT JOIN feature f1 ON f1.feature_id=subject_id
LEFT JOIN organism ON f1.organism_id=organism.organism_id

LEFT JOIN organismprop on (organismprop.organism_id = organism.organism_id and organismprop.type_id = (select cvterm_id from cvterm where name='taxonId') )

LEFT JOIN cvterm AS cv_f1 ON cv_f1.cvterm_id=f1.type_id
LEFT JOIN cvterm AS cv_fr ON cv_fr.cvterm_id=fr.type_id
LEFT JOIN cvterm AS cv_f  ON cv_f.cvterm_id=f.type_id

WHERE f.uniquename IN %(orthologues)s
AND (cv_fr.name='orthologous_to' OR cv_fr.name='paralogous_to')
