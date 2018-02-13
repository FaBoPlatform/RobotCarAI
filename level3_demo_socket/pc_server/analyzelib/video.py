# coding: utf-8
# OpenCV ライン検出クラス
import cv2
import numpy as np
import time
import os
import sys
import math
from analyzelib import *
import platform

class VideoReader():
    OUTPUT_DIR = './output'
    OUTPUT_FILENAME = 'analyze.avi'
    vid = None
    out = None
    def __init__(self,filepath,save=True):
        '''
        OpenCVカメラ準備
        カメラ準備が出来たらTrue、失敗したらFalseを返す
        '''
        vid = cv2.VideoCapture(filepath)

        print(vid.isOpened())
        if not vid.isOpened():
            # カメラオープン失敗は復旧できないので終了にする
            raise IOError(("Couldn't open video file or webcam. If you're "
                           "trying to open a webcam, make sure you video_path is an integer!"))

        fourcc = None
        cv_version = cv2.__version__.split(".")
        if cv_version[0] == '2':
            # OpenCV 2.4
            self.cols=vid.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
            self.rows=vid.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
            self.fps=vid.get(cv2.cv.CV_CAP_PROP_FPS)
            self.fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
        else:
            # OpenCV 3.2
            self.cols=vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.rows=vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.fps=vid.get(cv2.CAP_PROP_FPS)
            self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.vid = vid
        self.save = save
        return

    def init_write(self,fps=None,cols=None,rows=None):
        if fps is None:
            fps = self.fps
        if cols is None:
            cols = int(self.cols)*3
        if rows is None:
            rows = int(self.rows)*5

        if self.save:
            mkdir(self.OUTPUT_DIR)
            self.out = cv2.VideoWriter(os.path.join(self.OUTPUT_DIR, self.OUTPUT_FILENAME), int(self.fourcc), fps, (int(cols), int(rows)))
        return

    def __del__(self):
        if self.vid is not None:
            self.vid.release()
        if self.out is not None:
            self.out.release()
        return

    def read_frame(self):
        '''
        1フレーム読み込む
        '''
        retval, cv_bgr = self.vid.read()
        if not retval:
            print('Done.')
            return retval, cv_bgr
        return retval, cv_bgr

    def write_frame(self,cv_bgr):
        '''
        1フレームをavi動画に保存する
        '''
        self.out.write(cv_bgr)
        return
