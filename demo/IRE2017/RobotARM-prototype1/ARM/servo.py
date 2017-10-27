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

class ServoAngleError(Exception):
    pass

class Servo():
    '''
    ロボットアームのSERVOサーボ回転を制御するクラス
    arm = Servo(channel=#PWD)
    arm.SERVO_MIN_ANGLE_VALUE = 0
    arm.SERVO_MAX_ANGLE_VALUE = 600
    arm.SERVO_NEUTRAL_ANGLE_VALUE = 300
    '''
    CHANNEL = 0 # PCA9685 サーボ接続チャネル

    # サーボの限界回転角。サーボ自体の回転角の他に、サーボを取り付けた部分の稼働可能角を考慮して、稼働可能な回転角を決めること
    SERVO_MIN_ANGLE_VALUE = 0
    SERVO_MAX_ANGLE_VALUE = 600
    # サーボの中央位置
    SERVO_NEUTRAL_ANGLE_VALUE = 300
    # サーボの角速度
    SERVO_SPEED = 10

    # 現在のサーボの回転角
    SERVO_ANGLE_VALUE = 0

    def __init__(self,bus=1,channel=0):
        try:
            self.CHANNEL = channel
            self.bus = smbus.SMBus(bus)
            self.PCA9685 = Fabo_PCA9685.PCA9685(self.bus)
            # self.PCA9685.set_freq(50) default: 50 Hz
        except:
            import traceback
            traceback.print_exc()
        return

    def set_angle(self, angle, speed=None):
        if speed is None:
            speed = self.SERVO_SPEED
        try:
            START_ANGLE = self.get_angle()
            print("servo set_angle:{} -> {} speed:{}".format(START_ANGLE,angle,speed))
            if START_ANGLE == angle:
                return
            if speed == 0:
                self.PCA9685.set_channel_value(self.CHANNEL, angle)
                return

            if START_ANGLE >= angle:
                STEP=-1
            if START_ANGLE <= angle:
                STEP=+1

            ANGLE = START_ANGLE
            while True:
                ANGLE+=STEP
                self.PCA9685.set_channel_value(self.CHANNEL, ANGLE)
                time.sleep(1.0/(speed*10.0))
                if ANGLE == angle:
                    END_ANGLE = self.get_angle()
                    if not ANGLE == END_ANGLE:
                        msg = 'Servo angle error. Couldn\'t move '+str(START_ANGLE)+" to "+str(angle)+". Now "+str(END_ANGLE)+"."
                        raise ServoAngleError(Exception(msg))
                    else:
                        print("Servo angle ok. start:{} target:{} now:{}".format(START_ANGLE,angle,END_ANGLE))
                    break
            return
        except:
            import traceback
            traceback.print_exc()

    def get_angle(self):
        try:
            self.SERVO_ANGLE_VALUE = self.PCA9685.get_channel_value(self.CHANNEL)
            return self.SERVO_ANGLE_VALUE
        except:
            import traceback
            traceback.print_exc()

    def neutral(self, value=None):
        try:
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
            #self.PCA9685.set_channel_value(self.CHANNEL, self.SERVO_NEUTRAL_ANGLE_VALUE)
            # サーボをゆっくりニュートラル位置に移動する
            self.set_angle(self.SERVO_NEUTRAL_ANGLE_VALUE)
        except:
            import traceback
            traceback.print_exc()

    def servo_angle_validation(self,value):
        try:
            '''
            引数valueがサーボの可動範囲内かどうかを確認する
            '''
            # バリデーション: SERVO_MIN_ANGLE_VALUE <= value <= SERVO_MAX_ANGLE_VALUE
            if not (self.SERVO_MIN_ANGLE_VALUE <= value):
                return False
            if not (value <= self.SERVO_MAX_ANGLE_VALUE):
                return False
            return True
        except:
            import traceback
            traceback.print_exc()
