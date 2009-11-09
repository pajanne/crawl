#!/bin/bash

if [ $# != 1 ]; then
  echo "./charpy test|run|export"
  exit 1
fi

# edit this path to point to the genlib folder, as well as to the charpy folder
GENEDB_LIB_PATH=/home/gv1/code/genlib/python:/home/gv1/code/charpy

export PYTHONPATH=$PYTHONPATH:$GENEDB_LIB_PATH


case "$1" in
test) 
    python test/unit_tests.py
    ;;
run) 
    python server/server.py
    ;;
export) 
    python script/bulk_export.py
    ;;
*)
    echo "Unknown server command."
    exit 1
    ;;
esac




