#!/usr/bin/python
# coding: utf-8 

from __future__ import division
import time
from arm import ARM

print("start")

arm_cls=ARM()

arm=arm_cls.arm3
HUMAN_INPUT=False
AUTO=True
def main():
    ANGLE=300
    try:
        while True:
            # 人力確認
            if HUMAN_INPUT:
                value = arm.get_angle()
                print(value)
                ANGLE = float(raw_input('Enter angle: '))
                ARM_ANGLE = ANGLE
                arm.set_angle(ARM_ANGLE)

            if AUTO:
                arm_cls.arm_catch()
                #time.sleep(1)
                arm_cls.arm_put()
                #time.sleep(1)
                #arm_release()
                arm_cls.arm_empty()
                time.sleep(2)


            #arm2.set_angle(ANGLE)
            #time.sleep(0.0005)
            
            #if ANGLE >= 300:
            #    STEP=-1
            #if ANGLE <=150:
            #    STEP=+1
            #ANGLE+=STEP

    except KeyboardInterrupt:
        pass
    finally:
        arm_cls.arm_empty()

main()

print("END")
