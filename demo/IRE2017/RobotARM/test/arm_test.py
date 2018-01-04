#!/usr/bin/python
# coding: utf-8 
from __future__ import division

import os
_FILE_DIR=os.path.abspath(os.path.dirname(__file__))

import time
import sys
sys.path.append(_FILE_DIR+'/..')
from lib import ARM

print("start")

arm_cls=ARM()

arm=arm_cls.arm1
HUMAN_INPUT=False
AUTO=True

def main():
    ANGLE=90 # 0-180 degree
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
                arm_cls.start('catch put empty')

                '''
                動作終了まで待機する
                '''
                #arm_cls.wait() # waitだと処理終わりまでCtrl+cによるKeyboardInterruptの例外処理を受け付けず、自身が止まっているので停止命令も受理出来なくなるので使わないことにする。代わりにcallbackを確認する。
                while not arm_cls.checkCallback():
                    time.sleep(1)

    except:
        import traceback
        traceback.print_exc()
    finally:
        #arm_cls.stop()
        #arm_cls.arm_empty()
        #arm_cls.wait()
        pass

main()

print("END")
