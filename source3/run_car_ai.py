# coding: utf-8
# ラジコン自走コード
# pip install futures

import time
from concurrent import futures
import os
from multiprocessing import Manager
import thread
import threading
import logging
from __future__ import division
import Adafruit_PCA9685
import smbus
import numpy as np
import LidarLiteV3
import tensorflow as tf


# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

LIDAR_INTERVAL = 0.05

'''
ステアリング制御クラス
'''
class SteeringControl(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.lock = threading.Lock()
        self.CALIBRATION = kwargs[0]

        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(60)

        self.HANDLE_NUTRAL = 375 + self.CALIBRATION
        #self.HANDLE_MAX_RIGHT = 150
        #self.HANDLE_MAX_LEFT = 600

        self.MAX_HANDLE_ANGLE = 45
        self.HANDLE_RIGHT = self.HANDLE_NUTRAL + self.MAX_HANDLE_ANGLE
        self.HANDLE_LEFT = self.HANDLE_NUTRAL - self.MAX_HANDLE_ANGLE

        self.channel = 0
        return

    def right(self):
        self.pwm.set_pwm(self.channel, 0, self.HANDLE_RIGHT)
    def forward(self):
        self.pwm.set_pwm(self.channel, 0, self.HANDLE_NUTRAL)
    def left(self):
        self.pwm.set_pwm(self.channel, 0, self.HANDLE_LEFT)
    def stop(self):
        self.pwm.set_pwm(self.channel, 0, self.HANDLE_NUTRAL)


'''
モーター制御クラス
'''
class MotorControl(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                              verbose=verbose)
        self.lock = threading.Lock()

        ## DRV8830 Default I2C slave address
        self.MOTOR1_ADDRESS  = 0x64
        ''' DRV8830 Register Addresses '''
        ## sample rate driver
        self.CONTROL = 0x00
        ## Value motor.
        self.FORWARD = 0x02
        self.BACK = 0x01
        self.STOP = 0x00

        self.MAX_SPEED = 101

        ## smbus
        self.bus = smbus.SMBus(1)

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def drive(self, speed=101):
        if speed < 0:
            return
        if speed > self.MAX_SPEED:
            return
        s = self.map(speed, 1, 100, 1, 58)
        sval = self.FORWARD | ((s+5)<<2) #スピードを設定して送信するデータを1Byte作成
        self.bus.write_i2c_block_data(self.MOTOR1_ADDRESS,self.CONTROL,[sval]) #生成したデータを送信

    def back(self, speed=101):
        if speed < 0:
            return
        if speed > self.MAX_SPEED:
            return
        s = self.map(speed, 1, 100, 1, 58)
        sval = self.BACK | ((s+5)<<2) #スピードを設定して送信するデータを1Byte作成
        self.bus.write_i2c_block_data(self.MOTOR1_ADDRESS,self.CONTROL,[sval]) #生成したデータを送信

    def stop(self):
        speed = 0
        s = self.map(speed, 1, 100, 1, 58)
        sval = self.FORWARD | ((s+5)<<2) #スピードを設定して送信するデータを1Byte作成
        self.bus.write_i2c_block_data(self.MOTOR1_ADDRESS,self.CONTROL,[sval]) #生成したデータを送信


'''
ここはプロセスで実行される
SHARED_VARIABLE['CONTROL_READY']=True であるうちは実行を続ける
'''
def do_control():
    logging.debug("enter")
    SHARED_VARIABLE['CONTROL_READY']=True

    STOP=0
    LEFT=1
    FORWARD=2
    RIGHT=3

    calibration = +0
    steering_control_thread = SteeringControl(kwargs=[calibration])
    motor_control_thread = MotorControl()
    # タイヤをまっすぐにする
    steering_control_thread.forward()

    ####################
    # ループ実行
    ####################
    while SHARED_VARIABLE['CONTROL_READY']:
        print("control: ", SHARED_VARIABLE['PREDICTION_VALUE'])
        if SHARED_VARIABLE['PREDICTION_VALUE'] == STOP:
            motor_control_thread.stop()
            steering_control_thread.forward()
        if SHARED_VARIABLE['PREDICTION_VALUE'] == LEFT:
            steering_control_thread.left()
            motor_control_thread.drive()
        if SHARED_VARIABLE['PREDICTION_VALUE'] == FORWARD:
            steering_control_thread.forward()
            motor_control_thread.drive()
        if SHARED_VARIABLE['PREDICTION_VALUE'] == RIGHT:
            steering_control_thread.right()
            motor_control_thread.drive()

        time.sleep(LIDAR_INTERVAL)

    motor_control_thread.stop()
    steering_control_thread.forward()
    return



def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the 
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we can use again a convenient built-in function to import a graph_def into the 
    # current default Graph
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def, 
            input_map=None, 
            return_elements=None, 
            name="prefix", 
            op_dict=None, 
            producer_op_list=None
        )
    return graph


