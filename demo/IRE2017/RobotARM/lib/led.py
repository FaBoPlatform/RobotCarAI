# coding: utf-8 
# Fabo #210 LED点灯サポートクラス
import FaBoGPIO_PCAL6408
import time
import sys
import threading

class LED():

    STOP_PATTERN = False
    def __init__(self):
        self.pcal6408 = FaBoGPIO_PCAL6408.PCAL6408()
        self.lock = threading.Lock()
        return

    '''
    STOP命令で解除可能なsleep
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
    指定したLED番号を点灯する
    targets: LED番号
    default: 0番目のLEDを点灯する
    '''
    def light(self, targets=None):
        #print('start light {}'.format(targets))
        default = 0
        with self.lock:
            if targets is None:
                self.pcal6408.setDigital(1<<default, 1)
            else:
                for target in targets:
                    self.pcal6408.setDigital(1<<target, 1)
        return

    '''
    LEDを全灯する
    '''
    def lightall(self):
        #print('start lightall')
        with self.lock:
            for i in range(8):
                self.pcal6408.setDigital(1<<i, 1)
        return
    
    '''
    LED番号0から7までを順番に点灯し、消灯する
    light0to7動作中はstop以外の他の機能はlock待ちにより動作しない
    他の機能を使うためには一度stopを実行するか、この処理が終わるまで待つこと
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
    他の機能を使うためには一度stopを実行すること
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
    指定したLED番号を点滅する
    targets: LED番号
    default: 0番目のLEDを点滅する
    blink動作中はstop以外の他の機能はlock待ちにより動作しない
    他の機能を使うためには一度stopを実行すること
    '''
    def blink(self, targets=None):
        #print('start blink {}'.format(targets))
        sleep_time = 0.0
        sleep_interval = 0.01
        default = 0
        with self.lock:
            while True:
                if self.STOP_PATTERN:
                    break
                if targets is None:
                    self.pcal6408.setDigital(1<<default, 1)
                else:
                    for target in targets:
                        self.pcal6408.setDigital(1<<target, 1)
                self.rem_sleep(0.1)

                if self.STOP_PATTERN:
                    break
                if targets is None:
                    self.pcal6408.setDigital(1<<default, 0)
                else:
                    for target in targets:
                        self.pcal6408.setDigital(1<<target, 0)
                self.rem_sleep(0.4)
        return

    '''
    指定したLED番号を消灯する
    targets: LED番号
    default: すべてのLEDを消灯する
    '''
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
    pattern:
    'light 0 1 2..': 指定したLED番号を点灯する
    'lightall': 全てのLEDを点灯する
    'light0to7': LEDを0から7まで順に点灯し、消灯する
    'lightline': 上一列を点滅させた後、下一列を点滅させることを繰り返し行う。stopで解除
    'blink 0 1 2..': 指定したLED番号を点滅する。stopで解除
    'stop 0 1 2..': 指定したLED番号を消灯する

    ex.
    'lightall'
    'stop 0 2 5 7'
    'stop'
    'light 0 7'
    '''
    def start(self,pattern='light0to7'):
        pattern = pattern.split(' ')
        #print('pattern {}'.format(pattern))
        self.STOP_PATTERN = False
        t=None
        '''
        LED点灯番号を引数として受け取らないコマンド
        light0to7,lightall,lightline
        LED点灯番号を引数として受け取るコマンド
        light,blink,stop
        '''
        targets = None
        if len(pattern) > 1:
            targets = []
            for i in range(len(pattern)-1):
                targets += [int(pattern[i+1])]
        if pattern[0] == 'light':
            t = threading.Thread(target=self.light,args=(targets,))
            t.start()
        elif pattern[0] == 'lightall':
            t = threading.Thread(target=self.lightall,args=())
            t.start()
        elif pattern[0] == 'light0to7':
            t = threading.Thread(target=self.light0to7,args=())
            t.start()
        elif pattern[0] == 'lightline':
            t = threading.Thread(target=self.lightline,args=())
            t.start()
        elif pattern[0] == 'blink':
            t = threading.Thread(target=self.blink,args=(targets,))
            t.start()
        elif pattern[0] == 'stop': # stop()を呼び出してもよい
            t = threading.Thread(target=self.stop,args=(targets,))
            t.start()

