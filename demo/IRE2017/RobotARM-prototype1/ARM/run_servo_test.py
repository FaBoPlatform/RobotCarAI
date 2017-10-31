#!/usr/bin/python
# coding: utf-8 

from __future__ import division
import time
from servo import Servo
print("start")

bus=1
channel=2 # 胴体関節稼働値 PWM=2 胴体関節は0-180度の可動域を確保できるので、サーボ動作確認はこれを使う
arm = Servo(bus,channel)

AUTO=True
def main():
    ANGLE=90 # 0-180 degree
    try:
        print("angle:{}".format(arm.get_angle()))
        while True:
            if AUTO:
                v = 180
                arm.set_angle(v)
                print("angle:{}".format(arm.get_angle()))

                time.sleep(1)
                v = 0
                arm.set_angle(v)
                print("angle:{}".format(arm.get_angle()))

                time.sleep(2)

    except:
        import traceback
        traceback.print_exc()
    finally:
        pass

main()

print("END")
