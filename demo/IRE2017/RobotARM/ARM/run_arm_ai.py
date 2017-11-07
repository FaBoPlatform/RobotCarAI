# coding: utf-8
# アーム動作

import time
import logging
from arm import ARM
from ai import AI

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

########################################
# ARMとAI準備
########################################
# ARM準備
arm = ARM()
# AI準備
ai = AI()
ai.init_webcam()

'''
メイン処理を行う部分
'''
def main():
    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        while True:
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
    main()
