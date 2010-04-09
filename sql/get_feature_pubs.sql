SELECT 
    feature.uniquename as feature,
    pub.uniquename as pub
FROM feature
JOIN feature_pub ON feature_pub.feature_id = feature.feature_id
JOIN pub on pub.pub_id = feature_pub.pub_id
WHERE feature.uniquename in %(features)s
