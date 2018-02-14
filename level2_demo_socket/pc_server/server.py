#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ClientからOpenCV画像データを受け取り、ライン検出して制御命令を送る
# Server: Jetson TX2
# Client: Jetson TX2/Raspberry Pi3 Docker
# 先にServerを起動する

'''
Python 3.6
    送信するmessageは.encode('ascii')や.encode('utf-8')等でエンコードする必要がる
    ここではClientから送られてくるOpenCV BGR画像データが'ascii'に変換されているので'ascii'で統一している
'''
print("loading...")
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


def main():
    # 通信設定
    HOST = '192.168.0.77' # Server IP Address
    PORT = 6666 # Server Port

    # IPM変換後の画像におけるx,yメートル(黒い部分も含む)
    X_METER=1.5
    Y_METER=1

    # 映像を保存するかどうか
    IS_SAVE = True
    OUTPUT_DIR ='./'
    OUTPUT_FILENAME = 'received.avi'

    HANDLE_ANGLE = 42

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
    # 解析準備
    ########################################
    ld = None
    frame_counter = 0
    fourcc = None
    out = None
    control = None
    cols = 0
    rows = 0
    fps = 0
    roi_vertices = None
    ipm_vertices = None

    cv_version = cv2.__version__.split(".")
    if cv_version[0] == '2':
        # OpenCV 2.4
        fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
    else:
        # OpenCV 3.1
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    print("ready")

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
                    # 1Frameずつデータサイズが異なるので、毎回sizeを送ること
                    if is_need_header_receive:
                        print('header')
                        packet = packet.decode('ascii')
                        txt = str(packet)
                        if packet:
                            print('packet True')
                            if packet.startswith('SIZE'):
                                print('got SIZE')
                                tmp = txt.split()
                                size = int(tmp[1])
                                is_need_header_receive = False
                                sock.sendall("GOT SIZE".encode('ascii'))
                            elif packet.startswith('CAMERA'):
                                # 画像サイズを取得する
                                _, cols,rows,fps = txt.split(',')
                                cols = int(float(cols))
                                rows = int(float(rows))
                                fps = float(fps)

                                ld = LaneDetection(X_METER,Y_METER,cols=cols,rows=rows)
                                print('got CAMERA,cols={},rows={},fps={}'.format(cols,rows,fps))
                                out = cv2.VideoWriter(os.path.join(OUTPUT_DIR, OUTPUT_FILENAME), int(fourcc), fps, (int(cols), int(rows)))
                            elif packet.startswith('BYE'):
                                print('got BYE')
                                is_need_header_receive = True
                                sock.shutdown(socket.SHUT_RDWR)
                                sock.close()
                                connected_clients_sockets.remove(sock)
                                frame_counter = 0
                                out.release()
                        else:
                            print('client disconnect')
                            is_need_header_receive = True
                            sock.shutdown(socket.SHUT_RDWR)
                            sock.close()
                            connected_clients_sockets.remove(sock)
                            frame_counter = 0
                            out.release()
                    if not is_need_header_receive:
                        print('body')
                        if packet:
                            print('packet True')
                            frame_counter += 1
                            print("frame_counter = {}".format(frame_counter))
                            print('packet size = {}'.format(size))
                            # 1Frameのデータサイズが大きいと、分割送信されてくるのでループで最後まで取得する
                            data = b''
                            while True:
                                packet = sock.recv(4096)
                                if not packet:
                                    break
                                else:
                                    data += packet
                                if size == len(data):
                                    break

                            nparr = np.fromstring(data, np.uint8)
                            cv_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # cv2.CV_LOAD_IMAGE_COLOR/cv2.IMREAD_COLOR in OpenCV 3.1
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
                                control='0,0'
                                sock.sendall(("CONTROL,"+ control).encode('ascii'))
                                continue
                            ########################################
                            # 速度調整を行う
                            ########################################
                            if np.abs(angle2_deg) > np.abs(angle1_deg):
                                speed = 50
                            else:
                                speed = 80

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
                            if handle_angle <  -1*HANDLE_ANGLE:
                                handle_angle = -1*HANDLE_ANGLE

                            # avi動画に保存する
                            if IS_SAVE:
                                out.write(cv_bgr)

                            is_need_header_receive = True
                            control=str(speed)+','+str(handle_angle)
                            print("speed={},handle_angle={},CONTROL,{}".format(speed,handle_angle,control))
                            sock.sendall(("CONTROL,"+ control).encode('ascii'))
                        else:
                            print('data finished')
                            is_need_header_receive = True
                            sock.shutdown(socket.SHUT_RDWR)
                            sock.close()
                            connected_clients_sockets.remove(sock)
                            frame_counter = 0
                            out.release()

    except:
        import traceback
        traceback.print_exc()
    finally:
        is_need_header_receive = True
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        connected_clients_sockets.remove(sock)
        server_socket.close()
        frame_counter = 0
        out.release()

if __name__ == '__main__':
    main()
    print("end server")
