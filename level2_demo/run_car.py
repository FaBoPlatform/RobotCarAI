# coding: utf-8
# レーン認識
# ロボットカー自走コード

import time
import logging
import threading
import numpy as np
from fabolib import Kerberos
from fabolib import Car
from lib import SPI
from lib import LaneDetection
from lib import *

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    import Queue
elif PY3:
    import queue as Queue
# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

########################################
# ステータス
########################################
main_thread_running = True
stop_thread_running = True


def do_stop_button():
    '''
    停止ボタンの値を取得し続ける関数
    '''
    global stop_thread_running
    global main_thread_running

    # 停止ボタン準備
    A0 = 0 # SPI PIN
    STOP_BUTTON_SPI_PIN = A0
    spi = SPI()

    while stop_thread_running:
        data = spi.readadc(STOP_BUTTON_SPI_PIN)
        if data >= 1000:
            # 停止ボタンが押された
            main_thread_running = False
            stop_thread_running = False
            break
        time.sleep(0.1)
    return

def main():
    '''
    メイン処理を行う部分
    '''
    global stop_thread_running
    global main_thread_running

    # I2C Bus number
    BUSNUM = 1

    # CAR準備
    HANDLE_NEUTRAL = 95 # ステアリングニュートラル位置
    HANDLE_ANGLE = 42 # 左右最大アングル
    car = Car(busnum=BUSNUM)
    speed = 0
    angle = HANDLE_NEUTRAL

    # カメラ準備
    COLS = 160
    ROWS = 120
    # IPM変換後の画像におけるx,yメートル(黒い部分も含む)
    X_METER=1.5
    Y_METER=1
    ld = LaneDetection(X_METER,Y_METER,cols=COLS,rows=ROWS)
    ld.init_webcam(fps=15,save=False) # Raspberry PiはCPU負荷が高いので消費電流を抑えるためにfpsを下げる必要がある。
    # ライン検出結果を保存しておく
    tilt1_deg = 0
    tilt2_deg = 0
    angle1_deg = 0
    angle2_deg = 0
    curve1_r = 0
    curve2_r = 0
    meters_from_center = 0
    while main_thread_running:
        try:
            if not stop_thread_running: break # 強制停止ならループを抜ける

            # カメラ画像を読み込む
            try:
                ld.webcam_capture()
            except:
                import traceback
                traceback.print_exc()
                main_thread_running = False
                stop_thread_running = False
                break
            # ラインを検出する
            tilt1_deg,tilt2_deg,angle1_deg,angle2_deg,curve1_r,curve2_r, \
                meters_from_center = ld.lane_detection()

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

            if not stop_thread_running: break # 強制停止ならループを抜ける

            ########################################
            # 車両を制御する
            ########################################
            car.set_angle(HANDLE_NEUTRAL + handle_angle)
            car.forward(speed)
        except:
            import traceback
            traceback.print_exc()
            # カメラエラーもしくはラインが検出出来なかった時
            car.stop()
            car.set_angle(HANDLE_NEUTRAL)
        finally:
            time.sleep(0.05)
            pass
    car.stop()
    car.set_angle(HANDLE_NEUTRAL)
    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_stop_button,args=())
    t.start()
    main()
    print("end car")
