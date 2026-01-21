以下是 **JavaScript 最常见的 200 个关键词**，每个关键词附带**一句话简短总结**，按分类整理，便于快速理解和记忆：


### 一、核心语法与基础概念（50个）
1. `var`：函数级作用域变量声明（ES5）。  
2. `let`：块级作用域变量声明（ES6+）。  
3. `const`：块级作用域常量声明（不可重新赋值）。  
4. `function`：定义函数。  
5. `return`：函数返回值。  
6. `if`/`else`：条件判断语句。  
7. `for`：循环语句（含初始化、条件、更新表达式）。  
8. `for...in`：遍历对象可枚举属性（键名）。  
9. `for...of`：遍历可迭代对象（值，如数组、字符串）。  
10. `while`：条件为真时循环。  
11. `do...while`：先执行一次再判断条件的循环。  
12. `switch`：多分支条件判断（匹配`case`值）。  
13. `break`：跳出循环或`switch`。  
14. `continue`：跳过循环当前迭代。  
15. `try`/`catch`/`finally`：异常捕获与处理（`finally`必执行）。  
16. `throw`：主动抛出异常。  
17. `typeof`：检测数据类型（返回字符串，如`"string"`）。  
18. `instanceof`：检测对象是否属于某个构造函数（原型链判断）。  
19. `null`：表示空值（类型为`object`）。  
20. `undefined`：表示未定义（变量未赋值或属性不存在）。  
21. `true`/`false`：布尔值（逻辑判断的两种状态）。  
22. `this`：函数执行时的上下文对象（指向调用者）。  
23. `new`：实例化构造函数，创建对象。  
24. `class`：ES6+类定义（语法糖，基于原型）。  
25. `extends`：类继承（继承父类属性和方法）。  
26. `super`：调用父类构造函数或方法（子类中使用）。  
27. `static`：类的静态方法（属于类本身，不实例化可调用）。  
28. `constructor`：类的构造函数（实例化时自动执行）。  
29. `Array`：数组构造函数（创建数组或检测数组类型）。  
30. `Object`：对象构造函数（创建对象或检测对象类型）。  
31. `String`/`Number`/`Boolean`：基本类型的包装对象（如`new String("abc")`）。  
32. `Date`：日期时间处理（创建日期对象、格式化时间）。  
33. `RegExp`：正则表达式（匹配、替换字符串模式）。  
34. `Math`：数学工具类（静态方法，如`Math.random()`、`Math.PI`）。  
35. `JSON`：JSON数据处理（`JSON.parse()`解析、`JSON.stringify()`序列化）。  
36. `Map`：ES6+键值对集合（键可任意类型，有序）。  
37. `Set`：ES6+唯一值集合（无重复元素，有序）。  
38. `WeakMap`：弱引用`Map`（键为对象，不阻止垃圾回收）。  
39. `WeakSet`：弱引用`Set`（元素为对象，不阻止垃圾回收）。  
40. `Symbol`：ES6+唯一标识类型（不可重复，可作为对象属性名）。  
41. `BigInt`：ES10+大整数类型（处理超出`Number`范围的整数）。  
42. `NaN`：非数值（`isNaN()`检测，`NaN !== NaN`）。  
43. `Infinity`：无穷大（正数或负数，如`1 / 0`）。  
44. `void`：执行表达式并返回`undefined`（如`void 0`等价于`undefined`）。  
45. `delete`：删除对象属性（返回布尔值，无法删除原型属性）。  
46. `in`：判断对象是否包含某个属性（`"key" in obj`）。  
47. `of`：`for...of`循环的关键字（遍历可迭代对象的值）。  
48. `async`：声明异步函数（返回`Promise`对象）。  
49. `await`：等待`Promise`完成（仅在`async`函数中使用）。  
50. `Promise`：ES6+异步编程容器（三种状态：pending/resolved/rejected）。  


