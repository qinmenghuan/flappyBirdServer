'''
    http返回数据处理工具
    create by qmh 2018-03-24
'''

from flask import make_response

JSON_MIME_TYPE="application/json"
CONTENT_TYPE="Content-type"

# 返回json格式信息处理
def json_response(data='',status=200,headers=None):
    headers=headers or {}
    if CONTENT_TYPE not in headers:
        headers[CONTENT_TYPE]=JSON_MIME_TYPE
    return make_response(data,status,headers)

