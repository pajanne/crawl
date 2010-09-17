select f.uniquename from feature f
join featureprop using (feature_id)
where f.organism_id= %(organism_id)s
and featureprop.type_id = %(type_id)s
