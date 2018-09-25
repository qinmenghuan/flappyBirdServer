'''
    启动文件
    create by qmh 2018-03-27
'''

# 引入类库
from flask import Flask
from flask_sockets import Sockets

# 引入业务文件
from socketapi.wsapi import wsapi
from restapi.userapi import userapi
from restapi.taskapi import taskapi

app=Flask(__name__)
# 注册restapi 同一route先注册优先
app.register_blueprint(userapi)
app.register_blueprint(taskapi)

# 注册socket api
sockets = Sockets(app)
sockets.register_blueprint(wsapi)


# 启动主程序
if __name__ =="__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 8003), app, handler_class=WebSocketHandler)
    server.serve_forever()
