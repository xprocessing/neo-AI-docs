#批量cvs文件id查询亚马逊搜索排名
#搜索关键词，查出
#系统只抓取每个关键词搜索结果的前6页，比对后返回商品的排名数据：总排名+在第几页+所在页的位置，​总排名是指该类型排名的位置累计之和。 
# ​比如某个关键词在PC端搜索结果页的结构为：每页60个位置，其中48个自然位置+12个广告位置，
# 某ASIN排在第3页的第10个自然位置，那么其排名显示为：总排名106（第1页48+第2页48+第3页10=106），第3页第10名

# 地址https://www.amazon.com/s?k=car&page=2 k为关键词，page为页数
# div role="listitem" data-asin="B0CWQ8QMKT" 

#第一步：读取csv文件，获取ASIN和keyword
import csv
input_file = 'item.csv'
asins_keywords = []
with open(input_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        asins_keywords.append((row['ASIN'], row['keyword']))
        print(row['ASIN'], row['keyword'])

print(asins_keywords)
        
#第二步：根据ASIN和keyword，抓取亚马逊搜索结果页面前6页，获取排名数据
import requests
from bs4 import BeautifulSoup
import time
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
def get_rank(asin, keyword):
    base_url = 'https://www.amazon.com/s'
    total_rank = 0
    for page in range(1, 7):  # 前6页
        params = {'k': keyword, 'page': page}
        response = requests.get(base_url, headers=headers, params=params)
        print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', {'data-asin': True})
        
        position_in_page = 0
        for item in items:
            data_asin = item['data-asin']
            if data_asin:
                position_in_page += 1
                total_rank += 1
                if data_asin == asin:
                    print(f'Found ASIN: {asin} for keyword: {keyword} at Total Rank: {total_rank}, Page: {page}, Position in Page: {position_in_page}')
                    return total_rank, page, position_in_page
                
                
        time.sleep(1)  # 避免请求过快
    return None  # 未找到排名

#执行查询
for asin, keyword in asins_keywords:
    rank_info = get_rank(asin, keyword)





#更新csv文件，添加排名数据

"""
output_file = 'item_with_ranks.csv'
with open(output_file, mode='w', encoding='utf-8', newline='') as file:
    fieldnames = ['ASIN', 'keyword', 'rank']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    
    for asin, keyword in asins_keywords:
        rank_info = get_rank(asin, keyword)
        if rank_info:
            total_rank, page, position_in_page = rank_info
            rank_str = f'Total Rank: {total_rank}, Page: {page}, Position: {position_in_page}'
        else:
            rank_str = 'Not Found'
        
        writer.writerow({'ASIN': asin, 'keyword': keyword, 'rank': rank_str})
        print(f'Processed ASIN: {asin}, Keyword: {keyword}, Rank: {rank_str}')
#第三步：保存结果到新的csv文件
"""