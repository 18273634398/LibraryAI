# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-25
# Version   ：1.0
# Description：用于上传本地文件到知识库
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# 仅支持非结构化文件(如doc、docx、ppt、pptx、pdf、txt等)上传到知识库
# 注意上传文件时需要携带其文件后缀(.doc)
# ===========================================================================================================

import os
import hashlib
import requests
import time
from alibabacloud_bailian20231229.client import Client as bailian20231229Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_util import models as util_models
from dashscope import Assistants, Messages, Runs, Threads
import sys

# 构建本地数据库并上传一份文件到该知识库
# 参数：文件路径，数据库名，类别ID（包含服务框架/藏书信息）
def create_knowledge(file_path: str, kb_name: str='藏书信息' , category_id: str='藏书信息') -> str:
    # 第一步：检查并提示设置必要的环境变量
    check_environment_variables()
    # 第二步：创建知识库
    index_id = create_knowledge_base(kb_name,file_path,category_id )
    if not index_id:
        print("知识库创建失败，程序退出。")
        return ''
    print(f"知识库创建成功，索引ID为：{index_id}")
    return index_id



# 检查并提示设置必要的环境变量
def check_environment_variables():
    required_vars = {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': '阿里云访问密钥ID',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': '阿里云访问密钥密码',
        'DASHSCOPE_API_KEY': '百炼API密钥',
        'WORKSPACE_ID': '百炼工作空间ID'
    }
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(var)
            print(f"错误：请设置 {var} 环境变量 ({description})")
    if missing_vars:
        print("\n您可以使用以下命令设置环境变量：")
        for var in missing_vars:
            print(f"export {var}='您的{required_vars[var]}'")
        return False
    return True



# 创建并返回阿里云客户端用于后续调用API
def create_client() -> bailian20231229Client:
    config = open_api_models.Config(
        access_key_id=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'),
        access_key_secret=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    )
    config.endpoint = 'bailian.cn-beijing.aliyuncs.com'
    return bailian20231229Client(config)

