select organism_id 
    from organismprop 
    join cvterm on type_id = cvterm_id 
    where cvterm.name = 'taxonId' 
    and value = %s;