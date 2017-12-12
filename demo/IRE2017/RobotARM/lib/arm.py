#!/usr/bin/python
# coding: utf-8 

from __future__ import division
import time
from .servo import Servo, ServoConfig
import threading

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    import Queue
elif PY3:
    import queue as Queue

class ARM():
    STOP_PATTERN = False

    CONTROL_MOVING = 1 # アームが動作時のSATUS値
    CONTROL_EMPTY = 0 # アームが停止時のSTATUS値
    CONTROL_FORCE_STOP = 2 # アームを強制停止する時のSTATUS値
    CONTROL_STATUS = CONTROL_EMPTY # アーム動作状態定義

    # つまみ関節稼働値
    ARM1_CLOSE=62 # 初期位置[0-180] 試作アーム:62
    ARM1_OPEN=90  # 開いた状態[0-180] 試作アーム:90
    ARM1_CATCH=60 # キャッチ[0-180] 試作アーム:60

    # 手首関節可動値
    ARM2_EMPTY=80 # 初期位置[0-180] 試作アーム:80
    ARM2_LIFT=45  # 持ち上げ[0-180] 試作アーム:45
    ARM2_CATCH=10 # キャッチ[0-180] 試作アーム:10

    # 胴体関節稼働値
    ARM3_EMPTY=90 # 初期位置[0-180] 試作アーム:90
    ARM3_CATCH=90 # キャッチ[0-180] 試作アーム:90
    ARM3_PUT=30   # 置く位置[0-180] 試作アーム:30

    ARM1_STATUS=0 # 0:close, 1:open, 2:catch
    ARM2_STATUS=0 # 0:empty, 1:catch, 2:lift
    ARM3_STATUS=0 # 0:empty, 1:catch, 2:put

    DELAY=2 # 各動作間隔の遅延を延ばす


    def __init__(self):
        self.lock = threading.Lock()
        self.callback_queue = Queue.Queue()
        self.pattern_queue = Queue.Queue() # コマンド動作スレッド保持 停止処理用

        bus=1
        channel=0 # arm1 つまみ関節 #PWM=0
        self.arm1 = Servo(bus,channel)
        channel=1 # arm2 手首関節 #PWM=1
        self.arm2 = Servo(bus,channel)
        channel=2 # arm3 胴体関節 #PWM=2
        self.arm3 = Servo(bus,channel)
        self.arm1.neutral()
        self.arm2.neutral()
        self.arm3.neutral()
        
        t = threading.Thread(target=self.queue_execution_thread,args=())
        t.setDaemon(True)
        t.start()

        return

    '''
    STOP命令でsleepを解除する
    '''
    def rem_sleep(self,sectime):
        sleep_time = 0.0
        sleep_interval = 0.01

        while sleep_time < sectime: # time.sleep(sectime) に停止フラグ検証を追加
            if self.STOP_PATTERN:
                break        
            time.sleep(sleep_interval)
            sleep_time += sleep_interval
        return
    
    def arm_empty(self):
        print("ARM empty()")
        '''
        アームを初期位置に移動する
        '''
        if self.STOP_PATTERN:
            return
        if not self.arm1.get_angle() == self.ARM1_OPEN:
            self.arm1.set_angle(self.ARM1_OPEN)
            self.ARM1_STATUS=1
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm2.get_angle() == self.ARM2_EMPTY:
            self.arm2.set_angle(self.ARM2_EMPTY)
            self.ARM2_STATUS=0
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm1.get_angle() == self.ARM1_CLOSE:
            self.arm1.set_angle(self.ARM1_CLOSE)
            self.ARM1_STATUS=0
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm3.get_angle() == self.ARM3_EMPTY:
            self.arm3.set_angle(self.ARM3_EMPTY)
            self.ARM3_STATUS=0
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        return

    def arm_catch(self):
        print("ARM catch()")
        '''
        ARM2が降りたままARM3をCATCH位置に動かすと、ターゲットにぶつける可能性があるため、
        必ずarm_empty()状態であること
        '''
        if self.STOP_PATTERN:
            return        
        if not self.arm3.get_angle() == self.ARM3_CATCH:
            self.arm3.set_angle(self.ARM3_CATCH)
            self.ARM3_STATUS=1
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm1.get_angle() == self.ARM1_OPEN:
            self.arm1.set_angle(self.ARM1_OPEN)
            self.ARM1_STATUS=1
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm2.get_angle() == self.ARM2_CATCH:
            self.arm2.set_angle(self.ARM2_CATCH)
            self.ARM2_STATUS=1
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm1.get_angle() == self.ARM1_CATCH:
            self.arm1.set_angle(self.ARM1_CATCH)
            self.ARM1_STATUS=2
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm2.get_angle() == self.ARM2_LIFT:
            self.arm2.set_angle(self.ARM2_LIFT)
            self.ARM2_STATUS=2
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        return
    def arm_release(self):
        print("ARM release()")
        '''
        その場に高さ0でリリースする
        '''
        if self.STOP_PATTERN:
            return        
        if not self.arm2.get_angle() == self.ARM2_CATCH+2:
            self.arm2.set_angle(self.ARM2_CATCH+2)
            self.ARM2_STATUS=1
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm1.get_angle() == self.ARM1_OPEN:
            self.arm1.set_angle(self.ARM1_OPEN)
            self.ARM1_STATUS=1
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm2.get_angle() == self.ARM2_EMPTY:
            self.arm2.set_angle(self.ARM2_EMPTY)
            self.ARM2_STATUS=0
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        return
    def arm_put(self):
        print("ARM put()")
        '''
        台の上に置く
        '''
        if self.STOP_PATTERN:
            return        
        if not self.arm3.get_angle() == self.ARM3_PUT:
            self.arm3.set_angle(self.ARM3_PUT)
            self.ARM3_STATUS=2
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm2.get_angle() == self.ARM2_CATCH+12:
            self.arm2.set_angle(self.ARM2_CATCH+12)
            self.ARM2_STATUS=1
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm1.get_angle() == self.ARM1_OPEN:
            self.arm1.set_angle(self.ARM1_OPEN)
            self.ARM1_STATUS=1
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        if not self.arm2.get_angle() == self.ARM2_EMPTY:
            self.arm2.set_angle(self.ARM2_EMPTY)
            self.ARM2_STATUS=0
            self.rem_sleep(0.5*self.DELAY)
            if self.STOP_PATTERN:
                return        
        return


    def checkCallback(self):
        '''
        スレッドコールバックキューの値を確認する
        return: キューに値があるとき、Trueを返す。無ければFalseを返す。
        '''
        result = False
        isQueueExists = False
        while not self.callback_queue.empty(): # キューが空になるまで取得を続ける
            if not isQueueExists:
                isQueueExists = True
            value = self.callback_queue.get(block=False)
            print("callback:{}".format(value))
        if isQueueExists:
            isQueueExists = False
            result = True

        return result

    def stop(self):
        '''
        stopはスレッド外呼び出しを考慮し、lockをメソッドで取る
        '''
        print("ARM stop()")
        self.STOP_PATTERN = True
        isQueueExists = False
        with self.lock:
            # パターンキューが空になるまでキューを取得する
            while not self.pattern_queue.empty():
                if not isQueueExists:
                    isQueueExists = True
                p = self.pattern_queue.get(block=False)
                self.pattern_queue.task_done()
                print("stop:{}".format(p))
            if isQueueExists:
                isQUeueExists = False

            self.STOP_PATTERN = False
        print("end stop")
        return

    def wait(self):
        '''
        パターンキューが終了するまで待つ
        '''
        print("ARM wait()")
        if not self.pattern_queue.empty():
            self.pattern_queue.join()
        print("end wait")

        return

    def get_status(self):
        '''
        アームが稼働中かどうかを返す
        パターンキューにキューがあるときは稼働中と判断する
        return: 稼働中の時True、停止中の時False
        '''
        if self.pattern_queue.empty():
            return False
        else:
            return True

    def queue_execution_thread(self):
        '''
        コマンド命令キューを一つ一つ実行する単一の常時動作スレッドとして使う
        callbackキューへの処理完了キュー追加はsleepしている0.5秒以内に受け付けたqueue毎となる
        '''
        isQueueExists = False
        # パターンキューが空になるまでキューを取得し実行する
        try:
            while True:
                with self.lock:
                    while not self.pattern_queue.empty(): # パターンキューが空になるまでキュー取得->処理を続ける
                        if not isQueueExists:
                            isQueueExists = True
                        p = self.pattern_queue.get(block=False)
                        # パターンキューがあるならキューを実行する
                        if p == 'empty':
                            self.arm_empty()
                        elif p == 'catch':
                            self.arm_catch()
                        elif p == 'put':
                            self.arm_put()
                        elif p == 'release':
                            self.arm_release()

                        self.pattern_queue.task_done() # wait()で全てのタスクの完了を待つためのjoinをしているため、queue一つ一つでtask_done()を行う

                    # パターンキュー処理をすべて完了したのでcallbackキューに完了通知を入れる
                    if isQueueExists:
                        isQueueExists = False
                        self.callback_queue.put('0')

                # lockを解放後、次のキューを待つためsleepする
                time.sleep(0.5) # ここは終了するべきキューが空の状態、且つこのスレッド自体は終了しないスレッドなので、停止確認用rem_sleep()は不要。キューが空の状態でstop命令を行っても、stop命令はそもそもここには来ない。仮にstopをここで処理するように追加しても0.5sec待機するだけ。
        except:
            import traceback
            traceback.print_exc()

        return

    def start(self,pattern='empty'):
        '''
        スレッド動作のstopは単独パターンのみとする
        先頭stop後に続くパターンは無視
        パターン途中のstopは無視
        '''
        pattern = pattern.split(' ')

        if pattern[0] == 'stop':
            print("start stop")
            self.stop()
        else:
            # start pattern1 pattern2..
            with self.lock:
                print('start'+''.join(' {}'.format(p) for p in pattern))
                for p in pattern:
                    if p == 'stop':
                        continue
                    self.pattern_queue.put(p) # catch,put,emptyの文字列をqueueに入れる

