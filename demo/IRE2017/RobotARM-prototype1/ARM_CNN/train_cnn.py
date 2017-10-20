# -*- coding: utf-8 -*-
# ステップ記録
# ミニバッチに入るクラス分布を調整
import os
import time
import tensorflow as tf

import cv2
import numpy as np
import sys

MODEL_DIR="./model"
SUMMARY_LOG_DIR="./log"
TRAIN_DATA_DIR="./train_data"
TEST_DATA_DIR="./test_data"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

target_step = 200
#n_classes = 5 # [アレルケア][紙コップ][ペットボトル][手][その他]
n_classes = 5
class_batch_size = 10 # ミニバッチデータに入れる各クラスデータ件数
class_max_read = 100000 # 特定のクラスだけが特別に多くのバリエーションがあることを制限する。多くのデータがある状態なら制限の必要はない
view_step = 1 # 表示するステップ間隔
batch_size = class_batch_size*n_classes # バッチサイズは10〜100前後に
#label_bytes = 1 # 0-3
label_bytes = 2 # 4-7
image_width = 160
image_height = 120
image_depth = 3
image_bytes = image_width*image_height*image_depth #
data_cols = image_bytes
record_bytes=label_bytes + data_cols # byte. label_bytes + image_bytes
batch_data_bytes=batch_size*record_bytes

x = tf.placeholder('int32', [None, data_cols], name='input_x')
y = tf.placeholder('int32', name='label_y')

conv1_width=5
conv1_height=5
conv1_depth=image_depth
conv1_outputs=32
conv2_width=5
conv2_height=5
conv2_outputs=64

fully1_width=image_width
fully1_height=image_height
fully1_inputs=4
fully1_outputs=256 # 適当な値


########################################
# RGBに変換する
########################################
def toRGB(cv_bgr):
    BGRflags = [flag for flag in dir(cv2) if flag.startswith('COLOR_BGR') ]
    cv_rgb = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2RGB)
    return cv_rgb

########################################
# ラベル番号をone_hot_valueに変換する
########################################
def toONEHOT(int_label):
    one_hot_value = np.zeros((1,n_classes))
    one_hot_value[np.arange(1),np.array([int_label])] = 1
    return one_hot_value

'''
学習データ取得
学習データはラベル番号のディレクトリ以下に画像ファイルとして保存されている
'''
def read_data_files(DATA_DIR):
    train_data = []

    # OpenCV imageFormat is either 1 or 0 or -1
    #1 for loading as RGB image (strips alfa component of RGBA file)
    #0 for loading as grayscale image
    #-1 for loading as is (includes alfa component of RGBA file)
    imageFormat=1
    total_counter=0 # ディレクトリから読み込んだファイル総数
    
    # ラベルディレクトリは0から連番なのでforループで回すが、ラベルディレクトリ以下にある画像ファイル名に規則性は無いためファイル検索で取得する
    #train_label_dirs = [os.path.join(DATA_DIR, '%d' % i) for i in range(n_classes)]
    for int_label in range(n_classes):
        label_data = []
        label = str(int_label)
        if not os.path.exists(os.path.join(DATA_DIR,label)):
            raise ValueError('Failed to label dir: ' + label)
        
        path=os.path.join(DATA_DIR, label)
        file_names = sorted(os.listdir(path))
        counter = 0
        for file_name in file_names:
            sys.stdout.write("%s:%s" % (label,file_name))
            sys.stdout.flush()
            if file_name.endswith(".jpeg"):
                pass
            elif file_name.endswith(".jpg"):
                pass
            elif file_name.endswith(".png"):
                pass
            else:
                sys.stdout.write(" - ng \n")
                sys.stdout.flush()
                continue
            if counter >= class_max_read:
                sys.stdout.write(" - skip \n")
                sys.stdout.flush()
                continue
            start_time = time.time()
            cv_bgr = cv2.imread(os.path.join(path, file_name), imageFormat)
            ########################################
            # ラベル番号をone_hot_valueに変換する
            ########################################
            one_hot_value = toONEHOT(int_label)


            train_row = np.append(cv_bgr.reshape(1,data_cols),one_hot_value)
            label_data += [list(train_row)]
            end_time = time.time()
            sys.stdout.write(" - ok")
            sys.stdout.write(" time:%.8f\n" % (end_time - start_time))
            sys.stdout.flush()
            counter+=1
            
        train_data += [np.array(label_data)]
        total_counter += counter

    print("load files:{}".format(total_counter))
    return np.array(train_data)

class_train_data = read_data_files(TRAIN_DATA_DIR)
class_test_data = read_data_files(TEST_DATA_DIR)


