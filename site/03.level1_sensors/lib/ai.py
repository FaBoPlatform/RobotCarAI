# coding: utf-8
# AI予測実行クラス

import time
import os
import numpy as np
import tensorflow as tf
import logging

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

class AI():

    sess = None
    learned_step = None # モデルの学習ステップ数
    OTHER_LABEL = 100

    def __init__(self,frozen_model_name=None):
        # グラフ初期化
        tf.reset_default_graph()

        ########################################
        # モデル読み込み
        ########################################
        '''
        AIモデルファイル名とディレクトリ
        カレントディレクトリが別の場所からの実行でも問題ないように、
        ディレクトリパスはこのファイルと同じディレクトリとして取得する
        '''
        MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/../model"
        if frozen_model_name is None:
            frozen_model_path=MODEL_DIR+"/car_model.pb"
        else:
            frozen_model_path=MODEL_DIR+"/"+frozen_model_name
            
        # AIモデル読み込み
        self.graph = self.load_graph(frozen_model_path)
        #self.graph_def = self.graph.as_graph_def()
        # AI入出力ノード取得
        self.input_x = self.graph.get_tensor_by_name('prefix/queue/dequeue_op:0')
        self.output_y= self.graph.get_tensor_by_name('prefix/neural_network_model/output_y:0')
        self.score = self.graph.get_tensor_by_name('prefix/neural_network_model/score:0')
        self.step = self.graph.get_tensor_by_name('prefix/step/step:0')

        self.sess = tf.Session(graph=self.graph)

        return

    def __del__(self):
        if self.sess is not None:
            self.sess.close()
        return

    def load_graph(self,frozen_graph_filename):
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

    def get_other_label(self):
        '''
        その他のラベル番号を返す
        '''
        return self.OTHER_LABEL

    def get_learned_step(self):
        '''
        モデルが保持する学習済みステップ数を取得する
        '''
        if self.learned_step is None:
            self.learned_step = self.sess.run(self.step)

        return self.learned_step

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

        max_index = np.argmax(_output_y[0])
        max_score = _score[0][max_index]

        # 予測結果の最大値のスコアと閾値を比較する
        if max_score >= score:
            # スコアが高い
            prediction_index = max_index
            prediction_score = max_score
        else:
            # スコアが低いのでその他にする
            prediction_index = self.OTHER_LABEL # その他
            #prediction_score = _score[0][prediction_index] # その他ラベルを持たなければ、取得できるスコアは存在しない

        return prediction_index

    def get_predictions(self,sensors,score=0):
        '''
        AI予測を実行する
        評価用に複数のデータセットで実行する
        args:
            sensors: [[左センサー値,前センサー値,右センサー値],[左センサー値,前センサー値,右センサー値],...]
            score: 予測結果に必要なスコア閾値。0.0-1.0
        return:
            prediction_indices: [予測結果のクラス番号,予測結果のクラス番号,...]
        '''

        _output_y,_score = self.sess.run([self.output_y,self.score],feed_dict={self.input_x:sensors})

        prediction_indices = []
        
        n_rows = len(sensors)
        for i in range(0,n_rows):
            max_index = np.argmax(_output_y[i])
            max_score = _score[i][max_index]

            # 予測結果の最大値のスコアと閾値を比較する
            if max_score >= score:
                # スコアが高い
                prediction_index = max_index
                prediction_score = max_score
            else:
                # スコアが低いのでその他にする
                prediction_index = self.OTHER_LABEL # その他
                #prediction_score = _score[0][prediction_index] # その他ラベルを持たなければ、取得できるスコアは存在しない
            prediction_indices += [prediction_index]

        return prediction_indices
    
