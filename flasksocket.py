from flask import Flask
from flask_sockets import Sockets
import json

app = Flask(__name__)
sockets = Sockets(app)


# 用户列表 1.名称 2.socket 3.游戏状态 4.gameindex 所在游戏局
userlist=[]
# 邀请列表数据 1.用户名称  2.用户index  3.b用户名称  4.b用户index  5.邀请状态 0：失败  1.a邀请b  2：b邀请a  3.成功
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
        msgsrv.observers.append(ws)
        message = ws.receive()
        if message == "Search":
            liststring =json.dumps(userlist)
            msgsrv.add_message(liststring)
        else:
            # userlist插入用户列表
            msgObj = json.loads(message)
            username = msgObj['user']
            # 定义用户对象
            userDic={}
            userDic['username']=username
            userDic['wsindex']=len(msgsrv.observers)-1
            userDic['gameindex']=-1
            # 0 未开始  1 邀请中  2游戏中  3 游戏结束
            userDic['gamestatus'] = 0
            # 插入用户列表
            userlist.append(userDic)
            userobjliststr=json.dumps(userlist)
            msgsrv.add_message(userobjliststr)

# 邀请参加
    



@app.route('/')
def hello():
    return 'Hello World!'


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('localhost', 9876), app, handler_class=WebSocketHandler)
    server.serve_forever()