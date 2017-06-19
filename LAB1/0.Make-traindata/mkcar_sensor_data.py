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

# 車両全幅(cm)
OVERALL_WIDTH=18.0
# ホイールベース + ノーズ(cm)
WHEELBASE=27.0 + 12.0
# 最小回転半径(cm)
TURNING_CIRCLE=60 # 旋回半径
LEFT45_MAX_DRIVE_CONTROL_DISTANCE=TURNING_CIRCLE/np.sqrt(2) + OVERALL_WIDTH # 幅調整開始距離 45度斜め距離60.4264cm,真横42.72792cm
RIGHT45_MAX_DRIVE_CONTROL_DISTANCE=LEFT45_MAX_DRIVE_CONTROL_DISTANCE
FRONT_MAX_DRIVE_CONTROL_DISTANCE=100
# 旋回禁止距離定義
LEFT45_MIN_DRIVE_CONTROL_DISTANCE=OVERALL_WIDTH # 幅調整禁止距離 真横12.7279cm 左には曲がれない距離
RIGHT45_MIN_DRIVE_CONTROL_DISTANCE=OVERALL_WIDTH # 幅調整禁止距離 真横12.7279cm 右には曲がれない距離
# 絶対停止距離定義　前方障害物回避は左右フロントバンパーがこすらなければよい
x=np.sqrt(np.power(TURNING_CIRCLE,2)-np.power(WHEELBASE,2))
a=(TURNING_CIRCLE-OVERALL_WIDTH/2-(TURNING_CIRCLE-x))
y=np.sqrt(np.power(TURNING_CIRCLE,2)-np.power(a,2))
z=y-WHEELBASE
FRONT_MIN_DRIVE_CONTROL_DISTANCE=z+10 # 8.5471 全面に障害物があり、曲がってもぶつかる前方障害物までの距離。停止のために10cmおまけで追加しておく

RECORD=100 # 各分岐パターンの生成データ件数

print("車両幅:{}".format(OVERALL_WIDTH))
print("最小回転半径:{}".format(TURNING_CIRCLE))
print("左右制御開始距離:{} (左右幅調整開始距離)".format(LEFT45_MAX_DRIVE_CONTROL_DISTANCE))
print("前方制御開始距離:{} (旋回開始距離)".format(FRONT_MAX_DRIVE_CONTROL_DISTANCE))
print("左右旋回禁止距離:{} (曲がれない距離)".format(LEFT45_MIN_DRIVE_CONTROL_DISTANCE))
print("絶対停止距離:{} (曲がってもぶつかる前方障害物までの距離)".format(FRONT_MIN_DRIVE_CONTROL_DISTANCE))

'''
return 
  0:安全範囲につき制御不要
  1:危険範囲につき制御が必要
  2:曲がれない
'''
def left45_control(LEFT45_SENSOR_DISTANCE):
    # 安全範囲
    if LEFT45_MAX_DRIVE_CONTROL_DISTANCE < LEFT45_SENSOR_DISTANCE:
        return 0
    # 制御範囲
    if LEFT45_MIN_DRIVE_CONTROL_DISTANCE <= LEFT45_SENSOR_DISTANCE and LEFT45_SENSOR_DISTANCE <= LEFT45_MAX_DRIVE_CONTROL_DISTANCE:
        return 1
    # 旋回禁止範囲
    if LEFT45_SENSOR_DISTANCE < LEFT45_MIN_DRIVE_CONTROL_DISTANCE:
        return 2
'''
return 
  0:安全範囲につき制御不要
  1:危険範囲につき制御が必要
  2:曲がれない
'''
def right45_control(RIGHT45_SENSOR_DISTANCE):
    # 安全範囲
    if RIGHT45_MAX_DRIVE_CONTROL_DISTANCE < RIGHT45_SENSOR_DISTANCE:
        return 0
    # 制御範囲
    if RIGHT45_MIN_DRIVE_CONTROL_DISTANCE <= RIGHT45_SENSOR_DISTANCE and RIGHT45_SENSOR_DISTANCE <= RIGHT45_MAX_DRIVE_CONTROL_DISTANCE:
        return 1
    # 旋回禁止範囲
    if RIGHT45_SENSOR_DISTANCE < RIGHT45_MIN_DRIVE_CONTROL_DISTANCE:
        return 2
