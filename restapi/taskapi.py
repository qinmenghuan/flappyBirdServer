# coding:utf-8

'''
    任务相关接口实例
    create by qmh 2018-09-24
'''


from flask import Flask,request,Blueprint,make_response
import json
import common.CJsonEncoder
import common.mysqldemo
from restapi.utils import json_response, JSON_MIME_TYPE,RESPONSE_CODE

taskapi = Blueprint(r'taskapi', __name__)
# 初始化sql操作类
sqlutils=common.mysqldemo.MySQL_Utils()


# 根据日期  星期获取任务列表
@taskapi.route('/tasks',methods=['GET'])
def get_task():
    # 获取星期几
    weekindex = request.args.get('weekindex')
    if weekindex is None:
        weekindex=""
    print(weekindex)
    # 拼接执行sql
    sqlstr = "SELECT t.task_id,t.taskname,t.starttime,t.endtime FROM xfz_task AS t WHERE t.isdeleted=0 AND t.weekindex LIKE '%%"+weekindex+"%%'"
    listResult = sqlutils.exec_sql(sqlstr)
    return json.dumps({'tasklist': listResult}, cls=common.CJsonEncoder.CJsonEncoder)
