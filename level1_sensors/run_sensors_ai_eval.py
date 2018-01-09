# coding: utf-8
# センサー値を取得し、予測を実行する
# ジェネレータの結果と比較し、精度を評価する

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


def print_log(sensors,ai,ai_value,if_value,counter,miss_counter,bad_score_counter,keep=False):
    '''
    コンソールに表示する
    '''
    ########################################
    # 予測結果を文字列に変換する
    ########################################
    if ai_value == 0:
        result = 'STOP'
    elif ai_value == 1:
        result = 'LEFT'
    elif ai_value == 2:
        result = 'FORWARD'
    elif ai_value == 3:
        result = 'RIGHT'

    # 予測結果のスコアが低い時、予測結果の文字列にBAD SCOREを入れる
    if ai_value == ai.get_other_label():
        result = 'BAD SCORE'

    # 予測結果とジェネレータ結果が同じならok、異なるならngを付ける
    if if_value == ai_value:
        suffix = 'ok'
    else:
        suffix = 'ng'
        if if_value == 0:
            suffix += ' generator:STOP'
        elif if_value == 1:
            suffix += ' generator:LEFT'
        elif if_value == 2:
            suffix += ' generator:FORWARD'
        elif if_value == 3:
            suffix += ' generator:RIGHT'

    sys.stdout.write("accuracy:"+str((counter-miss_counter)/(counter*1.0))+" total:"+str(counter)+" miss:"+str(miss_counter)+" bad score:"+str(bad_score_counter)+" result:"+result+" "+str(sensors)+" - "+suffix+"                \r")
    sys.stdout.flush()
    if keep:
        print("")
        sys.stdout.flush()

    return


def main():
    '''
    予測を実行する
    '''
    # AI準備
    ai = AI()
    # スコア閾値。予測結果がこれより低いスコアの時はその他と見なす。
    score = 0.6

    # IF準備 (AI学習データジェネレータ)
    generator = SensorGenerator()

    # 評価した回数をカウント
    counter = 0
    # 低スコアの回数をカウント
    bad_score_counter = 0
    # 予測結果とジェネレータ結果が異なる回数をカウント(低スコアの回数も含む)
    miss_counter = 0
    # 評価する距離範囲
    min_range = 0
    max_range = 200
    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        ########################################
        # 近接センサー値を生成する
        ########################################
        for distance1 in range(min_range,max_range):
            for distance2 in range(min_range,max_range):
                sensors=[]
                for distance3 in range(min_range,max_range):
                    sensors = [distance1,distance2,distance3]
                    counter +=1

                    ########################################
                    # AI予測結果を取得する
                    ########################################
                    # 今回の予測結果を取得する
                    ai_value = ai.get_prediction(sensors,score)

                    # 予測結果のスコアが低かった回数をカウントする
                    if ai_value == ai.get_other_label():
                        bad_score_counter += 1

                    ########################################
                    # IF結果を取得する
                    ########################################
                    # 今回の結果を取得する
                    w = generator.driving_instruction(sensors)
                    if_value = np.argmax(w[0:4])

                    # 予測結果とジェネレータ結果が異なった回数をカウントする
                    if not if_value == ai_value:
                        miss_counter += 1
                        print_log(sensors,ai,ai_value,if_value,counter,miss_counter,bad_score_counter,True)

                    ########################################
                    # 予測結果をコンソールに表示する
                    ########################################
                    if counter % 1000 == 0:
                        print_log(sensors,ai,ai_value,if_value,counter,miss_counter,bad_score_counter)

    except:
        import traceback
        traceback.print_exc()
        print('error! main failed.')
    finally:
        sys.stdout.write("accuracy:"+str((counter-miss_counter)/(counter*1.0))+" total:"+str(counter)+" miss:"+str(miss_counter)+" bad score:"+str(bad_score_counter)+"                \r")
        sys.stdout.flush()
        print("")
        sys.stdout.flush()

        print("main end")
        pass

    return

if __name__ == '__main__':
    main()



