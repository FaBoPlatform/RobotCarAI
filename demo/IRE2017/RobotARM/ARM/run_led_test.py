# coding: utf-8 
import time
import sys
from led import LED

print("start")
try:
    led = LED()
    led.start('light0to7') # ここは新規スレッドで実行されるため、終了を待たずにすぐに次に進む。スレッドではlockを取得してからの動作になる。forループとsleepによる動作のため、すぐには終わらない
    led.start('blink 0 2 5 7') # ここは新規スレッドで実行されるため、すぐに次に進む。スレッドではlockを取得してからの動作になるため、light0to7の終了を待ってから実行される。while無限ループとsleepによる動作のため、stopを受けるまで終わらない
    time.sleep(12) # ここはlight0to7とblinkの終了を待たずに来るため、長めに取ってある
    led.stop() # ここはLED停止を待ってから次に進む。他スレッドへの停止フラグはすぐに立つが、他スレッドが開放したlockを取得後に消灯する。他スレッドはsleep明けにlockを開放するため、すぐには消灯しない。
    led.start('light 0') # ここは新規スレッドで実行されるため、すぐに次に進む。スレッドではlockを取得してからの動作になる。
    time.sleep(2)
    led.stop()
    time.sleep(0.5)
    led.start('lightall')
    time.sleep(2)
    led.start('stop 1 3 4 6')
    time.sleep(2)
    led.stop()
    led.start('light 1 3 4 6')
    time.sleep(2)
    led.stop()
    led.start('lightline')
    time.sleep(5)
    led.stop()
    
except:
    import traceback
    traceback.print_exc()
finally:
    pass

print("end")
