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
import time
import datetime

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
    sqlstr = "SELECT t.taskid,t.taskname,t.starttime,t.endtime FROM xfz_taskrule AS t WHERE t.isdeleted=0 AND t.weekindex LIKE '%%"+weekindex+"%%'"
    listResult = sqlutils.exec_sql(sqlstr)
    return json.dumps({'tasklist': listResult}, cls=common.CJsonEncoder.CJsonEncoder)

# 根据任务id删除任务
@taskapi.route('/deleteTask',methods=['GET'])
def delete_task():
    # 获取任务id
    taskid = request.args.get('taskid')
    if taskid is None:
        taskid =""
    print(taskid)
    # 拼接执行sql
    sqlstr = "UPDATE xfz_task SET isdeleted=1 WHERE task_id = "+str(taskid)
    count = sqlutils.exec_txsql(sqlstr)
    return str(count)

# 根据日期或者用户id任务列表
@taskapi.route('/getTaskList',methods=['GET'])
def get_tasklist():
    # 获取参数
    userid = request.args.get('userid')
    if userid is None:
        userid=""
    searchDate= request.args.get('searchDate')
    if searchDate is None:
        searchDate=time.strftime('%Y-%m-%d',time.localtime())

    # 拼接执行sql
    sqlstr = "SELECT t.id,t.taskid,s.taskname,s.starttime,s.endtime,t.taskStatus FROM xfz_dailytask AS t " \
             "LEFT JOIN xfz_taskrule AS s ON t.taskid=s.taskid " \
             "WHERE t.userid={0} AND DATE_FORMAT(t.create_time,'%Y-%m-%d')='{1}'".format(userid,searchDate)

    print(sqlstr)
    listResult = sqlutils.exec_sql(sqlstr)
    return json.dumps({'tasklist': listResult}, cls=common.CJsonEncoder.CJsonEncoder)

# 根据具体任务id完成任务
@taskapi.route('/finishTask',methods=['POST'])
def finish_task():

    try:
        # 校验请求header
        if request.content_type != JSON_MIME_TYPE:
            error = json.dumps({'errorMsg': '无效Content Type'})
            return json_response(error, 400)

        requestdata = request.json
        # 校验必输项为空
        if not all([requestdata.get('id')]):
            error = json.dumps({'responseMsg': '请输入必输项', RESPONSE_CODE: 300})
            return json_response(error, 200)

        insertStr = 'UPDATE xfz_dailytask SET taskStatus=1 WHERE id ={0}'.format(requestdata['id'])
        count = sqlutils.exec_txsql(insertStr)
        success = json.dumps({RESPONSE_CODE: 200})
        return json_response(success)
    except:
        return json_response(error,500)

# 新建任务规则
@taskapi.route('/createTask', methods=['POST'])
def createTask():
    try:
        # 校验请求header
        if request.content_type != JSON_MIME_TYPE:
            error = json.dumps({'errorMsg': '无效Content Type'})
            return json_response(error, 400)

        requestdata = request.json
        # 校验必输项为空
        # if not all([requestdata.get('telephone'), requestdata.get('pwd')]):
        #     error = json.dumps({'responseMsg': '请输入必输项', RESPONSE_CODE: 300})
        #     return json_response(error, 200)

        nowdt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        insertStr = "INSERT INTO xfz_taskrule (taskname, starttime,endtime,weekindex,repeattype,wechat_open_id,userid,createtime,updatetime,isdeleted) " \
                    "VALUES ('{0}','{1}','{2}','{3}',{4},'{5}',{6},'{7}','{8}',{9})".\
            format(requestdata['taskname'], requestdata['starttime'], requestdata['endtime'], requestdata['weekindex'],requestdata['repeattype'],
                   requestdata['wechat_open_id'],requestdata['userid'],nowdt,nowdt,0)
        count = sqlutils.exec_txsql(insertStr)
        success = json.dumps({RESPONSE_CODE: 200})
        return json_response(success)
    except:
        return json_response(error,500)

# 根据opencode 返回openid，如果没有openid存储openid







