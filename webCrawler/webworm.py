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
print(html)

# html =urlopen("https://www.google.com.tw/").read().decode("utf-8")
# html =urlopen("https://www.baidu.com/").read().decode("utf-8")
html =urlopen("https://morvanzhou.github.io/static/scraping/basic-structure.html").read().decode("utf-8")
# print(html)

# 常规正则查询
res =re.findall(r"<title>(.+?)</title>",html)
# print("\n page title is ",res[0])

# 利用beautifulsoup
soup = BeautifulSoup(html,features="lxml")
all_href=soup.find_all('a')
for l in all_href:
    print(l['href'])
print(soup.h1)




