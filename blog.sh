#!/bin/bash

# Change this stuff
BLOG_DIR=$HOME/stuff/Blog/
OUT_DIR=$HOME/stuff/vasuman.github.io/
SCRIPT_PATH=$HOME/code/py/glob/generate.py 

PORT_NUMBER=59937
WATCH_DIR=$BLOG_DIR/posts
python2 $SCRIPT_PATH $BLOG_DIR $OUT_DIR
if [[ $1 == "-deploy" ]]; then
    cd $OUT_DIR
    git add . 
    git commit -am 'Automated commit' 
    git push
    cd -
elif [[ $1 == "-watch" ]]; then
    echo "Listeneing on $WATCH_DIR"
    while inotifywait -e close_write,moved_to,create "$WATCH_DIR"; do
        python2 $SCRIPT_PATH $BLOG_DIR $OUT_DIR
    done
fi
unset BLOG_DIR
unset OUT_DIR
unset PORT_NUMBER
unset SCRIPT_PATH
unset WATCH_DIR
