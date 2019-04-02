# coding: utf-8
# Region Of Interestを確認する
#%matplotlib inline
import cv2
from matplotlib import pyplot as plt
import numpy as np
import time
import os
import sys
import math
from lib.functions import *

def main():
    FILE_DIR = './test_images'
    FILENAME = "frame_86"
    OUTPUT_DIR ='./output'
    mkdir(OUTPUT_DIR)    
    print("OpenCV Version : %s " % cv2.__version__)
    try:
        IMAGE_FORMAT = 1
        cv_bgr = cv2.imread(os.path.join(FILE_DIR, FILENAME)+".jpg", IMAGE_FORMAT)

        ########################################
        # Region Of Interest Coordinates
        ########################################
        # sample
        #roi_vertices = calc_roi_vertices(cv_bgr,
        #                                 top_width_rate=0.3,top_height_position=0.15,
        #                                 bottom_width_rate=0.8,bottom_height_position=0.9)
        # capture-2
        #roi_vertices = calc_roi_vertices(cv_bgr,
        #                                 top_width_rate=0.45,top_height_position=0.15,
        #                                 bottom_width_rate=4.0,bottom_height_position=1)
        # robocar camera demo_lane
        roi_vertices = calc_roi_vertices(cv_bgr,
                                         top_width_rate=0.9,top_height_position=0.15,
                                         bottom_width_rate=2.0,bottom_height_position=1)

        ########################################
        # ROI座標を確認する
        ########################################
        cv_bgr_roi_before_preview = draw_vertices(cv_bgr,roi_vertices)
        plt.title('Before ROI')
        plt.imshow(to_rgb(cv_bgr_roi_before_preview))
        plt.show()
        cv_bgr_roi_after_preview = to_roi(cv_bgr_roi_before_preview,roi_vertices)
        plt.title('After ROI')
        plt.imshow(to_rgb(cv_bgr_roi_after_preview))
        plt.show()
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_before_roi.jpg",cv_bgr_roi_before_preview)
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_after_roi.jpg",cv_bgr_roi_after_preview)
        ########################################
        # Region Of Interest
        ########################################
        cv_bgr = to_roi(cv_bgr,roi_vertices)
        plt.title('ROI')
        plt.imshow(to_rgb(cv_bgr))
        plt.show()
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_roi.jpg",cv_bgr)
    except:
        import traceback
        traceback.print_exc()
    finally:
        pass
    return

if __name__ == '__main__':
    main()

