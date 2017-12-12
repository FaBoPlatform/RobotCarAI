# coding: utf-8
# アーム動作

import os
_FILE_DIR=os.path.abspath(os.path.dirname(__file__))

import time
import logging
import threading
import sys
sys.path.append(_FILE_DIR+'/..')
from lib import AI, SaveConfig
from lib import SPI
import cv2
import math
import numpy as np

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

n_classes = 7 # [その他][ラベル1][ラベル2][ラベル3][ラベル4][ラベル5][ラベル6]
class_max_read = 100000 # 特定のクラスだけが特別に多くのバリエーションがあることを制限する。多くのデータがある状態なら制限の必要はない
image_width = 160
image_height = 120
image_depth = 3
image_bytes = image_width*image_height*image_depth #
data_cols = image_bytes
TEST_DATA_DIR=_FILE_DIR+"/../CNN/test_data2"


########################################
# ステータス
########################################
MAIN_THREAD_RUN = True
FORCE_STOP_THREAD_RUN = True

########################################
# 停止ボタンの値を取得し続ける関数
########################################
def do_force_stop_button():
    global FORCE_STOP_THREAD_RUN
    global MAIN_THREAD_RUN

    # 停止ボタン準備
    A0 = 0 # SPI PIN
    STOP_BUTTON_SPI_PIN = A0
    spi = SPI()

    while FORCE_STOP_THREAD_RUN:
        data = spi.readadc(STOP_BUTTON_SPI_PIN)
        if data >= 1000:
            # 停止ボタンが押された
            MAIN_THREAD_RUN = False
            FORCE_STOP_THREAD_RUN = False
            break
        time.sleep(0.1)
    return


########################################
# ラベル番号をone_hot_valueに変換する
########################################
def toONEHOT(int_label):
    one_hot_value = np.zeros((1,n_classes))
    one_hot_value[np.arange(1),np.array([int_label])] = 1
    return one_hot_value


'''
メイン処理を行う部分
'''
def main():

    global MAIN_THREAD_RUN
    global FORCE_STOP_THREAD_RUN

    # AI準備
    ai = AI()
    score = 0.95 # スコア閾値
    ########################################
    # 結果保存
    ########################################
    # filename: PREFIX_SCORE_NUMBER.png
    # 0番目のラベルしかカメラに映さない前提とすると、
    # label=0,score=False: 不正解を全て保存する
    # label=0,score=True: 不正解を全て保存し、正解であってもスコア未満は保存する
    # label=None,score=False: 全ての結果を保存する
    # label=None,score=True: 全ての結果のうち、スコア未満のみ保存する
    # saveConfig = SaveConfig(prefix='capture',label=0,save=True,score=True) # 正解であってもスコア未満は保存する
    saveConfig = SaveConfig(prefix='fail',label=None,save=False,score=False)
    ai.set_save_config(saveConfig)
    # WebCam準備
    try:
        ai.init_webcam()
    except:
        import traceback
        traceback.print_exc()
        # WebCamの準備に失敗
        FORCE_STOP_THREAD_RUN = False
        sys.exit(0)
    finally:
        pass

    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        imageFormat=1

        ok_count = 0
        ng_count = 0
        file_count = 0
        bad_count = 0 # その他以外での失敗数

        for int_label in range(n_classes):
            label_data = []
            label = str(int_label)
            if not os.path.exists(os.path.join(TEST_DATA_DIR,label)):
                raise ValueError('Failed to label dir: ' + label)

            path=os.path.join(TEST_DATA_DIR, label)
            file_names = sorted(os.listdir(path))
            counter = 0
            for file_name in file_names:
                if not FORCE_STOP_THREAD_RUN: break # 強制停止ならループを抜ける
                start_time = time.time()

                ########################################
                # 画像を読み込む
                ########################################
                cv_bgr = cv2.imread(os.path.join(path, file_name), imageFormat)
                image_data = cv_bgr.reshape(1,data_cols)
                ########################################
                # AI予測結果を取得する
                ########################################
                ai_value = ai.get_prediction(score,cv_bgr)
                end_time = time.time()
                if int_label == ai_value:
                    print("label:ai_value => {}:{} - ok {} time:{:.8f}".format(int_label,ai_value,file_name,end_time-start_time))
                    ok_count += 1
                else:
                    print("label:ai_value => {}:{} - ng {} time:{:.8f}".format(int_label,ai_value,file_name,end_time-start_time))
                    ng_count += 1
                    if not ai_value == ai.get_other_label():
                        bad_count += 1

                file_count += 1


        print("file_count:{} ok:{} ng:{} bad:{}".format(file_count,ok_count,ng_count,bad_count))

    except:
        import traceback
        traceback.print_exc()
        print('error! main failed.')
    finally:
        print("main end")
        # ボタンスレッドを停止させる
        FORCE_STOP_THREAD_RUN = False
        pass

    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_force_stop_button,args=())
    t.start()
    main()
