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
    other_label = 100

    def __init__(self):
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
        FROZEN_MODEL_NAME="car_model.pb"
        MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/model"

        # AIモデル読み込み
        self.graph = self.load_graph(MODEL_DIR+"/"+FROZEN_MODEL_NAME)
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
        return self.other_label

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
        score: 予測結果に必要なスコア閾値
        '''

        # 予測結果をその他で初期化する
        prediction_index = self.other_label

        _output_y,_score = self.sess.run([self.output_y,self.score],feed_dict={self.input_x:[sensors]})

        max_index = np.argmax(_output_y[0])
        max_score = _score[0][max_index]

        # 予測結果の最大値のスコアと閾値を比較する
        if max_score >= score:
            # スコアが高い
            prediction_index = max_index
            prediction_score = max_score
            pass
        else:
            # スコアが低いのでその他にする
            prediction_index = self.other_label # その他
            #prediction_score = _score[0][prediction_index] # その他ラベルを持たなければ、取得できるスコアは存在しない

        return prediction_index
