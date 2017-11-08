# coding: utf-8 
# Fabo #210 LED点灯サポートクラス
import FaBoGPIO_PCAL6408
import time
import sys
import threading

class LED():

    PATTERN = None
    STOP_PATTERN = False
    def __init__(self):
        self.pcal6408 = FaBoGPIO_PCAL6408.PCAL6408()
        self.lock = threading.Lock()
        return

    '''
    STOP命令でsleepを解除する
    '''
    def rem_sleep(self,sectime):
        sleep_time = 0.0
        sleep_interval = 0.01

        while sleep_time < sectime: # time.sleep(sectime) に停止フラグ検証を追加
            if self.STOP_PATTERN:
                break        
            time.sleep(sleep_interval)
            sleep_time += sleep_interval
        return

    '''
    light動作中は他の機能(light0to7,blink)はlock待ちにより動作しない
    途中で切り替えるには一度stopを実行後、他の機能を実行すること
    '''
    def light(self, target):
        #print('start light {}'.format(target))
        with self.lock:
            self.pcal6408.setDigital(1<<target, 1)
        return

    '''
    全灯する
    '''
    def lightall(self):
        #print('start lightall')
        with self.lock:
            for i in range(8):
                self.pcal6408.setDigital(1<<i, 1)
        return
    
    '''
    light0to7動作中は他の機能(light,blink)はlock待ちにより動作しない
    途中で切り替えるには一度stopを実行後、他の機能を実行すること
    '''
    def light0to7(self):
        #print('start light0to7')
        with self.lock:
            for i in range(8):
                if self.STOP_PATTERN:
                    break
                self.pcal6408.setDigital(1<<i, 1)
                self.rem_sleep(0.5)

            for i in range(8):
                if self.STOP_PATTERN:
                    break
                self.pcal6408.setDigital(1<<i, 0)
                self.rem_sleep(0.5)

        return

    '''
    上一列を点滅させた後、下一列を点滅させることを繰り返し行う
    '''
    def lightline(self):
        #print('start lightline')
        with self.lock:
            while True:
                if self.STOP_PATTERN:
                    break
                for i in range(4):
                    if self.STOP_PATTERN:
                        break
                    self.pcal6408.setDigital(1<<i, 1)
                    self.rem_sleep(0.01)
                    if self.STOP_PATTERN:
                        break
                    self.pcal6408.setDigital(1<<i, 0)
                    self.rem_sleep(0.01)

                self.rem_sleep(0.5)
                for i in range(4,8):
                    if self.STOP_PATTERN:
                        break
                    self.pcal6408.setDigital(1<<i, 1)
                    self.rem_sleep(0.01)
                    if self.STOP_PATTERN:
                        break
                    self.pcal6408.setDigital(1<<i, 0)
                    self.rem_sleep(0.01)

                self.rem_sleep(0.5)
        return
        
    '''
    blink動作中は他の機能(light,light0to7)はlock待ちにより動作しない
    途中で切り替えるには一度stopを実行後、他の機能を実行すること
    '''
    def blink(self, target):
        #print('start blink {}'.format(target))
        sleep_time = 0.0
        sleep_interval = 0.01
        with self.lock:
            while True:
                if self.STOP_PATTERN:
                    break
                self.pcal6408.setDigital(1<<target, 1)
                self.rem_sleep(0.1)

                if self.STOP_PATTERN:
                    break
                self.pcal6408.setDigital(1<<target, 0)
                self.rem_sleep(0.4)
        return

    def stop(self, targets=None):
        #print('start stop targets:{}'.format(targets))
        self.STOP_PATTERN = True
        with self.lock:
            if targets is None:
                self.pcal6408.setAllClear()
            else:
                for target in targets:
                    self.pcal6408.setDigital(1<<target, 0)
            self.STOP_PATTERN = False
        return
        

    '''
    pattern:'ligght0to7', 'blink', 'blink 0',.. 'blink 7'
    '''
    def start(self,pattern='light0to7'):
        self.PATTERN = pattern.split(' ')
        self.STOP_PATTERN = False
        t=None
        if self.PATTERN[0] == 'light':
            #print('pattern {}'.format(self.PATTERN))
            target = 7
            if len(self.PATTERN) == 1:
                target = 7
            else:
                target = int(self.PATTERN[1])
            t = threading.Thread(target=self.light,args=(target,))
            t.start()
        elif self.PATTERN[0] == 'lightall':
            #print('pattern {}'.format(self.PATTERN))
            t = threading.Thread(target=self.lightall,args=())
            t.start()
        elif self.PATTERN[0] == 'light0to7':
            #print('pattern {}'.format(self.PATTERN))
            t = threading.Thread(target=self.light0to7,args=())
            t.start()
        elif self.PATTERN[0] == 'lightline':
            #print('pattern {}'.format(self.PATTERN))
            t = threading.Thread(target=self.lightline,args=())
            t.start()
        elif self.PATTERN[0] == 'blink':
            #print('pattern {}'.format(self.PATTERN))
            target = 7
            if len(self.PATTERN) == 1:
                target = 7
            else:
                target = int(self.PATTERN[1])
            t = threading.Thread(target=self.blink,args=(target,))
            t.start()
        elif self.PATTERN[0] == 'stop': # stop()を呼び出してもよい
            #print('pattern {}'.format(self.PATTERN))
            targets = None
            if len(self.PATTERN) == 1:
                targets = None
            else:
                targets = []
                for i in range(len(self.PATTERN)-1):
                    targets += [int(self.PATTERN[i+1])]

            t = threading.Thread(target=self.stop,args=(targets,))
            t.start()

