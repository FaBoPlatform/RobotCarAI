########################################
# Bug fix
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/../script_define.conf


####################
# read image option change (bug fix)
####################
# UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte

# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

# before: image_data = tf.gfile.FastGFile(filename, 'r').read()
# after:  image_data = tf.gfile.FastGFile(filename, 'rb').read()
sed -i 's/image_data = tf\.gfile\.FastGFile(filename, '\''r'\'')\.read()/image_data = tf\.gfile\.FastGFile(filename, '\''rb'\'')\.read()/g' $SSD_TENSORFLOW_DIR/datasets/pascalvoc_to_tfrecords.py

