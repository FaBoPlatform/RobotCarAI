# coding: utf-8
# ロボットカー制御ネットワーククライアント

import socket, select
import time
import logging
import threading
import numpy as np
import cv2
from fabolib.car import Car
from lib.spi import SPI
from lib.camera import Camera

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
    try:
        ########################################
        # CAR準備
        ########################################
        car = Car(busnum=BUSNUM)
        speed = 0
        ########################################
        # カメラ準備
        ########################################
        camera = Camera()
        camera.init_webcam(cols=COLS,rows=ROWS,fps=FPS,save=False)
        frame_count=0
        ########################################
        # 通信準備
        ########################################
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        sock.connect(server_address)
        is_need_header_send = True

        ########################################
        # 画像サイズ、FPSをサーバに送る
        ########################################
        message = "CAMERA,"+str(COLS)+","+str(ROWS)+","+str(FPS/5)
        sock.sendall(message.encode('ascii'))    

        ########################################
        # 処理開始
        ########################################
        while main_thread_running:
            start_time,clock_time = time.time(),time.clock()
            if not stop_thread_running: break # 強制停止ならループを抜ける
            # カメラ画像を読み込む
            for i in range(5):
                if not camera.webcam_capture():
                    break
            frame_count+=1

            ########################################
            # 送信するデータを準備する
            ########################################
            bytes = cv2.imencode('.jpg', camera.cv_bgr)[1].tostring()
            size = len(bytes)

            ########################################
            # 最初にデータサイズを送り、返答を待つ
            ########################################
            if is_need_header_send:
                # send image size to server
                #print("send size = {}".format(size))
                sock.sendall(("SIZE %s" % size).encode('ascii'))
                answer = sock.recv(4096)
                answer = answer.decode('ascii')
                #print('answer = {}'.format(answer))

            ########################################
            # 画像データを送り、返答を待つ
            ########################################
            if answer == 'GOT SIZE':
                is_need_header_send = False
                sock.sendall(bytes)
                # 画像データ送信後、0.5秒したら前回制御命令で動作している車両を停止する
                time.sleep(0.5)
                car.stop()
                # check what server send
                answer = sock.recv(4096)
                answer = answer.decode('ascii')
                print('answer = {}'.format(answer))

            ########################################
            # 車両制御を行う
            ########################################
            if answer.startswith('CONTROL'):
                is_need_header_send = True                
                _,speed,handle_angle = answer.split(',')
                speed = int(float(speed))
                handle_angle = int(float(handle_angle))
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
            # サーボを高速動作させるとRPに電力遮断されてカメラが動作不能になるため、車両制御にsleepを入れる
            time.sleep(0.2)
    except:
        import traceback
        traceback.print_exc()
    finally:
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
