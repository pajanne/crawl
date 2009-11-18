#!/bin/bash

if [ $# != 3 ]; then
  echo "./charpy test|run|export -conf /path/to/conf/file.ini"
  exit 1
fi

# edit this path to point to the genlib folder, as well as to the charpy folder
GENEDB_LIB_PATH=/home/gv1/code/genlib/python:/home/gv1/code/charpy

export PYTHONPATH=$PYTHONPATH:$GENEDB_LIB_PATH

case "$1" in
test) 
    python src/unit_tests.py $@
    ;;
run) 
    python src/server.py $@
    ;;
export) 
    python src/bulk_export.py $@
    ;;
*)
    echo "Unknown server command."
    exit 1
    ;;
esac




