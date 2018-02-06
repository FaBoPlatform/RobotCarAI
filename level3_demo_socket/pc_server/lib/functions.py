# coding: utf-8
import os
import cv2
import numpy as np
import math
#import time

def mkdir(PATH):
    '''
    ディレクトリを作成する
    '''
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    return


def new_rgb(height, width):
    '''
    新しいRGB画像を作成する
    args:
        height: 画像の高さ
        width: 画像の幅
    return:
        cv_rgb_blank_image: 新しい画像データ
    '''
    cv_rgb_blank_image = np.zeros((height,width,3), np.uint8)
    return cv_rgb_blank_image


def new_rgba(height, width):
    '''
    新しいRGBA画像を作成する
    args:
        height: 画像の高さ
        width: 画像の幅
    return:
        cv_rgb_blank_image: 新しい画像データ
    '''
    cv_rgb_blank_image = np.zeros((height,width,4), np.uint8)
    return cv_rgb_blank_image


def to_rgb(cv_bgr):
    '''
    RGBに変換する
    args:
        cv_bgr: OpenCV BGR画像データ
    return:
        cv_rgb: OpenCV RGB画像データ
    '''
    #BGRflags = [flag for flag in dir(cv2) if flag.startswith('COLOR_BGR') ]
    #print(BGRflags)

    cv_rgb = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2RGB)
    return cv_rgb


def to_bgr(cv_rgb):
    '''
    BGRに変換する
    args:
        cv_rgb: OpenCV RGB画像データ
    return:
        cv_bgr: OpenCV BGR画像データ
    '''
    cv_bgr = cv2.cvtColor(cv_rgb, cv2.COLOR_RGB2BGR)
    return cv_bgr


def to_white(cv_bgr):
    '''
    白色だけを抽出する
    args:
        cv_bgr: OpenCV BGR画像データ
    return:
        cv_bgr_result: OpenCV BGR画像データ
    '''
    #print("to_white()")
    #t0 = time.time()
    cv_hsv = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2HSV)
    # 取得する色の範囲を指定する
    lower1_color = np.array([0,0,120])
    upper1_color = np.array([45,40,255])
    lower2_color = np.array([50,0,200])
    upper2_color = np.array([100,20,255])
    lower3_color = np.array([45,0,225])
    upper3_color = np.array([100,40,255])

    # 指定した色に基づいたマスク画像の生成
    white1_mask = cv2.inRange(cv_hsv,lower1_color,upper1_color)
    white2_mask = cv2.inRange(cv_hsv,lower2_color,upper2_color)
    white3_mask = cv2.inRange(cv_hsv,lower3_color,upper3_color)
    img_mask = cv2.bitwise_or(white1_mask, white2_mask)
    img_mask = cv2.bitwise_or(img_mask, white3_mask)
    # フレーム画像とマスク画像の共通の領域を抽出する
    cv_bgr_result = cv2.bitwise_and(cv_bgr,cv_bgr,mask=img_mask)
    #t1 = time.time()
    #dt_cv = t1-t0
    #print("Conversion took {:.5} seconds".format(dt_cv))

    return cv_bgr_result


def to_bin(cv_bgr):
    '''
    画像を2値化する
    args:
        cv_bgr: OpenCV BGR画像データ
    return:
        cv_bin: OpenCV 2値化したグレースケール画像データ
    '''
    #print("to_bin()")
    #t0 = time.time()
    # ガウスぼかしで境界線の弱い部分を消す
    cv_gauss = cv2.GaussianBlur(cv_bgr,(5,5),0) # サイズは奇数
    cv_gray = cv2.cvtColor(cv_gauss, cv2.COLOR_BGR2GRAY)
    #plt.title('gray')
    #plt.imshow(cv_gray)
    #plt.show()

    # 色の薄い部分を削除する
    ret, mask = cv2.threshold(cv_gray, 20, 255, cv2.THRESH_BINARY)
    mask = cv2.bitwise_and(cv_gray,cv_gray,mask=mask)
    cv_gray = cv2.bitwise_and(cv_gray,cv_gray,mask=mask)
    #plt.title('gray')
    #plt.imshow(cv_gray)
    #plt.show()

    # 入力画像，閾値，maxVal，閾値処理手法
    ret,cv_bin = cv2.threshold(cv_gray,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU);

    #t1 = time.time()
    #dt_cv = t1-t0
    #print("Conversion took {:.5} seconds".format(dt_cv))
    return cv_bin


def bin_to_rgb(cv_bin):
    '''
    二値化したグレースケール画像をOpenCV RGB画像データに変換する
    args:
        cv_bin: OpenCV grayscale画像データ
    return:
        cv_rgb: OpenCV RGB画像データ
    '''
    cv_rgb = np.dstack((cv_bin, cv_bin, cv_bin))
    return cv_rgb


