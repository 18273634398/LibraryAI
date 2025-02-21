# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-29
# Version   ：1.0
# Description：用于联网获取图书信息
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# ===========================================================================================================
import random
import re
from tools.MySQL import cmd
import requests
from bs4 import BeautifulSoup

# 随机UserAgent
userAgents = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
]

def getBookPosition(keyword):
    """获取图书在图书馆的位置"""
    result = cmd.sqlcmd(f"SELECT book_name, book_position FROM book_position WHERE book_name LIKE '%{keyword}%' LIMIT 5")
    if result:
        result = f"获取到与{keyword}相关图书的位置信息为：{result}"
    return result


def getDetailInfo(book_url):
    """获取图书详细信息"""
    Doc = []
    for url in book_url:
        headers = {
            'User-Agent': userAgents[random.randint(0, len(userAgents) - 1)],
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
        }
        response = requests.get(url, headers=headers)
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 基础信息
            baseInfo = soup.find('div', class_='book_wr')
            baseInfoItems = baseInfo.findAll('div', class_='book_item')
            baseInfo = ''
            for baseInfoItem in baseInfoItems:
                baseInfo += baseInfoItem.get_text(strip=True)
            print("[图书搜索引擎]已获取图书基本信息")
            print(url)
            # 提取详细信息
            detailInfo = soup.find('div', id='detail-info', class_='book_na_bottom show')
            detailInfoItems = detailInfo.findAll('div', class_='book_item')
            detailInfo = ''
            for detailInfoItem in detailInfoItems:
                detailInfo += detailInfoItem.get_text(strip=True)
            print("[图书搜索引擎]已获取图书详细信息")
            print(baseInfo + detailInfo) # 测试
            Doc.append(baseInfo + detailInfo)

        except Exception as e:
            print("Error:", e)
    return Doc


def getBookInfoByWeb(model, keyword):
    """以指定源模式 通过网络获取图书的URL并传给getDetailInfo()函数解析后返回图书信息文档DOoc"""
    url = f'http://find.nlc.cn/search/doSearch?query={keyword}&secQuery=&actualQuery={keyword}&searchType=2&docType=%E5%85%A8%E9%83%A8&isGroup=isGroup&targetFieldLog=%E5%85%A8%E9%83%A8%E5%AD%97%E6%AE%B5&orderBy=RELATIVE&fromHome=true'
    headers = {
        'User-Agent': userAgents[random.randint(0, len(userAgents) - 1)],
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    book_list_temp = soup.find('div', class_='article_list')
    book_list = book_list_temp.find_all('div', class_='article_item')
    # 存储指定书目的URL
    book_url = []
    # 解析每本书的URL
    def getHref(soup):
        '''传入书目的div元素，返回该书目的URL'''
        bookUrl = soup.find('a', onclick=re.compile(r'makeDetailUrl'))
        # 提取 onclick 属性值
        onclick_value = bookUrl.get('onclick')
        # 使用正则表达式提取参数
        params = re.findall(r"'(.*?)'", onclick_value)
        # 拼接 URL
        base_url = params[1]
        dataSource = params[2]
        query = params[3]
        url = f'http://find.nlc.cn/search/showDocDetails?docId={base_url}&dataSource={dataSource}&query={query}'
        return url

    # 该模式下仅仅返回第一条搜索结果（最近似）
    if model == 1:
        book_url.append(getHref(book_list[0]))
    elif model == 2:
        # 该模式下返回前3条搜索结果
        for book in book_list[0:3]:
            book_url.append(getHref(book))
    Doc = getDetailInfo(book_url)
    if Doc:
        print("[图书搜索引擎]已获取图书信息")
        positionInfo = getBookPosition(keyword)
        if positionInfo:
            Doc.append(positionInfo)
        return Doc
    else:
        print("未找到相关图书")
        return "未找到相关图书"




def getBookInfo(model,text):
    """获取指定图书的详细信息(包括作者、标识号或ISBN号、出版地或发行地、关键词、语种、分类、载体形态等)"""
    try:
        print(f"[图书搜索引擎]正在搜索{text}相关图书信息")
        result = getBookInfoByWeb(model,text)
        return result
    except Exception as e:
        return f"服务器错误，原因:{e}"

# 预约图书或归还图书 当model=0时为归还
def reserveBook(book_name, model=1):
    from System.settings import host, user, password, database
    import pymysql
    """预约图书或归还图书"""
    try:
        # 连接到 MySQL 数据库
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            if model == 1:  # 预约图书
                # 查询书的剩余数目
                query = "SELECT book_number FROM book_position WHERE book_name = %s"
                cursor.execute(query, (book_name,))

                # 获取查询结果
                result = cursor.fetchone()

                if result :
                    book_number = result['book_number']

                    if book_number > 0:  # 如果有书可以借
                        # 将剩余数目减 1
                        update_query = "UPDATE book_position SET book_number = book_number - 1 WHERE book_name = %s"
                        cursor.execute(update_query, (book_name,))

                        # 提交事务
                        connection.commit()
                        cmd.sqlcmd(f"INSERT INTO library_operations(operation_type, content) VALUES ('借书','{book_name}')")
                        return f"已成功借阅{book_name}"
                    else:
                        cmd.sqlcmd(f"INSERT INTO library_operations(operation_type, content) VALUES ('异常','无法借阅{book_name}，原因：暂无多余可借阅图书，该书的所有书籍均已被借出')")
                        return f"借阅{book_name}失败，原因：当前暂无多余可借阅图书，该书的所有书籍均已被借出"
                else:
                    cmd.sqlcmd(f"INSERT INTO library_operations(operation_type, content) VALUES ('异常','用户无法借阅{book_name}，原因是这本书暂时未入库')")
                    return f"借阅{book_name}失败，该图书暂未入库，请等待管理员添加"

            elif model == 0:  # 归还图书
                # 增加书的数量
                update_query = "UPDATE book_position SET book_number = book_number + 1 WHERE book_name = %s"
                cursor.execute(update_query, (book_name,))

                # 提交事务
                connection.commit()
                cmd.sqlcmd(f"INSERT INTO library_operations(operation_type, content) VALUES ('还书','{book_name}')")
                return f"已成功归还{book_name}"

            else:
                print("Invalid model value. Use 1 for borrowing and 0 for returning.")
                return f"归还图书{book_name}失败，原因：无效的操作类型"

    except pymysql.MySQLError as error:
        print("Error while connecting to MySQL", error)
        return False
    finally:
        if connection:
            connection.close()
            print("MySQL connection is closed")


if __name__ == '__main__':
    # getBookInfoByWeb(1, '三体')
    # print(getBookPosition('三体'))
    # getBookInfoPlus('三体',10)
    reserveBook('三体',0)

