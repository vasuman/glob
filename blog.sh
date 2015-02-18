OUT_DIR=$HOME/stuff/vasuman.github.io/
PORT_NUMBER=59937
SCRIPT_PATH=$HOME/code/py/glob/generate.py 
WATCH_DIR=$(dirname $SCRIPT_PATH)
python2 $SCRIPT_PATH $OUT_DIR
if [[ $1 == "-deploy" ]]; then
    cd $OUT_DIR
    git add . 
    git commit -am 'Automated commit' 
    git push
    cd -
elif [[ $1 == "-watch" ]]; then
    echo "Listeneing on $WATCH_DIR/posts"
    while inotifywait -e close_write,moved_to,create "$WATCH_DIR/posts"; do
        python2 $SCRIPT_PATH $OUT_DIR
    done
fi
unset OUT_DIR
unset PORT_NUMBER
unset SCRIPT_PATH
unset WATCH_DIR
