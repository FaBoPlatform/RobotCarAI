# coding: utf-8

"""
Fabo RobotCar Network Control Program.


"""

import socket, select
import time
import logging
import threading
import numpy as np
import cv2
from fabolib.car import Car
from lib.spi import SPI
import yaml
import os

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

########################################
# ステータス
########################################
main_thread_running = True
stop_thread_running = True

def load_config():
    """
    LOAD CONFIG FILE
    Convert config.yml to DICT.
    """
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = IOError

    cfg = None
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'config.yml')
    print(file_path)
    if (os.path.isfile(file_path)):
        with open(file_path, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
    else:
        raise FileNotFoundError(("File not found: config.yml"))
    return cfg


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
    global stop_thread_running
    global main_thread_running

    """ """ """ """ """ """ """ """ """ """ """
    LOAD SETUP VARIABLES
    """ """ """ """ """ """ """ """ """ """ """
    cfg = load_config()

    """ """ """ """ """ """ """ """ """ """ """
    GET CONFIG
    """ """ """ """ """ """ """ """ """ """ """
    BUSNUM               = cfg['i2c_bus']          # I2C bus number.
    HANDLE_NEUTRAL       = cfg['handle_neutral']   # Steering neutral position.
    MAX_HANDLE_ANGLE     = cfg['max_handle_angle'] # Steering left/right max angle.
    HOST                 = cfg['host']             # Server IP Address.
    PORT                 = cfg['port']             # Server TCP Port.

    sock = None
    try:
        """ """ """ """ """ """ """ """ """ """ """
        Create CAR
        """ """ """ """ """ """ """ """ """ """ """
        car = Car(busnum=BUSNUM)
        speed = 0

        """ """ """ """ """ """ """ """ """ """ """
        Connect to Server
        """ """ """ """ """ """ """ """ """ """ """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        sock.connect(server_address)
        is_need_header_send = True
        data = ''

        """ """ """ """ """ """ """ """ """ """ """
        Send "START" strings to Server
        """ """ """ """ """ """ """ """ """ """ """
        message = "START"
        sock.sendall(message.encode('ascii'))    

        """ """ """ """ """ """ """ """ """ """ """
        Processing Loop
        """ """ """ """ """ """ """ """ """ """ """
        while main_thread_running:
            if not stop_thread_running:
                message = "BYE"
                sock.sendall(message.encode('ascii'))    
                break

            """ """ """ """ """ """ """ """ """ """ """
            Wait until receive control signal from server
            """ """ """ """ """ """ """ """ """ """ """
            answer = sock.recv(4096)
            if len(data) > 0:
                answer = data + answer.decode('ascii')
            else:
                answer = answer.decode('ascii')
            #print('answer = {}'.format(answer))

            """ """ """ """ """ """ """ """ """ """ """
            Car Control
                Because packet is concatenated or divided, it analyze as TCP streaming.
            """ """ """ """ """ """ """ """ """ """ """
            packet_length = len(answer)
            delimiter_counter = 0
            control_start_index = None
            for i in range(packet_length-1, 0, -1):
                if answer[i] == ',':
                    delimiter_counter += 1
                if answer[i] == 'L':
                    """
                    CONTROL 'L' string found
                    """
                    if delimiter_counter >= 3:
                        """
                        Found speed and handle_angle values.
                        """
                        control_start_index = i
                        break
                    else:
                        """
                        Latest data is divided. Search previous data.
                        """
                        delimiter_counter = 0
                        print("data too short {} {}".format(i, delimiter_counter))
                        continue
            if control_start_index is None:
                """
                No complete control data found.
                    add to next data.
                """
                data = answer
                continue

            """
            Found speed and handle_angle values.
                get values.
            """
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
            #print("CONTROL,speed={},handle_angle={}".format(speed,handle_angle))

            """
            Adjust within operable angle
            """
            if handle_angle > MAX_HANDLE_ANGLE:
                handle_angle = MAX_HANDLE_ANGLE
            if handle_angle < -1*MAX_HANDLE_ANGLE:
                handle_angle = -1*MAX_HANDLE_ANGLE

            """
            Car Control
            """
            car.set_angle(HANDLE_NEUTRAL + handle_angle)
            if speed == 0:
                car.stop()
            else:
                car.forward(speed)
            # サーボを高速動作させるとRPに電力遮断されてカメラが動作不能になるため、車両制御にsleepを入れる
            time.sleep(0.2)
    except:
        import traceback
        traceback.print_exc()
    finally:
        car.stop()
        car.set_angle(HANDLE_NEUTRAL)

        main_thread_running = False
        stop_thread_running = False
        if sock is not None:
            sock.close()
    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_stop_button, args=())
    t.start()
    main()
    print("end car")
