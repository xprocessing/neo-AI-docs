import requests

# 1. 基本GET请求
url = "https://gongziyu.com/"
response = requests.get(url)
print("状态码：", response.status_code)  # 200表示成功
print("响应内容：", response.text)       # 文本形式
print("JSON数据：", response.json())     # 解析JSON（适用于接口返回）

# 2. 带参数和headers的请求（模拟浏览器）
params = {"key": "value", "page": 1}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get("https://gongziyu.com/", params=params, headers=headers)
print("带参数的URL：", response.url)  # 自动拼接参数

# 3. POST请求（提交表单数据）
data = {"username": "test1", "password": "123"}
data = {"username": "test2", "password": "123"}
data3 = {"username": "test3", "password": "123"}
data4 = {"username": "test4", "password": "123"}
data5 = {"username": "test5", "password": "123"}
response = requests.post("https://gongziyu.com/", data=data)

