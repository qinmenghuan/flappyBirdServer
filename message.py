from geventwebsocket import WebSocketError
import json

class MessageServer(object):

    def __init__(self):
        # 邀请websocket集合
        self.invitesWslist = []
        # 查询websocket集合
        self.observers = []
        # 用户列表 1.名称 2.socket 3.游戏状态 4.gameindex 所在游戏局
        self.userlist=[]
        # 用户名称列表
        self.usernamelist=[]

        # 游戏列表 1.a用户 2.a用户ws 3.b用户 4.b用户ws  5.游戏状态
        self.gamelist=[]

    # 全局发送消息
    def add_message(self, msg):
        for ws in self.observers:
            try:
                ws.send(msg)
            except WebSocketError:
                self.observers.pop(self.observers.index(ws))
                print(ws, 'is closed')
                continue

    def invite_message(self ,inviteobj):
        try:
            print(self.invitesWslist)
            awsindex=inviteobj['aWsIndex']
            print(awsindex)
            aws = self.invitesWslist[awsindex]
            aws.send("inviteSuccess")
            bwsindex=inviteobj['bWsIndex']
            bws = self.invitesWslist[bwsindex]
            bws.send(json.dumps(inviteobj))
        except WebSocketError:
            self.observers.pop(self.observers.index(ws))
            print(ws, 'is closed')

    def agree_message(self ,responseobj):
        try:
            inviteobj=responseobj["data"]
            print(self.invitesWslist)
            awsindex=inviteobj['aWsIndex']
            print(awsindex)
            aws = self.invitesWslist[awsindex]
            aws.send(json.dumps(responseobj))
            bwsindex=inviteobj['bWsIndex']
            bws = self.invitesWslist[bwsindex]
            bws.send(json.dumps(responseobj))
        except WebSocketError:
            # self.observers.pop(self.observers.index(ws))
            print('is closed')