# coding: utf-8
# ロボットカー制御ネットワーククライアント

import socket, select
import time
import logging
import threading
import numpy as np
import cv2
from fabolib import Kerberos
from fabolib import Car
from lib import SPI
from lib import *

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

    # CAR設定
    HANDLE_NEUTRAL = 95 # ステアリングニュートラル位置
    HANDLE_ANGLE = 42 # 左右最大アングル
    # カメラ設定
    COLS = 160
    ROWS = 120
    FPS = 5
    # 通信設定
    HOST = '192.168.0.77' # Server IP Address
    PORT = 6666 # Server TCP Port
    #HOST = '34.224.145.198' # AWS
    #PORT = 8091 # AWS
    #HOST = '192.168.0.17' # PC
    #PORT = 8091 # PC

    sock = None
    frame_counter = 0
    try:
        ########################################
        # CAR準備
        ########################################
        car = Car()
        speed = 0
        ########################################
        # 通信準備
        ########################################
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        sock.connect(server_address)
        is_need_header_send = True

        ########################################
        # ロボットカー開始をサーバに送る
        ########################################
        message = "START"
        sock.sendall(message.encode('ascii'))    

        ########################################
        # 処理開始
        ########################################
        data = ''
        while main_thread_running:
            start_time,clock_time = time.time(),time.clock()
            if not stop_thread_running: break # 強制停止ならループを抜ける

            ########################################
            # サーバからの車両制御を待つ
            ########################################
            answer = sock.recv(4096)
            if len(data) > 0:
                answer = data + answer.decode('ascii')
            else:
                answer = answer.decode('ascii')
            #print('answer = {}'.format(answer))

            ########################################
            # 車両制御を行う
            ########################################
            # パケット解析は連結していたり分割されているのでTCPストリーミングとして解析する
            packet_length = len(answer)
            delimiter_counter = 0
            control_start_index = None
            for i in range(packet_length-1,0,-1):
                if answer[i] == ',':
                    delimiter_counter += 1
                if answer[i] == 'L':
                    # 制御開始文字を発見
                    if delimiter_counter >= 3:
                        # 制御データが含まれている
                        control_start_index = i
                        break
                    else:
                        # 制御データが無いので探す
                        print("data too short {} {}".format(i,delimiter_counter))
                        continue
            if control_start_index is None:
                # 制御データが見つからなかった、次のパケットの先頭にデータを結合する
                #print("is None")
                data = answer
                continue

            # 制御データが見つかったのでspeed,handle_angleを取得する
            partition_counter = 0
            speed = ''
            handle_angle = ''
            data = ''
            for i in range(control_start_index, packet_length):
                if answer[i] == ',':
                    if partition_counter > 3:
                        data += answer[i]
                    partition_counter += 1
                    continue
                if partition_counter == 1:
                    # speed
                    speed += answer[i]
                elif partition_counter == 2:
                    # handle_angle
                    handle_angle += answer[i]
                elif partition_counter == 3:
                    # next data
                    data += answer[i]

            speed = int(float(speed))
            handle_angle = int(float(handle_angle))
            frame_counter += 1
            print("CONTROL,speed={},handle_angle={}".format(speed,handle_angle))

            # 動作可能な角度内に調整する
            if handle_angle > HANDLE_ANGLE:
                handle_angle = HANDLE_ANGLE
            if handle_angle < -1*HANDLE_ANGLE:
                handle_angle = -1*HANDLE_ANGLE

            if not stop_thread_running: break # 強制停止ならループを抜ける

            ########################################
            # 車両を制御する
            ########################################
            car.set_angle(HANDLE_NEUTRAL + handle_angle)
            if speed == 0:
                car.stop()
            else:
                car.forward(speed)
            print("FPS:{} ".format(1/(time.time() - start_time)))
            #time.sleep(0.5)
            #car.stop()
    except:
        import traceback
        traceback.print_exc()
    finally:
        #print("FPS:{} ".format(frame_counter/(time.time() - start_time)))
        
        main_thread_running = False
        stop_thread_running = False
        pass
    if sock is not None:
        sock.close()
    car.stop()
    car.set_angle(HANDLE_NEUTRAL)
    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_stop_button,args=())
    t.start()
    main()
    print("end car")
