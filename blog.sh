#!/bin/bash

# Fill this stuff in
BLOG_DIR=
OUT_DIR=
SCRIPT_PATH=

PORT_NUMBER=8000
WATCH_DIR=$BLOG_DIR


python $SCRIPT_PATH $BLOG_DIR $OUT_DIR

if [[ $1 == "-deploy" ]]; then
    python $SCRIPT_PATH $BLOG_DIR $OUT_DIR -skipdrafts
    cd $OUT_DIR
    git add . 
    git commit -am 'Automated commit' 
    git push
    cd -
elif [[ $1 == "-watch" ]]; then
    python $SCRIPT_PATH $BLOG_DIR $OUT_DIR
    cd $OUT_DIR
    python -m SimpleHTTPServer $PORT_NUMBER &
    cd -
    trap 'kill $(jobs -p)' EXIT
    echo "Started HTTP server"
    echo "Watching... $WATCH_DIR"
    WAIT_CMD="read -p \"Regen...\""
    if [[ $5 == "-inotify" ]]; then
        WAIT_CMD="inotifywait -r -e close_write,moved_to,create \"$WATCH_DIR\""
    fi
    while eval $WAIT_CMD; do
        python $SCRIPT_PATH $BLOG_DIR $OUT_DIR
    done
fi