'''
ここはプロセスで実行される
SHARED_VARIABLE['PREDICTION_READY']=True であるうちは実行を続ける
'''
def do_prediction():
    logging.debug("enter")
    SHARED_VARIABLE['PREDICTION_READY']=True
    tf.reset_default_graph()

    ########################################
    # AI準備
    ########################################
    try:

        # Lidar準備
        lidar1 = LidarLiteV3.Connect(0x52)
        lidar2 = LidarLiteV3.Connect(0x54)
        lidar3 = LidarLiteV3.Connect(0x56)
        
        # AIモデルファイル名とディレクトリ
        FROZEN_MODEL_NAME="car_lidar_queue_20000.pb"
        MODEL_DIR = "./model_car_lidar_queue"

        # AIモデル読み込み
        graph = load_graph(MODEL_DIR+"/"+FROZEN_MODEL_NAME)
        graph_def = graph.as_graph_def()
        # AI入出力ノード取得
        input_x = graph.get_tensor_by_name('prefix/queue/dequeue_op:0')
        output_y= graph.get_tensor_by_name('prefix/neural_network_model/output_y:0')

        n_classes=4 # 出力数(STOP,LEFT,FORWARD,RIGHTの4種類)
        start_time, start_clock = time.time(), time.clock()

        '''
        AI予測実行
        sensor:[[100,200,100]] # [[LEFT45,FRONT,RIGHT45]], int型[1,3]配列
        max_index:N # 0:STOP,1:LEFT,2:FORWARD,3:RIGHT int型
        '''
        with tf.Session(graph=graph) as sess:
            ####################
            # ループ実行
            ####################
            while SHARED_VARIABLE['PREDICTION_READY']:
                distance1 = lidar1.getDistance()
                distance2 = lidar2.getDistance()
                distance3 = lidar3.getDistance()

                _output_y = sess.run(output_y,feed_dict={input_x:[[distance1,distance2,distance3]]})
                max_index = np.argmax(_output_y) # max_value's index no
                SHARED_VARIABLE['PREDICTION_VALUE'] = max_index

                time.sleep(LIDAR_INTERVAL)

    except Exception as e:
        print str(e)
        if not SHARED_VARIABLE['PREDICTION_READY']:
            print 'error! PREDICTION_READY is False'
    finally:
        return





'''
ここはプロセスで実行される
'''
def do_stop():
    tag='STOP'

    ####################
    # ループ実行
    ####################
    start_time = time.time()
    RUNNING_SEC = 60
    time.sleep(RUNNING_SEC)
    SHARED_VARIABLE['CONTROL_READY']=False
    SHARED_VARIABLE['PREDICTION_READY']=False
    SHARED_VARIABLE['IF_READY']=False

    return

'''
process pattern
'''
SHARED_VARIABLE=Manager().dict()
SHARED_VARIABLE['CONTROL_READY']=False
SHARED_VARIABLE['PREDICTION_READY']=False
SHARED_VARIABLE['IF_READY']=False
SHARED_VARIABLE['CONTROL_VALUE']=0
SHARED_VARIABLE['PREDICTION_VALUE']=0

'''
プロセスによる実行関数の振り分け定義
'''
PROCESS_LIST=['do_control','do_prediction','do_stop']
def do_process(target):

    if target == 'do_control':
        do_control()
        return "end do_control"
    if target == 'do_prediction':
        do_prediction()
        return "end do_prediction"
    if target == 'do_stop':
        do_stop()
        return "end do_stop"

'''
メイン処理を行う部分
・メインスレッド（ここ）
・スレッド1(concurrent.futures)
・スレッド2(concurrent.futures)
・制御スレッド(concurrent.futures)
'''
def do_main():
    try:
        with futures.ProcessPoolExecutor(max_workers=len(PROCESS_LIST)) as executer:
            mappings = {executer.submit(do_process, pname): pname for pname in PROCESS_LIST}
            for i in futures.as_completed(mappings):
                target = mappings[i]
                result = i.result()
                print(result)

    except Exception as e:
        print('error! executer failed.')
        print(str(e))
    finally:
        print("executer end")

    return

do_main()
