crawl = {
    "Connection" : {
        "host" : 'db.genedb.org',
        "database" : 'snapshot',
        "user" : 'genedb_ro',
        "password" : '',
        "port" : 5432
    },
    "server.socket_port" : 7666,
    "server.socket_host" : '0.0.0.0',
    "server.environment" : 'production'
}


file_store_config = {
    "path" : "/Users/gv1/Documents/Data/heirarchy",
    "db_mappings" : [
        {
            "folder" : "^\S+MRSA252\S+",
            "name" : "Staphylococcus aureus (MRSA252)",
            "organismID" : "65", 
            "chromosomes" : "*"
        },
        {
            "folder" : "^\S+B_bronchiseptica_RB50\S+",
            "name" : "Bordetella bronchiseptica",
            "organismID" : "49", 
            "chromosomes" : "*"
        },
        {
            "folder" : "^\S+S_Typhimurium_D23580\S+",
            "name" : "Salmonella typhimurium",
            "organismID" : "165", 
            "chromosomes" : "*"
        }
    ]
}

