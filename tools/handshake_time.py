#!/usr/bin/evn python
# -*- coding: utf-8 -*-
# Time        : 18-5-14 下午2:04
# Site        : 
# File        : handshake_time2.py 
# Software    : PyCharm
# Author      : zhi 
# Mail        : 937042882@qq.com

import re
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from queue import Queue
from threading import Thread
import time

# 配置ip
ip_com = re.compile('((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)')

# 设置log回滚,每个日志文件最大为100M,最多备份五个日志文件.
logFile = '/tmp/handshake.log'
Rthandler = RotatingFileHandler(logFile, maxBytes=100 * 1024 * 1024, backupCount=5)

formatter = logging.Formatter('%(message)s')
Rthandler.setFormatter(formatter)

logger = logging.getLogger('')
logger.addHandler(Rthandler)
logger.setLevel(logging.DEBUG)

def timeStamps(strTime):
    # 将'11:26:43.974019'的时间字符串转化为'1970-01-01 11:26:43.974019'的时间戳
    timeString, microSeconds = strTime.split('.')
    timeStruct = time.strptime('1970-01-01 {}'.format(timeString), '%Y-%m-%d %X')
    timeStamps = time.mktime(timeStruct) + float(microSeconds)/1000000
    return timeStamps

def calTime(startTime, endTime):
    # 返回tcpdump获取的时间格式的间隔
    return timeStamps(endTime) - timeStamps(startTime)

def handel_each_line(line, syn_dict, queue):
    line_list = line.split()
    try:
        if re.search(r'http', line_list[4], re.IGNORECASE) and re.match(r'\[S\],', line_list[6], re.IGNORECASE):
            secIpPort = line_list[2]
            syn_dict[secIpPort] = line_list[0]
        elif re.match(r'\[\.\],', line_list[6], re.IGNORECASE) and re.match(r'1,', line_list[8]):
            secIpPort = line_list[2]
            ip = ip_com.match(secIpPort)
            if secIpPort in syn_dict:
                startTime = syn_dict.pop(secIpPort)
                endTime = line_list[0]
                if ip:
                    queue.put((ip.group(), calTime(startTime, endTime)))
    except KeyError:
        pass

def getTime(queue):
    # 用于存储手包收件的dict
    syn_dict = dict()

    # tcpdump获取握手的数据包,分析并处理.
    p = subprocess.Popen('tcpdump "tcp[tcpflags] & (tcp-syn|tcp-ack) != 0"', shell=True, stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline()
        line = str(line.strip(), encoding='utf-8')
        if line:
            handel_each_line(line, syn_dict, queue)

def writeLog(queue):
    while True:
        handShakeTime = queue.get()
        if handShakeTime:
            logger.info(handShakeTime)

def main():
    queue = Queue()
    product = Thread(target=getTime, args=(queue,))
    consumer = Thread(target=writeLog, args=(queue,))

    product.start()
    consumer.start()


if __name__ == '__main__':
    main()