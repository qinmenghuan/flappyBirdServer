# coding:utf-8

from geventwebsocket import WebSocketError
import json

class GameServer(object):

    def __init__(self):
        # 邀请websocket集合
        self.invitesWslist = []
        # 查询websocket集合
        self.observers = []
        # 游戏的socket集合
        self.gameSocketDic={}

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
            # 邀请者返回消息
            aws = self.invitesWslist[awsindex]
            aResponse={"type":"inviteSuccess"}
            aws.send(json.dumps(aResponse))
            # 被邀请者返回消息
            bResponse={"type":"beInvited","data":inviteobj}
            bwsindex=inviteobj['bWsIndex']
            bws = self.invitesWslist[bwsindex]
            bws.send(json.dumps(bResponse))
        except WebSocketError:
            self.observers.pop(self.observers.index(ws))
            # print(ws, 'is closed')

    def agree_message(self ,responseobj):
        try:
            inviteobj=responseobj["data"]
            print(self.invitesWslist)
            awsindex=inviteobj['aWsIndex']
            print(awsindex)
            # 邀请人返回消息
            aws = self.invitesWslist[awsindex]
            aws.send(json.dumps(responseobj))
            # 被邀请人返回消息
            bwsindex=inviteobj['bWsIndex']
            bws = self.invitesWslist[bwsindex]
            bws.send(json.dumps(responseobj))
        except WebSocketError:
            # self.observers.pop(self.observers.index(ws))
            print('is closed')