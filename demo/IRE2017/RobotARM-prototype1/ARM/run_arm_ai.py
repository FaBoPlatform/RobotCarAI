# coding: utf-8
# アーム動作
# pip install futures

from __future__ import division
import time
from concurrent import futures
import os
from multiprocessing import Manager
import thread
import threading
import logging
from arm import ARM
import numpy as np
import tensorflow as tf
import cv2

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

CONTROL_MOVING = 1
CONTROL_EMPTY = 0
CONTROL_FORCE_STOP = 100

'''
ここはプロセスで実行される
SHARED_VARIABLE['CONTROL_READY']=True であるうちは実行を続ける
'''
def do_control():
    logging.debug("enter")
    SHARED_VARIABLE['CONTROL_READY']=True

    ####################
    # ARM準備
    ####################
    arm_cls=ARM()
    arm_cls.arm_empty()

    LOCAL_AI_VALUE = 4; # 動作時のAI判定結果を保持する。4:その他 を初期値とする。
    ####################
    # ループ実行
    ####################
    try:
        while SHARED_VARIABLE['CONTROL_READY']:
            LOCAL_AI_VALUE = SHARED_VARIABLE['PREDICTION_VALUE']
            if LOCAL_AI_VALUE == 0: # アレルケア
                SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                print("control 0 moving")
                arm_cls.arm_catch()
                arm_cls.arm_put()
            if LOCAL_AI_VALUE == 1: # 紙コップ
                SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                print("control 1 moving")
                arm_cls.arm_catch()
                arm_cls.arm_put()
            if LOCAL_AI_VALUE == 2: # いろはす
                SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                print("control 2 moving")
                arm_cls.arm_catch()
                arm_cls.arm_put()
            if LOCAL_AI_VALUE == 3: # 手
                # for CONTROL_FORCE_STOP
                print("control 3 hand")
                time.sleep(0.5)
            if LOCAL_AI_VALUE == 4: # その他
                print("control 4 other")
                time.sleep(0.5)
                continue
            if LOCAL_AI_VALUE == None:
                time.sleep(0.5)
                print("control None")
                continue
            arm_cls.arm_empty()
            SHARED_VARIABLE['PREDICTION_VALUE'] = None
            print("control empty")
            SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_EMPTY
    except:
        import traceback
        traceback.print_exc()
    finally:
        arm_cls.arm_empty()
            
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

        # AIモデルファイル名とディレクトリ
        FROZEN_MODEL_NAME="cnn_model.pb"
        MODEL_DIR = "./model"

        # AIモデル読み込み
        graph = load_graph(MODEL_DIR+"/"+FROZEN_MODEL_NAME)
        graph_def = graph.as_graph_def()
        # AI入出力ノード取得
        input_x = graph.get_tensor_by_name('prefix/input_x:0')
        output_y= graph.get_tensor_by_name('prefix/output_y:0')
        step = graph.get_tensor_by_name('prefix/step/step:0')

        n_classes=5 # 出力数(アレルケア,紙コップ,いろはす,手,その他の5種類)

        ####################
        # OpenCV カメラ設定
        ####################

        # OpenCV Webカメラ準備
        #vid = cv2.VideoCapture(0) # WebCam Raspberry Pi3 /dev/video0
        vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
        print(vid.isOpened())
        if not vid.isOpened():
            raise IOError(("Couldn't open video file or webcam. If you're "
                           "trying to open a webcam, make sure you video_path is an integer!"))

        # カメラ画像サイズ
        image_height = 120
        image_width = 160
        image_depth = 3

        vidw = None
        vidh = None
        fps = None
        fourcc = None
        cv_version = cv2.__version__.split(".")
        if cv_version[0] == '2':
            # OpenCV 2.4
            vidw = vid.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, image_width)
            vidh = vid.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, image_height)
            fps = vid.get(cv2.cv.CV_CAP_PROP_FPS)
            fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
        else:
            # OpenCV 3.2
            vidw = vid.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
            vidh = vid.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
            fps = vid.get(cv2.CAP_PROP_FPS)
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')


        SAVE_PREDICTION=True
        PREDICTION_DIR="./prediction"

        if SAVE_PREDICTION:
            if not os.path.exists(PREDICTION_DIR):
                os.makedirs(PREDICTION_DIR)
        
        start_time, start_clock = time.time(), time.clock()

        '''
        AI予測実行
        max_index:N # 0:アレルケア,1:紙コップ,2:いろはす,3:手,4:その他 int型
        '''
        with tf.Session(graph=graph) as sess:
            # CNNモデルの入力値となる画像サイズ
            data_cols=image_height * image_width * image_depth # 160*120*3
            frame_cnt = 0
            learned_step = sess.run(step)
            print("learned_step:{}".format(learned_step))

            # 3回連続で同じ分類になったら確定する
            same_count = 0
            LOCAL_VALUE = None
            prev_time = time.time()
            try:
                ####################
                # ループ実行
                ####################
                while SHARED_VARIABLE['PREDICTION_READY']:
                    
                    if frame_cnt >= 10000:
                        frame_cnt = 0
                        prev_time = time.time()

                    retval, cv_bgr = vid.read()
                    if not retval:
                        print("Done!")
                        SHARED_VARIABLE['PREDICTION_READY']=False
                        break

                    if SHARED_VARIABLE['CONTROL_VALUE'] == CONTROL_EMPTY:
                        image_data = cv_bgr.reshape(1,data_cols)
                        _output_y = sess.run(output_y,feed_dict={input_x:image_data})
                        max_index=np.argmax(_output_y[0])
                        if LOCAL_VALUE == max_index:
                            same_count += 1
                        else:
                            same_count = 0
                        LOCAL_VALUE = max_index
                        if same_count == 3:
                            same_count = 0
                            SHARED_VARIABLE['PREDICTION_VALUE'] = max_index
                        print("prediction:{}".format(max_index)) # 予測クラス 0:アレルケア 1:紙コップ 2:ペットボトル 3:危険待機 4:その他

                        if SAVE_PREDICTION:
                            SAVE_DIR=PREDICTION_DIR+"/"+str(max_index)
                            if not os.path.exists(SAVE_DIR):
                                os.makedirs(SAVE_DIR)
                            cv2.imwrite(SAVE_DIR+"/pred1-"+str(frame_cnt)+".png",cv_bgr)
                    else:
                        print("prediction else")
                        time.sleep(0.5)
                    frame_cnt += 1
            except:
                import traceback
                traceback.print_exc()
            finally:
                curr_time = time.time()
                exec_time = curr_time - prev_time
                print('FPS:{0}'.format(frame_cnt/exec_time))
                print("time:%.8f clock:%.8f" % (time.time() - start_time,time.clock() - start_clock))
                vid.release()

    except:
        import traceback
        traceback.print_exc()
        if not SHARED_VARIABLE['PREDICTION_READY']:
            print('error! PREDICTION_READY is False')
    finally:
        print("prediction finally")
        return





'''
ここはプロセスで実行される
'''
def do_stop():

    ####################
    # ループ実行
    ####################
    start_time = time.time()
    RUNNING_SEC = 300
    time.sleep(RUNNING_SEC)
    SHARED_VARIABLE['CONTROL_READY']=False
    SHARED_VARIABLE['PREDICTION_READY']=False

    return

'''
process pattern
'''
SHARED_VARIABLE=Manager().dict()
SHARED_VARIABLE['CONTROL_READY']=False
SHARED_VARIABLE['CONTROL_VALUE']=CONTROL_EMPTY
SHARED_VARIABLE['PREDICTION_READY']=False
SHARED_VARIABLE['PREDICTION_VALUE']=None

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
