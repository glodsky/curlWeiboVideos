# -*- coding: cp936 -*-
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import requests
import json
import os
import time
import sys
import re
import datetime
from collections import Iterable
from collections import defaultdict

g_dir = r'./video'


def down_video(videodicts):
    global g_dir
    count = 0
    for (key,value) in videodicts.items():
        start = time.clock()
        shortname = ""
        if (len(key)>20):
            shortname = key[0:20] + "......"
        else:
            shortname = key
        count = count + 1
        print('Downloading...['+ str(count) + ']: ' + shortname)
        start = time.clock()
        response = requests.get(value)
        if response.status_code == 200:
            # 过滤
            key0 = key.replace('\n','')
            key1 = key0.replace('/','')
            key2 = key1.replace(':','')
            key3 = key2.replace('\\','')
            key4 = key3.replace('?','')
            key5 = key4.replace('%','') 
            fname =validateFileName(key5)
            stime = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            print(stime + " Downloading... : %s" % shortname)
            fn = g_dir + r'/%s.mp4'% fname
            with open( fn , 'wb') as f:                
                # 以二进制写入到本地
                f.write(response.content)
                f.close()
                end = time.clock()
                times = (end - start)
                etime = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
                print(etime + " Download Over   : %s" % shortname)
                print(" 耗 时       ：%s秒"% times)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")


def validateFileName(sname):
    ##    \/:*?"<>|
    ##  \/: 路径  *? 通配符  " 文件路径  <> 重定向  | 管道
    good = re.sub('[\/:*?"<>|]','_',sname)
    good2 = good.strip()   
    return good2

def getOneVideo(url,save_to_path='./'):
    browser = webdriver.Chrome()
    browser.get(url)
    shortname = ""
    try:
        div_wbtext = browser.find_element_by_class_name("weibo-text")
    except NoSuchElementException as msg:
        strmsg = url+"\ntarget: find_element_by_class_name(\"weibo-text\")\nError: "+u"查找元素异常%s"%msg              
        print(strmsg)
        browser.close()
        return
    else:# 处理过滤wbtext中的异常字符乱码等
        videoname = div_wbtext.text
        print(videoname)
        vn = videoname.strip('\n')
        videoname3 = validateFileName(vn)
        if(len(videoname3)>30): #文件名短名化处理
            shortname = videoname3[0:30] + "..."
        else:
            shortname = videoname3
            
        try:
            btnplayer = browser.find_element_by_xpath("//button[@class='mwbv-play-button']")
        except NoSuchElementException as msg:
            print(url+"\ntarget: //button[@class='mwbv-play-button']\nError: "+u"查找元素异常%s"%msg)
            browser.close()
            return   
        else:# 获取视频源链
            btnplayer.click() #必须模拟点击，weibo的js才会解析可用的ssig                 
            video = browser.find_element_by_xpath("//video")
            videoUrls = video.get_attribute("src") 
            if(len(videoUrls)<=0):
                print( "Warning!: 获取视频src失败!:\n   " + videoname3 + "\n   " + url + "\n" )
            # 下载视频文件
            start = time.clock()
            stime = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            print(stime + " Downloading... : %s" % shortname)
            fn = save_to_path + r'%s.mp4'% videoname3
            response = requests.get(videoUrls)
            if response.status_code == 200:
                with open( fn , 'wb') as f:                
                    # 以二进制写入到本地
                    f.write(response.content)
                    f.close()
                    end = time.clock()
                    times = (end - start)
                    etime = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
                    print(etime + " Download Over   : %s" % shortname)
                    print(" 耗 时       ：%s秒"% times)
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
                    
                    
            
def watchOneVideo(url):
    browser = webdriver.Chrome()
    browser.get(url) 
   #element = driver.find_element_by_id("passwd-id")
   #element = driver.find_element_by_name("passwd")
    btnplayer = browser.find_element_by_xpath("//button[@class='mwbv-play-button']")
    btnplayer.click()
   # print(browser.page_source)
   # wait = WebDriverWait(browser, 5)
   # browser.implicitly_wait(10) 
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
    
