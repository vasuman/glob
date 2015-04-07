#!/bin/bash

# Pass these arguments
BLOG_DIR=$1
OUT_DIR=$2
SCRIPT_PATH=$3

PORT_NUMBER=8000
WATCH_DIR=$BLOG_DIR


# Fourth argument is an additional flag
if [[ $4 == "-deploy" ]]; then
    python $SCRIPT_PATH $BLOG_DIR $OUT_DIR -skipdrafts
    cd $OUT_DIR
    git add . 
    git commit -am 'Automated commit' 
    git push
    cd -
elif [[ $4 == "-watch" ]]; then
    python $SCRIPT_PATH $BLOG_DIR $OUT_DIR
    cd $OUT_DIR
    python -m SimpleHTTPServer $PORT_NUMBER &
    cd -
    trap 'kill $(jobs -p)' EXIT
    echo "Started HTTP server"
    echo "Watching... $WATCH_DIR"
    while inotifywait -r -e close_write,moved_to,create "$WATCH_DIR"; do
        python $SCRIPT_PATH $BLOG_DIR $OUT_DIR
    done
fi