'''
return 
  0:安全範囲につき制御不要
  1:危険範囲につき制御が必要
  2:曲がれない
'''
def front_control(FRONT_SENSOR_DISTANCE):
    # 安全範囲
    if FRONT_MAX_DRIVE_CONTROL_DISTANCE < FRONT_SENSOR_DISTANCE:
        return 0
    # 制御範囲
    if FRONT_MIN_DRIVE_CONTROL_DISTANCE <= FRONT_SENSOR_DISTANCE and FRONT_SENSOR_DISTANCE <= FRONT_MAX_DRIVE_CONTROL_DISTANCE:
        return 1
    # 停止範囲
    if FRONT_SENSOR_DISTANCE < FRONT_MIN_DRIVE_CONTROL_DISTANCE:
        return 2


'''
sensors=[LEFT45_SENSOR_DISTANCE,FRONT_SENSOR_DISTANCE,RIGHT45_SENSOR_DISTANCE]
'''
def driving_instruction(sensors):

    LEFT45_CONTROL = left45_control(sensors[0])
    FRONT_CONTROL = front_control(sensors[1])
    RIGHT45_CONTROL = right45_control(sensors[2])

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


CONTROL=np.zeros(11)
hh=[]
'''for debug'''
#sensors = [LEFT45_MIN_DRIVE_CONTROL_DISTANCE-1,100,100]
#w = driving_instruction(sensors)
#if w[4] == 1:
#    print("error occured")
#print(np.hstack((sensors,w[0:4])))
#ww = np.hstack((sensors,w[0:4]))
#hh.append(ww)
#CONTROL[w[5]-1]+=1
 
#for i in range(100):
#    sensors = np.random.randint(0,51,3) 
#    w = driving_instruction(sensors)
#    if w[4] == 1:
#        print("error occured")
#    ww = np.hstack((sensors,w[0:4]))
#    hh.append(ww)
#    CONTROL[w[5]-1]+=1

#8=np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE)-1
#9=np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE)
#17=np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1
#18=np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)
#60=np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1
#61=np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)
#100=FRONT_MAX_DRIVE_CONTROL_DISTANCE
#101=FRONT_MAX_DRIVE_CONTROL_DISTANCE+1
UNLIMIT=1000


########################################
# データ生成
########################################
# 境界値に±1を加えた値を返す
def fill_boundary_point(boundary):
    # boundaryに±1の値を追加する
    for i in range(len(boundary)):
        PLUS=boundary[i]+1
        MINUS=boundary[i]-1
        boundary.append(PLUS)
        if MINUS >= 0:
            boundary.append(MINUS)
    return boundary
# センサーデータを作成する
def mk_sensor_data(LEFT45,FRONT,RIGHT45):
    global w
    global ww
    global hh
    global CONTROL
    for i in range(len(LEFT45)):
        for j in range(len(FRONT)):
            for k in range(len(RIGHT45)):
                sensors = [LEFT45[i],FRONT[j],RIGHT45[k]]
                w = driving_instruction(sensors)
                if w[4] == 1:
                    print("error occured")
                ww = np.hstack((sensors,w[0:4]))
                hh.append(ww)
                CONTROL[w[5]-1]+=1    

########################################
# CONTROL_NUMBER=1
# 範囲:[FRONT<19]
# 境界値:[0,1000][19±1][0,1000]
########################################
BOUNDARY_LEFT45 = [0,UNLIMIT]
BOUNDARY_FRONT = [np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE)]
BOUNDARY_RIGHT45 = [0,UNLIMIT]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
# 境界データを作成する
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

# 全域
for i in range(RECORD):
    LEFT45 = np.random.randint(0,UNLIMIT) 
    FRONT = np.random.randint(0,np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE)-1) 
    RIGHT45 = np.random.randint(0,UNLIMIT)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