### 二、DOM/BOM操作（30个）
51. `document`：HTML文档对象（操作页面元素的入口）。  
52. `window`：浏览器窗口对象（全局对象，如`window.alert()`）。  
53. `document.getElementById`：通过ID获取单个元素（唯一）。  
54. `document.querySelector`：通过CSS选择器获取第一个匹配元素。  
55. `document.querySelectorAll`：通过CSS选择器获取所有匹配元素（返回类数组）。  
56. `getElementsByClassName`：通过类名获取元素集合（实时更新）。  
57. `getElementsByTagName`：通过标签名获取元素集合（实时更新）。  
58. `createElement`：创建新DOM元素（如`document.createElement("div")`）。  
59. `appendChild`：向父元素末尾添加子元素（移动已有元素）。  
60. `append`：向父元素末尾添加节点或字符串（ES6+，可多个参数）。  
61. `removeChild`：从父元素中移除子元素（需指定父元素）。  
62. `remove`：直接移除元素（ES6+，无需父元素）。  
63. `parentNode`：获取元素的父节点（包含文本节点）。  
64. `parentElement`：获取元素的父元素（仅元素节点）。  
65. `children`：获取元素的子元素集合（仅元素节点，类数组）。  
66. `childNodes`：获取元素的所有子节点（含文本、注释节点）。  
67. `classList`：元素类名操作对象（`add`/`remove`/`toggle`/`contains`）。  
68. `setAttribute`：设置元素属性（如`elem.setAttribute("src", "img.jpg")`）。  
69. `getAttribute`：获取元素属性值（如`elem.getAttribute("src")`）。  
70. `removeAttribute`：移除元素属性（如`elem.removeAttribute("src")`）。  
71. `style`：操作元素内联样式（如`elem.style.color = "red"`）。  
72. `innerHTML`：设置/获取元素的HTML内容（解析标签）。  
73. `textContent`：设置/获取元素的文本内容（不解析标签）。  
74. `innerText`：类似`textContent`，但受CSS样式影响（如隐藏文本不返回）。  
75. `addEventListener`：为元素绑定事件监听（如`click`、`scroll`）。  
76. `removeEventListener`：移除元素的事件监听（需与绑定参数一致）。  
77. `event`：事件对象（包含事件信息，如`event.target`、`event.type`）。  
78. `event.target`：触发事件的元素（实际点击的元素）。  
79. `event.currentTarget`：绑定事件的元素（监听的元素）。  
80. `event.preventDefault`：阻止事件默认行为（如表单提交、链接跳转）。  


### 三、数组与对象方法（30个）
81. `push`：向数组末尾添加元素（返回新长度，改变原数组）。  
82. `pop`：删除数组末尾元素（返回删除元素，改变原数组）。  
83. `unshift`：向数组开头添加元素（返回新长度，改变原数组）。  
84. `shift`：删除数组开头元素（返回删除元素，改变原数组）。  
85. `slice`：截取数组（返回新数组，不改变原数组，参数为起始/结束索引）。  
86. `splice`：修改数组（添加/删除/替换元素，返回删除元素，改变原数组）。  
87. `forEach`：遍历数组（无返回值，回调函数处理每个元素）。  
88. `map`：数组映射（返回新数组，每个元素为回调函数返回值）。  
89. `filter`：数组过滤（返回新数组，包含满足条件的元素）。  
90. `reduce`：数组归约（累加计算，返回最终结果，如求和、合并对象）。  
91. `reduceRight`：从数组末尾开始归约（与`reduce`方向相反）。  
92. `find`：查找数组中第一个满足条件的元素（返回元素，无则`undefined`）。  
93. `findIndex`：查找数组中第一个满足条件的元素索引（返回索引，无则`-1`）。  
94. `some`：判断数组是否有至少一个元素满足条件（返回布尔值）。  
95. `every`：判断数组是否所有元素满足条件（返回布尔值）。  
96. `sort`：数组排序（默认按字符串Unicode排序，可传比较函数）。  
97. `concat`：数组合并（返回新数组，不改变原数组）。  
98. `includes`：判断数组是否包含指定元素（返回布尔值，区分`NaN`）。  
99. `indexOf`：查找元素在数组中首次出现的索引（返回索引，无则`-1`）。  
100. `lastIndexOf`：查找元素在数组中最后出现的索引（返回索引，无则`-1`）。  
101. `join`：将数组元素拼接为字符串（默认逗号分隔，可指定分隔符）。  
102. `reverse`：反转数组（改变原数组，返回反转后的数组）。  
103. `flat`：数组扁平化（减少维度，如`[1,[2]]`→`[1,2]`，参数为深度）。  
104. `flatMap`：先映射再扁平化（相当于`map`+`flat(1)`）。  
105. `Object.keys`：获取对象所有可枚举属性名（返回数组）。  
106. `Object.values`：获取对象所有可枚举属性值（返回数组）。  
107. `Object.entries`：获取对象所有可枚举属性的键值对（返回`[key, value]`数组）。  
108. `Object.assign`：对象合并（浅拷贝，将源对象属性复制到目标对象）。  
109. `Object.freeze`：冻结对象（不可添加、删除、修改属性）。  
110. `hasOwnProperty`：判断对象是否自身拥有某个属性（不包含原型链）。  


