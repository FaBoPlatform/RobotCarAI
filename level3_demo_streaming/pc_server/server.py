#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ClientからOpenCV画像データを受け取り、ライン検出して制御命令を送る
# Server: Jetson TX2
# Client: Jetson TX2/Raspberry Pi3 Docker
# 1. FFMPEG UDP StreamingをClientで実行する。AWS向け10FPS,Jetson TX2向け1FPS
# 2. Serverを起動する
# 3. Clientを起動する
# コード修正
# lib/camera.py: vid = cv2.VideoCapture()を環境に合わせて修正する必要がある
# lib/object_detection.py: /home/ubuntu/notebooks/github/SSD-Tensorflow/ を環境に合わせて修正する必要がある
'''
Python 3.6
    送信するmessageは.encode('ascii')や.encode('utf-8')等でエンコードする必要がる
    ここではClientから送られてくるOpenCV BGR画像データが'ascii'に変換されているので'ascii'で統一している
'''
print("wait. launching...")
import socket, select
import time
import cv2
import numpy as np
import time
import os
import sys
import logging
import threading
import numpy as np
from lib import *

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

# 解析、送信スレッド動作フラグ
is_analyze_running = False

sock = None
out = None

# IPM変換後の画像におけるx,yメートル(黒い部分も含む)
X_METER=1.5
Y_METER=1

# ライン検出クラス
ld = None
# 物体検出クラス
od = None

def do_analyze():
    global is_analyze_running
    global sock
    global out
    global X_METER
    global Y_METER
    global ld
    global od

    # 映像を保存するかどうか
    IS_SAVE = False
    OUTPUT_DIR ='./'
    OUTPUT_FILENAME = 'received.avi'

    HANDLE_ANGLE = 42

    frame_counter = 0
    fourcc = None
    control = None
    roi_vertices = None
    ipm_vertices = None
    speed = None

    # 映像準備
    camera = Camera()
    cols,rows,fps,fourcc = camera.init_webcam()
    fps = 1
    if IS_SAVE:
        out = cv2.VideoWriter(os.path.join(OUTPUT_DIR, OUTPUT_FILENAME), int(fourcc), fps, (int(cols), int(rows)))

    ########################################
    # ライン検出準備
    ########################################
    ld = LaneDetection(X_METER,Y_METER,cols=cols,rows=rows)

    ########################################
    # 最初に映像バッファを削除する
    ########################################
    for i in range(300):
        res = camera.webcam_capture()
    while is_analyze_running:
        frame_start_time = time.time()
        #time.sleep(0.2)
        ########################################
        # 映像取得
        ########################################
        for i in range(30): # 処理が遅くてバッファに蓄積されてくる古いフレームを除去
            res = camera.webcam_capture()
            if not res:
                break
        frame_counter += 1
        ########################################
        # 物体認識
        ########################################
        cv_bgr = camera.cv_bgr
        if cv_bgr is None:
            continue
        # avi動画に保存する
        if IS_SAVE:
            out.write(cv_bgr)
        rclasses,rscores,rbboxes = od.get_detection(cv_bgr)
        print(rclasses,rscores,rbboxes)
        if len(rclasses) > 0:
            prediction_class = np.min(rclasses)
            if prediction_class == 1:
                # 止まれを検出した
                is_need_header_receive = True
                control='0,0,'
                sock.sendall(("CONTROL,"+ control).encode('ascii'))
                continue
            elif prediction_class == 2:
                # 10を検出した
                speed = 40
            elif prediction_class == 3:
                # 20を検出した
                speed = 50
            elif prediction_class == 4:
                # 30を検出した
                speed = 60
        else:
            # 物体検出無し
            if speed is None:
                speed = 40

        handle_angle = 0
        ########################################
        # ライン検出
        ########################################
        ld.cv_bgr = cv_bgr
        # ラインを検出する
        try:
            tilt1_deg,tilt2_deg,angle1_deg,angle2_deg,curve1_r,curve2_r, \
                meters_from_center = ld.lane_detection()
        except:
            # ライン検出失敗
            is_need_header_receive = True
            control='0,0,'
            sock.sendall(("CONTROL,"+ control).encode('ascii'))
            continue

        ########################################
        # 速度調整を行う
        ########################################
        #if np.abs(angle2_deg) > np.abs(angle1_deg):
        #    speed = 50
        #else:
        #    speed = 60

        '''
        左右について
        tilt_deg: -が右、+が左
        angle_deg: +が右、-が左
        meters_from_center: -が右にいる、+が左にいる
        handle_angle: +が右、-が左
        '''
        ########################################
        # ハンドル角調整を行う
        ########################################
        handle_angle = -1*tilt1_deg
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
        if handle_angle < -1*HANDLE_ANGLE:
            handle_angle = -1*HANDLE_ANGLE

        # 車両制御送信
        control=str(speed)+','+str(handle_angle)+','
        print("speed={},handle_angle={},CONTROL,{}".format(speed,handle_angle,control))
        sock.sendall(("CONTROL,"+ control).encode('ascii'))
        frame_end_time = time.time()
        print("FPS={}".format(round(1/(frame_end_time-frame_start_time),2)))

