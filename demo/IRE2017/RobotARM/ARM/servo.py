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

class ServoConfig():
    # サーボの限界軸角度
    SERVO_MIN_PULSE = 650   # サーボの軸角度が0度になるHIGH時間のμ秒。サーボ毎に特性が異なる。
    SERVO_MAX_PULSE = 2350  # サーボの軸角度が180度になるHIGH時間のμ秒。サーボ毎に特性が異なる。
    # サーボの中央位置
    SERVO_CENTER_PULSE = (SERVO_MIN_PULSE + SERVO_MAX_PULSE)/2
    # サーボの角速度
    SERVO_SPEED = 10


class Servo():
    '''
    ロボットアームのSERVOサーボ回転を制御するクラス
    arm = Servo(channel=#PWD)
    '''
    CHANNEL = 0 # PCA9685 サーボ接続チャネル


    # サーボの限界軸角度。サーボ自体の軸角度の他に、サーボを取り付けた部分の稼働可能角を考慮して、稼働可能な軸角度を決めること
    SERVO_MIN_ANGLE = 0
    SERVO_MAX_ANGLE = 180
    SERVO_CENTER_ANGLE = 90

    # PWM周期 PCA9685設定になるため、全てのサーボで同じ値を使うこと
    SERVO_HZ = 60

    def __init__(self,bus=1,channel=0,conf=ServoConfig()):
        try:
            self.conf = conf
            self.CHANNEL = channel
            self.bus = smbus.SMBus(bus)
            init_analog = self.angle_to_analog(90)
            self.PCA9685 = Fabo_PCA9685.PCA9685(self.bus,init_analog)
            self.PCA9685.set_hz(self.SERVO_HZ)
            print("hz:{}".format(self.SERVO_HZ))
        except:
            import traceback
            traceback.print_exc()
        return

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)        

    def angle_to_analog(self, angle):
        '''
        angle: 0 to 180 degree.
        return: PWM value.
        '''
        pulse = self.translate(angle, 0, 180, self.conf.SERVO_MIN_PULSE, self.conf.SERVO_MAX_PULSE)
        analog = round(float(pulse) / 1000000 * self.SERVO_HZ * 4096)
        return analog

    def analog_to_angle(self, analog):
        '''
        analog: PWM value.
        return: 0 to 180 degree.
        '''
        pulse = float(analog) * 1000000 / self.SERVO_HZ / 4096
        angle = round(self.translate(pulse, self.conf.SERVO_MIN_PULSE, self.conf.SERVO_MAX_PULSE, 0, 180))
        return angle
    
    def get_analog(self):
        return self.PCA9685.get_channel_value(self.CHANNEL)

    def set_analog(self, analog):
        self.PCA9685.set_channel_value(self.CHANNEL, analog)

    def set_angle(self, angle, speed=None):
        '''
        angle: 0 to 180 degree.
        '''
        target_analog = self.angle_to_analog(angle)
        
        if speed is None:
            speed = self.conf.SERVO_SPEED
        try:
            START_ANALOG = self.get_analog()
            START_ANGLE = self.analog_to_angle(START_ANALOG)
            print("servo set_angle:{}({}) -> {}({}) speed:{}".format(START_ANGLE,START_ANALOG,angle,target_analog,speed))
            if START_ANALOG == target_analog:
                return
            if speed == 0:
                self.set_analog(target_analog)
                return

            if START_ANALOG >= target_analog:
                STEP=-1
            if START_ANALOG <= target_analog:
                STEP=+1

            ANALOG = START_ANALOG
            while True:
                ANALOG+=STEP
                self.set_analog(ANALOG)
                time.sleep(1.0/(speed*10.0))
                if ANALOG == target_analog:
                    NOW_ANALOG = self.get_analog()
                    NOW_ANGLE = self.analog_to_angle(NOW_ANALOG)
                    if not ANALOG == NOW_ANALOG:
                        msg = 'Servo angle error. Couldn\'t move '+str(START_ANGLE)+" to "+str(angle)+". Now "+str(NOW_ANGLE)+"."
                        raise ServoAngleError(Exception(msg))
                    else:
                        print("Servo angle ok. start:{} target:{} now:{}".format(START_ANGLE,angle,NOW_ANGLE))
                    break
            return
        except:
            import traceback
            traceback.print_exc()

    def get_angle(self):
        '''
        return: 0 to 180 degree.
        '''
        try:
            analog = self.get_analog()
            return self.analog_to_angle(analog)
        except:
            import traceback
            traceback.print_exc()

    def neutral(self, value=None):
        '''
        value: 0 to 180 degree.
        ちょうどいい初期位置が中央位置とも限らないので、ここはニュートラル位置と呼ぶことにする
        '''
        try:
            if value is None:
                value = self.SERVO_CENTER_ANGLE
            '''
            サーボをニュートラル位置に戻す
            引数valueはニュートラル位置を更新する
            '''
            if not self.servo_angle_validation(value):
                return

            # 引数valueをニュートラル位置に更新する
            self.SERVO_CENTER_ANGLE = value
            # サーボをゆっくりニュートラル位置に移動する
            self.set_angle(90)
        except:
            import traceback
            traceback.print_exc()

    def servo_angle_validation(self,value):
        '''
        value: 0 to 180 degree.
        '''
        try:
            '''
            引数valueがサーボの可動範囲内かどうかを確認する
            '''
            # バリデーション: SERVO_MIN_ANGLE <= value <= SERVO_MAX_ANGLE
            if not (self.SERVO_MIN_ANGLE <= value):
                return False
            if not (value <= self.SERVO_MAX_ANGLE):
                return False
            return True
        except:
            import traceback
            traceback.print_exc()
