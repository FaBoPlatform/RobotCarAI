<a name='top'>

【タイトル】
# レベル1：距離センサーの値をニューラルネットワークで使う
<hr>

【目標】
#### 3つの距離センサーから値を取得し、ロボットカーが走行可能な進行方向をニューラルネットワークモデルを用いて予測する

【画像】
![](./document/robotcar.jpg)<br>

【実行環境】
* Fabo TYPE1 ロボットカー
  * Fabo #902 Kerberos ver 1.0.0
  * Lidar Lite v3
  * Raspberry Pi3
    * Jessie Lite
    * docker
      * Ubuntu
      * Python 2.7
      * Tensorflow r1.1.0

<hr>

<a name='0'>

【実行】
* [インストール方法](#a)
* [コースの準備](#course)
* [実行方法](#b)

【目次】
* [Hardware] [距離センサーLidarLite v3について](#1)
  * 取得できる距離、値、誤差、測定周期
* [Neural Networks] [学習データのフォーマットについて](#2)
  * クラス分類
  * one hot value
  * データフォーマット
* [Python] [学習データ ジェネレータを作る](#3)
  * 簡単なIF文での判定
  * 車両旋回性能
  * 曲がる、止まる判定
* [Neural Networks] [学習モデルについて](#4)
  * Multi-Layer Perceptron
* [Python/TensorFlow] [学習用コードのコーディング](#5)
  * 学習コード設計
* [Python/TensorFlow] [学習と保存](#6)
  * 学習実行
  * 保存と読み込み
* [Python/TensorFlow] [予測を実行](#7)
* [Python/TensorFlow] [予測精度を評価](#8)
* [ディレクトリとファイルについて](#9)
<hr>

<a name='a'>

## インストール方法
インストール済みのロボットカーを用意しているので省略します。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='course'>

## コースの準備
ここはニューラルネットワークの学習と実行の項目なので、ロボットカーは走行しないのでコースの準備は不要です。<br>

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
> `cd /notebooks/github/RobotCarAI/level1_sensors/`<br>
> `ls`<br>
>> total 104<br>
>> 160616  4 ./    125780 48 README.md  160618  4 generator/  142810  4 run_ai.py           141770  4 to_one_hot_value.py<br>
>>  123628  4 ../   160709  4 document/  160686  4 lib/        125870  8 run_ai_eval.py<br>
>> 160617  4 MLP/  160710  4 fabolib/   160687  4 model/      125871  8 run_ai_eval_400.py<br>

#### 5. ニューラルネットワークによる進行方向判断処理を実行します
今回は学習済みのモデルを実行します。
> `python run_ai.py`<br>
>> [DEBUG] time:1518164009.79348111 pid:170 pn:MainProcess tid:1811108976 tn:Thread-1   fn:do_stop    enter<br>
>> learned_step:50000000<br>
>> result:FORWARD [218, 511, 112]        <br>
>> main end<br>

#### これ以降について
学習にはメモリやCPU性能のいいマシンを用意する必要があります。<br>
この学習はAWS c5.xlargeインスタンスで一週間程度実行してあります。<br>

[<ページTOP>](#top)　[<目次>](#0)
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

ここはlevel1_carと同じ内容になります。

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='2'>

## [Neural Networks] 学習データのフォーマットについて
#### クラス分類
ロボットカーの進行方向の予測は、STOP,LEFT,FOWARD,RIGHTのどれか一つに属します。これを一般的にクラス分類と呼びます。<br>
画像認識では、用意したクラスのどれにも属さないことを表すためにその他クラスも用意しますが、今回のセンサー値を入力値としたロボットカーの進行方向予測では、その他は存在しないものと考えます。
<hr>

#### one hot value
Neural Networksでは予測結果を確率で算出するため、全てのクラスの確率の和を1にします。<br>
クラス分類では、入力値はどれか一つのクラスに属するため、そのクラスだけを1に、他のクラスを0にした正解ラベルを用意します。これを一般的にone hot valueと呼びます。

クラス分類 | STOP | LEFT | FOWARD | RIGHT
-- | -- | -- | -- | --
label0 | 1 | 0 | 0 | 0
label1 | 0 | 1 | 0 | 0
label2 | 0 | 0 | 1 | 0
label3 | 0 | 0 | 0 | 1

pythonでは、numpyを使ってone hot valueを作ることが出来ます。<br>
ソースコード：[./to_one_hot_value.py](./to_one_hot_value.py)<br>
```python
# coding: utf-8
import numpy as np
n_classes = 4 # クラス分類の総数
########################################
# ラベル番号をone_hot_valueに変換する
########################################
def to_one_hot_value(int_label):
    one_hot_value = np.zeros((1,n_classes))
    one_hot_value[np.arange(1),np.array([int_label])] = 1
    return one_hot_value

for i in range(n_classes):
    one_hot_value = to_one_hot_value(i)
    print("label:{} one_hot_value:{}".format(i,one_hot_value))
```
> label:0 one_hot_value:[[ 1.  0.  0.  0.]]<br>
> label:1 one_hot_value:[[ 0.  1.  0.  0.]]<br>
> label:2 one_hot_value:[[ 0.  0.  1.  0.]]<br>
> label:3 one_hot_value:[[ 0.  0.  0.  1.]]<br>

今回は学習データ ジェネレータの分岐バグチェックを兼ねてone hot valueを作るのでこのコードは出てきませんが、画像認識などでデータがすでにあり、ラベル付けを別途行わなければならない場合に使います。
<hr>

#### データフォーマット
距離センサーを3個使うので入力値は3つ、出力値はone hot valueで表すので4つとなり、学習データのフォーマットはCSVで表すと以下のようになります。<br>
```csv
#left_sensor,front_sensor,right_sensor,stop,left,foward,right
0,0,0,1,0,0,0
200,200,50,0,1,0,0
200,200,200,0,0,1,0
50,200,200,0,0,0,1
```
[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='3'>

## [Python] 学習データ ジェネレータを作る
学習データフォーマットが決まったので、実際に学習データを作っていきます。<br>
CSVデータを人力で用意していってもよいのですが、IF文で書ける分岐条件なので関数で書いてしまうことにします。<br>
<hr>

<a name='3-1'>

#### 簡単なIF文での判定
level_carで作ったSimpleLabelGenerator。
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

<hr>

#### 車両旋回性能
[簡単なIF文での判定](#3-1)のラベルジェネレータはlevel1_carで実際に使っていますが、車両の旋回性能に合わせたカスタマイズがあってもよいかもしれません。そこで、車両がどのように旋回するのかを考慮してみます。<br>
(実際のところ、定常円を描けなかったり左右で旋回半径が異なったりする車両の足回りでは計算通りの旋回にならないので走行具合をみて調整が必要になります。)<br>
<hr>

車両の旋回は、リアタイヤの車軸の延長線上に円の中心が来ることから、旋回イメージを図に描いてみます。
![](./document/magaru1.png)
図に描いてみると、避けきれない前方障害物(点P)の存在も見えてきます。
<hr>

車両データを実測します。<br>
赤い#1202,#605,#103,#902はFabo製プロトタイピング用基板。
![](./document/robotcar.png)
ホイールベースとノーズは個別に使うことはしていないので、単純に全長と考えてよいです。
<hr>

車両データを旋回イメージに当てはめます。
![](./document/magaru2.png)
<hr>


#### 曲がる、止まる判定
車両の旋回イメージが出来たので、旋回に入る距離と、旋回しても回避出来ないため停止と判断する距離を算出します。
![](./document/calc1.png)
止まる為に用意した10cmマージンは、車両制御コード側で前方障害物までの距離を元に速度調整を入れたため、実際の学習データ ジェネレータのコードでは10cmマージンを削除してあります。
<hr>

旋回方向は左右のより空いている方向に曲がればよいのですが、左右どちらにも壁があり曲がれないことも考慮します。
![](./document/habadori.png)
分岐パターンを適当に決めます。3つの距離センサー値はそれぞれ以下の3パターンで考えることが出来ます。
* パターン0： 障害物までの距離が遠いため、制御不要
* パターン1： 障害物までの距離が近いため、制御必要
* パターン2： 障害物までの距離が近すぎるため、その方向には進めない

左前右センサー値をそれぞれこのパターンのどれにあたるのかをIF文で判断し、次に進行方向を決定するための分岐を作成します。
* コントロール1：前2 - 直進も旋回も出来ないため停止する
* コントロール分岐：左01,前1,右01 - 前方障害物あり。左右旋回可能。左右の距離が遠い方に曲がる
  * コントロール2：右の方が距離が遠い場合。右に曲がる
  * コントロール3：左の方が距離が遠い場合。左に曲がる
* コントロール4：右0前0左0 - 制御不要のため、直進する
* コントロール5：左12右0 - 左は障害物までの距離が近いか近すぎるため、右に曲がる
* コントロール6：左0右12 - 右は障害物までの距離が近いか近すぎるため、左に曲がる
* コントロール7：左2右2 - 左も右も旋回不可能。前方はコントロール1を通過しているので進行可能。直進するが、もしかしたら壁にぶつかる可能性もある
* コントロール分岐：左1右1 - 左右どちらも障害物に近いので、真ん中になるように幅調整をする
  * コントロール8：右の方が距離が遠い場合。右に曲がる
  * コントロール9：左の方が距離が遠い場合。左に曲がる
* コントロール10：左2右1 - 左は障害物までの距離が近すぎるため、右に曲がる
* コントロール11：左1右2 - 右は障害物までの距離が近すぎるため、左に曲がる

制御分岐を通ったら[簡単なIF文での判定](#3-1)と同様にone hot valueで値を返して学習データ ジェネレータは完成です。<br>

ラベル ジェネレータ：[./generator/labelgenerator.py](./generator/labelgenerator.py)<br>
学習データ ジェネレータ：[./MLP/train_model.py](./MLP/train_model.py)<br>
```python
def generate_random_train_data(n_rows):
    '''
    ランダムなセンサー値と、それに対応するラベルデータを作成する
    args:
        n_rows: 作成するデータ件数
    return:
        batch_data: センサー値
        batch_target: ラベルデータ
    '''
    csvdata=[]
    # 2m以内のランダムなINT値を作成する
    sensors = np.random.randint(0,200,[n_rows,DATA_COLS])

    for i in range(n_rows):
        generator_result = generator.get_label(sensors[i])
        csvrow = np.hstack((sensors[i],generator_result))
        csvdata.append(csvrow)
    csvdata = np.array(csvdata)

    batch_data = csvdata[0:n_rows,0:DATA_COLS]
    batch_target = csvdata[0:n_rows,DATA_COLS:]
    return batch_data, batch_target
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='4'>

## [Neural Networks] 学習モデルについて
学習モデルはシンプルなMulti-Layer Perceptronで作成します。
#### Multi-Layer Perceptron
![](./document/mlp.png)
入力層はセンサー値を入れるため3入力を持ちます。<br>
隠れ層は1つだけ持ち、11ノードを用意します。各ノードは3つのセンサー値を入力に持ちます。<br>
隠れ層と出力層では全ての入力線で個別にweightを持ち、各ノード毎にbiasを持ちます。<br>
Neural Networksではこのweightとbiasの値が学習成果となり、ノードの形をモデルと呼びます。値とモデル構造が分かれていることは主に学習途中からの再開時(checkpointからの値のrestore)や、学習成果を凍結する時(ノード情報と値をpbファイルに保存。freeze graph)に現れます。

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='5'>

## [Python/TensorFlow] 学習用コードのコーディング
#### 学習コード設計
* 簡単かつスケール増減が単純なMulti-Layer Perceptronモデルとする
* 学習データ ジェネレータを作成する
* 実装はミニバッチでおこなう
* 学習データ処理にはスレッドセーフなデータスタックが可能なqueueを用いる
* 予測時に用いる入出力オペレーションには名前を付ける
* ステップ数を記録する
* checkpoint保存と途中から再開する
* Tensorboard用にsummary出力する
* 定数の変数は大文字にする

ミニバッチとは、学習時に特徴量を算出しやくするために、学習データを10～100個程度に小分けにしたものになります。<br>
1つのミニバッチデータには各クラスが同数含まれている方が精度が良くなりますが、今回は気にしないことにします。<br>
1ステップ毎の学習中に次のステップで使う学習データを準備するために、ミニバッチのデータ作成はスレッドで実行してqueueに入れます。<br>
。<br>

<hr>

![](./document/code-design1.png)
![](./document/code-design2.png)
![](./document/code-design3.png)
![](./document/code-design4.png)
![](./document/code-design5.png)
<hr>

センサー値の入力変数はplaceholder_input_dataとdequeue_input_dataの2種類あります。<br>
予測実行時のセンサー値の入力変数はdequeue_input_dataとなるオペレーション名dequeue_op:0を使います。<br>
学習コード：[./MLP/train_model.py](./MLP/train_model.py)
```python
    dequeue_input_data, dequeue_input_target = queue.dequeue_many(placeholder_batch_size, name='dequeue_op') # instead of data/target placeholder
```
<hr>

ミニバッチサイズを可変とするためにplaceholderを使い、行数をNoneとしています。<br>
学習コード：[./MLP/train_model.py](./MLP/train_model.py)
```python
placeholder_input_data = tf.placeholder('float', [None, DATA_COLS], name='input_data') # for load_and_enqueue. use dequeue_op:0 for prediction
```
<hr>

placeholderの行数をNoneとすることで、1つの値を予測するためであっても予測にかけるデータは配列に入れる必要が生じますが([[左センサー値,前センサー値,右センサー値]])、学習時のミニバッチサイズと予測時のデータ件数は異なるため、入力変数に使うplaceholderの行数はNoneとすることで、モデルで可変行数の入力値を扱えるようにします。<br>
予測実行コード：[./MLP/run_ai_test.py](./MLP/run_ai_test.py)
```python
        # センサー値をランダムな0-1000の範囲で作成する
        # sensors = [[LEFT45,FRONT,RIGHT45]]
        sensors = np.array([np.random.randint(0,1000,3)])

        # 予測を実行する
        _output_y,_score = sess.run([output_y,score],feed_dict={input_x:sensors})
```
<hr>

ミニバッチデータは学習とは別のスレッドで作成するので、スレッドセーフなqueueに入れておきます。<br>
queueには1ステップ分の学習データを入れておくので、queueの容量をBATCH_SIZEにしてあります。<br>
TensorFlowでは、オペレーションの実行はsess.run()で指定したオペレーションと関連しているオペレーションが連鎖的に実行されるため、ここはqueueの出し入れについてのオペレーション定義をしている部分となります。<br>
ソースコード：[./MLP/train_model.py](./MLP/train_model.py)
```python
CHUNK_SIZE = BATCH_SIZE*1 # queueで保持するデータ件数
...
with tf.variable_scope("queue"):
    queue = tf.FIFOQueue(
        capacity=CHUNK_SIZE, # enqueue size
        dtypes=['float', 'float'],
        shapes=[[DATA_COLS], [N_CLASSES]],
        name='FIFOQueue'
    )

    # Enqueue and dequeue operations
    enqueue_op = queue.enqueue_many([placeholder_input_data, placeholder_input_target], name='enqueue_op')
    # dequeue_manyでBATCH_SIZE分のデータを取得する。テストデータや実際に予測時に使う可変個数のデータ件数に対応するためにplaceholderで取得件数を指定する。
    dequeue_input_data, dequeue_input_target = queue.dequeue_many(placeholder_batch_size, name='dequeue_op') # instead of data/target placeholder
```

load_and_enqueue()が学習データをqueueに入れる役割になります。これはスレッドで動作させています。<br>
無限ループにあるsess.run()でenqueue_opを実行していますが、queueには指定した容量分しか入らないので、dequeue_many()によってqueueが空になるまで待機することになります。<br>
ソースコード：[./MLP/train_model.py](./MLP/train_model.py)
```python
N_THREADS = 1 # データ生成スレッド件数。ミニバッチデータ作成時間より学習時間の方が処理負荷が高いので、データ生成スレッドは1スレッドにする
...
def load_and_enqueue(sess):
    while True:
        try:
            batch_data, batch_target = generate_random_train_data(BATCH_SIZE)
            sess.run(enqueue_op, feed_dict={placeholder_input_data:batch_data, placeholder_input_target:batch_target})
            #logging.debug("running")
        except tf.errors.CancelledError as e:
            break
    print("finished enqueueing")
...
    # 学習データ ジェネレータを用いてミニバッチデータを作成し、enqueue_op実行によりqueueへデータを挿入するスレッドを開始する
    for i in range(N_THREADS):
        enqueue_thread = threading.Thread(target=load_and_enqueue, args=[sess])
        enqueue_thread.isDaemon()
        enqueue_thread.start()
```

queueからミニバッチデータを取得するのは、dequeue_opと名付けたオペレーションがsess.run()によって実行された時になります。<br>
これはtrain_opが実行された時に、連鎖的に実行されるオペレーションになります。<br>
実際にコードを追ってみましょう。<br>
ソースコード：[./MLP/train_model.py](./MLP/train_model.py)
```python
    # 中間層計算
    layer_1 = tf.add(tf.matmul(dequeue_input_data,hidden_layer_1['weights']), hidden_layer_1['biases'])
    layer_1 = tf.nn.relu(layer_1)
...
    prediction = tf.add(tf.matmul(layer_1,output_layer['weights']), output_layer['biases'], name='output_y')
...
    losses = tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=dequeue_input_target)
    loss_op = tf.reduce_mean(losses, name='cost')
...
train_op = tf.train.AdamOptimizer(0.0001).minimize(loss_op, name='train_op')
...
            _, batch_loss, w_summary = sess.run([train_op, loss_op, summary_op],
                                                feed_dict={placeholder_batch_size:BATCH_SIZE})
```
train_opがsess.run()で実行されると、loss_op->losses->prediction->layer_1->dequeue_input_dataまで連鎖的に実行されることになります。<br>
この時、dequeue_many()が実行され、queueにある学習データが取得されます。<br>
このコードでは、accuracyとtrain_opをsess.run()で実行した時に、queueからのデータ取得が実行されます。<br>
また、queueからデータ取得が実行された瞬間に、新たにqueueにデータが挿入されることになります。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='6'>

## [Python/TensorFlow] 学習と保存
#### 学習実行
> `cd ./MLP/`<br>
> `python train_model.py`<br>

学習はTARGET_STEPまで学習を行います。<br>
学習コード：[./MLP/train_model.py](./MLP/train_model.py)
```python
TARGET_STEP = 10000 # ステップ数
```
今回はステップ数もモデルに変数として保存しているので、(途中から再開しても)TARGET_STEPまで学習したらそこで終了します。<br>
TARGET_STEPを増やすことで、さらに学習させることが出来ます。
<hr>

#### 保存と読み込み
保存と読み込みには2種類の方法があります。
* 再学習可能な方法
  * checkpointに保存
  * checkpointを読み込む
* 凍結する方法
  * pbファイルに保存
  * pbファイルを読み込む

checkpointに保存すると、学習・実行に必要な全てのモデル構成と変数値が保存されます。そのため、checkpointを読み込むことで学習を再開することが出来ます。<br>
checkpointでは、モデル構成と学習した変数値はそれぞれ別のファイルに保存されるため、読み込みはモデルの読み込み方と、学習値の復元の2種類あります。<br>

pbファイルで保存すると、予測に必要なオペレーション名だけを指定してモデル構成と変数値を保存することが出来ます。そのため、再学習に用いることは出来ませんが、バイナリサイズは小さくなります。<br>
pbファイルでは変数値を定数に変換しモデル構成の中に埋め込みます。

step数を記録するために用意したstep変数に関連する情報：pbファイル変換前
```
step/input_step [<tf.Tensor 'step/input_step:0' shape=<unknown> dtype=int32>]
step/step/initial_value [<tf.Tensor 'step/step/initial_value:0' shape=() dtype=int32>]
step/step [<tf.Tensor 'step/step:0' shape=() dtype=int32_ref>]
step/step/Assign [<tf.Tensor 'step/step/Assign:0' shape=() dtype=int32_ref>]
step/step/read [<tf.Tensor 'step/step/read:0' shape=() dtype=int32>]
step/Assign [<tf.Tensor 'step/Assign:0' shape=() dtype=int32_ref>]
```
step数を記録するために用意したstep変数に関連する情報：pbファイル変換後
```
prefix/step/step [<tf.Tensor 'prefix/step/step:0' shape=() dtype=int32>]
```

neural_network_model/Variable_1に関する情報：pbファイル変換前
```
neural_network_model/Variable_1 [<tf.Tensor 'neural_network_model/Variable_1:0' shape=(3, 11) dtype=float32_ref>]
neural_network_model/Variable_1/IsVariableInitialized [<tf.Tensor 'neural_network_model/Variable_1/IsVariableInitialized:0' shape=() dtype=bool>]
neural_network_model/Variable_1/cond/Switch [<tf.Tensor 'neural_network_model/Variable_1/cond/Switch:0' shape=() dtype=bool>, <tf.Tensor 'neural_network_model/Variable_1/cond/Switch:1' shape=() dtype=bool>]
neural_network_model/Variable_1/cond/switch_t [<tf.Tensor 'neural_network_model/Variable_1/cond/switch_t:0' shape=() dtype=bool>]
neural_network_model/Variable_1/cond/switch_f [<tf.Tensor 'neural_network_model/Variable_1/cond/switch_f:0' shape=() dtype=bool>]
neural_network_model/Variable_1/cond/pred_id [<tf.Tensor 'neural_network_model/Variable_1/cond/pred_id:0' shape=() dtype=bool>]
neural_network_model/Variable_1/cond/read/Switch [<tf.Tensor 'neural_network_model/Variable_1/cond/read/Switch:0' shape=(3, 11) dtype=float32_ref>, <tf.Tensor 'neural_network_model/Variable_1/cond/read/Switch:1' shape=(3, 11) dtype=float32_ref>]
neural_network_model/Variable_1/cond/read [<tf.Tensor 'neural_network_model/Variable_1/cond/read:0' shape=(3, 11) dtype=float32>]
neural_network_model/Variable_1/cond/Switch_1 [<tf.Tensor 'neural_network_model/Variable_1/cond/Switch_1:0' shape=(3, 11) dtype=float32>, <tf.Tensor 'neural_network_model/Variable_1/cond/Switch_1:1' shape=(3, 11) dtype=float32>]
neural_network_model/Variable_1/cond/Merge [<tf.Tensor 'neural_network_model/Variable_1/cond/Merge:0' shape=(3, 11) dtype=float32>, <tf.Tensor 'neural_network_model/Variable_1/cond/Merge:1' shape=() dtype=int32>]
neural_network_model/Variable_1/neural_network_model/Variable/read_neural_network_model/Variable_1_0 [<tf.Tensor 'neural_network_model/Variable_1/neural_network_model/Variable/read_neural_network_model/Variable_1_0:0' shape=(3, 11) dtype=float32>]
neural_network_model/Variable_1/Assign [<tf.Tensor 'neural_network_model/Variable_1/Assign:0' shape=(3, 11) dtype=float32_ref>]
neural_network_model/Variable_1/read [<tf.Tensor 'neural_network_model/Variable_1/read:0' shape=(3, 11) dtype=float32>]

neural_network_model/Variable_1/Adam/Initializer/zeros [<tf.Tensor 'neural_network_model/Variable_1/Adam/Initializer/zeros:0' shape=(3, 11) dtype=float32>]
neural_network_model/Variable_1/Adam [<tf.Tensor 'neural_network_model/Variable_1/Adam:0' shape=(3, 11) dtype=float32_ref>]
neural_network_model/Variable_1/Adam/Assign [<tf.Tensor 'neural_network_model/Variable_1/Adam/Assign:0' shape=(3, 11) dtype=float32_ref>]
neural_network_model/Variable_1/Adam/read [<tf.Tensor 'neural_network_model/Variable_1/Adam/read:0' shape=(3, 11) dtype=float32>]
neural_network_model/Variable_1/Adam_1/Initializer/zeros [<tf.Tensor 'neural_network_model/Variable_1/Adam_1/Initializer/zeros:0' shape=(3, 11) dtype=float32>]
neural_network_model/Variable_1/Adam_1 [<tf.Tensor 'neural_network_model/Variable_1/Adam_1:0' shape=(3, 11) dtype=float32_ref>]
neural_network_model/Variable_1/Adam_1/Assign [<tf.Tensor 'neural_network_model/Variable_1/Adam_1/Assign:0' shape=(3, 11) dtype=float32_ref>]
neural_network_model/Variable_1/Adam_1/read [<tf.Tensor 'neural_network_model/Variable_1/Adam_1/read:0' shape=(3, 11) dtype=float32>]

train_op/update_neural_network_model/Variable_1/ApplyAdam [<tf.Tensor 'train_op/update_neural_network_model/Variable_1/ApplyAdam:0' shape=(3, 11) dtype=float32_ref>]
```

neural_network_model/Variable_1に関する情報：pbファイル変換後
```
prefix/neural_network_model/Variable_1 [<tf.Tensor 'prefix/neural_network_model/Variable_1:0' shape=(3, 11) dtype=float32>]
prefix/neural_network_model/Variable_1/read [<tf.Tensor 'prefix/neural_network_model/Variable_1/read:0' shape=(3, 11) dtype=float32>]
```

prefixはpb読み込み時に追加した接頭辞<br>
学習コード：[./MLP/run_ai.py](./MLP/run_ai.py)
```python
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def, 
            input_map=None, 
            return_elements=None, 
            name="prefix", 
            op_dict=None, 
            producer_op_list=None
        )
```

<hr>

#### 再利用可能な方法
学習途中で保存したり、学習コード内で保存する際はcheckpointに保存します。
<hr>

#### checkpointに保存
学習コードで途中経過や学習完了時に保存する時はcheckpointを使います。
```python
saver = tf.train.Saver(max_to_keep=100)
''' 学習を実行 '''
saver.save(sess, MODEL_DIR + '/model-'+str(step)+'.ckpt')
```
checkpointはデフォルトでは最新5件までしか残さないため、長時間の学習を行う時はmax_to_keepの値を指定しておきます。<br>
例えば5000万ステップを学習する場合は、checkpointは100万ステップ毎に保存する感じで使います。<br>

学習コード：[./MLP/train_model.py](./MLP/train_model.py)
```python
            # 1000000 step毎にsaveする
            if step % 1000000 == 0:
                _step = sess.run(step_op,feed_dict={placeholder_step:step}) # variable_stepにstepを記録する
                saver.save(sess, MODEL_DIR + '/model-'+str(step)+'.ckpt')
```
checkpointへの保存で使うsaver.save()は、学習済みの値の他にモデル構成情報となるmeta_graphも出力します。
<hr>

#### checkpointを読み込む
今回は、学習コードにモデルをフルスクラッチで書いているので、checkpointからのモデル情報の復元はスキップして、変数値だけを復元して再開します。<br>
学習コード：[./MLP/train_model.py](./MLP/train_model.py)
```python
saver = tf.train.Saver(max_to_keep=100)
with tf.Session() as sess:
    ckpt = tf.train.get_checkpoint_state(MODEL_DIR)
    if ckpt:
        # checkpointファイルから最後に保存したモデルへのパスを取得する
        last_model = ckpt.model_checkpoint_path
        print("load {}".format(last_model))
        # 学習済みモデルを読み込む
        saver.restore(sess, last_model)
    else:
        print("initialization")
        # 初期化処理
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
```
checkpointがある場合、学習済みの変数値をsaver.restore()で復元します。この時、checkpointのモデル情報と今のモデル情報が一致している必要があります。モデル情報を変更していると復元に失敗します。<br>
checkpointが無い場合は、tf.global_variables_initializer()でモデルの変数値を初期化します。
<hr>

#### 凍結する方法
checkpointから復元した再学習可能なフルモデルデータでも予測は出来ますが、実行環境においては学習でしか使わない情報は無駄なので削り落として必要なものだけをpbファイルに保存したものを使います。<br>
<hr>

#### pbファイルに保存
> `cd ./MLP/`<br>
> `python freeze_graph.py`<br>

./MLP/model/car_model.pb ファイルが作成されます。<br>
pbファイル作成コード：[./MLP/freeze_graph.py](./MLP/freeze_graph.py)

![](./document/freeze-design1.png)
学習コードで学習済みモデルのpbファイルを作ろうとすると、学習時のセッションとは別のセッションを作成して変数値を再読み込みしないといけないため、pbファイルを作成するコードは学習コードとは別に用意します。<br>
<hr>

予測時に使うOP名は、学習コードで付けた名前になります。tf.variable_scope()で名前スコープを付けた場合はスコープ名から必要になります。<br>
学習コード：[./MLP/train_model.py](./MLP/train_model.py)
```python
with tf.variable_scope("queue"):
...
    dequeue_input_data, dequeue_input_target = queue.dequeue_many(placeholder_batch_size, name='dequeue_op') # instead of data/target placeholder
```
pbファイル作成コード：[./MLP/freeze_graph.py](./MLP/freeze_graph.py)
```python
OUTPUT_NODE_NAMES="queue/dequeue_op,neural_network_model/output_y,neural_network_model/score,step/step"
```
ここで名付けたdequeue_opは、予測実行時にdequeue_op:0をセンサー値入力用に使います。dequeue_op:1は正解ラベル用になりますが、予測に使うことはありません。

<hr>

OP名が分からない時は、表示されるOP名から推測してください。<br>
pbファイル作成コード：[./MLP/freeze_graph.py](./MLP/freeze_graph.py)
```python
def print_graph_operations(graph):
    # print operations
    print("----- operations in graph -----")
    for op in graph.get_operations():
        print("{} {}".format(op.name,op.outputs))
...
        # print operations
        print_graph_operations(graph)
```
```
----- operations in graph -----
input/input_data [<tf.Tensor 'input/input_data:0' shape=(?, 3) dtype=float32>]
input/input_target [<tf.Tensor 'input/input_target:0' shape=<unknown> dtype=float32>]
input/batch_size [<tf.Tensor 'input/batch_size:0' shape=<unknown> dtype=int32>]
step/input_step [<tf.Tensor 'step/input_step:0' shape=<unknown> dtype=int32>]
step/step/initial_value [<tf.Tensor 'step/step/initial_value:0' shape=() dtype=int32>]
step/step [<tf.Tensor 'step/step:0' shape=() dtype=int32_ref>]
step/step/Assign [<tf.Tensor 'step/step/Assign:0' shape=() dtype=int32_ref>]
step/step/read [<tf.Tensor 'step/step/read:0' shape=() dtype=int32>]
step/Assign [<tf.Tensor 'step/Assign:0' shape=() dtype=int32_ref>]
```

freeze_graph.pyは、他のモデルのcheckpointでも使うことが出来ます。
<hr>

基本的に学習マシンと実行マシンは異なるため、通常はモデル構成情報からデバイス情報を削除してcheckpointからモデル構成を復元します。<br>
pbファイル作成コード：[./MLP/freeze_graph.py](./MLP/freeze_graph.py)
```python
CLEAR_DEVICES=True
...
        # Graphを読み込む
        # We import the meta graph and retrieve a Saver
        saver = tf.train.import_meta_graph(last_model + '.meta', clear_devices=CLEAR_DEVICES)
```
tf.train.import_meta_graph()でモデル構成が復元され、さらにsaverが作成されます。<br>
<hr>

モデル構成を読み込んだら、グラフ定義を取得します。<br>
pbファイル作成コード：[./MLP/freeze_graph.py](./MLP/freeze_graph.py)
```python
        # We retrieve the protobuf graph definition
        graph = tf.get_default_graph()
        graph_def = graph.as_graph_def()
```
<hr>

学習済みの変数値を復元します。<br>
pbファイル作成コード：[./MLP/freeze_graph.py](./MLP/freeze_graph.py)
```python
        saver.restore(sess, last_model)
```

<hr>

必要なモデル情報だけに削り落とします。<br>
pbファイル作成コード：[./MLP/freeze_graph.py](./MLP/freeze_graph.py)
```python
        # We use a built-in TF helper to export variables to constants
        output_graph_def = graph_util.convert_variables_to_constants(
            sess, # The session is used to retrieve the weights
            graph_def, # The graph_def is used to retrieve the nodes
            OUTPUT_NODE_NAMES.split(",") # The output node names are used to select the usefull nodes
        )
```
<hr>

pbファイルにバイナリデータで保存します。<br>
pbファイル作成コード：[./MLP/freeze_graph.py](./MLP/freeze_graph.py)
```python
        tf.train.write_graph(output_graph_def, MODEL_DIR,
                             FROZEN_MODEL_NAME, as_text=False)
```
as_text=Trueにすると、テキストファイルで保存することが出来ます。

<a name="6-4">

#### pbファイルを読み込む
予測実行を行うアプリケーションでは、pbファイルを読み込んで予測を実行します。<br>
予測実行コード：[./MLP/run_ai_test.py](./MLP/run_ai_test.py)
```python
def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the 
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we can use again a convenient built-in function to import a graph_def into the 
    # current default Graph
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def, 
            input_map=None, 
            return_elements=None, 
            name="prefix", 
            op_dict=None, 
            producer_op_list=None
        )
    return graph

graph = load_graph(MODEL_DIR+"/"+FROZEN_MODEL_NAME)
...
with tf.Session(graph=graph) as sess:
```
モデルを読み込む際にname="prefix"でモデル毎にprefix名を付けておくと、複数のモデルを使う場合に区別しやすくなります。<br>
読み込んだモデル(graph)はtf.Session()の引数に渡します。<br>
<hr>

予測実行で使う変数はオペレーション名から取得します。<br>
予測実行コード：[./MLP/run_ai_test.py](./MLP/run_ai_test.py)
```python
input_x = graph.get_tensor_by_name('prefix/queue/dequeue_op:0')
output_y = graph.get_tensor_by_name('prefix/neural_network_model/output_y:0')
score = graph.get_tensor_by_name('prefix/neural_network_model/score:0')
step = graph.get_tensor_by_name('prefix/step/step:0')
```
<hr>

pbファイルを読み込みオペレーションを用意したら、予測実行が出来るようになります。<br>
予測実行コード：[./MLP/run_ai_test.py](./MLP/run_ai_test.py)
```python
with tf.Session(graph=graph) as sess:
...
        # センサー値をランダムな0-1000の範囲で作成する
        # sensors = [[LEFT45,FRONT,RIGHT45]]
        sensors = np.array([np.random.randint(0,1000,3)])

        # 予測を実行する
        _output_y,_score = sess.run([output_y,score],feed_dict={input_x:sensors})
``` 

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='7'>

## [Python/TensorFlow] 予測を実行
![](./document/prediction-design1.png)
[pbファイルを読み込む](#6-4)で予測実行までを見ました。
* モデルの読み込み
* 入出力オペレーションの変数取得
* 読み込んだモデルでセッションを開始
* 入力値作成
* 予測実行

最後に、予測結果から最も確率の高いものは何なのか？を知る必要があります。<br>
予測実行コード：[./MLP/run_ai_test.py](./MLP/run_ai_test.py)
```python
        # 予測を実行する
        _output_y,_score = sess.run([output_y,score],feed_dict={input_x:sensors})
        # 予測結果から最も大きな値の配列番号を取得する
        max_value = np.argmax(_output_y[0]) # max_value: 0:STOP,1:LEFT,2:FORWARD,3:RIGHT
        # そのスコアを取得する
        max_score = _score[0][max_value]
        print("max_value:{} score:{} input:{}".format(max_value,max_score,sensors))
```
max_valueが0:STOP,1:LEFT,2:FORWARD,3:RIGHTを示す予測結果となります。<br>
max_scoreはその点数で、1.0に近い方が強く結果を示していることになります。<br>

<hr>

#### 距離センサーから値を取得して予測を実行する
入力値を実際の距離センサーから取得して予測を実行します。<br>
予測実行コード：[./MLP/run_ai_test.py](./MLP/run_ai_test.py)<br>
```python
        sensors = np.array([np.random.randint(0,1000,3)])
```
この部分をセンサー値に書き換えればいいのですが、これまでの./MLP/ディレクトリは学習用としておいて、作成したモデル(pbファイル)は実行環境向けに場所にコピーします。<br>
> `mkdir ./model/`<br>
> `cp ./MLP/model/car_model.pb ./model/`<br>

距離センサー値の取得方法はlevel_carと同じになります。<br>
TensorFlow部分はAIクラスとして書いてあります。<br>
距離センサーFabo #224 Distance用ライブラリ：[./fabolib/kerberos_vl53l0x.py](./fabolib/kerberos_vl53l0x.py)<br>
距離センサーLidarLite v3用ライブラリ：[./fabolib/kerberos.py](./fabolib/kerberos.py)<br>
AIライブラリ：[./lib/ai.py](./lib/ai.py)<br>
予測実行コード：[./run_ai.py](./run_ai.py)<br>
```python
from fabolib import KerberosVL53L0X as Kerberos
...
    # 距離センサー準備
    kerberos = Kerberos()
    # Lidar取得間隔(秒)
    LIDAR_INTERVAL = 0.05
...
            ########################################
            # 距離センサー値を取得する
            ########################################
            distance1,distance2,distance3 = kerberos.get_distance()
            sensors = [distance1,distance2,distance3]
```
> `python run_ai.py`<br>

このコードを実行するには、Fabo #902 Kerberos基板とFabo #224 Distanceが必要になります。<br>
LidarLite v3を使っている場合は、import部分を以下のように変更してください。<br>
```python
from fabolib import Kerberos
#from fabolib import KerberosVL53L0X as Kerberos
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='8'>

## [Python/TensorFlow] 予測精度を評価
入力値はfor文で生成可能で、対応する正解ラベルはIF文で求めることが出来るため、網羅的に予測を実行し、IF文の結果と比較することで精度を評価してみることにします。<br>

一度に400000件の入力データを作成し、予測にかけます。1件ずつ予測するよりも速く予測出来ます。<br>
予測実行コード：[./run_ai_eval.py](./run_ai_eval.py)
```python
    # 評価する距離範囲
    MIN_RANGE = 0
    MAX_RANGE = 200
    try:
        learned_step = ai.get_learned_step()
        print("learned_step:{}".format(learned_step))

        ########################################
        # 距離センサー値を生成する
        ########################################
        sensors=[]
        for distance1 in range(MIN_RANGE,MAX_RANGE):
            for distance2 in range(MIN_RANGE,MAX_RANGE):
                for distance3 in range(MIN_RANGE,MAX_RANGE):
                    sensors.append([distance1,distance2,distance3])
            if (distance1+1) % 10 == 0:
                sensors=np.array(sensors)

                ########################################
                # AI予測結果を取得する
                ########################################
                # 今回の予測結果を取得する
                ai_values = ai.get_predictions(sensors,SCORE)
```
ジェネレータは一気に複数行を計算出来ないので、予測結果と一件ずつ比較します。<br>
予測実行コード：[./run_ai_eval.py](./run_ai_eval.py)
```python
                n_rows = len(sensors)
                for i in range(n_rows):
                    counter +=1
                    # 予測結果のスコアが低かった回数をカウントする
                    if ai_values[i] == ai.get_other_label():
                        bad_score_counter += 1

                    ########################################
                    # IF結果を取得する
                    ########################################
                    # 今回の結果を取得する
                    generator_result = generator.get_label(sensors[i])
                    if_value = np.argmax(generator_result)

                    # 予測結果とジェネレータ結果が異なった回数をカウントする
                    if not if_value == ai_values[i]:
                        miss_counter += 1
                        # 不一致の予測結果をコンソールに表示する
                        print_log(sensors[i],ai,ai_values[i],if_value,counter,miss_counter,bad_score_counter)
```
<hr>

学習範囲(0-199)の評価は精度はかなりよくなりますが、800万件の予測を実行するのでJetson TX2でそこそこ時間がかかります。<br>
読み込むモデルはAIクラスを初期化する際に変更できます。<br>
評価実行コード：[./run_ai_eval.py](./run_ai_eval.py)<br>
```python
    # AI準備
    ai = AI("car_model.pb")
```

> `time python ./run_ai_eval.py > eval.log`<br>
> real	11m12.715s<br>
> user	11m11.452s<br>
> sys	0m5.844s<br>

*学習範囲(0-199)*

学習ステップ数 | 精度 | 不一致件数 | 低スコア件数
-- | -- | -- | --
10M | 0.999633875 | 2929 | 2890
20M | 0.9999945 | 44 | 14
30M | 0.999986 | 112 | 102
40M | 0.999991875 | 65 | 51
50M | 0.99979775 | 1618 | 1176

<hr>

学習範囲外(0-399から学習範囲を除外)の精度の評価はデータ件数が5600万件と多いためJetson TX2ではかなり時間がかかります。<br>
> `time python ./run_ai_eval_400.py > eval_400.log`<br>
> real    77m28.863s<br>
> user    77m24.504s<br>
> sys     0m33.284s<br>

*学習範囲外(0-399から学習範囲を除外)*

学習ステップ数 | 精度 | 不一致件数 | 低スコア件数
-- | -- | -- | --
10M | 0.91746125 | 4622170 | 116278
20M | 0.9027016071428572 | 5448710 | 59344
30M | 0.9085851071428571 | 5119234 | 74547
40M | 0.9152485535714285 | 4746081 | 30425
50M | 0.9193687857142857 | 4515348 | 40832

<hr>

この評価結果はとても興味深いことを示しています。<br>
50Mステップまでで見てみると、20Mステップは学習範囲内のデータで精度がよくなっていますが、学習範囲外では50Mステップより精度が悪いことが分かります。<br>
学習時に記録したTensorBoardのlossの値も見てみます。<br>
![](./document/tensorboard1.png)

学習ステップを重ねることで、lossが減ってきているように見えるので、トータル的には学習ステップを重ねれば精度が上がるのではないかと思われます。<br>

もう少し学習を進めてみます。<br>

*学習範囲(0-199)*

学習ステップ数 | 精度 | 不一致件数 | 低スコア件数
-- | -- | -- | --
60M | 0.999956625 | 347 | 344
70M | 0.99999925 | 6 | 2
80M | 0.999999625 | 3 | 2
90M | 0.99999925 | 6 | 1
100M | 0.999999625 | 3 | 0
110M | 0.999999625 | 3 | 1
120M | 0.9999995 | 4 | 2
130M | 0.99999925 | 6 | 2
140M | 0.999998875 | 9 | 3
150M | 0.9999995 | 4 | 0

<hr>

*学習範囲外(0-399から学習範囲を除外)*

学習ステップ数 | 精度 | 不一致件数 | 低スコア件数
-- | -- | -- | --
60M | 0.9232642142857143 | 4297204 | 42645
70M | 0.9267239285714286 | 4103460 | 31735
80M | 0.9253654285714286 | 4179536 | 31836
90M | 0.9089407857142857 | 5099316 | 45796
100M | 0.907304625 | 5190941 | 47454
110M | 0.913579625 | 4839541 | 40684
120M | 0.9103865714285714 | 5018352 | 39680
130M | 0.9080933928571429 | 5146770 | 43341
140M | 0.9049904107142858 | 5320537 | 44950
150M | 0.9081959821428571 | 5141025 | 41063

<hr>

![](./document/tensorboard2.png)
![](./document/tensorboard3.png)

<hr>

70Mステップで学習範囲内の精度と学習範囲外の精度の両方が頭打ちになり、その後は学習範囲外で2%程の精度差が出ています。<br>
学習範囲内での誤判定箇所を見てみると、大体同じデータを間違えているようです。<br>
```
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_70M.log 
learned_step:70000000
accuracy:0.9999984462809404 total:643617 miss:1 bad score:0 result:STOP [16 18 16] - ng generator:FORWARD
accuracy:0.9999970743167432 total:683601 miss:2 bad score:0 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.9999956114815346 total:683602 miss:3 bad score:0 result:FORWARD [17 18  1] - ng generator:LEFT
accuracy:0.9999941503449102 total:683801 miss:4 bad score:0 result:FORWARD [17 19  0] - ng generator:LEFT
accuracy:0.9999926900691666 total:684001 miss:5 bad score:1 result:BAD SCORE [17 20  0] - ng generator:LEFT
accuracy:0.9999912283010096 total:684018 miss:6 bad score:2 result:BAD SCORE [17 20 17] - ng generator:RIGHT
accuracy:0.99999925 total:8000000 miss:6 bad score:2
main end
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_80M.log 
learned_step:80000000
accuracy:0.9999984462809404 total:643617 miss:1 bad score:1 result:BAD SCORE [16 18 16] - ng generator:FORWARD
accuracy:0.9999970743167432 total:683601 miss:2 bad score:1 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.999999624065191 total:7980107 miss:3 bad score:2 result:BAD SCORE [199 100 106] - ng generator:LEFT
accuracy:0.999999625 total:8000000 miss:3 bad score:2
main end
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_90M.log 
learned_step:90000000
accuracy:0.9999984462809404 total:643617 miss:1 bad score:0 result:STOP [16 18 16] - ng generator:FORWARD
accuracy:0.9999970743167432 total:683601 miss:2 bad score:0 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.9999956127586828 total:683801 miss:3 bad score:0 result:FORWARD [17 19  0] - ng generator:LEFT
accuracy:0.9999994987535253 total:7980106 miss:4 bad score:1 result:BAD SCORE [199 100 105] - ng generator:LEFT
accuracy:0.9999993734419852 total:7980107 miss:5 bad score:1 result:FORWARD [199 100 106] - ng generator:LEFT
accuracy:0.9999992481492254 total:7980307 miss:6 bad score:1 result:FORWARD [199 101 106] - ng generator:LEFT
accuracy:0.99999925 total:8000000 miss:6 bad score:1
main end
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_100M.log 
learned_step:100000000
accuracy:0.9999984462809404 total:643617 miss:1 bad score:0 result:STOP [16 18 16] - ng generator:FORWARD
accuracy:0.9999970743167432 total:683601 miss:2 bad score:0 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.999999624065191 total:7980107 miss:3 bad score:0 result:FORWARD [199 100 106] - ng generator:LEFT
accuracy:0.999999625 total:8000000 miss:3 bad score:0
main end
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_110M.log 
learned_step:110000000
accuracy:0.9999985371583716 total:683601 miss:1 bad score:0 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.999997074321023 total:683602 miss:2 bad score:1 result:BAD SCORE [17 18  1] - ng generator:LEFT
accuracy:0.9999956127586828 total:683801 miss:3 bad score:1 result:FORWARD [17 19  0] - ng generator:LEFT
accuracy:0.999999625 total:8000000 miss:3 bad score:1
main end
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_120M.log 
learned_step:120000000
accuracy:0.9999985371583716 total:683601 miss:1 bad score:0 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.999997074321023 total:683602 miss:2 bad score:1 result:BAD SCORE [17 18  1] - ng generator:LEFT
accuracy:0.9999956127586828 total:683801 miss:3 bad score:1 result:FORWARD [17 19  0] - ng generator:LEFT
accuracy:0.9999994987535882 total:7980107 miss:4 bad score:2 result:BAD SCORE [199 100 106] - ng generator:LEFT
accuracy:0.9999995 total:8000000 miss:4 bad score:2
main end
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_130M.log 
learned_step:130000000
accuracy:0.9999985371583716 total:683601 miss:1 bad score:0 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.999997074321023 total:683602 miss:2 bad score:1 result:BAD SCORE [17 18  1] - ng generator:LEFT
accuracy:0.9999956127586828 total:683801 miss:3 bad score:1 result:FORWARD [17 19  0] - ng generator:LEFT
accuracy:0.999999069853967 total:4300400 miss:4 bad score:2 result:BAD SCORE [107 101 199] - ng generator:FORWARD
accuracy:0.9999993734419852 total:7980107 miss:5 bad score:2 result:FORWARD [199 100 106] - ng generator:LEFT
accuracy:0.9999992481492254 total:7980307 miss:6 bad score:2 result:FORWARD [199 101 106] - ng generator:LEFT
accuracy:0.99999925 total:8000000 miss:6 bad score:2
main end
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_140M.log 
learned_step:140000000
accuracy:0.9999985371583716 total:683601 miss:1 bad score:0 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.999997074321023 total:683602 miss:2 bad score:1 result:BAD SCORE [17 18  1] - ng generator:LEFT
accuracy:0.9999956127586828 total:683801 miss:3 bad score:1 result:FORWARD [17 19  0] - ng generator:LEFT
accuracy:0.9999941520553333 total:684001 miss:4 bad score:2 result:BAD SCORE [17 20  0] - ng generator:LEFT
accuracy:0.9999993703014254 total:7940307 miss:5 bad score:3 result:BAD SCORE [198 101 106] - ng generator:LEFT
accuracy:0.999999248130288 total:7980106 miss:6 bad score:3 result:FORWARD [199 100 105] - ng generator:LEFT
accuracy:0.9999991228187792 total:7980107 miss:7 bad score:3 result:FORWARD [199 100 106] - ng generator:LEFT
accuracy:0.9999989975323005 total:7980307 miss:8 bad score:3 result:FORWARD [199 101 106] - ng generator:LEFT
accuracy:0.9999988722521013 total:7980507 miss:9 bad score:3 result:FORWARD [199 102 106] - ng generator:LEFT
accuracy:0.999998875 total:8000000 miss:9 bad score:3
main end
ubuntu@tegra-ubuntu:~/notebooks/github/RobotCarAI/level1_sensors$ cat eval_150M.log 
learned_step:150000000
accuracy:0.9999985371583716 total:683601 miss:1 bad score:0 result:FORWARD [17 18  0] - ng generator:LEFT
accuracy:0.9999970751724552 total:683801 miss:2 bad score:0 result:FORWARD [17 19  0] - ng generator:LEFT
accuracy:0.999999624065191 total:7980107 miss:3 bad score:0 result:FORWARD [199 100 106] - ng generator:LEFT
accuracy:0.9999994987661502 total:7980307 miss:4 bad score:0 result:FORWARD [199 101 106] - ng generator:LEFT
accuracy:0.9999995 total:8000000 miss:4 bad score:0
main end
```
<hr>

この学習では、これ以上続けても学習成果は上がりそうにありません。<br>
Neural Netwoksを使った学習では、学習の止め時も考えるポイントになります。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='9'>

## ディレクトリとファイルについて
* ディレクトリについて
  * document/ ドキュメント関連
  * fabolib/ Fabo製基板関連
  * generator/ 学習データのラベル生成関連
  * lib/ 予測関連
  * MLP/ 学習とpbファイル作成関連
  * model/ 学習済みモデル置き場
* ファイルについて
  * README.md このファイル
  * run_ai_eval.py 学習範囲内の予測精度評価用コード
  * run_ai_eval_400.py 学習範囲外の予測精度評価用コード
  * run_ai.py センサー値を取得して予測を実行するコード。Fabo #902、LidarLite v3が必要。
  * MLP/train_model.py 学習実行コード
    * MLP/log/にTensorboard用のログファイルが出力される
    * MLP/model/にcheckpointファイルが出力される
  * MLP/freeze_graph.py pbファイル作成コード
    * MLP/model/car_model.pbファイルを作成する
  * MLP/run_ai_test.py ランダム値を入力値として予測を実行するコード

[<ページTOP>](#top)　[<目次>](#0)
<hr>


