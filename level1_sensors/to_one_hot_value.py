# coding: utf-8
import numpy as np
n_classes = 4 # クラス分類の総数
########################################
# ラベル番号をone_hot_valueに変換する
########################################
def get_one_hot_value(int_label):
    one_hot_value = np.zeros((1,n_classes))
    one_hot_value[np.arange(1),np.array([int_label])] = 1
    return one_hot_value

for i in range(n_classes):
    one_hot_value = get_one_hot_value(i)
    print("label:{} one_hot_value:{}".format(i,one_hot_value))
