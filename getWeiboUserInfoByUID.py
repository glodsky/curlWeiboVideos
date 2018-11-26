# -*- coding: utf-8 -*-
# python version : 3.6
import urllib.request
import os
import json
import datetime
import random

WEIBO_USER_BASE_INFOR = []
Proxies_POOLs =[]

#设置代理IP
proxy_addr="175.155.138.182:1133"

def get_proxiesPOOLs():
    #初始化IP代理池
    global Proxies_POOLs
    with open('./prxies_pools.csv','r') as f:
        contents = f.readlines()
        f.close()
    num = len(contents)
    for i in range(num):
        details = contents[i].split(',')
        proxy= {details[2].strip('\n') :"%s:%s"%(details[0],details[1])}
        Proxies_POOLs.append(proxy)     
    print ( Proxies_POOLs[32])
    

#定义页面打开函数
def use_proxy(url,proxy_addr):
    global Proxies_POOLs
    req=urllib.request.Request(url)
    proxy_addr = Proxies_POOLs[random.randint(0,len(Proxies_POOLs)-1)]
    req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
    proxy=urllib.request.ProxyHandler({'http':proxy_addr})
    opener=urllib.request.build_opener(proxy,urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    data=urllib.request.urlopen(req).read().decode('utf-8','ignore')
    return data


def getUIDs(filename):
    UIDs_list = []
    with open(filename,'r') as fn:
        UIDs_list = fn.read().split('\n')
        fn.close()
    return UIDs_list

def save_to_json(userInfor,filename='./userInfor.json'):
    with open(filename,'w+',encoding='utf-8') as fn:
        for line in userInfor:
            data = str(line)
            if data.find('\u0e51'):
                data.replace('\u0e51','')
            fn.write(data+"\n")
        fn.close()   

    
    
#获取微博账号的用户基本信息，如：微博昵称、微博地址、微博头像、关注人数、粉丝数、性别、等级等
def get_userInfo(id):
    global WEIBO_USER_BASE_INFOR
    url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+id
    data=use_proxy(url,proxy_addr)
    #print (data)
    try:        
        content=json.loads(data).get('data')
        profile_image_url=content.get('userInfo').get('profile_image_url')
        description=content.get('userInfo').get('description')
        profile_url=content.get('userInfo').get('profile_url')
        verified=content.get('userInfo').get('verified')
        guanzhu=content.get('userInfo').get('follow_count')
        name=content.get('userInfo').get('screen_name')
        fensi=content.get('userInfo').get('followers_count')
        gender=content.get('userInfo').get('gender')
        urank=content.get('userInfo').get('urank')
        userInfor = {"微博昵称": name,"微博主页地址": profile_url, \
                     "微博头像地址" : profile_image_url,"是否认证" : str(verified), \
                     "微博说明" : description,"关注人数" : str(guanzhu), \
                     "粉丝数" : str(fensi),"性别" : gender,"微博等级" : str(urank) }
        WEIBO_USER_BASE_INFOR.append(userInfor)
        
    except AttributeError as e:
        print("at UID=%s  Error type = %s"%(id,e  ))
        
 
def main():
    global WEIBO_USER_BASE_INFOR
    uid_list = getUIDs('./handledwell_UIDs.txt')
    print( uid_list )
    get_proxiesPOOLs()
    for uid in uid_list: 
        get_userInfo(uid)
    
    save_to_json(WEIBO_USER_BASE_INFOR)
    
    for x in WEIBO_USER_BASE_INFOR:
        print(x)
 
if __name__ == '__main__':    
    main()
