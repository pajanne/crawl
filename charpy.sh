#!/bin/bash

if [ $# -le 3 ]; then
  echo "charpy test|run|export -conf /path/to/conf/file.ini [(if run) -production True|False]"
  exit 1
fi

echo "Python version:"
python --version

export scriptpath=${0%/*} 

case "$1" in
test) 
    python $scriptpath/src/unit_tests.py $@
    ;;
run) 
    python $scriptpath/src/server.py $@
    ;;
export) 
    python $scriptpath/src/bulk_export.py $@
    ;;
*)
    echo "Unknown server command."
    exit 1
    ;;
esac




