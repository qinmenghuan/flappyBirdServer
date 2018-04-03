'''
    邀请处理类
    create by qmh 2018-03-29
'''

from geventwebsocket import WebSocketError
import json


class InviteServer(object):

    def __init__(self):
        # 邀请socket 键值对
        self.invite_socket_dic = {}

        # 邀请键值对
        self.invite_dic = {}

        # 游戏键值对
        self.game_dic = {}

    # 发送邀请消息
    def invite_message(self, receive_data):
        try:
            aTelephone = receive_data['aTelephone']
            bTelephone = receive_data["bTelephone"]
            aSocket = self.invite_socket_dic[aTelephone]
            bSocket = self.invite_socket_dic[bTelephone]
            # 邀请者返回消息
            aResponse = {"type": "Invite", "response_code": "200"}
            aSocket.send(json.dumps(aResponse))
            # 被邀请者返回消息
            bResponse = {"type": "beInvited", "response_code": "200", "response_data": receive_data}
            bSocket.send(json.dumps(bResponse))
        except WebSocketError:
            # self.observers.pop(self.observers.index(ws))
            print(aSocket, 'is closed')
            print(bSocket, 'is closed')

    def agree_message(self, receive_data):
        try:
            aTelephone = receive_data["aTelephone"]
            bTelephone = receive_data["bTelephone"]
            response = {"type": "Agree", "response_code": "200", "response_data": receive_data}

            # 邀请人返回消息
            aSocket = self.invite_socket_dic[aTelephone]
            aSocket.send(json.dumps(response))

            # 被邀请人返回消息
            bSocket = self.invite_socket_dic[bTelephone]
            bSocket.send(json.dumps(response))

        except WebSocketError:
            # self.observers.pop(self.observers.index(ws))
            print('is closed')