# クラス毎のデータ位置を初期化
CLASS_TRAIN_START_INDEX=[0]*n_classes
CLASS_TRAIN_END_INDEX=[0]*n_classes # ダミー
CLASS_TRAIN_INDEX_I=[0]*n_classes
CLASS_TRAIN_ROWS=[0]*n_classes # ダミー
TOTAL_TRAIN_ROWS=0 # ダミー
for i in range(n_classes):
    CLASS_TRAIN_ROWS[i]=len(class_train_data[i])
    TOTAL_TRAIN_ROWS+=CLASS_TRAIN_ROWS[i]
#
CLASS_DATA_COLS=len(class_train_data[0][0])
def next_class_train_data(int_label,remain_batch_size):
    global class_train_data
    global CLASS_TRAIN_START_INDEX
    global CLASS_TRAIN_END_INDEX
    global CLASS_TRAIN_INDEX_I
    global CLASS_TRAIN_ROWS
    global CLASS_DATA_COLS
    
    get_batch_size=remain_batch_size
    if get_batch_size > CLASS_TRAIN_ROWS[int_label]:
        get_batch_size = CLASS_TRAIN_ROWS[int_label]

    class_data = np.empty((0,CLASS_DATA_COLS), int)
    while remain_batch_size>0:
        CLASS_TRAIN_START_INDEX[int_label]=CLASS_TRAIN_INDEX_I[int_label]*get_batch_size
        CLASS_TRAIN_END_INDEX[int_label]=CLASS_TRAIN_START_INDEX[int_label] + get_batch_size
        if CLASS_TRAIN_ROWS[int_label] <= CLASS_TRAIN_START_INDEX[int_label]:
            CLASS_TRAIN_START_INDEX[int_label]=0
            CLASS_TRAIN_END_INDEX[int_label]=CLASS_TRAIN_START_INDEX[int_label] + get_batch_size
            CLASS_TRAIN_INDEX_I[int_label]=0
            
        if CLASS_TRAIN_ROWS[int_label] < CLASS_TRAIN_END_INDEX[int_label]:
            CLASS_TRAIN_END_INDEX[int_label]=CLASS_TRAIN_ROWS[int_label]

        if CLASS_TRAIN_INDEX_I[int_label] == 0:
            np.random.shuffle(class_train_data[int_label]) # データをシャッフルする

        class_data = np.append(class_data,class_train_data[int_label][CLASS_TRAIN_START_INDEX[int_label]:CLASS_TRAIN_END_INDEX[int_label]],axis=0)
        remain_batch_size -= len(class_data)
        if remain_batch_size < get_batch_size:
            get_batch_size = remain_batch_size
            
        CLASS_TRAIN_INDEX_I[int_label]+=1

    return class_data

#

# クラス毎のデータ位置を初期化
CLASS_TEST_START_INDEX=[0]*n_classes
CLASS_TEST_END_INDEX=[0]*n_classes # ダミー
CLASS_TEST_INDEX_I=[0]*n_classes
CLASS_TEST_ROWS=[0]*n_classes # ダミー
TOTAL_TEST_ROWS=0 # ダミー
for i in range(n_classes):
    CLASS_TEST_ROWS[i]=len(class_test_data[i])
    TOTAL_TEST_ROWS+=CLASS_TEST_ROWS[i]
#
def next_class_test_data(int_label,remain_batch_size):
    global class_test_data
    global CLASS_TEST_START_INDEX
    global CLASS_TEST_END_INDEX
    global CLASS_TEST_INDEX_I
    global CLASS_TEST_ROWS
    global CLASS_DATA_COLS
    
    get_batch_size=remain_batch_size
    if get_batch_size > CLASS_TEST_ROWS[int_label]:
        get_batch_size = CLASS_TEST_ROWS[int_label]

    class_data = np.empty((0,CLASS_DATA_COLS), int)
    while remain_batch_size>0:
        CLASS_TEST_START_INDEX[int_label]=CLASS_TEST_INDEX_I[int_label]*get_batch_size
        CLASS_TEST_END_INDEX[int_label]=CLASS_TEST_START_INDEX[int_label] + get_batch_size
        if CLASS_TEST_ROWS[int_label] <= CLASS_TEST_START_INDEX[int_label]:
            CLASS_TEST_START_INDEX[int_label]=0
            CLASS_TEST_END_INDEX[int_label]=CLASS_TEST_START_INDEX[int_label] + get_batch_size
            CLASS_TEST_INDEX_I[int_label]=0
        if CLASS_TEST_ROWS[int_label] < CLASS_TEST_END_INDEX[int_label]:
            CLASS_TEST_END_INDEX[int_label]=CLASS_TEST_ROWS[int_label]

        if CLASS_TEST_INDEX_I[int_label] == 0:
            np.random.shuffle(class_test_data[int_label]) # データをシャッフルする

        class_data = np.append(class_data,class_test_data[int_label][CLASS_TEST_START_INDEX[int_label]:CLASS_TEST_END_INDEX[int_label]],axis=0)
        remain_batch_size -= len(class_data)
        if remain_batch_size < get_batch_size:
            get_batch_size = remain_batch_size
            
        CLASS_TEST_INDEX_I[int_label]+=1

    return class_data

