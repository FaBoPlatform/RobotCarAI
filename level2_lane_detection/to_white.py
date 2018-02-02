# coding: utf-8
# 白色パラメータを確認する
#%matplotlib inline
import cv2
from matplotlib import pyplot as plt
import numpy as np
import time
import os
import sys
import math
from lib import *

def main():
    FILE_DIR = './test_images'
    FILENAME = "frame_325_ipm"
    OUTPUT_DIR ='./output'
    mkdir(OUTPUT_DIR)
    print("OpenCV Version : %s " % cv2.__version__)
    lineType = None
    cv_version = cv2.__version__.split(".")
    if cv_version[0] == '2':
        lineType=cv2.CV_AA
    else:
        # OpenCV 3.1
        lineType=cv2.LINE_AA
    try:
        IMAGE_FORMAT = 1
        cv_bgr = cv2.imread(os.path.join(FILE_DIR, FILENAME+".jpg"), IMAGE_FORMAT)

        cv_rgb = to_rgb(cv_bgr)
        plt.title('Original RGB')
        plt.imshow(cv_rgb)
        plt.show()

        cv_bgr = to_white(cv_bgr)
        plt.title('to_white')
        plt.imshow(to_rgb(cv_bgr))
        plt.show()
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_white.jpg",cv_bgr)

        ########################################
        # 画像を2値化する
        ########################################
        cv_bin = to_bin(cv_bgr)
        cv_rgb_bin = bin_to_rgb(cv_bin)        
        plt.title('to_bin')
        plt.imshow(cv_rgb_bin)
        plt.show()
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_bin.jpg",to_bgr(cv_rgb_bin))

        rows, cols = cv_bin.shape[:2]
        # 画面下半分のピクセル数をカウントする
        histogram = np.sum(cv_bin[int(rows/2):,:], axis=0)
        plt.title('HISTOGRAM')
        plt.plot(histogram)
        plt.show()
        ########################################
        # ヒストグラム画像を作成する
        ########################################
        cv_rgb_histogram = draw_histogram(cols,rows,histogram,lineType)
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_histogram.jpg",to_bgr(cv_rgb_histogram))

    except:
        import traceback
        traceback.print_exc()
    finally:
        pass
    return


if __name__ == '__main__':
    main()
