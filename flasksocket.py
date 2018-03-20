from flask import Flask
from flask_sockets import Sockets
import json

app = Flask(__name__)
sockets = Sockets(app)

# 用户列表 1.名称 2.socket 3.游戏状态 4.gameindex 所在游戏局
userlist = []
# 邀请列表数据 1.用户名称  2.用户index  3.b用户名称  4.b用户index  5.邀请状态 0：失败  1.a邀请 b邀请中  2.成功
invitelist = []
# 游戏列表 1.a用户 2.a用户ws 3.b用户 4.b用户ws  5.游戏状态  # 0 未开始  1 游戏中  2 游戏结束,a方胜 3.游戏结束，b方胜
gamelist = []

wslist = []

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
        msgObj = json.loads(message)
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
            liststring = json.dumps(userlist)
            msgsrv.add_message(liststring)
        else:
            # userlist插入用户列表
            msgObj = json.loads(message)
            username = msgObj['user']
            # 定义用户对象
            userDic = {}
            userDic['username'] = username
            userDic['wsindex'] = len(msgsrv.observers)
            userDic['gameindex'] = -1
            # 0 未开始  1 邀请中  2游戏中  3 游戏结束
            userDic['gamestatus'] = 0
            # 插入用户列表
            userlist.append(userDic)
            # 返回当前用户
            userDicStr = json.dumps(userDic)
            # 返回当前登陆人
            ws.send(userDicStr)
            # 通知其他玩家上线啦
            userliststr = json.dumps(userlist)
            msgsrv.add_message(userliststr)


# 邀请参加
@sockets.route('/invite')
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
            inviteitem["inviteIndex"]=len(invitelist)
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
            invitelist[inviteIndex]=inviteitem
            gamelist.append(inviteitem)
            # 发送成功对战消息
            response = {}
            response["type"] = "AGREE"
            gameindex = len(gamelist) - 1
            inviteitem["gameIndex"] = gameindex
            response["data"] = inviteitem
            msgsrv.agree_message(response)

#  进行游戏1
@sockets.route('/game')
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
            msgsrv.gameSocketDic[username]=ws
        # 游戏进行中
        elif msgtype =='gaming':
            gameStepInfo = receiveObj["msgobj"]
            opponentName=gameStepInfo["opponentName"]
            opponentSocket=msgsrv.gameSocketDic[opponentName]
            opponentSocket.send(json.dumps(receiveObj))
        # 游戏结束
        elif msgtype=='GameOver':
            # 跟对手发送消息
            gameStepInfo = receiveObj["msgobj"]
            opponentName = gameStepInfo["opponentName"]
            opponentSocket = msgsrv.gameSocketDic[opponentName]
            #更新游戏数据
            gameIndex = gameStepInfo["gameIndex"]
            gameInfo=gamelist[gameIndex]
            gameInfo["status"]=gameStepInfo["gameStatus"]
            gamelist[gameIndex]=gameInfo
            # 发socket
            opponentSocket.send(json.dumps(receiveObj))



@app.route('/')
def hello():
    return 'Hello World!'


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('localhost', 9876), app, handler_class=WebSocketHandler)
    server.serve_forever()
