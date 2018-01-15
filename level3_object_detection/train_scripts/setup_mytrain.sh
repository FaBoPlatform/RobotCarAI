########################################
# Setup mytrain
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
#NUM_CLASSES=5 # num of classes + 1(0:background) for my object detection
NUM_CLASSES=$(( ${#LABELS[@]} + 1 ))
TRAIN_CODE=train_$MY_TRAIN.py # copy train_ssd_network.py to $TRAIN_CODE
PASCALVOC_LABEL=pascalvoc_common_$MY_TRAIN

####################
# edit label
####################
cp $SSD_TENSORFLOW_DIR/datasets/pascalvoc_common.py $SSD_TENSORFLOW_DIR/datasets/$PASCALVOC_LABEL.py

# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

# before:
#VOC_LABELS = {
#    ...
#}
# after:
#VOC_LABELS = {
#    'none': (0, 'Background'),
#    'stop': (1, 'stop'),
#    'speed_10': (2, 'speed_10'),
#    'speed_20': (3, 'speed_20'),
#    'speed_30': (4, 'speed_30'),
#}
#AFTER=""VOC_LABELS = {\n 'none': (0, 'Background'),\n 'stop': ([1], 'stop'),\n 'speed_10': ([2], 'speed_10'),\n 'speed_20': ([3], 'speed_20'),\n 'speed_30': ([4], 'speed_30'),\n}\n"

AFTER="VOC_LABELS = {\n    'none': (0, 'Background'),\n"
for i in "${!LABELS[@]}"
do
    AFTER=$AFTER"    '"${LABELS[$i]}"': ("${i}", '"${LABELS[$i]}"'),\n"
done
AFTER=$AFTER"}\n"
#echo $AFTER

sed -i ':lbl1;N;s/VOC_LABELS = {[^}]*}\n/'"$AFTER"'/;b lbl1;' $SSD_TENSORFLOW_DIR/datasets/$PASCALVOC_LABEL.py


####################
# edit label images and objects
####################
cp $SSD_TENSORFLOW_DIR/datasets/pascalvoc_2012.py $SSD_TENSORFLOW_DIR/datasets/pascalvoc_$MY_TRAIN.py

# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

# before: FILE_PATTERN = 'voc_2012_%s_*.tfrecord'
# after:  FILE_PATTERN = 'roadsign_%s_*.tfrecord'

sed -i 's/FILE_PATTERN = '\''voc_2012_%s_\*\.tfrecord'\''/FILE_PATTERN = '\'''$MY_TRAIN'_%s_*.tfrecord'\''/g' $SSD_TENSORFLOW_DIR/datasets/pascalvoc_$MY_TRAIN.py


# find /home/ubuntu/notebooks/data/PascalVOC/Annotations/ -type f -name "*.xml" | xargs grep "<name>stop</name>" 2> /dev/null | wc -l
# find /home/ubuntu/notebooks/data/PascalVOC/Annotations/ -type f -name "*.xml" | xargs grep -c "<name>stop</name>" 2> /dev/null | grep -v ".xml:0" | wc -l
TOTAL_OBJECTS=0
for i in "${!LABELS[@]}"
do
    LABEL_OBJECTS[$i]=`find $VOC_DATASET_DIR/Annotations/ -type f -name "*.xml" | xargs grep "<name>${LABELS[$i]}</name>" 2> /dev/null | wc -l`
    LABEL_IMAGES[$i]=`find $VOC_DATASET_DIR/Annotations/ -type f -name "*.xml" | xargs grep -c "<name>${LABELS[$i]}</name>" 2> /dev/null | grep -v ".xml:0" | wc -l`
    TOTAL_OBJECTS=$(( $TOTAL_OBJECTS + ${LABEL_OBJECTS[$i]} ))
done
echo "total objects:"$TOTAL_OBJECTS

# before:
#SPLITS_TO_SIZES = {
#    'train': 17125,
#}
# after:
#SPLITS_TO_SIZES = {
#    'train': 66,
#}
TRAIN=$(( $TOTAL_OBJECTS / 3 * 2 ))
sed -i 's/\''train\'': 17125,/\''train\'': '$TRAIN',/g' $SSD_TENSORFLOW_DIR/datasets/pascalvoc_$MY_TRAIN.py

# check datas
echo label:objects:images
for i in "${!LABELS[@]}"
do
    echo ${LABELS[$i]}:${LABEL_OBJECTS[$i]}:${LABEL_IMAGES[$i]}
done

# before:
#TRAIN_STATISTICS = {
#    ...
#}
# after:
#TRAIN_STATISTICS = {
#    'none': (0, 0),
#    'stop': (70, 63),
#    'speed_20': (68, 59),
#    'speed_20': (168, 161),
#    'speed_30': (72, 72),
#}

AFTER="TRAIN_STATISTICS = {\n    'none': (0, 0),\n"
for i in "${!LABELS[@]}"
do
    AFTER=$AFTER"    '"${LABELS[$i]}"': ("${LABEL_OBJECTS[$i]}", '"${LABEL_IMAGES[$i]}"'),\n"
done
AFTER=$AFTER"}\n"
#echo $AFTER

sed -i ':lbl1;N;s/TRAIN_STATISTICS = {[^}]*}\n/'"$AFTER"'/;b lbl1;' $SSD_TENSORFLOW_DIR/datasets/pascalvoc_$MY_TRAIN.py


####################
# edit dataset_factory
####################
cp $SSD_TENSORFLOW_DIR/datasets/dataset_factory.py $SSD_TENSORFLOW_DIR/datasets/${MY_TRAIN}_factory.py

# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

# before:
#from datasets import cifar10
#from datasets import imagenet
#
#from datasets import pascalvoc_2007
#from datasets import pascalvoc_2012
#
#datasets_map = {
#    'cifar10': cifar10,
#    'imagenet': imagenet,
#    'pascalvoc_2007': pascalvoc_2007,
#    'pascalvoc_2012': pascalvoc_2012,
#}
# after:
#from datasets import pascalvoc_roadsign
#
#datasets_map = {
#    'pascalvoc_roadsign': pascalvoc_roadsign,
#}

AFTER="from datasets import pascalvoc_$MY_TRAIN\n\ndatasets_map = {\n    'pascalvoc_"$MY_TRAIN"': pascalvoc_"$MY_TRAIN",\n}\n"

sed -i ':lbl1;N;s/from datasets import cifar10[^}]*}\n/'"$AFTER"'/;b lbl1;' $SSD_TENSORFLOW_DIR/datasets/${MY_TRAIN}_factory.py


####################
# edit label import
####################
cp $SSD_TENSORFLOW_DIR/datasets/pascalvoc_to_tfrecords.py $SSD_TENSORFLOW_DIR/datasets/pascalvoc_${MY_TRAIN}_to_tfrecords.py

# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

# before: from datasets.pascalvoc_common import VOC_LABELS
# after:  from datasets.pascalvoc_common_roadsign import VOC_LABELS

sed -i 's/^from datasets\.pascalvoc_common import VOC_LABELS/from datasets.'$PASCALVOC_LABEL' import VOC_LABELS/g' $SSD_TENSORFLOW_DIR/datasets/pascalvoc_${MY_TRAIN}_to_tfrecords.py


####################
# edit train code
####################
cp $SSD_TENSORFLOW_DIR/train_ssd_network.py $SSD_TENSORFLOW_DIR/$TRAIN_CODE

# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

# before: 'num_classes', 21, 'Number of classes to use in the dataset.')
# after:  'num_classes', 5, 'Number of classes to use in the dataset.')
sed -i 's/'\''num_classes'\'', 21, '\''Number of classes to use in the dataset.'\'')/'\''num_classes'\'', '$NUM_CLASSES', '\''Number of classes to use in the dataset.'\'')/g' $SSD_TENSORFLOW_DIR/$TRAIN_CODE

# before: from datasets import dataset_factory
# after:  from datasets import roadsign_factory as dataset_factory
sed -i 's/from datasets import dataset_factory/from datasets import '$MY_TRAIN'_factory as dataset_factory/g' $SSD_TENSORFLOW_DIR/$TRAIN_CODE


####################
# edit data converter
####################
cp $SSD_TENSORFLOW_DIR/tf_convert_data.py $SSD_TENSORFLOW_DIR/tf_convert_data_$MY_TRAIN.py

# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

# before: from datasets import pascalvoc_to_tfrecords
# after:  from datasets import pascalvoc_roadsign_to_tfrecords as pascalvoc_to_tfrecords

sed -i 's/from datasets import pascalvoc_to_tfrecords/from datasets import pascalvoc_'$MY_TRAIN'_to_tfrecords as pascalvoc_to_tfrecords/g' $SSD_TENSORFLOW_DIR/tf_convert_data_$MY_TRAIN.py


####################
# download VGG16 model
####################
cd $SSD_TENSORFLOW_DIR/checkpoints
if [ ! -e $SSD_TENSORFLOW_DIR/checkpoints/vgg_16_2016_08_28.tar.gz ]; then
   wget http://download.tensorflow.org/models/vgg_16_2016_08_28.tar.gz
fi
if [ ! -e $SSD_TENSORFLOW_DIR/checkpoints/vgg_16.ckpt ]; then
     tar fxv vgg_16_2016_08_28.tar.gz
fi

