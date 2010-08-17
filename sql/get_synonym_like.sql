SELECT f.uniquename, f.name, synonym.name as synonym, cvterm.name as synonymtype, feature_synonym.is_current FROM feature f

JOIN feature_synonym ON f.feature_id = feature_synonym.feature_id 
JOIN synonym ON feature_synonym.synonym_id = synonym.synonym_id 
JOIN cvterm ON synonym.type_id = cvterm.cvterm_id 

