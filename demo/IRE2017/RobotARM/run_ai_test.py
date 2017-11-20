# coding: utf-8
# アーム動作

import time
import logging
import threading
import sys
#from ai import AI
#from ai import SaveConfig
from ai2_dropout import AI
from ai2_dropout import SaveConfig
from spi import SPI
from led import LED

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

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

'''
メイン処理を行う部分
'''
def main():

    global MAIN_THREAD_RUN
    global FORCE_STOP_THREAD_RUN

    # LED 準備
    led = LED()
    led.stop()
    led.start('blink 7') # LED点滅開始
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
    saveConfig = SaveConfig(prefix='fail',label=None,save=True,score=False)
    ai.set_save_config(saveConfig)
    # WebCam準備
    try:
        ai.init_webcam()
    except:
        import traceback
        traceback.print_exc()
        # WebCamの準備に失敗
        FORCE_STOP_THREAD_RUN = False
        led.stop()
        led.start('lightall')
        time.sleep(5)
        led.stop()
        sys.exit(0)
    finally:
        pass

    try:
        led.start('light 7')
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        while MAIN_THREAD_RUN:
            if not FORCE_STOP_THREAD_RUN: break # 強制停止ならループを抜ける

            ########################################
            # AI予測結果を取得する
            ########################################
            same_count = 1 # 連続で同じ結果になった回数を保持する。初回を1回目とカウントする
            last_ai_value = None # 前回の分類結果を保持する
            frame_buffer = 10 # OpenCV フレームバッファサイズ。この分のフレームを廃棄する
            while frame_buffer > 0: # OpenCVカメラ画像が過去のバッファの可能性があるので、その分を廃棄する
                if not FORCE_STOP_THREAD_RUN: break # 強制停止ならループを抜ける
                ai.webcam_capture()
                frame_buffer -= 1
            while same_count < 3: # N回連続で同じ分類になったら確定する
                if not FORCE_STOP_THREAD_RUN: break # 強制停止ならループを抜ける
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

            # LED点滅を停止する
            led.start('stop 0 1 2 3 4 5 6')

    except:
        import traceback
        traceback.print_exc()
        print('error! main failed.')
    finally:
        print("main end")
        # ボタンスレッドを停止させる
        FORCE_STOP_THREAD_RUN = False
        # LEDを消灯する
        led.stop()
        pass

    return

if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_force_stop_button,args=())
    t.start()
    main()
