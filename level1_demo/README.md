<a name='top'>

【タイトル】
# レベル1：ロボットカー走行デモ
<hr>

【目標】
#### 3つの距離センサーから値を取得し、Neaural Networksで進行方向を判断してロボットカーを自走させる

【画像】<br>
![](./document/img1.jpg)
![](./document/robotcar.jpg)<br>

【実行環境】
* Fabo TYPE1 ロボットカー
  * Fabo #605 Motor Shield Raspberry Pi Rev 1.0.1
  * Fabo #902 Kerberos ver 1.0.0
  * Fabo #1202 Robot Car Rev. 1.0.1
  * Fabo #103 Button
  * Lidar Lite v3
  * Tower Pro SG90
  * Raspberry Pi3
    * Jessie Lite
    * docker
      * Ubuntu
      * Python 2.7
      * FaBoPWM-PCA9685-Python
      * FaBoGPIO-PCAL6408-Python
      * Tensorflow r1.1.0

【動画】<br>
走行デモ動画：[![走行デモ動画](https://img.youtube.com/vi/0IXHXuacMEI/3.jpg)](https://www.youtube.com/watch?v=0IXHXuacMEI)<br>

<hr>

<a name='0'>

【実行】
* [インストール方法](#a)
* [コースの準備](#course)
* [実行方法](#b)

【目次】
* [必要なコードとファイル](#1)
* [Python] [level1_carの自走コードを元に修正する](#2)
  * Neural Networksの判断処理を追加する
  * 開始ボタン
* [ディレクトリとファイルについて](#3)
<hr>

<a name='a'>

## インストール方法
インストール済みのロボットカーを用意しているので省略します。
<hr>

<a name='course'>

## コースの準備
コースとなる壁は、距離センサーが発するレーザーが反射できるような素材で作ります。<br>
足元での突起物となるので、人がぶつかった時の安全性や価格、レイアウト変更のしやすさ、修復しやすさを考えて画用紙とクリップで作ってあります。<br>
ジグザグに織ることで、収納しやすさ、立たせやすさ、レイアウト変更のしやすさ、レーザー反射しやすさも獲得しています。<br>
道幅は直線なら狭くても大丈夫ですが、カーブでは側面にセンサーが付いていないため、内側を巻き込みやすくなっています。<br>
そのため、カーブは広めに作り、狭い道への入り口も誘導しやすいように広めに作っておきます。<br>

![](./document/course.jpg)<br>

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

> `cd /notebooks/github/RobotCarAI/level1_demo/`<br>
> `ls`<br>
>> total 48<br>
>> 160769  4 ./   127297  4 README.md  160770  4 fabolib/  160772  4 model/         141770  4 start_button.py<br>
>> 123628  4 ../  160804  4 document/  160771  4 lib/      141769 16 run_car_ai.py<br>

#### 5. ロボットカーを起動します
> `python start_button.py`<br>

#### 6. 走行開始するには、ロボットカーの青いボタンを押します
![](./document/img2.jpg)

#### 7. 走行停止するには、ロボットカーの赤いボタンを押します
![](./document/img3.jpg)<br>
Ctrl + c でstart_button.pyを終了します

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='1'>

## 必要なコードとファイル
走行に必要なコードは以下になります。<br>
* ライブラリ
  * ./fabolib/以下
  * ./lib/以下
* 学習済みモデル
  * ./model/以下
* 実行コード
  * start_button.py 開始ボタンコード
  * run_car_ai.py level0のrun_car_if.pyを元に修正

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='2'>

## [Python] level1_carの自走コードを元に修正する
#### Neural Networksの判断処理を追加する
AI判断を追加し、ジェネレータの判断は不要なのでコメントアウトしておきます。<br>

車両自走コード：[./run_car_ai.py](./run_car_ai.py)<br>
```python
from lib import AI
#from generator import LabelGenerator
...
    # AI準備
    ai = AI("car_model_100M.pb")
    SCORE = 0.6 # スコア閾値
    # IF準備 (学習ラベル ジェネレータ)
    #generator = LabelGenerator()
...
            ########################################
            # AI予測結果を取得する
            ########################################
            # 今回の予測結果を取得する
            ai_value = ai.get_prediction(sensors,SCORE)

            print("ai_value:{} {}".format(ai_value,sensors))
            # 予測結果のスコアが低い時は何もしない
            if ai_value == ai.get_other_label():
                time.sleep(LIDAR_INTERVAL)
                continue

            ########################################
            # IF結果を取得する
            ########################################
            # 今回の結果を取得する
            #generator_result = generator.get_label(sensors)
            #ai_value = np.argmax(generator_result)
```

開始ボタンコードも修正します。<br>
開始ボタンコード：[./start_button.py](./start_button.py)
```python
    cmd = "python "+os.path.abspath(os.path.dirname(__file__))+"/run_car_ai.py"
```

あとはlevel1_car同様に開始ボタンコードを実行します。<br>
> `python start_button.py`<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='3'>

## ディレクトリとファイルについて
* ディレクトリについて
  * document/ ドキュメント関連
  * fabolib/ Fabo製基板関連
  * lib/ SPI,AIライブラリ
* ファイルについて
  * README.md このファイル
  * run_ai_ai.py 自動走行コード
  * start_button.py 開始ボタンコード

[<ページTOP>](#top)　[<目次>](#0)
<hr>


