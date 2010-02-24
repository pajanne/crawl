SELECT uniquename as gene, cvterm.name as type
from feature 
left join cvterm on feature.type_id = cvterm.cvterm_id 
where organism_id = %s 
and type_id in (792 , 423);