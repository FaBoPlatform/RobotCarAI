########################################
# Balancap SSD-Tensorflowにname scopeを追加する
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
# Patch to Balancap SSD-TensorFlow
####################
patch -u $SSD_TENSORFLOW_DIR/preprocessing/ssd_vgg_preprocessing.py <  $SCRIPT_DIR/../patch_to_SSD-Tensorflow/ssd_vgg_preprocessing.patch

patch -u $SSD_TENSORFLOW_DIR/net/ssd_vgg_300.py <  $SCRIPT_DIR/../patch_to_SSD-Tensorflow/ssd_vgg_300.patch
