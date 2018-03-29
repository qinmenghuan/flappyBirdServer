'''
    socket接口实例
    create by qmh 2018-03-29
'''


from flask import Flask,request,Blueprint,make_response
import json
import common.CJsonEncoder
import common.mysqldemo
from restapi.utils import json_response, JSON_MIME_TYPE,RESPONSE_CODE

userapi = Blueprint(r'userapi', __name__)
sqlutils=common.mysqldemo.MySQL_Utils()

@userapi.route('/')
def hello():
    return 'Hello World1234!!!'

@userapi.route('/hello')
def hello1():
    return 'Hello World111!!!'

# 获取用户列表信息
@userapi.route('/user/getusers',methods=['GET'])
def get_userlist():
    sqlstr="SELECT * FROM xfz_user"
    listResult =sqlutils.exec_sql(sqlstr)
    return json.dumps({'users': listResult}, cls=common.CJsonEncoder.CJsonEncoder)

# 删除用户
@userapi.route('/user/deluser',methods=['GET'])
def get_deluser():
    userid =request.args.get('userid')
    print(userid)
    sqlstr="update xfz_user set isdeleted=1 where id = "+str(userid)
    count =sqlutils.exec_txsql(sqlstr)
    return str(count)

# 注册用户
@userapi.route('/user/register',methods=['POST'])
def register():
    # 校验请求header
    if request.content_type != JSON_MIME_TYPE:
        error=json.dumps({'errorMsg':'无效Content Type'})
        return json_response(error,400)

    requestdata = request.json
    # 校验必输项为空
    if not all([requestdata.get('telephone'),requestdata.get('pwd')]):
        error=json.dumps({'responseMsg':'请输入必输项',RESPONSE_CODE:300})
        return json_response(error,200)

    insertStr = 'INSERT INTO xfz_user (telephone, pwd) VALUES ({0},{1})'.format(requestdata['telephone'], requestdata['pwd'])
    count = sqlutils.exec_txsql(insertStr)
    success = json.dumps({RESPONSE_CODE:200})
    return json_response(success)

