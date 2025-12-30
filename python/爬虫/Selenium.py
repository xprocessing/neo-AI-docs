from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. 创建 ChromeOptions 对象并添加参数
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')  # 如果在 Windows 上运行，这句可以不加，但加上也无妨
chrome_options.add_argument('--incognito') # 核心：使用隐身模式

# 2. 初始化浏览器驱动时传入 options
driver = webdriver.Chrome(options=chrome_options)

try:
    # 打开百度首页
    driver.get("https://www.baidu.com")
    print("等待搜索框变为可点击...")

    # 增加等待时间到 20 秒，双重保险
    search_box = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "kw"))
    )
    print("搜索框已可交互！")

    search_box.send_keys("Selenium 教程")
    print("已输入搜索内容。")

    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "su"))
    )
    search_button.click()
    print("已点击搜索按钮。")

    time.sleep(5)
    print("当前页面标题是：", driver.title)

finally:
    driver.quit()
    print("浏览器已关闭。")

print("脚本执行完毕！")