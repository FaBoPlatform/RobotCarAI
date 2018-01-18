########################################
# freeze_graph
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
OUTPUT_DIR=$SCRIPT_DIR/../model


####################
# train
####################
cd $SSD_TENSORFLOW_DIR
python freeze_graph.py
