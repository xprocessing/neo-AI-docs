"""
Selenium自动化演示脚本

此脚本展示了使用Selenium进行网页自动化的基本操作，包括：
1. 百度搜索功能
2. 京东商品搜索、排序和信息提取

使用说明：
=========
1. 安装依赖：
   pip install selenium

2. ChromeDriver配置（二选一）：
   - 方法一：安装ChromeDriver与浏览器版本匹配
     1. 查看Chrome浏览器版本：在地址栏输入 chrome://settings/help
     2. 下载对应版本的ChromeDriver：https://chromedriver.chromium.org/downloads
     3. 将chromedriver.exe放入Python安装目录或添加到系统PATH
   
   - 方法二：使用WebDriverManager自动管理（推荐）
     1. 安装：pip install webdriver-manager
     2. 取消第27行的注释，使用WebDriverManager

3. 运行脚本：
   python selenium_test.py

注意事项：
=========
- 网站结构可能会变化，导致选择器失效
- 脚本中包含适当的异常处理和等待机制
- 可根据需要修改搜索关键词和等待时间
- 某些网站可能有反爬机制，实际使用时可能需要添加更多模拟人类行为的代码
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# 如果使用WebDriverManager，取消下面的注释并安装webdriver-manager
# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(ChromeDriverManager().install())

def baidu_search(keyword="Python爬虫"):
    """
    使用Selenium进行百度搜索并提取结果
    
    Args:
        keyword: 搜索关键词，默认为"Python爬虫"
        
    Returns:
        list: 包含搜索结果标题和链接的列表
    """
    # 初始化浏览器 - 现代Selenium语法（v4+不需要executable_path）
    try:
        # 对于较新版本的Selenium，会自动查找匹配的驱动
        driver = webdriver.Chrome()
        driver.maximize_window()  # 最大化窗口
        print("浏览器启动成功")
        
        # 访问百度首页
        driver.get("https://www.baidu.com")
        print(f"已访问百度首页")
        
        # 等待搜索框加载完成（显式等待）
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "kw")))
        
        # 执行搜索操作
        search_box.clear()
        search_box.send_keys(keyword)
        print(f"已输入搜索关键词: {keyword}")
        
        # 点击搜索按钮
        search_button = driver.find_element(By.ID, "su")
        search_button.click()
        print("搜索按钮已点击")
        
        # 等待搜索结果加载完成
        wait.until(EC.presence_of_element_located((By.ID, "content_left")))
        print("搜索结果已加载")
        time.sleep(1)  # 额外等待一秒确保所有元素都已加载
        
        # 提取搜索结果
        results = []
        result_elements = driver.find_elements(By.CSS_SELECTOR, ".result a")
        
        for i, element in enumerate(result_elements[:10], 1):  # 只取前10个结果
            try:
                title = element.text
                link = element.get_attribute("href")
                if title and link:
                    results.append({"title": title, "link": link})
                    print(f"结果 {i}: {title}")
                    print(f"链接: {link}")
                    print("-" * 50)
            except Exception as e:
                print(f"处理结果时出错: {e}")
        
        return results
        
    except TimeoutException:
        print("超时异常: 元素加载超时")
    except NoSuchElementException:
        print("未找到元素异常")
    except Exception as e:
        print(f"发生异常: {e}")
    finally:
        # 无论如何都要关闭浏览器
        if 'driver' in locals():
            print("正在关闭浏览器...")
            driver.quit()

def demo_web_automation():
    """
    演示一个更复杂的网页自动化任务：
    1. 访问京东网站
    2. 搜索商品
    3. 筛选商品（按价格排序）
    4. 提取前5个商品信息
    """
    try:
        # 初始化浏览器
        driver = webdriver.Chrome()
        driver.maximize_window()
        wait = WebDriverWait(driver, 15)
        
        print("\n===== 开始京东商品搜索自动化演示 =====")
        
        # 访问京东首页
        driver.get("https://www.jd.com/")
        print("已访问京东首页")
        
        # 等待搜索框加载并输入关键词
        search_box = wait.until(EC.presence_of_element_located((By.ID, "key")))
        search_box.clear()
        search_box.send_keys("笔记本电脑")
        print("已输入搜索关键词: 笔记本电脑")
        
        # 点击搜索按钮
        search_button = driver.find_element(By.CLASS_NAME, "button")
        search_button.click()
        print("搜索按钮已点击")
        
        # 等待搜索结果加载
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "gl-warp")))
        print("搜索结果已加载")
        time.sleep(2)
        
        # 尝试按价格排序（点击价格排序按钮）
        try:
            price_sort_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-idx='2']")))
            price_sort_button.click()
            print("已点击价格排序按钮")
            # 等待排序后的结果加载
            time.sleep(3)
        except Exception as e:
            print(f"排序时出错: {e}")
        
        # 提取商品信息
        print("\n===== 商品信息提取结果 =====")
        product_items = driver.find_elements(By.CLASS_NAME, "gl-item")
        
        for i, item in enumerate(product_items[:5], 1):
            try:
                # 提取商品标题
                title_element = item.find_element(By.CLASS_NAME, "p-name")
                title = title_element.text.strip()
                
                # 提取商品价格
                price_element = item.find_element(By.CLASS_NAME, "p-price")
                price = price_element.text.strip()
                
                # 提取商品评价数
                try:
                    comment_element = item.find_element(By.CLASS_NAME, "p-commit")
                    comment = comment_element.text.strip()
                except:
                    comment = "暂无评价"
                
                # 提取商品店铺
                try:
                    shop_element = item.find_element(By.CLASS_NAME, "p-shop")
                    shop = shop_element.text.strip()
                except:
                    shop = "未知店铺"
                
                print(f"\n商品 {i}:")
                print(f"标题: {title[:50]}..." if len(title) > 50 else f"标题: {title}")
                print(f"价格: {price}")
                print(f"评价: {comment}")
                print(f"店铺: {shop}")
                print("-" * 60)
                
            except Exception as e:
                print(f"处理商品 {i} 时出错: {e}")
        
        print("\n===== 自动化演示完成 =====")
        
    except Exception as e:
        print(f"自动化任务执行出错: {e}")
    finally:
        if 'driver' in locals():
            print("正在关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    # 执行百度搜索演示
    print("===== Selenium百度搜索演示 =====")
    results = baidu_search()
    print(f"共找到 {len(results)} 条有效搜索结果")
    print("===== 百度搜索演示结束 =====")
    
    # 执行京东自动化演示
    demo_web_automation()
    
    print("\n所有Selenium演示已完成！")