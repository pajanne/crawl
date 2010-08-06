select o.genus || ' ' || o.species as name, o.common_name, o.organism_id as organism_id, op.value as taxonomyID
from organism o, organismprop op, cvterm c
where op.type_id = c.cvterm_id 
and c.name = 'taxonId'
and o.organism_id = op.organism_id
order by o.genus, o.species
