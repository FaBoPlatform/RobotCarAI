# coding: utf-8
# センサー値から予測を実行する

import time
import logging
import threading
import numpy as np
from lib import Kerberos
from lib import AI

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


# スレッド停止フラグ
STOP_FLAG = False

def do_stop(running_sec):
    '''
    時間が経ったら停止フラグを立てる
    running_sec: スレッド停止フラグを立てるまでの時間(秒)
    '''
    logging.debug("enter")

    time.sleep(running_sec)
    STOP_FLAG = True
    return


def main():
    '''
    予測を実行する
    '''
    # AI準備
    ai = AI()
    # スコア閾値。予測結果がこれより低いスコアの時はその他と見なす。
    score = 0.6

    # 近接センサー準備
    kerberos = Kerberos()
    # Lidar取得間隔(秒)
    LIDAR_INTERVAL = 0.05

    # 予測結果を文字列で保持する
    result = None
    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        ########################################
        # 予測を実行する
        ########################################
        while True:
            if STOP_FLAG:
                break;
            
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
            # 予測結果を文字列に変換する
            ########################################
            if ai_value == STOP:
                result = 'STOP'
            elif ai_value == LEFT:
                result = 'LEFT'
            elif ai_value == FORWARD:
                result = 'FORWARD'
            elif ai_value == RIGHT:
                result = 'RIGHT'

            # 予測結果のスコアが低い時、予測結果の文字列にBAD SCOREを入れる
            if ai_value == ai.get_other_label():
                result = 'BAD SCORE'

            ########################################
            # 予測結果をコンソールに表示する
            ########################################
            sys.stdout.write("result:"+result+" "+str(sensors)+"        \r")
            sys.stdout.flush()

            
            time.sleep(LIDAR_INTERVAL)

    except:
        import traceback
        traceback.print_exc()
        print('error! main failed.')
    finally:
        print("")
        sys.stdout.flush()

        print("main end")
        pass

    return

if __name__ == '__main__':
    # スレッド停止フラグを立てるまでの時間(秒)
    running_sec = 10
    # 停止フラグを立てるスレッドを起動する
    t = threading.Thread(target=do_stop,args=(running_sec))
    t.start()
    main()



