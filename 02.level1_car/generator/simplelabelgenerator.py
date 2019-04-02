# coding: utf-8
import numpy as np
class SimpleLabelGenerator():
    def get_label(self,sensors):
        '''
        args:
            sensors: [左センサー値,前センサー値,右センサー値]
        return:
            one hot valueのラベル
        '''

        if sensors[1] < 20: # 前方に空きが無い
            return [1,0,0,0] # STOP
        elif sensors[0] < 20: # 左に空きが無い
            return [0,0,0,1] # RIGHT
        elif sensors[2] < 20: # 右に空きが無い
            return [0,1,0,0] # LEFT
        else: # 全方向に空きがある
            return [0,0,1,0] # FOWARD