def to_edge(cv_gray):
    '''
    エッジを求める
    args:
        cv_gray: OpenCVグレースケール画像データ
    return:
        cv_gray_result: エッジのOpenCVグレースケール画像データ
    '''
    #print("to_edge()")
    #t0 = time.time()
    # Canny
    cv_gray_result = cv2.Canny(cv_gray, 50, 200);
    #t1 = time.time()
    #dt_cv = t1-t0
    #print("Conversion took {:.5} seconds".format(dt_cv))
    return cv_gray_result


def to_hough_lines_p(cv_bin):
    '''
    確率的Hough変換で直線を求める
    args:
        cv_bin: OpenCV グレースケール画像データ
    return:
        cv_bin_out: OpenCV グレースケール画像データ
    '''
    #print("確率的Hough変換")
    #t0 = time.time()
    threshold=10
    minLineLength=10
    maxLineGap=10

    _lines = cv2.HoughLinesP(cv_bin,rho=1,theta=1*np.pi/180,threshold=threshold,lines=np.array([]),minLineLength=minLineLength,maxLineGap=maxLineGap)

    cv_bin_result=np.zeros_like(cv_bin)
    if _lines is None:
        #print('There is no lines to be detected!')
        pass
    else:
        a,b,c = _lines.shape
        #print(len(_lines[0]))
        for i in range(a):
            x1 = _lines[i][0][0]
            y1 = _lines[i][0][1]
            x2 = _lines[i][0][2]
            y2 = _lines[i][0][3]
            cv2.line(cv_bin_result,(x1,y1),(x2,y2),(255,255,255),1)

    #t1 = time.time()
    #dt_cv = t1-t0
    #print("Conversion took {:.5} seconds".format(dt_cv))
    return cv_bin_result


def to_layer(cv_bgr_image,cv_bgr_overlay,image_alpha=1.0,overlay_alpha=0.75):
    '''
    2つの画像を重ねる
    args:
        cv_bgr_image: 下になるOpenCV BGR画像データ
        cv_bgr_overlay: 上になるOpenCV BGR画像データ
        image_alpha: 下になる画像のアルファ値
        overlay_alpha: 上になる画像のアルファ値
    return:
        cv_bgr_result: 重ねたOpenCV BGR画像データ
    '''

    cv_bgr_result = cv2.addWeighted(cv_bgr_image, image_alpha, cv_bgr_overlay, overlay_alpha, 0)
    return cv_bgr_result


def to_roi(cv_bgr, vertices):
    """
    Region Of Interest
    頂点座標でmaskを作り、入力画像に適用する
    args:
        cv_bgr: OpenCV BGR画像データ
        vertices: 領域の頂点座標
    return:
        cv_bgr_result: 領域外を黒くしたOpenCV BGR画像データ
    """
    mask = np.zeros_like(cv_bgr)
    if len(mask.shape)==2:
        cv2.fillPoly(mask, vertices, 255)
    else:
        cv2.fillPoly(mask, vertices, (255,)*mask.shape[2]) # in case, the input image has a channel dimension
    return cv2.bitwise_and(cv_bgr, mask)


def to_ipm(cv_bgr,ipm_vertices):
    '''
    Inverse Perspective Mapping
    TopViewに画像を変換する
    args:
        cv_bgr: OpenCV BGR画像データ
        ipm_vertices: 視点変換座標
    return:
        cv_bgr_ipm: 変換後のOpenCV BGR画像データ
    '''
    rows, cols = cv_bgr.shape[:2]

    offset = cols*.25

    src = ipm_vertices
    dst = np.float32([[offset, 0], [cols - offset, 0], [cols - offset, rows], [offset, rows]])

    # srcとdst座標に基づいて変換行列を作成する
    matrix = cv2.getPerspectiveTransform(src, dst)

    # 変換行列から画像をTopViewに変換する
    cv_bgr_ipm = cv2.warpPerspective(cv_bgr, matrix, (cols, rows))

    return cv_bgr_ipm


def calc_roi_vertices(cols,rows,
                      top_width_rate=0.6,top_height_position=0.7,
                      bottom_width_rate=4.0,bottom_height_position=0.95):
    '''
    Region Of Interest 頂点座標計算
    args:
        cols: 画像横サイズ
        rows: 画像縦サイズ
        top_widh_rate: 領域とする上辺幅の画像幅比
        top_height_position: 領域とする上辺位置の画像高さ比 0.0: 画像上、1.0:画像下
        bottom_width_rate: 領域とする底辺幅の画像比
        bottom_height_position: 領域とする底辺位置の画像高さ比 0.0: 画像上、1.0:画像下
    return:
        vertices: 領域の頂点座標配列
    '''
    bottom_width_left_position = (1.0 - bottom_width_rate)/2
    bottom_width_right_position = (1.0 - bottom_width_rate)/2 + bottom_width_rate
    top_width_left_position = (1.0 - top_width_rate)/2
    top_width_right_position = (1.0 - top_width_rate)/2 + top_width_rate

    # Region Of Interest
    bottom_left  = [cols*bottom_width_left_position, rows*bottom_height_position]
    top_left     = [cols*top_width_left_position, rows*top_height_position]
    bottom_right = [cols*bottom_width_right_position, rows*bottom_height_position]
    top_right    = [cols*top_width_right_position, rows*top_height_position]
    # the vertices are an array of polygons (i.e array of arrays) and the data type must be integer
    vertices = np.array([[top_left, top_right, bottom_right, bottom_left]], dtype=np.int32)

    return vertices