########################################
# CONTROL_NUMBER=2or3
# 範囲:[60<LEFT45][19<=FRONT<=100][60<RIGHT45]
# 範囲:[60<LEFT45][19<=FRONT<=100][18<=RIGHT45<=60]
# 境界値:[60,1000][19,100],[60,1000]
# 境界値:[60,1000][19,100],[18,60]
########################################
BOUNDARY_LEFT45 = [np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,UNLIMIT]
BOUNDARY_FRONT = [np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),FRONT_MAX_DRIVE_CONTROL_DISTANCE]
BOUNDARY_RIGHT45 = [np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,UNLIMIT]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

for i in range(RECORD*2): # 2or3の分岐なので2倍にしておく
    LEFT45 = np.random.randint(np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE),UNLIMIT) 
    FRONT = np.random.randint(np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),FRONT_MAX_DRIVE_CONTROL_DISTANCE) 
    RIGHT45 = np.random.randint(np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),UNLIMIT)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

########################################
# CONTROL_NUMBER=4
# 範囲:[60<LEFT45][100<FRONT][60<RIGHT45]
# 境界値:[60,1000][100,1000][60,1000]
########################################
BOUNDARY_LEFT45 = [np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,UNLIMIT]
BOUNDARY_FRONT = [FRONT_MAX_DRIVE_CONTROL_DISTANCE,UNLIMIT]
BOUNDARY_RIGHT45 = [np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,UNLIMIT]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

for i in range(RECORD):
    LEFT45 = np.random.randint(np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE),UNLIMIT) 
    FRONT = np.random.randint(FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,UNLIMIT) 
    RIGHT45 = np.random.randint(np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE),UNLIMIT)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

########################################
# CONTROL_NUMBER=5
# 範囲:[18<=LEFT45<=60][100<FRONT][60<RIGHT45]
# 範囲:[LEFT45<18][100<FRONT][60<RIGHT45]
# 境界値:[18,60][100,1000][60,1000]
# 境界値:[0,18][100,1000][60,1000]
########################################
BOUNDARY_LEFT45 = [0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
BOUNDARY_FRONT = [FRONT_MAX_DRIVE_CONTROL_DISTANCE,UNLIMIT]
BOUNDARY_RIGHT45 = [np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,UNLIMIT]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

for i in range(RECORD/2):
    LEFT45 = np.random.randint(np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1) 
    FRONT = np.random.randint(FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,UNLIMIT) 
    RIGHT45 = np.random.randint(np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE),UNLIMIT)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])
for i in range(RECORD/2):
    LEFT45 = np.random.randint(0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1) 
    FRONT = np.random.randint(FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,UNLIMIT) 
    RIGHT45 = np.random.randint(np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE),UNLIMIT)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

########################################
# CONTROL_NUMBER=6
# 範囲:[60<LEFT45][100<FRONT][18<=RIGHT45<=60]
# 範囲:[60<LEFT45][100<FRONT][RIGHT45<18]
# 範囲:[60<LEFT45][19<=FRONT<=100][RIGHT45<18]
# 境界値:[60,1000][100,1000][18,60]
# 境界値:[60,1000][100,1000][0,18]
# 境界値:[60,1000][19,100][0,18]
########################################
BOUNDARY_LEFT45 = [np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1,UNLIMIT]
BOUNDARY_FRONT = [np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),FRONT_MAX_DRIVE_CONTROL_DISTANCE,UNLIMIT]
BOUNDARY_RIGHT45 = [0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

for i in range(RECORD/2):
    LEFT45 = np.random.randint(np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE),UNLIMIT) 
    FRONT = np.random.randint(FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,UNLIMIT) 
    RIGHT45 = np.random.randint(0,np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])