#


# 各クラスから均等に学習データを取得する
def next_train_data():
    global CLASS_DATA_COLS
    train_data = np.empty((0,CLASS_DATA_COLS), int)
    
    for i in range(n_classes):
        train_data = np.append(train_data,next_class_train_data(i,class_batch_size),axis=0)

    np.random.shuffle(train_data) # データをシャッフルする

    batch_data = train_data[:,0:data_cols]
    batch_target = train_data[:,data_cols:]

    return batch_data, batch_target

# 各クラスから均等に学習データを取得する
def next_test_data():
    global CLASS_DATA_COLS
    test_data = np.empty((0,CLASS_DATA_COLS), int)
    
    for i in range(n_classes):
        test_data = np.append(test_data,next_class_test_data(i,class_batch_size),axis=0)

    np.random.shuffle(test_data) # データをシャッフルする

    batch_data = test_data[:,0:data_cols]
    batch_target = test_data[:,data_cols:]

    return batch_data, batch_target
#







# dropout用
keep_rate = 0.8
keep_prob = tf.placeholder(tf.float32)

# VGGの固定値
def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1,1,1,1], padding='SAME')

# VGGの固定値
def maxpool2d(x):
    return tf.nn.max_pool(x, ksize=[1,2,2,1],
                          strides=[1,2,2,1], padding='SAME')

# 初期値をランダムにする関数
def weight_variable_conv(shape):
    n = shape[0]*shape[1]*shape[2]*shape[3]
    stddev = tf.sqrt(2.0/n)
    initial=tf.truncated_normal(shape, stddev=stddev)
    return tf.Variable(initial)

def bias_variable_conv(shape):
    initial = tf.constant(0.0, shape=shape)
    return tf.Variable(initial)

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def convolutional_neural_network(data):
    weights = {'W_conv1':weight_variable_conv([conv1_width,conv1_height,conv1_depth,conv1_outputs]),
               'W_conv2':weight_variable_conv([conv2_width,conv2_height,conv1_outputs,conv2_outputs]),
               'W_fc':weight_variable([fully1_width*fully1_height*fully1_inputs,fully1_outputs]),
               'out':weight_variable([fully1_outputs, n_classes])}

    biases = {'b_conv1':bias_variable_conv([conv1_outputs]),
              'b_conv2':bias_variable_conv([conv2_outputs]),
              'b_fc':bias_variable([fully1_outputs]),
              'out':bias_variable([n_classes])}

    data = tf.reshape(data, shape=[-1, image_width, image_height, image_depth])

    # 入力画像はint[]型にして、reluはfloat型なのでtf.cast()でtf.float32型に変換する
    conv1 = tf.nn.relu(conv2d(tf.cast(data,tf.float32), weights['W_conv1']) + biases['b_conv1'])
    conv1 = maxpool2d(conv1)

    conv2 = tf.nn.relu(conv2d(conv1, weights['W_conv2']) + biases['b_conv2'])
    conv2 = maxpool2d(conv2)

    fc = tf.reshape(conv2,[-1, fully1_width*fully1_height*fully1_inputs])
    fc = tf.nn.relu(tf.matmul(fc, weights['W_fc'])+biases['b_fc'])
    fc = tf.nn.dropout(fc, keep_rate)

    prediction = tf.add(tf.matmul(fc, weights['out']), biases['out'], name='output_y')

    return prediction

