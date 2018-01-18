# -*- coding: utf-8 -*-
# frozen_model.pbファイルを読み込む

import tensorflow as tf
import numpy as np
import time
import os
import cv2
import random
import sys

#import sys
#sys.path.append('../')

from nets import ssd_vgg_300, np_methods

tf.reset_default_graph()

MODEL_DIR="./model"
FROZEN_MODEL_NAME="ssd_roadsign.pb"
DEMO_DIR="./demo_images"

# TensorFlow session: grow memory when needed. TF, DO NOT USE ALL MY GPU MEMORY!!!
gpu_options = tf.GPUOptions(allow_growth=True)
config = tf.ConfigProto(log_device_placement=False, gpu_options=gpu_options)

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
# 非常に粗いconv10_2とconv11_2を削ってもよい
predictions= [graph.get_tensor_by_name('prefix/ssd_300_vgg/block4_cls_pred/softmax/Reshape_1:0'),
              graph.get_tensor_by_name('prefix/ssd_300_vgg/block7_cls_pred/softmax/Reshape_1:0'),
              graph.get_tensor_by_name('prefix/ssd_300_vgg/block8_cls_pred/softmax/Reshape_1:0'),
              graph.get_tensor_by_name('prefix/ssd_300_vgg/block9_cls_pred/softmax/Reshape_1:0'),
              graph.get_tensor_by_name('prefix/ssd_300_vgg/block10_cls_pred/softmax/Reshape_1:0'),
              graph.get_tensor_by_name('prefix/ssd_300_vgg/block11_cls_pred/softmax/Reshape_1:0')]
localisations= [graph.get_tensor_by_name('prefix/ssd_300_vgg/block4_box/loc_pred:0'),
                graph.get_tensor_by_name('prefix/ssd_300_vgg/block7_box/loc_pred:0'),
                graph.get_tensor_by_name('prefix/ssd_300_vgg/block8_box/loc_pred:0'),
                graph.get_tensor_by_name('prefix/ssd_300_vgg/block9_box/loc_pred:0'),
                graph.get_tensor_by_name('prefix/ssd_300_vgg/block10_box/loc_pred:0'),
                graph.get_tensor_by_name('prefix/ssd_300_vgg/block11_box/loc_pred:0')]
bbox_img= graph.get_tensor_by_name('prefix/ssd_preprocessing_train/my_bbox_img/strided_slice:0')


# SSD default anchor boxes.
net_shape = (300, 300)
ssd_net = ssd_vgg_300.SSDNet()
ssd_anchors = ssd_net.anchors(net_shape)

########################################
# ラベル
########################################
VOC_LABELS = {
    0: 'none',
    1: 'stop',
    2: 'speed_10',
    3: 'speed_20',
    4: 'speed_30',
}
colors = [(random.randint(0,255), random.randint(0,255), random.randint(0,255)) for i in range(len(VOC_LABELS))]

def write_bboxes(img, classes, scores, bboxes):
    """Visualize bounding boxes. Largely inspired by SSD-MXNET!
    """
    height = img.shape[0]
    width = img.shape[1]
    for i in range(classes.shape[0]):
        cls_id = int(classes[i])
        if cls_id >= 0:
            score = scores[i]
            ymin = int(bboxes[i, 0] * height)
            xmin = int(bboxes[i, 1] * width)
            ymax = int(bboxes[i, 2] * height)
            xmax = int(bboxes[i, 3] * width)
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax),
                                 colors[cls_id],
                                 2)
            class_name = VOC_LABELS[cls_id]
            cv2.rectangle(img, (xmin, ymin-6), (xmin+180, ymin+6),
                                 colors[cls_id],
                                 -1)
            cv2.putText(img, '{:s} | {:.3f}'.format(class_name, score),
                           (xmin, ymin + 6),
                           cv2.FONT_HERSHEY_PLAIN, 1,
                           (255, 255, 255))

# Main image processing routine.
def process_image(sess, img, select_threshold=0.5, nms_threshold=.45, net_shape=(300, 300)):
    # Run SSD network.
    rpredictions, rlocalisations, rbbox_img = sess.run([predictions, localisations, bbox_img],
                                                       feed_dict={input_x: img})

    # Get classes and bboxes from the net outputs.
    rclasses, rscores, rbboxes = np_methods.ssd_bboxes_select(
            rpredictions, rlocalisations, ssd_anchors,
            select_threshold=select_threshold, img_shape=net_shape, num_classes=5, decode=True)

    rbboxes = np_methods.bboxes_clip(rbbox_img, rbboxes)
    rclasses, rscores, rbboxes = np_methods.bboxes_sort(rclasses, rscores, rbboxes, top_k=400)
    rclasses, rscores, rbboxes = np_methods.bboxes_nms(rclasses, rscores, rbboxes, nms_threshold=nms_threshold)
    # Resize bboxes to original image shape. Note: useless for Resize.WARP!
    rbboxes = np_methods.bboxes_resize(rbbox_img, rbboxes)
    return rclasses, rscores, rbboxes



