const { chromium } = require('playwright');
const fs = require('fs'); // 用于将结果保存为 JSON 文件

(async () => {
    // 1. 启动浏览器，配置模拟真实浏览器环境（降低反爬风险）
    const browser = await chromium.launch({
        headless: false, // 调试阶段开启有头模式，方便观察；上线可改为 true（无头模式）
        slowMo: 800, // 放慢操作速度，模拟人工操作，避免被反爬
        args: [
            '--disable-blink-features=AutomationControlled', // 禁用自动化检测标识
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' // 模拟真实浏览器 UA
        ]
    });

    // 2. 创建新页面，进一步隐藏自动化特征
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }, // 模拟桌面端视口
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    const page = await context.newPage();

    // 3. 禁用 Playwright 的自动化标识（额外反爬优化）
    await page.addInitScript(() => {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    });

    try {
        // 4. 访问 Amazon 美国站首页
        await page.goto('https://www.amazon.com', {
            waitUntil: 'networkidle', // 等待网络请求基本完成，确保页面加载完整
            timeout: 30000 // 超时时间 30 秒
        });

        // 5. 定位搜索框，输入关键词 "wireless headphones"
        // Amazon 搜索框的 CSS 选择器通常为 #twotabsearchtextbox
        const searchBox = await page.locator('#twotabsearchtextbox');
        await searchBox.fill('wireless headphones');

        // 6. 点击搜索按钮（或按回车键提交搜索）
        // 搜索按钮选择器：#nav-search-submit-button
        await page.locator('#nav-search-submit-button').click();

        // 7. 等待搜索结果页面加载完成，等待商品列表元素出现
        await page.waitForLoadState('networkidle');
        await page.waitForLocator('.s-result-item', { timeout: 20000 }); // 商品卡片的通用选择器

        // 8. 提取商品数据（标题、价格、评分、商品链接）
        const productData = await page.$$eval('.s-result-item', (items) => {
            // 过滤有效商品（排除广告、无关元素）
            return items
                .filter(item => item.querySelector('h2 a') && item.querySelector('.a-price-whole'))
                .map(item => {
                    // 提取标题
                    const title = item.querySelector('h2 a')?.textContent?.trim() || '无标题';
                    // 提取商品链接
                    const link = `https://www.amazon.com${item.querySelector('h2 a')?.getAttribute('href') || ''}`;
                    // 提取价格（整数部分 + 小数部分）
                    const priceWhole = item.querySelector('.a-price-whole')?.textContent?.trim() || '0';
                    const priceFraction = item.querySelector('.a-price-fraction')?.textContent?.trim() || '00';
                    const price = `$${priceWhole}${priceFraction}`;
                    // 提取评分
                    const rating = item.querySelector('.a-icon-alt')?.textContent?.trim() || '无评分';

                    return { title, price, rating, link };
                });
        });

        // 9. 打印爬取结果
        console.log('爬取到的商品数据：');
        console.log(JSON.stringify(productData, null, 2));

        // 10. 将结果保存为 JSON 文件，方便后续查看
        fs.writeFileSync('amazon_products.json', JSON.stringify(productData, null, 2), 'utf-8');
        console.log('数据已保存至 amazon_products.json 文件');

    } catch (error) {
        console.error('爬取过程中出现错误：', error.message);
    } finally {
        // 11. 停留 5 秒后关闭浏览器（调试阶段方便观察结果）
        await new Promise(resolve => setTimeout(resolve, 5000));
        await browser.close();
    }
})();