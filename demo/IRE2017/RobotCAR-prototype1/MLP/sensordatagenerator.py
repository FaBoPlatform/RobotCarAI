# coding: utf-8
# STAGE1:
# Forward Collision Avoidance System:Forward CAS[前方衝突回避システム]
# 光学センサーとなる
# ラジコンカーは直進する
# 上り坂については考慮しない
# ラジコンカーの速度については考慮しない
# 首振りで道を探すことは考慮しない
# 
import numpy as np


class SensorGenerator():
    # 車両全幅(cm)
    OVERALL_WIDTH=19.0
    # ホイールベース + ノーズ(cm)
    WHEELBASE=24.5 + 14.0
    # 最小回転半径(cm)
    TURNING_CIRCLE=75 # 旋回半径
    # 旋回禁止距離定義
    LEFT45_MAX_DRIVE_CONTROL_DISTANCE=TURNING_CIRCLE/np.sqrt(2) + OVERALL_WIDTH # 幅調整開始距離 45度斜め距離72.0330cm,真横50.9350cm
    RIGHT45_MAX_DRIVE_CONTROL_DISTANCE=LEFT45_MAX_DRIVE_CONTROL_DISTANCE
    FRONT_MAX_DRIVE_CONTROL_DISTANCE=100
    # 旋回禁止距離定義
    LEFT45_MIN_DRIVE_CONTROL_DISTANCE=OVERALL_WIDTH # 幅調整禁止距離 真横13.4350cm 左には曲がれない距離
    RIGHT45_MIN_DRIVE_CONTROL_DISTANCE=OVERALL_WIDTH # 幅調整禁止距離 真横13.4350cm 右には曲がれない距離
    # 絶対停止距離定義　前方障害物回避は左右フロントバンパーがこすらなければよい
    x=np.sqrt(np.power(TURNING_CIRCLE,2)-np.power(WHEELBASE,2))
    a=(TURNING_CIRCLE-OVERALL_WIDTH/2-(TURNING_CIRCLE-x))
    y=np.sqrt(np.power(TURNING_CIRCLE,2)-np.power(a,2))
    z=y-WHEELBASE
    FRONT_MIN_DRIVE_CONTROL_DISTANCE=z+10 # 22.6363 全面に障害物があり、曲がってもぶつかる前方障害物までの距離。停止のために10cmおまけで追加しておく

    UNLIMIT=1000 # 生成するセンサー値の最大値

    CONTROL=np.zeros(11)
    CONTRES=None
    CSVROW=None
    CSVDATA=[]
    
    def printinfo(self):
        print("車両幅:{}".format(self.OVERALL_WIDTH))
        print("最小回転半径:{}".format(self.TURNING_CIRCLE))
        print("左右制御開始距離:{} (左右幅調整開始距離)".format(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE))
        print("前方制御開始距離:{} (旋回開始距離)".format(self.FRONT_MAX_DRIVE_CONTROL_DISTANCE))
        print("左右旋回禁止距離:{} (曲がれない距離)".format(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE))
        print("絶対停止距離:{} (曲がってもぶつかる前方障害物までの距離)".format(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE))
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

        #print LEFT45_CONTROL
        #print FRONT_CONTROL
        #print RIGHT45_CONTROL

        STOP=0
        FORWARD=0
        LEFT=0
        RIGHT=0
        ERROR=0
        CONTROL_NUMBER=0
        '''
        ラジコンは[LEFT45_CONTROL,FRONT_CONTROL,RIGHT45_CONTROL]が不要になるように動作する
        x FRONT_CONTROL==2
        直進も旋回も出来ないため停止する
        x LEFT45_CONTROL x FRONT_CONTROL x RIGHT45_CONTROL：
        コントロール不要で直進する
        o LEFT45_CONTROL x FRONT_CONTROL x RIGHT45_CONTROL：
        右に曲がる
        x LEFT45_CONTROL o FRONT_CONTROL x RIGHT45_CONTROL：
        左右のより大きい空間に曲がる
        x LEFT45_CONTROL x FRONT_CONTROL o RIGHT45_CONTROL：
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
        elif LEFT45_CONTROL == 2 and RIGHT45_CONTROL == 2: # 直進する ここは量幅制御を諦めたため、事故死する可能性がある部分
            FORWARD=1
            CONTROL_NUMBER=7
        elif LEFT45_CONTROL == 1 and RIGHT45_CONTROL == 1: # 量幅調整しながら直進する
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
        return [STOP,LEFT,FORWARD,RIGHT,ERROR,CONTROL_NUMBER]


    '''for debug'''
    #sensors = [self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE-1,100,100]
    #self.CONTRES = self.driving_instruction(sensors)
    #if self.CONTRES[4] == 1:
    #    print("error occured")
    #print(np.hstack((sensors,self.CONTRES[0:4])))
    #self.CSVROW = np.hstack((sensors,self.CONTRES[0:4]))
    #self.CSVDATA.append(self.CSVROW)
    #self.CONTROL[self.CONTRES[5]-1]+=1

    #for i in range(100):
    #    sensors = np.random.randint(0,51,3) 
    #    self.CONTRES = self.driving_instruction(sensors)
    #    if self.CONTRES[4] == 1:
    #        print("error occured")
    #    self.CSVROW = np.hstack((sensors,self.CONTRES[0:4]))
    #    self.CSVDATA.append(self.CSVROW)
    #    self.CONTROL[self.CONTRES[5]-1]+=1

    #8=np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE)-1
    #9=np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE)
    #17=np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1
    #18=np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)
    #60=np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1
    #61=np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)
    #100=self.FRONT_MAX_DRIVE_CONTROL_DISTANCE
    #101=self.FRONT_MAX_DRIVE_CONTROL_DISTANCE+1


    ########################################
    # データ生成
    ########################################
    # 境界値に±1を加えた値を返す
    def fill_boundary_point(self,boundary):
        # boundaryに±1の値を追加する
        for i in range(len(boundary)):
            PLUS=boundary[i]+1
            MINUS=boundary[i]-1
            boundary.append(PLUS)
            if MINUS >= 0:
                boundary.append(MINUS)
        return boundary
    # センサーデータを作成する
    def mk_sensor_data(self,LEFT45,FRONT,RIGHT45):
        for i in range(len(LEFT45)):
            for j in range(len(FRONT)):
                for k in range(len(RIGHT45)):
                    sensors = [LEFT45[i],FRONT[j],RIGHT45[k]]
                    self.CONTRES = self.driving_instruction(sensors)
                    if self.CONTRES[4] == 1:
                        print("error occured")
                    self.CSVROW = np.hstack((sensors,self.CONTRES[0:4]))
                    self.CSVDATA.append(self.CSVROW)
                    self.CONTROL[self.CONTRES[5]-1]+=1    

    def mk_random_data(self,record=100):
        ########################################
        # CONTROL_NUMBER=1
        # 範囲:[FRONT<19]
        # 境界値:[0,1000][19±1][0,1000]
        ########################################
        BOUNDARY_LEFT45 = [0,self.UNLIMIT]
        BOUNDARY_FRONT = [np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE)]
        BOUNDARY_RIGHT45 = [0,self.UNLIMIT]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        # 境界データを作成する
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        # 全域
        for i in range(record):
            LEFT45 = np.random.randint(0,self.UNLIMIT) 
            FRONT = np.random.randint(0,np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE)-1) 
            RIGHT45 = np.random.randint(0,self.UNLIMIT)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

        ########################################
        # CONTROL_NUMBER=2or3
        # 範囲:[60<LEFT45][19<=FRONT<=100][60<RIGHT45]
        # 範囲:[60<LEFT45][19<=FRONT<=100][18<=RIGHT45<=60]
        # 境界値:[60,1000][19,100],[60,1000]
        # 境界値:[60,1000][19,100],[18,60]
        ########################################
        BOUNDARY_LEFT45 = [np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,self.UNLIMIT]
        BOUNDARY_FRONT = [np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.FRONT_MAX_DRIVE_CONTROL_DISTANCE]
        BOUNDARY_RIGHT45 = [np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,self.UNLIMIT]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        for i in range(record*2): # 2or3の分岐なので2倍にしておく
            LEFT45 = np.random.randint(np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE),self.UNLIMIT) 
            FRONT = np.random.randint(np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.FRONT_MAX_DRIVE_CONTROL_DISTANCE) 
            RIGHT45 = np.random.randint(np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),self.UNLIMIT)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

        ########################################
        # CONTROL_NUMBER=4
        # 範囲:[60<LEFT45][100<FRONT][60<RIGHT45]
        # 境界値:[60,1000][100,1000][60,1000]
        ########################################
        BOUNDARY_LEFT45 = [np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,self.UNLIMIT]
        BOUNDARY_FRONT = [self.FRONT_MAX_DRIVE_CONTROL_DISTANCE,self.UNLIMIT]
        BOUNDARY_RIGHT45 = [np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,self.UNLIMIT]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        for i in range(record):
            LEFT45 = np.random.randint(np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE),self.UNLIMIT) 
            FRONT = np.random.randint(self.FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,self.UNLIMIT) 
            RIGHT45 = np.random.randint(np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE),self.UNLIMIT)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

        ########################################
        # CONTROL_NUMBER=5
        # 範囲:[18<=LEFT45<=60][100<FRONT][60<RIGHT45]
        # 範囲:[LEFT45<18][100<FRONT][60<RIGHT45]
        # 境界値:[18,60][100,1000][60,1000]
        # 境界値:[0,18][100,1000][60,1000]
        ########################################
        BOUNDARY_LEFT45 = [0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
        BOUNDARY_FRONT = [self.FRONT_MAX_DRIVE_CONTROL_DISTANCE,self.UNLIMIT]
        BOUNDARY_RIGHT45 = [np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,self.UNLIMIT]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        for i in range(record/2):
            LEFT45 = np.random.randint(np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1) 
            FRONT = np.random.randint(self.FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,self.UNLIMIT) 
            RIGHT45 = np.random.randint(np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE),self.UNLIMIT)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])
        for i in range(record/2):
            LEFT45 = np.random.randint(0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1) 
            FRONT = np.random.randint(self.FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,self.UNLIMIT) 
            RIGHT45 = np.random.randint(np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE),self.UNLIMIT)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

        ########################################
        # CONTROL_NUMBER=6
        # 範囲:[60<LEFT45][100<FRONT][18<=RIGHT45<=60]
        # 範囲:[60<LEFT45][100<FRONT][RIGHT45<18]
        # 範囲:[60<LEFT45][19<=FRONT<=100][RIGHT45<18]
        # 境界値:[60,1000][100,1000][18,60]
        # 境界値:[60,1000][100,1000][0,18]
        # 境界値:[60,1000][19,100][0,18]
        ########################################
        BOUNDARY_LEFT45 = [np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,self.UNLIMIT]
        BOUNDARY_FRONT = [np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.FRONT_MAX_DRIVE_CONTROL_DISTANCE,self.UNLIMIT]
        BOUNDARY_RIGHT45 = [0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        for i in range(record/2):
            LEFT45 = np.random.randint(np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE),self.UNLIMIT) 
            FRONT = np.random.randint(self.FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,self.UNLIMIT) 
            RIGHT45 = np.random.randint(0,np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])
        for i in range(record/2):
            LEFT45 = np.random.randint(np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE),self.UNLIMIT) 
            FRONT = np.random.randint(np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.FRONT_MAX_DRIVE_CONTROL_DISTANCE) 
            RIGHT45 = np.random.randint(0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

        ########################################
        # CONTROL_NUMBER=7
        # 範囲:[LEFT45<18][19<=FRONT<=100][RIGHT45<18]
        # 範囲:[LEFT45<18][FRONT<100][RIGHT45<18]
        # 境界値:[0,18][19,100][0,18]
        # 境界値:[0,18][0,100][0,18]
        ########################################
        BOUNDARY_LEFT45 = [0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)]
        BOUNDARY_FRONT = [0,np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.FRONT_MAX_DRIVE_CONTROL_DISTANCE]
        BOUNDARY_RIGHT45 = [0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        for i in range(record):
            LEFT45 = np.random.randint(0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1) 
            FRONT = np.random.randint(np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.UNLIMIT) 
            RIGHT45 = np.random.randint(0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

        ########################################
        # CONTROL_NUMBER=8or9
        # 範囲:[18<=LEFT45<=60][100<FRONT][18<=RIGHT45<=60]
        # 境界値:[18,60][100,1000][18,60]
        ########################################
        BOUNDARY_LEFT45 = [0,np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
        BOUNDARY_FRONT = [self.FRONT_MAX_DRIVE_CONTROL_DISTANCE,self.UNLIMIT]
        BOUNDARY_RIGHT45 = [np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        for i in range(record*2):
            LEFT45 = np.random.randint(np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1) 
            FRONT = np.random.randint(self.FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,self.UNLIMIT) 
            RIGHT45 = np.random.randint(np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

        ########################################
        # CONTROL_NUMBER=10
        # 範囲:[LEFT45<18][100<FRONT][18<=RIGHT45<=60]
        # 範囲:[LEFT45<18][19<=FRONT<=100][18<=RIGHT45<=60]
        # 境界値:[0,18][100,1000][18,60]
        # 境界値:[0,18][19,100][18,60]
        ########################################
        BOUNDARY_LEFT45 = [0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)]
        BOUNDARY_FRONT = [np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.FRONT_MAX_DRIVE_CONTROL_DISTANCE,self.UNLIMIT]
        BOUNDARY_RIGHT45 = [np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        for i in range(record):
            LEFT45 = np.random.randint(0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1) 
            FRONT = np.random.randint(np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.UNLIMIT) 
            RIGHT45 = np.random.randint(np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1)
            sensors = [LEFT45,FRONT,RIGHT45]
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

        ########################################
        # CONTROL_NUMBER=11
        # 範囲:[18<=LEFT45<=60][100<FRONT][RIGHT45<18]
        # 範囲:[18<=LEFT45<=60][19<=FRONT<=100][RIGHT45<18]
        # 境界値:[18,60][100,1000][0,18]
        # 境界値:[18,60][19,100][0,18]
        ########################################
        BOUNDARY_LEFT45 = [np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
        BOUNDARY_FRONT = [np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.FRONT_MAX_DRIVE_CONTROL_DISTANCE,self.UNLIMIT]
        BOUNDARY_RIGHT45 = [0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)]
        BOUNDARY_LEFT45 = self.fill_boundary_point(BOUNDARY_LEFT45)
        BOUNDARY_FRONT = self.fill_boundary_point(BOUNDARY_FRONT)
        BOUNDARY_RIGHT45 = self.fill_boundary_point(BOUNDARY_RIGHT45)
        self.mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

        for i in range(record):
            LEFT45 = np.random.randint(np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(self.LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1) 
            FRONT = np.random.randint(np.ceil(self.FRONT_MIN_DRIVE_CONTROL_DISTANCE),self.UNLIMIT) 
            RIGHT45 = np.random.randint(0,np.ceil(self.LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1)
            self.mk_sensor_data([LEFT45],[FRONT],[RIGHT45])


        # for debug
        for i in range(11):
            print("CONTROL_NUMBER={}:{}").format(i+1,self.CONTROL[i])

        np.savetxt("car_sensor_data.csv",self.CSVDATA,delimiter=",",header="left45_sensor,front_sensor,right45_sensor,stop,left,forward,right",fmt='%d')

