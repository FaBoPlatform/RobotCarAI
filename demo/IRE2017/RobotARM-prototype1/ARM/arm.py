#!/usr/bin/python
# coding: utf-8 

from __future__ import division
import time
from servo import Servo
import threading


class ARM(threading.Thread):
    CONTROL_MOVING = 1 # アームが動作時のSATUS値
    CONTROL_EMPTY = 0 # アームが停止時のSTATUS値
    CONTROL_FORCE_STOP = 2 # アームを強制停止する時のSTATUS値
    CONTROL_STATUS = CONTROL_EMPTY # アーム動作状態定義

    # アーム動作パターン番号定義
    RUN_EMPTY = 0
    RUN_CATCH_AND_PUT = 1
    RUN_PATTERN = RUN_EMPTY

    bus=1
    channel=0 # arm1 つまみ関節 #PWM=0
    arm1 = Servo(bus,channel)
    arm1.SERVO_MIN_ANGLE_VALUE = 0
    arm1.SERVO_MAX_ANGLE_VALUE = 600
    arm1.SERVO_NEUTRAL_ANGLE_VALUE = 300 # つまみが若干開いた時のサーボ位置
    arm1.SERVO_SPEED=10 # 角速度
    ARM1_CLOSE=255 # 金属アーム:380 試作アーム:255 閉じた状態
    ARM1_OPEN=300 # 金属アーム:250 試作アーム:300 開いた状態
    ARM1_CATCH=265 # 金属アーム:330 試作アーム:265 キャッチの状態
    #arm1.neutral()

    channel=1 # arm2 手首関節 #PWM=1
    arm2 = Servo(bus,channel)
    arm2.SERVO_MIN_ANGLE_VALUE = 0
    arm2.SERVO_MAX_ANGLE_VALUE = 600
    arm2.SERVO_NEUTRAL_ANGLE_VALUE = 300 # 手首の通常時のサーボ位置
    arm2.SERVO_SPEED = 10 # 角速度
    ARM2_EMPTY=arm2.SERVO_NEUTRAL_ANGLE_VALUE # 閉じた状態
    ARM2_LIFT=210 # 金属アーム:200 試作アーム:210 持ち上げの状態
    ARM2_CATCH=155 # 金属アーム:150 試作アーム:155 キャッチの状態
    #arm2.neutral()

    channel=2 # arm3 胴体関節 #PWM=2
    arm3 = Servo(bus,channel)
    arm3.SERVO_MIN_ANGLE_VALUE = 0
    arm3.SERVO_MAX_ANGLE_VALUE = 600
    arm3.SERVO_NEUTRAL_ANGLE_VALUE = 290 # 胴体の通常時のサーボ位置
    arm3.SERVO_SPEED = 10 # 角速度
    ARM3_EMPTY=arm3.SERVO_NEUTRAL_ANGLE_VALUE # 前向きの状態
    ARM3_CATCH=290 # 金属アーム: 試作アーム:290 キャッチの状態
    ARM3_PUT=180 # 金属アーム: 試作アーム:180 持ち上げの状態
    #arm3.neutral()

    ARM1_STATUS=0 # 0:close, 1:open, 2:catch
    ARM2_STATUS=0 # 0:empty, 1:catch, 2:lift
    ARM3_STATUS=0 # 0:empty, 1:catch, 2:put

    DELAY=2 # 各動作間隔の遅延を延ばす


    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  args=args, verbose=verbose)
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self.callback_bucket = args
        self.kwargs = kwargs
        return

    def arm_empty(self):
        print("ARM empty()")
        '''
        アームを初期位置に移動する
        '''
        if not self.arm1.get_angle() == self.ARM1_OPEN:
            self.arm1.set_angle(self.ARM1_OPEN)
            self.ARM1_STATUS=1
            time.sleep(0.5*self.DELAY)
        if not self.arm2.get_angle() == self.ARM2_EMPTY:
            self.arm2.set_angle(self.ARM2_EMPTY)
            self.ARM2_STATUS=0
            time.sleep(0.5*self.DELAY)
        if not self.arm1.get_angle() == self.ARM1_CLOSE:
            self.arm1.set_angle(self.ARM1_CLOSE)
            self.ARM1_STATUS=0
            time.sleep(0.5*self.DELAY)
        if not self.arm3.get_angle() == self.ARM3_EMPTY:
            self.arm3.set_angle(self.ARM3_EMPTY)
            self.ARM3_STATUS=0
            time.sleep(0.5*self.DELAY)
        return
    def arm_catch(self):
        print("ARM catch()")
        '''
        ARM2が降りたままARM3をCATCH位置に動かすと、ターゲットにぶつける可能性があるため、
        必ずarm_empty()状態であること
            '''
        if not self.arm3.get_angle() == self.ARM3_CATCH:
            self.arm3.set_angle(self.ARM3_CATCH)
            self.ARM3_STATUS=1
            time.sleep(0.5*self.DELAY)
        if not self.arm1.get_angle() == self.ARM1_OPEN:
            self.arm1.set_angle(self.ARM1_OPEN)
            self.ARM1_STATUS=1
            time.sleep(0.5*self.DELAY)
        if not self.arm2.get_angle() == self.ARM2_CATCH:
            self.arm2.set_angle(self.ARM2_CATCH)
            self.ARM2_STATUS=1
            time.sleep(0.5*self.DELAY)
        if not self.arm1.get_angle() == self.ARM1_CATCH:
            self.arm1.set_angle(self.ARM1_CATCH)
            self.ARM1_STATUS=2
            time.sleep(0.5*self.DELAY)
        if not self.arm2.get_angle() == self.ARM2_LIFT:
            self.arm2.set_angle(self.ARM2_LIFT)
            self.ARM2_STATUS=2
            time.sleep(0.5*self.DELAY)
        return
    def arm_release(self):
        print("ARM release()")
        '''
        その場に高さ0でリリースする
        '''
        if not self.arm2.get_angle() == self.ARM2_CATCH+7:
            self.arm2.set_angle(self.ARM2_CATCH+7)
            self.ARM2_STATUS=1
            time.sleep(0.5*self.DELAY)
        if not self.arm1.get_angle() == self.ARM1_OPEN:
            self.arm1.set_angle(self.ARM1_OPEN)
            self.ARM1_STATUS=1
            time.sleep(0.5*self.DELAY)
        if not self.arm2.get_angle() == self.ARM2_EMPTY:
            self.arm2.set_angle(self.ARM2_EMPTY)
            self.ARM2_STATUS=0
            time.sleep(0.5*self.DELAY)
        return
    def arm_put(self):
        print("ARM put()")
        '''
        台の上に置く
        '''
        if not self.arm3.get_angle() == self.ARM3_PUT:
            self.arm3.set_angle(self.ARM3_PUT)
            self.ARM3_STATUS=2
            time.sleep(0.5*self.DELAY)
        if not self.arm2.get_angle() == self.ARM2_CATCH+30:
            self.arm2.set_angle(self.ARM2_CATCH+30)
            self.ARM2_STATUS=1
            time.sleep(0.5*self.DELAY)
        if not self.arm1.get_angle() == self.ARM1_OPEN:
            self.arm1.set_angle(self.ARM1_OPEN)
            self.ARM1_STATUS=1
            time.sleep(0.5*self.DELAY)
        if not self.arm2.get_angle() == self.ARM2_EMPTY:
            self.arm2.set_angle(self.ARM2_EMPTY)
            self.ARM2_STATUS=0
            time.sleep(0.5*self.DELAY)
        return

    # ステータス設定 強制停止用
    def set_status(self, status):
        self.CONTROL_STATUS = status
        return True
    # ステータス取得 外部呼び出し用
    def get_status(self):
        return self.CONTROL_STATUS

    # ステータス書き換え アーム動作/停止状態更新用
    def set_status_if_control_is(self, before_status, after_status):
        with self.lock:
            print("before_status:{} after_status:{}".format(before_status,after_status))
            if self.CONTROL_STATUS == before_status:
                self.CONTROL_STATUS = after_status
                print("change status - ok")
                return True
            elif self.CONTROL_STATUS == after_status:
                print("change status - already")
            else:
                print("change status - ng")
                return False

    # キャッチ用動作をスレッド設定
    def run_catch_and_put(self):
        if not self.isAlive():
            self.set_status_if_control_is(self.CONTROL_EMPTY,self.CONTROL_MOVING)
            self.RUN_PATTERN = self.RUN_CATCH_AND_PUT
            return True
        else:
            print("skip run_catch_and_put(). because arm is moving.")
            return False

    # EMPTY用動作をスレッド設定
    def run_empty(self):
        if not self.isAlive():
            self.set_status_if_control_is(self.CONTROL_EMPTY,self.CONTROL_MOVING)
            self.RUN_PATTERN = self.RUN_EMPTY
            return True
        else:
            print("skip run_empty(). because arm is moving.")
            return False

    def force_stop(self):
        print("ARM force_stop()")
        self.set_status(self.CONTROL_FORCE_STOP)
        # スレッド実行中ならスレッドを停止する
        if self.isAlive():
            self._stop_event.set()
        else:
            print("ARM no thread is Alive")

    def run(self): # 一度しか実行できないため、lockは不要
        print("enter run()")
        self.set_status_if_control_is(self.CONTROL_EMPTY,self.CONTROL_MOVING)

        if self.RUN_PATTERN == self.RUN_EMPTY:
            print("run empty")
            self.arm_empty()
        elif self.RUN_PATTERN == self.RUN_CATCH_AND_PUT:
            print("run catch and put")
            self.arm_catch()
            self.arm_put()
            self.arm_empty()

        print("exit run()")
        self.set_status_if_control_is(self.CONTROL_MOVING,self.CONTROL_EMPTY)
        self.callback_bucket.put('0')
