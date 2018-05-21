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

# 设置log回滚,每个日志文件最大为100M,最多备份五个日志文件.
logFile = '/tmp/handshake.log'
Rthandler = RotatingFileHandler(logFile, maxBytes=100 * 1024 * 1024, backupCount=5)
Rthandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)

def handel_each_line(line, syn_dict):
    line_list = line.split()
    try:
        if re.search(r'http', line_list[4], re.IGNORECASE) and re.match(r'\[S\],', line_list[6], re.IGNORECASE):
            secIpPort = line_list[2]
            syn_dict[secIpPort] = line_list[0]
        elif re.match(r'\[\.\],', line_list[6], re.IGNORECASE) and re.match(r'1,', line_list[8]):
            secIpPort = line_list[2]
            if secIpPort in syn_dict:
                logging.error(secIpPort, syn_dict.pop(secIpPort), line_list[0])
    except KeyError:
        pass



def main():
    # 用于存储手包收件的dict
    syn_dict = dict()

    # tcpdump获取握手的数据包,分析并处理.
    p = subprocess.Popen('tcpdump "tcp[tcpflags] & (tcp-syn|tcp-ack) != 0"', shell=True, stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline()
        line = str(line.strip(), encoding='utf-8')
        if line:
            handel_each_line(line, syn_dict)

if __name__ == '__main__':
    main()
