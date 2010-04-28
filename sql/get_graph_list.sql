SELECT graph.graph_id as id, feature.uniquename as feature, graph.graph.name as graph, graph.graph.description
FROM graph.graph 
JOIN feature ON graph.graph.feature_id = feature.feature_id 
