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
OVERALL_WIDTH=10.0
# 最小回転半径(cm)
TURNING_CIRCLE=20.0 # その場で回転が出来る
# [制動範囲最低距離]から[制動範囲最大距離]の間は制動運転を行う
# 停止 - [制動範囲最低距離] - 制動運転 - [制動範囲最大距離] - 直線番長
# 衝突回避距離定義(cm) [制動範囲最大距離]
LEFT45_MAX_DRIVE_CONTROL_DISTANCE=TURNING_CIRCLE/np.sqrt(2) + OVERALL_WIDTH # 45度斜め距離24.142cm,真横17.071cm
FRONT_MAX_DRIVE_CONTROL_DISTANCE=100
RIGHT45_MAX_DRIVE_CONTROL_DISTANCE=LEFT45_MAX_DRIVE_CONTROL_DISTANCE
# 完全停止距離定義 [制動範囲最低距離]
LEFT45_MIN_DRIVE_CONTROL_DISTANCE=OVERALL_WIDTH # 真横7.071cm 左には曲がれない
FRONT_MIN_DRIVE_CONTROL_DISTANCE=(TURNING_CIRCLE+OVERALL_WIDTH)/(2*(OVERALL_WIDTH/TURNING_CIRCLE)+(OVERALL_WIDTH/TURNING_CIRCLE)*(OVERALL_WIDTH/TURNING_CIRCLE)) + 2 # 24cm + 2cm 全面に障害物があり、曲がるとぶつかる距離になるなら停止する
RIGHT45_MIN_DRIVE_CONTROL_DISTANCE=OVERALL_WIDTH # 右には曲がれない


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
    # 停止範囲
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
    # 停止範囲
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
TODO: one_hot_value
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
    ラジコンは[LEFT45_CONTROL,FRONT_CONTROL,RIGHT45_CONTROL]が不要になるように機動する
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
    elif not LEFT45_CONTROL and not FRONT_CONTROL and not RIGHT45_CONTROL: # 制御不要
        FORWARD=1
        CONTROL_NUMBER=2
    elif LEFT45_CONTROL and not RIGHT45_CONTROL: # 右に曲がる
        RIGHT=1
        CONTROL_NUMBER=3
    elif not LEFT45_CONTROL and FRONT_CONTROL==1 and not RIGHT45_CONTROL: # 左右の大きい空間に曲がる
        if sensors[0] <= sensors[2]: # LEFT45_SENSOR_DISTANCE <= RIGHT45_SENSOR_DISTANCE
            RIGHT=1
            CONTROL_NUMBER=4
        else:
            LEFT=1
            CONTROL_NUMBER=5
    elif not LEFT45_CONTROL and RIGHT45_CONTROL: # 左に曲がる
        LEFT=1
        CONTROL_NUMBER=6
    elif LEFT45_CONTROL==2 and RIGHT45_CONTROL==2: # 直進する ここは量幅制御を諦めたため、事故死する可能性がある部分
        FORWARD=1
        CONTROL_NUMBER=7
    elif LEFT45_CONTROL==1 and RIGHT45_CONTROL==1: # 量幅調整しながら直進する
        if sensors[0] <= sensors[2]: # LEFT45_SENSOR_DISTANCE <= RIGHT45_SENSOR_DISTANCE
            RIGHT=1
            CONTROL_NUMBER=8
        else:
            LEFT=1
            CONTROL_NUMBER=9
    elif LEFT45_CONTROL==2 and RIGHT45_CONTROL==1: # 右に曲がる
        RIGHT=1
        CONTROL_NUMBER=10
    elif LEFT45_CONTROL==1 and RIGHT45_CONTROL==2: # 左に曲がる
        LEFT=1
        CONTROL_NUMBER=11

    if not (STOP+LEFT+FORWARD+RIGHT) == 1:
        #STOP=0
        #LEFT=0
        #FORWARD=0
        #RIGHT=0
        ERROR=1
    return [STOP,LEFT,FORWARD,RIGHT,ERROR,CONTROL_NUMBER]


'''for debug
sensors = [182,27,12]
w = driving_instruction(sensors)
if w[4] == 1:
    print("error occured")
print(np.hstack((sensors,w)))
'''
CONTROL=np.zeros(11)
hh=[]
#for i in range(10):
#    sensors = np.random.randint(0,51,3) 
#    w = driving_instruction(sensors)
#    if w[4] == 1:
#        print("error occured")
#    ww = np.hstack((sensors,w[0:4]))
#    hh.append(ww)
#    CONTROL[w[5]-1]+=1
for i in range(200000):
    sensors = np.random.randint(0,51,3) 
    w = driving_instruction(sensors)
    if w[4] == 1:
        print("error occured")
    ww = np.hstack((sensors,w[0:4]))
    hh.append(ww)
    CONTROL[w[5]-1]+=1
for i in range(100000):
    sensors = np.random.randint(11,51,3) 
    w = driving_instruction(sensors)
    if w[4] == 1:
        print("error occured")
    ww = np.hstack((sensors,w[0:4]))
    hh.append(ww)
    CONTROL[w[5]-1]+=1
for i in range(10000):
    sensors = np.random.randint(31,151,3) 
    w = driving_instruction(sensors)
    if w[4] == 1:
        print("error occured")
    ww = np.hstack((sensors,w[0:4]))
    hh.append(ww)
    CONTROL[w[5]-1]+=1
for i in range(10000):
    sensors = np.random.randint(101,401,3) 
    w = driving_instruction(sensors)
    if w[4] == 1:
        print("error occured")
    ww = np.hstack((sensors,w[0:4]))
    hh.append(ww)
    CONTROL[w[5]-1]+=1
for i in range(500000):
    sensors = np.random.randint(0,401,3) 
    w = driving_instruction(sensors)
    if w[4] == 1:
        print("error occured")
    ww = np.hstack((sensors,w[0:4]))
    hh.append(ww)
    CONTROL[w[5]-1]+=1
# for debug
for i in range(11):
    print(CONTROL[i])

np.savetxt("car_sensor_data.csv",hh,delimiter=",",fmt='%d')

