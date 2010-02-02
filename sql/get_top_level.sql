select f.uniquename from feature f
join featureprop using (feature_id)
where f.organism_id= %s
and featureprop.type_id = (select cvterm_id from cvterm join cv using (cv_id) where cv.name = 'genedb_misc' and cvterm.name = 'top_level_seq')  
order by uniquename