# coding: utf-8
# アーム動作

import time
import logging
import threading
import sys
from arm import ARM
from ai import AI
from spi import SPI
from led import LED

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
# 停止ボタンの値を取得し続ける関数
########################################
def do_stop_button():
    global BUTTON_STATE_RUN
    global MAIN_STATE_RUN

    # 停止ボタン準備
    A0 = 0 # SPI PIN
    STOP_BUTTON_SPI_PIN = A0
    spi = SPI()

    while BUTTON_STATE_RUN:
        data = spi.readadc(STOP_BUTTON_SPI_PIN)
        if data >= 1000:
            # 停止ボタンが押された
            MAIN_STATE_RUN = False
            BUTTON_STATE_RUN = False
            break
        time.sleep(0.1)
    return

'''
メイン処理を行う部分
'''
def main():

    global MAIN_STATE_RUN
    global BUTTON_STATE_RUN

    # LED 準備
    led = LED()
    led.stop()
    led.start('blink 7') # LED点滅開始
    # ARM準備
    arm = ARM()
    # AI準備
    ai = AI()
    score = 0 # スコア閾値
    # WebCam準備
    try:
        ai.init_webcam()
    except:
        import traceback
        traceback.print_exc()
        # WebCamの準備に失敗
        BUTTON_STATE_RUN = False
        led.stop()
        led.start('lightall')
        time.sleep(5)
        sys.exit(0)
    finally:
        led.stop()

    try:
        led.start('light 7')
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        while MAIN_STATE_RUN:
            ########################################
            # AI予測結果を取得する
            ########################################
            same_count = 1 # 連続で同じ結果になった回数を保持する。初回を1回目とカウントする
            last_ai_value = None # 前回の分類結果を保持する
            while same_count < 3: # N回連続で同じ分類になったら確定する
                # 今回の予測結果を取得する
                ai_value = ai.get_prediction(score)
                # 分類番号のLEDを消灯する
                led.start('stop 0 1 2 3 4 5 6')
                time.sleep(0.02)
                # 分類番号のLEDを点灯する
                led.start('light '+str(ai_value))
                print("ai_value:{}".format(ai_value))
                # 前回の予測結果と同じかどうか確認する
                if ai_value == last_ai_value:
                    # 前回の予測結果と同じならsame_countに1を加算する
                    same_count += 1
                else:
                    # 前回の予測結果と違うならsame_countを1に戻す
                    same_count = 1
                # 今回の予測結果をlast_ai_valueに保存する
                last_ai_value = ai_value

            # スコア不足もしくは判定によりその他だった場合、処理を戻す
            if last_ai_value == ai.get_other_label(): # その他
                # 予測結果がその他なら処理を戻す
                continue

            ########################################
            # アームを稼働する
            ########################################
            # 予測番号のLEDを点滅する
            led.start('blink '+str(ai_value))
            # アームでつかむ
            arm.start('catch put empty')
            # アームの処理が終わるまで待機する
            arm.wait()
            # LED点滅を停止する
            led.start('stop 0 1 2 3 4 5 6')

    except:
        import traceback
        traceback.print_exc()
        print('error! main failed.')
    finally:
        print("main end")
        # ボタンスレッドを停止させる
        BUTTON_STATE_RUN = False
        # LEDを消灯する
        led.stop()
        pass

    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_stop_button,args=())
    t.start()
    main()
