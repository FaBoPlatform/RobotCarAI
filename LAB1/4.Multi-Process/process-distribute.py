# coding: utf-8
# プロセス分散
# pip install futures

import time
from concurrent import futures
import os
from multiprocessing import Manager
'''
ここはプロセスで実行される
SHARED_VARIABLE['SOMETHING1_READY']=True であるうちは実行を続ける
'''
def do_something1():
    tag='SOMETHING1'
    print("enter "+tag)
    SHARED_VARIABLE['SOMETHING1_READY']=True

    ####################
    # ループ実行
    ####################
    execute_time=0.0
    execute_clock_time=0.0
    count = 0
    while SHARED_VARIABLE['SOMETHING1_READY']:
        start_time,clock_time=time.time(),time.clock()
        SHARED_VARIABLE['SOMETHING1_VALUE'] += 1
        execute_time += time.time() - start_time
        execute_clock_time += time.clock() - clock_time
        count+=1
        print("Process-%s:%d Parent id:%d value:%s" % (tag,os.getpid(),os.getppid(),str(SHARED_VARIABLE['SOMETHING1_VALUE'])))
        time.sleep(0.1)
    print("Process-%s:%d Parent id:%d ave time:%.8f ave clock:%.8f" % (tag,os.getpid(),os.getppid(),execute_time/count,execute_clock_time/count))
    return

'''
ここはプロセスで実行される
SHARED_VARIABLE['SOMETHING2_READY']=True であるうちは実行を続ける
'''
def do_something2():
    tag='SOMETHING2'
    print("enter "+tag)
    SHARED_VARIABLE['SOMETHING2_READY']=True

    ####################
    # ループ実行
    ####################
    execute_time=0.0
    execute_clock_time=0.0
    count = 0
    while SHARED_VARIABLE['SOMETHING2_READY']:
        start_time,clock_time=time.time(),time.clock()
        SHARED_VARIABLE['SOMETHING2_VALUE'] = SHARED_VARIABLE['SOMETHING1_VALUE'] << 2
        execute_time += time.time() - start_time
        execute_clock_time += time.clock() - clock_time
        count+=1
        print("Process-%s:%d Parent id:%d value:%s" % (tag,os.getpid(),os.getppid(),str(SHARED_VARIABLE['SOMETHING2_VALUE'])))
        time.sleep(0.1)
    print("Process-%s:%d Parent id:%d ave time:%.8f ave clock:%.8f" % (tag,os.getpid(),os.getppid(),execute_time/count,execute_clock_time/count))
    return

'''
ここはプロセスで実行される
SHARED_VARIABLE['SOMETHING2_READY']=True であるうちは実行を続ける
'''
def do_stop():
    tag='STOP'

    ####################
    # ループ実行
    ####################
    start_time = time.time()
    RUNNING_SEC = 30
    time.sleep(RUNNING_SEC)
    SHARED_VARIABLE['SOMETHING1_READY']=False
    SHARED_VARIABLE['SOMETHING2_READY']=False
        
    return

'''
process pattern
'''
SHARED_VARIABLE=Manager().dict()
SHARED_VARIABLE['SOMETHING1_READY']=False
SHARED_VARIABLE['SOMETHING2_READY']=False
SHARED_VARIABLE['SOMETHING1_VALUE']=0
SHARED_VARIABLE['SOMETHING2_VALUE']=0

'''
プロセスによる実行関数の振り分け定義
'''
PROCESS_LIST=['do_something1','do_something2','do_stop']
def do_process(target):

    if target == 'do_something1':
        do_something1()
        return "end do_something1"
    if target == 'do_something2':
        do_something2()
        return "end do_something2"
    if target == 'do_stop':
        do_stop()
        return "end do_stop"

'''
メイン処理を行う部分
・メインスレッド（ここ）
・スレッド1(concurrent.futures)
・スレッド2(concurrent.futures)
・制御スレッド(concurrent.futures)
'''
def do_main():
    try:
        with futures.ProcessPoolExecutor(max_workers=len(PROCESS_LIST)) as executer:
            mappings = {executer.submit(do_process, pname): pname for pname in PROCESS_LIST}
            for i in futures.as_completed(mappings):
                target = mappings[i]
                result = i.result()
                print(result)

    except Exception as e:
        print 'error! executer failed.'
        print str(e)
    finally:
        print("executer end")

    return

do_main()

