# GitHub WebHook 实现自动部署：从新手到生产实践

要实现 GitHub 提交代码后自动触发服务器更新代码，核心思路是利用 **GitHub WebHook** + **服务器脚本** 来完成自动化部署。下面我会一步步教你实现这个完整流程，新手也能轻松上手。

### 一、整体实现思路

1. 在服务器上准备一个可执行的脚本，用于拉取最新代码、处理依赖（可选）、重启服务（可选）。

2. 在 GitHub 仓库配置 WebHook，指定触发事件（如 push）和服务器接收请求的地址。

3. 服务器上搭建一个简单的 HTTP 服务（用 Python/Node.js/PHP 均可），接收 GitHub 的 WebHook 请求，验证合法性后执行更新脚本。

### 二、服务器端准备工作

#### 1. 编写代码更新脚本（以 Shell 为例）

创建一个可执行的脚本文件（如 `deploy.sh`），放在服务器的安全目录下（如 `/home/your_user/deploy/`）：

```Bash

#!/bin/bash

# 配置项（根据你的实际情况修改）
REPO_DIR="/www/your_project"  # 你的代码仓库目录
GIT_USER="your_git_user"      # 服务器上的用户（避免权限问题）

# 进入代码目录
cd $REPO_DIR || { echo "目录不存在: $REPO_DIR"; exit 1; }

# 拉取最新代码（如果是私有仓库，需提前配置 SSH 免密拉取）
echo "开始拉取最新代码..."
git pull origin main  # 分支名根据你的仓库修改（如 master）

# 可选：安装依赖（如果是 Node.js 项目）
# npm install --production

# 可选：重启服务（如 Node.js 服务用 pm2）
# pm2 restart your_app_name

echo "代码更新完成！"
```

给脚本添加执行权限：

```Bash

chmod +x /home/your_user/deploy/deploy.sh
```

#### 2. 配置 Git 免密拉取（关键）

如果你的仓库是私有仓库，需要让服务器能免密拉取代码：

```Bash

# 1. 生成 SSH 密钥（一路回车，不设置密码）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 复制公钥（~/.ssh/id_ed25519.pub）
cat ~/.ssh/id_ed25519.pub

# 3. 把公钥添加到 GitHub 仓库的 Deploy keys 中
#    GitHub 仓库 → Settings → Deploy keys → Add deploy key → 粘贴公钥，勾选 Allow write access
```

#### 3. 搭建 HTTP 服务接收 WebHook 请求

这里用 **Python + Flask** 实现一个简单的 HTTP 服务，接收 GitHub 的 WebHook 请求并验证合法性：

##### （1）安装依赖

```Bash

pip install flask requests
```

##### （2）编写 WebHook 接收脚本（`webhook_server.py`）

```Python

from flask import Flask, request, abort
import hmac
import hashlib
import os
import subprocess

app = Flask(__name__)

# 配置项
SECRET_TOKEN = "your_github_webhook_secret"  # 和 GitHub WebHook 配置的密钥一致
DEPLOY_SCRIPT_PATH = "/home/your_user/deploy/deploy.sh"  # 你的更新脚本路径

def verify_signature(payload_body, signature_header):
    """验证 GitHub WebHook 请求的合法性"""
    if not signature_header:
        abort(403, "Missing signature header")
    
    # 拆分签名（格式：sha256=xxx）
    signature_parts = signature_header.split("=")
    if len(signature_parts) != 2 or signature_parts[0] != "sha256":
        abort(403, "Invalid signature format")
    
    # 计算请求体的 HMAC 签名
    mac = hmac.new(SECRET_TOKEN.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()
    
    # 安全比较签名（防止时序攻击）
    if not hmac.compare_digest(expected_signature, signature_header):
        abort(403, "Invalid signature")

@app.route('/webhook/deploy', methods=['POST'])
def handle_webhook():
    """处理 GitHub WebHook 请求"""
    # 1. 验证请求签名
    signature = request.headers.get('X-Hub-Signature-256')
    verify_signature(request.get_data(), signature)
    
    # 2. 验证触发事件（只处理 push 事件）
    event = request.headers.get('X-GitHub-Event')
    if event != 'push':
        return "忽略非 push 事件", 200
    
    # 3. 执行部署脚本
    try:
        # 执行脚本并捕获输出
        result = subprocess.run(
            DEPLOY_SCRIPT_PATH,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return f"部署成功：{result.stdout}", 200
    except subprocess.CalledProcessError as e:
        return f"部署失败：{e.stderr}", 500

if __name__ == '__main__':
    # 运行服务（监听 0.0.0.0，端口自定义，如 8080）
    # 生产环境建议用 Gunicorn + Nginx 反向代理
    app.run(host='0.0.0.0', port=8080, debug=False)
```

##### （3）后台运行 HTTP 服务

用 `nohup` 让服务后台运行，避免终端关闭后停止：

```Bash

nohup python3 /home/your_user/deploy/webhook_server.py > /home/your_user/deploy/webhook.log 2>&1 &
```

#### 4. 配置服务器防火墙（关键）

确保服务器开放你指定的端口（如 8080），允许 GitHub 的 IP 访问：

```Bash

# 以 CentOS 为例
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --reload

# 以 Ubuntu 为例
ufw allow 8080/tcp
ufw reload
```

### 三、GitHub 仓库配置 WebHook

1. 打开你的 GitHub 仓库 → 点击顶部 `Settings` → 左侧 `Webhooks` → 点击 `Add webhook`。

2. 填写关键配置：

    - **Payload URL**：服务器接收请求的地址，如 `http://你的服务器IP:8080/webhook/deploy`（如果用了 Nginx 反向代理，填域名地址）。

    - **Content type**：选择 `application/json`。

    - **Secret**：填写和脚本中 `SECRET_TOKEN` 一致的密钥（自定义，如随机字符串）。

    - **Which events would you like to trigger this webhook?**：选择 `Just the push event`（仅 push 触发）。

    - 勾选 `Active` → 点击 `Add webhook`。

### 四、测试验证

1. 本地修改代码，提交并推送到 GitHub：

    ```Bash
    
    git add .
    git commit -m "test webhook deploy"
    git push origin main
    ```

2. 查看 GitHub WebHook 日志：

GitHub 仓库 → Settings → Webhooks → 点击你配置的 WebHook → 查看 `Recent deliveries`，如果状态是 200，说明请求成功。

1. 查看服务器日志：

    ```Bash
    
    cat /home/your_user/deploy/webhook.log
    ```

2. 检查服务器代码目录，确认代码已更新。

### 五、进阶优化（可选）

1. **用 Nginx 反向代理**：将 HTTP 服务挂在域名下，并用 HTTPS（更安全）。

2. **添加日志记录**：在脚本中记录每次部署的时间、结果，方便排查问题。

3. **限制分支触发**：在 Python 脚本中判断推送的分支（如只允许 main 分支触发）。

4. **使用进程管理工具**：如 `supervisor` 管理 Python WebHook 服务，异常时自动重启。

---

### 总结

1. **核心原理**：GitHub WebHook 在代码 push 时向服务器发送 HTTP 请求，服务器验证请求合法性后执行更新脚本。

2. **关键步骤**：编写部署脚本 → 搭建 WebHook 接收服务 → 配置 GitHub WebHook → 验证测试。

3. **安全要点**：必须验证 WebHook 签名（防止恶意请求）、配置 Git 免密拉取（避免脚本执行时需要输入密码）。

按照这个流程，你就能实现提交代码后服务器自动更新了，整个过程对新手友好，且符合生产环境的最佳实践。
> （注：文档部分内容可能由 AI 生成）