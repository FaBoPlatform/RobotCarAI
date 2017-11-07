# coding: utf-8
import RPi.GPIO as GPIO
import sys
import threading

# Button pin
BUTTONPIN_RED = 5
BUTTONPIN_BLUE = 6

# State 
ARM_STATE_IDLE = 1
ARM_STATE_RUN = 2
ARM_STATE_FINISH = 3
ARM_STATE_STOP = 4

# Static state
state = ARM_STATE_IDLE

# Static counter
counter = 0

# Static thread state
runnning = False

"""
Thread処理
DeepLearningの認識の処理
"""
def AI(self):
    while self.running:
        # AIの判定処理(プロセスからの結果等？)待ち

"""
counterベースで時系列のARMの挙動を記載する
"""
def controlArm(self, counter):
    if self.counter < 100:
    else self.counter < 300:

"""
Button Event
"""
def buttonCallback(channel):
    if GPIO.input(BUTTONPIN_RED):
        self.state = ARM_STATE_STOP
    if GPIO.input(BUTTONPIN_BLUE):
        self.state = ARM_STATE_IDLE
        self.counter = 0
        
"""
初期化処理
"""
def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTONPIN_RED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTONPIN_BLUE, GPIO.IN,  pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(BUTTONPIN_RED, GPIO.RISING, callback=buttonCallback, bouncetime=300)
    GPIO.add_event_detect(BUTTONPIN_BLUE, GPIO.RISING, callback=buttonCallback, bouncetime=300)

"""
各State毎の処理を記載する
"""
def main():
    try:
        while True:
            # ロジック
            if state == ARM_STATE_STOP:
                # 強制ストップ処理
            elif state == ARM_STATE_RUN:
                # ARMを起動する処理
                self.counter++;
                controlArm(counter)
            elif state == ARM_STATE_IDLE:
                self.running = True
                threading.Thread(target=self.AI,).start()
                
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit(0)

if __name__ == '__main__':
    init()
    main()