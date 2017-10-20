# coding: utf-8
import Fabo_PCA9685
import time

import pkg_resources
SMBUS='smbus'
for dist in pkg_resources.working_set:
    #print(dist.project_name, dist.version)
    if dist.project_name == 'smbus':
        break
    if dist.project_name == 'smbus2':
        SMBUS='smbus2'
        break
if SMBUS == 'smbus':
    import smbus
elif SMBUS == 'smbus2':
    import smbus2 as smbus


class Servo():
    '''
    ロボットアームのSERVOサーボ回転を制御するクラス
    arm = Servo(channel=#PWD)
    arm.SERVO_MIN_ANGLE_VALUE = 0
    arm.SERVO_MAX_ANGLE_VALUE = 600
    arm.SERVO_NEUTRAL_ANGLE_VALUE = 300
    arm.SERVO_SINGLESHOT_ANGLE_VALUE = 10
    '''
    CHANNEL = 0 # PCA9685 サーボ接続チャネル

    # サーボの限界回転角。サーボ自体の回転角の他に、サーボを取り付けた部分の稼働可能角を考慮して、稼働可能な回転角を決めること
    SERVO_MIN_ANGLE_VALUE = 0
    SERVO_MAX_ANGLE_VALUE = 600
    # サーボの中央位置
    SERVO_NEUTRAL_ANGLE_VALUE = 300
    # サーボの一度の稼働角
    SERVO_SINGLESHOT_ANGLE_VALUE = 10

    # 現在のサーボの回転角
    SERVO_ANGLE_VALUE = 0
    
    def __init__(self,bus=1,channel=0):
        self.CHANNEL = channel
        self.bus = smbus.SMBus(bus)
        self.PCA9685 = Fabo_PCA9685.PCA9685(self.bus)
        # self.PCA9685.set_freq(50) default: 50 Hz
        return

    def right(self):
        self.set_angle(self.SERVO_NEUTRAL_ANGLE_VALUE + self.SERVO_SINGLESHOT_ANGLE_VALUE)

    def left(self):
        self.set_angle(self.SERVO_NEUTRAL_ANGLE_VALUE - self.SERVO_SINGLESHOT_ANGLE_VALUE)

    def neutral(self, value=None):
        if value is None:
            value = self.SERVO_NEUTRAL_ANGLE_VALUE
        '''
        サーボをニュートラル位置に戻す
        引数valueはニュートラル位置を更新する
        '''
        if not self.servo_angle_validation(value):
            return

        # 引数valueをニュートラル位置に更新する
        self.SERVO_NEUTRAL_ANGLE_VALUE = value
        self.PCA9685.set_channel_value(self.CHANNEL, self.SERVO_NEUTRAL_ANGLE_VALUE)

    def set_angle(self, value):
        result = self.PCA9685.set_channel_value(self.CHANNEL, value)
        return result

    def set_angle_with_speed(self, angle, speed=1):
        START_ANGLE = self.get_angle()
        if START_ANGLE == angle:
            return

        if START_ANGLE >= angle:
            STEP=-1
        if START_ANGLE <= angle:
            STEP=+1

        ANGLE = START_ANGLE
        while True:
            ANGLE+=STEP
            self.set_angle(ANGLE)
            time.sleep(1/(speed*10.0))
            if ANGLE == angle:
                break
        return 

    def get_angle(self):
        self.SERVO_ANGLE_VALUE = self.PCA9685.get_channel_value(self.CHANNEL)
        return self.SERVO_ANGLE_VALUE

    def servo_angle_validation(self,value):
        '''
        引数valueがサーボの可動範囲内かどうかを確認する
        '''
        # バリデーション: SERVO_MIN_ANGLE_VALUE <= value <= SERVO_MAX_ANGLE_VALUE
        if not (self.SERVO_MIN_ANGLE_VALUE <= value):
            return False
        if not (value <= self.SERVO_MAX_ANGLE_VALUE):
            return False
        return True
