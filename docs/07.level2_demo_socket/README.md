<a name='top'>

# レベル2：ロボットカー走行デモ TCP通信版
<hr>

## 目標
#### カメラ映像をTCP通信でサーバに送り、サーバからの走行指示でロボットカーを自走させる

## 画像
![](./document/robotcar1.jpg)<br>
![](./document/robotcar2.jpg)<br>
![](./document/robotcar3.jpg)<br>

## 実行環境
* Fabo TYPE1 ロボットカー<br>
    * USB Webcam<br>
    * Fabo #605 Motor Shield Raspberry Pi Rev 1.0.1<br>
    * Fabo Robot Car #1202 Rev. 1.0.1<br>
    * Tower Pro SG90<br>
    * Raspberry Pi3<br>
        * Jessie Lite<br>
        * docker<br>
            * Ubuntu<br>
            * Python 2.7<br>
            * OpenCV 2.4<br>
            * FaBoPWM-PCA9685-Python<br>
            * FaBoGPIO-PCAL6408-Python<br>
* Jetson TX2<br>
    * JetPack 3.1<br>
        * Ubuntu<br>
        * Python 3.6<br>
        * OpenCV 3.3<br>

<a name='0'>

## 実行
* [インストール方法](#a)<br>
* [コースの準備](#course)<br>
* [Jetson TX2/PC] [サーバ起動](#b)<br>
* [Raspberry Pi3] [ロボットカー起動](#c)<br>

## 目次
* [トラブルシューティング](#l2)<br>
    * Webcamが起動しない<br>
    * 走行中にハンドルが固まった<br>
    * Raspberry Pi3が起動しない<br>
    * サーバが起動しない<br>
* [ディレクトリとファイルについて](#l3)<br>

<hr>

<a name='a'>

## インストール方法
インストール済みのロボットカー/Jetson TX2を用意しているので省略します。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='course'>

## コースの準備
コースは白線で作り、カーブは緩やかに作ってください。<br>
カーブが急だとカメラに映らなくなります。<br>

![](./document/course.jpg)<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='b'>

## [Jetson TX2/PC] サーバ起動
#### 1. Jetson TX2にログインします
USER:ubuntu<br>
PASSWORD:ubuntu<br>
> `ssh ubuntu@192.168.xxx.xxx`<br>

用意してあるJetson TX2はDockerを使っていないので、Raspberry Pi3の時のようなdockerコンテナへのログインはありません。<br>

#### 2. ロボットカーのディレクトリに移動します
> `cd ~/notebooks/github/RobotCarAI/level2_demo_socket/pc_server`<br>
> `ls`<br>
>> total 24<br>
>> 160938  4 ./  160847  4 ../  160939  4 lib/  142530 12 server.py<br>

#### 3. ソースコードのIPアドレスをサーバのIPアドレスに修正します
サーバ側が監視する自分のIPアドレスとTCPポート番号をサーバに合わせて修正してください。<br>
> `vi server.py`<br>
>>`    HOST = '192.168.0.77' # Server IP Address`<br>
>>`    PORT = 6666 # Server Port`<br>

#### 4. ライン検出コードを実行します
> `python server.py`<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='c'>

## [Raspberry Pi3] ロボットカー起動
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
> `cd /notebooks/github/RobotCarAI/level2_demo_socket/car_client/`<br>
> `ls`<br>
>> total 28<br>
>> 160848 4 ./  160847 4 ../  160850 4 fabolib/  160937 4 lib/  142528 8 run_car_client.py  142529 4 start_button.py<br>

#### 5. ソースコードのIPアドレスをサーバのIPアドレスに修正します
クライアント側も通信先のサーバのIPアドレスとTCPポート番号をサーバに合わせて修正してください。<br>
> `vi run_car_client.py`<br>
>>`    HOST = '192.168.0.77' # Server IP Address`<br>
>>`    PORT = 6666 # Server Port`<br>

#### 5. ロボットカーを起動します
> `python start_button.py`<br>

#### 6. 走行開始するには、ロボットカーの青いボタンを押します
![](./document/img2.jpg)

#### 7. 走行停止するには、ロボットカーの赤いボタンを押します
![](./document/img3.jpg)<br>
Ctrl + c でstart_button.pyを終了します

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l2'>

## トラブルシューティング
#### Webcamが起動しない
>`IOError: Couldn't open video file or webcam. If you're trying to open a webcam, make sure you video_path is an integer!`

OpenCVの映像取得に失敗した場合にこのエラーが発生します。<br>
他にカメラを使っているプロセスがなければ、数秒おいて再実行で解決することが多いです。<br>
それでも解決しない場合は、カメラのUSBケーブルを抜き差ししてください。<br>
これは再実行時によく発生します。<br>
<hr>

#### 走行中にハンドルが固まった
>`VIDIOC_DQBUF: No such device`

ロボットカーの赤いボタンを押して車両を停止してください。<br>
カメラのUSBケーブルを抜き差ししてください。<br>
走行中に突然一方方向に進み続けてしまう場合は、Raspberry Pi3からの電力供給が遮断されてカメラが認識不能になったために発生します。<br>
Faboシールドの電源をRaspberry Pi3から取得している時に、サーボの消費電力量が増えた瞬間に発生します。電力供給はすぐに復旧するので走行は続くのですが、カメラが認識不能になるため、制御不能に陥ります。<br>
<hr>

#### Raspberry Pi3が起動しない
バッテリーの出力不足が原因として上げられます。<br>
2A以上のモバイルバッテリーを使ってください。<br>
<hr>

#### サーバが起動しない
server.pyのHOST,PORTを確認してください。<br>
Dockerを使っている場合は、HOSTはDockerコンテナIDになります。<br>
ファイアーウォールは通常、内部IPに対して設定していないので通信可能ですが、設定している場合はサーバ側でTCPポート番号の通信を許可してください。<br>
<hr>

#### 走行開始ボタンを押してもすぐ終了する
run_car.pyのHOST,PORTを確認してください。(サーバのIPアドレス、ポート番号を設定します)<br>
サーバが起動していることを確認してください。<br>

カメラエラーかもしれないので、USBカメラを抜き差ししてください。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l3'>

## ディレクトリとファイルについて
* ディレクトリについて<br>
    * car_client/ ロボットカー制御関連<br>
    * car_client/fabolib/ Fabo製基板関連<br>
    * car_client/lib/ SPI,カメラライブラリ<br>
    * pc_server/ サーバ解析関連<br>
    * pc_server/lib/ ライン検出関連<br>
* ファイルについて<br>
    * README.md このファイル<br>
    * car_client/run_car_client.py 自動走行コード<br>
    * car_client/start_button.py 開始ボタンコード<br>
    * pc_server/server.py サーバ起動コード<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>
