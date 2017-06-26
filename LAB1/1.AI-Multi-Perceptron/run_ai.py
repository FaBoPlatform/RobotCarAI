# coding: utf-8
# frozen_model.pbファイルを読み込む

import tensorflow as tf
import numpy as np
import time

tf.reset_default_graph()

FROZEN_MODEL_NAME="car_lidar_queue_100000.pb"
MODEL_DIR = "../model_car_lidar_queue"

def print_graph_operations(graph):
    # print operations
    print "----- operations in graph -----"
    for op in graph.get_operations():
        print op.name,op.outputs 
        
def print_graph_nodes(graph_def):
    # print nodes
    print "----- nodes in graph_def -----"
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
output_y= graph.get_tensor_by_name('prefix/neural_network_model/output_y:0')
ph_batch_size = graph.get_tensor_by_name('prefix/input/batch_size:0')


y_true = graph.get_tensor_by_name('prefix/queue/dequeue_op:1')
accuracy= graph.get_tensor_by_name('prefix/accuracy/accuracy:0')


loop=100
n_classes=4
total_start_time, total_start_clock = time.time(), time.clock()
# We start a session and restore the graph weights
with tf.Session(graph=graph) as sess:

    for i in range(loop):
        start_time, start_clock = time.time(), time.clock()
        # ランダム予測
        # sensors = [[LEFT45,FRONT,RIGHT45]] # unsigned int value
        sensors = np.array([np.random.randint(0,1000,3)])
        
        # max_value = [[N]] # N = 0:STOP,1:LEFT,2:FORWARD,3:RIGHT
        _output_y = sess.run(output_y,feed_dict={input_x:sensors})
        max_value = np.argmax(_output_y) # max_value
        
        print("max_value:"+str(max_value)+" input:"+str(sensors))

print("total_time: %.8f, total_clock: %.8f" % (time.time()-total_start_time,time.clock()-total_start_clock))
