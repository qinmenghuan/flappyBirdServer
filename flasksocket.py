from flask import Flask
from flask_sockets import Sockets
import json

app = Flask(__name__)
sockets = Sockets(app)


# 用户列表 1.名称 2.socket 3.游戏状态 4.gameindex 所在游戏局
userlist=[]
# 邀请列表数据 1.用户名称  2.用户index  3.b用户名称  4.b用户index  5.邀请状态 0：失败  1.a邀请b邀请中  2.成功

invitelist=[]
wslist=[]

import message
msgsrv = message.MessageServer()

@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)

@sockets.route('/login')
def echo_socket(ws):
    while not ws.closed:
        wslist.append(ws)
        message = ws.receive()
        # userlist插入用户列表
        msgObj=json.loads(message)
        userlist.append(msgObj['user'])
        # print(userlist)
        ws.send(json.dumps(userlist))

# 登陆及返回
@sockets.route('/gamelogin')
def echo_socket(ws):
    while not ws.closed:
        # 获取message
        message = ws.receive()
        if message is None:
            return
        if message == "Search":
            # 保存websocket
            msgsrv.observers.append(ws)
            # 返回全部用户列表
            liststring =json.dumps(userlist)
            msgsrv.add_message(liststring)
        else:
            # userlist插入用户列表
            msgObj = json.loads(message)
            username = msgObj['user']
            # 定义用户对象
            userDic={}
            userDic['username']=username
            userDic['wsindex']=len(msgsrv.observers)
            userDic['gameindex']=-1
            # 0 未开始  1 邀请中  2游戏中  3 游戏结束
            userDic['gamestatus'] = 0
            # 插入用户列表
            userlist.append(userDic)
            # 返回当前用户
            userDicStr=json.dumps(userDic)
            # 返回当前登陆人
            ws.send(userDicStr)
            # 通知其他玩家上线啦
            userliststr = json.dumps(userlist)
            msgsrv.add_message(userliststr)


# 邀请参加
@sockets.route('/invite')
def echo_socket(ws):
    while not ws.closed:
        # 保存websocket
        msgsrv.invitesWslist.append(ws)
        # 接受邀请对象
        message = ws.receive()
        inviteobj=json.loads(message)
        # 添加邀请列表
        invitelist.append(inviteobj)
        # 发送消息
        # ws.send("邀请成功")
        msgsrv.invite_message(inviteobj)


@app.route('/')
def hello():
    return 'Hello World!'


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('localhost', 9876), app, handler_class=WebSocketHandler)
    server.serve_forever()