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
    print("OpenCV Version : %s " % cv2.__version__)
    filenames = sorted(os.listdir(FILE_DIR))
    #IMAGE_FORMAT is either 1 or 0 or -1
    #1 for loading as RGB image (strips alfa component of RGBA file)
    #0 for loading as grayscale image
    #-1 for loading as is (includes alfa component of RGBA file)
    IMAGE_FORMAT = 1
    try:
        for filename in filenames:
            if not filename.startswith("frame_"):
                continue
            if not filename.endswith("_ipm.jpg"):
                continue
            print(filename)
            cv_bgr = cv2.imread(os.path.join(FILE_DIR, filename), IMAGE_FORMAT)

            cv_rgb = to_rgb(cv_bgr)
            plt.title('Original RGB')
            plt.imshow(cv_rgb)
            plt.show()

            cv_bgr = to_white(cv_bgr)
            plt.title('to_white')
            plt.imshow(to_rgb(cv_bgr))
            plt.show()

            ########################################
            # 画像を2値化する
            ########################################
            cv_bin = to_bin(cv_bgr)
            plt.title('to_bin')
            plt.imshow(bin_to_rgb(cv_bin))
            plt.show()

            rows, cols = cv_bin.shape[:2]
            # 画面下半分のピクセル数をカウントする
            histogram = np.sum(cv_bin[int(rows/2):,:], axis=0)
            plt.title('HISTOGRAM')
            plt.plot(histogram)
            plt.show()

    except:
        import traceback
        traceback.print_exc()
    finally:
        pass
    return


if __name__ == '__main__':
    main()
