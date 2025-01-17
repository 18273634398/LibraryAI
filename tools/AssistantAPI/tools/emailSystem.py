# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2025-01-16
# Version   ：1.0
# Description：用于发送电子邮件
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# ===========================================================================================================
import requests
from System.settings import authorizationCode,senderEmail
from datetime import datetime
def sendEmail(text,title = '文献翻译结果',name='智库书韵',addressEmail='2209030006@stu.hutb.edu.cn'):
    text = generate_email(text, datetime.now())
    url = "http://api.mmp.cc/api/mail"
    # 请求参数
    params = {
        "email": senderEmail,
        "key": authorizationCode,
        "mail": "2209030006@stu.hutb.edu.cn",  # 收件邮箱
        "title": title,
        "name": name,
        "text": text
    }

    # 发送GET请求
    response = requests.get(url, params=params)

    # 检查响应状态
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "success":
            print("邮件发送成功")
        else:
            print("邮件发送失败，错误信息：", result["message"])
    else:
        print("请求失败，状态码：", response.status_code)
    return "邮件引擎被成功调用"



def generate_email(translation_text, date):
    email_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>信纸</title>
    <style>
        body {{
            font-family: 'Courier New', Courier, monospace;
            background-color: #f0e6d2; /* 信纸背景颜色 */
            margin: 0;
            padding: 0;
        }}
        .letter {{
            width: 80%;
            margin: 50px auto;
            background-color: #fff; /* 信纸主体颜色 */
            border: 1px solid #ccc;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            position: relative;
        }}
        .letter::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://example.com/letter-texture.jpg'); /* 信纸纹理图片 */
            background-size: cover;
            opacity: 0.2;
            z-index: -1;
        }}
        .letter-header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .letter-header h1 {{
            font-size: 24px;
            color: #333;
            margin: 0;
        }}
        .letter-header p {{
            font-size: 16px;
            color: #666;
            margin: 5px 0 0;
        }}
        .letter-body {{
            font-size: 18px;
            line-height: 1.6;
            color: #333;
            margin-bottom: 20px;
        }}
        .letter-footer {{
            text-align: right;
            margin-top: 20px;
        }}
        .letter-footer p {{
            font-size: 18px;
            color: #333;
        }}
    </style>
</head>
<body>
<div class="letter">
    <div class="letter-header">
        <h1>智库书韵用户</h1>
        <p>{date}</p>
    </div>
    <div class="letter-body">
        <p>你好！</p>
        <p>以下是你的文献翻译结果</p>
        <p>{translation_text}</p>
    </div>
    <div class="letter-footer">
        <p>智库书韵</p>
    </div>
</div>
</body>
</html>
"""
    return email_content


if __name__ == '__main__':
    text ="你好，这是一封测试邮件。"
    sendEmail(text)



