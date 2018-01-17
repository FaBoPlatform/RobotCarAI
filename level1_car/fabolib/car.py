#!/usr/bin/python
# coding: utf-8
# ロボットカー制御クラス

import time
import threading
import logging
from .motor import Motor
from .servo import Servo

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)


class Car():

    motor = None # モーター制御クラスを保持する
    handle = None # ハンドル制御クラスを保持する

    def __init__(self):
        logging.debug("init")

        self.motor = Motor()
        self.handle = Servo()
        HANDLE_NEUTRAL = 90 # ステアリングニュートラル位置
        self.motor.stop()
        self.handle.set_angle(HANDLE_NEUTRAL)
        return

    def set_angle(self,angle):
        self.handle.set_angle(angle)

    def forward(self,speed):
        self.motor.forward(speed)

    def back(self,speed):
        self.motor.back(speed)

    def stop(self):
        self.motor.stop()

    def brake(self):
        self.motor.brake()

