const { chromium } = require('playwright');

(async () => {
    // 1. 启动浏览器
    const browser = await chromium.launch({ headless: false, slowMo: 500 });
    
    // 2. 创建新页面
    const page = await browser.newPage();
    
    // 3. 访问百度首页
    await page.goto('https://m.baidu.com/');
    
    // 4. 输入搜索关键词
    await page.locator('#index-kw').fill('Playwright 教程');
    
    // 5. 点击搜索按钮
    await page.locator('#index-bn').click();
    
    // 6. 等待结果加载并截图
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'baidu_search_result_js.png', fullPage: true });
    
    // 7. 停留3秒后关闭浏览器
    await new Promise(resolve => setTimeout(resolve, 3000));
    await browser.close();
})();