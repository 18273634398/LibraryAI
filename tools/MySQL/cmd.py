import pymysql
from System import settings


def connectToMySQL():
    # 创建数据库连接
    print("【连接数据库】")
    try:
        connection = pymysql.connect(host=settings.host,
                                     user=settings.user,
                                     password=settings.password,
                                     database=settings.database,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        print("数据库连接成功")
        return connection
    except:
        print("数据库连接失败")
        return None


def showDataBases(connect=None):
    print("【获取数据库列表】")
    if connect == None:
        connect = connectToMySQL()
    try:
        with connect.cursor() as cursor:
            # 执行SQL语句
            sql = "SHOW DATABASES"
            cursor.execute(sql)
            # 获取查询结果
            result = cursor.fetchall()
            # 打印结果
            print("数据库列表：")
            for row in result:
                print(row)
            return result
    finally:
        # 使用完连接后放回连接池
        connect.close()

def createDatabase(databaseName,connect=None):
    print("【创建数据库】")
    if connect == None:
        connect = connectToMySQL()
    try:
        with connect.cursor() as cursor:
            # 执行SQL语句
            sql = "CREATE DATABASE IF NOT EXISTS %s"
            cursor.execute(sql, (databaseName,))
            # 提交事务
            connect.commit()
            print("数据库创建成功")
    finally:
        # 使用完连接后放回连接池
        connect.close()

def sqlcmd(sqlcmd,connect=None):
    print(f"【执行指定SQL语句】\n{sqlcmd}")
    if connect == None:
        connect = connectToMySQL()
    try:
        with connect.cursor() as cursor:
            # 执行SQL语句
            cursor.execute(sqlcmd)
            connect.commit()
            # 获取查询结果
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(f"执行SQL语句失败：{e}")
    finally:
        # 使用完连接后放回连接池
        print("【关闭数据库连接】")
        connect.close()

if __name__ == '__main__':
    sqlcmd("show databases;")