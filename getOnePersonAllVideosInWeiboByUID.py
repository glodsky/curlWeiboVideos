# -*- coding: utf-8 -*-

#  python 3

import json
import time
import datetime
import random
import os
import re
import requests
import sys
import imp 
imp.reload(sys)

def use_proxy(url):     
    response = requests.get(url)
    #print(response.content)
    if response.status_code == 200:
        proxy_status,data = 200 , response.content
    else:
        print("use_proxy Failtured response.status_code = %s"%response.status_code)
        proxy_status,data = response.status_code,"{}"
    return  proxy_status,data

#获取微博主页的containerid，爬取微博内容时需要此id
def get_containerid(url):
    proxy_status,data = use_proxy(url)
    if proxy_status != 200:
        return 0
    content=json.loads(data).get('data')
    tabs = content.get('tabsInfo').get('tabs')
    for data in tabs:
        if(data.get('tab_type')=='weibo'):
            containerid=data.get('containerid')
    return containerid 

def get_ShortName(filename):    #文件名太长,截断
    if len(filename)>25:
        return filename[:25]
    else:
        return filename
    
def init_UrlInfor(uid,page):    
    url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+ uid
    containerid = get_containerid(url)
    if containerid == 0 :
        print("init_UrlInfor Error containerid!")
        return ("","")
    weibo_url="https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=%s&page=%s"%(uid,str(containerid),str(page))
    print(weibo_url)
    return (url,weibo_url)

def download_video(video_name,stream_url):
    print(u"%s downloading ......"% datetime.datetime.now().strftime('[%H:%M:%S]'))
    stime = time.perf_counter()
    response = requests.get(stream_url)
    if response.status_code == 200:
        fn = open(video_name,'wb')
        fn.write(response.content)
        fn.close()
    else:
        print("download Failtured response.status_code = %s"%response.status_code)
        return 0
    etime = time.perf_counter()
    tt = stime - etime
    print(u"%s downloaded  耗时: %.2f 秒\n"% (datetime.datetime.now().strftime('[%H:%M:%S]'),tt))

def get_ParentDirName(cards,uid):
    mblog0 = cards[0].get("mblog")
    user = mblog0.get("user") 
    screen_name = user["screen_name"].strip().replace(" ","")
    #description = re.sub('[\/:*?"<>|，：、]','_',user["description"]).replace(" ","")
    dirName =  u"%s/%s_%s"%(os.curdir,uid,screen_name)
    print ("dirName=%s"%dirName)
    return dirName

def filter_Non_BMP_Characters(target):    
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    name=target.translate(non_bmp_map)
    return name

def get_VideoNameAndUrl(mblog,dirName):
    #text =re.sub('[\/:*?"<>|，：、]','_',mblog["text"]).replace(" ","") 
    page_info = mblog["page_info"]
    media_type = page_info["type"]  #类型 作 扩展名 
    if media_type == "article":
        return ("","")
    elif media_type == "video":
        content2 =re.sub('[\/:*?"<>|，：、？\\n]','_', page_info["content2"]).replace(" ","")
        content2 = filter_Non_BMP_Characters(content2)
        shortname = get_ShortName(content2)
        stream_url = page_info.get("media_info")["stream_url"]
        video_name = "%s/%s.%s"%(dirName,content2,media_type)
        return video_name,stream_url
    else:
        return ("","")

def waiting_times(judge,times = None):
    sleeptime = 0
    if times == None:
        sleeptime = random.randint(1,5)
    if( judge % 3 == 0):     
        time.sleep(sleeptime)
    
def get_weiboAllPictureByUID(uid):
    count = 0
    cur_page= 0
    while True:
        print("\n")
        cur_page = cur_page + 1
        url,weibo_url = init_UrlInfor(uid,cur_page)
        try:
            proxy_status,data = use_proxy(weibo_url)
            if proxy_status != 200:
                continue            
            ok   = int(json.loads(data)['ok'])
            if ok == 0 :
                print("At %s  %s "%(cur_page,json.loads(data)["msg"]))
                continue            
            content = json.loads(data).get('data')            
            cards=content.get('cards')
            cards_len = len(cards)
            print("cards_len=%s"%cards_len) 
            if(cards_len>0):                
                dirName = get_ParentDirName(cards,uid)
                if not os.path.exists(dirName):
                    os.mkdir(dirName)                
                for card_index in range(cards_len):                     
                    print("\n-----正在探测第"+str(cur_page)+"页，第"+str(card_index+1)+"条微博中视频信息------")
                    card_type=int(cards[card_index]['card_type'])
                    if(card_type==9):
                        mblog=cards[card_index].get('mblog')                         
                        if "page_info" not in mblog:
                            print("当前微博中没有视频")                            
                            continue
                        else:
                            #print("mblog['page_info']=%s"%mblog["page_info"])
                            pass
                        video_name,stream_url = get_VideoNameAndUrl(mblog,dirName)
                        if video_name == "" or stream_url == "":
                            print("当前微博中没有视频")                            
                            continue
                        if os.path.exists(video_name):
                            print("已下载过了%s"%(video_name.split("/")[-1]))
                            continue                        
                        download_video(video_name,stream_url)
                        count = count + 1    #下载总数                        
                        waiting_times(cur_page)        
            
        except Exception as e:
            print(e)
            break                  

    print('>>>>>>>>>>>>>>>>>>>')
    print('共计：%s'%count)                         

     
def main():
    id_list = ['1402400261','2155926845','6070772899','3942238643']
    for uid in id_list:
        get_weiboAllPictureByUID(uid)
              
    
if __name__=="__main__":
    main()



    

