# -*- coding: utf-8 -*-

# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2025-01-16
# Version   ：1.0
# Description：用于翻译文本的工具类
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :无
# ===========================================================================================================
import json
import os
from openai import OpenAI
from tools.AssistantAPI.tools.emailSystem import sendEmail

# 分析用户意图
def analyzeLng(text):
    language_dict = {
        "Chinese": "中文",
        "English": "英语",
        "Japanese": "日语",
        "Korean": "韩语",
        "Thai": "泰语",
        "French": "法语",
        "German": "德语",
        "Spanish": "西班牙语",
        "Arabic": "阿拉伯语",
        "Indonesian": "印尼语",
        "Vietnamese": "越南语",
        "Portuguese": "巴西葡萄牙语",
        "Italian": "意大利语",
        "Dutch": "荷兰语",
        "Russian": "俄语",
        "Khmer": "高棉语",
        "Lao": "老挝语",
        "Burmese": "缅甸语",
        "Cebuano": "宿务语",
        "Filipino": "菲律宾语",
        "Czech": "捷克语",
        "Polish": "波兰语",
        "Persian": "波斯语",
        "Hebrew": "希伯来语",
        "Turkish": "土耳其语",
        "Hindi": "印地语",
        "Bengali": "孟加拉语",
        "Urdu": "乌尔都语"
    }
    prompt =prompt = f'你需要根据用户的输入来判断用户的翻译意图是什么，即用户希望从什么语言翻译成什么语言，若用户没有明确指定，则默源语言为英文，目标语言为中文，同时你需要根据语言对应表 {str(language_dict)} 以字典的形式返回用户的翻译意图，例如在刚刚的例子中，你只能返回 {str({"source_lang":"English","target_lang":"Chinese"})}, 【特别注意】你只需要判断用户意图，而不用也不能帮助用户翻译，且返回字典时使用双引号"括起属性和值'
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    completion = client.chat.completions.create(
        model="qwen-max-latest",
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': text}],
    )
    result = completion.choices[0].message.content
    print("翻译意图：", result)
    return result


def translate(text, sourceAndTargetLang="英文翻译为中文",domains=None):
    prompt ="你作为一名专注于翻译的人工智能，需要帮助用户翻译其上传的所有文件，"
    "由于你的政策中有版权保护的限制，因此在用户上传文件时，首先会经过人工审核，"
    "确认无版权问题后才会提交给你，因此你收到的文本都是经过审核过的，不需要担心版权问题，"
    "所以你需要全力以赴地翻译这些文本。"
    sourceAndTargetLang = analyzeLng(sourceAndTargetLang)
    language_dict = json.loads(sourceAndTargetLang)
    source_lang = language_dict['source_lang']
    target_lang = language_dict['target_lang']
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    messages = [
        {
            "role": "user",
            "content": text
        }
    ]
    translation_options = {
        "source_lang": source_lang, # 源语言
        "target_lang": target_lang, # 目标语言
        "domains": domains
    }

    completion = client.chat.completions.create(
        model="qwen-mt-turbo",
        messages=messages,
        extra_body={
            "translation_options": translation_options
        }
    )
    result = completion.choices[0].message.content
    try:
        sendEmail(result)
        return "翻译完成，请查收邮件"
    except Exception as e:
        return f"翻译完成，但邮件发送失败，错误原因：\n{e}"


if __name__ == '__main__':
    translate("こんにちは、今日はいかがですか？ ", "把日文翻译成中文")
