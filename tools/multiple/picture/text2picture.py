from http import HTTPStatus
import requests
from dashscope import ImageSynthesis
import os
from System.settings import generatedImageURL

def text2picture(text):
    def async_call(text):
        print('----create task----')
        task_info = create_async_task(text)
        print('----wait task done then save image----')
        wait_async_task(task_info)


    # 创建异步任务
    def create_async_task(text):
        rsp = ImageSynthesis.async_call(api_key=os.getenv("DASHSCOPE_API_KEY"),
                                        model="wanx2.1-t2i-turbo",
                                        prompt=text,
                                        n=1,
                                        size='1024*1024')
        print(rsp)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))
        return rsp


    # 等待异步任务结束
    def wait_async_task(task):
        rsp = ImageSynthesis.wait(task)
        print(rsp)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output)
            for result in rsp.output.results:
                with open(generatedImageURL, 'wb+') as f:
                    f.write(requests.get(result.url).content)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))

    try:
        async_call(text)
        return f"文生图生成完成，路径为{generatedImageURL}"
    except Exception as e:
        return f"文生图生成失败,原因:{e}"

if __name__ == '__main__':
    # text2picture('文生图的文本描述')
    print("正在测试文生图")