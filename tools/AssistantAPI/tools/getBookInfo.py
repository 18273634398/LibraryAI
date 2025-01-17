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
            # 提取详细信息
            detailInfo = soup.find('div', id='detail-info', class_='book_na_bottom show')
            detailInfoItems = detailInfo.findAll('div', class_='book_item')
            detailInfo = ''
            for detailInfoItem in detailInfoItems:
                detailInfo += detailInfoItem.get_text(strip=True)
            print("[图书搜索引擎]已获取图书详细信息")
            Doc.append(baseInfo + detailInfo)

        except Exception as e:
            print("Error:", e)
    return Doc


def getBookInfoByWeb(model, keyword, source = 1):
    """以指定源模式 通过网络获取图书的URL并传给getDetailInfo()函数解析后返回图书信息文档DOoc"""
    if source == 1:
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

        # 以书名的形式查找
        # 该模式下仅仅返回第一条搜索结果（最近似）
        if model == 1:
            book_url.append(getHref(book_list[0]))
        elif model == 2:
            # 以作者的形式查找
            # 该模式下返回前10条搜索结果
            for book in book_list[0:10]:
                book_url.append(getHref(book))
        Doc = getDetailInfo(book_url)
        if Doc:
            print("[图书搜索引擎]已获取图书信息")
            return Doc
        else:
            print("未找到相关图书")
            return "未找到相关图书"
    # elif source == 2:
    #     # 使用其他源用于进行模糊搜索并提取ISBN号
    #     url = f'https://search.datacdn.cn/sbooklist?name=pdfrsteam&q={keyword}=_all'
    #     headers = {
    #         'User-Agent': userAgents[random.randint(0, len(userAgents) - 1)],
    #         'Connection': 'keep-alive',
    #         'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
    #     }
    #     response = requests.get(url, headers=headers)
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     book_list = soup.find('div', class_='pay-content shadowbox').find('div', class_='intro')
    #     book_list_items = book_list.findAll('div', class_='content')






def getBookInfo(model,text,retries=False):
    """获取指定图书的详细信息(包括作者、标识号或ISBN号、出版地或发行地、关键词、语种、分类、载体形态等)"""
    # retries: 是否因为准确搜索导致无结果发起重试过
    try:
        print(f"[图书搜索引擎]正在搜索{text}相关图书信息")
        result = getBookInfoByWeb(model,text)
        return result
    except Exception as e:
        # try:
        #     if  "'NoneType'" in str(e) and retries == False:
        #         print(f"[图书搜索引擎]换源搜索{text}相关图书信息")
        #         result = getBookInfoByWeb(model,text,2)
        #         return result
        # except Exception as e:
        #     return f"服务器错误，原因:{e}"
        return f"服务器错误，原因:{e}"

if __name__ == '__main__':
    getBookInfoByWeb(1, '刘慈欣')
