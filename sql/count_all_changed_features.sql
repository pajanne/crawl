SELECT feature.organism_id, count(*), organism.common_name
from feature, organism 
where feature.timelastmodified > %s
and feature.organism_id in %s 
and feature.organism_id = organism.organism_id
group by feature.organism_id, organism.common_name;

