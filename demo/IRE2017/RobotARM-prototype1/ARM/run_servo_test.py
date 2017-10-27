#!/usr/bin/python
# coding: utf-8 

from __future__ import division
import time
from servo import Servo
print("start")

bus=1
channel=0 # arm1 つまみ関節 #PWM=0
arm1 = Servo(bus,channel)
arm1.SERVO_MIN_ANGLE_VALUE = 0
arm1.SERVO_MAX_ANGLE_VALUE = 600
arm1.SERVO_NEUTRAL_ANGLE_VALUE = 300 # つまみが若干開いた時のサーボ位置
arm1.SERVO_SPEED=10 # 角速度
ARM1_CLOSE=280 # 金属アーム:380 試作アーム:280 閉じた状態
ARM1_OPEN=320 # 金属アーム:250 試作アーム:320 開いた状態
ARM1_CATCH=275 # 金属アーム:330 試作アーム:275 キャッチの状態

AUTO=True
def main():
    ANGLE=300
    try:
        while True:

            if AUTO:
                arm1.set_angle(ARM1_OPEN)
                time.sleep(1)
                arm1.set_angle(ARM1_CLOSE)
                time.sleep(2)

    except:
        import traceback
        traceback.print_exc()
    finally:
        pass

main()

print("END")
