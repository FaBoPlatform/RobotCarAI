# coding: utf-8
# STAGE1:
# Forward Collision Avoidance System:Forward CAS[前方衝突回避システム]
# 光学センサーとなる
# ロボットカーは直進する
# 上り坂については考慮しない
# ロボットカーの速度については考慮しない
# 首振りで道を探すことは考慮しない
# 
import numpy as np


class SensorGenerator():
    # 車両全幅(cm)
    CAR_WIDTH=16.5
    # ホイールベース + ノーズ(cm)
    CAR_LENGTH=19.0 + 14.0
    # 最小旋回半径(cm)
    MIN_CIRCLE_R=75
    # 最大旋回半径(cm)
    MAX_CIRCLE_R=np.sqrt(np.power(MIN_CIRCLE_R+CAR_WIDTH,2)+np.power(CAR_LENGTH,2)) # 97.26895702124085cm

    # 旋回開始距離定義
    FRONT_MAX_DRIVE_CONTROL_DISTANCE=100 # 最大旋回半径より大きく取る
    LEFT45_MAX_DRIVE_CONTROL_DISTANCE=MIN_CIRCLE_R*np.sqrt(2) # 106.06601717798213
    RIGHT45_MAX_DRIVE_CONTROL_DISTANCE=LEFT45_MAX_DRIVE_CONTROL_DISTANCE
    # 旋回禁止距離定義
    LEFT45_MIN_DRIVE_CONTROL_DISTANCE=CAR_WIDTH # 幅調整禁止距離 真横12cm 左には曲がれない距離
    RIGHT45_MIN_DRIVE_CONTROL_DISTANCE=CAR_WIDTH # 幅調整禁止距離 真横12cm 右には曲がれない距離
    # 停止距離定義　前方障害物回避は左右フロントバンパーがこすらなければよい
    Px=MIN_CIRCLE_R+CAR_WIDTH/2
    Py=np.sqrt(np.power(MAX_CIRCLE_R,2)-np.power(Px,2))
    STOP_DISTANCE=Py-CAR_LENGTH
    FRONT_MIN_DRIVE_CONTROL_DISTANCE=STOP_DISTANCE # 17.305939013202007 全面に障害物があり、曲がってもぶつかる前方障害物までの距離。停止のために10cmおまけで追加しておく->車両制御コードに前方障害物までの距離を元に速度調整を入れたので10cmマージンを削除。

    def printinfo(self):
        print("車両幅:{}".format(self.CAR_WIDTH))
        print("最小旋回半径:{}".format(self.MIN_CIRCLE_R))
        print("最大旋回半径:{}".format(self.MAX_CIRCLE_R))
        print("左右制御開始距離:{} (左右幅取り開始距離)".format(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE))
        print("前方制御開始距離:{} (旋回開始距離)".format(self.FRONT_MAX_DRIVE_CONTROL_DISTANCE))
        print("左右旋回禁止距離:{}, {} (幅寄せ禁止距離と真横の距離)".format(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE,self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE/np.sqrt(2)))
        print("停止距離:{} (曲がってもぶつかる前方障害物までの距離)".format(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE))
        return

    '''
    return 
    0:安全範囲につき制御不要
    1:危険範囲につき制御が必要
    2:曲がれない
    '''
    def left45_control(self,LEFT45_SENSOR_DISTANCE):
        # 安全範囲
        if self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE < LEFT45_SENSOR_DISTANCE:
            return 0
        # 制御範囲
        if self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE <= LEFT45_SENSOR_DISTANCE and LEFT45_SENSOR_DISTANCE <= self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE:
            return 1
        # 旋回禁止範囲
        if LEFT45_SENSOR_DISTANCE < self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE:
            return 2

    '''
    return 
    0:安全範囲につき制御不要
    1:危険範囲につき制御が必要
    2:曲がれない
    '''
    def right45_control(self,RIGHT45_SENSOR_DISTANCE):
        # 安全範囲
        if self.RIGHT45_MAX_DRIVE_CONTROL_DISTANCE < RIGHT45_SENSOR_DISTANCE:
            return 0
        # 制御範囲
        if self.RIGHT45_MIN_DRIVE_CONTROL_DISTANCE <= RIGHT45_SENSOR_DISTANCE and RIGHT45_SENSOR_DISTANCE <= self.RIGHT45_MAX_DRIVE_CONTROL_DISTANCE:
            return 1
        # 旋回禁止範囲
        if RIGHT45_SENSOR_DISTANCE < self.RIGHT45_MIN_DRIVE_CONTROL_DISTANCE:
            return 2

    '''
    return 
    0:安全範囲につき制御不要
    1:危険範囲につき制御が必要
    2:曲がれない
    '''
    def front_control(self,FRONT_SENSOR_DISTANCE):
        # 安全範囲
        if self.FRONT_MAX_DRIVE_CONTROL_DISTANCE < FRONT_SENSOR_DISTANCE:
            return 0
        # 制御範囲
        if self.FRONT_MIN_DRIVE_CONTROL_DISTANCE <= FRONT_SENSOR_DISTANCE and FRONT_SENSOR_DISTANCE <= self.FRONT_MAX_DRIVE_CONTROL_DISTANCE:
            return 1
        # 停止範囲
        if FRONT_SENSOR_DISTANCE < self.FRONT_MIN_DRIVE_CONTROL_DISTANCE:
            return 2

    '''
    sensors=[LEFT45_SENSOR_DISTANCE,FRONT_SENSOR_DISTANCE,RIGHT45_SENSOR_DISTANCE]
    '''
    def driving_instruction(self,sensors):

        LEFT45_CONTROL = self.left45_control(sensors[0])
        FRONT_CONTROL = self.front_control(sensors[1])
        RIGHT45_CONTROL = self.right45_control(sensors[2])

        STOP=0
        FORWARD=0
        LEFT=0
        RIGHT=0
        ERROR=0 # 分岐ミス確認用
        CONTROL_NUMBER=0 # 分岐場所確認用
        '''
        ロボットカーは[LEFT45_CONTROL,FRONT_CONTROL,RIGHT45_CONTROL]が不要になるように走行する
        x FRONT_CONTROL==2
        直進も旋回も出来ないため停止する
        x LEFT45_CONTROL, x FRONT_CONTROL, x RIGHT45_CONTROL：
        コントロール不要で直進する
        o LEFT45_CONTROL, x FRONT_CONTROL, x RIGHT45_CONTROL：
        右に曲がる
        x LEFT45_CONTROL, o FRONT_CONTROL, x RIGHT45_CONTROL：
        左右のより大きい空間に曲がる
        x LEFT45_CONTROL, x FRONT_CONTROL, o RIGHT45_CONTROL：
        左に曲がる
        '''
        if FRONT_CONTROL == 2: # 直進も旋回も出来ないため停止する
            STOP=1
            CONTROL_NUMBER=1
        elif not LEFT45_CONTROL == 2 and FRONT_CONTROL == 1 and not RIGHT45_CONTROL == 2: # 前方障害物あり、左右旋回可能なので、左右の大きい空間に曲がる
            if sensors[0] <= sensors[2]: # LEFT45_SENSOR_DISTANCE <= RIGHT45_SENSOR_DISTANCE
                RIGHT=1
                CONTROL_NUMBER=2
            else:
                LEFT=1
                CONTROL_NUMBER=3
        elif LEFT45_CONTROL == 0 and FRONT_CONTROL == 0 and RIGHT45_CONTROL == 0: # 制御不要
            FORWARD=1
            CONTROL_NUMBER=4
        elif not LEFT45_CONTROL == 0 and RIGHT45_CONTROL == 0: # 右に曲がる
            RIGHT=1
            CONTROL_NUMBER=5
        elif LEFT45_CONTROL == 0 and not RIGHT45_CONTROL == 0: # 左に曲がる
            LEFT=1
            CONTROL_NUMBER=6
        elif LEFT45_CONTROL == 2 and RIGHT45_CONTROL == 2: # 直進する ここは幅制御を諦めたため、壁にぶつかる可能性がある部分
            FORWARD=1
            CONTROL_NUMBER=7
        elif LEFT45_CONTROL == 1 and RIGHT45_CONTROL == 1: # 幅調整しながら進む
            if sensors[0] <= sensors[2]: # LEFT45_SENSOR_DISTANCE <= RIGHT45_SENSOR_DISTANCE
                RIGHT=1
                CONTROL_NUMBER=8
            else:
                LEFT=1
                CONTROL_NUMBER=9
        elif LEFT45_CONTROL == 2 and RIGHT45_CONTROL == 1: # 右に曲がる
            RIGHT=1
            CONTROL_NUMBER=10
        elif LEFT45_CONTROL == 1 and RIGHT45_CONTROL == 2: # 左に曲がる
            LEFT=1
            CONTROL_NUMBER=11

        if not (STOP+LEFT+FORWARD+RIGHT) == 1:
            #STOP=0
            #LEFT=0
            #FORWARD=0
            #RIGHT=0
            ERROR=1

        # 分岐ミスが起こっていなければ[STOP,LEFT,FOWARD,RIGHT]はone hot valueとなる
        return [STOP,LEFT,FORWARD,RIGHT,ERROR,CONTROL_NUMBER]


