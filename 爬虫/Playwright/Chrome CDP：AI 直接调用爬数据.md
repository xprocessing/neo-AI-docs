# Chrome CDP：AI 直接调用爬数据

Chrome 自身提供的核心接口是 **Chrome DevTools Protocol (CDP)** —— 这是浏览器原生的、底层的 WebSocket 控制协议，所有 AI 浏览器工具（Browser Use、Puppeteer、Playwright）**底层全靠它**。

### 一、Chrome 原生接口：CDP（核心）

**全称**：Chrome DevTools Protocol

**本质**：浏览器内置的 WebSocket API，**无需安装任何驱动/插件**

**作用**：AI/程序直接控制 Chrome：

- 导航、刷新、关闭页面

- 获取完整 DOM、HTML、文本

- 模拟点击、输入、滚动、表单提交

- 拦截网络请求、修改响应

- 执行任意 JS、获取控制台输出

- 截图、生成 PDF

- 监听页面事件（加载完成、弹窗、错误）

**官方文档**：

- 主协议：[https://chromedevtools.github.io/devtools-protocol/tot/](https://chromedevtools.github.io/devtools-protocol/tot/)

- 浏览器端：[https://chromedevtools.github.io/devtools-protocol/tot/Browser/](https://chromedevtools.github.io/devtools-protocol/tot/Browser/)

- Page（页面）：[https://chromedevtools.github.io/devtools-protocol/tot/Page/](https://chromedevtools.github.io/devtools-protocol/tot/Page/)

- DOM：[https://chromedevtools.github.io/devtools-protocol/tot/DOM/](https://chromedevtools.github.io/devtools-protocol/tot/DOM/)

- Runtime（JS执行）：[https://chromedevtools.github.io/devtools-protocol/tot/Runtime/](https://chromedevtools.github.io/devtools-protocol/tot/Runtime/)

- Network：[https://chromedevtools.github.io/devtools-protocol/tot/Network/](https://chromedevtools.github.io/devtools-protocol/tot/Network/)

---

### 二、启动 Chrome 开放 CDP 端口（AI 可直接连）

**命令行启动（Windows/macOS/Linux）**：

```Bash

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug \
  --no-first-run \
  --disable-popup-blocking

# Windows
chrome.exe --remote-debugging-port=9222 --user-data-dir=D:\chrome-debug

# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

**验证**：浏览器打开 `http://localhost:9222/json` → 返回所有标签页的 CDP 连接信息

---

### 三、AI 直接调用 CDP（原生接口，无中间库）

**原理**：

- AI 连 WebSocket：`ws://localhost:9222/devtools/page/xxx`

- 发 JSON-RPC 命令

- 接收浏览器返回结果

**示例（AI 可直接执行）**：

1. **获取页面 HTML**

```JSON

{"id":1,"method":"Runtime.evaluate","params":{"expression":"document.documentElement.outerHTML"}}
```

1. **点击按钮**

```JSON

{"id":2,"method":"DOM.querySelector","params":{"selector":"button.add-to-cart"}}
// 返回 nodeId
{"id":3,"method":"DOM.click","params":{"nodeId": 42}}
```

1. **输入文本**

```JSON

{"id":4,"method":"DOM.focus","params":{"nodeId": 43}}
{"id":5,"method":"Input.insertText","params":{"text":"iPhone 16"}}
```

1. **获取商品数据（AI 最常用）**

```JSON

{"id":6,"method":"Runtime.evaluate","params":{
  "expression":"JSON.stringify([...document.querySelectorAll('.item')].map(i=>({title:i.querySelector('.title').textContent,price:i.querySelector('.price').textContent})))"
}}
```

---

### 四、Chrome 原生 AI 接口（2026 最新）

#### 1. WebMCP（Web Machine Control Protocol）

- Chrome 内置 AI 直连协议（2026 新）

- 比 CDP 更快、更语义化

- AI 直接理解网页：按钮、输入框、列表、商品

- 官方：[https://developer.chrome.com/docs/webmcp/](https://developer.chrome.com/docs/webmcp/)

#### 2. Chrome Gemini 内置 AI（2026）

- F12 DevTools → Gemini 面板

- 自然语言指令：

    - “抓取当前页商品标题、价格、销量”

    - “自动填写表单”

    - “生成 CDP 脚本”

---

### 五、CDP vs 封装库（Browser Use/Playwright）

|方式|优点|缺点|适合|
|---|---|---|---|
|**原生 CDP**|最轻、最快、无依赖|命令多、需自己解析|AI 底层调用、极致性能|
|**Browser Use**|AI 自然语言、全自动|封装层、略重|快速开发、电商爬取|
|**Playwright**|稳定、跨浏览器|需安装、较重|企业级、复杂登录|
---

### 六、AI 电商爬取最佳实践（原生接口）

1. **启动 Chrome 开放 9222 端口**

2. **AI 连接 WebSocket**

3. **Page.navigate 到淘宝/京东**

4. **Runtime.evaluate 执行 JS 提取商品**

5. **Page.click 翻页**

6. **循环采集 → 返回 JSON**

**优势**：

- **完全原生**，无任何第三方依赖

- **反爬最强**：和真人浏览器一模一样

- **AI 直接控制**，不需要中间库

- **保留登录态、Cookie、插件**

---

### 七、你要的：原生接口网址（全）

- CDP 主页：[https://chromedevtools.github.io/devtools-protocol/](https://chromedevtools.github.io/devtools-protocol/)

- CDP JSON 定义：[https://github.com/ChromeDevTools/devtools-protocol](https://github.com/ChromeDevTools/devtools-protocol)

- WebMCP：[https://developer.chrome.com/docs/webmcp/](https://developer.chrome.com/docs/webmcp/)

- Chrome 远程调试：[https://developer.chrome.com/docs/devtools/remote-debugging/](https://developer.chrome.com/docs/devtools/remote-debugging/)

- CDP Python 直连库：[https://github.com/HMaker/python-cdp](https://github.com/HMaker/python-cdp)

---

### 八、我直接给你：AI 可运行的 CDP 原生代码

```Python

import asyncio
import websockets
import json

async def cdp_call(ws, method, params={}):
    msg = {"id": 1, "method": method, "params": params}
    await ws.send(json.dumps(msg))
    return json.loads(await ws.recv())

async def main():
    # 连接 Chrome 原生 CDP
    async with websockets.connect("ws://localhost:9222/devtools/page/xxx") as ws:
        # 1. 打开淘宝
        await cdp_call(ws, "Page.navigate", {"url":"https://s.taobao.com/search?q=手机"})
        await asyncio.sleep(3)
        
        # 2. 原生接口获取商品数据
        res = await cdp_call(ws, "Runtime.evaluate", {
            "expression":"""
            JSON.stringify([...document.querySelectorAll('.item J_MouserOnverReq')].map(i=>({
                title: i.querySelector('.title').textContent.trim(),
                price: i.querySelector('.price').textContent,
                sales: i.querySelector('.deal-cnt').textContent
            })))
            """
        })
        print(res["result"]["result"]["value"])

asyncio.run(main())
```

---

### 总结

- **Chrome 自身接口 = CDP（Chrome DevTools Protocol）**

- **AI 直接连 WebSocket:9222**，无需任何库

- **最稳、最原生、反爬最强**

- 2026 新增 **WebMCP**，AI 语义化控制网页

需要我帮你生成 **AI 直接调用 CDP 爬淘宝/京东/拼多多** 的完整原生代码吗？
> （注：文档部分内容可能由 AI 生成）