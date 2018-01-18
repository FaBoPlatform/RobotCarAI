<a name='top'>

【タイトル】
# ニューラルネットワークで道路標識を検出する
<hr>

【目標】
#### カメラ映像を取得し、道路標識を検出する

【画像】<br>
![](./document/jetson_tx2-stop.png)<br>
![](./document/course.jpg)<br>

【動画】<br>
止まれを検出する動画：[./document/stop.mp4](./document/stop.mp4)<br>
走行しながら道路標識を検出する動画：[./document/course160x120.mp4](./document/course160x120.mp4)<br>

<hr>

<a name='0'>

【目次】
* [物体検出の紹介](#1)
  * [OpenCV] [テンプレートマッチング]
  * [Python] [Selective Search]
  * [Neural Networks] [SSD: Single Shot MultiBox Detection]
  * [Python/TensorFlow] [TensorFlow Object Detection API]
* [Python/OpenCV/TensorFlow] [Balancap SSD-Tensorflowを使う](#2)
  * インストール
  * demo実行
  * 扱える学習データフォーマット
  * 学習データを作成する
  * 学習コードの作成と学習実行
  * 検出実行
  * カメラ映像の読み込み
  * ストリーミング配信
  * ストリーミング解析実行
  * 動画に保存
* [ディレクトリとファイルについて](#3)
* [開発/学習/実行環境について](#4)
<hr>

<a name='1'>

## 物体検出の紹介
物体検出はこれまでに色々な方法が試みられてきました。
#### [OpenCV] テンプレートマッチング
昔からある方法としては、黒枠などのテンプレート画像を検索する方法があり、OpenCVで使う事が出来ます。<br>
検出には入力画像内にあるテンプレート同様の画像サイズが、用意したテンプレート画像サイズとほぼ一致している必要があるため、複数のサイズでテンプレートを用意します。<br>
黒枠を検出したら、その内部をCNNで画像識別して結果を得ます。
<hr>

#### [Python] Selective Search
候補領域を選出し、その内部をCNNで画像識別して結果を得ます。<br>
テンプレートの用意は不要ですが、候補領域はアルゴリズムで算出されるため、領域が出なければ識別にかけることは出来ません。<br>
1つの画像に候補領域が大量に出てくると識別回数が増えて遅くなります。<br>
<hr>

#### [Neural Networks] SSD: Single Shot MultiBox Detection
VGG16を内部に持ち、DeepLearningによる物体検出と識別を行います。<br>
TensorFlowでのコードが公開されていますので、今回はこれを使うことにします。
<hr>

#### [Python/TensorFlow] TensorFlow Object Detection API
TensorFlow公式で用意されている物体検出APIです。<br>
様々なモデルを使うことが出来ますが、バージョンアップに伴うトラブルもあるため、今後に期待します。

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='2'>

## [Python/OpenCV/TensorFlow] Balancap SSD-Tensorflowを使う
TensorFlowを使った物体検出として、Balancap SSD-Tensorflowを使って道路標識を学習し、Jetson TX2で実行してみます。
Balancap SSD-Tensorflow：[https://github.com/balancap/SSD-Tensorflow](https://github.com/balancap/SSD-Tensorflow)

#### インストール
インストール先や学習コード生成に必要な情報はスクリプト設定ファイルで用意しました。環境に合わせて修正してください。<br>
特に、Jetson TX2では/home/ubuntu/notebooks/github/...と直します。<br>

スクリプト設定ファイル：[./script_define.conf](./script_define.conf)<br>
```bash
# Balancap SSD-Tensorflowのディレクトリ
GIT_DIR=/home/ubuntu/notebooks/github
SSD_TENSORFLOW_DIR=$GIT_DIR/SSD-Tensorflow

# データ名
MY_TRAIN=roadsign
# 学習データディレクトリ
VOC_DATASET_DIR=/home/ubuntu/notebooks/github/RobotCarAI/level3_object_detection/roadsign_data/PascalVOC
TF_DATASET_DIR=/home/ubuntu/notebooks/github/RobotCarAI/level3_object_detection/roadsign_data/tfrecords

# 道路標識の学習データで使うラベル
# LABELS[0]はbackground(その他)用に空けておく
# 学習データのラベルを増やす時はここにも追加する
LABELS[1]=stop
LABELS[2]=speed_10
LABELS[3]=speed_20
LABELS[4]=speed_30

# 新規VGG16 checkpoint
CHECKPOINT_PATH=$SSD_TENSORFLOW_DIR/checkpoints/vgg_16.ckpt
# 学習を再開するcheckpoint
LEARNED_CHECKPOINT_PATH=$SSD_TENSORFLOW_DIR/output/model.ckpt-7352
```
<hr>

Balancap SSD-Tensorflow インストールスクリプト：[./install_scripts/install.sh](./install_scripts/install.sh)<br>
> `chmod 755 ./install_scripts/*.sh`<br>
> `./install_scripts/install.sh`<br>

<hr>

#### demo実行
jupyterでSSD-Tensorflow/notebooks/ssd_notebook.ipynb を開いて実行します。
<hr>

#### 扱える学習データフォーマット
SSD-Tensorflowで扱うことの出来るデータフォーマットはPascalVOC形式になります。<br>
自前の学習データを用意する際は、PascalVOC形式で作成する必要があります。
<hr>

#### 学習データを作成する
学習データはGUIツールのLabelImgを使って作成します。<br>
LabelImg：[https://github.com/tzutalin/labelImg](https://github.com/tzutalin/labelImg)<br>
LabelImg インストールスクリプト：[./install_scripts/install_labelimg.sh](./install_scripts/install_labelimg.sh)<br>
> `./install_scripts/install_labelimg.sh`<br>

![labelImg.png](./document/labelImg.png)

GUIツールなので画面のある開発環境で学習データを作成してください。<br>
labelImgで作成したラベルは画像ファイルと同じディレクトリに作成されます。<br>
Balancap SSD-Tensorflowでは、TF-Recordへのコンバート時は画像ファイルをJPEGImagesに、ラベルファイルをAnnotationsに分けておく必要があります。<br>

画像データ:[./roadsign_data/PascalVOC/JPEGImages/](./roadsign_data/PascalVOC/JPEGImages)<br>
ラベルデータ:[./roadsign_data/PascalVOC/Annotations/](./roadsign_data/PascalVOC/Annotations/)<br>

学習データを作ったら、学習用コードの作成、データの変換、学習、となります。<br>
<hr>

#### 学習コードの作成と実行
Balancap SSD-Tensorflowの学習コードは、元の学習コードをコピーしてスクリプトで修正して作成します。<br>
<hr>

スクリプト設定ファイルで以下を設定します。
* 学習データディレクトリ
* ラベル

スクリプト設定ファイル：[./script_define.conf](./script_define.conf)<br>
```bash
# 学習データディレクトリ
VOC_DATASET_DIR=/notebooks/github/RobotCarAI/level3_object_detection/roadsign_data/PascalVOC
TF_DATASET_DIR=/notebooks/github/RobotCarAI/level3_object_detection/roadsign_data/tfrecords

# 道路標識の学習データで使うラベル
# LABELS[0]はbackground(その他)用に空けておく
# 学習データのラベルを増やす時はここにも追加する
LABELS[1]=stop
LABELS[2]=speed_10
LABELS[3]=speed_20
LABELS[4]=speed_30
```
<hr>

スクリプトコードを作成し、PascalVOCデータをTF-Recordsに変換して学習を実行します。<br>
スクリプト作成コード：[./train_scripts/setup_mytrain.sh](./train_scripts/setup_mytrain.sh)<br>
データ変換コード：[./train_scripts/convert_PascalVOC_to_TF-Records.sh](./train_scripts/convert_PascalVOC_to_TF-Records.sh)<br>
学習実行コード：[./train_scripts/train_ssd.sh](./train_scripts/train_ssd.sh)<br>
> `chmod 755 ./train_scripts/*`<br>
> `./train_scripts/setup_mytrain.sh`<br>
> `./train_scripts/convert_PascalVOC_to_TF-Records.sh`<br>
> `./train_scripts/train_ssd.sh`<br>
> `./train_scripts/freeze_graph.sh`<br>

学習はGPUを搭載した学習環境でおこないます。<br>
一定時間毎にcheckpointが保存されるので、適当なところでCtrl_cで学習を停止してください。<br>

途中のチェックポイントから学習を再開する際は、スクリプト設定ファイルのLEARNED_CHECKPOINT_PATHに再開するチェックポイントを指定して学習を再開します。<br>
スクリプト設定ファイル：[./script_define.conf](./script_define.conf)<br>
```bash
# 学習済みcheckpoint
LEARNED_CHECKPOINT_PATH=$SSD_TENSORFLOW_DIR/output/model.ckpt-4870
```
学習再開クリプト：[./train_scripts/train_ssd_continue.sh](./train_scripts/train_ssd_continue.sh)<br>
> `./train_scripts/train_ssd_continue.sh`<br>

<hr>

Balancap SSD-Tensorflowではjpegしか扱えないため、pngで画像を用意した場合は変換が必要になります。  

> `apt-get install imagemagick`<br>
> `# png to jpg`<br>
> `for i in *.png ; do convert "$i" "${i%.*}.jpg" ; done`<br>
> `# replace xml`<br>
> `find ./ -name "*.xml" | xargs sed -i 's/\.png/.jpg/g'`<br>

<hr>

#### 検出実行
pbファイルを読み込んで実行します。<br>

検出実行コード：[./copy_to_SSD-Tensorflow/run_ssd.py](./copy_to_SSD-Tensorflow/run_ssd.py)
> `cd /notebooks/github/SSD-Tensorflow/`<br>
> `python run_ssd.py`<br>

検出結果は層毎に出てくるため、SSDNetクラスを使って集計を行います。<br>
検出実行コード：[./copy_to_SSD-Tensorflow/run_ssd.py](./copy_to_SSD-Tensorflow/run_ssd.py)<br>
```python
        # 予測実行
        rclasses, rscores, rbboxes =  process_image(sess,cv_bgr)
```python

/notebooks/github/SSD-Tensorflow/demo_images/以下に検出元画像と検出結果画像があります。

<hr>

#### カメラ映像の読み込み
画像の時と同じで、カメラ映像の時も1フレームを1画像として読み込みます。<br>

画像の読み込み<br>
検出実行コード：[./copy_to_SSD-Tensorflow/run_ssd.py](./copy_to_SSD-Tensorflow/run_ssd.py)<br>
```python
        cv_bgr = cv2.imread(DEMO_DIR+"/" + file_name)
```

カメラ映像の読み込み<br>
WebCamストリーミング解析コード：[./copy_to_SSD-Tensorflow/run_streaming.py](./copy_to_SSD-Tensorflow/run_streaming.py)
```python
    vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
...
            retval, cv_bgr = vid.read()
```
Jetson TX2の場合は/dev/video1がUSBカメラデバイスなので、cv2.VideoCapture(1)となります。<br>
Raspberry Pi3やPCでは/dev/video0がUSBカメラデバイスなので、cv2.VideoCapture(0)となります。<br>

UDPストリーミングで動画が送られている場合は、vid = cv2.VideoCapture('udp://localhost:8090')のようにUDPポートを指定して受信します。<br>
USBカメラが未接続だったり、ストリーミングが開始されていない時は映像取得に失敗します。
<hr>

#### ストリーミング配信
##### FFMPEG UDP Streamingを使う場合
送信側コマンド(192.168.0.77は受信側アドレス)<br>
> `ffmpeg -thread_queue_size 1024 -r 30 -video_size 160x120 -input_format yuyv422 -i /dev/video0 -pix_fmt yuv422p -threads 4 -f mpegts udp://192.168.0.77:8090`<br>

受信側確認コマンド(動画プレイヤーが立ち上がるので、画面のあるPCで確認する場合になります)
> `ffplay udp://localhost:8090`<br>

AWSで受信する場合は、UDPポートで受信出来るようにするために、外部IPアドレスを持ち、セキュリティグループにUDPポート番号を設定必要があります。<br>
Jetson TX2で受信する場合は、内部IPアドレスとポート番号だけで受信出来ます。

<hr>

#### ストリーミング解析実行
ストリーミング時はUDPポートを読み込みに指定します。
WebCamストリーミング解析コード：[./copy_to_SSD-Tensorflow/run_streaming.py](./copy_to_SSD-Tensorflow/run_streaming.py)
```python
    vid = cv2.VideoCapture('udp://localhost:8090') # UDP Streaming
```
分類結果、スコア、物体の領域が得られるので、例えばそれを画像に描画して動画に保存することが出来ます。<br>
ロボットカーの場合は描画や動画への保存は不要ですが、停止を検出したら数秒止まる、速度を検出したら速度を変更する、等の処理を行うことになります。
<hr>

#### 動画に保存
予測結果を画像に描画して動画で保存します。ここでは結果を見たいだけなので、保存する動画のFPSは適当に処理性能くらいにしておきます。<br>
Jetson TX2はメモリが不足になりやすいため、OOM(Out Of Memory)等で落ちやすいです。<br>

Jetson TX2では、pbファイル化して検出に不要なオペレーションをそぎ落としてメモリ消費量を抑えることで、SSDの結果を動画に保存することが出来ます。<br>

WebCamストリーミング解析コード：[./copy_to_SSD-Tensorflow/run_streaming.py](./copy_to_SSD-Tensorflow/run_streaming.py)
```python
# FPSは処理速度を実際の見てから考慮する
#out = cv2.VideoWriter(DEMO_DIR+'/output.avi', int(fourcc), fps, (int(vidw), int(vidh)))
out = cv2.VideoWriter(DEMO_DIR+'/output.avi', int(fourcc), 2.1, (int(vidw), int(vidh)))
    ...
            # 予測実行
            rclasses, rscores, rbboxes = process_image(sess,cv_bgr)
            # 枠を描く
            write_bboxes(cv_bgr, rclasses, rscores, rbboxes)
            # avi動画に保存する
            out.write(cv_bgr)
```
動画はavi形式で/notebooks/github/SSD-Tensorflow/demo_images/output.aviに保存されます。

[<ページTOP>](#top)　[<目次>](#0)

<hr>

<a name='3'>

## [ディレクトリとファイルについて]
* ディレクトリについて
  * documment/ ドキュメント関連
  * install_scripts/ インストールスクリプト
  * copy_to_SSD-Tensorflow/ Balancap SSD-Tensorflowにコピーするファイル
  * roadsign_data/ 道路標識データ
  * train_scripts/ 学習関連スクリプト
* ファイルについて
  * README.md このファイル
  * scritp_define.conf ディレクトリパス等設定ファイル
  * install_scripts/install.sh インストールスクリプト
    * install_scripts/install_balancap_ssd-tensorflow.sh Balancap SSD-Tensorflow ダウンロードスクリプト
    * install_scripts/setup_bugfix.sh Balancap SSD-Tensorflow バグ修正スクリプト
    * install_scripts/copy_to.sh ファイルコピースクリプト
    * install_scripts/patch_to.sh ファイル修正スクリプト
  * install_scripts/install_labelimg.sh LabelImg インストールスクリプト
  * copy_to_SSD-Tensorflow/add_input_x.py 学習済みcheckpointに入力名を追加するコード
  * copy_to_SSD-Tensorflow/freeze_graph.py モデル凍結コード
  * copy_to_SSD-Tensorflow/run_ssd.py 検出実行コード
  * copy_to_SSD-Tensorflow/model/ssd_roadsign.pb 学習済みモデル
  * copy_to_SSD-Tensorflow/run_streaming.py Webcamストリーミング動画解析コード
  * train_scripts/setup_mytrain.sh 学習コード生成スクリプト
  * train_scripts/convert_PascalVOC_to_TF-Records.sh 学習データ変換スクリプト
  * train_scripts/train_ssd.sh 学習実行スクリプト
  * train_scripts/train_ssd_continue.sh 学習再開スクリプト
  * train_scripts/freeze_graph.sh モデル凍結スクリプト

[<ページTOP>](#top)　[<目次>](#0)

<hr>

<a name='4'>

## [開発/学習/実行環境について]
* 開発環境
  * ラベル作成はGUIツールを使うため、画面のある環境が必要です。
* 学習環境
  * 学習環境はGPUが使える環境が必要です。
* 実行環境
  * 実行環境はUSBカメラが使える環境が必要です。
  * クラウドで実行する場合は、PCかRaspberryPi3等にUSBカメラを付けてFFMPEGを使ってカメラ映像をクラウド実行環境にUDP Streaming配信する必要があります。
  * USBカメラの代わりに画像ファイル、動画ファイルの読み込みも可能です。その場合はOpenCVの公式ドキュメントを参考にしてください。

[<ページTOP>](#top)　[<目次>](#0)
