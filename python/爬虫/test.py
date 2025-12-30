#请求https://www.amazon.com/s?k=car&page=2，获取页面内容并解析,需要header

import requests
url = "https://www.amazon.com/s?k=car&page=2"
#response = requests.get(url)
#print(response.text)
#经过测试，无法直接请求这个页面，需要添加请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
response = requests.get(url, headers=headers)
print(response.text)