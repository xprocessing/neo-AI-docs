import requests

# 1. 基本GET请求
url = "http://baidu.com/"
response = requests.get(url)
print("状态码：", response.status_code)  # 200表示成功
print("响应内容：", response.text)       # 文本形式

