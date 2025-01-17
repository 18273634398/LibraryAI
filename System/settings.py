from datetime import timedelta

embeddingModel = "multimodal-embedding-v1"
text2videoModel = "sambert-zhichu-v1"
video2textModel = 'paraformer-mtl-v1'
video2vedioModel = 'videoretalk'
# 阿里百炼服务平台AceessKey
api = ''
# 阿里云百炼服务平台智能体应用ID
appID =''


# learnByWeb
timeout = 5  #  超时时间
maxLearn =10  #  每次学习的最大数量
banURL = ['bilibili']  #  禁止或不学习的网站（例如视频网站）

# DelayTime
maxVoiceUnderstandDelay = timedelta(hours=0, minutes=0, seconds=5)  # 语音识别延迟

# 数据库相关
# 数据库连接信息
host = ''  # 数据库服务器地址
user = ''           # 数据库用户名
password = ''  # 数据库密码
database = ''  # 数据库名称，根据实际情况修改

# 电子邮件系统
authorizationCode = '' # 发送方授权码
senderEmail = '' # 接收邮箱

# 文生图相关
# 图片保存路径
generatedImageURL = 'D:\Documents\Code\Python\LibraryAI\Resource\pic\generated\Image.png'