def calc_ipm_vertices(cols,rows,
                      top_width_rate=0.6,top_height_position=0.7,
                      bottom_width_rate=4.0,bottom_height_position=0.95):
    '''
    Inverse Perspective Mapping 頂点座標計算
    args:
        cols: 画像横サイズ
        rows: 画像縦サイズ
        top_widh_rate: 変換する上辺幅の画像幅比
        top_height_position: 変換する上辺位置の画像高さ比 0.0: 画像上、1.0:画像下
        bottom_width_rate: 変換する底辺幅の画像比
        bottom_height_position: 変換する底辺位置の画像高さ比 0.0: 画像上、1.0:画像下
    return:
        vertices: 変換する頂点座標配列
    '''
    bottom_width_left_position = (1.0 - bottom_width_rate)/2
    bottom_width_right_position = (1.0 - bottom_width_rate)/2 + bottom_width_rate
    top_width_left_position = (1.0 - top_width_rate)/2
    top_width_right_position = (1.0 - top_width_rate)/2 + top_width_rate

    # Inverse Perspective Mapping
    bottom_left  = [cols*bottom_width_left_position, rows*bottom_height_position]
    top_left     = [cols*top_width_left_position, rows*top_height_position]
    bottom_right = [cols*bottom_width_right_position, rows*bottom_height_position]
    top_right    = [cols*top_width_right_position, rows*top_height_position]

    vertices = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)

    return vertices


def draw_vertices(cv_bgr,vertices):
    '''
    ROIの座標確認のために表示する
    ROI範囲にラインが映っているかを確認するためのもの
    args:
        cv_bgr: 下になるOpenCV BGR画像
        vertices: オーバーレイ表示する頂点座標
    return:
        before_roi: 変換前のオーバーレイ表示画像
        after_roi: 変換後のオーバーレイ表示画像
    '''
    color=(0,255,0)
    image_alpha = 1.0
    overlay_alpha = 0.5
    overlay = new_rgb(cv_bgr.shape[0], cv_bgr.shape[1])
    cv2.fillConvexPoly(overlay, vertices.astype('int32'), color)
    cv_bgr_result = cv2.addWeighted(cv_bgr,image_alpha,overlay,overlay_alpha,0)
    return cv_bgr_result


def histogram_equalization(cv_bgr,grid_size=(8,8)):
    '''
    ヒストグラム平坦化
    args:
        cv_bgr: OpenCV BGR画像データ
        grid_size: 平坦化計算範囲
    return:
        cv_bgr_result: OpenCV BGR画像データ
    '''
    #print("ヒストグラム平坦化")
    #t0 = time.time()
    lab= cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=grid_size)
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    cv_bgr_result = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    #t1 = time.time()
    #dt_cv = t1-t0
    #print("Conversion took {:.5} seconds".format(dt_cv))
    return cv_bgr_result


def draw_arrow(cv_rgb, x, y, color, size=1, arrow_type=1, lineType=1):
    '''
    矢印を描画する
    args:
        cv_rgb: OpenCV RGB画像データ
        x: 左上x座標
        y: 左上y座標
        color: 色
        size: 矢印のサイズ
        arrowTyep: 矢印の上下左右向き。1:右、2:上、3:左、4:下
        lineType: ラインタイプ
    return:
        cv_rgb_arrow: OpenCV RGB画像データ
    '''
    # 矢印の基本座標
    if arrow_type == 1:
        pts_arrow = np.array([[0,10],[20,10],[20,0],[35,15],[20,30],[20,20],[0,20],[0,10]])
    elif arrow_type == 2:
        pts_arrow = np.array([[0,15],[10,15],[10,35],[20,35],[20,15],[30,15],[15,0],[0,15]])
    elif arrow_type == 3:
        pts_arrow = np.array([[35,10],[15,10],[15,0],[0,15],[15,30],[15,20],[35,20],[35,10]])
    elif arrow_type == 4:
        pts_arrow = np.array([[10,0],[10,20],[0,20],[15,35],[30,20],[20,20],[20,0],[10,0]])
    pts_arrow = (pts_arrow * size + [[x,y]]).astype(int)
    # 座標に囲まれた領域を描画
    cv2.fillPoly(cv_rgb, [pts_arrow], color,lineType)
    #cv2.polylines(cv_rgb, [pts_arrow], False, (255,255,255),lineType)

    return

