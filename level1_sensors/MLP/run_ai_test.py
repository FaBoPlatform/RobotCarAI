# coding: utf-8
# frozen_model.pbファイルを読み込む
# ランダムなセンサー値を生成し、予測を実行する

import tensorflow as tf
import numpy as np
import time
import os

tf.reset_default_graph()

FROZEN_MODEL_NAME="car_model.pb"
MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/model"

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
input_x = graph.get_tensor_by_name('prefix/queue/dequeue_op:0')
output_y = graph.get_tensor_by_name('prefix/neural_network_model/output_y:0')
score = graph.get_tensor_by_name('prefix/neural_network_model/score:0')
step = graph.get_tensor_by_name('prefix/step/step:0')

total_start_time, total_start_clock = time.time(), time.clock()

# graphのweightsを復元してsessionを開始する
with tf.Session(graph=graph) as sess:
    learned_step = sess.run(step)
    print("learned_step:{}".format(learned_step))

    loop=100
    for i in range(loop):
        start_time, start_clock = time.time(), time.clock()
        # センサー値をランダムな0-1000の範囲で作成する
        # sensors = [[LEFT45,FRONT,RIGHT45]]
        sensors = np.array([np.random.randint(0,1000,3)])

        # 予測を実行する
        _output_y,_score = sess.run([output_y,score],feed_dict={input_x:sensors})
        # max_value = [[N]] # N = 0:STOP,1:LEFT,2:FORWARD,3:RIGHT
        max_value = np.argmax(_output_y) # max_value
        
        print("max_value:{} score:{} input:{}".format(max_value,_score[0][max_value],sensors))

print("total_time: %.8f, total_clock: %.8f" % (time.time()-total_start_time,time.clock()-total_start_clock))

