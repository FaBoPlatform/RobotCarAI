########################################
# Balancap SSD-Tensorflow インストール
########################################
GIT_DIR=/notebooks/github
SSD_TENSORFLOW_DIR=$GIT_DIR/SSD-Tensorflow


####################
# download Balancap SSD-TensorFlow
####################
mkdir -p $GIT_DIR
cd $GIT_DIR
git clone https://github.com/balancap/SSD-Tensorflow


####################
# unzip demo model
####################
cd $SSD_TENSORFLOW_DIR/checkpoints
unzip -u ssd_300_vgg.ckpt.zip

