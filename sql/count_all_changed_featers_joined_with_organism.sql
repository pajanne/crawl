-- not currently used but it might be useful (quite slow as it is, and doesn't return organisms without changes)

select o.genus || ' ' || o.species as name, o.organism_id as organism_id, op.value as taxonomyID, count(f)
from organism o, organismprop op, cvterm c, feature f

where op.type_id = c.cvterm_id 
and c.name = 'taxonId'
and o.organism_id = op.organism_id

and f.organism_id = o.organism_id
and f.timelastmodified > DATE '2009-06-01' 
group by o.genus, o.species, o.organism_id, op.value




