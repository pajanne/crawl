SELECT f.uniquename as feature, analysis.*, analysisfeature.rawscore
FROM feature f 
JOIN analysisfeature ON f.feature_id = analysisfeature.feature_id
JOIN analysis ON analysisfeature.analysis_id = analysis.analysis_id
WHERE f.uniquename in %(features)s