<a name='top'>

# レベル2：OpenCVでラインを検出する
<hr>

## 目標
#### 映像から、ラインを検出する

## 画像
![](./document/result_frame_1.jpg)<br>

## 動画
入力動画：[./demo_lane/input4.mp4](./demo_lane/input4.mp4)<br>
出力動画：[![出力動画](https://img.youtube.com/vi/KUhikZq7zXc/3.jpg)](https://www.youtube.com/watch?v=KUhikZq7zXc)<br>

## 参考
Programmatic lane finding: [https://github.com/BillZito/lane-detection](https://github.com/BillZito/lane-detection)<br>
level4:OpenCVでレーン検出する: [11.level4_lane_detection](../11.level4_lane_detection/)<br>

## 実行環境
* Fabo TYPE1 ロボットカー<br>
    * USB Webcam<br>
    * Raspberry Pi3<br>
        * Jessie Lite<br>
        * docker<br>
            * Ubuntu<br>
            * Python 2.7<br>
            * OpenCV 2.4<br>
* Jetson TX2<br>
    * USB Webcam<br>
    * JetPack 3.1<br>
        * Ubuntu<br>
        * Python 3.6<br>
        * OpenCV 3.3<br>

<hr>

<a name='0'>

## 実行
* [インストール方法](#a)<br>
* [コースの準備](#course)<br>
* [Raspberry Pi3での実行方法](#b)<br>
* [Jetson TX2での実行方法](#c)<br>

## 目次
* [座標とカラーフィルタの確認](#l1)<br>
* [処理について](#l2)<br>
* [ディレクトリとファイルについて](#l3)<br>

<a name='a'>

## インストール方法
インストール済みのロボットカー/Jetson TX2を用意しているので省略します。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='course'>

## コースの準備
走行中のカメラ動画をdemo_lane/capture.mp4に用意してあるのでコースの準備は不要です。<br>
自分でコースを用意する場合は、白色抽出しやすいようにはっきりとした白色でコースを作ってください。<br>
急なカーブはカメラに映らなくなってしまうので、できるだけ緩やかなカーブでコースを作ってください。<br>

![](./document/course.jpg)<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='b'>

## Raspberry Pi3での実行方法
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
> `cd /notebooks/github/RobotCarAI/level2_lane_detection/`<br>
> `ls`<br>
>> total 68<br>
>> 160846  4 ./         160940  4 demo_lane/  125612 24 opencv_lane_detection.py  142544  4 to_inverse_perspective_mapping.py<br>
>> 123628  4 ../        160941  4 document/   160851  4 output/                   142545  4 to_region_of_interest.py<br>
>> 142509  4 README.md  160849  4 lib/        160942  4 test_images/              142546  4 to_white.py<br>

#### 5. ライン検出コードを実行します
demo_lane/capture.mp4を入力として読み込み、1フレームずつ検出してoutput/result_capture.aviに保存します。<br>
> `python opencv_lane_detection.py`<br>
>> FPS:6.43823125369 <br>
>> frame 229 Done!<br>

途中、ライン検出に失敗したフレームでエラーを吐きながら進みますが実行には問題ありません。<br>
>Traceback (most recent call last):<br>
>  File "opencv_lane_detection.py", line 211, in main<br>
>    line_polyfit_const, pts_line = calc_line_curve(line_x,line_y,plot_y)<br>
>  File "/notebooks/github/RobotCarAI/level2_lane_detection/lib/functions.py", line 799, in calc_line_curve<br>
>    line_polyfit_const = polynormal_fit(line_y,line_x)<br>
>  File "/notebooks/github/RobotCarAI/level2_lane_detection/lib/functions.py", line 777, in polynormal_fit<br>
>    polyfit_const = np.polyfit(pts_y, pts_x, 2)<br>
>  File "/usr/local/lib/python2.7/dist-packages/numpy/lib/polynomial.py", line 555, in polyfit<br>
>    raise TypeError("expected non-empty vector for x")<br>
>TypeError: expected non-empty vector for x<br>

#### 6. 確認します
ブラウザでRaspberry Pi3のjupyterにアクセスします<br>
> http://192.168.xxx.xxx:8888/tree/github/RobotCarAI/level2_lane_detection/<br>

jupyterのpasswordは別途説明があるかと思います。<br>

実行によってできたデータは、<br>
http://192.168.xxx.xxx:8888/tree/github/RobotCarAI/level2_lane_detection/output/result_capture.avi<br>
になります。<br>

この実行で使った入力用データは、<br>
http://192.168.xxx.xxx:8888/tree/github/RobotCarAI/level2_lane_detection/demo_lane/capture.mp4<br>
になります。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='c'>

## Jetson TX2での実行方法
#### 1. Jetson TX2にログインします
USER:ubuntu<br>
PASSWORD:ubuntu<br>
> `ssh ubuntu@192.168.xxx.xxx`<br>

用意してあるJetson TX2はDockerを使っていないので、Raspberry Pi3の時のようなdockerコンテナへのログインはありません。<br>

#### 2. ロボットカーのディレクトリに移動します
> `cd ~/notebooks/github/RobotCarAI/level2_lane_detection/`<br>
> `ls`<br>
>> total 68<br>
>> 160846  4 ./         160940  4 demo_lane/  125612 24 opencv_lane_detection.py  142544  4 to_inverse_perspective_mapping.py<br>
>> 123628  4 ../        160941  4 document/   160851  4 output/                   142545  4 to_region_of_interest.py<br>
>> 142509  4 README.md  160849  4 lib/        160942  4 test_images/              142546  4 to_white.py<br>

#### 3. ライン検出コードを実行します
demo_lane/capture.mp4を入力として読み込み、1フレームずつ検出してoutput/result_capture.aviに保存します。<br>
> `python opencv_lane_detection.py`<br>
>> FPS:34.37121576286537 <br>
>> frame 229 Done!<br>

途中、ライン検出に失敗したフレームでエラーを吐きながら進みますが実行には問題ありません。<br>
>Traceback (most recent call last):<br>
>  File "opencv_lane_detection.py", line 211, in main<br>
>    line_polyfit_const, pts_line = calc_line_curve(line_x,line_y,plot_y)<br>
>  File "/home/ubuntu/notebooks/github/RobotCarAI/level2_lane_detection/lib/functions.py", line 799, in calc_line_curve<br>
>    line_polyfit_const = polynormal_fit(line_y,line_x)<br>
>  File "/home/ubuntu/notebooks/github/RobotCarAI/level2_lane_detection/lib/functions.py", line 777, in polynormal_fit<br>
>    polyfit_const = np.polyfit(pts_y, pts_x, 2)<br>
>  File "/usr/local/lib/python3.6/dist-packages/numpy/lib/polynomial.py", line 555, in polyfit<br>
>    raise TypeError("expected non-empty vector for x")<br>
>TypeError: expected non-empty vector for x<br>

#### 6. 確認します
ブラウザでJetson TX2のjupyterにアクセスします<br>
> http://192.168.xxx.xxx:8888/tree/github/RobotCarAI/level2_lane_detection/<br>

jupyterのpasswordは別途説明があるかと思います。<br>

実行によってできたデータは、<br>
http://192.168.xxx.xxx:8888/tree/github/RobotCarAI/level2_lane_detection/output/result_capture.avi<br>
になります。<br>

この実行で使った入力用データは、<br>
http://192.168.xxx.xxx:8888/tree/github/RobotCarAI/level2_lane_detection/demo_lane/capture.mp4<br>
になります。<br>


#### これ以降について
ライン検出は、level4(仮)の2本線から走行レーンを検出するコードを1本線に簡素化したものになります。<br>
処理内容についてはlevel4(仮)を参考にしてください。level4(仮)が分かれば、要らないものを削っていくだけのコード修正でできる内容になります。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l1'>

## 座標とカラーフィルタの確認

自分のライン動画で検出する場合、視点変更、ラインの色抽出を調整する必要があります。<br>
関心領域の確認<br>
> `python to_region_of_interest.py`<br>

視点の確認<br>
> `python to_inverse_perspective_mapping.py`<br>

白色抽出の確認<br>
> `python to_white.py`<br>

<hr>

<a name='l2'>

## 処理について
処理方法はlevel4:OpenCVでレーン検出する: [11.level4_lane_detection](../11.level4_lane_detection/)と同じ流れになります。<br>
level4を1本線の処理に修正したものになるため、処理についてはlevel4を参考にしてください。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='l3'>
## [ディレクトリとファイルについて]
* ディレクトリについて<br>
    * documment/ ドキュメント関連<br>
    * demo_lane/ デモ用ディレクトリ<br>
    * lib/ 関数ライブラリ<br>
    * test_images/ ROI,IPM,白色フィルタの確認用ディレクトリ<br>
    * output/ 出力用ディレクトリ(実行時に作成)<br>
* ファイルについて<br>
    * README.md このファイル<br>
    * opencv_lane_detection.py ライン検出コード<br>
    * to_region_of_interest.py ROI座標確認コード<br>
    * to_inverse_perspective_mapping.py IPM座標確認コード<br>
    * to_white.py 白色フィルタ確認コード<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>
