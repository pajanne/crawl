SELECT feature_id as id, uniquename as uniquename, c1.name as type, timelastmodified as timelastmodified, feature_id as rootID, uniquename as rootName, c1.name as rootType
FROM feature, cvterm c1
WHERE timelastmodified >= DATE %s 
AND organism_id = %s 
AND feature.type_id IN ('792', '423')
AND c1.cvterm_id = feature.type_id
UNION 
SELECT f1.feature_id as id, f1.uniquename as uniquename, c1.name as type, f1.timelastmodified as timelastmodified, f2.feature_id as rootID, f2.uniquename as rootName, c2.name as rootType
FROM feature f1, feature f2, feature_relationship fr, cvterm c1, cvterm c2
WHERE f1.timelastmodified >= DATE %s
AND f1.organism_id = %s 
AND f2.type_id in ('792', '423')
AND fr.subject_id = f1.feature_id
AND fr.object_id = f2.feature_id
AND c1.cvterm_id = f1.type_id
AND c2.cvterm_id = f2.type_id
UNION
SELECT f1.feature_id as id, f1.uniquename as uniquename, c1.name as type, f1.timelastmodified as timelastmodified, f3.feature_id as rootID, f3.uniquename as rootName, c2.name as rootType
FROM feature f1, feature f2, feature f3, feature_relationship fr, feature_relationship fr2, cvterm c1, cvterm c2
WHERE f1.timelastmodified >= DATE %s
AND f1.organism_id = %s
AND f3.type_id in ('792', '423')
AND fr.subject_id = f1.feature_id
AND fr.object_id = f2.feature_id
AND fr2.subject_id = f2.feature_id
AND fr2.object_id = f3.feature_id
AND c1.cvterm_id = f1.type_id
AND c2.cvterm_id = f3.type_id