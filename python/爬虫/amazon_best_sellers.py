#亚马逊热卖产品页面 https://www.amazon.com/Best-Sellers/zgbs
#汽车品类https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/ref=zg_bs_nav_automotive_0

#第一步，请求页面，获取页面内容https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/ref=zg_bs_nav_automotive_0
import requests
url = "https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/ref=zg_bs_nav_automotive_0"
#response = requests.get(url)
#print(response.text)
#经过测试，无法直接请求这个页面，需要添加请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
response = requests.get(url, headers=headers)
print(response.text)

#找到class=a-ordered-list 的ol标签
#提取ol标签下的所有li标签
#输出每个li标签的a标签的href属性值
#输出每个li标签的img标签的src属性值
#输出每个li标签的span.div 的id属性值


from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")
ol_tag = soup.find("ol", class_="a-ordered-list")
li_tags = ol_tag.find_all("li")
for li in li_tags:
    a_tag = li.find("a")
    href = a_tag['href'] if a_tag else "No link"
    #href前面加上域名
    full_url = f"https://www.amazon.com{href}" if href != "No link" else "No link"   
    img_tag = li.find("img")
    img_src = img_tag['src'] if img_tag else "No image"
    div_tag = li.find("div", class_="p13n-sc-uncoverable-faceout")
    div_id = div_tag['id'] if div_tag else "No div"
    print(f"Image URL: {img_src}, Div ID: {div_id}, Link: {full_url}")


#导出数据到CSV文件
import csv
with open("amazon_best_sellers.csv", "w", newline='', encoding='utf-8') as f:

    writer = csv.writer(f)

    writer.writerow(["Image URL", "Div ID", "Link"])

    for li in li_tags:

        a_tag = li.find("a")

        href = a_tag['href'] if a_tag else "No link"

        full_url = f"https://www.amazon.com{href}" if href != "No link" else "No link"   

        img_tag = li.find("img")

        img_src = img_tag['src'] if img_tag else "No image"

        div_tag = li.find("div", class_="p13n-sc-uncoverable-faceout")

        div_id = div_tag['id'] if div_tag else "No div"

        writer.writerow([img_src, div_id, full_url])


#输出markdown文件，点击图片
import csv
with open("amazon_best_sellers.csv", "r", newline='', encoding='utf-8') as f:

    reader = csv.reader(f)

    with open("amazon_best_sellers.md", "w", encoding='utf-8') as md_file:

        for row in reader:

            img_src, div_id, full_url = row

            #md_file.write(f"![{div_id}]({img_src})\n")
            md_file.write(f"[![{div_id}]({img_src})]({full_url})\n")

            md_file.write(f"[直达链接Link]({full_url})\n\n")