'''
OpenCVカメラ準備 ストリーミングが流れてきていること
'''
print("camera check")
import platform
vid = None
if platform.machine() == 'aarch64':
    #vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
    vid = cv2.VideoCapture('udp://localhost:8090') # UDP Streaming
elif platform.machine() == 'armv7l': # armv7l
    vid = cv2.VideoCapture(0) # WebCam Raspberry Pi3 /dev/video0
else: # amd64
    #vid = cv2.VideoCapture(0) # WebCam
    vid = cv2.VideoCapture('udp://0084121c9205:8090') # GPU docker container id

print(vid.isOpened())
if not vid.isOpened():
    # カメラオープン失敗
    raise IOError(("Couldn't open video file or webcam. If you're "
                   "trying to open a webcam, make sure you video_path is an integer!"))

# カメラ画像サイズ(ストリーミングは値を指定しない)
#image_height = 120
#image_width = 160
#image_depth = 3    # BGRの3色

vidw = None
vidh = None
fps = None
fourcc = None
cv_version = cv2.__version__.split(".")
if cv_version[0] == '2':
    # OpenCV 2.4
    vidw = vid.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    vidh = vid.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    #fps = vid.get(cv2.cv.CV_CAP_PROP_FPS)
    #vidw = vid.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, image_width)
    #vidh = vid.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, image_height)
    fps = vid.get(cv2.cv.CV_CAP_PROP_FPS)
    fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
else:
    # OpenCV 3.1
    vidw = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    vidh = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    #fps = vid.get(cv2.CAP_PROP_FPS)
    #vidw = vid.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
    #vidh = vid.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
    fps = vid.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

# FPSは処理速度を実際の見てから考慮する
#out = cv2.VideoWriter(DEMO_DIR+'/output.avi', int(fourcc), fps, (int(vidw), int(vidh)))
out = cv2.VideoWriter(DEMO_DIR+'/output.avi', int(fourcc), 2.1, (int(vidw), int(vidh)))

frame_count = 0
frame_done = 300 # この分のフレームを処理したら終了する
total_frame_time = 0

flag_read_frame = True # フレームの読み込み成功フラグ
cv_bgr=None
with tf.Session(config=config,graph=graph) as sess:
    start_time,clock_time = time.time(),time.clock()
    try:
        while flag_read_frame:
            frame_time = time.time()
            if frame_count >= frame_done:
                flag_read_frame = False
                print("{} frame Done!".format(frame_done))
                break

            drop_frame_buffer = 10 # 10 OpenCV フレームバッファサイズ。この分のフレームを廃棄する
            while drop_frame_buffer > 0: # OpenCVカメラ画像が過去のバッファの可能性があるので、その分を廃棄する
                retval, cv_bgr = vid.read()
                drop_frame_buffer -= 1
                if not retval:
                    flag_read_frame = False
                    print("Done!")
                    break
            if not flag_read_frame:
                break
            # カメラ画像を取得する
            retval, cv_bgr = vid.read()
            if not retval:
                flag_read_frame = False
                print("Done!")
                break

            read_time = time.time() - frame_time
            # 予測実行
            rclasses, rscores, rbboxes = process_image(sess,cv_bgr)
            pred_time = time.time() - frame_time - read_time
            # 枠を描く
            write_bboxes(cv_bgr, rclasses, rscores, rbboxes)
            box_time = time.time() - frame_time - read_time - pred_time
            # avi動画に保存する
            out.write(cv_bgr)
            write_time = time.time() - frame_time - read_time - pred_time - box_time

            frame_count += 1
            total_frame_time += time.time() - frame_time
            sys.stderr.write('\r\033[K'+"FPS:{:.4} frame:{} done. read_time:{:.4} pred_time:{:.4} box_time:{:.4} write_time:{:.4}".format(frame_count/total_frame_time,frame_count,read_time,pred_time,box_time,write_time))

            sys.stderr.flush()
        
    except:
        import traceback
        traceback.print_exc()
    finally:
        curr_time = time.time()
        if frame_count > 0:
            print('FPS:{:.4} time:{:.8} clock:{:.8}'.format(frame_count/total_frame_time,time.time() - start_time,time.clock() - clock_time))
        vid.release()
        out.release()

print("end")