### 四、异步与网络（20个）
111. `XMLHttpRequest`：传统AJAX请求对象（兼容旧浏览器）。  
112. `fetch`：现代AJAX请求API（基于`Promise`，支持跨域）。  
113. `axios`：常用HTTP请求库（基于`Promise`，支持拦截器、取消请求）。  
114. `Promise.resolve`：快速创建已 resolved 状态的`Promise`。  
115. `Promise.reject`：快速创建已 rejected 状态的`Promise`。  
116. `Promise.all`：等待所有`Promise`完成（全部 resolved 才返回，一个 rejected 则失败）。  
117. `Promise.race`：等待第一个完成的`Promise`（无论成功或失败）。  
118. `Promise.allSettled`：等待所有`Promise`完成（返回每个`Promise`的状态和结果）。  
119. `AbortController`：中断请求（如`fetch`、`axios`，通过`signal`控制）。  
120. `Blob`：二进制大对象（存储文件数据，如图片、PDF）。  
121. `FormData`：表单数据对象（用于上传文件或提交表单，支持`multipart/form-data`）。  
122. `FileReader`：读取文件内容（异步，支持`readAsText`、`readAsDataURL`等）。  
123. `WebSocket`：双向通信协议（服务器推送数据，如实时聊天）。  
124. `queueMicrotask`：将任务添加到微任务队列（优先级高于宏任务）。  
125. `requestAnimationFrame`：浏览器重绘前执行（用于动画，同步屏幕刷新率）。  
126. `cancelAnimationFrame`：取消`requestAnimationFrame`的动画。  
127. `IntersectionObserver`：监听元素是否进入视口（如懒加载图片）。  
128. `BroadcastChannel`：同源页面间通信（广播消息）。  
129. `Response`：`fetch`响应对象（包含状态码、 headers、响应体）。  
130. `Request`：`fetch`请求对象（配置请求方法、 headers、 body 等）。  


### 五、框架与工具（30个）
131. `React`：前端框架（组件化、虚拟DOM、单向数据流）。  
132. `Vue`：前端框架（双向绑定、渐进式、易上手）。  
133. `Angular`：前端框架（TypeScript、完整生态、依赖注入）。  
134. `Node.js`：服务端JavaScript运行环境（基于V8引擎，无浏览器DOM）。  
135. `Express`：Node.js轻量Web框架（路由、中间件）。  
136. `Koa`：Node.js现代Web框架（洋葱模型、异步中间件）。  
137. `Next.js`：React服务端渲染框架（SEO友好、路由自动配置）。  
138. `Nuxt.js`：Vue服务端渲染框架（基于Vue，支持SSR/SSG）。  
139. `TypeScript`：JavaScript超集（强类型、静态检查，编译为JS）。  
140. `Webpack`：前端构建工具（模块打包、代码分割、 loader 插件）。  
141. `Vite`：前端构建工具（快速热更新、原生ES模块，替代Webpack）。  
142. `Rollup`：模块打包工具（适合库打包，Tree-shaking更彻底）。  
143. `Babel`：JavaScript编译器（将ES6+转ES5，兼容旧浏览器）。  
144. `ESLint`：代码检查工具（规范语法、发现错误，可自定义规则）。  
145. `Prettier`：代码格式化工具（统一代码风格，支持多种语言）。  
146. `npm`：Node.js包管理工具（安装依赖、运行脚本）。  
147. `yarn`：替代npm的包管理工具（更快、缓存机制、.lock文件）。  
148. `pnpm`：高效包管理工具（节省磁盘空间，共享依赖）。  
149. `package.json`：项目配置文件（依赖、脚本、元信息）。  
150. `node_modules`：npm/yarn安装的依赖包目录。  
151. `CommonJS`：Node.js模块规范（`require`导入、`module.exports`导出）。  
152. `ES Modules`：浏览器/现代Node.js模块规范（`import`/`export`）。  
153. `Redux`：React状态管理库（单一数据源、不可变状态、纯函数）。  
154. `Pinia`：Vue3状态管理库（替代Vuex，更简洁、支持TypeScript）。  
155. `React Router`：React路由库（页面跳转、参数传递）。  
156. `Vue Router`：Vue路由库（路由配置、嵌套路由、守卫）。  
157. `Svelte`：前端框架（编译时优化，无虚拟DOM，生成原生JS）。  
158. `Deno`：安全的JavaScript/TypeScript运行时（替代Node.js，支持Web API）。  
159. `Electron`：桌面应用开发框架（用JS/HTML/CSS构建跨平台应用）。  
160. `React Native`：移动端应用开发框架（用React构建原生App）。  


