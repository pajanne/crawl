SELECT f.uniqueName, fc_term.name as term, fc_term_cv.name as vocabulary, fcp.value as property, fcp_type.name as term_property_type from feature f
    JOIN feature_cvterm fc ON fc.feature_id = f.feature_id
    JOIN cvterm fc_term ON fc.cvterm_id = fc_term.cvterm_id
    JOIN cv fc_term_cv ON fc_term.cv_id = fc_term_cv.cv_id 
    JOIN feature_cvtermprop fcp ON fcp.feature_cvterm_id = fc.feature_cvterm_id 
    JOIN cvterm fcp_type ON fcp.type_id = fcp_type.cvterm_id 
    JOIN organism o ON f.organism_id = o.organism_id 
WHERE o.organism_id = %(organism_id)s