def reverse_ipm(cv_bgr,ipm_vertices):
    '''
    IPM逆変換を行う
    args:
        cv_bgr: OpenCV BGR画像データ
        ipm_vertices: 変換時に使ったIPM座標
    return:
        cv_bgr_ipm_reverse: OpenCV BGR画像データ
    '''
    rows, cols = cv_bgr.shape[:2]

    offset = cols*.25

    dst = ipm_vertices
    src = np.float32([[offset, 0], [cols - offset, 0], [cols - offset, rows], [offset, rows]])

    matrix = cv2.getPerspectiveTransform(src, dst)

    cv_bgr_ipm_reverse = cv2.warpPerspective(cv_bgr, matrix, (cols,rows))
    return cv_bgr_ipm_reverse


def draw_histogram(cols,rows,histogram,lineType):
    '''
    ヒストグラムを描画する
    args:
        cols: 画像縦サイズ
        rows: 画像横サイズ
        histogram: ヒストグラム
        inlineType: 描画ラインタイプ
    returns:
        cv_rgb_histogram: ヒストグラムOpenCV RGB画像データ
    '''
    # ヒストグラムの最大値を画像高さ*0.9の値に変換する
    max_value = np.max(histogram)
    if max_value > 0:
        np.putmask(histogram,histogram>=0,np.uint32(rows - rows*0.9*histogram/max_value))
    # ヒストグラムをx,y座標に変換する
    _x = np.arange(len(histogram))
    pts_histogram = np.transpose(np.vstack([_x, histogram]))
    # ヒストグラムを描画する
    cv_rgb_histogram = new_rgb(rows,len(histogram))
    cv2.polylines(cv_rgb_histogram,[np.int32(pts_histogram)],False,(255, 255, 0),lineType=lineType)
    # ヒストグラム画像をリサイズする
    if cols != len(histogram):
        cv_rgb_histogram = cv2.resize(cv_rgb_histogram, (cols,rows), interpolation = cv2.INTER_LINEAR)
    return cv_rgb_histogram


