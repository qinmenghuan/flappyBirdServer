'''
    xima爬虫
    create by qmh 2018-06-05
'''

import re

sourceUrl="http://www.ximalaya.com/yingshi/11438377/"
id_numberlist=re.findall("/(\d+)/",sourceUrl)
id_number=id_numberlist[0]
print(id_number)