# 计算文件的 MD5 哈希值
def calculate_md5(file_path: str) -> str:
    """
    参数:
        file_path (str): 文件路径
    返回:
        str: 文件的 MD5 哈希值
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# 获取文件大小（以字节为单位）
def get_file_size(file_path: str) -> int:
    """
    参数:
        file_path (str): 文件路径。
    返回:
        int: 文件大小（以字节为单位）。
    """
    return os.path.getsize(file_path)

# 从阿里云百炼服务申请文件上传租约，申请成功后得到用于上传文件的临时请求头和临时URL
def apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id):
    """
    参数:
        client (bailian20231229Client): 阿里云百炼客户端。
        category_id (str): 类别 ID。
        file_name (str): 文件名称。
        file_md5 (str): 文件的 MD5 哈希值。
        file_size (int): 文件大小（以字节为单位）。
        workspace_id (str): 业务空间 ID。
    返回:
        阿里云百炼服务的响应。
    """
    headers = {}
    request = bailian_20231229_models.ApplyFileUploadLeaseRequest(
        file_name=file_name,
        md_5=file_md5,
        size_in_bytes=file_size,
    )
    runtime = util_models.RuntimeOptions()
    return client.apply_file_upload_lease_with_options(category_id, workspace_id, request, headers, runtime)

# 利用申请的租约上传文件到阿里云百炼服务
def upload_file(lease_id, upload_url, headers, file_path):
    """
    参数:
        lease_id (str): 租约 ID。
        upload_url (str): 上传 URL。
        headers (dict): 上传请求的头部。
        file_path (str): 文件路径。
    """
    with open(file_path, 'rb') as f:
        file_content = f.read()
    upload_headers = {
        "X-bailian-extra": headers["X-bailian-extra"],
        "Content-Type": headers["Content-Type"]
    }
    response = requests.put(upload_url, data=file_content, headers=upload_headers)
    response.raise_for_status()

# 将文件添加到阿里云百炼服务。
def add_file(client: bailian20231229Client, lease_id: str, parser: str, category_id: str, workspace_id: str):
    """
    参数:
        client (bailian20231229Client): 阿里云百炼客户端。
        lease_id (str): 租约 ID。
        parser (str): 用于文件的解析器。
        category_id (str): 类别 ID。
        workspace_id (str): 业务空间 ID。
    返回:
        阿里云百炼服务的响应。
    """
    headers = {}
    request = bailian_20231229_models.AddFileRequest(
        lease_id=lease_id,
        parser=parser,
        category_id=category_id,
    )
    runtime = util_models.RuntimeOptions()
    return client.add_file_with_options(workspace_id, request, headers, runtime)

# 在阿里云百炼服务中描述文件。
def describe_file(client, workspace_id, file_id):
    """
    参数:
        client (bailian20231229Client): 阿里云百炼客户端。
        workspace_id (str): 业务空间 ID。
        file_id (str): 文件 ID。
    返回:
        阿里云百炼服务的响应。
    """
    headers = {}
    runtime = util_models.RuntimeOptions()
    return client.describe_file_with_options(workspace_id, file_id, headers, runtime)

# 为文件在阿里云百炼服务中创建知识库索引。
def create_index(client, workspace_id, file_id, name, structure_type, source_type, sink_type):
    """
    参数:
        client (bailian20231229Client): 阿里云百炼客户端。
        workspace_id (str): 业务空间 ID。
        file_id (str): 文件 ID。
        name (str): 知识库索引名称。
        structure_type (str): 知识库的数据类型。
        source_type (str): 数据管理的数据类型。
        sink_type (str): 知识库的向量存储类型。、
    返回:
        阿里云百炼服务的响应。
    """
    headers = {}
    request = bailian_20231229_models.CreateIndexRequest(
        structure_type=structure_type,
        name=name,
        source_type=source_type,
        sink_type=sink_type,
        document_ids=[file_id]
    )
    runtime = util_models.RuntimeOptions()
    return client.create_index_with_options(workspace_id, request, headers, runtime)

# 向阿里云百炼服务提交索引任务。
def submit_index(client, workspace_id, index_id):
    """
    参数:
        client (bailian20231229Client): 阿里云百炼客户端。
        workspace_id (str): 业务空间 ID。
        index_id (str): 索引 ID。
    返回:
        阿里云百炼服务的响应。
    """
    headers = {}
    submit_index_job_request = bailian_20231229_models.SubmitIndexJobRequest(
        index_id=index_id
    )
    runtime = util_models.RuntimeOptions()
    return client.submit_index_job_with_options(workspace_id, submit_index_job_request, headers, runtime)

# 获取阿里云百炼服务中索引任务的状态。
def get_index_job_status(client, workspace_id, job_id, index_id):
    """
    参数:
        client (bailian20231229Client): 阿里云百炼客户端。
        workspace_id (str): 业务空间 ID。
        job_id (str): 任务 ID。
        index_id (str): 索引 ID。
    返回:
        阿里云百炼服务的响应。
    """
    headers = {}
    get_index_job_status_request = bailian_20231229_models.GetIndexJobStatusRequest(
        index_id=index_id,
        job_id=job_id
    )
    runtime = util_models.RuntimeOptions()
    return client.get_index_job_status_with_options(workspace_id, get_index_job_status_request, headers, runtime)

# 使用阿里云百炼服务创建索引知识库。
def create_knowledge_base(
        name:str,
        file_path: str,
        category_id: str ='default'
):
    """
    参数:
        name (str): 知识库名称。
        file_path (str): 文件路径。
        category_id (str): 类别 ID。(包含服务框架/藏书信息）
    返回:
        str or None: 如果成功，返回索引 ID；否则返回 None。
    """
    # 目录ID转化
    if category_id == '藏书信息':
        category_id = 'cate_5be67d62713c407a83e809f3211f2460_10563706'
    elif category_id == '服务框架':
        category_id = 'cate_0172568f98174f13869004072b7ba863_10563706'
    else:
        category_id = 'cate_bf68f2d79b0c44e69ce7645e2a0b7aad_10563706'
    # 设置默认值
    workspace_id = os.environ.get('WORKSPACE_ID')
    parser = 'DASHSCOPE_DOCMIND'
    source_type = 'DATA_CENTER_FILE'
    structure_type = 'unstructured'
    sink_type = 'DEFAULT'

# try:
    # 步骤1：创建客户端
    client = create_client()

    # 步骤2：准备文件信息
    file_name = os.path.basename(file_path)
    file_md5 = calculate_md5(file_path)
    file_size = get_file_size(file_path)

    # 步骤3：申请上传租约
    lease_response = apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id)
    print(lease_response)
    lease_id = lease_response.body.data.file_upload_lease_id
    upload_url = lease_response.body.data.param.url
    upload_headers = lease_response.body.data.param.headers

    # 步骤4：上传文件
    upload_file(lease_id, upload_url, upload_headers, file_path)

    # 步骤5：将文件添加到服务器
    add_response = add_file(client, lease_id, parser, category_id, workspace_id)
    file_id = add_response.body.data.file_id

    # 步骤6：检查文件状态
    while True:
        describe_response = describe_file(client, workspace_id, file_id)
        status = describe_response.body.data.status
        print(f"当前文件状态：{status}")
        if status == 'INIT':
            print("文件待解析，请稍候...")
        elif status == 'PARSING':
            print("文件解析中，请稍候...")
        elif status == 'PARSE_SUCCESS':
            print("文件解析完成！")
            break
        else:
            print(f"未知的文件状态：{status}，请联系技术支持。")
            return None
        time.sleep(5)

    # 步骤7：创建知识文件索引
    print("正在创建知识文件索引")
    index_response = create_index(client, workspace_id, file_id, name, structure_type, source_type, sink_type)
    # 索引创建失败
    try:
        if index_response.body.status != 200:
            print(f"创建索引失败：{index_response.body.message}")
            return None
    except Exception as e:
        pass

    index_id = index_response.body.data.id

    # 步骤8：提交索引任务
    print("步骤8：正在提交索引任务")
    submit_response = submit_index(client, workspace_id, index_id)
    job_id = submit_response.body.data.id

    # 步骤9：获取索引任务状态
    print("步骤9：获取索引任务状态")
    while True:
        get_index_job_status_response = get_index_job_status(client, workspace_id, job_id, index_id)
        status = get_index_job_status_response.body.data.status
        print(f"当前索引任务状态：{status}")
        if status == 'COMPLETED':
            break
        time.sleep(5)

    print("知识库创建成功！")
    return index_id

    # except Exception as e:
    #     print(f"发生错误：{e}")
    #     return None

def upload(file_path:str,kb_name:str,category_id:str='藏书信息'):
    # 默认值设置 设置文件解析器 图书的类别为藏书信息 获取业务空间ID
    parser = 'DASHSCOPE_DOCMIND'
    workspace_id = os.environ.get('WORKSPACE_ID')
    index_id = None
    if kb_name =="藏书信息":
        print("正在添加藏书信息知识库数据")
        # 设置图书的类别为藏书信息
        category_id = 'cate_5be67d62713c407a83e809f3211f2460_10563706'
        # 设置数据库索引ID为藏书库对应ID
        index_id = 'tcpm27g3m5'
    elif kb_name == "服务框架":
        print("正在添加服务框架知识库数据")
        # 设置图书的类别为服务框架
        category_id = 'cate_0172568f98174f13869004072b7ba863_10563706'
        # 设置数据库索引ID为服务框架库对应ID
        index_id = '36t16dh5er'
    else:
        print("正在添加其他知识库数据")
        # 设置图书的类别为其他
        category_id = 'cate_bf68f2d79b0c44e69ce7645e2a0b7aad_10563706'
        # 设置数据库索引ID为其他库对应ID
        index_id = 'l2c4jv7i9p'
    # 第一步：检查并提示设置必要的环境变量并创建客户端
    check_environment_variables()
    client = create_client()
    # 步骤2：准备文件信息
    file_name = os.path.basename(file_path)
    file_md5 = calculate_md5(file_path)
    file_size = get_file_size(file_path)
    # 步骤3：申请上传租约
    lease_response = apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id)
    lease_id = lease_response.body.data.file_upload_lease_id
    upload_url = lease_response.body.data.param.url
    upload_headers = lease_response.body.data.param.headers
    # 步骤4：上传文件
    upload_file(lease_id, upload_url, upload_headers, file_path)
    # 步骤5：将文件添加到服务器
    add_response = add_file(client, lease_id, parser, category_id, workspace_id)
    file_id = add_response.body.data.file_id
    # 步骤6：检查文件状态
    while True:
        describe_response = describe_file(client, workspace_id, file_id)
        status = describe_response.body.data.status
        print(f"当前文件状态：{status}")
        if status == 'INIT':
            print("文件待解析，请稍候...")
        elif status == 'PARSING':
            print("文件解析中，请稍候...")
        elif status == 'PARSE_SUCCESS':
            print("文件解析完成！")
            break
        else:
            print(f"未知的文件状态：{status}，请联系技术支持。")
            return None
        time.sleep(5)
    # 步骤7：创建知识文件索引
    print("正在提交索引任务")
    submit_index_add_documents_job_request = bailian_20231229_models.SubmitIndexAddDocumentsJobRequest(
        index_id=index_id,
        source_type='DATA_CENTER_CATEGORY',
        category_ids=[
            category_id
        ]
    )
    response = client.submit_index_add_documents_job_with_options(workspace_id, submit_index_add_documents_job_request,headers={},runtime=util_models.RuntimeOptions())
    job_id = response.body.data.id

    # # 步骤8：获取索引任务状态
    print("获取索引任务状态")
    while True:
        get_index_job_status_response = get_index_job_status(client, workspace_id, job_id, index_id)
        status = get_index_job_status_response.body.data.status
        print(f"当前索引任务状态：{status}")
        if status == 'COMPLETED':
            break
        time.sleep(5)
    print("数据添加成功！")


############################################################################################################
# 以下为临时上传文件用于大模型提问
from pathlib import Path
from openai import OpenAI
def uploadTemp(filePath):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    file_object = client.files.create(file=Path(filePath), purpose="file-extract")
    file_id = file_object.id
    completion = client.chat.completions.create(
        model="qwen-long",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'system', 'content': f'fileid://{file_id}'},
            {'role': 'user', 'content': '请务必仅仅返回文件中的文本内容，而不要包括其他的任何信息。'}
        ],
    )
    result = completion.choices[0].message.content
    print(result)
    return result

if __name__ == '__main__':
    uploadTemp('D:/Desktop/temp.txt')
    #upload('D:/Desktop/智库书韵基础配置.txt','藏书信息')
    # # create_knowledge('D:/Desktop/真我GT5Pro.txt')