def draw_ellipse_and_tilt(cols,rows,plot_y,pts_line,line_polyfit_const):
    '''
    弧と傾き角を描画する
    描画値 ピクセル座標系における計算
    args:
        cols: 画像横サイズ
        rows: 画像縦サイズ
        plot_y: Y軸に均等なY座標群
        pts_line: ライン上の座標群
        line_polyfit_const: ラインの曲線式の定数
    returns:
        cv_rgb_ellipse: 弧のOpenCV RGB画像データ
        cv_rgb_tilt: 傾き角のOpenCV RGB画像データ
    '''
    ########################################
    # 弧を描画する
    ########################################
    cv_rgb_ellipse = new_rgb(rows,cols)
    quarter_y = (np.max(plot_y) - np.min(plot_y))/4
    ########################################
    # 下半分の座標と角度を求める
    ########################################
    y0 = np.max(plot_y) - 2*quarter_y
    y1 = np.max(plot_y)
    x,y,r, \
        rotate_deg,angle_deg, \
        tilt_deg = calc_curve(y0,y1,line_polyfit_const)
    '''
    # 弧を描画する
    cv2.ellipse(cv_rgb_ellipse,(int(x),int(y)),(int(r),int(r)),rotate_deg,0,angle_deg,(255,0,0),-1)
    or
    pts_ellipse = np.array(pts_line[:,int(pts_line.shape[1]/2):,:]).astype(int)
    pts_ellipse = np.concatenate((pts_ellipse,np.array([[[x,y]]]).astype(int)),axis=1)
    cv2.fillPoly(cv_rgb_ellipse, [pts_ellipse], (255,0,0))

    cv2.ellipse()は小数点以下の角度が描画範囲に影響を与える時、正しく描画できない
    そのため、ポリゴンで描画する
    '''
    pts_ellipse = np.array(pts_line[:,int(pts_line.shape[1]/2):,:]).astype(int)

    # x,yが画面より非常に遠く離れている時、描画に時間がかかるため、直線の式から画面上の点を取得する
    # 2点(x,y),(x0,y0)を通る直線と、y=0,y=rows,x=0,x=colsの4直線との交点を求める
    if x<0 or x>cols or y<0 or y>rows:
        x0 = line_polyfit_const[0]*y0**2 + line_polyfit_const[1]*y0 + line_polyfit_const[2]
        x1 = line_polyfit_const[0]*y1**2 + line_polyfit_const[1]*y1 + line_polyfit_const[2]
        y0_1 = 0 # y = 0
        x0_1 = calc_line(y,x,y0,x0,y0_1)
        y0_2 = rows # y = rows
        x0_2 = calc_line(y,x,y0,x0,y0_2)
        x0_3 = 0 # x = 0
        y0_3 = calc_line(x,y,x0,y0,x0_3)
        x0_4 = cols # x = cols
        y0_4 = calc_line(x,y,x0,y0,x0_4)

        pts_x0 = [x0_1,x0_2,x0_3,x0_4]
        pts_y0 = [y0_1,y0_2,y0_3,y0_4]

        y1_1 = 0 # y = 0
        x1_1 = calc_line(y,x,y1,x1,y1_1)
        y1_2 = rows # y = rows
        x1_2 = calc_line(y,x,y1,x1,y1_2)
        x1_3 = 0 # x = 0
        y1_3 = calc_line(x,y,x1,y1,x1_3)
        x1_4 = cols # x = cols
        y1_4 = calc_line(x,y,x1,y1,x1_4)

        pts_x1 = [x1_1,x1_2,x1_3,x1_4]
        pts_y1 = [y1_1,y1_2,y1_3,y1_4]

        if x<0 or x>cols:
            for i in range(4):
                if (x<0 and pts_x0[i] == 0) or (x>cols and pts_x0[i] == cols):
                    pts_x0 = pts_x0[i]
                    pts_y0 = pts_y0[i]
                    break
            for i in range(4):
                if (x<0 and pts_x1[i] == 0) or (x>cols and pts_x1[i] == cols):
                    pts_x1 = pts_x1[i]
                    pts_y1 = pts_y1[i]
                    break
        elif y<0 or y>rows:
            for i in range(4):
                if (y<0 and pts_y0[i] == 0) or (y>rows and pts_y0[i] == rows):
                    pts_x0 = pts_x0[i]
                    pts_y0 = pts_y0[i]
                    break
            for i in range(4):
                if (y<0 and pts_y1[i] == 0) or (y>rows and pts_y1[i] == rows):
                    pts_x1 = pts_x1[i]
                    pts_y1 = pts_y1[i]
                    break
        pts_ellipse = np.concatenate((pts_ellipse,np.array([[[pts_x1,pts_y1],[pts_x0,pts_y0]]]).astype(int)),axis=1)
    else:
        pts_ellipse = np.concatenate((pts_ellipse,np.array([[[x,y]]]).astype(int)),axis=1)
    cv2.fillPoly(cv_rgb_ellipse, [pts_ellipse], (255,0,0))
    ########################################
    # 傾きを描画する
    ########################################
    cv_rgb_tilt = new_rgb(rows,cols)
    x0 = line_polyfit_const[0]*y0**2 + line_polyfit_const[1]*y0 + line_polyfit_const[2]
    x1 = line_polyfit_const[0]*y1**2 + line_polyfit_const[1]*y1 + line_polyfit_const[2]
    pts_tilt = np.array([[x0,y0],[x1,y1],[x1,y0]]).astype(int)
    cv2.fillPoly(cv_rgb_tilt,[pts_tilt],(255,0,0))

    ########################################
    # 上半分の座標と角度を求める
    ########################################
    quarter_y = (np.max(plot_y) - np.min(plot_y))/4
    y0 = np.min(plot_y)
    y1 = np.max(plot_y) - 2*quarter_y
    x,y,r, \
        rotate_deg,angle_deg, \
        tilt_deg = calc_curve(y0,y1,line_polyfit_const)
    # 弧を描画する
    #cv2.ellipse(cv_rgb_ellipse,(int(x),int(y)),(int(r),int(r)),rotate_deg,0,angle_deg,(0,255,255),-1)
    pts_ellipse = np.array(pts_line[:,:int(pts_line.shape[1]/2),:]).astype(int)
    # x,yが画面より非常に遠く離れている時、描画に時間がかかるため、直線の式から画面上の点を取得する
    # 2点(x,y),(x0,y0)を通る直線と、y=0,y=rows,x=0,x=colsの4直線との交点を求める
    if x<0 or x>cols or y<0 or y>rows:
        x0 = line_polyfit_const[0]*y0**2 + line_polyfit_const[1]*y0 + line_polyfit_const[2]
        x1 = line_polyfit_const[0]*y1**2 + line_polyfit_const[1]*y1 + line_polyfit_const[2]
        y0_1 = 0 # y = 0
        x0_1 = calc_line(y,x,y0,x0,y0_1)
        y0_2 = rows # y = rows
        x0_2 = calc_line(y,x,y0,x0,y0_2)
        x0_3 = 0 # x = 0
        y0_3 = calc_line(x,y,x0,y0,x0_3)
        x0_4 = cols # x = cols
        y0_4 = calc_line(x,y,x0,y0,x0_4)

        pts_x0 = [x0_1,x0_2,x0_3,x0_4]
        pts_y0 = [y0_1,y0_2,y0_3,y0_4]

        y1_1 = 0 # y = 0
        x1_1 = calc_line(y,x,y1,x1,y1_1)
        y1_2 = rows # y = rows
        x1_2 = calc_line(y,x,y1,x1,y1_2)
        x1_3 = 0 # x = 0
        y1_3 = calc_line(x,y,x1,y1,x1_3)
        x1_4 = cols # x = cols
        y1_4 = calc_line(x,y,x1,y1,x1_4)

        pts_x1 = [x1_1,x1_2,x1_3,x1_4]
        pts_y1 = [y1_1,y1_2,y1_3,y1_4]

        if x<0 or x>cols:
            for i in range(4):
                if (x<0 and pts_x0[i] == 0) or (x>cols and pts_x0[i] == cols):
                    pts_x0 = pts_x0[i]
                    pts_y0 = pts_y0[i]
                    break
            for i in range(4):
                if (x<0 and pts_x1[i] == 0) or (x>cols and pts_x1[i] == cols):
                    pts_x1 = pts_x1[i]
                    pts_y1 = pts_y1[i]
                    break
        elif y<0 or y>rows:
            for i in range(4):
                if (y<0 and pts_y0[i] == 0) or (y>rows and pts_y0[i] == rows):
                    pts_x0 = pts_x0[i]
                    pts_y0 = pts_y0[i]
                    break
            for i in range(4):
                if (y<0 and pts_y1[i] == 0) or (y>rows and pts_y1[i] == rows):
                    pts_x1 = pts_x1[i]
                    pts_y1 = pts_y1[i]
                    break
        #print("{} {} {} {}".format(pts_x0,pts_y0,pts_x1,pts_y1))
        pts_ellipse = np.concatenate((pts_ellipse,np.array([[[pts_x1,pts_y1],[pts_x0,pts_y0]]]).astype(int)),axis=1)
    else:
        pts_ellipse = np.concatenate((pts_ellipse,np.array([[[x,y]]]).astype(int)),axis=1)
    cv2.fillPoly(cv_rgb_ellipse, [pts_ellipse], (0,255,255))
    ########################################
    # 傾きを描画する
    ########################################
    x0 = line_polyfit_const[0]*y0**2 + line_polyfit_const[1]*y0 + line_polyfit_const[2]
    x1 = line_polyfit_const[0]*y1**2 + line_polyfit_const[1]*y1 + line_polyfit_const[2]
    pts_tilt = np.array([[x0,y0],[x1,y1],[x1,y0]]).astype(int)
    cv2.fillPoly(cv_rgb_tilt,[pts_tilt],(0,255,255))

    # 弧にラインを描画する
    cv2.polylines(cv_rgb_ellipse,[pts_line],False,(0,255,255))

    # 傾きにラインを描画する
    cv2.polylines(cv_rgb_tilt,[pts_line],False,(0,255,255))

    return cv_rgb_ellipse,cv_rgb_tilt


