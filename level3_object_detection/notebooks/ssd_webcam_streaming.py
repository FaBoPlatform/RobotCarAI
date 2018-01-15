import os
import math
import random

import numpy as np
import tensorflow as tf
import cv2

slim = tf.contrib.slim
%matplotlib inline
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import sys
sys.path.append('../')

from nets import ssd_vgg_300, ssd_common, np_methods
from preprocessing import ssd_vgg_preprocessing
import visualization

# TensorFlow session: grow memory when needed. TF, DO NOT USE ALL MY GPU MEMORY!!!
gpu_options = tf.GPUOptions(allow_growth=True)
config = tf.ConfigProto(log_device_placement=False, gpu_options=gpu_options)
isess = tf.InteractiveSession(config=config)

# Input placeholder.
net_shape = (300, 300)
data_format = 'NHWC'
img_input = tf.placeholder(tf.uint8, shape=(None, None, 3))
# Evaluation pre-processing: resize to SSD net shape.
image_pre, labels_pre, bboxes_pre, bbox_img = ssd_vgg_preprocessing.preprocess_for_eval(
    img_input, None, None, net_shape, data_format, resize=ssd_vgg_preprocessing.Resize.WARP_RESIZE)
image_4d = tf.expand_dims(image_pre, 0)

# Define the SSD model.
reuse = True if 'ssd_net' in locals() else None
ssd_net = ssd_vgg_300.SSDNet()
with slim.arg_scope(ssd_net.arg_scope(data_format=data_format)):
    predictions, localisations, _, _ = ssd_net.net(image_4d, is_training=False, reuse=reuse)

# Restore SSD model.
#ckpt_filename = '../checkpoints/ssd_300_vgg.ckpt'
#ckpt_filename = '../checkpoints/VGG_VOC0712_SSD_300x300_ft_iter_120000.ckpt'
ckpt_filename = '../checkpoints/model.ckpt-4870'
isess.run(tf.global_variables_initializer())
saver = tf.train.Saver()
saver.restore(isess, ckpt_filename)

# SSD default anchor boxes.
ssd_anchors = ssd_net.anchors(net_shape)

# Main image processing routine.
def process_image(img, select_threshold=0.5, nms_threshold=.45, net_shape=(300, 300)):
    # Run SSD network.
    rimg, rpredictions, rlocalisations, rbbox_img = isess.run([image_4d, predictions, localisations, bbox_img],
                                                              feed_dict={img_input: img})

    # Get classes and bboxes from the net outputs.
    rclasses, rscores, rbboxes = np_methods.ssd_bboxes_select(
            rpredictions, rlocalisations, ssd_anchors,
            select_threshold=select_threshold, img_shape=net_shape, num_classes=21, decode=True)

    rbboxes = np_methods.bboxes_clip(rbbox_img, rbboxes)
    rclasses, rscores, rbboxes = np_methods.bboxes_sort(rclasses, rscores, rbboxes, top_k=400)
    rclasses, rscores, rbboxes = np_methods.bboxes_nms(rclasses, rscores, rbboxes, nms_threshold=nms_threshold)
    # Resize bboxes to original image shape. Note: useless for Resize.WARP!
    rbboxes = np_methods.bboxes_resize(rbbox_img, rbboxes)
    return rclasses, rscores, rbboxes

########################################
# for image
########################################
import time
'''
# Test on some demo image and visualize output.
path = '../demo/'
image_names = sorted(os.listdir(path))
for image_name in image_names:
    start_time,clock_time = time.time(),time.clock()
    img = mpimg.imread(path + image_name)
    rclasses, rscores, rbboxes =  process_image(img)
    print("time:%.8f clock:%.8f" % (time.time() - start_time,time.clock() - clock_time))

    # visualization.bboxes_draw_on_img(img, rclasses, rscores, rbboxes, visualization.colors_plasma)
    visualization.plt_bboxes(img, rclasses, rscores, rbboxes)
'''
########################################
# for video/Webcam
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


'''
OpenCVカメラ準備 ストリーミングが流れてきていること
'''
print("camera check")
import platform
vid = None
if platform.machine() == 'aarch64':
    vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
    #vid = cv2.VideoCapture('udp://localhost:8090')
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
#out = cv2.VideoWriter('../output/output.avi', int(fourcc), fps, (int(vidw), int(vidh)))
out = cv2.VideoWriter('../output/output.avi', int(fourcc), 2.1, (int(vidw), int(vidh)))

start_time,clock_time = time.time(),time.clock()
prev_time = time.time()
frame_count = 0
frame_done = 30 # この分のフレームを処理したら終了する

flag_read_frame = True # フレームの読み込み成功フラグ
cv_bgr=None
try:
    while flag_read_frame:
        if frame_count >= frame_done:
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

        # 予測実行
        rclasses, rscores, rbboxes =  process_image(cv_bgr)
        # 枠を描く
        write_bboxes(cv_bgr, rclasses, rscores, rbboxes)
        # avi動画に保存する
        out.write(cv_bgr)

        frame_count += 1

except:
    import traceback
    traceback.print_exc()
finally:
    vid.release()
    out.release()

curr_time = time.time()
exec_time = curr_time - prev_time
print('FPS:{0}'.format(frame_count/exec_time))
print("time:%.8f clock:%.8f" % (time.time() - start_time,time.clock() - clock_time))

