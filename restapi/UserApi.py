'''
    接口实例
    create by qmh 2018-03-24
'''

from flask import Flask,request,Blueprint,make_response
import json
import common.CJsonEncoder
import common.mysqldemo
from restapi.utils import json_response, JSON_MIME_TYPE

sqlutils=common.mysqldemo.MySQL_Utils()
app = Flask(__name__)

# user api
user_api=Blueprint('user_api',__name__)

@user_api.route("/hello")
def hello():
    return "Hello World112!"

# 获取用户列表信息
@user_api.route('/user/getusers',methods=['GET'])
def get_userlist():
    sqlstr="SELECT * FROM xfz_user"
    listResult =sqlutils.exec_sql(sqlstr)
    return json.dumps({'users': listResult}, cls=common.CJsonEncoder.CJsonEncoder)

# 删除用户
@user_api.route('/user/deluser',methods=['GET'])
def get_deluser():
    userid =request.args.get('userid')
    print(userid)
    sqlstr="update xfz_user set isdeleted=1 where id = "+str(userid)
    count =sqlutils.exec_txsql(sqlstr)
    return str(count)

@user_api.route('/user/register',methods=['POST'])
def register():
    # 校验请求header
    if request.content_type != JSON_MIME_TYPE:
        error=json.dumps({'errorMsg':'无效Content Type'})
        return json_response(error,400)

    requestdata = request.json
    # 校验必输项为空
    if not all([requestdata.get('telephone'),requestdata.get('pwd')]):
        error=json.dumps({'errorMsg':'请输入必输项'})
        return json_response(error,200)

    insertStr = 'INSERT INTO xfz_user (telephone, pwd) VALUES ({0},{1})'.format(requestdata['telephone'], requestdata['pwd'])
    count = sqlutils.exec_txsql(insertStr)
    success = json.dumps({'success':True})
    return json_response(success)


@user_api.route('/postjson', methods = ['POST'])
def postJsonHandler():
    print (request.is_json)
    content = request.get_json()
    print (content)
    return 'JSON posted'