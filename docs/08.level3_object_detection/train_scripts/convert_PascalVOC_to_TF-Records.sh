########################################
# Convert Pascal VOC datasets to TF-Records
########################################
# Balancap SSDではTF-Recordsデータに変化する必要がある
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
OUTPUT_NAME=${MY_TRAIN}_train


#OUTPUT_NAMEは読み込み時にSSD-TensorFlowのどこかにハードコーディングされている
# find ./ -type f -name "*.py" | xargs grep -Hn -B 0 -A 0 "voc_2007_" 2> /dev/null
#./datasets/pascalvoc_2007.py:22:FILE_PATTERN = 'voc_2007_%s_*.tfrecord'
#voc_2007_train_*.tfrecord

mkdir -p $TF_DATASET_DIR

cd $SSD_TENSORFLOW_DIR

python tf_convert_data_$MY_TRAIN.py \
    --dataset_name=pascalvoc \
    --dataset_dir=$VOC_DATASET_DIR \
    --output_name=$OUTPUT_NAME \
    --output_dir=$TF_DATASET_DIR


