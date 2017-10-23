# coding: utf-8
# frozen_model.pbファイルを読み込む

import numpy as np
import time
import sys

import os
import cv2


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
image_depth = 3 # BGRの3bit

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


def capture():
    PREDICTION_DIR="prediction"
    if not os.path.exists(PREDICTION_DIR):
        os.makedirs(PREDICTION_DIR)
    start_time, clock_time = time.time(), time.clock()
    # CNNモデルの入力値となる画像サイズ
    data_cols=image_height * image_width * image_depth

    frame_cnt = 0
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

            cv2.imwrite(PREDICTION_DIR+"/capture-"+str(frame_cnt)+".png",cv_bgr)

            time.sleep(0.2)

            #if frame_cnt >= 100:
            #    print("100 frame Done!")
            #    break
        curr_time = time.time()
        exec_time = curr_time - prev_time
        print('FPS:{0}'.format(frame_cnt/exec_time))
        print("time:%.8f clock:%.8f" % (time.time() - start_time,time.clock() - clock_time))
    except:
        import traceback
        traceback.print_exc()
    finally:
        print("vid.release")
        vid.release()




capture()
print("end")
