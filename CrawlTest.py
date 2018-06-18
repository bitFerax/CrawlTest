#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def Format(content):    #整理数据格式
        content = content.replace("\n","")
        content = content.replace("},{","\n\n")
        content = content.replace("}{","\n\n")
        content = content[1:-1]+'\n\n'
        content = content.replace("\",\"","\n")
        content = content.replace("\":\"",": ")
        content = content.replace("\"","")
        return content

def Gettotal(content):    #提取该次查询返回结果的总条数
        x = content.index('total') + 8
        y = content.index('page') - 3
        return int(content[x:y])

print("This code crawls metadata from https://api.itbook.store")
list = ['artificial intelligence','bitcoin','c++','database']    #依次访问关键字list中的每个关键字对应的查询结果
for kw in list:
    starttime = time.time()
    try:
        response = requests.get('https://api.itbook.store/1.0/search/%s' % kw)
    except Exception as e:
        raise("Request failed.")
    text = response.content.decode("utf8")
    
    if text[text.index('total')+8] == '0':    #判断是否有有效数据，如有则开始处理第1页
        print('Request succeeded. No data found for %s.' % kw)
    else:
        total = Gettotal(text)
        if total % 10:
            pages = total/10 + 1
        else:
            pages = total/10
        p1text = text[(text.index('title')-2):-2]
        p1text = Format(p1text)
        print("Request succeeded. Found %d page(s) of data for %s..." % (pages,kw))

        with open("APIData for %s.txt" % kw, 'w') as f:    #储存第1页
            f.write("Query: %s\n" % kw)
            f.write("Total: %d\n" % total)
            f.write("Books:\n\n")
            f.write(p1text)
        print("Successfully written 1 page...")

        if pages > 1:    #继续访问并储存余下数据
            for page in range(pages-1):
                try:
                    response = requests.get('https://api.itbook.store/1.0/search/%s/%d' % (kw,page+2))
                except Exception as e:
                    raise("Request failed.")
                text = response.content.decode("utf8")
                skimmedText = text[(text.index('title')-2):-2]
                skimmedText = Format(skimmedText)
                with open("APIData for %s.txt" % kw, 'a') as f:
                    f.write(skimmedText)
                print("Successfully written %s pages..." % str(page+2))
        print("Data successfully saved to file.")
    endtime = time.time()
    print("Time elapsed = "+"%ss" % str(endtime-starttime))    