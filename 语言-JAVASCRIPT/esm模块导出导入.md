你想要一个**纯本地、无需任何构建工具**（不用 Vite/Webpack）、直接在浏览器中运行的 ESM 实用示例，对吧？

这个例子我们做一个「简易工具库」：拆分 3 个模块（工具函数、配置、主入口），通过 ESM 的 `import`/`export` 实现模块化调用，最终在浏览器中运行效果。

### 第一步：创建项目文件结构
先在本地新建一个文件夹（比如 `esm-local-demo`），里面创建 4 个文件，结构如下：
```
esm-local-demo/
├── config.js       # 配置模块（默认导出）
├── utils.js        # 工具函数模块（命名导出）
├── app.js          # 主业务模块（导入其他模块并使用）
└── index.html      # 浏览器入口页面（引入 app.js 作为 ESM 模块）
```

### 第二步：编写各个文件的代码
#### 1. config.js（默认导出一个配置对象）
这里用 `export default` 导出全局配置，一个模块只能有一个默认导出。
```javascript
// 项目配置模块（默认导出）
const appConfig = {
  appName: "ESM 本地演示项目",
  version: "1.0.0",
  baseUrl: "https://api.example.com"
};

// 默认导出（导入时可以自定义命名）
export default appConfig;
```

#### 2. utils.js（命名导出多个工具函数）
这里用 `export` 导出多个独立工具函数，支持按需导入。
```javascript
// 工具函数模块（命名导出）

/**
 * 格式化日期：把 Date 对象转为 "YYYY-MM-DD" 格式
 * @param {Date} date - 日期对象
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * 防抖函数：避免高频操作（如输入、点击）频繁触发
 * @param {Function} fn - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(fn, delay = 300) {
  let timer = null;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

/**
 * 打印带样式的日志（方便调试）
 * @param {string} message - 日志信息
 */
export function logInfo(message) {
  console.log(`%c [${new Date().toLocaleTimeString()}] ${message}`, "color: #42b983; font-weight: bold;");
}
```

#### 3. app.js（主模块：导入并使用其他模块）
这里用 `import` 导入上面两个模块的内容，然后编写业务逻辑。
```javascript
// 主业务模块：导入其他模块并使用

// 1. 导入默认导出的配置（自定义命名为 config，无需大括号）
import config from './config.js';

// 2. 导入命名导出的工具函数（需要大括号，与导出名称一致）
import { formatDate, logInfo, debounce } from './utils.js';

// 3. 业务逻辑：使用导入的配置和工具函数
function initApp() {
  // 打印应用配置
  logInfo(`应用名称：${config.appName}，版本：${config.version}`);
  
  // 格式化当前日期并打印
  const today = formatDate(new Date());
  logInfo(`当前日期：${today}`);
  
  // 演示防抖函数（输入框输入后，延迟 500 毫秒才触发回调）
  const input = document.getElementById('search-input');
  const result = document.getElementById('search-result');
  
  input.addEventListener('input', debounce((e) => {
    result.textContent = `你输入了：${e.target.value}`;
    logInfo(`搜索内容：${e.target.value}`);
  }, 500));
}

// 4. 页面加载完成后初始化应用
window.onload = initApp;
```

#### 4. index.html（浏览器入口：引入 ESM 模块）
关键是 `<script>` 标签要添加 `type="module"`，告诉浏览器这是 ESM 模块，支持 `import`/`export`。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>ESM 本地实用示例</title>
  <style>
    body { padding: 20px; font-family: Arial; }
    .container { max-width: 600px; margin: 0 auto; }
    input { padding: 8px; width: 300px; margin: 10px 0; }
    #search-result { color: #666; margin-top: 10px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>ESM 本地模块化演示</h1>
    <input type="text" id="search-input" placeholder="输入内容演示防抖效果...">
    <div id="search-result"></div>
  </div>

  <!-- 关键：添加 type="module"，引入 ESM 主模块 -->
  <script type="module" src="./app.js"></script>
</body>
</html>
```

### 第三步：运行并查看效果
#### 1. 启动方式（两种可选）
##### 方式 1：直接打开 HTML 文件（注意坑点）
- 直接双击 `index.html`，浏览器会以 `file://` 协议打开。
- ❌ 可能出现错误：`Access to script at 'file:///xxx/app.js' from origin 'null' has been blocked by CORS policy`。
- 原因：浏览器对 `file://` 协议的 ESM 模块有跨域限制，优先推荐方式 2。

##### 方式 2：启动本地静态服务器（推荐，无跨域问题）
最简单的方式是用 Node.js 自带的 `http-server`，步骤如下：
1.  打开终端，进入 `esm-local-demo` 文件夹。
2.  安装 `http-server`（全局安装一次即可）：
    ```bash
    npm install -g http-server
    ```
3.  启动本地服务器：
    ```bash
    http-server
    ```
4.  终端会输出访问地址，通常是 `http://localhost:8080`，复制这个地址在浏览器中打开。

#### 2. 查看效果
1.  浏览器打开后，打开**开发者工具（F12）** → 切换到「Console」标签，能看到带绿色样式的日志，显示应用配置和当前日期。
2.  在输入框中快速输入内容（比如「ESM 真好用」），会发现：只有停止输入 500 毫秒后，下方才会显示输入内容，控制台也会打印对应的日志，这就是防抖函数的效果。
3.  可以在开发者工具的「Sources」标签中，看到各个模块文件的结构，验证 ESM 模块化的加载关系。

### 第四步：示例核心解析
1.  **模块化拆分**：把配置、工具函数、业务逻辑分开，提高代码可维护性，这是 ESM 最核心的实用价值。
2.  **导出与导入对应**：默认导出用 `import 自定义名称 from 路径`，命名导出用 `import { 导出名称 } from 路径`。
3.  **浏览器原生支持**：无需任何构建工具，仅靠 `<script type="module">` 就能实现模块化，这也是 Vite 开发阶段的核心原理。
4.  **实用工具函数**：示例中的 `formatDate`（日期格式化）、`debounce`（防抖）都是项目中高频使用的工具，体现了模块化的复用价值。

### 总结
1.  核心要点：ESM 实现了前端代码的模块化拆分与复用，浏览器通过 `type="module"` 原生支持。
2.  运行关键：避免 `file://` 协议的跨域问题，优先使用本地静态服务器（如 `http-server`）。
3.  语法对应：默认导出（单个）与命名导出（多个）的导入语法需严格匹配，路径要写完整扩展名。

这个示例是纯本地、无依赖的，你可以直接复制文件内容运行，也可以在此基础上扩展更多模块（比如新增 `api.js` 处理接口请求），进一步理解 ESM 的实用性。