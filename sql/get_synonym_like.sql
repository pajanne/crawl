SELECT feature.uniquename, feature.name, synonym.name as synonym, cvterm.name as synonymtype, feature_synonym.is_current FROM feature

JOIN feature_synonym ON feature.feature_id = feature_synonym.feature_id 
JOIN synonym ON feature_synonym.synonym_id = synonym.synonym_id AND synonym.name ~* %(term)s
JOIN cvterm ON synonym.type_id = cvterm.cvterm_id 
