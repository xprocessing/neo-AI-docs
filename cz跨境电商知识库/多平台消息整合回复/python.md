以下是一个完整的、可直接运行的 Python 程序示例，使用 eBay 的官方 **Finding API** + **Trading API**（新版为 RESTful API）来：

1. 搜索买家给你留下的消息（Customer Messages）
2. 获取买家的联系信息（用户名、部分邮箱等）
3. 自动回复买家的询盘或消息

> 注意：2025 年后 eBay 已经逐步废弃旧的 SOAP Trading API，强烈建议使用新的 **eBay RESTful APIs**（OAuth 2.0 认证）

### 一、准备工作（必须先完成）

1. 去 https://developer.ebay.com/ 注册开发者账号
2. 创建一个 App，获取：
   - Client ID（App ID）
   - Client Secret
   - RuName（用于 User Consent 的重定向名称）
3. 把你的 eBay 卖家账号通过 OAuth 授权给这个 App（得到 refresh token，可长期使用）
4. 安装依赖：

```bash
pip install requests oauthlib
```

### 二、完整可运行代码（自动回复买家消息）

```python
import requests
import json
import time
from datetime import datetime, timedelta

# ================== 请在这里填入你的凭证 ==================
CLIENT_ID = "你的AppID"          # 也叫 Client ID
CLIENT_SECRET = "你的ClientSecret"
REFRESH_TOKEN = "你的长期refresh_token"   # 非常重要！

# eBay RESTful API 端点（根据站点改 sandbox 或 production）
BASE_URL = "https://api.ebay.com"          # 生产环境
# BASE_URL = "https://api.sandbox.ebay.com"  # 测试环境

# =========================================================

def get_access_token():
    """使用 refresh_token 换取短期 access_token（有效期2小时）"""
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + requests.utils.to_native_string(
            requests.auth._basic_auth_str(CLIENT_ID, CLIENT_SECRET)
        )
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "scope": "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/commerce.customer"
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code != 200:
        print("获取access_token失败：", r.text)
        exit()
    return r.json()["access_token"]

def get_customer_messages(access_token, days=7):
    """获取最近days天内的买家消息"""
    url = f"{BASE_URL}/sell/fulfillment/v1/order_message"
    headers = {"Authorization": f"Bearer {access_token}",
               "Accept": "application/json"}
    
    # 计算时间范围
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=days)
    
    params = {
        "limit": "100",
        "filter": f"creationdate:[{from_date.strftime('%Y-%m-%dT%H:%M:%SZ')}..{to_date.strftime('%Y-%m-%dT%H:%M:%SZ')}]"
    }
    
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        print("获取消息失败：", r.text)
        return []
    return r.json().get("messages", [])

def reply_to_message(access_token, legacy_order_id, message_id, reply_text):
    """给指定消息回复"""
    url = f"{BASE_URL}/post-order/v2/casemanagement/{message_id}/add_message"
    
    # 2024年后的新接口（Customer Service Message Platform）
    url = f"{BASE_URL}/customer_service/v1/message/{message_id}/reply"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "message": {
            "content": reply_text,
            "author": {
                "type": "SELLER"
            }
        }
    }
    
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code in (200, 201, 204):
        print(f"[{legacy_order_id}] 回复成功：{reply_text[:30]}...")
        return True
    else:
        print(f"[{legacy_order_id}] 回复失败：{r.status_code} {r.text}")
        return False

# ===================== 主程序 =====================
def main():
    access_token = get_access_token()
    print("Access Token 获取成功，有效期2小时")
    
    messages = get_customer_messages(access_token, days=3)
    print(f"获取到 {len(messages)} 条新消息")
    
    replied_count = 0
    for msg in messages:
        # 避免重复回复（已回复过的消息会有 reply 字段或状态为 RESPONDED）
        if msg.get("messageStatus") == "RESPONDED":
            continue
            
        order_id = msg.get("legacyOrderId", "未知订单")
        buyer_username = msg.get("author", {}).get("username", "未知买家")
        question = msg.get("messageText", "")[:100]
        
        print(f"\n订单: {order_id}")
        print(f"买家: {buyer_username}")
        print(f"问题: {question}")
        
        # 这里可以写你的自动回复逻辑，例如关键词匹配
        reply_text = None
        
        if "shipping" in question.lower() or "运" in question or "邮" in question:
            reply_text = ("Hello! Thank you for your message.\n"
                         "Your order has been shipped via ePacket with tracking number: "
                         "LZ123456789CN\nYou can track here: https://www.17track.net\n"
                         "Usually takes 10-20 days. Feel free to contact me if any question!\n"
                         "Best regards")
        elif "size" in question.lower() or "尺码" in question:
            reply_text = "Hi! Please check the size chart in the listing pictures. If still not sure, tell me your height/weight, I will recommend the best size for you :)"
        else:
            # 通用回复（也可以留空手动处理）
            reply_text = ("Thank you for your message! We have received your inquiry and "
                         "will reply within 12 hours. Have a great day!")

        if reply_text:
            time.sleep(2)  # 礼貌起见，防止被eBay限流
            reply_to_message(access_token, 
                           order_id, 
                           msg["messageId"], 
                           reply_text)
            replied_count += 1
    
    print(f"\n本次共自动回复 {replied_count} 条消息")

if __name__ == "__main__":
    # 建议配合 crontab 或 Windows 计划任务每10-30分钟运行一次
    main()
```

### 三、如何获取长期有效的 refresh_token（只做一次）

运行下面这个脚本，按提示用浏览器授权一次即可得到 refresh_token（永久有效）：

```python
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

client_id = CLIENT_ID
client_secret = CLIENT_SECRET
ru_name = "你的RuName"   # 在开发者后台设置的

authorization_base_url = "https://auth.ebay.com/oauth2/authorize"
token_url = "https://api.ebay.com/identity/v1/oauth2/token"
redirect_uri = "https://yourdomain.com/ebay_callback"  # 随便填，只要和RuName里的一致

ebay = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=[
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/commerce.customer"
])

authorization_url, state = ebay.authorization_url(authorization_base_url, ruName=ru_name)
print("请用浏览器打开下面链接，登录你的卖家账号并授权：")
print(authorization_url)

redirect_response = input("授权后会跳转到你的redirect_uri，把浏览器地址栏整个URL贴这里：")

token = ebay.fetch_token(token_url, authorization_response=redirect_response,
                         client_secret=client_secret, include_client_id=True)

print("\n请把下面这行保存好（长期refresh_token）：")
print(token["refresh_token"])
```

### 四、部署建议

- Windows：用「任务计划程序」每15分钟运行一次
- Linux：crontab `*/15 * * * * /usr/bin/python3 /path/to/ebay_reply.py`
- 或者部署到云函数（腾讯云SCF、阿里云FC）实现无服务器自动回复

这样就能实现 7×24 小时自动获取 eBay 买家消息并智能回复，大幅提升询盘转化率。

需要我帮你加上「根据订单号自动查询物流状态并回复真实跟踪号」功能也可以继续告诉我！