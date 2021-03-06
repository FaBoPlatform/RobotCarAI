<a name='top'>

# レベル1：Fabo TYPE1 ロボットカー制御
<hr>

## 目標
3つの距離センサーから値を取得し、IF文で進行方向を判断してロボットカーを自走させる

## 画像
![](./document/img1.jpg)
![](./document/robotcar.jpg)

## 動画
走行デモ動画：[![走行デモ動画](https://img.youtube.com/vi/aGF8QZeBsto/2.jpg)](https://www.youtube.com/watch?v=aGF8QZeBsto)<br>

## 実行環境
* Fabo TYPE1 ロボットカー<br>
    * Fabo #605 Motor Shield Raspberry Pi Rev 1.0.1<br>
    * Fabo #902 Kerberos ver 1.0.0<br>
    * Fabo #1202 Robot Car Rev. 1.0.1<br>
    * Fabo #103 Button<br>
    * VL53L0X or Lidar Lite v3<br>
    * Tower Pro SG90<br>
    * Raspberry Pi3<br>
        * Stretch Lite or Jessie Lite<br>
        * docker<br>
            * Ubuntu<br>
            * Python 2.7<br>
            * FaBoPWM-PCA9685-Python<br>
            * FaBoGPIO-PCAL6408-Python<br>
            * VL53L0X_rasp_python<br>

<hr>

<a name='0'>

## 実行
* [インストール方法](#a)<br>
* [コースの準備](#course)<br>
* [実行方法](#b)<br>

## 目次
* [Hardware] [距離センサーLidarLite v3について](#l1)<br>
    * 取得できる距離、値、誤差、測定周期<br>
* [Python] [簡単なIF文での判定を作る](#l2)<br>
    * 簡単なIF文での判定<br>
* [Python] [車両を制御する](#l3)<br>
    * モーターの速度制御<br>
    * ハンドル制御<br>
* [Python] [距離センサーの値を取る](#l4)<br>
    * 距離センサーの値を取る<br>
* [Python] [自走コードを作成する](#l5)<br>
    * 距離センサーの値を取る<br>
    * 進行方向を判断する<br>
    * 速度調整を入れる<br>
    * ハンドル角調整を入れる<br>
    * 車両を制御する<br>
    * 後進を追加する<br>
    * 停止ボタンを追加する<br>
    * 開始ボタンを追加する<br>
* [ディレクトリとファイルについて](#l6)<br>
<hr>

<a name='a'>

## インストール方法
インストール済みのロボットカーを用意しているので省略します。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='course'>

## コースの準備
コースとなる壁は、距離センサーが発するレーザーが反射できるような素材で作ります。<br>
足元での突起物となるので、人がぶつかった時の安全性や価格、レイアウト変更のしやすさ、修復しやすさを考えて画用紙とクリップで作ってあります。<br>
ジグザグに織ることで、収納しやすさ、立たせやすさ、レイアウト変更のしやすさ、レーザー反射しやすさも獲得しています。<br>
道幅は直線なら狭くても大丈夫ですが、カーブでは側面にセンサーが付いていないため、内側を巻き込みやすくなっています。<br>
そのため、カーブは広めに作り、狭い道への入り口も誘導しやすいように広めに作っておきます。<br>

![](./document/img1.jpg)<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='b'>

## 実行方法
#### 1. ロボットカーのRaspberry Pi3にログインします
USER:pi<br>
PASSWORD:raspberry<br>
> `ssh pi@192.168.xxx.xxx`<br>

#### 2. rootになってdockerコンテナIDを調べます
> `sudo su`<br>
> `docker ps -a`<br>
>> CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS                     PORTS                                                                    NAMES<br>
>> 2133fa3ca362        naisy/fabo-jupyter-armhf   "/bin/bash -c 'jup..."   3 weeks ago         Up 2 minutes               0.0.0.0:6006->6006/tcp, 0.0.0.0:8091->8091/tcp, 0.0.0.0:8888->8888/tcp   hardcore_torvalds<br>

STATUSがUpになっているコンテナIDをメモします。

#### 3. dockerコンテナにログインします
docker exec -it CONTAINER_ID /bin/bash<br>
> `docker exec -it 2133fa3ca362 /bin/bash`<br>

CONTAINER_IDにはベースイメージがnaisy/fabo-jupyter-armhfの2133fa3ca362を使います。<br>

#### 4. ロボットカーのディレクトリに移動します

> `cd /notebooks/github/RobotCarAI/level1_car/`<br>
> `ls`<br>
>> total 60<br>
>> 160688  4 ./   125618 16 README.md  160720  4 fabolib/    160809  4 lib/           127092  4 start_button.py<br>
>> 123628  4 ../  160708  4 document/  160808  4 generator/  127056 12 run_car_if.py  160810  4 test/<br>

#### 5. ロボットカーを起動します
> `python start_button.py`<br>

#### 6. 走行開始するには、ロボットカーの青いボタンを押します
![](./document/img2.jpg)

#### 7. 走行停止するには、ロボットカーの赤いボタンを押します
![](./document/img3.jpg)<br>
Ctrl + c でstart_button.pyを終了します

#### 8. ソースコードを修正して、ロボットカーを再度走らせます
進行方向の判断処理を変更して、ロボットカーを走らせてみます。<br>
> `vi run_car_if.py`<br>

ソースコード：[./run_car_if.py](./run_car_if.py)<br>
```python
# 書き換え前 シンプルな判断処理を読み込む
from generator.simplelabelgenerator import SimpleLabelGenerator as LabelGenerator
#from generator.labelgenerator import LabelGenerator

# 書き換え後 複雑な判断処理を読み込むように、#を入れ替えてコメントアウトを変更
#from generator.simplelabelgenerator import SimpleLabelGenerator as LabelGenerator
from generator.labelgenerator import LabelGenerator
```
走行は5.6.7.の手順になります。<br>

#### viエディタについて
viエディタは初期のUNIXからあるテキストエディタです。しかし、2002年までは自由に入手出来なかったため、フリーのviライクのエディタが登場しました。その中でもvimは多くのOSに移植され、Ubuntuではviコマンドはvimを起動します。<br>
UNIX系のサーバ設定ファイルを手で書き換える時は、どのサーバでも使えるという点からviコマンドを使うので、簡単な使い方を覚えておきます。<br>

* コマンドモードと編集モードの切り替え (vi起動時はコマンドモード)<br>
編集モードに切り替え：コマンドモード時、'i'もしくは'a'もしくは'o'を押す<br>
コマンドモードに切り替え：編集モード時、'ESC'を押す<br>
* 保存して終了<br>
コマンドモード時、':wq'を押す<br>
* 保存せずに終了<br>
コマンドモード時、':!q'を押す<br>
* 検索<br>
コマンドモード時、'/検索したい文字列'を押す<br>


#### これ以降について
level1_carでは、ロボットカーの制御方法についての内容になります。<br>
level1_sensorsでは、書き換え後となるLabelGeneratorの進行方向の判断処理についてと、その判断をニューラルネットワークに覚えさせる内容になります。<br>
level1_demoでは、ニューラルネットワークで判断処理を行い、ロボットカーを制御する内容になります。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l1'>

## [Hardware] 距離センサーLidarLite v3について
CLASS1 LASERで距離を計測する機器。
#### 取得できる距離、値、誤差、測定周期
  * 測定可能距離は40m<br>
  * cm単位の整数値で取得<br>
  * 測定誤差は5m以内で2.5cm、5m以上で10cm<br>
  * 測定周期は50Hz=0.02秒間隔<br>

仕様書：[https://static.garmin.com/pumac/LIDAR_Lite_v3_Operation_Manual_and_Technical_Specifications.pdf](https://static.garmin.com/pumac/LIDAR_Lite_v3_Operation_Manual_and_Technical_Specifications.pdf)

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l2'>

## [Python] 簡単なIF文での判定を作る
#### 簡単なIF文での判定
3センサー値を入力に、STOP,LEFT,FOWARD,RIGHTを識別出来るように値を返すIF文を作ります。<br>
0:STOP,1:LEFT,2:FOWARD,3:RIGHTと定義しますが、level1_sensorsのNeural Networksのone hot valueの値に合わせておくために、<br>
[1,0,0,0]:STOP,[0,1,0,0]:LEFT,[0,0,1,0]:FOWARD,[0,0,0,1]:RIGHTとして値を返しておきます。<br>
one hot value(配列)の最大値を持つindex番号が0-3の値(0:STOP,1:LEFT,2:FOWARD,3:RIGHT)となります。<br>
```python
value = np.argmax([1,0,0,0]) # value = 0
```
ラベル ジェネレータ：[./generator/simplelabelgenerator.py](./generator/simplelabelgenerator.py)<br>
```python
# coding: utf-8
import numpy as np
class SimpleLabelGenerator():
    def get_label(self,sensors):
        '''
        sensors: [左センサー値,前センサー値,右センサー値]
        '''

        if sensors[1] < 20: # 前方に空きが無い
            return [1,0,0,0] # STOP
        elif sensors[0] < 20: # 左に空きが無い
            return [0,0,0,1] # RIGHT
        elif sensors[2] < 20: # 右に空きが無い
            return [0,1,0,0] # LEFT
        else: # 全方向に空きがある
            return [0,0,1,0] # FOWARD

generator = SimpleLabelGenerator()
n_rows = 10 # 作成するデータ件数
sensors = np.random.randint(0,200,[n_rows,3]) # 範囲0-200の値で3つの値を持つ配列をn_rows個作る
print("--- sensors ---\n{}".format(sensors))
csvdata=[]
for i in range(n_rows):
    generator_result = generator.get_label(sensors[i])
    csvrow = np.hstack((sensors[i],generator_result))
    csvdata.append(csvrow)
csvdata = np.array(csvdata)
print("--- batch data ---\n{}".format(csvdata))
```
>--- sensors ---<br>
> [[123  76 172]<br>
>  [ 12  74  98]<br>
>  [ 52  59  45]<br>
>  [ 51 137 147]<br>
>  [  8  45  58]<br>
>  [ 87 176 189]<br>
>  [183  34 197]<br>
>  [115   4 100]<br>
>  [108 154 136]<br>
>  [140  53 101]]<br>
> --- batch data ---<br>
> [[123  76 172   0   0   1   0]<br>
>  [ 12  74  98   1   0   0   0]<br>
>  [ 52  59  45   0   1   0   0]<br>
>  [ 51 137 147   0   0   1   0]<br>
>  [  8  45  58   1   0   0   0]<br>
>  [ 87 176 189   0   0   1   0]<br>
>  [183  34 197   0   0   0   1]<br>
>  [115   4 100   0   0   0   1]<br>
>  [108 154 136   0   0   1   0]<br>
>  [140  53 101   0   0   1   0]]<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l3'>

## [Python] 車両を制御する
#### モーターの速度制御
車両動作確認コード：[./test/car_test.py](./test/car_test.py)<br>
```python
from fabolib.car import Car
car = Car()
try:
    for i in range(1,101):
        car.forward(i)
        time.sleep(0.1)
    car.stop()

    #モーターが惰性を含めて回転中は逆回転にすることが出来ないため、sleepを入れておく
    time.sleep(1)

    for i in range(1,101):
        car.back(i)
        time.sleep(0.1)
    car.stop()
```
モーターの速度は1から100までの値で制御できます。<br>
しかし、値が低いとモーターが動作しないため、進む際は40以上の値を設定します。<br>
前進、後進、停止が可能です。<br>
急に逆回転にするとモーターが回らなくなるため、逆回転にする場合は、モーターの回転が止まるまでsleepを入れておきます。

<hr>

#### ハンドル制御
車両動作確認コード：[./test/car_test.py](./test/car_test.py)<br>
```python
from fabolib.car import Car
car = Car()
try:
    car.set_angle(90)
    time.sleep(1)
    car.set_angle(45)
    time.sleep(1)
    car.set_angle(90)
    time.sleep(1)
    car.set_angle(135)
    time.sleep(1)
    car.set_angle(90)
```
ハンドル制御は45-135度の角度で指定します。<br>
0-180度まで動作するサーボを使っていますが、真ん中の90度の位置でロボットカーを組み立てる必要があります。<br>
ここは車両に合わせて微調整が必要になります。<br>

パラメータ設定：[./fabolib/config.py](./fabolib/config.py)<br>
```python
class CarConfig():
    HANDLE_NEUTRAL = 95 # ステアリングニュートラル位置
    HANDLE_ANGLE = 42 # 左右最大アングル
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l4'>

## [Python] 距離センサーの値を取る
距離センサーにはFabo #224 Distanceを使います。<br>
今回3つの距離センサーを使うのですが、全てのセンサーは通電時に同じ物理アドレスとなっていますので、それぞれのアドレスを変更する必要があります。<br>
このアドレス変更を自動的に行うために、Fabo #902 Kerberos基板を使ってアドレス変更を行ったうえで取得するライブラリを作成してあります。<br>

距離センサーFabo #224 Distance用ライブラリ：[./fabolib/kerberos_vl53l0x.py](./fabolib/kerberos_vl53l0x.py)<br>
距離センサーLidarLite v3用ライブラリ：[./fabolib/kerberos.py](./fabolib/kerberos.py)<br>
距離取得確認コード：[./test/fabolib_kerberos_test.py](./test/fabolib_kerberos_test.py)<br>
```python
from fabolib.kerberos_vl53l0x import KerberosVL53L0X as Kerberos
kerberos = Kerberos()
try:
    for i in range(0,300):
        distance1,distance2,distance3 = kerberos.get_distance()
```
このコードを実行するには、Fabo #902 Kerberos基板とFabo #224 Distanceが必要になります。<br>
LidarLite v3を使っている場合は、import部分を以下のように変更してください。<br>
```python
from fabolib.kerberos import Kerberos
#from fabolib.kerberos_vl53l0x import KerberosVL53L0X as Kerberos
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l5'>

## [Python] 自走コードを作成する
#### 距離センサーの値を取る
距離センサーは0.02秒間隔で値が更新されるので、値を取ったら余裕を持って0.05秒のsleepを入れておきます。<br>
車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
    # 近接センサー準備
    kerberos = Kerberos()
    LIDAR_INTERVAL = 0.05 # 距離センサー取得間隔 sec
...
    try:
        while main_thread_running:
...
            ########################################
            # 近接センサー値を取得する
            ########################################
            distance1,distance2,distance3 = kerberos.get_distance()
            sensors = [distance1,distance2,distance3]
...
            time.sleep(LIDAR_INTERVAL)

    except:
```
<hr>

#### 進行方向を判断する
車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
from generator.simplelabelgenerator import SimpleLabelGenerator as LabelGenerator
#from generator.labelgenerator import LabelGenerator
...
    # IF準備 (学習ラベル ジェネレータ)
    generator = LabelGenerator()
...
            ########################################
            # IF結果を取得する
            ########################################
            # 今回の結果を取得する
            generator_result = generator.get_label(sensors)
            if_value = np.argmax(generator_result)
```
簡単なIF文を判定に使っていますが、level1_sensorsのIF文も使うことが出来ます。<br>
```python
#from generator.simplelabelgenerator import SimpleLabelGenerator as LabelGenerator
from generator.labelgenerator import LabelGenerator
```
<hr>

#### 速度調整を入れる
常に全力走行だとぶつかりやすいため、取得した前方距離から速度を調整を入れます。<br>
低すぎる値だと車両が進まなくなるため、最低速度を40にしています。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
            ########################################
            # 速度調整を行う
            ########################################
            if distance2 >= 100:
                # 前方障害物までの距離が100cm以上ある時、速度を最大にする
                speed = 100
            else:
                # 前方障害物までの距離が100cm未満の時、速度を調整する
                speed = int(distance2)
                if speed < 40:
                    speed = 40
```
<hr>

#### ハンドル角調整を入れる
常に全開でハンドルを切るとジグザク走行になってしまうため、距離からハンドル角の調整を入れます。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
            ########################################
            # ハンドル角調整を行う
            ########################################
            if if_value == 1: # 左に行くけど、左右スペース比で舵角を制御する
                if distance1 > 100: # 左空間が非常に大きい時、ratio制御向けに最大値を設定する
                    distance1 = 100
                if distance3 > distance1: # raitoが1.0を超えないように確認する
                    distance3 = distance1
                ratio = (float(distance1)/(distance1 + distance3) -0.5) * 2 # 角度をパーセント減にする
                if distance2 < 100:
                    ratio = 1.0
            elif if_value == 3: # 右に行くけど、左右スペース比で舵角を制御する
                if distance3 > 100: # 右空間が非常に大きい時、ratio制御向けに最大値を設定する
                    distance3 = 100
                if distance1 > distance3: # raitoが1.0を超えないように確認する
                    distance3 = distance1
                ratio = (float(distance3)/(distance1 + distance3) -0.5) * 2 # 角度をパーセント減にする
                if distance2 < 100:
                    ratio = 1.0
            else:
                ratio = 1.0
```
<hr>

#### 車両を制御する
進行方向の判断結果と、速度調整、ハンドル角調整を行った値で車両を制御します。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
            ########################################
            # ロボットカーを 前進、左右、停止 する
            ########################################
            if if_value == STOP:
                car.stop()
                car.set_angle(HANDLE_NEUTRAL)
            elif if_value == LEFT:
                car.set_angle(HANDLE_NEUTRAL - (HANDLE_ANGLE * ratio))
                car.forward(speed)
            elif if_value == FORWARD:
                car.forward(speed)
                car.set_angle(HANDLE_NEUTRAL)
            elif if_value == RIGHT:
                car.set_angle(HANDLE_NEUTRAL + (HANDLE_ANGLE * ratio))
                car.forward(speed)
```
<hr>

#### 後進を追加する
カーブを曲がりきれなかったり、行き止まりになった時のために、止まったら後進するようにします。<br>
このロボットカーは後ろにセンサーが付いていないため、後進はあまりうまくは出来ません。<br>
今回はとりあえず真っ直ぐ後進して、その後ハンドルを切るようにします。<br>
それでも曲がれるスペースが見つからない時は、スペースが見つかるまで適当に後進するようにします。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
            ########################################
            # もし停止なら、ロボットカーを後進する
            ########################################
            '''
            バック時、直前のハンドルログからN件分を真っ直ぐバックし、M件分を逆ハンドルでバックする
            その後、狭い方にハンドルを切ってバックする
            '''
            if if_value == STOP:
                time.sleep(1) # 停止後1秒、車体が安定するまで待つ
                if not stop_thread_running: break # 強制停止ならループを抜ける

                # バック時のハンドル操作キューを作成する
                copy_log_queue.queue = copy.deepcopy(log_queue.queue)

                # ハンドル操作キューが足りない時はバックハンドル操作を前進にする
                if log_queue.qsize() < MAX_LOG_LENGTH:
                    for i in range(log_queue.qsize(),MAX_LOG_LENGTH):
                        back_queue.put(FORWARD)

                while not log_queue.empty():
                    back_queue.put(log_queue.get(block=False))
                log_queue.queue = copy.deepcopy(copy_log_queue.queue)
...
            else:
                if not stop_thread_running: break # 強制停止ならループを抜ける
                # 前進の時は直前のハンドル操作を記憶する
                qsize = log_queue.qsize()
                if qsize >= MAX_LOG_LENGTH:
                    log_queue.get(block=False)
                    qsize = log_queue.qsize()
                log_queue.put(if_value)
```
<hr>

#### 停止ボタンを追加する
ロボットカーを止めるためのボタンを追加します。<br>
ボタン監視スレッドの作成と、車両制御ループを抜けるためのbreakを追加します。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
def do_stop_button():
    '''
    停止ボタンの値を取得し続ける関数
    '''
    global stop_thread_running
    global main_thread_running

    # 停止ボタン準備
    A0 = 0 # SPI PIN
    STOP_BUTTON_SPI_PIN = A0
    spi = SPI()

    while stop_thread_running:
        data = spi.readadc(STOP_BUTTON_SPI_PIN)
        if data >= 1000:
            # 停止ボタンが押された
            main_thread_running = False
            stop_thread_running = False
            break
        time.sleep(0.1)
    return
...
            if not stop_thread_running: break # 強制停止ならループを抜ける
...
if __name__ == '__main__':
    # 停止ボタンの状態を監視するスレッドを起動する
    t = threading.Thread(target=do_stop_button,args=())
    t.start()
    main()
```
<hr>

#### 開始ボタンを追加する
パソコンが無くてもロボットカーを開始出来るように開始ボタンを追加します。<br>

開始ボタンコード：[./start_button.py](./start_button.py)
```python
from lib.spi import SPI
# 開始ボタンのSPI接続コネクタ番号
A1 = 1
START_BUTTON_SPI_PIN = A1
spi = SPI()
proc = None

try:
    cmd = "python "+os.path.abspath(os.path.dirname(__file__))+"/run_car_if.py"
    while True:
        data = spi.readadc(START_BUTTON_SPI_PIN) # data: 0-1023
        if data >= 1000:
            print("start car")
            proc = Popen(cmd,shell=True)
            proc.wait()

        time.sleep(0.1)
```
ロボットカー起動時にこの開始ボタンを監視するプログラムを自動実行するように設定すれば、ロボットカーだけで動作するようになるため、デモ等でネットワークやパソコンが不要になります。

> `python start_button.py`<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l6'>

## ディレクトリとファイルについて
* ディレクトリについて<br>
    * document/ ドキュメント関連<br>
    * fabolib/ Fabo製基板関連<br>
    * generator/ 学習データのラベル生成関連<br>
    * lib/ SPIライブラリ<br>
    * test/ Fabo基板動作確認関連<br>
* ファイルについて<br>
    * README.md このファイル<br>
    * run_car_if.py 自動走行コード<br>
    * start_button.py 開始ボタンコード<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

