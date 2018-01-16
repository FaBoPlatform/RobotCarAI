# coding: utf-8
# ロボットカー自走コード

import time
import logging
import threading
import numpy as np
from fabolib import Kerberos
from fabolib import Car
from lib import SPI
from lib import AI
#from generator import LabelGenerator
import copy

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

    # CAR準備
    STOP=0
    LEFT=1
    FORWARD=2
    RIGHT=3
    HANDLE_NEUTRAL = 95 # ステアリングニュートラル位置
    HANDLE_ANGLE = 42 # 左右最大アングル
    car = Car()
    speed = 0
    angle = HANDLE_NEUTRAL
    ratio = 1.0 # 角度制御率

    N_BACK_FOWARD = 5 # バック時、真っ直ぐバックする回数
    MAX_LOG_LENGTH = 20 # ハンドル操作ログの保持数 MAX_LOG_LENGTH > N_BACK_FOWARD
    log_queue = Queue.Queue(maxsize=MAX_LOG_LENGTH) # バック時に使うために行動結果を保持する
    copy_log_queue = Queue.Queue(maxsize=MAX_LOG_LENGTH) # 連続バック動作のためのlog_queueバックアップキュー
    back_queue = Queue.LifoQueue(maxsize=MAX_LOG_LENGTH) # バック方向キュー

    # AI準備
    ai = AI("car_model_100M.pb")
    SCORE = 0.6 # スコア閾値
    # IF準備 (学習ラベル ジェネレータ)
    #generator = LabelGenerator()
    # 近接センサー準備
    kerberos = Kerberos()
    LIDAR_INTERVAL = 0.05

    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        while main_thread_running:
            if not stop_thread_running: break # 強制停止ならループを抜ける

            ########################################
            # 近接センサー値を取得する
            ########################################
            distance1,distance2,distance3 = kerberos.get_distance()
            sensors = [distance1,distance2,distance3]

            ########################################
            # AI予測結果を取得する
            ########################################
            # 今回の予測結果を取得する
            ai_value = ai.get_prediction(sensors,SCORE)

            print("ai_value:{} {}".format(ai_value,sensors))
            # 予測結果のスコアが低い時は何もしない
            if ai_value == ai.get_other_label():
                time.sleep(LIDAR_INTERVAL)
                continue

            ########################################
            # IF結果を取得する
            ########################################
            # 今回の結果を取得する
            #generator_result = generator.get_label(sensors)
            #ai_value = np.argmax(generator_result)

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
                if distance1 > 100: # 左空間が非常に大きい時、ratio制御向けに最大値を設定する
                    distance1 = 100
                if distance3 > distance1: # raitoが1.0を超えないように確認する
                    distance3 = distance1
                ratio = (float(distance1)/(distance1 + distance3) -0.5) * 2 # 角度をパーセント減にする
                if distance2 < 100:
                    ratio = 1.0
            elif ai_value == 3: # 右に行くけど、左右スペース比で舵角を制御する
                if distance3 > 100: # 右空間が非常に大きい時、ratio制御向けに最大値を設定する
                    distance3 = 100
                if distance1 > distance3: # raitoが1.0を超えないように確認する
                    distance3 = distance1
                ratio = (float(distance3)/(distance1 + distance3) -0.5) * 2 # 角度をパーセント減にする
                if distance2 < 100:
                    ratio = 1.0
            else:
                ratio = 1.0

            if not stop_thread_running: break # 強制停止ならループを抜ける
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

            ########################################
            # もし停止なら、ロボットカーを後進する
            ########################################
            '''
            バック時、直前のハンドルログからN件分を真っ直ぐバックし、M件分を逆ハンドルでバックする
            その後、狭い方にハンドルを切ってバックする
            '''
            if ai_value == STOP:
                time.sleep(1) # 停止後1秒、車体が安定するまで待つ
                if not stop_thread_running: break # 強制停止ならループを抜ける

                # バック時のハンドル操作キューを作成する
                copy_log_queue.queue = copy.deepcopy(log_queue.queue)

                # ハンドル操作キューが足りない時はバックハンドル操作を前進にする
                if log_queue.qsize() < MAX_LOG_LENGTH:
                    for i in range(log_queue.qsize(),MAX_LOG_LENGTH):
                        back_queue.put(FORWARD)

                while not log_queue.empty():
                    back_queue.put(log_queue.get(block=False))
                log_queue.queue = copy.deepcopy(copy_log_queue.queue)

                speed = 60
                car.back(speed) # バックする
                ####################
                # N件分を真っ直ぐバックする
                ####################
                for i in range(0,N_BACK_FOWARD):
                    if not stop_thread_running: break # 強制停止ならループを抜ける
                    car.set_angle(HANDLE_NEUTRAL)
                    # N件分をバックハンドル操作キューから削除する
                    back_queue.get(block=False)
                    time.sleep(LIDAR_INTERVAL)

                ####################
                # 残りのログ分のハンドル操作の最大方向をハンドルに設定する
                ####################
                angle = 0 # 左右どちらが多いか
                angle_forward = 0 # 前進方向の回数
                back_queue_size = back_queue.qsize()
                for i in range(0,back_queue_size):
                    value = back_queue.get(block=False)
                    if value == RIGHT:
                        angle += 1
                    elif value == LEFT:
                        angle -= 1
                    elif value == FORWARD:
                        angle_forward +=1
                if angle_forward >= back_queue_size/3: # ハンドルログは前進が多いので真っ直ぐバックする
                    back = FORWARD
                elif angle > 0: # ハンドルログは左が多いので右にバッグする
                    back = RIGHT
                else: # ハンドルログは右が多いので左にバックする
                    back = LEFT
                for i in range(0,back_queue_size):
                    if not stop_thread_running: break # 強制停止ならループを抜ける
                    if back == LEFT:
                        car.set_angle(HANDLE_NEUTRAL + HANDLE_ANGLE) # 直前のハンドル方向とは逆の右にハンドルを切る
                    elif back == RIGHT:
                        car.set_angle(HANDLE_NEUTRAL - HANDLE_ANGLE) # 直前のハンドル方向とは逆の左にハンドルを切る
                    elif back == FORWARD:
                        car.set_angle(HANDLE_NEUTRAL)
                    time.sleep(LIDAR_INTERVAL)

                ####################
                # ここで左,前,右に20cm以上の空きスペースを見つけられない場合はひたすらバックする
                ####################
                speed=60
                car.back(speed) # バックする
                while True:
                    if not stop_thread_running: break # 強制停止ならループを抜ける
                    distance1,distance2,distance3 = kerberos.get_distance()
                    if distance1 > 20 and distance2 > 20 and distance3 > 20:
                        break
                    if distance1 >= distance3*2: # 右の方が圧倒的に狭いので右にハンドルを切る
                        car.set_angle(HANDLE_NEUTRAL + HANDLE_ANGLE) # 右にハンドルを切る
                    elif distance3 >= distance1*2: # 左の方が圧倒的に狭いので左にハンドルを切る
                        car.set_angle(HANDLE_NEUTRAL - HANDLE_ANGLE) # 左にハンドルを切る
                    elif distance1 >= distance3: # 右に少しハンドルを切る
                        ratio = float(distance3)/(distance1 + distance3) # 角度をパーセント減にする
                        car.set_angle(HANDLE_NEUTRAL + HANDLE_ANGLE*ratio) # 右にハンドルを切る
                    elif distance3 >= distance1: # 左に少しハンドルを切る
                        ratio = float(distance1)/(distance1 + distance3) # 角度をパーセント減にする
                        car.set_angle(HANDLE_NEUTRAL - HANDLE_ANGLE*ratio) # 左にハンドルを切る

                    time.sleep(LIDAR_INTERVAL)


                if not stop_thread_running: break # 強制停止ならループを抜ける

                car.stop()
                ai_value = 0
                speed = 0
                time.sleep(0.5) # 停止後0.5秒待つ
                car.set_angle(HANDLE_NEUTRAL)
                time.sleep(0.5) # 停止後ハンドル修正0.2秒待つ
                if not stop_thread_running: break # 強制停止ならループを抜ける
            else:
                if not stop_thread_running: break # 強制停止ならループを抜ける
                # 前進の時は直前のハンドル操作を記憶する
                qsize = log_queue.qsize()
                if qsize >= MAX_LOG_LENGTH:
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
        stop_thread_running = False
        car.stop()
        car.set_angle(HANDLE_NEUTRAL)
        pass

    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_stop_button,args=())
    t.start()
    main()
