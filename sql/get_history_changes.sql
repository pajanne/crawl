SELECT
f.uniquename as transcriptuniquename,
-- ctype.name as type,
mrna.uniquename as mrnauniquename,
gene.uniquename as geneuniquename,
fcp_detail.value as changedetail,
to_date (fcp_date.value, 'YYYYMMDD' ) as changedate --,
-- fcp_user.value as changeuser

FROM feature f
JOIN feature_cvterm fc ON f.feature_id = fc.feature_id 
-- JOIN cvterm ctype ON f.type_id = ctype.cvterm_id

JOIN cvterm fctype ON fc.cvterm_id = fctype.cvterm_id 
JOIN cv fctypecv ON fctypecv.cv_id = fctype.cv_id AND fctypecv.name = 'annotation_change'

JOIN feature_cvtermprop fcp_date ON fc.feature_cvterm_id = fcp_date.feature_cvterm_id AND fcp_date.type_id = %(date_type_id)s
JOIN feature_cvtermprop fcp_detail ON fc.feature_cvterm_id = fcp_detail.feature_cvterm_id AND fcp_detail.type_id = %(qualifier_type_id)s
-- JOIN feature_cvtermprop fcp_user ON fc.feature_cvterm_id = fcp_user.feature_cvterm_id AND fcp_user.type_id = %(curatorName_type_id)s

LEFT JOIN feature_relationship fr ON fr.subject_id = f.feature_id and fr.type_id IN (42, 69)
LEFT JOIN feature mrna ON fr.object_id = mrna.feature_id

LEFT JOIN feature_relationship fr2 ON fr2.subject_id = fr.object_id and fr2.type_id IN (42, 69)
LEFT JOIN feature gene ON fr2.object_id = gene.feature_id AND gene.type_id IN ('792', '423')

WHERE f.organism_id = %(organism_id)s 
AND to_date (fcp_date.value, 'YYYYMMDD' ) >= DATE %(since)s;