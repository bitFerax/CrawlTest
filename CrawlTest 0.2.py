#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import re
import json
import os

def SaveImage(book,kw):    #获取并储存封面图片
    img_url = book['image']
    img = requests.get(img_url)
    with open('%s/ibookstoreAPIData/%s/image/%s.jpg' % (rootpath,kw,book['title']), 'ab') as f:
        f.write(img.content)
    return 0

def Gettotal(content):    #提取该次查询返回结果的总条数
    x = content.index('total') + 8
    y = content.index('page') - 3
    return int(content[x:y])

def Getlist():    #捕获用户输入的查询关键字
    list = []
    while(1):
        nextlist = input()
        if nextlist:
            list.append(nextlist)
        else:
            break
    return list

print("This code crawls metadata, in json, from https://api.itbook.store")
print("Enter the keywords you want to search, end with an empty line:")
list = Getlist()
starttime = time.time()
rootpath = os.path.abspath('.')
if os.path.exists('%s/ibookstoreAPIData' % rootpath) == False:    #创建文件路径
    os.mkdir('%s/ibookstoreAPIData' % rootpath)

for kw in list:    #依次访问关键字list中的每个关键字对应的查询结果
    try:
        response = requests.get('https://api.itbook.store/1.0/search/%s' % kw)
    except Exception:
        raise("Request failed.")
    text = response.content.decode("utf8")
    
    if text[text.index('total')+8] == '0':    #判断是否有有效数据，如有则开始处理第1页
        print('Request succeeded. No data found for %s.' % kw)
    else:
        if os.path.exists('%s/ibookstoreAPIData/%s' % (rootpath,kw)) == False:
            os.mkdir('%s/ibookstoreAPIData/%s' % (rootpath,kw))
            if os.path.exists('%s/ibookstoreAPIData/%s/image' % (rootpath,kw)) == False:
                os.mkdir('%s/ibookstoreAPIData/%s/image' % (rootpath,kw))

        total = Gettotal(text)
        if total % 10:
            pages = int(total/10 + 1)
        else:
            pages = int(total/10)
        print("Request succeeded. Found %d page(s) of data for %s..." % (pages,kw))
        dictionary = {"Query": kw, "Total": total, "Books": []}
        
        p1text = text[(text.index('title')-2):-2]    #储存第1页
        booklist = re.split(r'},',p1text)
        for i in range(len(booklist)-1):
            booklist[i]=booklist[i]+"}"
        for book in booklist:
            book = json.loads(book)
            dictionary["Books"].append(book)
            SaveImage(book,kw)
        print('Saved 1 page of data...')

        if pages > 1:    #继续访问并储存余下数据
            for page in range(pages-1):
                try:
                    response = requests.get('https://api.itbook.store/1.0/search/%s/%d' % (kw,page+2))
                except Exception as e:
                    raise("Request failed.")
                text = response.content.decode("utf8")
                pnText = text[(text.index('title')-2):-2]
                booklist = re.split(r'},',pnText)
                for i in range(len(booklist)-1):
                    booklist[i]=booklist[i]+"}"
                for book in booklist:
                    book = json.loads(book)
                    dictionary["Books"].append(book)
                    SaveImage(book,kw)
                print('Saved %d pages of data...' % (page+2))

        file = json.dumps(dictionary)    #将dict转化为json并写入文件
        with open('%s/ibookstoreAPIData/%s/metadata.json' % (rootpath,kw), 'w') as f:
            f.write(file)
        print("Data for %s saved to file." % kw)

endtime = time.time()
print("Time elapsed = "+"%ss" % str(endtime-starttime))