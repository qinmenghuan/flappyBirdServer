from geventwebsocket import WebSocketError


class MessageServer(object):

    def __init__(self):
        # websocket集合
        self.observers = []
        # 用户列表 1.名称 2.socket 3.游戏状态 4.gameindex 所在游戏局
        self.userlist=[]
        # 用户名称列表
        self.usernamelist=[]

        # 游戏列表 1.a用户 2.a用户ws 3.b用户 4.b用户ws  5.游戏状态
        self.gamelist=[]

    def add_message(self, msg):
        for ws in self.observers:
            try:
                ws.send(msg)
            except WebSocketError:
                self.observers.pop(self.observers.index(ws))
                print(ws, 'is closed')
                continue