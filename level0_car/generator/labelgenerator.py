# coding: utf-8
import numpy as np
class LabelGenerator():
    def get_label(self,sensors):
        '''
        args:
            sensors: [左センサー値,前センサー値,右センサー値]
        return:
            one hot valueのラベル
        '''

        if sensors[0] < 50: # 前方に空きが無い
            return [1,0,0,0] # STOP
        elif sensors[1] < 50: # 左に空きが無い
            return [0,0,0,1] # RIGHT
        elif sensors[2] < 50: # 右に空きが無い
            return [0,1,0,0] # LEFT
        else: # 全方向に空きがある
            return [0,0,1,0] # FOWARD