for i in range(RECORD/2):
    LEFT45 = np.random.randint(np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE),UNLIMIT) 
    FRONT = np.random.randint(np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),FRONT_MAX_DRIVE_CONTROL_DISTANCE) 
    RIGHT45 = np.random.randint(0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

########################################
# CONTROL_NUMBER=7
# 範囲:[LEFT45<18][19<=FRONT<=100][RIGHT45<18]
# 範囲:[LEFT45<18][FRONT<100][RIGHT45<18]
# 境界値:[0,18][19,100][0,18]
# 境界値:[0,18][0,100][0,18]
########################################
BOUNDARY_LEFT45 = [0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)]
BOUNDARY_FRONT = [0,np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),FRONT_MAX_DRIVE_CONTROL_DISTANCE]
BOUNDARY_RIGHT45 = [0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

for i in range(RECORD):
    LEFT45 = np.random.randint(0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1) 
    FRONT = np.random.randint(np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),UNLIMIT) 
    RIGHT45 = np.random.randint(0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

########################################
# CONTROL_NUMBER=8or9
# 範囲:[18<=LEFT45<=60][100<FRONT][18<=RIGHT45<=60]
# 境界値:[18,60][100,1000][18,60]
########################################
BOUNDARY_LEFT45 = [0,np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
BOUNDARY_FRONT = [FRONT_MAX_DRIVE_CONTROL_DISTANCE,UNLIMIT]
BOUNDARY_RIGHT45 = [np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

for i in range(RECORD*2):
    LEFT45 = np.random.randint(np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1) 
    FRONT = np.random.randint(FRONT_MAX_DRIVE_CONTROL_DISTANCE+1,UNLIMIT) 
    RIGHT45 = np.random.randint(np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

########################################
# CONTROL_NUMBER=10
# 範囲:[LEFT45<18][100<FRONT][18<=RIGHT45<=60]
# 範囲:[LEFT45<18][19<=FRONT<=100][18<=RIGHT45<=60]
# 境界値:[0,18][100,1000][18,60]
# 境界値:[0,18][19,100][18,60]
########################################
BOUNDARY_LEFT45 = [0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)]
BOUNDARY_FRONT = [np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),FRONT_MAX_DRIVE_CONTROL_DISTANCE,UNLIMIT]
BOUNDARY_RIGHT45 = [np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

for i in range(RECORD):
    LEFT45 = np.random.randint(0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1) 
    FRONT = np.random.randint(np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),UNLIMIT) 
    RIGHT45 = np.random.randint(np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1)
    sensors = [LEFT45,FRONT,RIGHT45]
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])

########################################
# CONTROL_NUMBER=11
# 範囲:[18<=LEFT45<=60][100<FRONT][RIGHT45<18]
# 範囲:[18<=LEFT45<=60][19<=FRONT<=100][RIGHT45<18]
# 境界値:[18,60][100,1000][0,18]
# 境界値:[18,60][19,100][0,18]
########################################
BOUNDARY_LEFT45 = [np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1]
BOUNDARY_FRONT = [np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),FRONT_MAX_DRIVE_CONTROL_DISTANCE,UNLIMIT]
BOUNDARY_RIGHT45 = [0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)]
BOUNDARY_LEFT45 = fill_boundary_point(BOUNDARY_LEFT45)
BOUNDARY_FRONT = fill_boundary_point(BOUNDARY_FRONT)
BOUNDARY_RIGHT45 = fill_boundary_point(BOUNDARY_RIGHT45)
mk_sensor_data(BOUNDARY_LEFT45,BOUNDARY_FRONT,BOUNDARY_RIGHT45)

for i in range(RECORD):
    LEFT45 = np.random.randint(np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE),np.ceil(LEFT45_MAX_DRIVE_CONTROL_DISTANCE)-1) 
    FRONT = np.random.randint(np.ceil(FRONT_MIN_DRIVE_CONTROL_DISTANCE),UNLIMIT) 
    RIGHT45 = np.random.randint(0,np.ceil(LEFT45_MIN_DRIVE_CONTROL_DISTANCE)-1)
    mk_sensor_data([LEFT45],[FRONT],[RIGHT45])


# for debug
for i in range(11):
    print("CONTROL_NUMBER={}:{}").format(i+1,CONTROL[i])

np.savetxt("car_sensor_data.csv",hh,delimiter=",",header="left45_sensor,front_sensor,right45_sensor,stop,left,forward,right",fmt='%d')

