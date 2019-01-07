# coding: utf-8
# センサー値を取得し、予測を実行する

import time
import logging
import threading
import numpy as np
#from fabolib import Kerberos
from fabolib import KerberosVL53L0X as Kerberos
from lib import AI

import sys
# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)


# スレッド実行フラグ
run_flag = True

def do_stop(run_sec=10):
    '''
    時間が経ったら実行フラグを落とす
    run_sec: スレッド停止フラグを立てるまでの時間(秒)
    '''
    global run_flag
    logging.debug("enter")

    time.sleep(run_sec)
    run_flag = False
    return


def main():
    '''
    予測を実行する
    '''
    # AI準備
    ai = AI()
    # スコア閾値。予測結果がこれより低いスコアの時はその他と見なす。
    SCORE = 0.6
    STOP = 0
    LEFT = 1
    FORWARD = 2
    RIGHT = 3

    # 距離センサー準備
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
        while run_flag:
            ########################################
            # 距離センサー値を取得する
            ########################################
            distance1,distance2,distance3 = kerberos.get_distance()
            sensors = [distance1,distance2,distance3]
            ########################################
            # AI予測結果を取得する
            ########################################
            # 今回の予測結果を取得する
            ai_value = ai.get_prediction(sensors,SCORE)

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

            # 次のセンサー値更新まで待機する
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
    # スレッド実行フラグを落とすまでの時間(秒)
    RUN_SEC = 10
    # 実行フラグを落とすスレッドを起動する
    t = threading.Thread(target=do_stop,args=(RUN_SEC,))
    t.start()
    main()