def main():
    global is_analyze_running
    global sock
    global out
    global ld
    global od

    # 通信設定
    HOST = '192.168.0.77' # Server IP Address
    PORT = 6666 # Server TCP Port
    #HOST = 'a32158c3da9f' # AWS Docker
    #PORT = 8091 # AWS TCP Port
    #HOST = '2204f9b0e871' # PC Docker
    #PORT = 8091 # PC TCP Port

    ########################################
    # 通信準備
    ########################################
    connected_clients_sockets = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    connected_clients_sockets.append(server_socket)
    # Headerの受信が必要かどうか。Headerを受信したら、encode('ascii')を通さずに受信データを解析する
    is_need_header_receive = True

    ########################################
    # 物体認識準備
    ########################################
    od = ObjectDetection()

    print("Server start")
    try:

        while True:
            ########################################
            # 受信待ち
            ########################################
            read_sockets, write_sockets, error_sockets = select.select(connected_clients_sockets, [], [])

            for sock in read_sockets:
                if sock == server_socket:
                    sockfd, client_address = server_socket.accept()
                    connected_clients_sockets.append(sockfd)
                else:
                    # ClientがServerにHeaderを送る時は4096 Byte以下にすること
                    packet = sock.recv(4096)
                    print(type(packet))
                    # 
                    if is_need_header_receive:
                        print('header')
                        packet = packet.decode('ascii')
                        txt = str(packet)
                        if packet:
                            print('packet True')
                            if packet == 'START':
                                is_analyze_running = True
                                t = threading.Thread(target=do_analyze)
                                t.start()
                            elif packet.startswith('BYE'):
                                print('got BYE')
                                is_need_header_receive = True
                                is_analyze_running = False
                                sock.shutdown(socket.SHUT_RDWR)
                                sock.close()
                                connected_clients_sockets.remove(sock)
                                if out is not None:
                                    out.release()
                        else:
                            print('client disconnect')
                            is_need_header_receive = True
                            is_analyze_running = False
                            sock.shutdown(socket.SHUT_RDWR)
                            sock.close()
                            connected_clients_sockets.remove(sock)
                            if out is not None:
                                out.release()
                    if not is_need_header_receive:
                        # ここには来ない
                        print('body')
                        if packet:
                            print('packet True')
                            is_need_header_receive = True
                        else:
                            print('data finished')
                            is_need_header_receive = True
                            is_analyze_running = False
                            sock.shutdown(socket.SHUT_RDWR)
                            sock.close()
                            connected_clients_sockets.remove(sock)
                            if out is not None:
                                out.release()

    except:
        import traceback
        traceback.print_exc()
    finally:
        is_need_header_receive = True
        is_analyze_running = False
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        connected_clients_sockets.remove(sock)
        server_socket.close()
        if out is not None:
            out.release()

if __name__ == '__main__':
    main()
    print("end server")