### 六、性能优化与安全（15个）
161. `debounce`：防抖（短时间内多次触发，只执行最后一次）。  
162. `throttle`：节流（短时间内多次触发，间隔固定时间执行一次）。  
163. `memoization`：记忆化（缓存函数计算结果，避免重复计算）。  
164. `lazy loading`：懒加载（延迟加载非首屏资源，如图片、组件）。  
165. `code splitting`：代码分割（将代码拆分为小块，按需加载）。  
166. `tree shaking`：摇树优化（移除未使用的代码，减小打包体积）。  
167. `CORS`：跨域资源共享（浏览器安全机制，允许跨域请求）。  
168. `XSS`：跨站脚本攻击（注入恶意脚本，窃取信息）。  
169. `CSRF`：跨站请求伪造（利用用户身份发起恶意请求）。  
170. `sanitize`：输入 sanitize（过滤恶意字符，防止XSS）。  
171. `web worker`：后台线程（处理耗时操作，不阻塞主线程）。  
172. `service worker`：离线缓存（PWA核心，拦截请求、缓存资源）。  
173. `subresource integrity`：子资源完整性（验证CDN资源是否被篡改）。  
174. `HTTP/2`：HTTP协议新版本（多路复用、头部压缩，提升性能）。  
175. `CDN`：内容分发网络（就近分发静态资源，提升访问速度）。  


### 七、其他常用概念（25个）
176. `RESTful API`：REST风格接口设计（基于HTTP方法，资源为中心）。  
177. `GraphQL`：API查询语言（按需获取数据，替代REST）。  
178. `JWT`：JSON Web Token（无状态身份验证，传递用户信息）。  
179. `OAuth`：授权协议（第三方登录，如微信、QQ登录）。  
180. `Serverless`：无服务器架构（无需管理服务器，按使用付费）。  
181. `PWA`：渐进式Web应用（离线访问、推送通知、安装到桌面）。  
182. `SPA`：单页应用（无刷新跳转，如React/Vue项目）。  
183. `SSR`：服务端渲染（页面在服务器生成HTML，提升SEO）。  
184. `SSG`：静态站点生成（构建时生成HTML，如Next.js、Nuxt.js）。  
185. `CSR`：客户端渲染（浏览器生成HTML，SEO较差）。  
186. `JSONP`：跨域请求方案（利用`<script>`标签，仅支持GET）。  
187. `iframe`：内嵌框架（在页面中嵌入另一个页面）。  
188. `Web Component`：Web组件（自定义元素、Shadow DOM、HTML模板）。  
189. `Shadow DOM`：影子DOM（隔离组件样式和结构，避免冲突）。  
190. `Custom Element`：自定义元素（创建可复用的HTML标签）。  
191. `Closure`：闭包（函数嵌套，内部函数访问外部函数变量）。  
192. `Prototype`：原型（JS继承基础，对象通过`__proto__`指向原型）。  
193. `Inheritance`：继承（子类获取父类的属性和方法）。  
194. `Polymorphism`：多态（同一方法在不同对象上有不同实现）。  
195. `Encapsulation`：封装（隐藏对象内部细节，仅暴露公共接口）。  
196. `Currying`：柯里化（将多参数函数转为单参数函数链）。  
197. `Compose`：函数组合（将多个函数组合为一个函数，从右到左执行）。  
198. `Middleware`：中间件（请求/响应处理的拦截器，如Express/Koa中间件）。  
199. `Namespace`：命名空间（避免变量名冲突，如`const MyApp = { ... }`）。  
200. `Type Coercion`：类型强制转换（JS自动转换数据类型，如`1 + "2"`→`"12"`）。