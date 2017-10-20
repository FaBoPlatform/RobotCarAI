# coding: utf-8
# cnn_model.pbファイルを読み込む

import tensorflow as tf
import numpy as np
import time
import sys

import os
import cv2

tf.reset_default_graph()

MODEL_DIR="./model"
FROZEN_MODEL_NAME="cnn_model.pb"

path="./test_data/0"
file_name="capture288.png"

def print_graph_operations(graph):
    # print operations
    print("----- operations in graph -----")
    for op in graph.get_operations():
        print(op.name,op.outputs)
        
def print_graph_nodes(graph_def):
    # print nodes
    print("----- nodes in graph_def -----")
    for node in graph_def.node:
        print(node)

def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the 
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we can use again a convenient built-in function to import a graph_def into the 
    # current default Graph
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def, 
            input_map=None, 
            return_elements=None, 
            name="prefix", 
            op_dict=None, 
            producer_op_list=None
        )
    return graph

graph = load_graph(MODEL_DIR+"/"+FROZEN_MODEL_NAME)
graph_def = graph.as_graph_def()

# print operations
print_graph_operations(graph)

# print nodes
#print_graph_nodes(graph_def)

####################
input_x = graph.get_tensor_by_name('prefix/input_x:0')
output_y= graph.get_tensor_by_name('prefix/output_y:0')
step = graph.get_tensor_by_name('prefix/step/step:0')


imageFormat=1
cv_bgr = cv2.imread(os.path.join(path, file_name), imageFormat)

data_cols=160*120*3 # 
image_data = cv_bgr.reshape(1,data_cols)

total_start_time, total_start_clock = time.time(), time.clock()
# We start a session and restore the graph weights
with tf.Session(graph=graph) as sess:

    # numpyデータを省略せずに表示する
    np.set_printoptions(threshold=np.inf)    
    #print(image_data)
    #cv2.imwrite("output.png",image_data)
    learned_step = sess.run(step)
    print("learned_step:{}").format(learned_step)

    _output_y = sess.run(output_y,feed_dict={input_x:image_data})
    print(_output_y[0]) # 予測値
    pmax=np.argmax(_output_y[0])
    print("prediction:{}").format(pmax) # 予測クラス

print("end")
