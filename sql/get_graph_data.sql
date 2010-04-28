SELECT graph_id, feature.uniquename, graph.graph.name, data 
FROM graph.graph 
JOIN feature ON graph.graph.feature_id = feature.feature_id 
WHERE graph.graph_id = %s

