# coding: utf-8
# センサー値を取得し、予測を実行する
# ジェネレータの結果と比較し、精度を評価する
# 学習範囲外で評価する
# python run_ai_eval.py > eval.log

import time
import logging
import threading
import numpy as np
from lib import AI
from generator import LabelGenerator

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


def print_log(sensors,ai,ai_value,if_value,counter,miss_counter,bad_score_counter,log=True):
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

    if log:
        print("accuracy:"+str((counter-miss_counter)/(counter*1.0))+" total:"+str(counter)+" miss:"+str(miss_counter)+" bad score:"+str(bad_score_counter)+" result:"+result+" "+str(sensors)+" - "+suffix)
    else:
        # '\r': ラインの先頭にカーソルを置く
        # '\r\033[K': ラインの全ての文字を消す
        # stderrの現在の行に上書きする
        sys.stderr.write('\r\033[K'+"accuracy:"+str((counter-miss_counter)/(counter*1.0))+" total:"+str(counter)+" miss:"+str(miss_counter)+" bad score:"+str(bad_score_counter)+" result:"+result+" "+str(sensors)+" - "+suffix)

        sys.stderr.flush()

    return


def main():
    '''
    予測を実行する
    '''
    # AI準備
    ai = AI("car_model.pb")
    # スコア閾値。予測結果がこれより低いスコアの時はその他と見なす。
    SCORE = 0.6

    # IF準備 (AI学習データジェネレータ)
    generator = LabelGenerator()

    # 評価した回数をカウント
    counter = 0
    # 低スコアの回数をカウント
    bad_score_counter = 0
    # 予測結果とジェネレータ結果が異なる回数をカウント(低スコアの回数も含む)
    miss_counter = 0
    # 評価する距離範囲
    MIN_RANGE = 0
    MAX_RANGE = 200
    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        ########################################
        # 距離センサー値を生成する
        ########################################
        sensors=[]
        for distance1 in range(MIN_RANGE,MAX_RANGE):
            for distance2 in range(MIN_RANGE,MAX_RANGE):
                for distance3 in range(MIN_RANGE,MAX_RANGE):
                    sensors.append([distance1,distance2,distance3])
            if (distance1+1) % 10 == 0:
                sensors=np.array(sensors)

                ########################################
                # AI予測結果を取得する
                ########################################
                # 今回の予測結果を取得する
                ai_values = ai.get_predictions(sensors,SCORE)

                n_rows = len(sensors)
                for i in range(n_rows):
                    counter +=1
                    # 予測結果のスコアが低かった回数をカウントする
                    if ai_values[i] == ai.get_other_label():
                        bad_score_counter += 1

                    ########################################
                    # IF結果を取得する
                    ########################################
                    # 今回の結果を取得する
                    generator_result = generator.get_label(sensors[i])
                    if_value = np.argmax(generator_result)

                    # 予測結果とジェネレータ結果が異なった回数をカウントする
                    if not if_value == ai_values[i]:
                        miss_counter += 1
                        # 不一致の予測結果をコンソールに表示する
                        print_log(sensors[i],ai,ai_values[i],if_value,counter,miss_counter,bad_score_counter)

                    ########################################
                    # 定期的に予測結果をコンソールに表示する
                    ########################################
                    if counter % 10000 == 0:
                        print_log(sensors[i],ai,ai_values[i],if_value,counter,miss_counter,bad_score_counter,log=False)
                # sensorsを初期化する
                sensors=[]
    except:
        import traceback
        traceback.print_exc()
        print('error! main failed.')
    finally:
        print("accuracy:"+str((counter-miss_counter)/(counter*1.0))+" total:"+str(counter)+" miss:"+str(miss_counter)+" bad score:"+str(bad_score_counter))
        print("main end")
        pass

    return

if __name__ == '__main__':
    main()



