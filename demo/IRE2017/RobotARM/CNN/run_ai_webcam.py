# coding: utf-8
# cnn_model.pbファイルを読み込む

import tensorflow as tf
import numpy as np
import time
import sys

import os
import cv2

tf.reset_default_graph()

MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/model"
FROZEN_MODEL_NAME="cnn_model.pb"

# 予測結果を./predictionディレクトリ以下に保存するかどうか
PREDICTION_DIR=os.path.abspath(os.path.dirname(__file__))+"/prediction"
SAVE_PREDICTION=True

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
score= graph.get_tensor_by_name('prefix/score:0')
step = graph.get_tensor_by_name('prefix/step/step:0')

# OpenCV 画像を読み込む
#imageFormat=1
#cv_bgr = cv2.imread(os.path.join(path, file_name), imageFormat)

# OpenCV Webカメラ準備
import platform
vid = None
if platform.machine() == 'aarch64':
    vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
else: # armv7l
    vid = cv2.VideoCapture(0) # WebCam Raspberry Pi3 /dev/video0
print(vid.isOpened())
if not vid.isOpened():
    raise IOError(("Couldn't open video file or webcam. If you're "
    "trying to open a webcam, make sure you video_path is an integer!"))

# カメラ画像サイズ
image_height = 120
image_width = 160
image_depth = 3

vidw = None
vidh = None
fps = None
fourcc = None
cv_version = cv2.__version__.split(".")
if cv_version[0] == '2':
    # OpenCV 2.4
    vidw = vid.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, image_width)
    vidh = vid.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, image_height)
    fps = vid.get(cv2.cv.CV_CAP_PROP_FPS)
    fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
else:
    # OpenCV 3.2
    vidw = vid.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
    vidh = vid.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
    fps = vid.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')


start_time, clock_time = time.time(), time.clock()
# We start a session and restore the graph weights
with tf.Session(graph=graph) as sess:

    # CNNモデルの入力値となる画像サイズ
    data_cols=image_height * image_width * image_depth # 160*120*3

    frame_cnt = 0

    learned_step = sess.run(step)
    print("learned_step:{}".format(learned_step))

    if SAVE_PREDICTION:
        if not os.path.exists(PREDICTION_DIR):
            os.makedirs(PREDICTION_DIR)
    prev_time = time.time()
    try:
        while True:
            retval, cv_bgr = vid.read()
            if not retval:
                print("Done!")
                break
        
            frame_cnt += 1

            ########################################
            # CNNモデルの入力値となる画像サイズにリサイズする
            ########################################
            #cv_bgr = cv2.resize(cv_bgr, (image_height,image_width), interpolation = cv2.INTER_LINEAR)

            image_data = cv_bgr.reshape(1,data_cols)

            _output_y,_score = sess.run([output_y,score],feed_dict={input_x:image_data})
            #print(_output_y[0]) # 予測値
            max_index=np.argmax(_output_y[0])
            prediction_score = _score[0][max_index]
            print("prediction:{} score:{}".format(max_index,prediction_score)) # 予測クラス 0:その他 1:ラベル1 2:ラベル2 ..

            if SAVE_PREDICTION:
                SAVE_DIR=PREDICTION_DIR+"/"+str(max_index)
                if not os.path.exists(SAVE_DIR):
                    os.makedirs(SAVE_DIR)
                cv2.imwrite(SAVE_DIR+"/pred1-"+str(frame_cnt)+".png",cv_bgr)


            #if frame_cnt >= 100:
            #    print("100 frame Done!")
            #    break
    except:
        import traceback
        traceback.print_exc()
    finally:
        curr_time = time.time()
        exec_time = curr_time - prev_time
        print('FPS:{0}'.format(frame_cnt/exec_time))
        print("time:%.8f clock:%.8f" % (time.time() - start_time,time.clock() - clock_time))
        vid.release()

    
print("end")
