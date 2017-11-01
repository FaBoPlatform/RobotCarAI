# coding: utf-8
# アーム動作
# pip install futures

from __future__ import division
import time
from concurrent import futures
import os
from multiprocessing import Manager
import threading
import logging
from arm import ARM
import numpy as np
import tensorflow as tf
import cv2
import FaBoGPIO_PCAL6408

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

CONTROL_MOVING = 1
CONTROL_EMPTY = 0
CONTROL_SHOULD_MOVE = 2
CONTROL_FORCE_STOP = 100

'''
ここはプロセスで実行される
SHARED_VARIABLE['LED_READY']=True であるうちは実行を続ける
'''
def do_led():
    from led import LED
    logging.debug("enter")
    SHARED_VARIABLE['LED_READY']=True

    ####################
    # LED準備
    ####################
    led = LED()
    # SHARED_VARIABLE['LED_VALUE'] == 'stop' を呼ぶ場合は、0.5sec以上のsleepを入れるか、SHARED_VARIABLE['LED_VALUE'] is None:であることを確認してから次に移ること
    try:
        while SHARED_VARIABLE['LED_READY']:
            if SHARED_VARIABLE['LED_VALUE'] is not None:
                print('led: {}'.format(SHARED_VARIABLE['LED_VALUE']))
                led.start(SHARED_VARIABLE['LED_VALUE'])
                SHARED_VARIABLE['LED_VALUE'] = None
            time.sleep(0.01)
                
    except:
        import traceback
        traceback.print_exc()
    finally:
        SHARED_VARIABLE['FORCE_STOP_READY']=False
        SHARED_VARIABLE['CONTROL_READY']=False
        SHARED_VARIABLE['PREDICTION_READY']=False
        SHARED_VARIABLE['LED_READY']=False
        SHARED_VARIABLE['LED_VALUE'] = 'stop'
        led.stop()

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
    arm_cls = ARM()
    arm_cls.start('empty')
    while not arm_cls.checkCallback(): # アームの移動完了を待つ。Ctrl+cによる強制終了を受け付けるためにarm_cls.wait()ではなくarm_cls.checkCallback()でempty処理の終了キューを確認する
        time.sleep(0.5)

    LOCAL_AI_VALUE = None; # 動作時のAI判定結果を保持する。None を初期値とする。
    ####################
    # ループ実行
    ####################
    try:
        while SHARED_VARIABLE['CONTROL_READY']:
            if SHARED_VARIABLE['FORCE_STOP_VALUE']:
                print('control FORCE STOP')
                arm_cls.stop()
                break

            # ARM状態を確認する
            ARM_WORKING = arm_cls.get_status()

            if not ARM_WORKING:
                # ARM停止中なら、前回実行したARMスレッドの実行終了の存在を確認する
                if arm_cls.checkCallback(): # ARMスレッド終了通知キューがあるなら、キューを廃棄する
                    # ARM動作終了したので、ステータス群を初期化する
                    SHARED_VARIABLE['PREDICTION_VALUE'] = None
                    print("control empty")
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_EMPTY
                    SHARED_VARIABLE['LED_VALUE'] = 'stop 0 1 2 3 4 5 6'
                    time.sleep(0.02)
                    continue

                if not SHARED_VARIABLE['CONTROL_VALUE'] == CONTROL_SHOULD_MOVE:
                    # AIプロセスからの動作命令が出ていない時は動作しない
                    time.sleep(0.5)
                    continue

                LOCAL_AI_VALUE = SHARED_VARIABLE['PREDICTION_VALUE']

                if LOCAL_AI_VALUE == 0: # その他
                    print("control "+str(LOCAL_AI_VALUE)+" other")
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_EMPTY
                    time.sleep(0.5)
                    continue
                if LOCAL_AI_VALUE == 1: # ラベル1
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                    SHARED_VARIABLE['LED_VALUE']='blink '+str(LOCAL_AI_VALUE)
                    print("control "+str(LOCAL_AI_VALUE)+" start")
                    arm_cls.start('catch put empty')
                if LOCAL_AI_VALUE == 2: # ラベル2
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                    SHARED_VARIABLE['LED_VALUE']='blink '+str(LOCAL_AI_VALUE)
                    print("control "+str(LOCAL_AI_VALUE)+" start")
                    arm_cls.start('catch put empty')
                if LOCAL_AI_VALUE == 3: # ラベル3
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                    SHARED_VARIABLE['LED_VALUE']='blink '+str(LOCAL_AI_VALUE)
                    print("control "+str(LOCAL_AI_VALUE)+" start")
                    arm_cls.start('catch put empty')
                if LOCAL_AI_VALUE == 4: # ラベル4
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                    SHARED_VARIABLE['LED_VALUE']='blink '+str(LOCAL_AI_VALUE)
                    print("control "+str(LOCAL_AI_VALUE)+" start")
                    arm_cls.start('catch put empty')
                if LOCAL_AI_VALUE == 5: # ラベル5
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                    SHARED_VARIABLE['LED_VALUE']='blink '+str(LOCAL_AI_VALUE)
                    print("control "+str(LOCAL_AI_VALUE)+" start")
                    arm_cls.start('catch put empty')
                if LOCAL_AI_VALUE == 6: # ラベル6
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_MOVING
                    SHARED_VARIABLE['LED_VALUE']='blink '+str(LOCAL_AI_VALUE)
                    print("control "+str(LOCAL_AI_VALUE)+" start")
                    arm_cls.start('catch put empty')
                if LOCAL_AI_VALUE == None:
                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_EMPTY
                    print("control None")
                    time.sleep(0.5)
                    continue
                time.sleep(0.1)
            else: # ARM_RUNNING:
                # アームクラスの返答が動作中の時
                print("control "+str(LOCAL_AI_VALUE)+" moving")
                time.sleep(0.5)
    except:
        import traceback
        traceback.print_exc()
    finally:
        SHARED_VARIABLE['FORCE_STOP_READY']=False
        SHARED_VARIABLE['CONTROL_READY']=False
        SHARED_VARIABLE['PREDICTION_READY']=False
        SHARED_VARIABLE['LED_READY']=False
        if not SHARED_VARIABLE['FORCE_STOP_VALUE']: # 強制停止でなければアームをEMPTYに移動する
            arm_cls.start('empty')
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
        MODEL_DIR = os.path.abspath(os.path.dirname(__file__))+"/model"

        # AIモデル読み込み
        graph = load_graph(MODEL_DIR+"/"+FROZEN_MODEL_NAME)
        graph_def = graph.as_graph_def()
        # AI入出力ノード取得
        input_x = graph.get_tensor_by_name('prefix/input_x:0')
        output_y = graph.get_tensor_by_name('prefix/output_y:0')
        score = graph.get_tensor_by_name('prefix/score:0')
        step = graph.get_tensor_by_name('prefix/step/step:0')
        # モデル読み込み完了のLEDを点灯する
        SHARED_VARIABLE['LED_VALUE']='stop'
        time.sleep(0.5)
        SHARED_VARIABLE['LED_VALUE']='light 7'

        ####################
        # OpenCV カメラ設定
        ####################

        # OpenCV Webカメラ準備
        import platform
        vid = None
        if platform.machine() == 'aarch64':
            vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
        else: # armv7l
            vid = cv2.VideoCapture(0) # WebCam Raspberry Pi3 /dev/video0
        print(vid.isOpened())
        if not vid.isOpened():
            # LEDを全灯する
            SHARED_VARIABLE['LED_VALUE']='lightall'
            time.sleep(5)
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


        SAVE_PREDICTION=False
        PREDICTION_DIR=os.path.abspath(os.path.dirname(__file__))+"/prediction"

        if SAVE_PREDICTION:
            if not os.path.exists(PREDICTION_DIR):
                os.makedirs(PREDICTION_DIR)
        
        start_time, start_clock = time.time(), time.clock()

        '''
        AI予測実行
        max_index:N # 予測クラス 0:その他 1:ラベル1 2:ラベル2 ..
        '''
        with tf.Session(graph=graph) as sess:
            # CNNモデルの入力値となる画像サイズ
            data_cols=image_height * image_width * image_depth # 160*120*3
            frame_cnt = 0
            learned_step = sess.run(step)
            print("learned_step:{}".format(learned_step))

            # N回連続で同じ分類になったら確定する
            same_count = 0
            LAST_VALUE = None
            prev_time = time.time()
            try:
                ####################
                # ループ実行
                ####################
                same_count = 0
                while SHARED_VARIABLE['PREDICTION_READY']:
                    if frame_cnt >= 10000:
                        frame_cnt = 0
                        prev_time = time.time()

                    retval, cv_bgr = vid.read()
                    if not retval:
                        print("Done!")
                        SHARED_VARIABLE['PREDICTION_READY']=False
                        break

                    # アームが動作していなければ物体分類を行う
                    # アームはSLEEPしているため、物体分類中にアームが前回予測結果を動かす可能性がある。そのためSHARED_VARIABLE['PREDICTION_VALUE']に入れる前に再度確認する
                    if SHARED_VARIABLE['CONTROL_VALUE'] == CONTROL_EMPTY:
                        image_data = cv_bgr.reshape(1,data_cols)
                        _output_y,_score = sess.run([output_y,score],feed_dict={input_x:image_data})
                        max_index=np.argmax(_output_y[0])
                        max_score = _score[0][max_index]
                        if SHARED_VARIABLE['CONTROL_VALUE'] == CONTROL_EMPTY:
                            if max_score >= 0.6:
                                # スコアが高い
                                prediction_index = max_index
                                prediction_score = max_score
                                pass
                            else:
                                # スコアが低いのでその他にする
                                prediction_index = 0 # その他
                                prediction_score = _score[0][prediction_index]
                            if LAST_VALUE == prediction_index: # 前回と予測値が同じならsame_count+1
                                same_count += 1
                            else:
                                same_count = 0
                            LAST_VALUE = prediction_index

                            # 分類番号のLEDを消灯する
                            SHARED_VARIABLE['LED_VALUE']='stop 0 1 2 3 4 5 6'
                            time.sleep(0.02)

                            # 分類番号のLEDを点灯する
                            SHARED_VARIABLE['LED_VALUE']='light '+str(prediction_index)

                            if same_count == 3: # N回連続で同じ予測結果なら、予測値として使う
                                same_count = 0
                                if not prediction_index == 0: # 0:その他 以外なら値を使う
                                    SHARED_VARIABLE['PREDICTION_VALUE'] = prediction_index
                                    SHARED_VARIABLE['CONTROL_VALUE'] = CONTROL_SHOULD_MOVE

                            if max_index == prediction_index :
                                print("prediction:{} score{}".format(prediction_index, prediction_score)) # 予測クラス 0:その他 1:ラベル1 2:ラベル2 ..
                                pass
                            else:
                                # スコア未満の時は、予測値も表示する
                                print("prediction:{} score{}, max:{} score{}".format(prediction_index, prediction_score, max_index, max_score)) # 予測クラス 0:その他 1:ラベル1 2:ラベル2 ..
                                pass

                            if SAVE_PREDICTION:
                                SAVE_DIR=PREDICTION_DIR+"/"+str(max_index)
                                if not os.path.exists(SAVE_DIR):
                                    os.makedirs(SAVE_DIR)
                                cv2.imwrite(SAVE_DIR+"/pred1-"+str(frame_cnt)+".png",cv_bgr)
                        else:
                            # 予測結果は出たけど、アームが前回予測結果で動作中のため、実行しない
                            same_count = 0
                            pass
                    else:
                        same_count = 0
                        print("prediction skip. sleep 0.5 sec")
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
            pass
    finally:
        SHARED_VARIABLE['FORCE_STOP_READY']=False
        SHARED_VARIABLE['CONTROL_READY']=False
        SHARED_VARIABLE['PREDICTION_READY']=False
        SHARED_VARIABLE['LED_READY']=False
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

