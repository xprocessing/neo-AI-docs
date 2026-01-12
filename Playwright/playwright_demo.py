from playwright.sync_api import sync_playwright
import time

# 启动 Playwright 并管理浏览器生命周期
with sync_playwright() as p:
    # 1. 启动浏览器（chromium/firefox/webkit，headless=False 显示浏览器界面）
    browser = p.chromium.launch(headless=False, slow_mo=500)  # slow_mo 放慢操作速度，方便观察
    
    # 2. 创建新页面（标签页）
    page = browser.new_page()
    
    # 3. 访问百度首页
    page.goto("https://www.google.com/")
    
    # 4. 定位搜索框并输入关键词（自动等待搜索框可交互）
    # 方式1：CSS 选择器定位
    page.locator("#chat-input-area").fill("Playwright 教程")
    
    # 5. 定位搜索按钮并点击
    page.locator("#chat-submit-button").click()
    
    # 6. 等待搜索结果加载完成（可选，Playwright 已内置自动等待）
    page.wait_for_load_state("networkidle")  # 等待网络请求基本完成
    
    # 7. 截图保存结果页面
    page.screenshot(path="baidu_search_result.png", full_page=True)  # full_page=True 截取整页
    
    # 8. 停留3秒，观察效果
    time.sleep(3)
    
    # 9. 关闭浏览器
    browser.close()