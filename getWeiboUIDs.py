# -*- coding: cp936 -*-
import requests
import json
import os
import time
import sys
import re
import datetime
from collections import Iterable
from collections import defaultdict

WEIBO_UIDS= []

def preHandleWebUrls(filename):
    start = time.clock()
    f = open(filename,'r')
    fc = f.read()
    #print(fc)
    counts = 0
    contents = fc.split("\n")
    f.close()
    exampleLenths = len('https://m.weibo.cn/1231317854/4303609405582510')
    urls = []
    lens = len(contents)
    for index in range(lens):
        line = contents[index]        
        if((len(line) == exampleLenths) and (line.find('m.weibo.cn')>0)):
            #https://m.weibo.cn/1231317854/4303609405582510 
            weibo_UID  = line.replace("//","/").split("/")[2]
            print(weibo_UID)
            if weibo_UID not in WEIBO_UIDS:
                WEIBO_UIDS.append(weibo_UID)
                counts = counts + 1
        else:
            continue
    end = time.clock()
    times = (end - start)
    print ('处理文件：%s  有%s条VideoUrls'%(filename,lens)) + ('提取[  %s ]条'%counts) + (" 用时：%s"% times)
    print('==============================================')

def main():
    fnlist = os.listdir('./')
    for x in fnlist:
        if x.endswith('.txt') and \
           len(x)<len('handledwellUrls[2018-11-23 13 13 10].txt') and \
           (x != 'ErrorInformations.txt') and \
           (x != 'handledwell_UIDs.txt'):
            print x
            preHandleWebUrls('./'+ x)
    if len(WEIBO_UIDS)>0:
            sf = './handledwell_UIDs.txt'
            with open(sf,'w+') as savefile:
                savefile.write("\n".join(WEIBO_UIDS))
            savefile.close() 
    
        

if __name__ == '__main__':
    main()
