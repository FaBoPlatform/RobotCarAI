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
#from __future__ import division
import MotorShield
import numpy as np
import LidarLiteV3
import tensorflow as tf
import FaBoGPIO_PCAL6408


# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

LIDAR_INTERVAL = 0.05

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

    HANDLE_NEUTRAL = 310 # ステアリングニュートラル位置

    car = MotorShield.RobotCar()
    # タイヤのニュートラル位置を記憶し、設定する
    car.handle_forward(HANDLE_NEUTRAL)

    speed = 100 # 走行速度

    ####################
    # ループ実行
    ####################
    while SHARED_VARIABLE['CONTROL_READY']:
        if SHARED_VARIABLE['PREDICTION_VALUE'] == STOP:
            car.motor_stop()
            car.handle_forward()
        if SHARED_VARIABLE['PREDICTION_VALUE'] == LEFT:
            car.handle_left()
            car.motor_forward(speed)
        if SHARED_VARIABLE['PREDICTION_VALUE'] == FORWARD:
            car.handle_forward()
            car.motor_forward(speed)
        if SHARED_VARIABLE['PREDICTION_VALUE'] == RIGHT:
            car.handle_right()
            car.motor_forward(speed)

        time.sleep(LIDAR_INTERVAL)

    car.motor_stop()
    car.handle_forward()
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

    # Lidarの電源を入れるKerberos基板の準備をする
    pcal6408 = FaBoGPIO_PCAL6408.PCAL6408()

    ########################################
    # AI準備
    ########################################
    try:
        ########################################
        # Lidar1のアドレスを変更する 0x62 -> 0x52
        ########################################
        pcal6408.setDigital(1<<0, 1) # 0番目のLidarの電源を入れる
        time.sleep(0.1)
        lidar1 = LidarLiteV3.Connect(0x62)
        lidar1.changeAddress(0x52)
 
        ########################################
        # Lidar2のアドレスを変更する 0x62 -> 0x54
        ########################################
        pcal6408.setDigital(1<<1, 1) # 1番目のLidarの電源を入れる
        time.sleep(0.1)
        lidar2 = LidarLiteV3.Connect(0x62)
        lidar2.changeAddress(0x54)

        ########################################
        # Lidar3のアドレスを変更する 0x62 -> 0x56
        ########################################
        pcal6408.setDigital(1<<2, 1) # 3番目のLidarの電源を入れる
        time.sleep(0.1)
        lidar3 = LidarLiteV3.Connect(0x62)
        lidar3.changeAddress(0x56)
        
        # AIモデルファイル名とディレクトリ
        FROZEN_MODEL_NAME="car_model.pb"
        MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/model"

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

    except:
        import traceback
        traceback.print_exc()
        if not SHARED_VARIABLE['PREDICTION_READY']:
            print('error! PREDICTION_READY is False')
    finally:
        pcal6408.setAllClear() # すべてのLidarの電源を落とす
        return





'''
ここはプロセスで実行される
'''
def do_stop():

    ####################
    # ループ実行
    ####################
    start_time = time.time()
    RUNNING_SEC = 30
    time.sleep(RUNNING_SEC)
    SHARED_VARIABLE['CONTROL_READY']=False
    SHARED_VARIABLE['PREDICTION_READY']=False

    return

'''
process pattern
'''
SHARED_VARIABLE=Manager().dict()
SHARED_VARIABLE['CONTROL_READY']=False
SHARED_VARIABLE['PREDICTION_READY']=False
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

    except:
        import traceback
        traceback.print_exc()
        print('error! executer failed.')
    finally:
        print("executer end")

    return

do_main()
