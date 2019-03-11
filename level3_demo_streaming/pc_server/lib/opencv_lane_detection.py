# coding: utf-8
# OpenCV ライン検出クラス
import cv2
import numpy as np
import time
import os
import sys
import math
from .functions import *
import platform

class LaneDetection():
    OUTPUT_DIR = './output'
    OUTPUT_FILENAME = 'capture.avi'
    vid = None
    out = None
    cv_bgr = None
    def __init__(self,x_meter,y_meter,cols=160,rows=120):
        self.x_meter = x_meter
        self.y_meter = y_meter
        self.cols = cols
        self.rows = rows
        ########################################
        # Region Of Interest Coordinates
        ########################################
        self.roi_vertices = calc_roi_vertices(cols,rows,
                                              # robocar camera demo_lane
                                              top_width_rate=0.80,top_height_position=0.65,
                                              bottom_width_rate=2.0,bottom_height_position=1)

        ########################################
        # Inverse Perspective Mapping Coordinates
        ########################################
        self.ipm_vertices = calc_ipm_vertices(cols,rows,
                                              # robocar camera demo_lane
                                              top_width_rate=0.80,top_height_position=0.65,
                                              bottom_width_rate=2.0,bottom_height_position=1)

        # ピクセルをメートルに変換
        self.ym_per_pix = 1.0*self.y_meter/self.rows
        self.xm_per_pix = 1.0*self.x_meter/self.cols

        return

    def __del__(self):
        if self.vid is not None:
            self.vid.release()
        if self.out is not None:
            self.out.release()
        return

    def init_webcam(self,fps=30,save=False):
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
            #vid = cv2.VideoCapture('udp://0084121c9205:8090') # GPU docker container id

        print(vid.isOpened())
        if not vid.isOpened():
            # カメラオープン失敗は復旧できないので終了にする
            raise IOError(("Couldn't open video file or webcam. If you're "
                           "trying to open a webcam, make sure you video_path is an integer!"))

        fourcc = None
        cv_version = cv2.__version__.split(".")
        if cv_version[0] == '2':
            # OpenCV 2.4
            vid.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.cols)
            vid.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.rows)
            vid.set(cv2.cv.CV_CAP_PROP_FPS,fps)
            fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
        else:
            # OpenCV 3.2
            vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.cols)
            vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.rows)
            vid.set(cv2.CAP_PROP_FPS,fps)
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.vid = vid
        self.save = save

        if save:
            mkdir(self.OUTPUT_DIR)
            self.out = cv2.VideoWriter(os.path.join(self.OUTPUT_DIR, self.OUTPUT_FILENAME), int(fourcc), fps, (int(self.cols), int(self.rows)))

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

    def lane_detection(self):
        '''
        ラインを検出する
        args:
        returns:
            tilt1_deg: 手前の傾き角度。-が右、+が左
            tilt2_deg: 奥の傾き角度。-が右、+が左
            angle1_deg: 手前のカーブ角度。-が左、+が右
            angle2_deg: 奥のカーブ角度。-が左、+が右
            curve1_r: 手前のカーブ半径(m)
            curve2_r: 奥のカーブ半径(m)
            meters_from_center: 中央との距離(m)
        '''
        ########################################
        # Region Of Interest
        ########################################
        cv_bgr = to_roi(self.cv_bgr,self.roi_vertices)

        ########################################
        # Inverse Perspective Mapping
        ########################################
        cv_bgr = to_ipm(cv_bgr,self.ipm_vertices)

        ########################################
        # 白色抽出
        ########################################
        cv_bgr = to_white(cv_bgr)

        ########################################
        # 画像を2値化する
        ########################################
        cv_bin = to_bin(cv_bgr)

        ########################################
        # レーンを検出する
        ########################################
        # sliding windowsを行い、ラインを構成するピクセル座標を求める
        line_x, line_y = sliding_windows(cv_bin)

        '''
        実測値 メートル座標系における計算
        '''
        # 等間隔なy座標を生成する
        plot_ym = np.linspace(0, self.rows-1, self.rows)*self.ym_per_pix
        # ラインの二次多項式と座標を求める
        line_polyfit_const, \
            _pts_line = calc_line_curve(line_x*self.xm_per_pix,line_y*self.ym_per_pix,plot_ym)

        ########################################
        # 弧の座標と角度を求める
        # センターを上下2分割にして曲率半径と中心座標、y軸との傾き角度を計算する
        ########################################
        quarter_y = (np.max(plot_ym) - np.min(plot_ym))/4
        # 下半分を計算する
        y0 = np.max(plot_ym) - 2*quarter_y
        y1 = np.max(plot_ym)
        curve1_x,curve1_y,curve1_r, \
            rotate1_deg,angle1_deg, \
            tilt1_deg = calc_curve(y0,y1,line_polyfit_const)
        # 上半分を計算する
        quarter_y = (np.max(plot_ym) - np.min(plot_ym))/4
        y0 = np.min(plot_ym)
        y1 = np.max(plot_ym) - 2*quarter_y
        curve2_x,curve2_y,curve2_r, \
            rotate2_deg,angle2_deg, \
            tilt2_deg = calc_curve(y0,y1,line_polyfit_const)

        # 中央線までの距離を計算する
        # 最も下の位置で計算する
        bottom_y = np.max(plot_ym)
        bottom_x = line_polyfit_const[0]*bottom_y**2 + line_polyfit_const[1]*bottom_y + line_polyfit_const[2]
        meters_from_center = bottom_x - (self.cols/2)*self.xm_per_pix

        return tilt1_deg,tilt2_deg,angle1_deg,angle2_deg,curve1_r,curve2_r,meters_from_center
