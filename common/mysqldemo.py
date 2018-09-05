# coding:utf-8

'''
    数据库操作类
    create by qmh 2018-03-23
'''

import pymysql

# 全局变量- 本地数据库
# CONNECT_TIMEOUT=100
# IP='localhost'
# PORT=3306
# USER='root'
# PASSWORD='root'
# DBNAME="qmh"

# 全局变量- 服务器数据库
CONNECT_TIMEOUT=100
IP='47.98.129.66'
PORT=3306
USER='root'
PASSWORD='Qin774658293+'
DBNAME="qmh"


# 异常处理
class QueryException (Exception):
    ''''''

# 连接异常
class ConnctionException (Exception):
    ''''''

# mysql的操作类
class MySQL_Utils():
    # 构造函数
    def __init__(self,ip=IP,port=PORT,user=USER,password=PASSWORD,connect_timeout=CONNECT_TIMEOUT,
                 remote=False,  dbname=DBNAME):
        self.__conn=None
        self.__cursor=None
        self.lastrowid=None
        self.connect_timeout = connect_timeout
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.remote = remote
        self.dbname = dbname
        self.rows_affected = 0

    #  连接数据库初始化方法
    def __init_conn(self):
        try:
            # 数据库连接
            conn = pymysql.connect(
                host=self.ip,
                port=int(self.port),
                user=self.user,
                password=self.password,
                db=self.dbname,
                connect_timeout=self.connect_timeout,
                charset='utf8')

        except pymysql.Error as e:
            raise ConnctionException(e)
        self.__conn=conn

    # 初始化游标方法
    def __init_cursor(self):
        if self.__conn:
            self.__cursor=self.__conn.cursor(pymysql.cursors.DictCursor)

    # 关闭数据库连接
    def close(self):
        if self.__conn:
            self.__conn.close()
            self.__conn=None;

    # 专门处理select语句
    def exec_sql(self,sql,args=None):
        try:
            if self.__conn is None:
                self.__init_conn()
                self.__init_cursor()
            self.__conn.autocommit =True
            self.__cursor.execute(sql,args)
            self.rows_affected=self.__cursor.rowcount
            results =self.__cursor.fetchall()
            return results

        except pymysql.Error as e:
            raise pymysql.Error(e)
        finally:
            if self.__conn:
                self.close()

    # 专门处理dml语句 delete,update ,insert
    def exec_txsql(self,sql,args=None):
        try:
            if self.__conn is None :
                self.__init_conn()
                self.__init_cursor()
            if self.__cursor is None:
                self.__init_cursor()
            self.rows_affected=self.__cursor.execute(sql,args)
            # 提交执行
            self.__conn.commit()
            return self.rows_affected
        except pymysql.Error as e:
            raise  pymysql.Error(e)
        finally:
            if self.__cursor:
                self.__cursor.close()
                self.__cursor=None


