在JavaScript中，引用JS文件主要有**浏览器环境**和**Node.js环境**两种场景，不同场景的实现方式差异较大。以下是详细的引用方法及注意事项：

### 一、浏览器环境中引用JS文件
浏览器中通过HTML标签引入JS文件，核心是使用`<script>`标签，主要有**直接引入**、**异步引入**、**动态加载**三种方式。

#### 1. 基本引入方式（同步加载）
通过`<script>`标签的`src`属性指定JS文件路径，浏览器会按标签顺序同步加载并执行脚本。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>JS文件引用</title>
  <!-- 外部JS文件引入 -->
  <script src="js/script.js"></script>
  <!-- 也可以写内联JS -->
  <script>
    console.log("内联JS执行");
  </script>
</head>
<body>
</body>
</html>
```
**路径说明**：
- 相对路径：`src="js/script.js"`（当前HTML文件同级的`js`文件夹下）、`src="../script.js"`（上级目录）。
- 绝对路径：`src="https://cdn.example.com/script.js"`（CDN地址）。
- 根路径：`src="/js/script.js"`（网站根目录）。

#### 2. 异步引入（`async`属性）
`async`属性让浏览器异步加载JS文件，加载完成后立即执行（不保证执行顺序），适用于无依赖的脚本（如统计脚本）。
```html
<script src="js/script1.js" async></script>
<script src="js/script2.js" async></script>
<!-- script1和script2的执行顺序取决于加载速度，而非标签顺序 -->
```

#### 3. 延迟执行（`defer`属性）
`defer`属性让浏览器异步加载JS文件，但会等待HTML解析完成后**按标签顺序执行**，适用于依赖DOM或有执行顺序要求的脚本。
```html
<script src="js/script1.js" defer></script>
<script src="js/script2.js" defer></script>
<!-- 先执行script1，再执行script2，且都在DOMContentLoaded事件前执行 -->
```

#### 4. 动态加载JS文件（通过JS代码创建`<script>`标签）
在运行时动态加载JS文件，适合按需加载（如懒加载、条件加载）。
```javascript
// 动态创建script标签
const script = document.createElement('script');
script.src = 'js/script.js';
script.onload = function() {
  console.log('脚本加载完成并执行');
};
script.onerror = function() {
  console.error('脚本加载失败');
};
// 将标签插入DOM，开始加载
document.head.appendChild(script);
```

### 二、Node.js环境中引用JS文件
Node.js遵循**CommonJS模块规范**（默认）或**ES模块规范**（ES6+），通过`require`（CommonJS）或`import/export`（ES模块）实现文件引用。

#### 1. CommonJS模块（Node.js默认）
- **导出模块**：使用`module.exports`或`exports`暴露变量/函数。
- **引入模块**：使用`require()`加载模块，参数为文件路径（相对/绝对）或内置模块/第三方包名。

**示例**：
```javascript
// utils.js（导出模块）
function add(a, b) {
  return a + b;
}
module.exports = { add }; // 导出对象
// 或单个导出：exports.add = add;

// main.js（引入模块）
const { add } = require('./utils.js'); // 相对路径，.js后缀可省略
console.log(add(1, 2)); // 输出3
```

#### 2. ES模块（ES6+）
Node.js中使用ES模块需满足以下条件之一：
- 文件后缀为`.mjs`；
- 项目根目录创建`package.json`并添加`"type": "module"`；
- 运行时通过`node --experimental-modules`（低版本Node.js）。

**导出**：使用`export`（命名导出）或`export default`（默认导出）。
**引入**：使用`import`（静态导入）或`import()`（动态导入）。

**示例**：
```javascript
// utils.mjs（或package.json指定"type": "module"的utils.js）
export function add(a, b) {
  return a + b;
}
export default function multiply(a, b) {
  return a * b;
}

// main.mjs
import multiply, { add } from './utils.mjs'; // 静态导入
console.log(add(1, 2)); // 3
console.log(multiply(2, 3)); // 6

// 动态导入（返回Promise）
import('./utils.mjs').then(({ add, default: multiply }) => {
  console.log(add(1, 2));
});
```

### 三、注意事项
1. **浏览器跨域**：直接通过本地文件协议（`file://`）引用不同域名的JS文件会触发跨域，需通过服务器运行（如`http://localhost`）或配置CORS。
2. **执行顺序**：同步`<script>`会阻塞HTML解析，建议将脚本放在`<body>`底部，或使用`async/defer`。
3. **模块规范兼容**：浏览器原生支持ES模块需通过`<script type="module">`引入：
   ```html
   <script type="module" src="js/module.js"></script>
   ```
4. **Node.js路径**：`require`中相对路径以当前文件为基准，内置模块（如`fs`、`path`）无需路径，第三方包（如`lodash`）会从`node_modules`加载。