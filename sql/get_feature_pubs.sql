SELECT 
    feature.uniquename as feature,
    split_part(pub.uniquename, ':', 1) as database,
    split_part(pub.uniquename, ':', 2) as accession
FROM feature
JOIN feature_pub ON feature_pub.feature_id = feature.feature_id
JOIN pub on pub.pub_id = feature_pub.pub_id
WHERE feature.uniquename in %(features)s
