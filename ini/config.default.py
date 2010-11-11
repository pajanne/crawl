crawl = {
    "Connection" : {
        "host" : 'localhost',
        "database" : 'mydb',
        "user" : 'mself',
        "password" : 'mypass',
        "port" : 5432
    },
    "server.socket_port" : 6666,
    "server.socket_host" : '0.0.0.0',
    "server.environment" : 'production'
}


file_store_config = {
    "alignments" : [
        {
            "file" : "/Users/gv1/Documents/Data/heirarchy/4415_2-Staph_aureus_MRSA252_small/test.bam",
            "name" : "Staphylococcus aureus (MRSA252)",
            "organismID" : 65, 
            "chromosomes" : "*"
        },
        {
            "file" : "/Users/gv1/Documents/Data/heirarchy/4415_2_11-Staph_aureus_MRSA252/maq/raw.bam",
            "name" : "Staphylococcus aureus (MRSA252)",
            "organismID" : 65, 
            "chromosomes" : "*"
        },
        {
            "file" : "/Users/gv1/Documents/Data/heirarchy/4415_2_12-Staph_aureus_MRSA252/maq/raw.bam",
            "name" : "Staphylococcus aureus (MRSA252)",
            "organismID" : 65, 
            "chromosomes" : "*"
        },
    ]
}

