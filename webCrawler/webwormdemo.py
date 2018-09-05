# coding:utf-8
'''
    爬虫
    create by qmh 2018-05-06
'''

from urllib.request import urlopen
import re
from bs4 import BeautifulSoup

response = urlopen("http://www.google.com")
html = response.read()
# print(html)

soup = BeautifulSoup(html,features="lxml")
result={}

# 房源信息

all_img=soup.find_all("img")



imglist=[]
for img in all_img:
    imgItem={}
    imgItem["tagtype"]="img"
    imgItem["width"] = img["width"]
    imgItem["height"] = img["height"]
    imgItem["text"]=""
    imglist.append(imgItem)
    # print(img)
result["imglist"]=imglist

# 文本

# form

# others

print(result)



