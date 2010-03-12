SELECT 
    f.uniquename as feature, 
    orthof.uniquename as ortho,
    o.genus,
    o.species,
    op.value
FROM feature f
JOIN feature_relationship fr ON f.feature_id = fr.subject_id 
    AND fr.type_id = 
        (select cvterm.cvterm_id 
            from cvterm 
            join cv 
            on cvterm.cv_id = cvterm.cv_id 
            where cv.name = 'sequence' 
            and cvterm.name = 'orthologous_to')
JOIN feature orthof ON fr.object_id = orthof.feature_id
JOIN organism o on orthof.organism_id = o.organism_id
JOIN organismprop op on o.organism_id = op.organism_id 
    AND op.type_id = 
    (select cvterm.cvterm_id 
        from cvterm 
        join cv 
        on cvterm.cv_id = cvterm.cv_id 
        where cv.name = 'genedb_misc' 
        and cvterm.name = 'taxonId')
WHERE f.uniquename in %(features)s
;