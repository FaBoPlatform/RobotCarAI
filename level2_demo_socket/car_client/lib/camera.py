# coding: utf-8
# OpenCVカメラクラス

import cv2
import os
import platform

class Camera():
    vid = None
    out = None
    cv_bgr = None

    def __init__(self):
        return

    def __del__(self):
        if self.vid is not None:
            self.vid.release()
        if self.out is not None:
            self.out.release()
        return

    def init_webcam(self,cols=120,rows=160,fps=30,save=False):
        '''
        OpenCVカメラ準備
        カメラ準備が出来たらTrue、失敗したらFalseを返す
        '''
        vid = None
        if platform.machine() == 'aarch64':
            vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
        elif platform.machine() == 'armv7l': # armv7l
            vid = cv2.VideoCapture(0) # WebCam Raspberry Pi3 /dev/video0
        else: # amd64
            vid = cv2.VideoCapture(0) # WebCam

        print(vid.isOpened())
        if not vid.isOpened():
            # カメラオープン失敗は復旧できないので終了にする
            raise IOError(("Couldn't open video file or webcam. If you're "
                           "trying to open a webcam, make sure you video_path is an integer!"))

        fourcc = None
        cv_version = cv2.__version__.split(".")
        if cv_version[0] == '2':
            # OpenCV 2.4
            vid.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, cols)
            vid.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, rows)
            vid.set(cv2.cv.CV_CAP_PROP_FPS,fps)
            fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
        else:
            # OpenCV 3.2
            vid.set(cv2.CAP_PROP_FRAME_WIDTH, cols)
            vid.set(cv2.CAP_PROP_FRAME_HEIGHT, rows)
            vid.set(cv2.CAP_PROP_FPS,fps)
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.vid = vid
        self.cols = cols
        self.rows = rows
        self.save = save

        if save:
            mkdir(self.OUTPUT_DIR)
            self.out = cv2.VideoWriter(os.path.join(self.OUTPUT_DIR, self.OUTPUT_FILENAME), int(fourcc), fps, (int(cols), int(rows)))
        return

    def webcam_capture(self):
        '''
        webcam画像を取得する
        '''
        retval, self.cv_bgr = self.vid.read()
        if not retval:
            print('Done.')
            return False
        if self.save:
            # avi動画に保存する
            self.out.write(self.cv_bgr)
        return True
