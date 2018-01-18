########################################
# Balancap SSD-Tensorflowにファイルをコピー
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
# Copy to Balancap SSD-TensorFlow
####################
cp -rf $SCRIPT_DIR/../copy_to_SSD-Tensorflow/* $SSD_TENSORFLOW_DIR/
