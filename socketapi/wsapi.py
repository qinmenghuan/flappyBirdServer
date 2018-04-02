'''
    socket接口实例
    create by qmh 2018-03-29
'''

# 引用类库
from flask import Flask, Blueprint
import json

# 引用sql类，工具
import common.mysqldemo

# 初始化sql操作类
sqlutils = common.mysqldemo.MySQL_Utils()
wsapi = Blueprint(r'wsapi', __name__)


# 邀请列表数据 1.用户名称  2.用户index  3.b用户名称  4.b用户index  5.邀请状态 0：失败  1.a邀请 b邀请中  2.成功
invitelist = []
# 游戏列表 1.a用户 2.a用户ws 3.b用户 4.b用户ws  5.游戏状态  # 0 未开始  1 游戏中  2 游戏结束,a方胜 3.游戏结束，b方胜
gamelist = []

wslist = []

# 引用类
import message
import socketapi.user_server

# 实力化
msgsrv = message.MessageServer()
user_server_obj = socketapi.user_server.UserServer()


@wsapi.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)


# 最新登录及放回用户列表
@wsapi.route('/login')
def login_socket(web_socket):
    while not web_socket.closed:
        # wslist.append(ws)
        receive_msg = web_socket.receive()
        # userlist插入用户列表
        if not receive_msg:
            return
        receive_msg_dic = json.loads(receive_msg)
        socket_type = receive_msg_dic["type"]
        if socket_type == "Login":
            login_user = receive_msg_dic["data"]
            # 1 数据库查询是否存在该用户
            user_telephone = login_user['telephone']
            sqlstr = 'SELECT * FROM xfz_user WHERE telephone ={0} AND pwd = {1}'.format(user_telephone, login_user['pwd'])
            count = sqlutils.exec_sql(sqlstr)
            #  如果查不到该用户
            if not count :
                response_dic = {"type": "Login", "response_code": "300", "response_msg": "账号或密码不正确",
                                "response_data": {}}
                web_socket.send(json.dumps(response_dic))

            # 存在该用户
            else:
                #  2 缓存用户，判断是否存在  ，存在即更新
                # 如果存在该登录用户，则先下线该用户
                if user_telephone in user_server_obj.user_socket_dic:
                    user_socket = user_server_obj.user_socket_dic[user_telephone]
                    response_dic = {"type": "Login", "response_code": "301", "response_msg": "账号在另外台设备登录",
                                    "response_data": {}}
                    user_socket.send(json.dumps(response_dic))

                # 3 保存websocket
                user_server_obj.user_socket_dic[user_telephone] = web_socket

                # 4 保存用户列表
                login_user_dic = {}
                login_user_dic['telephone'] = user_telephone
                login_user_dic['gameid'] = -1
                # 0 未开始  1 邀请中  2游戏中  3 游戏结束
                login_user_dic['user_status'] = 0
                user_server_obj.user_list_dic[user_telephone]=login_user_dic

                # 5 发送成功消息,向所有用户发送用户列表消息
                user_server_obj.send_all_users()
        elif socket_type == "Search":
            # 5 发送成功消息,向所有用户发送用户列表消息
            user_server_obj.send_all_users()


# 邀请参加
@wsapi.route('/invite')
def echo_socket(ws):
    while not ws.closed:

        # 接受邀请对象
        invitemessage = ws.receive()
        # 转化msg对象
        inviteobj = json.loads(invitemessage)
        msgtype = inviteobj["type"]
        # 如果是初始化
        if msgtype == 'init':
            # 保存websocket
            msgsrv.invitesWslist.append(ws)
        elif msgtype == 'sendinvite':
            # 添加邀请列表
            inviteitem = inviteobj["msgobj"]
            inviteitem["inviteIndex"] = len(invitelist)
            invitelist.append(inviteitem)
            # 发送消息
            msgsrv.invite_message(inviteitem)
        # 如果同意邀请
        elif msgtype == 'agreeinvite':
            inviteitem = inviteobj["msgobj"]
            inviteIndex = inviteitem["inviteIndex"]
            # 保存游戏对象 {}
            inviteitem = invitelist[inviteIndex]
            inviteitem["status"] = 2
            invitelist[inviteIndex] = inviteitem
            gamelist.append(inviteitem)
            # 发送成功对战消息
            response = {}
            response["type"] = "AGREE"
            gameindex = len(gamelist) - 1
            inviteitem["gameIndex"] = gameindex
            response["data"] = inviteitem
            msgsrv.agree_message(response)


#  进行游戏1
@wsapi.route('/game')
def echo_socket(ws):
    while not ws.closed:
        # 返回的消息
        receiveMessage = ws.receive()
        # 转化msg对象
        receiveObj = json.loads(receiveMessage)
        msgtype = receiveObj["type"]

        # 如果是初始化
        if msgtype == 'init':
            username = receiveObj["username"]
            # 保存websocket
            msgsrv.gameSocketDic[username] = ws
        # 游戏进行中
        elif msgtype == 'gaming':
            gameStepInfo = receiveObj["msgobj"]
            opponentName = gameStepInfo["opponentName"]
            opponentSocket = msgsrv.gameSocketDic[opponentName]
            opponentSocket.send(json.dumps(receiveObj))
        # 游戏结束
        elif msgtype == 'GameOver':
            # 跟对手发送消息
            gameStepInfo = receiveObj["msgobj"]
            opponentName = gameStepInfo["opponentName"]
            opponentSocket = msgsrv.gameSocketDic[opponentName]
            # 更新游戏数据
            gameIndex = gameStepInfo["gameIndex"]
            gameInfo = gamelist[gameIndex]
            gameInfo["status"] = gameStepInfo["gameStatus"]
            gamelist[gameIndex] = gameInfo
            # 发socket
            opponentSocket.send(json.dumps(receiveObj))
