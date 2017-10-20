#!/usr/bin/python
# coding: utf-8 

from __future__ import division
import time
from servo import Servo

class ARM():
    bus=1
    channel=0 # arm1 つまみ関節 #PWM=0
    arm1 = Servo(bus,channel)
    arm1.SERVO_MIN_ANGLE_VALUE = 0
    arm1.SERVO_MAX_ANGLE_VALUE = 600
    arm1.SERVO_NEUTRAL_ANGLE_VALUE = 300 # つまみが若干開いた時のサーボ位置
    arm1.SERVO_SINGLESHOT_ANGLE_VALUE = 10
    ARM1_CLOSE=285 # 金属アーム:380 試作アーム:285 閉じた状態
    ARM1_OPEN=320 # 金属アーム:250 試作アーム:320 開いた状態
    ARM1_CATCH=285 # 金属アーム:330 試作アーム:285 キャッチの状態
    ARM1_SPEED=10
    arm1.neutral()

    channel=1 # arm2 手首関節 #PWM=1
    arm2 = Servo(bus,channel)
    arm2.SERVO_MIN_ANGLE_VALUE = 0
    arm2.SERVO_MAX_ANGLE_VALUE = 600
    arm2.SERVO_NEUTRAL_ANGLE_VALUE = 300 # 手首の通常時のサーボ位置
    arm2.SERVO_SINGLESHOT_ANGLE_VALUE = 10
    ARM2_EMPTY=arm2.SERVO_NEUTRAL_ANGLE_VALUE # 閉じた状態
    ARM2_LIFT=250 # 金属アーム:200 試作アーム:250 持ち上げの状態
    ARM2_CATCH=180 # 金属アーム:150 試作アーム:180 キャッチの状態
    ARM2_SPEED=10
    arm2.neutral()

    channel=2 # arm3 胴体関節 #PWM=2
    arm3 = Servo(bus,channel)
    arm3.SERVO_MIN_ANGLE_VALUE = 0
    arm3.SERVO_MAX_ANGLE_VALUE = 600
    arm3.SERVO_NEUTRAL_ANGLE_VALUE = 300 # 胴体の通常時のサーボ位置
    arm3.SERVO_SINGLESHOT_ANGLE_VALUE = 10
    ARM3_EMPTY=arm3.SERVO_NEUTRAL_ANGLE_VALUE # 前向きの状態
    ARM3_CATCH=300 # 金属アーム: 試作アーム:300 キャッチの状態
    ARM3_PUT=180 # 金属アーム: 試作アーム:180 持ち上げの状態
    ARM3_SPEED=10
    arm3.neutral()

    ARM1_STATUS=0 # 0:close, 1:open, 2:catch
    ARM2_STATUS=0 # 0:empty, 1:catch, 2:lift


    DELAY=2 # 各動作間隔の遅延を延ばす
    def arm_empty(self):
        self.ARM1_STATUS=1
        self.arm1.set_angle_with_speed(self.ARM1_OPEN,self.ARM1_SPEED)
        time.sleep(0.5*self.DELAY)
        self.ARM2_STATUS=0
        self.arm2.set_angle_with_speed(self.ARM2_EMPTY,self.ARM2_SPEED)
        time.sleep(0.5*self.DELAY)
        self.ARM1_STATUS=0
        self.arm1.set_angle_with_speed(self.ARM1_CLOSE,self.ARM1_SPEED)
        time.sleep(0.5*self.DELAY)
        self.arm3.set_angle_with_speed(self.ARM3_EMPTY,self.ARM3_SPEED)
        time.sleep(0.5*self.DELAY)
        return
    def arm_catch(self):
        '''必ずarm_empty()状態であること'''
        self.arm3.set_angle_with_speed(self.ARM3_CATCH,self.ARM3_SPEED)
        time.sleep(0.5*self.DELAY)
        self.ARM1_STATUS=1
        self.arm1.set_angle_with_speed(self.ARM1_OPEN,self.ARM1_SPEED)
        self.ARM2_STATUS=1
        time.sleep(0.5*self.DELAY)
        self.arm2.set_angle_with_speed(self.ARM2_CATCH,self.ARM2_SPEED)
        time.sleep(0.5*self.DELAY)
        self.ARM1_STATUS=2
        self.arm1.set_angle_with_speed(self.ARM1_CATCH,self.ARM1_SPEED)
        time.sleep(0.5*self.DELAY)
        self.ARM2_STATUS=2
        self.arm2.set_angle_with_speed(self.ARM2_LIFT,self.ARM2_SPEED)
        time.sleep(0.5*self.DELAY)
        return
    def arm_release(self):
        '''
        その場に高さ0でリリースする
        '''
        self.ARM2_STATUS=1
        self.arm2.set_angle_with_speed(self.ARM2_CATCH+7,self.ARM2_SPEED)
        time.sleep(0.5*self.DELAY)
        self.ARM1_STATUS=1
        self.arm1.set_angle_with_speed(self.ARM1_OPEN,self.ARM1_SPEED)
        time.sleep(0.5*self.DELAY)
        self.arm2.set_angle_with_speed(self.ARM2_EMPTY,self.ARM2_SPEED)
        time.sleep(0.5*self.DELAY)

        return
    def arm_put(self):
        '''
        台の上に置く
        '''
        self.arm3.set_angle_with_speed(self.ARM3_PUT,self.ARM3_SPEED)
        time.sleep(0.5*self.DELAY)
        self.ARM2_STATUS=1
        self.arm2.set_angle_with_speed(self.ARM2_CATCH+30,self.ARM2_SPEED)
        time.sleep(0.5*self.DELAY)
        self.ARM1_STATUS=1
        self.arm1.set_angle_with_speed(self.ARM1_OPEN,self.ARM1_SPEED)
        time.sleep(0.5*self.DELAY)
        self.arm2.set_angle_with_speed(self.ARM2_EMPTY,self.ARM3_SPEED)
        time.sleep(0.5*self.DELAY)

        return
