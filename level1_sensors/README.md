<a name='top'>

【タイトル】
# レベル1：距離センサーの値をニューラルネットワークで使う
<hr>

【目標】
#### 3つの距離センサーから値を取得し、ロボットカーが走行可能な進行方向をニューラルネットワークモデルを用いて予測する

【画像】
・Raspberry Pi3
・Fabo #605 Motor Shield Raspberry Pi Rev 1.0.1
・Fabo #902 Kerberos ver 1.0.0
・Lidar Lite v3
・USB電源
<hr>

<a name='0'>

【目次】
* [Hardware] [距離センサーLidar Lite v3について](#1)
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
* [Python/TensorFlow] [学習と保存](#6)
* [Python/TensorFlow] [予測を実行](#7)
* [Python/TensorFlow] [予測精度を評価](#8)
* [ディレクトリとファイルについて] (#9)
<hr>

<a name='1'>

## [Hardware] 距離センサーLidar Lite v3について
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

pythonでは、numpyを使ってone hot valueを作ることが出来ます。
```python
# coding: utf-8
import numpy as np
n_classes = 4 # クラス分類の総数
########################################
# ラベル番号をone_hot_valueに変換する
########################################
def toONEHOT(int_label):
    one_hot_value = np.zeros((1,n_classes))
    one_hot_value[np.arange(1),np.array([int_label])] = 1
    return one_hot_value

for i in range(n_classes):
    one_hot_value = toONEHOT(i)
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
```python
# coding: utf-8
import numpy as np
class LabelGenerator():
    def get_label(self,sensors):
        '''
        sensors: [左センサー値,前センサー値,右センサー値]
        '''

        if sensors[0] < 50: # 前方に空きが無い
            return [1,0,0,0] # STOP
        elif sensors[1] < 50: # 左に空きが無い
            return [0,0,0,1] # RIGHT
        elif sensors[2] < 50: # 右に空きが無い
            return [0,1,0,0] # LEFT
        else: # 全方向に空きがある
            return [0,0,1,0] # FOWARD

generator = LabelGenerator()
n_rows = 10 # 作成するデータ件数
sensors = np.random.randint(0,200,[n_rows,3]) # 範囲0-200の値で3つの値を持つ配列をミニバッチ個作る
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
[簡単なIF文での判定](#3-1)で学習データ ジェネレータは出来たも当然ですが、実際の車両の旋回性能に合わせたカスタマイズがあってもよいかもしれません。そこで、車両がどのように旋回するのかを考慮してみます。<br>
(実際のところ、定常円を描けなかったり左右で旋回半径が異なったりする車両の足回りでは計算通りの旋回にならないので走行具合をみて調整が必要になります。)<br>
<hr>

車両の旋回は、リアタイヤの車軸の延長線上に円の中心が来ることから、旋回イメージを図に描いてみます。
![](./document/magaru1.png)
図に描いてみると、避けきれない前方障害物(点P)の存在も見えてきます。
<hr>

車両データを実測します。
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

制御分岐を通ったら[簡単なIF文での判定](#3-1)と同様にone hot valueで値を返して学習データ ジェネレータは完成です。

ラベル ジェネレータ：[./generator/labelgenerator.py](./generator/labelgenerator.py)
学習データ ジェネレータ：[./MLP/train_model.py](./MLP/train_model.py)
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
<hr>

<a name='4'>

## [Neural Networks] 学習モデルについて
学習モデルはシンプルなMulti-Layer Perceptronで作成します。
#### Multi-Layer Perceptron
![](./document/mlp.png)
入力層はセンサー値を入れるため3入力を持ちます。<br>
隠れ層は1つだけ持ち、11ノードを用意します。各ノードは3つのセンサー値を入力に持ちます。<br>
隠れ層と出力層では全ての入力線で個別にweightを持ち、各ノード毎にbiasを持ちます。<br>
Neural Networksではこのweightとbiasの値が学習成果となり、ノードの形をモデルと呼びます。値とモデル構図が分かれていることは主に学習途中からの再開時(checkpointからの値のrestore)や、学習成果を凍結する時(ノード情報と値をpbファイルに保存。freeze graph)に現れます。

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='5'>

## [Python/TensorFlow] 学習用コードのコーディング
#### 学習コード設計
* 簡単かつスケール増減が単純なMulti-Layer Perceptronモデルとする
* 学習データ ジェネレータを作成する
* 実装はミニバッチでおこなう
* 学習データ処理には分散処理が可能なqueueを用いる
* 予測時に用いる入出力オペレーションには名前を付ける
* ステップ数を記録する
* checkpoint保存と途中から再開する
* Tensorboard用にsummary出力する
* 定数の変数は大文字にする

ミニバッチとは、学習時に特徴量を算出しやくするために、学習データを10～100個程度に小分けにしたものになります。<br>
1つのミニバッチデータには各クラスが同数含まれている方が精度が良くなりますが、今回は気にしないことにします。
![](./document/code-design1.png)
![](./document/code-design2.png)
![](./document/code-design3.png)
![](./document/code-design4.png)
![](./document/code-design5.png)
センサー値の入力変数はplaceholder_input_dataとdequeue_input_dataの2種類あります。<br>
予測実行時のセンサー値の入力変数はdequeue_input_dataとなるオペレーション名dequeue_op:0を使います。<br>
学習コード：[./MLP/train_model.py](./MLP/train_model.py)
```python
    dequeue_input_data, dequeue_input_target = queue.dequeue_many(placeholder_batch_size, name='dequeue_op') # instead of data/target placeholder
```
ミニバッチサイズを可変とするためにplaceholderを使い、行数をNoneとしています。<br>
学習コード：[./MLP/train_model.py](./MLP/train_model.py)
```python
placeholder_input_data = tf.placeholder('float', [None, DATA_COLS], name='input_data') # for load_and_enqueue. use dequeue_op:0 for prediction
```
このことで、1つの値を予測するためであっても予測にかけるデータは配列に入れる必要が生じますが([[左センサー値,前センサー値,右センサー値]])、学習時のミニバッチサイズと予測時のデータ件数は異なるため、入力変数に使うplaceholderの行数はNoneとすることで、モデルで可変行数の入力値を扱えるようにします。<br>
予測コード：[./lib/ai.py](./lib/ai.py)
```python
    def get_prediction(self,sensors,score=0):
        '''
        AI予測を実行する
        args:
            sensors: [左センサー値,前センサー値,右センサー値]
            score: 予測結果に必要なスコア閾値。0.0-1.0
        return:
            prediction_index: 予測結果のクラス番号
        '''

        _output_y,_score = self.sess.run([self.output_y,self.score],feed_dict={self.input_x:[sensors]})
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='6'>

## [Python/TensorFlow] 学習と保存
[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='7'>

## [Python/TensorFlow] 予測を実行
[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='8'>

## [Python/TensorFlow] 予測精度を評価
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
  * test/ Fabo基板動作確認関連
* ファイルについて
  * README.md このファイル
  * run_ai_eval.py 予測精度評価用コード
  * run_ai.py センサー値を取得して予測を実行するコード。Fabo基板、LidarLite V3が必要。
  * MLP/train_model.py 学習実行コード
    * MLP/log/にTensorboard用のログファイルが出力される
    * MLP/model/にcheckpointファイルが出力される
  * MLP/freeze_graph.py pbファイル作成コード
    * MLP/model/car_model.pbファイルを作成する
  * MLP/run_ai_test.py ランダム値を入力値として予測を実行するコード

[<ページTOP>](#top)　[<目次>](#0)
<hr>


