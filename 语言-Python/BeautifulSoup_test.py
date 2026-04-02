from bs4 import BeautifulSoup
import requests

html = """
<html>
    <body>
        <div class="container">
            <h1>标题</h1>
            <ul>
                <li><a href="/link1">链接1</a></li>
                <li><a href="/link2">链接2</a></li>
            </ul>
        </div>
    </body>
</html>
"""

# 解析HTML
soup = BeautifulSoup(html, "lxml")  # 使用lxml解析器

# 提取数据
print("标题文本：", soup.h1.text)  # 直接通过标签名获取
print("所有a标签：", [a.text for a in soup.find_all("a")])  # 查找所有a标签
print("第一个li的a链接：", soup.li.a["href"])  # 获取属性
print("class为container的div：", soup.find("div", class_="container").text.strip())  # 按class查找