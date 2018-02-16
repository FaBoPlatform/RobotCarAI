########################################
# freeze_graph
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

####################
# input_x追加
####################
python ${SCRIPT_DIR}/add_input_x.py


########################################
# freeze_graph
########################################
python freeze_graph.py
