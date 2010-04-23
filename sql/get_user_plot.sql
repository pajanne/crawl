SELECT data 
FROM graph.graph 
JOIN feature ON graph.graph.feature_id = feature.feature_id AND feature.uniquename = %s
