import time
import csv
import random
from bs4 import BeautifulSoup

# Selenium 相关的库
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os

def get_driver():
    """
    配置并启动 Chrome 浏览器
    """
    chrome_options = Options()
    
    # --- 关键设置：反爬虫伪装 ---
    # 禁用“自动化控制”提示条
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # 模拟正常的用户代理
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # 忽略证书错误
    chrome_options.add_argument("--ignore-certificate-errors")
    
    # 如果你想要在后台静默运行（看不到浏览器窗口），取消下面这行的注释
    # chrome_options.add_argument("--headless") 

    # 获取驱动路径
    try:
        driver_path = ChromeDriverManager().install()
        print(f"正在使用 ChromeDriver 路径: {driver_path}")
    except Exception as e:
        print(f"下载 ChromeDriver 失败: {e}")
        return None

    service = Service(driver_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 进一步隐藏 Selenium 特征
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except OSError as e:
        if "WinError 193" in str(e):
            print("\n" + "!"*50)
            print("【严重错误解决方案】")
            print("检测到 WinError 193。这意味着下载的 chromedriver.exe 文件已损坏。")
            print(f"请手动删除此文件夹以清除缓存: {os.path.expanduser('~')}\\.wdm")
            print("然后重新运行脚本。")
            print("!"*50 + "\n")
        raise e

def parse_html(html_content):
    """
    使用 BeautifulSoup 解析 HTML (复用之前的逻辑)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    
    # 查找所有的搜索结果卡片
    results = soup.find_all('div', {'data-component-type': 's-search-result'})
    
    print(f"当前页面提取到 {len(results)} 个产品...")

    for item in results:
        product = {
            'title': 'N/A',
            'price': 'N/A',
            'sales_info': 'N/A',
            'link': 'N/A'
        }
        
        try:
            # 1. 标题
            title_tag = item.find('h2')
            if title_tag:
                product['title'] = title_tag.get_text().strip()
            
            # 2. 链接
            link_tag = item.find('a', class_='a-link-normal')
            if link_tag and 'href' in link_tag.attrs:
                product['link'] = "https://www.amazon.com" + link_tag['href']

            # 3. 价格
            price_tag = item.find('span', class_='a-price')
            if price_tag:
                offscreen_price = price_tag.find('span', class_='a-offscreen')
                if offscreen_price:
                    product['price'] = offscreen_price.get_text().strip()
            
            # 4. 销量/热度
            sales_tags = item.find_all('span', class_='a-size-base')
            found_sales = False
            for tag in sales_tags:
                text = tag.get_text().strip()
                if "bought in past month" in text:
                    product['sales_info'] = text
                    found_sales = True
                    break
            
            if not found_sales:
                review_tag = item.find('span', class_='a-size-base s-underline-text')
                if review_tag:
                    product['sales_info'] = f"Reviews: {review_tag.get_text().strip()}"

            products.append(product)
            
        except Exception:
            continue
            
    return products

def save_to_csv(products, filename):
    keys = ['title', 'price', 'sales_info', 'link']
    with open(filename, 'w', newline='', encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(products)
    print(f"数据已保存到 {filename}")

def main():
    keyword = input("请输入搜索关键词 (例如 gaming mouse): ").strip()
    if not keyword: return

    driver = get_driver()
    
    try:
        print("正在打开 Amazon...")
        # 直接构造搜索 URL，比模拟点击搜索栏更稳定
        search_url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
        driver.get(search_url)
        
        # --- 人工干预等待区 ---
        # 如果 Amazon 弹出了狗的图片或者验证码，Selenium 不会自动关闭
        # 你可以在弹出的浏览器窗口里手动解决验证码，然后按回车继续
        print("\n" + "="*50)
        print("请查看弹出的浏览器窗口。")
        print("如果看到了验证码，请手动完成验证。")
        print("如果没有验证码且页面加载正常，请直接按回车键继续...")
        print("="*50 + "\n")
        input("按回车键开始抓取数据...")
        
        # 模拟人类滚动页面，触发懒加载图片和数据
        print("正在滚动页面以加载所有商品...")
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {i * 800});")
            time.sleep(random.uniform(1.0, 2.0))
        
        # 获取渲染后的页面源代码
        page_source = driver.page_source
        
        # 解析数据
        data = parse_html(page_source)
        
        if data:
            filename = f"amazon_selenium_{keyword.replace(' ', '_')}.csv"
            save_to_csv(data, filename)
            
            # 打印前几个示例
            print("\n--- 抓取结果示例 ---")
            for p in data[:3]:
                print(f"Title: {p['title'][:40]}...")
                print(f"Price: {p['price']}")
                print("-" * 20)
        else:
            print("未找到商品数据，请检查页面是否加载正确。")

    except Exception as e:
        print(f"运行出错: {e}")
        
    finally:
        print("关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main()