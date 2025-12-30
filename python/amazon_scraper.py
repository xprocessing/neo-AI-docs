import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import random
import urllib.parse
import sys
import os

class AmazonScraper:
    def __init__(self, proxy=None):
        # 设置用户代理，模拟浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        # 基础URL
        self.base_url = 'https://www.amazon.com'
        # 代理设置
        self.proxy = proxy
        self.proxies = {}
        if proxy:
            self.proxies = {
                'http': proxy,
                'https': proxy
            }
    
    def search_products(self, keyword, max_results=10):
        """
        根据关键词搜索亚马逊产品
        
        Args:
            keyword (str): 搜索关键词
            max_results (int): 最大返回结果数
            
        Returns:
            list: 产品信息列表
        """
        print(f"正在搜索亚马逊产品: {keyword}")
        print(f"使用代理: {self.proxy if self.proxy else '否'}")
        
        # 对关键词进行URL编码
        encoded_keyword = urllib.parse.quote(keyword)
        search_url = f'{self.base_url}/s?k={encoded_keyword}'
        
        try:
            # 发送请求，添加超时和重试机制
            print(f"正在访问URL: {search_url}")
            response = requests.get(
                search_url, 
                headers=self.headers, 
                proxies=self.proxies if self.proxies else None,
                timeout=15
            )
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取产品信息
            products = []
            # 定位产品元素 - 注意：亚马逊的页面结构可能会变化
            product_elements = soup.select('div[data-asin][data-component-type="s-search-result"]')
            
            for i, product in enumerate(product_elements):
                if i >= max_results:
                    break
                
                # 添加随机延迟，避免被封
                time.sleep(random.uniform(1, 3))
                
                try:
                    # 提取产品标题
                    title_element = product.select_one('h2 a span')
                    title = title_element.text.strip() if title_element else 'N/A'
                    
                    # 提取产品链接
                    link_element = product.select_one('h2 a')
                    link = self.base_url + link_element['href'] if link_element else 'N/A'
                    
                    # 提取产品价格
                    price_element = product.select_one('.a-price .a-offscreen')
                    price = price_element.text.strip() if price_element else 'N/A'
                    
                    # 提取评分
                    rating_element = product.select_one('.a-icon-alt')
                    rating = rating_element.text.strip() if rating_element else 'N/A'
                    
                    # 提取评论数
                    review_element = product.select_one('.a-size-base.s-underline-text')
                    review_count = review_element.text.strip() if review_element else 'N/A'
                    
                    # 提取产品图片
                    image_element = product.select_one('.s-image')
                    image_url = image_element['src'] if image_element else 'N/A'
                    
                    products.append({
                        'title': title,
                        'price': price,
                        'rating': rating,
                        'review_count': review_count,
                        'link': link,
                        'image_url': image_url
                    })
                    
                    print(f"已提取产品 {i+1}/{min(max_results, len(product_elements))}: {title[:50]}...")
                    
                except Exception as e:
                    print(f"提取单个产品信息时出错: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"搜索过程中出错: {e}")
            print("\n提示: 亚马逊可能阻止了请求。您可以：")
            print("1. 检查网络连接")
            print("2. 尝试使用代理服务器")
            print("3. 稍后再试")
            return []

    def save_to_csv(self, products, filename='amazon_products.csv'):
        """
        将产品信息保存到CSV文件
        
        Args:
            products (list): 产品信息列表
            filename (str): 保存的文件名
        """
        if not products:
            print("没有产品数据可保存")
            return
        
        try:
            # 定义CSV字段名
            fieldnames = ['title', 'price', 'rating', 'review_count', 'link', 'image_url']
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for product in products:
                    writer.writerow(product)
            
            print(f"成功保存 {len(products)} 个产品信息到 {filename}")
            
        except Exception as e:
            print(f"保存CSV文件时出错: {e}")

    def save_to_json(self, products, filename='amazon_products.json'):
        """
        将产品信息保存到JSON文件
        
        Args:
            products (list): 产品信息列表
            filename (str): 保存的文件名
        """
        
        if not products:
            print("没有产品数据可保存")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(products, jsonfile, ensure_ascii=False, indent=4)
            
            print(f"成功保存 {len(products)} 个产品信息到 {filename}")
            
        except Exception as e:
            print(f"保存JSON文件时出错: {e}")

# 主函数示例
if __name__ == "__main__":
    # 从命令行获取关键词
    if len(sys.argv) > 1:
        keyword = ' '.join(sys.argv[1:])
    else:
        # 默认关键词
        keyword = "laptop"
    
    # 从环境变量或命令行参数获取代理设置
    proxy = None
    if 'PROXY' in os.environ:
        proxy = os.environ['PROXY']
    
    # 创建爬虫实例
    scraper = AmazonScraper(proxy=proxy)
    
    # 搜索产品
    print("="*60)
    print(f"亚马逊产品搜索工具")
    print("="*60)
    
    products = scraper.search_products(keyword, max_results=5)
    
    # 保存结果
    if products:
        print("\n" + "="*60)
        print(f"搜索完成！找到 {len(products)} 个产品")
        print("="*60)
        
        # 显示产品摘要
        for i, product in enumerate(products):
            print(f"\n产品 {i+1}:")
            print(f"标题: {product['title'][:80]}..." if len(product['title']) > 80 else f"标题: {product['title']}")
            print(f"价格: {product['price']}")
            print(f"评分: {product['rating']}")
            print(f"评论数: {product['review_count']}")
        
        # 保存为CSV
        csv_filename = f"amazon_{urllib.parse.quote(keyword)}_products.csv"
        scraper.save_to_csv(products, csv_filename)
        
        # 保存为JSON
        json_filename = f"amazon_{urllib.parse.quote(keyword)}_products.json"
        scraper.save_to_json(products, json_filename)
    else:
        print("\n未找到任何产品信息")
        print("\n提示: 您可以尝试以下方法:")
        print("1. 更换搜索关键词")
        print("2. 设置有效的代理服务器 (通过PROXY环境变量)")
        print("3. 检查网络连接是否正常")
