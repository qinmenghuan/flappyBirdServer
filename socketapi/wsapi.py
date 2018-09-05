# coding:utf-8

'''
    socket接口实例
    create by qmh 2018-03-29
'''

# 引用类库
from flask import Flask, Blueprint
import json
import datetime

# 引用sql类，工具
import common.mysqldemo
import message
import socketapi.user_server
import socketapi.invite_server

# 实例化sql操作类
sqlutils = common.mysqldemo.MySQL_Utils()
wsapi = Blueprint(r'wsapi', __name__)
msgsrv = message.MessageServer()
user_server_obj = socketapi.user_server.UserServer()
invite_server_obj=socketapi.invite_server.InviteServer()

# 游戏列表 1.a用户 2.a用户ws 3.b用户 4.b用户ws  5.游戏状态  # 0 未开始  1 游戏中  2 游戏结束,a方胜 3.游戏结束，b方胜
gamelist = []

@wsapi.route('/')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)


# 最新登录及放回用户列表
@wsapi.route('/login')
def login_socket(web_socket):
    while not web_socket.closed:
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
                                "data": {}}
                web_socket.send(json.dumps(response_dic))

            # 存在该用户
            else:
                #  2 缓存用户，判断是否存在  ，存在即更新
                # 如果存在该登录用户，则先下线该用户
                if user_telephone in user_server_obj.user_socket_dic:
                    user_socket = user_server_obj.user_socket_dic[user_telephone]
                    response_dic = {"type": "Login", "response_code": "301", "response_msg": "账号在另外台设备登录",
                                    "data": {}}
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

# 游戏邀请
@wsapi.route('/gameinvite')
def invite_socket(web_socket):
    while not web_socket.closed:
        receive_msg = web_socket.receive()
        # userlist插入用户列表
        if not receive_msg:
            return
        receive_msg_dic = json.loads(receive_msg)
        socket_type = receive_msg_dic["type"]
        receive_data = receive_msg_dic["data"]

        # 初始化
        if socket_type =="Init":
            telephone=receive_data["telephone"]
            invite_server_obj.invite_socket_dic[telephone]=web_socket

        # 发送邀请
        elif socket_type=="Invite":
            aTelephone = receive_data["aTelephone"]
            bTelephone = receive_data["bTelephone"]
            # 判断是否已经发邀请
            if aTelephone in invite_server_obj.invite_dic:
                response_dic = {"type": "Invite", "response_code": "300", "response_msg": "同一时间只能邀请一位","data": {}}
                web_socket.send(json.dumps(response_dic))

            # 判断已经被邀请
            if bTelephone in invite_server_obj.invite_dic:
                response_dic = {"type": "Invite", "response_code": "300", "response_msg": "该用户已被邀请","data": {}}
                web_socket.send(json.dumps(response_dic))

            # 插入邀请人信息
            invite_server_obj.invite_dic[aTelephone]=receive_data
            # 插入被邀请人信息
            invite_server_obj.invite_dic[bTelephone] = receive_data
            # 发送双方消息
            invite_server_obj.invite_message(receive_data)

        # 同意邀请
        elif socket_type=="Agree":
            aTelephone = receive_data["aTelephone"]
            bTelephone = receive_data["bTelephone"]
            # 用户状态
            user_server_obj.user_list_dic[aTelephone]["user_status"] = 2
            user_server_obj.user_list_dic[bTelephone]["user_status"] = 2

            # 保存游戏
            nowdt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # insertStr = 'INSERT INTO xfz_game (a_telephone, b_telephone,game_status,create_time,update_time) VALUES ({0},{1},{2},{3},{4})'.format(aTelephone, bTelephone,2,nowdt,nowdt)
            insertStr = 'INSERT INTO xfz_game (a_telephone, b_telephone,game_status) VALUES ({0},{1},{2})'.format(aTelephone, bTelephone,2)
            sqlutils.exec_txsql(insertStr)

            # 发送双方消息
            invite_server_obj.agree_message(receive_data)

        # 拒绝邀请
        elif socket_type=="Refuse":
            # 1 清空邀请消息
            aTelephone = receive_data["aTelephone"]
            bTelephone = receive_data["bTelephone"]
            invite_server_obj.invite_dic.pop(aTelephone)
            invite_server_obj.invite_dic.pop(bTelephone)

            # 2 发送邀请者消息
            invite_server_obj.refuse_message(receive_data)


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
