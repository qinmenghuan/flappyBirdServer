'''
    启动文件
    create by qmh 2018-03-27
'''

from flask import Flask
from restapi.UserApi import user_api

app=Flask(__name__)
app.register_blueprint(user_api)

@app.route("/")
def hello():
    return "Hello World!"

# 启动主程序
if __name__ =="__main__":
    app.run(debug=True)
