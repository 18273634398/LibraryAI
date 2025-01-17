# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2025-01-16
# Version   ：2.0
# Description：使用阿里云智能体应用提供的插件API进行联网学习内容
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code
# ===========================================================================================================
import os
from http import HTTPStatus
from dashscope import Application
from System.settings import appID
def learnByWeb(text):
    print("[联网搜索引擎]开始搜索...")
    response = Application.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        app_id=appID,
        prompt=f'调用夸克搜索插件联网搜索{text}相关信息')

    if response.status_code != HTTPStatus.OK:
        print(f'request_id={response.request_id}')
        print(f'code={response.status_code}')
        print(f'message={response.message}')
    else:
        result = response.output.text
        print("[联网搜索引擎]搜索结果：",result)
        return result

if __name__ == '__main__':
    keyword = input("请输入搜索关键字：")
    resultDoc = learnByWeb(keyword)