def draw_text(cv_rgb,strings,colors,tx=10,ty=20):
    '''
    画面に文字を描く
    args:
        cv_rgb: 描画対象のOpenCV RGB画像データ
        strings: 文字配列
        colors: 色配列
        tx: テキスト描画x座標
        ty: テキスト描画y座標
    return:
        ty: テキスト描画y座標
    '''
    length = len(strings)
    for i in range(length):
        cv2.putText(cv_rgb,
                    strings[i],
                    (tx,ty),
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    colors[i])
        ty += 20
    return ty


def sliding_windows(cv_bin):
    '''
    sliding windowを行い、1本の線を構成するピクセル座標を求める
    args:
        cv_bin: 2値化したライン画像のOpenCV grayscale画像データ
    returns:
        histogram: 入力画像の下半分の列毎のピクセル総数の配列(1,col)
        line_x: ラインを構成するピクセルのx座標群
        line_y: ラインを構成するピクセルのy座標群
    '''

    '''
    画像下半分のピクセル数を列毎にカウントしたものをhistogramとする
    '''
    rows, cols = cv_bin.shape[:2]
    # 画面下半分のピクセル数をカウントする
    histogram = np.sum(cv_bin[int(rows/2):,:], axis=0)

    '''
    sliding windowの開始位置となるx座標を求める
    histogramは画像幅ピクセル数分の配列数としているため、
    histogramの配列index番号が画像のx座標となる
    variables:
        win_line_x: sliding windowの現在のx座標
    '''
    # windowのカレント位置をヒストグラム最大となる位置で初期化する
    win_line_x = np.argmax(histogram)

    # window分割数を決める
    nwindows = int(rows/5)    
    # windowの高さを決める
    window_height = np.int(rows/nwindows)
    # 画像内のすべての非ゼロピクセルのxとyの位置を特定する
    nonzero = cv_bin.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    # window幅のマージン
    margin = int(cols/5)
    # windowをセンタリングするための最小ピクセル数
    minpix = margin/2
    # ラインピクセルindexを持つための配列
    lane_line_idx = []
    # windowの色
    rectangle_color=(0,160,0)

    '''
    sliding windows
    window処理から、ラインとなるピクセルを取得する
    枠が被ってしまう場合、直前の領域の多い方を優先枠範囲に取る
    空枠の時、片方が検出しているなら、そのx軸の移動範囲に追従する
    '''
    for window in range(nwindows):
        # windowの座標を求める
        win_y_low = rows - (window+1)*window_height
        win_y_high = rows - window*window_height
        win_line_x_low = win_line_x - margin
        win_line_x_high = win_line_x + margin

        # ウィンドウ内のxとyの非ゼロピクセルを取得する
        win_line_idx = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_line_x_low) & (nonzerox < win_line_x_high)).nonzero()[0]

        # 枠内画素数をカウントする
        win_num_lines = len(win_line_idx)
        
        # window内ラインピクセルをラインピクセルに追加する
        lane_line_idx.append(win_line_idx)

        # window開始x座標を更新する
        if win_num_lines > minpix:
            last_win_line_x = win_line_x
            win_line_x = np.int(np.mean(nonzerox[win_line_idx]))

    # window毎の配列を結合する
    lane_line_idx = np.concatenate(lane_line_idx)

    # ラインピクセル座標を取得する
    line_x = nonzerox[lane_line_idx]
    line_y = nonzeroy[lane_line_idx]

    return line_x, line_y

