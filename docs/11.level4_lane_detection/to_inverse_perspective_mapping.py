# coding: utf-8
# Inverse Perspective Mappingを確認する
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
        # Inverse Perspective Mapping Coordinates
        ########################################
        # sample
        #ipm_vertices = calc_ipm_vertices(cv_bgr,
        #                                 top_width_rate=0.3,top_height_position=0.15,
        #                                 bottom_width_rate=0.8,bottom_height_position=0.9)
        # capture-2
        #ipm_vertices = calc_ipm_vertices(cv_bgr,
        #                                 top_width_rate=0.45,top_height_position=0.15,
        #                                 bottom_width_rate=4.0,bottom_height_position=1)
        # robocar camera demo_lane
        ipm_vertices = calc_ipm_vertices(cv_bgr,
                                         top_width_rate=0.9,top_height_position=0.15,
                                         bottom_width_rate=2.0,bottom_height_position=1)

        ########################################
        # IPM座標を確認する
        ########################################
        cv_bgr_ipm_before_preview = draw_vertices(cv_bgr,ipm_vertices)
        plt.title('Before IPM')
        plt.imshow(to_rgb(cv_bgr_ipm_before_preview))
        plt.show()
        cv_bgr_ipm_after_preview = to_ipm(cv_bgr_ipm_before_preview,ipm_vertices)
        plt.title('After IPM')
        plt.imshow(to_rgb(cv_bgr_ipm_after_preview))
        plt.show()
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_before_ipm.jpg",cv_bgr_ipm_before_preview)
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_after_ipm.jpg",cv_bgr_ipm_after_preview)
        ########################################
        # Inverse Perspective Mapping
        ########################################
        cv_bgr = to_ipm(cv_bgr,ipm_vertices)
        plt.title('IPM')
        plt.imshow(to_rgb(cv_bgr))
        plt.show()
        cv2.imwrite(OUTPUT_DIR+"/result_"+FILENAME+"_ipm.jpg",cv_bgr)
    except:
        import traceback
        traceback.print_exc()
    finally:
        pass
    return

if __name__ == '__main__':
    main()

