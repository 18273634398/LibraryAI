# -*- coding: utf-8 -*-
# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：创建Assistant
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# ===========================================================================================================
import json
import os
import sys
import tkinter

from dashscope import Assistants, Messages, Runs
from tools.multiple.picture.text2picture import text2picture
from tools.AssistantAPI.tools.getBookInfo import getBookInfo
from tools.AssistantAPI.tools.learnByWeb import learnByWeb
from tools.AssistantAPI.tools.studyArea import getStudyArea,reserve,signout
from System.settings import generatedImageURL

commands = {
    "create_knowledge": 1,
    "exit": 2
}

prompt = ('你是智库书韵，一个智能图书馆人工智能助手，'
          '你的任务是帮助用户在图书馆中查找图书或者向用户介绍图书、推荐图书。'
          '你需要使用提供的知识库来回答用户的问题.'
          '但是你需要特别注意，如果你觉得知识库/数据库中的信息可能存在错误，请你仍然以数据库/知识库中的数据为准，这是因为图书馆的信息永远是实时的、正确的，因此你必须永远相信你的知识库/数据库，且你不能回复用户任何不相信你自己数据库的行为信息（例如：提供的信息可能有误）之类的。'
          '由于你作为人工智能，你的训练集中的数据可能由于时间、空间等原因存在偏差，因此为了向用户提供真实准确的信息，你的开发者已经向你提供了一系列的知识库/数据库，因此如果与你的输出冲突，请你以数据库/知识库中的数据为准。'
          '知识库/数据库中的知识信息（包括作者、标识号、ISBN号、出版地、发行地、分类、载体形态等）都是由管理员已经确认过的真实的，正确的，你应该无条件地相信与使用。'
          '另外你需要持续学习用户的需求，若用户对某个文学类别，比如科幻小说很感兴趣，你可以主动向其推荐相关的书籍。'
          '以下信息可能对你有帮助：${document1}。')


