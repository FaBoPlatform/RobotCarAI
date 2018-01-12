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


class LabelGenerator():
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
    def left45_control(self,left45_sensor_distance):
        # 安全範囲
        if self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE < left45_sensor_distance:
            return 0
        # 制御範囲
        if self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE <= left45_sensor_distance and left45_sensor_distance <= self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE:
            return 1
        # 旋回禁止範囲
        if left45_sensor_distance < self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE:
            return 2

    '''
    return 
    0:安全範囲につき制御不要
    1:危険範囲につき制御が必要
    2:曲がれない
    '''
    def right45_control(self,right45_sensor_distance):
        # 安全範囲
        if self.RIGHT45_MAX_DRIVE_CONTROL_DISTANCE < right45_sensor_distance:
            return 0
        # 制御範囲
        if self.RIGHT45_MIN_DRIVE_CONTROL_DISTANCE <= right45_sensor_distance and right45_sensor_distance <= self.RIGHT45_MAX_DRIVE_CONTROL_DISTANCE:
            return 1
        # 旋回禁止範囲
        if right45_sensor_distance < self.RIGHT45_MIN_DRIVE_CONTROL_DISTANCE:
            return 2

    '''
    return 
    0:安全範囲につき制御不要
    1:危険範囲につき制御が必要
    2:曲がれない
    '''
    def front_control(self,front_sensor_distance):
        # 安全範囲
        if self.FRONT_MAX_DRIVE_CONTROL_DISTANCE < front_sensor_distance:
            return 0
        # 制御範囲
        if self.FRONT_MIN_DRIVE_CONTROL_DISTANCE <= front_sensor_distance and front_sensor_distance <= self.FRONT_MAX_DRIVE_CONTROL_DISTANCE:
            return 1
        # 停止範囲
        if front_sensor_distance < self.FRONT_MIN_DRIVE_CONTROL_DISTANCE:
            return 2

    '''
    sensors=[LEFT45_SENSOR_DISTANCE,FRONT_SENSOR_DISTANCE,RIGHT45_SENSOR_DISTANCE]
    '''
    def control(self,sensors):

        left45_control = self.left45_control(sensors[0])
        front_control = self.front_control(sensors[1])
        right45_control = self.right45_control(sensors[2])

        stop=0
        forward=0
        left=0
        right=0
        error=0 # 分岐ミス確認用
        control_number=0 # 分岐場所確認用
        '''
        ロボットカーは[left45_control,front_control,right45_control]が不要になるように走行する
        x front_control==2
        直進も旋回も出来ないため停止する
        x left45_control, x front_control, x right45_control：
        コントロール不要で直進する
        o left45_control, x front_control, x right45_control：
        右に曲がる
        x left45_control, o front_control, x right45_control：
        左右のより大きい空間に曲がる
        x left45_control, x front_control, o right45_control：
        左に曲がる
        '''
        if front_control == 2: # 直進も旋回も出来ないため停止する
            stop=1
            control_number=1
        elif not left45_control == 2 and front_control == 1 and not right45_control == 2: # 前方障害物あり、左右旋回可能なので、左右の大きい空間に曲がる
            if sensors[0] <= sensors[2]: # LEFT45_SENSOR_DISTANCE <= RIGHT45_SENSOR_DISTANCE
                right=1
                control_number=2
            else:
                left=1
                control_number=3
        elif left45_control == 0 and front_control == 0 and right45_control == 0: # 制御不要
            forward=1
            control_number=4
        elif not left45_control == 0 and right45_control == 0: # 右に曲がる
            right=1
            control_number=5
        elif left45_control == 0 and not right45_control == 0: # 左に曲がる
            left=1
            control_number=6
        elif left45_control == 2 and right45_control == 2: # 直進する ここは幅制御を諦めたため、壁にぶつかる可能性がある部分
            forward=1
            control_number=7
        elif left45_control == 1 and right45_control == 1: # 幅調整しながら進む
            if sensors[0] <= sensors[2]: # LEFT45_SENSOR_DISTANCE <= RIGHT45_SENSOR_DISTANCE
                right=1
                control_number=8
            else:
                left=1
                control_number=9
        elif left45_control == 2 and right45_control == 1: # 右に曲がる
            right=1
            control_number=10
        elif left45_control == 1 and right45_control == 2: # 左に曲がる
            left=1
            control_number=11

        if not (stop+left+forward+right) == 1:
            #stop=0
            #left=0
            #forward=0
            #right=0
            error=1

        # 分岐ミスが起こっていなければ[stop,left,FOWARD,right]はone hot valueとなる
        return [stop,left,forward,right,error,control_number]

    def get_label(self,sensors):
        control_result = self.control(sensors)
        # 分岐ミスがある場合は表示し、STOPを返す
        if control_result[4] == 1:
            print("Label ERROR! sensors:{} control_number:{}".format(sensors,control_result[5]))
            return [1,0,0,0]
        # ラベルを返す
        return control_result[0:4]
                  
