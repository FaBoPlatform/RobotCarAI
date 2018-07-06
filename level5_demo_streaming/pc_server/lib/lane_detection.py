import cv2
import numpy as np
from lib.functions import *

lineType=cv2.LINE_AA
MAX_HANDLE_ANGLE = 42

def lane_detection(cv_bgr, cv_bgr_detection, x_meter, y_meter, cols, rows):

    is_pass = False
    tilt1_deg = None
    tilt2_deg = None
    angle1_deg = None
    angle2_deg = None
    curve1_r = None
    curve2_r = None
    meters_from_center = None

    
    ########################################
    # Region Of Interest Coordinates
    ########################################
    roi_vertices = calc_roi_vertices(cv_bgr,
                                     # robocar camera demo_lane
                                     top_width_rate=0.80,top_height_position=0.65,
                                     bottom_width_rate=2.0,bottom_height_position=1)

    ########################################
    # Inverse Perspective Mapping Coordinates
    ########################################
    ipm_vertices = calc_ipm_vertices(cv_bgr,
                                     # robocar camera demo_lane
                                     top_width_rate=0.80,top_height_position=0.65,
                                     bottom_width_rate=2.0,bottom_height_position=1)

    ########################################
    # Region Of Interest
    ########################################
    cv_bgr = to_roi(cv_bgr,roi_vertices)
    ########################################
    # Inverse Perspective Mapping
    ########################################
    cv_bgr = to_ipm(cv_bgr,ipm_vertices)
    ########################################
    # 白色抽出
    ########################################
    cv_bgr = to_white(cv_bgr)
    cv_bgr_white = cv_bgr


    ########################################
    # 画像を2値化する
    ########################################
    cv_bin = to_bin(cv_bgr)
    cv_rgb_bin = bin_to_rgb(cv_bin)
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
        # sliding windowsを行い、ラインを構成するピクセル座標を求める
        cv_rgb_sliding_windows, histogram, line_x, line_y = sliding_windows(cv_bin)
        is_sliding_window_success = True

        '''
        描画値 ピクセル座標系における計算
        '''
        # 等間隔なy座標を生成する
        plot_y = np.linspace(0, rows-1, rows)

        # 左右センターの二次多項式と座標を求める
        line_polyfit_const, pts_line = calc_line_curve(line_x,line_y,plot_y)
        is_pixel_pts_success = True

        # 弧と傾きを描画する
        cv_rgb_ellipse, cv_rgb_tilt \
            = draw_ellipse_and_tilt(cols,rows,plot_y,pts_line,line_polyfit_const)

        # 白線画像にレーンを描画する
        cv2.polylines(cv_rgb_bin,[pts_line],False,(255,0,0))
        # 白線道路領域をIPM逆変換する
        cv_rgb_bin = reverse_ipm(cv_rgb_bin,ipm_vertices)

        # 道路にラインを描画する
        cv_rgb_road = new_rgb(rows,cols)
        cv2.polylines(cv_rgb_road,[pts_line],False,(255,0,0))
        # 道路をIPM変換する
        cv_rgb_road = reverse_ipm(cv_rgb_road,ipm_vertices)

        '''
        実測値 メートル座標系における計算
        '''
        # ピクセルをメートルに変換
        ym_per_pix = 1.0*y_meter/rows
        xm_per_pix = 1.0*x_meter/cols
        # 等間隔なy座標を生成する
        plot_ym = np.linspace(0, rows-1, rows)*ym_per_pix
        # ラインの二次多項式と座標を求める
        line_polyfit_const, \
            _pts_line = calc_line_curve(line_x*xm_per_pix,line_y*ym_per_pix,plot_ym)
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
            tilt1_deg = calc_curve(y0,y1,line_polyfit_const)
        # 上半分を計算する
        quarter_y = (np.max(plot_ym) - np.min(plot_ym))/4
        y0 = np.min(plot_ym)
        y1 = np.max(plot_ym) - 2*quarter_y
        curve2_x,curve2_y,curve2_r, \
            rotate2_deg,angle2_deg, \
            tilt2_deg = calc_curve(y0,y1,line_polyfit_const)
        is_meter_ellipse_success = True

        # 中央線までの距離を計算する
        # 最も下の位置で計算する
        bottom_y = np.max(plot_ym)
        bottom_x = line_polyfit_const[0]*bottom_y**2 + line_polyfit_const[1]*bottom_y + line_polyfit_const[2]
        meters_from_center = bottom_x - (cols/2)*xm_per_pix

        is_pass = True
    except:
        #import traceback
        #traceback.print_exc()
        pass
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
        # 道路標識結果に道路を重ねる
        cv_rgb = to_layer(to_rgb(cv_bgr_detection),cv_rgb_road,overlay_alpha=0.5)
    else:
        cv_rgb = to_rgb(cv_bgr_detection)

    # 道路をリサイズする
    cv_rgb_row1 = cv2.resize(cv_rgb, (cols*3,rows*3), interpolation = cv2.INTER_LINEAR)


    if is_pass:
        '''
        左右について
        tiltx_deg: -が右、+が左
        anglex_deg: +が右、-が左
        meters_from_center: -が右にいる、+が左にいる
        handle_angle: +が右、-が左
        '''
        ########################################
        # row1に文字を書く
        ########################################
        tx=10
        ty=40
        strings = []
        colors = []
        if is_meter_ellipse_success:
            strings = []
            colors = []
            strings += ["Far"]
            colors += [(0,255,255)]
            if tilt2_deg < 0:
                strings += ["tilt2:"+str(round(tilt2_deg,2))+"deg right"]
                colors += [(0,255,255)]
            else:
                strings += ["tilt2:"+str(round(tilt2_deg,2))+"deg left"]
                colors += [(0,255,255)]
    
            if angle2_deg < 0:
                strings += ["angle2:"+str(round(angle2_deg,2))+"deg left"]
                colors += [(0,255,255)]
            else:
                strings += ["angle2:"+str(round(angle2_deg,2))+"deg right"]
                colors += [(0,255,255)]
            strings += ["r2:"+str(round(curve2_r,2))+"m"]
            colors += [(0,255,255)]
    
            strings += ["Near"]
            colors += [(255,0,0)]
            if tilt1_deg < 0:
                strings += ["tilt1:"+str(round(tilt1_deg,2))+"deg right"]
                colors += [(255,0,0)]
            else:
                strings += ["tilt1:"+str(round(tilt1_deg,2))+"deg left"]
                colors += [(255,0,0)]
    
            if angle1_deg < 0:
                strings += ["angle1:"+str(round(angle1_deg,2))+"deg left"]
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
                strings +=["center:"+str(round(meters_from_center*100,2))+"cm left"]
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
                    # とても離れて左にいる：
                    if tilt2_deg > 0:
                        # 先は左に曲がる：少し左に曲がる
                        handle_angle = -1*MAX_HANDLE_ANGLE/2
                    else:
                        # 先は右に曲がる：右に全開で曲がる
                        handle_angle = 1*MAX_HANDLE_ANGLE
                elif np.abs(meters_from_center)*100 > 10:
                    if tilt2_deg > 0 :
                        # 離れて左いる、奥は左カーブ：右に少し曲がる
                        handle_angle=MAX_HANDLE_ANGLE/2
                    else:
                        # 離れて左いる、奥は右カーブ：右に全開で曲がる
                        handle_angle=MAX_HANDLE_ANGLE
            else:
                # 右にいる
                if np.abs(meters_from_center)*100 > 20:
                    # とても離れて右にいる
                    if tilt2_deg < 0:
                        # 先は右に曲がる：少し右に曲がる
                        handle_angle = 1*MAX_HANDLE_ANGLE/2
                    else:
                        # 先は左に曲がる：左に全開で曲がる
                        handle_angle = -1*MAX_HANDLE_ANGLE
                elif np.abs(meters_from_center)*100 > 10:
                    if tilt2_deg < 0 :
                        # 離れて右いる、奥は右カーブ：左に少し曲がる
                        handle_angle=-1*MAX_HANDLE_ANGLE/2
                    else:
                        # 離れて右いる、奥は左カーブ、左に全開で曲がる
                        handle_angle=-1*MAX_HANDLE_ANGLE
    
            # 動作可能な角度内に調整する
            if handle_angle > MAX_HANDLE_ANGLE:
                handle_angle = MAX_HANDLE_ANGLE
            elif handle_angle <  -1*MAX_HANDLE_ANGLE:
                handle_angle = -1*MAX_HANDLE_ANGLE
            ratio = 10*np.abs(handle_angle)/100

            if np.abs(handle_angle) <= 5:
                arrow_type = 2
                arrow_color=(0,255-(255*ratio),0)
                arrow_text_color=(0,255,0)
                strings = [str(round(handle_angle,2))+"deg"]
                arrow_text_color=(0,255,0)
            elif handle_angle > 5:
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
            if np.abs(tilt2_deg) > np.abs(tilt1_deg) and np.abs(tilt2_deg) >= 15.0:
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
                strings += ["tilt2:"+str(round(tilt2_deg,2))+"deg right"]
                colors += [(0,255,255)]
            else:
                strings += ["tilt2:"+str(round(tilt2_deg,2))+"deg left"]
                colors += [(0,255,255)]
    
            strings += ["Near"]
            colors += [(255,0,0)]
            if tilt1_deg < 0:
                strings += ["tilt1:"+str(round(tilt1_deg,2))+"deg right"]
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
                strings += ["angle2:"+str(round(angle2_deg,2))+"deg left"]
                colors += [(0,200,200)]
            else:
                strings += ["angle2:"+str(round(angle2_deg,2))+"deg right"]
                colors += [(0,200,200)]
            strings += ["r2:"+str(round(curve2_r,2))+"m"]
            colors += [(0,200,200)]
            # Near
            if angle1_deg < 0:
                strings += ["angle1:"+str(round(angle1_deg,2))+"deg left"]
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


    return is_pass, to_bgr(cv_rgb_debug), tilt1_deg,tilt2_deg,angle1_deg,angle2_deg,curve1_r,curve2_r, \
        meters_from_center