def preHandleWebUrls(filename):
    start = time.clock()
    f = open(filename,'r')
    fc = f.read()
    #print(fc)
    print("===\n")
    counts = 0
    contents = fc.split("\n")
    f.close()
    exampleLenths = len('https://m.weibo.cn/1231317854/4303609405582510')
    urls = []
    lens = len(contents)
    for index in range(lens):
        line = contents[index]        
        if((len(line) == exampleLenths) and (line.find('m.weibo.cn')>0)):
            #https://m.weibo.cn/1231317854/4303609405582510替换成   #https://m.weibo.cn/status/4298029131336650?
            i = line.find('/',12,exampleLenths)
            s1 = line[0:i+1]
            j = line.find('/',i+5,exampleLenths)
            s3 = line[j:]
            url = s1+'status'+s3
            print(url)
##            #剔除网页中无video的url
##            if(url in NotExsiteVideoUrls):
##                continue
            #去重
            if url not in urls:
                urls.append(url)
                counts = counts + 1
        else:
            continue
    end = time.clock()
    times = (end - start)
    print ('处理%s条VideoUrls'%lens) + ('链接转换[  %s ]条'%counts) + (" 用时：%s"% times)
    print('==============================================')
    sf = './handledwellUrls%s.txt'% datetime.datetime.now().strftime('[%Y-%m-%d %H %M %S]')
    with open(sf,'w+') as savefile:
        savefile.write("\n".join(urls))
    savefile.close()

    return urls 

def saveToFile(filecontent):
    #获得当前时间时间戳 
    now = int(time.time()) 
    #转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S" 
    timeStruct = time.localtime(now) 
    strTime = time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)
    filecontent = filecontent + "\n" + strTime + "\n"
    with open('./ErrorInformations.txt','a+') as f1:
        f1.write(filecontent)
    f1.close()

def getVideoUrlsAndNames(urls):
    counts = 0
    browser = webdriver.Chrome()
    videodicts = {}
    for url in urls:
        start = time.clock()
        counts = counts +1
        print("第[ " + str(counts) + " ]条:" + url)
        browser.get(url)
        #get 小视频名
        try:
            div_wbtext = browser.find_element_by_class_name("weibo-text")
        except NoSuchElementException as msg:
            strmsg = url+"\ntarget: find_element_by_class_name(\"weibo-text\")\nError: "+u"查找元素异常%s"%msg              
            print(strmsg)
            saveToFile(url)
            continue   
        else:
            videoname = div_wbtext.text
            videoname2 = videoname.strip('\n')
            videoname3 = videoname2.replace('\n','')
            videoname3 = validateFileName(videoname2)
            print(videoname3)  
        try:
            btnplayer = browser.find_element_by_xpath("//button[@class='mwbv-play-button']")
        except NoSuchElementException as msg:
            print(url+"\ntarget: //button[@class='mwbv-play-button']\nError: "+u"查找元素异常%s"%msg)
            continue   
        else:
            btnplayer.click() #必须模拟点击，weibo的js才会解析出合法的ssig 从page source直接找着的无法使用
                 
        video = browser.find_element_by_xpath("//video")
        videoUrls = video.get_attribute("src")
        if(len(videoUrls)<=0):
            print( "Warning!: 获取视频src失败!:\n   " + videoname3 + "\n   " + url + "\n" )
            continue
        videodicts[videoname3]=videoUrls        
        end = time.clock()
        times = (end - start)
        print(videoUrls)
        print(" 用时：%s秒"% times)
        print("\n")
    browser.close()
    return videodicts

def main():        
    if not os.path.exists(g_dir):
        os.mkdir(g_dir)
    fnlist = [r'待下载视频.txt',r'https_m.weibo.txt',r'http_www.fast.txt']
    for x in fnlist:
        filename =  './' + x
        urls = preHandleWebUrls(filename)
        videodicts = getVideoUrlsAndNames(urls)
        down_video(videodicts)
        

if __name__ == '__main__':
    main()

##    url = 'https://m.weibo.cn/detail/4277600509482250#&video'
##    watchOneVideo(url)
##    getOneVideo(url)

