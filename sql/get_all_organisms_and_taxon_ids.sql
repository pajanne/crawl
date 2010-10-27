select o.genus || ' ' || o.species as name, o.common_name, o.organism_id as organism_id, op.value as taxonomyID
from organism o

join organismprop op on o.organism_id = op.organism_id 
join cvterm c on op.type_id = c.cvterm_id and c.name = 'taxonId'

order by o.genus, o.species