def polynormal_fit(pts_y,pts_x):
    '''
    曲線を構成する点から二次多項式を求める
    (y軸の値は均等に取るのでxを求める式となる)
    args:
        pts_x: x座標配列
        pts_y: y座標配列
    returns:
        polyfit_const: 二次曲線x=ay**2+by+cの[a,b,c]の値
    '''
    polyfit_const = np.polyfit(pts_y, pts_x, 2)
    return polyfit_const

def calc_line_curve(line_x,line_y,plot_y):
    '''
    ラインを構成する(ピクセルorメートル)点座標から、曲線と曲線上の座標を求める
    args:
        line_x: ラインを構成する点のx座標群
        line_y: ラインを構成する点のy座標群
        plot_y: 曲線上のy座標群
    returns:
        line_polyfit_const: ライン曲線の定数
        pts_line: ライン曲線上の[x,y]座標群
    '''

    '''
    点座標群からラインの二次多項式を求める
    ラインの二次多項式を求める
    ラインの曲率半径を求める
    ラインの画像下から画像中央までの角度を求める
    '''
    # ラインの二次多項式を求める
    line_polyfit_const = polynormal_fit(line_y,line_x)

    # y軸に対するラインの二次多項式上のx座標を求める
    line_plot_x = line_polyfit_const[0]*plot_y**2 + line_polyfit_const[1]*plot_y + line_polyfit_const[2]

    '''
    x,y座標を[x,y]配列に変換する
    '''
    pts_line = np.int32(np.array([np.transpose(np.vstack([line_plot_x, plot_y]))]))

    #pts_line = pts_line.reshape((-1,1,2))
    return line_polyfit_const, pts_line


def calc_curve(curve_y0,curve_y1,curve_polyfit_const):
    '''
    曲線を計算する
    args:
        curve_y0: 曲線上y座標
        curve_y1: 曲線下y座標
        curve_ployfit_const: 曲線の定数
    returns:
        x: 円の中心x座標
        y: 円の中心y座標
        r: 円の半径r (曲率半径r)
        rotate_deg: 弧の回転角度
        angle_deg: 弧の描画角度
        curve_tilt_deg: y軸との傾き角度
    '''
    # 中間点における曲率半径Rを求める
    curve_y = curve_y1-curve_y0
    curve_r = calc_curvature_radius(curve_polyfit_const,curve_y)

    # x座標を求める
    curve_x0 = curve_polyfit_const[0]*curve_y0**2 + curve_polyfit_const[1]*curve_y0 + curve_polyfit_const[2]
    curve_x1 = curve_polyfit_const[0]*curve_y1**2 + curve_polyfit_const[1]*curve_y1 + curve_polyfit_const[2]

    # 2点と半径と曲線の定数から円の中心座標を求める
    py = curve_y1
    px = curve_x1
    qy = curve_y0
    qx = curve_x0
    r = curve_r
    x,y = calc_circle_center_point(px,py,qx,qy,r,curve_polyfit_const[0])

    # 弧の描画角度を求める
    rotate_deg, angle_deg = calc_ellipse_angle(py,px,qy,qx,r,x,y,curve_polyfit_const[0])
    #print("py={},px={},qy={},qx={},x={},y={},r={}".format(py,px,qy,qx,x,y,r))
    #print("rotate_deg={} angle_deg={}".format(rotate_deg,angle_deg))

    # 垂直方向との傾き角を求める
    # プラスなら左カーブ、マイナスなら右カーブ
    curve_tilt_rad = math.atan((px-qx)/(py-qy))
    curve_tilt_deg = math.degrees(curve_tilt_rad)
    #print("curve_tilt_deg={}".format(curve_tilt_deg))

    return x,y,r,rotate_deg,angle_deg,curve_tilt_deg


