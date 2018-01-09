# coding: utf-8
# 予測精度を評価する

import time
import logging
import threading
import numpy as np
from lib import AI
from generator import SensorGenerator

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


'''
予測の精度評価を行う
'''
def main():
    # AI準備
    ai = AI()
    score = 0.0 # スコア閾値

    # IF準備 (AI学習データジェネレータ)
    generator = SensorGenerator()
    # 近接センサー準備
    kerberos = Kerberos()
    LIDAR_INTERVAL = 0.05

    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        ########################################
        # N回予測を実行し、IF文との不一致数をカウントする
        ########################################
        N=1000
        for i in range(0,N):
            ########################################
            # 近接センサー値を取得する
            ########################################
            '''
            速度、角度制御を入れるので距離はここで取る
            '''
            distance1,distance2,distance3 = kerberos.get_distance()
            sensors = [distance1,distance2,distance3]
            ########################################
            # AI予測結果を取得する
            ########################################
            # 今回の予測結果を取得する
            ai_value = ai.get_prediction(sensors,score)
            ########################################
            # IF結果を取得する
            ########################################
            # 今回の結果を取得する
            w = generator.driving_instruction(sensors)
            if_value = np.argmax(w[0:4])


            print("ai_value:{} {}".format(ai_value,sensors))
            # 予測結果のスコアが低い時は何もしない
            if ai_value == ai.get_other_label():
                time.sleep(LIDAR_INTERVAL)
                continue

            ########################################
            # 速度調整を行う
            ########################################
            if distance2 >= 100:
                speed = 100
            else:
                speed = int(distance2 + (100 - distance2)/2)
                if speed < 40:
                    speed = 40

            ########################################
            # ハンドル角調整を行う
            ########################################
            if ai_value == 1: # 左に行くけど、左右スペース比で舵角を制御する
                ratio = float(distance1)/(distance1 + distance3) # 角度をパーセント減にする
                if distance2 < 75 or distance3 < 8.0 :
                    ratio = 1.0
            elif ai_value == 3: # 右に行くけど、左右スペース比で舵角を制御する
                ratio = float(distance3)/(distance1 + distance3) # 角度をパーセント減にする
                if distance2 < 75 or distance1 < 8.0 :
                    ratio = 1.0
            else:
                ratio = 1.0

            if not FORCE_STOP_THREAD_RUN: break # 強制停止ならループを抜ける
            ########################################
            # ロボットカーを 前進、左右、停止 する
            ########################################
            if ai_value == STOP:
                car.stop()
                car.set_angle(HANDLE_NEUTRAL)
            elif ai_value == LEFT:
                car.set_angle(HANDLE_NEUTRAL - (HANDLE_ANGLE * ratio))
                car.forward(speed)
            elif ai_value == FORWARD:
                car.forward(speed)
                car.set_angle(HANDLE_NEUTRAL)
            elif ai_value == RIGHT:
                car.set_angle(HANDLE_NEUTRAL + (HANDLE_ANGLE * ratio))
                car.forward(speed)

            else:
                if not FORCE_STOP_THREAD_RUN: break # 強制停止ならループを抜ける
                count_stop = 0
                # 前進の時は直前のハンドル操作を記憶する
                qsize = log_queue.qsize()
                if qsize >= max_log_length:
                    log_queue.get(block=False)
                    qsize = log_queue.qsize()
                log_queue.put(ai_value)

            time.sleep(LIDAR_INTERVAL)

    except:
        import traceback
        traceback.print_exc()
        print('error! main failed.')
    finally:
        print("main end")
        # ボタンスレッドを停止させる
        FORCE_STOP_THREAD_RUN = False
        car.stop()
        car.set_angle(HANDLE_NEUTRAL)
        pass

    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_force_stop_button,args=())
    t.start()
    main()
