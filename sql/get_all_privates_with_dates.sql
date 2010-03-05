select 
 gene.uniquename as geneUniquename, mrna.uniquename as mrnauniquename, transcript.uniquename as transcriptUniquename, 
 to_date (
     substr(split_part(fp.value, '; ', 2), 6, 4) || '-' || 
     substr(split_part(fp.value, '; ', 2), 10, 2) || '-' || 
     substr(split_part(fp.value, '; ', 2), 12, 2) 
     , 'YYYY-MM-DD' 
    )
 as changedate, 
 split_part(fp.value, '; ', 3) as changedetail,
 split_part(fp.value, '; ', 1) as changecurator
from featureprop fp, feature transcript, feature mrna, feature gene, feature_relationship fr, feature_relationship fr2
where fp.value like %s = true
and fp.type_id = 26766 
and fp.feature_id= transcript.feature_id
and fr.subject_id = transcript.feature_id
and fr.object_id = mrna.feature_id
and fr2.subject_id = mrna.feature_id
and fr2.object_id = gene.feature_id
AND gene.type_id in ('792', '423')
AND transcript.organism_id =  %s
AND split_part(fp.value, '; ', 2) like %s


