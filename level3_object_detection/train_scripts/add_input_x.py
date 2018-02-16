# coding: utf-8
# 学習したSSDモデルにinput_xを追加して、./model/以下に保存する

import os
import tensorflow as tf
slim = tf.contrib.slim
import sys
sys.path.append('/home/ubuntu/notebooks/github/SSD-Tensorflow/')
sys.path.append('../')

from nets import ssd_vgg_300
from preprocessing import ssd_vgg_preprocessing
from lib import *

MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/../output"
OUTPUT_MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/../model"
# TensorFlow session: grow memory when needed. TF, DO NOT USE ALL MY GPU MEMORY!!!
gpu_options = tf.GPUOptions(allow_growth=True)
config = tf.ConfigProto(log_device_placement=False, gpu_options=gpu_options)
isess = tf.InteractiveSession(config=config)

# Input placeholder.
net_shape = (300, 300)
data_format = 'NHWC'
img_input = tf.placeholder(tf.int32, shape=(None, None, 3),name='input_x')
# Evaluation pre-processing: resize to SSD net shape.
image_pre, labels_pre, bboxes_pre, bbox_img = ssd_vgg_preprocessing.preprocess_for_eval(
    img_input, None, None, net_shape, data_format, resize=ssd_vgg_preprocessing.Resize.WARP_RESIZE)
image_4d = tf.expand_dims(image_pre, 0)

# Define the SSD model.
reuse = True if 'ssd_net' in locals() else None
ssd_net = ssd_vgg_300.SSDNet(params=ssd_params)
with slim.arg_scope(ssd_net.arg_scope(data_format=data_format)):
    predictions, localizations, _, _ = ssd_net.net(image_4d, is_training=False, reuse=reuse)

# Restore SSD model.
checkpoint = tf.train.get_checkpoint_state(MODEL_DIR)
if checkpoint:
    # checkpointファイルから最後に保存したモデルへのパスを取得する
    ckpt_filename = checkpoint.model_checkpoint_path
    print("load {0}".format(ckpt_filename))
else:
    #ckpt_filename = '../checkpoints/ssd_300_vgg.ckpt'
    #ckpt_filename = '../checkpoints/VGG_VOC0712_SSD_300x300_ft_iter_120000.ckpt'
    ckpt_filename = os.path.abspath(os.path.dirname(__file__))+'/../output/model.ckpt-7352'

isess.run(tf.global_variables_initializer())
saver = tf.train.Saver()
saver.restore(isess, ckpt_filename)

def print_graph_operations(graph):
    # print operations
    print("----- operations in graph -----")
    for op in graph.get_operations():
        print("{} {}".format(op.name,op.outputs))
        
def print_graph_nodes(graph_def):
    # print nodes
    print("----- nodes in graph_def -----")
    for node in graph_def.node:
        print(node)

# graphを出力する
graph = tf.get_default_graph()
graph_def = graph.as_graph_def()
# print operations
print_graph_operations(graph)
saver.save(isess, OUTPUT_MODEL_DIR + '/model.ckpt')

