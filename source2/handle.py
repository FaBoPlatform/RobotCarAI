#!/usr/bin/python
# coding: utf-8 

from __future__ import division
import time
import Adafruit_PCA9685

print("start")

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)

CALIBRATION = 4 # フロントタイヤがまっすぐになりそうな角度に調整
HANDLE_NUTRAL = 375 + CALIBRATION # フロントタイヤがまっすぐの時のサーボ位置
MAX_HANDLE_RIGHT = 150
MAX_HANDLE_LEFT = 600

MAX_HANDLE_ANGLE = 45 # フロントタイヤの左右最大角のサーボ位置
HANDLE_RIGHT = HANDLE_NUTRAL + MAX_HANDLE_ANGLE
HANDLE_LEFT = HANDLE_NUTRAL - MAX_HANDLE_ANGLE

def main():
    try:
        while True:
            # 人力確認
            #ANGLE = int(raw_input('Enter angle: '))
            #HANDLE_RIGHT = HANDLE_NUTRAL + ANGLE
            #HANDLE_LEFT = HANDLE_NUTRAL - ANGLE

            channel = 0
            pwm.set_pwm(channel, 0, HANDLE_RIGHT)
            time.sleep(1)
            pwm.set_pwm(channel, 0, HANDLE_NUTRAL)
            time.sleep(1)
            pwm.set_pwm(channel, 0, HANDLE_LEFT)
            time.sleep(1)
            pwm.set_pwm(channel, 0, HANDLE_NUTRAL)
            time.sleep(5)


    except KeyboardInterrupt:
        pass

main()

pwm.set_pwm(0, 0, HANDLE_NUTRAL)
time.sleep(1)
print("END")
