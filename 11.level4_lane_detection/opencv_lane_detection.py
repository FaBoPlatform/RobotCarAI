# coding: utf-8
# OpenCV レーン検出
# 参考：https://github.com/BillZito/lane-detection
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
    np.set_printoptions(precision=5, suppress=True)  # suppress scientific float notation

    FILE_DIR = './demo_lane'
    FILENAME = 'input1.mp4'
    OUTPUT_DIR ='./output'
    OUTPUT_FILENAME = 'result_output1.avi'
    HANDLE_ANGLE = 42
    # 描画、画像保存するフレーム番号
    TARGET_FRAME = -1
    # IPM変換後の画像におけるx,yメートル(黒い部分も含む)
    X_METER=3
    Y_METER=1.5
    mkdir(OUTPUT_DIR)
    print("OpenCV Version : %s " % cv2.__version__)
    print(FILE_DIR)
    '''
    OpenCVカメラ準備
    '''
    print("camera check")
    import platform
    vid = None
    if platform.machine() == 'aarch64':
        #vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
        vid = cv2.VideoCapture(os.path.join(FILE_DIR, FILENAME))
    elif platform.machine() == 'armv7l': # armv7l
        #vid = cv2.VideoCapture(0) # WebCam Raspberry Pi3 /dev/video0
        vid = cv2.VideoCapture(os.path.join(FILE_DIR, FILENAME))
    else: # amd64
        #vid = cv2.VideoCapture(0) # WebCam
        #vid = cv2.VideoCapture('udp://0084121c9205:8090') # GPU docker container id
        vid = cv2.VideoCapture(os.path.join(FILE_DIR, FILENAME))

    print(vid.isOpened())
    if not vid.isOpened():
        # カメラオープン失敗
        raise IOError(("Couldn't open video file or webcam. If you're "
                       "trying to open a webcam, make sure you video_path is an integer!"))

    vidw = None
    vidh = None
    fps = None
    fourcc = None
    lineType = None
    cv_version = cv2.__version__.split(".")
    if cv_version[0] == '2':
        # OpenCV 2.4
        vidw = vid.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        vidh = vid.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
        fps = vid.get(cv2.cv.CV_CAP_PROP_FPS)
        fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
        lineType=cv2.CV_AA
    else:
        # OpenCV 3.1
        vidw = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        vidh = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = vid.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        lineType=cv2.LINE_AA

    print("vidw:{} vidh:{}".format(vidw,vidh))
    out = cv2.VideoWriter(os.path.join(OUTPUT_DIR, OUTPUT_FILENAME), int(fourcc), fps, (int(vidw)*3, int(vidh)*5))

    frame_count = 0
    start_time,clock_time = time.time(),time.clock()

    try:
        while True:
            # カメラ画像を取得する
            retval, cv_bgr = vid.read()
            if not retval:
                flag_read_frame = False
                print("FPS:{} ".format(frame_count/(time.time() - start_time)))
                print("frame {} Done!".format(frame_count))
                break
            frame_count+=1
            #if not frame_count == TARGET_FRAME:
            #    continue

            print("frame_count = {}".format(frame_count))
            rows, cols = cv_bgr.shape[:2]
            print(cv_bgr.shape)

            frame_start_time = time.time()
            ########################################
            # RGBに変換する
            ########################################
            cv_rgb = to_rgb(cv_bgr)
            if frame_count == TARGET_FRAME:
                plt.title('Original RGB')
                plt.imshow(cv_rgb)
                plt.show()
                cv2.imwrite(OUTPUT_DIR+"/frame_"+str(frame_count)+".jpg",cv_bgr)

            ########################################
            # Region Of Interest Coordinates
            ########################################
            roi_vertices = calc_roi_vertices(cv_bgr,
                                             # robocar camera demo_lane
                                             top_width_rate=0.9,top_height_position=0.15,
                                             bottom_width_rate=2.0,bottom_height_position=1)

            ########################################
            # Inverse Perspective Mapping Coordinates
            ########################################
            ipm_vertices = calc_ipm_vertices(cv_bgr,
                                             # robocar camera demo_lane
                                             top_width_rate=0.9,top_height_position=0.15,
                                             bottom_width_rate=2.0,bottom_height_position=1)

            ########################################
            # Region Of Interest
            ########################################
            cv_bgr = to_roi(cv_bgr,roi_vertices)
            if frame_count == TARGET_FRAME:
                plt.title('After ROI')
                plt.imshow(to_rgb(cv_bgr))
                plt.show()
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_after_roi.jpg",cv_bgr)

            ########################################
            # IPM座標を確認する
            ########################################
            if frame_count == TARGET_FRAME:
                cv_bgr_ipm_before_preview = draw_vertices(cv_bgr,ipm_vertices)
                plt.title('Before IPM')
                plt.imshow(to_rgb(cv_bgr_ipm_before_preview))
                plt.show()
                cv_bgr_ipm_after_preview = to_ipm(cv_bgr_ipm_before_preview,ipm_vertices)
                plt.title('After IPM')
                plt.imshow(to_rgb(cv_bgr_ipm_after_preview))
                plt.show()
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_before_ipm.jpg",cv_bgr_ipm_before_preview)
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_after_ipm.jpg",cv_bgr_ipm_after_preview)

            ########################################
            # Inverse Perspective Mapping
            ########################################
            cv_bgr = to_ipm(cv_bgr,ipm_vertices)
            if frame_count == TARGET_FRAME:
                plt.title('IPM')
                plt.imshow(to_rgb(cv_bgr))
                plt.show()
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_ipm.jpg",cv_bgr)

            ########################################
            # 白色抽出
            ########################################
            cv_bgr = to_white(cv_bgr)
            if frame_count == TARGET_FRAME:
                plt.title('WHITE')
                plt.imshow(to_rgb(cv_bgr))
                plt.show()
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_white.jpg",cv_bgr)
            cv_bgr_white = cv_bgr


            ########################################
            # 画像を2値化する
            ########################################
            cv_bin = to_bin(cv_bgr)
            cv_rgb_bin = bin_to_rgb(cv_bin)
            if frame_count == TARGET_FRAME:
                plt.title('BIN')
                plt.imshow(cv_rgb_bin)
                plt.show()
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_bin.jpg",cv_rgb_bin)


            cv_rgb_road = None
            cv_rgb_sliding_windows = None
            cv_rgb_ellipse = None
            cv_rgb_tilt = None
            histogram = None
            meters_from_center = None
            is_sliding_window_success = False
            is_pixel_pts_success = False
            is_pixel_ellipse_success = False
            is_meter_pts_success = False
            is_meter_ellipse_success = False

            ########################################
            # レーンを検出する
            ########################################
            try:
                # sliding windowsを行い、左右レーンを構成するピクセル座標を求める
                cv_rgb_sliding_windows, histogram, left_x, left_y, right_x, right_y = sliding_windows(cv_bin)
                is_sliding_window_success = True

                '''
                描画値 ピクセル座標系における計算
                '''
                # 等間隔なy座標を生成する
                plot_y = np.linspace(0, rows-1, rows)

                # 左右センターの二次多項式と座標を求める
                left_polyfit_const, right_polyfit_const, center_polyfit_const, \
                    pts_left, pts_right, pts_center = calc_lr_curve_lane(left_x,left_y,right_x,right_y,plot_y)
                is_pixel_pts_success = True

                # 弧と傾きを描画する
                cv_rgb_ellipse,cv_rgb_tilt \
                    = draw_ellipse_and_tilt(cols,rows,plot_y,pts_left,pts_right,pts_center,center_polyfit_const)

                # 道路領域を描画する
                cv_rgb_road = draw_road_area(cols,rows,pts_left,pts_right)

                # 白線画像に道路領域を重ねる
                cv_rgb_bin = to_layer(cv_rgb_bin,cv_rgb_road,overlay_alpha=0.75)
                # 白線画像にレーンを描画する
                cv2.polylines(cv_rgb_bin,[pts_left],False,(255,0,255))
                cv2.polylines(cv_rgb_bin,[pts_right],False,(255,0,255))
                cv2.polylines(cv_rgb_bin,[pts_center],False,(0,0,255))
                if frame_count == TARGET_FRAME:
                    cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_bin_road.jpg",to_bgr(cv_rgb_bin))
                # 白線道路領域をIPM逆変換する
                cv_rgb_bin = reverse_ipm(cv_rgb_bin,ipm_vertices)

                # 道路領域にレーンを描画する
                cv2.polylines(cv_rgb_road,[pts_left],False,(255,0,255))
                cv2.polylines(cv_rgb_road,[pts_right],False,(255,0,255))
                cv2.polylines(cv_rgb_road,[pts_center],False,(0,0,255))
                # 道路領域をIPM変換する
                cv_rgb_road = reverse_ipm(cv_rgb_road,ipm_vertices)

                ''''
                実測値 メートル座標系における計算
                '''
                # ピクセルをメートルに変換
                ym_per_pix = 1.0*Y_METER/rows
                xm_per_pix = 1.0*X_METER/cols
                # 等間隔なy座標を生成する
                plot_ym = np.linspace(0, rows-1, rows)*ym_per_pix
                # 左右センターの二次多項式と座標を求める
                left_polyfit_const, right_polyfit_const, center_polyfit_const, \
                    _pts_left, _pts_right, _pts_center = calc_lr_curve_lane(left_x*xm_per_pix,left_y*ym_per_pix,right_x*xm_per_pix,right_y*ym_per_pix,plot_ym)
                is_meter_pts_success = True
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
                    tilt1_deg = calc_curve(y0,y1,center_polyfit_const)
                # 上半分を計算する
                quarter_y = (np.max(plot_ym) - np.min(plot_ym))/4
                y0 = np.min(plot_ym)
                y1 = np.max(plot_ym) - 2*quarter_y
                curve2_x,curve2_y,curve2_r, \
                    rotate2_deg,angle2_deg, \
                    tilt2_deg = calc_curve(y0,y1,center_polyfit_const)
                is_meter_ellipse_success = True

                # 中央線までの距離を計算する
                # 最も下の位置で計算する
                bottom_y = np.max(plot_ym)
                bottom_x = center_polyfit_const[0]*bottom_y**2 + center_polyfit_const[1]*bottom_y + center_polyfit_const[2]
                meters_from_center = bottom_x - (cols/2)*xm_per_pix

            except:
                import traceback
                traceback.print_exc()
            finally:
                '''
                レーンを検出出来なかった時は、検出画像に空の画像を用意する
                '''
                # エラー時、もしくは描画用処理をスキップした時
                if cv_rgb_sliding_windows is None:
                    cv_rgb_sliding_windows = new_rgb(rows,cols)
                if histogram is None:
                    histogram = np.sum(cv_bin[int(rows/2):,:], axis=0)
                if cv_rgb_bin is None:
                    cv_rgb_bin = bin_to_rgb(cv_bin)
                if cv_rgb_ellipse is None:
                    cv_rgb_ellipse = new_rgb(rows,cols)
                if cv_rgb_tilt is None:
                    cv_rgb_tilt = new_rgb(rows,cols)
                pass

            frame_end_time = time.time()

            ########################################
            # ヒストグラム画像を作成する
            ########################################
            cv_rgb_histogram = draw_histogram(cols,rows,histogram,lineType)

            ########################################
            # 見た目画像を作成する
            ########################################
            if cv_rgb_road is not None:
                # カメラ画像に道路領域画像を重ねる
                cv_rgb = to_layer(cv_rgb,cv_rgb_road,overlay_alpha=0.5)

            # 道路領域をリサイズする
            cv_rgb_row1 = cv2.resize(cv_rgb, (cols*3,rows*3), interpolation = cv2.INTER_LINEAR)

            ########################################
            # row1に文字を書く
            ########################################
            tx=10
            ty=20
            strings = []
            colors = []
            strings += ["FPS:"+str(round(1/(frame_end_time-frame_start_time),2))]
            colors += [(255,255,255)]
            strings += ["FRAME:"+str(frame_count)]
            colors += [(255,255,255)]
            ty = draw_text(cv_rgb_row1,strings,colors,tx=tx,ty=ty)
            if is_meter_ellipse_success:
                strings = []
                colors = []
                strings += ["Far"]
                colors += [(0,255,255)]
                if tilt2_deg < 0:
                    strings += ["tilt2:"+str(round(-1*tilt2_deg,2))+"deg right"]
                    colors += [(0,255,255)]
                else:
                    strings += ["tilt2:"+str(round(tilt2_deg,2))+"deg left"]
                    colors += [(0,255,255)]

                if angle2_deg < 0:
                    strings += ["angle2:"+str(round(-1*angle2_deg,2))+"deg left"]
                    colors += [(0,255,255)]
                else:
                    strings += ["angle2:"+str(round(angle2_deg,2))+"deg right"]
                    colors += [(0,255,255)]
                strings += ["r2:"+str(round(curve2_r,2))+"m"]
                colors += [(0,255,255)]

                strings += ["Near"]
                colors += [(255,0,0)]
                if tilt1_deg < 0:
                    strings += ["tilt1:"+str(round(-1*tilt1_deg,2))+"deg right"]
                    colors += [(255,0,0)]
                else:
                    strings += ["tilt1:"+str(round(tilt1_deg,2))+"deg left"]
                    colors += [(255,0,0)]

                if angle1_deg < 0:
                    strings += ["angle1:"+str(round(-1*angle1_deg,2))+"deg left"]
                    colors += [(255,0,0)]
                else:
                    strings += ["angle1:"+str(round(angle1_deg,2))+"deg right"]
                    colors += [(255,0,0)]
                strings += ["r1:"+str(round(curve1_r,2))+"m"]
                colors += [(255,0,0)]

                ty = draw_text(cv_rgb_row1,strings,colors,tx=tx,ty=ty)

            strings = []
            colors = []
            ty += 20
            if meters_from_center is not None:
                if meters_from_center >= 0:
                    strings += ["center:"+str(round(meters_from_center*100,2))+"cm right"]
                    colors += [(0,255,0)]
                else:
                    strings +=["center:"+str(round(-1*meters_from_center*100,2))+"cm left"]
                    colors += [(0,0,255)]
                ty = draw_text(cv_rgb_row1,strings,colors,tx=tx,ty=ty)

                ####################
                # cv_rgb_row1に矢印を描く
                ####################
                arrow_x = int(cv_rgb_row1.shape[1]/2-35)
                arrow_y = int(cv_rgb_row1.shape[0]/2-35)
                handle_angle = -1*tilt1_deg
                strings = [str(round(handle_angle,2))+"deg"]
                if meters_from_center >= 0:
                    # 左にいる
                    if np.abs(meters_from_center)*100 > 20:
                        # とても離れて左にいる：右に全開で曲がる
                        handle_angle=HANDLE_ANGLE
                    elif np.abs(meters_from_center)*100 > 10:
                        if tilt2_deg > 0 :
                            # 離れて左いる、奥は左カーブ：右に少し曲がる
                            handle_angle=HANDLE_ANGLE/2
                        else:
                            # 離れて左いる、奥は右カーブ：右に全開で曲がる
                            handle_angle=HANDLE_ANGLE
                else:
                    # 右にいる
                    if np.abs(meters_from_center)*100 > 20:
                        # とても離れて右にいる：左に全開で曲がる
                        handle_angle=-1*HANDLE_ANGLE
                    elif np.abs(meters_from_center)*100 > 10:
                        if tilt2_deg < 0 :
                            # 離れて右いる、奥は右カーブ：左に少し曲がる
                            handle_angle=-1*HANDLE_ANGLE/2
                        else:
                            # 離れて右いる、奥は左カーブ、左に全開で曲がる
                            handle_angle=-1*HANDLE_ANGLE

                # 動作可能な角度内に調整する
                if handle_angle > HANDLE_ANGLE:
                    handle_angle = HANDLE_ANGLE
                elif handle_angle <  -1*HANDLE_ANGLE:
                    handle_angle = -1*HANDLE_ANGLE
                ratio = 10*np.abs(handle_angle)/100

                if handle_angle > 0:
                    arrow_type = 1
                    arrow_color=(255-(255*ratio),255-(255*ratio),255)
                    arrow_text_color=(0,0,255)
                    strings = [str(round(handle_angle,2))+"deg"]
                    arrow_text_color=(0,0,255)
                else:
                    arrow_type = 3
                    arrow_color=(255,255-(255*ratio),255-(255*ratio))
                    arrow_text_color=(255,0,0)
                    strings = [str(round(handle_angle,2))+"deg"]
                    arrow_text_color=(255,0,0)

                draw_arrow(cv_rgb_row1,arrow_x,arrow_y,arrow_color,size=2,arrow_type=arrow_type,lineType=lineType)
                
                colors = [arrow_text_color]
                draw_text(cv_rgb_row1,strings,colors,arrow_x,arrow_y-10)
                ####################
                # 奥のカーブ角度が大きい時、slow downを表示する
                ####################
                if np.abs(angle2_deg) > np.abs(angle1_deg):
                    strings = ["slow down"]
                    colors = [(0,0,255)]
                    draw_text(cv_rgb_row1,strings,colors,arrow_x,arrow_y-30)

            ########################################
            # cv_bgr_white に文字を描く
            ########################################
            strings = ["white filter"]
            colors = [(255,255,255)]
            draw_text(cv_bgr_white,strings,colors)

            ########################################
            # histogram に文字を描く
            ########################################
            strings = ["histogram"]
            colors = [(255,255,255)]
            draw_text(cv_rgb_histogram,strings,colors)

            ########################################
            # sliding windows に文字を描く
            ########################################
            strings = ["sliding windows"]
            colors = [(255,255,255)]
            draw_text(cv_rgb_sliding_windows,strings,colors)

            ########################################
            # cv_rgb_bin に文字を描く
            ########################################
            strings = ["road"]
            colors = [(255,255,255)]
            draw_text(cv_rgb_bin,strings,colors)

            ########################################
            # tilt に文字を描く
            ########################################
            strings = ["tilts"]
            colors = [(255,255,255)]
            if is_meter_ellipse_success:
                strings += ["Far"]
                colors += [(0,255,255)]
                if tilt2_deg < 0:
                    strings += ["tilt2:"+str(round(-1*tilt2_deg,2))+"deg right"]
                    colors += [(0,255,255)]
                else:
                    strings += ["tilt2:"+str(round(tilt2_deg,2))+"deg left"]
                    colors += [(0,255,255)]

                strings += ["Near"]
                colors += [(255,0,0)]
                if tilt1_deg < 0:
                    strings += ["tilt1:"+str(round(-1*tilt1_deg,2))+"deg right"]
                    colors += [(255,0,0)]
                else:
                    strings += ["tilt1:"+str(round(tilt1_deg,2))+"deg left"]
                    colors += [(255,0,0)]
                draw_text(cv_rgb_tilt,strings,colors)

            ########################################
            # curve に文字を描く
            ########################################
            strings = ["curve"]
            colors = [(255,255,255)]
            if is_meter_ellipse_success:
                # Far
                if angle2_deg < 0:
                    strings += ["angle2:"+str(round(-1*angle2_deg,2))+"deg left"]
                    colors += [(0,200,200)]
                else:
                    strings += ["angle2:"+str(round(angle2_deg,2))+"deg right"]
                    colors += [(0,200,200)]
                strings += ["r2:"+str(round(curve2_r,2))+"m"]
                colors += [(0,200,200)]
                # Near
                if angle1_deg < 0:
                    strings += ["angle1:"+str(round(-1*angle1_deg,2))+"deg left"]
                    colors += [(200,0,0)]
                else:
                    strings += ["angle1:"+str(round(angle1_deg,2))+"deg right"]
                    colors += [(200,0,0)]
                strings += ["r1:"+str(round(curve1_r,2))+"m"]
                colors += [(200,0,0)]
            draw_text(cv_rgb_ellipse,strings,colors)

            # 画像を結合する
            cv_rgb_row2 = to_rgb(cv_bgr_white)
            cv_rgb_row2 = cv2.hconcat([cv_rgb_row2,cv_rgb_sliding_windows])
            cv_rgb_row2 = cv2.hconcat([cv_rgb_row2,cv_rgb_tilt])
            cv_rgb_row3 = cv_rgb_histogram
            cv_rgb_row3 = cv2.hconcat([cv_rgb_row3,cv_rgb_bin])
            cv_rgb_row3 = cv2.hconcat([cv_rgb_row3,cv_rgb_ellipse])
            cv_rgb_debug = cv2.vconcat([cv_rgb_row2,cv_rgb_row3])
            cv_rgb_debug = cv2.vconcat([cv_rgb_row1,cv_rgb_debug])


            # avi動画に保存する
            out.write(to_bgr(cv_rgb_debug))

            if frame_count == TARGET_FRAME:
                plt.title('result imgage')
                plt.imshow(cv_rgb_debug)
                plt.show()
                cv_bgr_debug = to_bgr(cv_rgb_debug)
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+".jpg",cv_bgr_debug)
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_ellipse.jpg",to_bgr(cv_rgb_ellipse))
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_tilt.jpg",to_bgr(cv_rgb_tilt))
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_histogram.jpg",to_bgr(cv_rgb_histogram))
                cv2.imwrite(OUTPUT_DIR+"/result_frame_"+str(frame_count)+"_sliding_windows.jpg",to_bgr(cv_rgb_sliding_windows))
            #break
    except:
        import traceback
        traceback.print_exc()
    finally:
        vid.release()
        out.release()
    return

if __name__ == '__main__':
    main()