def train_neural_network(x):

    global saver
    
    with tf.variable_scope("step"):
        placeholder_step = tf.placeholder(tf.int32, name='input_step') # step値入力用
        variable_step = tf.Variable(initial_value=0, trainable=False, name="step") # step記録用
        step_op = variable_step.assign(placeholder_step)

    
    prediction = convolutional_neural_network(x)
    losses = tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y)
    loss_op = tf.reduce_mean(losses, name='loss_op')
    tf.summary.scalar('loss', loss_op)

    train_op = tf.train.AdamOptimizer(0.0001).minimize(loss_op,name='train_op')

    correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct, 'float'), name='accuracy')
    tf.summary.scalar('accuracy', accuracy)

    
    ########################################
    # tesnroboeard項目を用意する
    ########################################
    with tf.variable_scope('extra_log'):
        placeholder_total_loss = tf.placeholder(tf.float32, name='input_total_loss') # total_loss値入力用。float型
        variable_total_loss = tf.Variable(initial_value=0., trainable=False, name="total_loss") # total_loss記録用
        total_loss_op = variable_total_loss.assign(placeholder_total_loss)
        tf.summary.scalar('total_loss', variable_total_loss) # total_lossを追加

        placeholder_ave_accuracy = tf.placeholder(tf.float32, name='input_ave_accuracy') # ave_accuracy値入力用。float型
        variable_ave_accuracy = tf.Variable(initial_value=0., trainable=False, name="ave_accuracy") # ave_accuracy記録用
        ave_accuracy_op = variable_ave_accuracy.assign(placeholder_ave_accuracy)
        tf.summary.scalar('ave_accuracy', variable_ave_accuracy) # ave_accuracyを追加


    summary_op = tf.summary.merge_all()

    
    saver = tf.train.Saver(max_to_keep=100)
    start_time, start_clock = time.time(), time.clock()

    
    with tf.Session() as sess:
        ckpt = tf.train.get_checkpoint_state(MODEL_DIR)
        if ckpt:
            # checkpointファイルから最後に保存したモデルへのパスを取得する
            last_model = ckpt.model_checkpoint_path
            print("load {0}".format(last_model))
            # 学習済みモデルを読み込む
            saver.restore(sess, last_model)
            LOAD_MODEL = True
        else:
            print("initialization")
            # 初期化処理
            init_op = tf.global_variables_initializer()
            sess.run(init_op)


        max_batch_step = int(TOTAL_TRAIN_ROWS/batch_size)
        total_loss = 0
        ave_accuracy = 0
        step = 0 # 最後にstep数をモデルに記録するために変数を用意しておく
        writer = None

        # step取得
        _step = sess.run(variable_step)
        print("learned step:{}".format(_step))
        
        for step in range(_step+1, target_step+1):
            # view_step*100 step毎にログを新しくする
            if step % view_step*10000 == 1:
                writer = tf.summary.FileWriter(SUMMARY_LOG_DIR, sess.graph)        

            step_loss = 0
            for _i in range(max_batch_step):
                train_x, train_y = next_train_data()
                _train_op, batch_loss,ac = sess.run([train_op,loss_op,accuracy], feed_dict={x: train_x, y: train_y})
                step_loss += batch_loss
                ave_accuracy+=ac
            total_loss += step_loss

            if step % view_step == 0: # view_step毎に表示する
                s = sess.run(step_op, feed_dict={placeholder_step:step}) # ステップ数を保存する
                ave_accuracy = ave_accuracy/(view_step*max_batch_step)

                # tensorboardログに出力する
                sess.run([total_loss_op,ave_accuracy_op],
                         feed_dict={placeholder_total_loss:total_loss,
                                    placeholder_ave_accuracy:ave_accuracy})
                    
                w_summary = sess.run(summary_op, feed_dict={x: train_x, y: train_y}) # ログ値生成
                # 途中再開でログ書き込み先ファイルが分からないときはログ書き込み先を作る
                if writer is None:
                    writer = tf.summary.FileWriter(SUMMARY_LOG_DIR, sess.graph)        
                writer.add_summary(w_summary, step) # ログ出力
                
                print("step:%d ave_accuracy:%.8f total_loss:%.8f time:%.8f clock:%.8f" % (step,ave_accuracy,total_loss,time.time()-start_time,time.clock()-start_clock))
                total_loss = 0
                ave_accuracy = 0

            # view_step step毎にsaveする
            if step % view_step*1000 == 0:
                saver.save(sess, MODEL_DIR + '/model-'+str(step)+'.ckpt')


        train_x, train_y = next_train_data() # 精度評価のため全件取得する
        test_x, test_y = next_test_data() # 精度評価のため全件取得する
        print('Train accuracy:',accuracy.eval({x:train_x, y:train_y}))
        print('Test accuracy:',accuracy.eval({x:test_x, y:test_y}))


        sess.run(step_op, feed_dict={placeholder_step:step}) # ステップ数を保存する
        saver.save(sess, MODEL_DIR + '/model-'+str(step)+'.ckpt')

train_neural_network(x)
