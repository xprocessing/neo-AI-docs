# Playwright 全面介绍与基础使用
你想了解的 **Playwright** 是由 Microsoft 开发的一款现代化、开源的端到端（E2E）测试工具，同时也可用于网页自动化、数据爬取等场景。它的核心优势是提供了统一的 API 来操作所有主流浏览器，具备强大的自动化能力和良好的开发体验。

## 一、核心特性
1.  **跨浏览器支持**：完美支持 Chromium（Chrome、Edge 基于此内核）、Firefox、WebKit（Safari 内核），无需修改核心代码即可实现多浏览器兼容测试/自动化。
2.  **多语言支持**：提供 Python、JavaScript/TypeScript、C#、Java 等多种编程语言的绑定，满足不同技术栈开发者的需求。
3.  **自动等待机制**：内置智能等待（等待元素可见、可点击、网络请求完成等），无需手动添加 `sleep()` 等待，解决了自动化中最常见的元素定位超时问题。
4.  **强大的元素选择器**：支持 CSS 选择器、XPath、文本内容选择器（`text="xxx"`）、属性选择器等，还支持自定义选择器。
5.  **丰富的自动化能力**：支持页面导航、表单提交、文件上传/下载、弹窗处理、网络请求拦截与模拟、移动端设备模拟等。
6.  **无头/有头模式**：默认支持无头模式（无浏览器界面，运行高效，适合CI/CD环境），也可切换为有头模式（可视化运行，方便调试）。

## 二、安装（主流编程语言）
### 1. Python 环境安装
首先确保已安装 Python 3.8+，然后通过 `pip` 安装：
```bash
# 安装 Playwright Python 绑定
pip install playwright

# 安装所需的浏览器驱动（Chromium、Firefox、WebKit）
playwright install
```

### 2. JavaScript/TypeScript 环境安装
确保已安装 Node.js 14+，然后通过 `npm`/`yarn` 安装：
```bash
# 初始化项目（可选，已有项目可跳过）
npm init -y

# 安装 Playwright 核心依赖
npm install playwright --save-dev

# （可选）安装 Playwright 测试运行器（用于结构化测试）
npm install @playwright/test --save-dev
```

## 三、基础实战示例
### 示例 1：Python 实现网页自动化（打开百度、搜索关键词、截图）
```python
from playwright.sync_api import sync_playwright
import time

# 启动 Playwright 并管理浏览器生命周期
with sync_playwright() as p:
    # 1. 启动浏览器（chromium/firefox/webkit，headless=False 显示浏览器界面）
    browser = p.chromium.launch(headless=False, slow_mo=500)  # slow_mo 放慢操作速度，方便观察
    
    # 2. 创建新页面（标签页）
    page = browser.new_page()
    
    # 3. 访问百度首页
    page.goto("https://www.baidu.com")
    
    # 4. 定位搜索框并输入关键词（自动等待搜索框可交互）
    # 方式1：CSS 选择器定位
    page.locator("#kw").fill("Playwright 教程")
    
    # 5. 定位搜索按钮并点击
    page.locator("#su").click()
    
    # 6. 等待搜索结果加载完成（可选，Playwright 已内置自动等待）
    page.wait_for_load_state("networkidle")  # 等待网络请求基本完成
    
    # 7. 截图保存结果页面
    page.screenshot(path="baidu_search_result.png", full_page=True)  # full_page=True 截取整页
    
    # 8. 停留3秒，观察效果
    time.sleep(3)
    
    # 9. 关闭浏览器
    browser.close()
```

### 示例 2：JavaScript/TypeScript 实现简单网页自动化
```javascript
const { chromium } = require('playwright');

(async () => {
    // 1. 启动浏览器
    const browser = await chromium.launch({ headless: false, slowMo: 500 });
    
    // 2. 创建新页面
    const page = await browser.newPage();
    
    // 3. 访问百度首页
    await page.goto('https://www.baidu.com');
    
    // 4. 输入搜索关键词
    await page.locator('#kw').fill('Playwright 教程');
    
    // 5. 点击搜索按钮
    await page.locator('#su').click();
    
    // 6. 等待结果加载并截图
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'baidu_search_result_js.png', fullPage: true });
    
    // 7. 停留3秒后关闭浏览器
    await new Promise(resolve => setTimeout(resolve, 3000));
    await browser.close();
})();
```

## 四、运行示例
1.  **Python 示例运行**：将代码保存为 `playwright_demo.py`，然后执行：
    ```bash
    python playwright_demo.py
    ```
2.  **JavaScript 示例运行**：将代码保存为 `playwright_demo.js`，然后执行：
    ```bash
    node playwright_demo.js
    ```

运行成功后，会看到浏览器自动打开并完成一系列操作，同时在当前目录下生成截图文件。

## 五、关键补充说明
1.  **同步/异步 API**：Playwright Python 提供 `sync_api`（同步，适合简单场景）和 `async_api`（异步，适合高并发场景）；JavaScript 仅提供异步 API（基于 Promise/async-await）。
2.  **元素定位方式**：除了上述的 CSS 选择器，还支持：
    - 文本定位：`page.locator("text=百度一下")`
    - XPath 定位：`page.locator("//*[@id='kw']")`
    - 属性定位：`page.locator("[name='wd']")`
3.  **CI/CD 集成**：Playwright 支持在 Docker、GitHub Actions、GitLab CI 等环境中运行，无需额外配置复杂的浏览器环境，可通过 `playwright install-deps` 安装系统依赖。
4.  **调试工具**：可使用 `page.pause()` 暂停自动化流程，打开内置调试器，方便排查元素定位、流程执行等问题。

## 总结
1. Playwright 是一款跨浏览器、多语言的现代化自动化/测试工具，核心优势是自动等待、无侵入式操作、强大的兼容性。
2. 快速上手步骤：安装 Playwright → 安装浏览器驱动 → 编写「启动浏览器→操作页面→关闭浏览器」的核心流程。
3. 适合场景：端到端测试、网页自动化、数据爬取、页面截图/录屏等，尤其在前端项目的自动化测试中应用广泛。