GIT_DIR=/notebooks/github
SSD_TENSORFLOW_DIR=$GIT_DIR/SSD-Tensorflow

MY_TRAIN=roadsign
VOC_DATASET_DIR=/notebooks/roadsign_data/PascalVOC
TF_DATASET_DIR=/notebooks/roadsign_data/tfrecords

LABELS[1]=stop
LABELS[2]=speed_10
LABELS[3]=speed_20
LABELS[4]=speed_30

CHECKPOINT_PATH=$SSD_TENSORFLOW_DIR/checkpoints/vgg_16.ckpt
LEARNED_CHECKPOINT_PATH=$SSD_TENSORFLOW_DIR/output/model.ckpt-4870
