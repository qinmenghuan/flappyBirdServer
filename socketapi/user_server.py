from geventwebsocket import WebSocketError
import json


class UserServer(object):

    def __init__(self):
        # 用户socket 键值对
        self.user_socket_dic = {}

        # 用户列表
        '''
            telephone:
            gameid: 没则-1
            user_status：用户的状态 0 未开始  1 邀请中  2游戏中  3 游戏结束
        '''
        self.user_list_dic = {}

    def get_user_list(self):
        userlist=[]
        for key in list(self.user_list_dic.keys()):
        # dictionary遍历时候不能修改，不然会报错
        # for key in self.user_list_dic:
            userlist.append(self.user_list_dic[key])
        return userlist

    # 全局发送用户列表消息
    def send_all_users(self):
        user_list = self.get_user_list()
        for key in list(self.user_list_dic.keys()):
            try:
                response_dic = {"type": "Search", "response_code": "200", "response_msg": "",
                                "response_data": user_list }
                self.user_socket_dic[key].send(json.dumps(response_dic))
            except WebSocketError:
                # self.observers.pop(self.observers.index(ws))
                # print(self., 'is closed')
                # 删除该socket
                del self.user_socket_dic[key]
                # 删除该用户
                del self.user_list_dic[key]
                continue
