# coding: utf-8
# アーム動作

import time
import logging
import threading
from arm import ARM
from ai import AI
from spi import SPI

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

########################################
# ステータス
########################################
BUTTON_STATE_RUN = True
MAIN_STATE_RUN = True

########################################
# ARMとAI準備
########################################
# ARM準備
arm = ARM()
# AI準備
ai = AI()
ai.init_webcam()
# 停止ボタン準備
A0 = 0 # SPI PIN
STOP_BUTTON_SPI_PIN = A0
spi = SPI()

########################################
# 停止ボタンの値を取得し続ける関数
########################################
def do_stop_button():
    global BUTTON_STATE_RUN
    global MAIN_STATE_RUN
    while BUTTON_STATE_RUN:
        data = spi.readadc(STOP_BUTTON_SPI_PIN)
        if data >= 1000:
            # 停止ボタンが押された
            MAIN_STATE_RUN = False
            BUTTON_STATE_RUN = False
            break
        time.sleep(0.1)
            
        
'''
メイン処理を行う部分
'''
def main():
    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        while MAIN_STATE_RUN:
            ########################################
            # AI予測結果を取得する
            ########################################
            same_count = 0 # 連続で同じ結果になった回数を保持する
            last_ai_value = None # 前回の分類結果を保持する
            while same_count < 3: # N回連続で同じ分類になったら確定する
                # 今回の予測結果を取得する
                ai_value = ai.get_prediction()
                print("ai_value:{}".format(ai_value))
                # 前回の予測結果と同じかどうか確認する
                if ai_value == last_ai_value:
                    # 前回の予測結果と同じならsame_countに1を加算する
                    same_count += 1
                else:
                    # 前回の予測結果と違うならsame_countを0に戻す
                    same_count = 0
                # 今回の予測結果をlast_ai_valueに保存する
                last_ai_value = ai_value

            # スコア不足もしくは判定によりその他だった場合、処理を戻す
            if last_ai_value == ai.get_other_label(): # その他
                # 予測結果がその他なら処理を戻す
                continue

            ########################################
            # アームを稼働する
            ########################################
            # アームでつかむ
            arm.start('catch put empty')
            # アームの処理が終わるまで待機する
            arm.wait()

    except:
        import traceback
        traceback.print_exc()
        print('error! main failed.')
    finally:
        print("main end")
        pass

    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_stop_button,args=())
    t.start()
    main()
