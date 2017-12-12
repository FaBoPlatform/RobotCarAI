# coding: utf-8
# AI予測実行クラス

import time
import os
import numpy as np
import tensorflow as tf
import cv2
import logging

# ログ設定
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] time:%(created).8f pid:%(process)d pn:%(processName)-10s tid:%(thread)d tn:%(threadName)-10s fn:%(funcName)-10s %(message)s',
)

class SaveConfig():
    ########################################
    # 結果保存
    ########################################
    # TRUE_LABEL = None # Noneならprediction結果をそのまま保存する
    # TRUE_LABEL = ラベル番号 # prediction結果が指定ラベル番号でなかった時に保存する
    # 画像ファイル名: PREFIX_PRED_SCORE_NUMBER
    CAPTURE_DIR = os.path.abspath(os.path.dirname(__file__))+"/../capture"
    PREFIX = None
    TRUE_LABEL = None # prediction結果が指定ラベル番号でなかった時に保存する
    SAVE_PREDICTION = True # True:保存する False:保存しない
    THINK_SCORE = False # 指定スコア未満での失敗を保存する

    def __init__(self,prefix,label=None,save=True,score=False):
        '''
        prefix:ファイル名の接頭語
        save:Trueなら予測結果の画像を保存する。Falseなら保存しない。
        label=0,score=False: 不正解を全て保存する
        label=0,score=True: 不正解を全て保存し、正解であってもスコア未満は保存する
        label=None,score=False: 全ての結果を保存する
        label=None,score=True: 全ての結果のうち、スコア未満のみ保存する
        '''
        self.PREFIX = prefix
        self.TRUE_LABEL = label
        self.SAVE_PREDICTION = save
        self.THINK_SCORE = score
        return

class AI():

    sess = None
    other_label = 0 # その他と判断するラベル番号
    learned_step = None # モデルの学習ステップ数
    save_config = None # 画像保存設定
    number = 0 # 保存するファイル番号
    vid = None
    sess = None

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
        FROZEN_MODEL_NAME="cnn_model_murayama_1570.pb"
        MODEL_DIR=os.path.abspath(os.path.dirname(__file__))+"/../model"

        # AIモデル読み込み
        self.graph = self.load_graph(MODEL_DIR+"/"+FROZEN_MODEL_NAME)
        #self.graph_def = self.graph.as_graph_def()
        # AI入出力ノード取得
        self.input_x = self.graph.get_tensor_by_name('prefix/input_x:0')
        self.output_y = self.graph.get_tensor_by_name('prefix/output_y:0')
        self.keep_prob = self.graph.get_tensor_by_name('prefix/Placeholder:0')
        self.score = self.graph.get_tensor_by_name('prefix/score:0')
        self.step = self.graph.get_tensor_by_name('prefix/step/step:0')

        self.sess = tf.Session(graph=self.graph)

        return

    def __del__(self):
        if self.vid is not None:
            self.vid.release()
        if self.sess is not None:
            self.sess.close()
        return

    def init_webcam(self):
        '''
        OpenCVカメラ準備
        カメラ準備が出来たらTrue、失敗したらFalseを返す
        '''
        import platform
        vid = None
        if platform.machine() == 'aarch64':
            vid = cv2.VideoCapture(1) # WebCam Jetson TX2 /dev/video1
        else: # armv7l
            vid = cv2.VideoCapture(0) # WebCam Raspberry Pi3 /dev/video0
        print(vid.isOpened())
        if not vid.isOpened():
            # カメラオープン失敗は復旧できないので終了にする
            raise IOError(("Couldn't open video file or webcam. If you're "
                           "trying to open a webcam, make sure you video_path is an integer!"))

        # カメラ画像サイズ（AIモデルはこのサイズを入力値に取る）
        image_height = 120
        image_width = 160
        image_depth = 3    # BGRの3色

        # AI入力データサイズ
        self.data_cols=image_height * image_width * image_depth # 120*160*3

        vidw = None
        vidh = None
        fps = None
        fourcc = None
        cv_version = cv2.__version__.split(".")
        if cv_version[0] == '2':
            # OpenCV 2.4
            vidw = vid.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, image_width)
            vidh = vid.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, image_height)
            fps = vid.get(cv2.cv.CV_CAP_PROP_FPS)
            fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
        else:
            # OpenCV 3.2
            vidw = vid.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
            vidh = vid.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
            fps = vid.get(cv2.CAP_PROP_FPS)
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

        self.vid = vid
        return

    def webcam_capture(self):
        '''
        webcam画像を取得する
        '''
        retval, self.cv_bgr = self.vid.read()
        if not retval:
            print('Done.')
            return False
        return True

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

    def get_prediction(self,score=0,cv_bgr=None):
        '''
        AI予測を実行する
        score: 予測結果に必要なスコア閾値
        '''

        # 予測結果をその他で初期化する
        prediction_index = self.other_label

        if not cv_bgr is None:
            self.cv_bgr = cv_bgr
        elif self.webcam_capture():
            pass
        else:
            return

        image_data = self.cv_bgr.reshape(1,self.data_cols)
        _output_y,_score = self.sess.run([self.output_y,self.score],feed_dict={self.input_x:image_data,self.keep_prob:1.0})

        max_index = np.argmax(_score[0])
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

        # 画像保存設定がある
        if not self.save_config is None:
            if self.save_config.SAVE_PREDICTION:
                # 保存設定になっている
                # ディレクトリを作成する
                SAVE_DIR = self.save_config.CAPTURE_DIR+"/"+str(max_index)
                if not os.path.exists(SAVE_DIR):
                    os.makedirs(SAVE_DIR)

                if self.save_config.TRUE_LABEL is None:
                    # prediction結果をそのまま保存する
                    if self.save_config.THINK_SCORE:
                        if max_score < score:
                            # スコア未満を保存する
                            cv2.imwrite(SAVE_DIR+"/"+self.save_config.PREFIX+"_"+str(max_index)+"_"+str(max_score)+"_"+str(self.number)+".png",self.cv_bgr)
                            self.number+=1
                        else:
                            # スコア以上なので保存しない
                            pass
                    else:
                        # スコア比較せずに、prediction結果をそのまま保存する
                        cv2.imwrite(SAVE_DIR+"/"+self.save_config.PREFIX+"_"+str(max_index)+"_"+str(max_score)+"_"+str(self.number)+".png",self.cv_bgr)
                        self.number+=1
                else:
                    # 指定ラベル以外の結果を保存する
                    if not max_index == self.save_config.TRUE_LABEL:
                        cv2.imwrite(SAVE_DIR+"/"+self.save_config.PREFIX+"_"+str(max_index)+"_"+str(max_score)+"_"+str(self.number)+".png",self.cv_bgr)
                        self.number+=1
                    else:
                        if self.save_config.THINK_SCORE:
                            # 指定ラベルであってもスコア未満なら保存する
                            if max_score < score:
                                cv2.imwrite(SAVE_DIR+"/"+self.save_config.PREFIX+"_"+str(max_index)+"_"+str(max_score)+"_"+str(self.number)+".png",self.cv_bgr)
                                self.number+=1
                            else:
                                # スコア以上なので保存しない
                                pass
                        else:
                            # スコアを考慮しないので正解となり保存しない
                            pass




        return prediction_index

    def set_save_config(self,config=SaveConfig(prefix='capture')):
        self.save_config = config
        return



