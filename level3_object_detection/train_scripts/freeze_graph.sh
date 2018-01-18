########################################
# freeze_graph
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
# input_x追加
####################
cd $SSD_TENSORFLOW_DIR
python add_input_x.py

python freeze_graph.py
