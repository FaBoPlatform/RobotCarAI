########################################
# notebooks/以下をBalancap SSD-Tensorflowにコピー
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
# Copy notebooks/ to Balancap SSD-TensorFlow
####################
cp -f $SCRIPT_DIR/../notebooks/* $SSD_TENSORFLOW_DIR/notebooks/