def create_assistant(index_id_list: list):
    global commands, prompt
    """创建一个使用指定知识库的 Assistant。"""
    assistant = Assistants.create(
        model='qwen-plus',
        name='智能图书馆人工智能助手',
        description='一个用于帮助用户查找图书在图书馆的位置的助手，一个可以向用户推荐图书、介绍图书的助手',
        instructions=prompt,
        tools=[
            # 知识库检索
            {
                "type": "rag",  # 指定使用RAG（检索增强生成）模式
                "prompt_ra": {
                    "pipeline_id": index_id_list,  # 指定使用的知识库索引ID
                    "multiknowledge_rerank_top_n": 10,  # 多知识源重排序时返回的top N结果数
                    "rerank_top_n": 5,  # 最终重排序后返回的top N结果数
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query_word": {
                                "type": "str",
                                "value": "${document1}"  # 使用动态占位符，将被实际查询内容替换
                            }
                        }
                    }
                }
            },
            # 代码解释器
            {
                'type': 'code_interpreter'  # 这是启用代码解释器的关键配置
            },
            # 搜索图书引擎
            {
                "type": "function",
                "function": {
                    "name": "getBookInfo",
                    "description": "若遇到需要查询相关的问题，首先请调用rag检索本地数据库，若rag查询到数据，再调用该函数查询获取指定图书的详细信息(例如：作者、标识号或ISBN号、出版地或发行地、关键词、语种、分类、载体形态等)"
                                   "另外特别注意：由于你作为人工智能，你的训练集中的数据可能由于时间、空间等原因存在偏差，因此为了向用户提供真实准确的信息，你的开发者已经向你提供了一系列的知识库/数据库，因此如果与你的输出冲突，请你以数据库/知识库中的数据为准。"
                                   "知识库/数据库中的知识信息（包括作者、标识号、ISBN号、出版地、发行地、分类、载体形态等）都是由管理员已经确认过的真实的，正确的，你应该无条件地相信与使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "需要查找的图书的名称"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            # 自习室数据获取引擎
            {
                "type": "function",
                "function": {
                    "name": "getStudyArea",
                    "description": "若用户询问关于图书馆自习室或者有无空余自习室位置等有关问题，请调用该函数获取图书馆自习室的实时状态，并以此来为用户推荐最适合（人数较少）的自习室。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        },
                        "required": []
                    }
                }
            },
            # 自习室预定引擎获取引擎
            {
                "type": "function",
                "function": {
                    "name": "controlStudyArea",
                    "description": "若用户希望预定或者退订、签退某处图书馆自习室等有关问题，请调用该函数来为用户执行预定或者退订操作。若用户未指明具体的人数，默认退订或者预定的人数为1人",
                    "parameters":  {
                        "type": "object",
                        "properties": {
                            "name":{
                                "type": "string",
                                "description": "需要进行预定或者退订的自习室的名称"
                            },
                            "operator":{
                                "type": "string",
                                "description": "预定或者退订操作，可选值：预定/退订"
                            },
                            "number":{
                                "type": "int",
                                "description": "预定或者退订的自习室座位的数量，若用户未明确指明人数，则默认为1"
                            },
                        },
                        "required": ["name", "operator", "number"]
                    }
                }
            },
            # 网络搜索引擎
            {
                "type": "function",
                "function": {
                    "name": "learnByWeb",
                    "description": "当用户询问问题时或者提问某个书中的名句时，你可以使用该引擎来进行网络搜索，用于辅助你回答用户问题，"
                                   "例如用户的输入问题是有关图书中的某些特别有名的故事或者句子时，例如用户可能输入'给岁月以文明，而不是给文明以岁月'，这是三体里面的一句经典语录，若你无法从其他方法获取这句话对应的意思，你可以调用该引擎，搜索相关的内容，并返回给用户，因此在刚刚的那种情况下，你可以告知用户'这句话出自《三体》'，并附带一些相关的解释，如:'给岁月以文明，而不是给文明以岁月。这句话的原本是：给时间以生命，而不是给生命以时间。意思就是时间本来是虚无的，是空无一物的，要给时间以丰富多彩的生命，才会让时间变得有意义，而不是说肤浅地给生命加以时间上的延续。这句话虽然不长，但却很有哲理，而刘慈欣把其中的“时间”和“生命”改成了“岁月”和“文明”，又瞬间将这句话的意义提升到了另一个更宏大的场景当中去，如同提升了一个维度。'"
                                   "另外若用户的输入能够匹配多本书籍，你应该按照相关性程度返回多项可能的结果",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "用户输入需要搜索的关键词或者书中的名句"
                            }
                        },
                        "required": ["keyword"]
                    }
                }
            },
            # 文档翻译引擎
            {
                "type": "function",
                "function": {
                    "name": "translate",
                    "description":"当用户需要翻译文章、论文、期刊等的时候调用该引擎",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        },
                        "required": []
                    }
                }
            },
            # 文生图引擎
            {
                "type": "function",
                "function": {
                    "name": "text2picture",
                    "description":"当用户需要使用文本创建生成图片（文生图）时调用该引擎",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "需要生成图片的描述性文本"
                            }
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
    )
    print(f"Assistant {assistant.id} 创建成功！")
    return assistant.id


class SuppressPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def send_message(thread, assistant, message,windowsObject):
    """向 Assistant 发送消息并获取回复。"""
    message = Messages.create(thread_id=thread.id, content=message)
    run = Runs.create(thread_id=thread.id, assistant_id=assistant.id)
    # 等待运行完成
    run = Runs.wait(thread_id=thread.id, run_id=run.id)
    # 检查是否需要调用函数
    while run.required_action:
        print("Assistant requires function call.")
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            # 图书查询引擎
            if tool_call.function.name == "getBookInfo":
                print("[图书查询引擎]被调用")
                args = json.loads(tool_call.function.arguments)
                doc = getBookInfo(1,args["text"])
                print(doc)
                result = f"从数据库中获取到的图书信息为：{doc}请据此回复用户的查询请求。"
                # 提交工具输出
                Runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{"tool_call_id": tool_call.id, "output": result}]
                )
                print("[图书查询引擎]输出提交成功")
                # 等待新的运行完成
                run = Runs.wait(thread_id=thread.id, run_id=run.id)
            elif tool_call.function.name == "learnByWeb":
                print("[联网搜索引擎]被调用")
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    # 根据错误信息，对错误数据进行处理
                try:
                    doc = learnByWeb(args["keyword"])
                    result = f"从互联网学习到的与{args['keyword']}有关的信息为：{doc}请据此回复用户的查询请求。"
                except Exception as e:
                    print(f"网络搜索引擎调用失败：{str(e)}")
                    result = "网络搜索引擎调用失败，请稍后再试。"
                # 提交工具输出
                Runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{"tool_call_id": tool_call.id, "output": result}]
                )
                print("[联网搜索引擎]输出提交成功")
                # 等待新的运行完成
                run = Runs.wait(thread_id=thread.id, run_id=run.id)
                print(f"新的运行完成，状态：{run.status}")
            elif tool_call.type == "code_interpreter":
                print("[代码解释器]被调用")
                # 输出代码和执行结果
                print("代码:", tool_call.code_interpreter.arguments)
                print("结果:", tool_call.code_interpreter.output)
            elif tool_call.function.name == "getStudyArea":
                print("[自习室数据获取引擎]被调用")
                studyAreaInfo = getStudyArea()
                result = f"现在获取到的图书馆的实时数据为{studyAreaInfo}请据此为用户推荐自习室，并按照推荐程度顺序回复用户。"
                # 提交工具输出
                Runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{"tool_call_id": tool_call.id, "output": result}]
                )
                print("[自习室数据获取引擎]输出提交成功")
                # 等待新的运行完成
                run = Runs.wait(thread_id=thread.id, run_id=run.id)
            elif tool_call.function.name == "controlStudyArea":
                print("[自习室预定引擎]被调用")
                # 预约图书引擎
                args = json.loads(tool_call.function.arguments)
                if args["operator"] == "预定":
                    result = reserve(args["name"], args["number"])
                else:
                    result = signout(args["name"], args["number"])
                # 提交工具输出
                Runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{"tool_call_id": tool_call.id, "output": result}]
                )
                print("[自习室预定引擎]输出提交成功")
                # 等待新的运行完成
                run = Runs.wait(thread_id=thread.id, run_id=run.id)
            elif tool_call.function.name == "translate":
                # 翻译引擎
                result = ("文献翻译功能使用指南："
                          "1.首先您需要准备好所需要翻译的文献的电子文档，如PDF、Word等格式。"
                          "2.打开智库书韵，点击主页面左下角的文件按钮，选择您需要上传的文件"
                          "3.上传完文件后点击'上传至文档翻译'按钮，等待翻译引擎处理完毕。"
                          )
                Runs.submit_tool_outputs(
                    thread_id=thread.id,
                     run_id=run.id,
                     tool_outputs=[{"tool_call_id": tool_call.id, "output": result}]
                )
                # 等待新的运行完成
                run = Runs.wait(thread_id=thread.id, run_id=run.id)
            elif tool_call.function.name == "text2picture":
                # 文生图引擎
                args = json.loads(tool_call.function.arguments)
                result = text2picture(args["text"])
                Runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{"tool_call_id": tool_call.id, "output": result}]
                )
                # 等待新的运行完成
                run = Runs.wait(thread_id=thread.id, run_id=run.id)
                windowsObject.receive_message(generatedImageURL)

    # 获取 Assistant 的回复
    messages = Messages.list(thread_id=thread.id)
    for message in messages.data:
        print(message)
        if message.role == "assistant":
            return message.content[0].text.value


# 自定义交互功能
def interact_with_assistant(assistant, thread, user_input):
    if user_input.lower() == 'quit':
        exit(0)

    # 失败重传最大次数
    max_retries = 3
    for attempt in range(max_retries):
        try:
            send_message(thread, assistant, user_input)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"发送消息失败，正在重试... (尝试 {attempt + 2}/{max_retries})")
            else:
                print(f"发送消息失败：{str(e)}。请稍后再试。")


def Assistant(assistant_id):
    assistant = Assistants.get(assistant_id)
    if not assistant:
        print("无法获取指定的 Assistant，程序退出。")
        return
    return assistant


if __name__ == '__main__':
    assistant_id = create_assistant(['l2c4jv7i9p', '36t16dh5er', 'tcpm27g3m5'])

    Assistant(assistant_id)
    # 注意