#read SPI from the ADC(MCP3008 chip), 8 possible chanels
def readadc(spi, channel):
    """
    Analog Data Converterの値を読み込む
    @channel チャンネル番号
    """    
    #Writes a list of values to SPI device.
    #bits_per_word: Property that gets / sets the bits per word.
    #xfer2(list of values[, speed_hz, delay_usec, bits_per_word])
    speed_hz = 1
    delay_usec = (8+channel)<<4
    bits_per_word = 0
    to_send = [speed_hz,delay_usec,bits_per_word]
    adc = spi.xfer2(to_send)

    data = ((adc[1]&3) << 8) + adc[2]
    return data

'''
強制停止ボタン
ここはプロセスで実行される
'''
def do_force_stop():
    ####################
    # SPIボタン準備
    ####################
    import spidev

    import platform
    spi = spidev.SpiDev()

    bus = None
    if platform.machine() == 'aarch64':
        bus = 3 # WebCam Jetson TX2 /dev/spidev-3.0
    else: # armv7l
        bus = 0 # WebCam Raspberry Pi3 /dev/spidev0.0
    device=0
    spi.open(bus,device)

    spi.max_speed_hz = 5000
    spi.mode=0b01

    # A0コネクタに機器を接続
    A0 = 0
    SPI_PIN = A0

    SHARED_VARIABLE['FORCE_STOP_READY']=True
    
    ####################
    # ループ実行
    ####################
    try:
        while SHARED_VARIABLE['FORCE_STOP_READY']:
            data = readadc(spi,SPI_PIN) # data: 0-1023
            if data >= 1000:
                print("Button FORCE_STOP!!")
                SHARED_VARIABLE['FORCE_STOP_READY']=False
                SHARED_VARIABLE['FORCE_STOP_VALUE']=True
                #SHARED_VARIABLE['CONTROL_READY']=False
                #SHARED_VARIABLE['PREDICTION_READY']=False
                break
            time.sleep( 0.1 )
    except:
        import traceback
        traceback.print_exc()
        SHARED_VARIABLE['CONTROL_READY']=False
        SHARED_VARIABLE['PREDICTION_READY']=False            
        SHARED_VARIABLE['LED_READY']=False
    finally:
        SHARED_VARIABLE['FORCE_STOP_READY']=False
            
    return


'''
process pattern
'''
SHARED_VARIABLE=Manager().dict()
SHARED_VARIABLE['CONTROL_READY']=False
SHARED_VARIABLE['CONTROL_VALUE']=CONTROL_EMPTY
SHARED_VARIABLE['PREDICTION_READY']=False
SHARED_VARIABLE['PREDICTION_VALUE']=None
SHARED_VARIABLE['FORCE_STOP_READY']=False
SHARED_VARIABLE['FORCE_STOP_VALUE']=False
SHARED_VARIABLE['LED_READY']=False
SHARED_VARIABLE['LED_VALUE']='blink 7' # LED点滅開始

'''
プロセスによる実行関数の振り分け定義
'''
#PROCESS_LIST=['do_control','do_prediction','do_stop','do_force_stop']
PROCESS_LIST=['do_force_stop','do_led','do_control','do_prediction']
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
    if target == 'do_force_stop':
        do_force_stop()
        return "end do_force_stop"
    if target == "do_led":
        do_led()
        return "end do_led"

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
        pass

    return

do_main()
