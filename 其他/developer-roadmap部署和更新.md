### 部署 `developer-roadmap` 到 Linux 服务器（宝塔面板）
`developer-roadmap` 是基于前端技术构建的静态/动态混合项目（核心为静态资源 + Node.js 构建），以下是结合宝塔面板的完整部署步骤：

### 一、前置准备
1. **服务器环境（宝塔面板）**
   - 确保服务器已安装宝塔面板，且预装：`Node.js`（16+）、`Git`、`Nginx`（宝塔默认安装）。
   - 宝塔面板 → 软件商店 → 安装「Node.js 版本管理器」，选择 16+/18+ 版本安装；
   - 宝塔面板 → 终端 → 执行 `git --version` 验证 Git，未安装则执行 `yum install git -y`（CentOS）或 `apt install git -y`（Ubuntu）。

2. **克隆代码库**
   宝塔面板 → 终端，执行以下命令克隆代码到服务器（推荐克隆到 `/www/wwwroot/` 目录）：
   ```bash
   # 进入网站根目录
   cd /www/wwwroot/
   # 克隆仓库
   git clone https://github.com/kamranahmedse/developer-roadmap.git
   # 进入项目目录
   cd developer-roadmap
   ```

### 二、构建项目（生成静态部署文件）
该项目需要通过 `npm` 构建生成可部署的静态资源：
1. **安装依赖**
   在项目目录执行：
   ```bash
   # 安装项目依赖（若网速慢，可切换淘宝源：npm config set registry https://registry.npmmirror.com）
   npm install
   ```
2. **构建生产包**
   执行构建命令生成 `dist` 目录（静态部署核心目录）：
   ```bash
   # 构建生产环境包
   npm run build
   ```
   构建完成后，项目目录下会生成 `dist` 文件夹，内含所有可部署的静态文件。

### 三、宝塔面板配置 Nginx 站点
1. **创建站点**
   - 宝塔面板 → 网站 → 添加站点：
     - 域名：填写你的域名（如 `roadmap.example.com`），若无域名可填服务器 IP；
     - 根目录：选择 `/www/wwwroot/developer-roadmap/dist`（关键：指向构建后的 dist 目录）；
     - PHP 版本：选择「纯静态」（无需 PHP）；
     - 其余默认，点击「提交」。

2. **配置 Nginx 伪静态（可选，解决路由问题）**
   该项目为单页应用（SPA），需配置 Nginx 伪静态避免刷新 404：
   - 宝塔面板 → 网站 → 对应站点 → 设置 → 伪静态 → 选择「自定义」，粘贴以下规则：
     ```nginx
     location / {
         try_files $uri $uri/ /index.html;
     }
     # 禁用缓存的配置（可选，确保更新生效）
     location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
         expires 1d;
         add_header Cache-Control "public, max-age=86400";
     }
     ```
   - 点击「保存」，重启 Nginx（宝塔面板 → 软件商店 → Nginx → 重启）。

### 四、访问验证
1. 打开浏览器，访问你的域名/服务器 IP（如 `http://roadmap.example.com` 或 `http://服务器IP`），即可看到 `developer-roadmap` 页面。
2. 若无法访问：
   - 检查宝塔面板 → 安全 → 防火墙，放行 80/443 端口；
   - 检查 Nginx 配置：宝塔面板 → 网站 → 对应站点 → 设置 → 配置文件，确认根目录指向 `dist` 且伪静态规则生效；
   - 检查构建是否成功：终端进入 `dist` 目录，确认有 `index.html` 等文件。

### 五、后续维护（更新项目）
若需要同步官方最新代码：
1. 宝塔面板 → 终端，执行：
   ```bash
   cd /www/wwwroot/developer-roadmap
   # 拉取最新代码
   git pull
   # 重新安装依赖（若有新增依赖）
   npm install
   # 重新构建
   npm run build
   ```
2. 构建完成后，刷新浏览器即可看到更新。

### 关键注意事项
1. **Node.js 版本**：项目要求 Node.js ≥16，若版本过低会导致构建失败，可通过宝塔「Node.js 版本管理器」切换；
2. **根目录指向**：必须指向 `dist` 目录（构建后的静态文件），而非项目根目录；
3. **伪静态配置**：SPA 应用必须配置 `try_files $uri $uri/ /index.html`，否则刷新页面会 404；
4. **权限问题**：若构建/访问报错，可执行 `chmod -R 755 /www/wwwroot/developer-roadmap` 赋予目录权限。

通过以上步骤，即可将 `developer-roadmap` 稳定部署在宝塔面板管理的 Linux 服务器上。