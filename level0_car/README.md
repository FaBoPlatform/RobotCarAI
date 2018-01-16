<a name='top'>

【タイトル】
# レベル0：Fabo TYPE1 ロボットカー制御
<hr>

【目標】
#### 3つの距離センサーから値を取得し、IF文で進行方向を判断してロボットカーを自走させる

【画像】
![](./document/robotcar.jpg)
実行環境の構成
* Fabo TYPE1 ロボットカー

<hr>

<a name='0'>

【目次】
* [Hardware] [距離センサーLidarLite v3について](#1)
  * 取得できる距離、値、誤差、測定周期
* [Python] [簡単なIF文での判定を作る](#2)
  * 簡単なIF文での判定
* [Python] [車両を制御する](#3)
  * モーターの速度制御
  * ハンドル制御
* [Python] [距離センサーの値を取る](#4)
  * 距離センサーの値を取る
* [Python] [自走コードを作成する](#5)
  * 距離センサーの値を取る
  * 進行方向を判断する
  * 速度調整を入れる
  * ハンドル角調整を入れる
  * 車両を制御する
  * バック機能を追加する
  * 終了ボタンを追加する
  * 開始ボタンを追加する
* [ディレクトリとファイルについて](#6)
<hr>

<a name='1'>

## [Hardware] 距離センサーLidarLite v3について
CLASS1 LASERで距離を計測する機器。
#### 取得できる距離、値、誤差、測定周期
  * 測定可能距離は40m
  * cm単位の整数値で取得
  * 測定誤差は5m以内で2.5cm、5m以上で10cm
  * 測定周期は50Hz=0.02秒間隔

仕様書：[https://static.garmin.com/pumac/LIDAR_Lite_v3_Operation_Manual_and_Technical_Specifications.pdf](https://static.garmin.com/pumac/LIDAR_Lite_v3_Operation_Manual_and_Technical_Specifications.pdf)

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='2'>

## [Python] 簡単なIF文での判定を作る
#### 簡単なIF文での判定
3センサー値を入力に、STOP,LEFT,FOWARD,RIGHTを識別出来るように値を返すIF文を作ります。<br>
0:STOP,1:LEFT,2:FOWARD,3:RIGHTと定義しますが、level1のNeural Networksのone hot valueの値に合わせておくために、<br>
[1,0,0,0]:STOP,[0,1,0,0]:LEFT,[0,0,1,0]:FOWARD,[0,0,0,1]:RIGHTとして値を返しておきます。<br>
0-3の値としては配列の最大値のindex番号となるため、numpyで取得することが出来ます。<br>
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

<a name='3'>

## [Python] 車両を制御する
#### モーターの速度制御
車両動作確認コード：[./test/car_test.py](./test/car_test.py)<br>
```python
from fabolib import Car
car = Car()
try:
    for i in range(1,101):
        car.forward(i)
        time.sleep(0.1)
    car.stop()

    for i in range(1,101):
        car.back(i)
        time.sleep(0.1)
    car.stop()
```
モーターの速度は1から100までの値で制御できます。<br>
しかし、値が低いとモーターが動作しないため、進む際は40以上の値を設定します。<br>
前進、後進、停止が可能です。

<hr>

#### ハンドル制御
車両動作確認コード：[./test/car_test.py](./test/car_test.py)<br>
```python
from fabolib import Car
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
値が範囲から外れるとパーツに負荷がかかるため、可動範囲の確認が重要になります。<br>
真ん中の位置が多少ずれていたりするので、最適な値への調整が必要になります。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
    HANDLE_NEUTRAL = 95 # ステアリングニュートラル位置
    HANDLE_ANGLE = 42 # 左右最大アングル
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='4'>

## [Python] 距離センサーの値を取る
距離センサーにはLidarLite v3を使います。<br>
今回3つの距離センサーを使うのですが、全てのセンサーは通電時に同じ物理アドレスとなっていますので、それぞれのアドレスを変更する必要があります。<br>
このアドレス変更を自動的に行うために、Fabo #902 Kerberos基板を使ってアドレス変更を行ったうえで取得しています。<br>
クラス化して簡単に使えるようにしてあります。<br>

距離センサー用ライブラリ：[./fabolib/kerberos.py](./fabo_lib/kerberos.py)<br>
距離取得確認コード：[./test/fabolib_kerberos_test.py](./test/fabolib_kerberos_test.py)<br>
```python
from fabolib import Kerberos
kerberos = Kerberos()
try:
    for i in range(0,300):
        distance1,distance2,distance3 = kerberos.get_distance()
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='5'>

## [Python] 自走コードを作成する
#### 距離センサーの値を取る
車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
    # 近接センサー準備
    kerberos = Kerberos()
    LIDAR_INTERVAL = 0.05
...
            ########################################
            # 近接センサー値を取得する
            ########################################
            distance1,distance2,distance3 = kerberos.get_distance()
            sensors = [distance1,distance2,distance3]
```
<hr>

#### 進行方向を判断する
車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
from generator import SimpleLabelGenerator as LabelGenerator
#from generator import LabelGenerator
...
    # IF準備 (学習ラベル ジェネレータ)
    generator = LabelGenerator()
...
            ########################################
            # IF結果を取得する
            ########################################
            # 今回の結果を取得する
            generator_result = generator.get_label(sensors)
            ai_value = np.argmax(generator_result)
```
level0の簡単なIF文での判定を使っていますが、level1では学習データ用にもう少し考慮したIF文を用意しています。<br>
level0でもimportを変えることで動作の違いを確認出来ます。<br>
```python
#from generator import SimpleLabelGenerator as LabelGenerator
from generator import LabelGenerator
```
<hr>

#### 速度調整を入れる
常に全力走行だとぶつかりやすいため、取得した前方距離から速度を調整する。<br>
低すぎる値だとパワー不足で停止してしまうため、最低速度を40にしておく。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
            ########################################
            # 速度調整を行う
            ########################################
            if distance2 >= 100:
                speed = 100
            else:
                speed = int(distance2 + (100 - distance2)/2)
                if speed < 40:
                    speed = 40
```
<hr>

#### ハンドル角調整を入れる
常に全開でハンドルを切るとジグザク走行になってしまうため、距離からハンドル角の調整を入れる。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
            ########################################
            # ハンドル角調整を行う
            ########################################
            if ai_value == 1: # 左に行くけど、左右スペース比で舵角を制御する
                if distance1 > 100: # 左空間が非常に大きい時、ratio制御向けに最大値を設定する
                    distance1 = 100
                if distance3 > distance1: # raitoが1.0を超えないように確認する
                    distance3 = distance1
                ratio = (float(distance1)/(distance1 + distance3) -0.5) * 2 # 角度をパーセント減にする
                if distance2 < 100:
                    ratio = 1.0
            elif ai_value == 3: # 右に行くけど、左右スペース比で舵角を制御する
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
進行方向の判断結果に、速度調整、ハンドル角調整を行った値で車両を制御します。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
            ########################################
            # ロボットカーを 前進、左右、停止 する
            ########################################
            if ai_value == STOP:
                car.stop()
                car.set_angle(HANDLE_NEUTRAL)
            elif ai_value == LEFT:
                car.set_angle(HANDLE_NEUTRAL - (HANDLE_ANGLE * ratio))
                car.forward(speed)
            elif ai_value == FORWARD:
                car.forward(speed)
                car.set_angle(HANDLE_NEUTRAL)
            elif ai_value == RIGHT:
                car.set_angle(HANDLE_NEUTRAL + (HANDLE_ANGLE * ratio))
                car.forward(speed)
```
<hr>

#### バック機能を追加する
カーブを曲がりきれなかったり、行き止まりになった時に、バックするようにします。<br>
このロボットカーは後ろにセンサーが付いていないため、バックはあまりうまくは出来ません。<br>
今回はとりあえず真っ直ぐバックして、その後ハンドルを切るようにします。<br>
それでも曲がれるスペースが見つからない時は、スペースが見つかるまで適当にバックするようにします。<br>

車両自走コード：[./run_car_if.py](./run_car_if.py)<br>
```python
            ########################################
            # もし停止なら、ロボットカーを後進する
            ########################################
            '''
            バック時、直前のハンドルログからN件分を真っ直ぐバックし、M件分を逆ハンドルでバックする
            その後、狭い方にハンドルを切ってバックする
            '''
            if ai_value == STOP:
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
                log_queue.put(ai_value)
```
<hr>

#### 終了ボタンを追加する
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
from lib import SPI
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
ロボットカー起動時にこのプログラムを自動実行するように設定すれば、ロボットカーだけで動作するようになるため、デモ等でネットワークやパソコンが不要になります。

> `python start_button.py`<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='6'>

## ディレクトリとファイルについて
* ディレクトリについて
  * document/ ドキュメント関連
  * fabolib/ Fabo製基板関連
  * generator/ 学習データのラベル生成関連
  * lib/ SPIライブラリ
  * test/ Fabo基板動作確認関連
* ファイルについて
  * README.md このファイル
  * run_ai_if.py 自動走行コード
  * start_button.py 開始ボタンコード

[<ページTOP>](#top)　[<目次>](#0)
<hr>


