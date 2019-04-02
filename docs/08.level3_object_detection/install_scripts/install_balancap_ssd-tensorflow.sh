########################################
# Balancap SSD-Tensorflow インストール
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
# download Balancap SSD-TensorFlow
####################
mkdir -p $GIT_DIR
cd $GIT_DIR
git clone https://github.com/balancap/SSD-Tensorflow


####################
# unzip demo model
####################
if [ ! -e $SSD_TENSORFLOW_DIR/checkpoints/ssd_300_vgg.ckpt.index ]; then
    cd $SSD_TENSORFLOW_DIR/checkpoints
    unzip -u ssd_300_vgg.ckpt.zip

fi