def calc_curvature_radius(const,y):
    '''
    二次曲線のy座標における曲率半径Rを求める
    args:
        const: 二次曲線y=ax**2+bx+cの[a,b,c]の値
        y: 二次曲線上の点Pのy座標
    returns:
        r: 曲率半径R
    '''
    r = (1 + (2*const[0]*y + const[1])**2)**1.5/np.abs(2*const[0])
    return r


def calc_circle_center_point(px,py,qx,qy,r,const):
    '''
    2点と半径rから円の中心座標を求める
    args:
        py: 円上の点Pのy座標
        px: 円上の点Pのx座標
        qy: 円上の点Qのy座標
        qx: 円上の点Qのx座標
        r: 円の半径r
        const: 候補2点の識別子
    return:
        x: 円の中心点x座標
        y: 円の中心点y座標
    '''
    if const > 0:
        x=((py - qy)*(np.sqrt(-(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2 - 4*r**2))*(px - qx) - (py + qy)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)) + (px**2 + py**2 - qx**2 - qy**2)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2))/(2*(px - qx)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2))
        y=(np.sqrt(-(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2 - 4*r**2))*(-px + qx)/2 + (py + qy)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)/2)/(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)
    else:
        x=(-(py - qy)*(np.sqrt(-(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2 - 4*r**2))*(px - qx) + (py + qy)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)) + (px**2 + py**2 - qx**2 - qy**2)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2))/(2*(px - qx)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2))
        y=(np.sqrt(-(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2 - 4*r**2))*(px - qx)/2 + (py + qy)*(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)/2)/(px**2 - 2*px*qx + py**2 - 2*py*qy + qx**2 + qy**2)

    return x,y


def calc_ellipse_angle(py,px,qy,qx,r,x,y,const):
    # ellipseの角度は左回転角度が-、右回転角度が+
    if const < 0:
        rotate_rad = math.asin((py-y)/r)
        if x > px:
            rotate_rad -= math.pi
        rotate_deg = math.degrees(rotate_rad)

        # 二等辺三角形から円の中心角を求める
        ml = np.linalg.norm(np.array([px,py])-np.array([qx,qy]))/2
        angle_rad = -1*2*math.asin(ml/r)
        angle_deg = math.degrees(angle_rad)

        # 弧の中心角が180度未満なら二等辺三角形の角度が弧の中心角となる
        # 弧の中心角が180度以上なら360-angle_degが弧の中心角となる
        # dx,dy: px,pyと円の中心座標の延長線上の座標
        dx = (x-(py-x))
        dy = (y-(py-y))
        if qx < dx:
            # 弧が180度より大きい
            angle_deg = 180-angle_deg
        elif qy > py: # y軸は下の値が大きい
            # 弧が180度より大きい
            angle_deg = 180-angle_deg
        elif qx == dx:
            # 弧が180度丁度
            angle_rad = 180
        else:
            # 弧が180度より小さい
            pass

    else:
        rotate_rad = -math.pi-math.asin((py-y)/r)
        if x < px:
            rotate_rad += math.pi
        rotate_deg = math.degrees(rotate_rad)

        # 二等辺三角形から円の中心角を求める
        ml = np.linalg.norm(np.array([px,py])-np.array([qx,qy]))/2
        angle_rad = 2*math.asin(ml/r)
        angle_deg = math.degrees(angle_rad)
        # 弧の中心角が180度未満なら二等辺三角形の角度が弧の中心角となる
        # 弧の中心角が180度以上なら360-angle_degが弧の中心角となる
        # dx,dy: px,pyと円の中心座標の延長線上の座標
        dx = ((x-py)+x)
        dy = ((y-py)+y)
        if qx > dx:
            # 弧が180度より大きい
            angle_deg = 180-angle_deg
        elif qy > py: # y軸は下の値が大きい
            # 弧が180度より大きい
            angle_deg = 180-angle_deg
        elif qx == dx:
            # 弧が180度丁度
            angle_deg = 180
        else:
            # 弧が180度より小さい
            pass

        #angle_deg = -1*angle_deg

    return rotate_deg, angle_deg

def calc_line(x1,y1,x2,y2,x):
    '''
    二点(x1,y1),(x2,y2)を通る直線の方程式から、座標xにおけるyの値を求める
    args:
        x1: 直線1上の点1のx座標
        y1: 直線1上の点1のy座標
        x2: 直線1上の点2のx座標
        y2: 直線1上の点2のy座標
        x: 直線1上の点のx座標
    return:
        y: 直線1上の点のy座標
    '''
    y = (x*y1 - x*y2 + x1*y2 - x2*y1)/(x1 - x2)
    return y

