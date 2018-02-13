# coding: utf-8
# saver.save()で保存したcheckpointのmeta(NNモデル)と値を読み込み、学習値込みのNNモデルをmodel.pbに保存する

import os
import tensorflow as tf
from tensorflow.python.framework import graph_util
import sys
sys.path.append('/home/ubuntu/notebooks/github/SSD-Tensorflow/')

MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/model"
FROZEN_MODEL_NAME="ssd_roadsign.pb"
# 非常に粗いconv10_2とconv11_2を削ってもよい
OUTPUT_NODE_NAMES="""input_x,
ssd_300_vgg/block4_cls_pred/softmax/Reshape_1,
ssd_300_vgg/block7_cls_pred/softmax/Reshape_1,
ssd_300_vgg/block8_cls_pred/softmax/Reshape_1,
ssd_300_vgg/block9_cls_pred/softmax/Reshape_1,
ssd_300_vgg/block10_cls_pred/softmax/Reshape_1,
ssd_300_vgg/block11_cls_pred/softmax/Reshape_1,
ssd_300_vgg/block4_box/loc_pred,
ssd_300_vgg/block7_box/loc_pred,
ssd_300_vgg/block8_box/loc_pred,
ssd_300_vgg/block9_box/loc_pred,
ssd_300_vgg/block10_box/loc_pred,
ssd_300_vgg/block11_box/loc_pred,
ssd_preprocessing_train/my_bbox_img/strided_slice"""

#OUTPUT_NODE_NAMES="""input_x,
#rclasses,
#rscores,
#rbboxes"""

CLEAR_DEVICES=True

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

def freeze_graph():
    # Graphを初期化する(実行エラーで古いGraphが残っている場合に消す)
    tf.reset_default_graph()
    
    checkpoint = tf.train.get_checkpoint_state(MODEL_DIR)
    if checkpoint:
        # checkpointファイルから最後に保存したモデルへのパスを取得する
        last_model = checkpoint.model_checkpoint_path
        print("load {0}".format(last_model))

        # pbファイル名を設定する
        # We precise the file fullname of our freezed graph
        absolute_model_dir = "/".join(last_model.split('/')[:-1])
        frozen_model = absolute_model_dir + "/" + FROZEN_MODEL_NAME
        
        # Graphを読み込む
        # We import the meta graph and retrieve a Saver
        saver = tf.train.import_meta_graph(last_model + '.meta', clear_devices=CLEAR_DEVICES)
        # We retrieve the protobuf graph definition
        graph = tf.get_default_graph()
        graph_def = graph.as_graph_def()

        # print operations
        print_graph_operations(graph)

        # print nodes
        #print_graph_nodes(graph_def)

            
    else:
        # checkpointファイルが見つからない
        print("cannot find checkpoint.")
        return


    # We start a session and restore the graph weights
    with tf.Session() as sess:
        # 学習済みモデルの値を読み込む
        saver.restore(sess, last_model)

        # We use a built-in TF helper to export variables to constants
        output_graph_def = graph_util.convert_variables_to_constants(
            sess, # The session is used to retrieve the weights
            graph_def, # The graph_def is used to retrieve the nodes 
            OUTPUT_NODE_NAMES.replace('\n','').split(",") # The output node names are used to select the usefull nodes
        )

        # pbファイルに保存する
        ''' バイナリならこれでもよい
        # Finally we serialize and dump the output graph to the filesystem
        with tf.gfile.GFile(frozen_model, "wb") as f:
            f.write(output_graph_def.SerializeToString())
            print("%d ops in the final graph." % len(output_graph_def.node))
        '''
        ''' バイナリ、テキストどちらも対応 '''
        tf.train.write_graph(output_graph_def, MODEL_DIR,
                             FROZEN_MODEL_NAME, as_text=False)

        print("%d ops in the final graph." % len(output_graph_def.node))


freeze_graph()
