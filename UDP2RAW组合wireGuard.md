从你解压的结果来看，UDP2RAW 提供了**不同架构**和**加密优化版本**的二进制文件，你的服务器是 **x86_64（amd64）** 架构（阿里云服务器默认主流架构），因此应选择 `udp2raw_amd64` 主程序（若服务器支持硬件 AES 加速，可选择 `udp2raw_amd64_hw_aes`）。

下面基于你的解压结果，完成**UDP2RAW 安装**和**后续配置的适配调整**（你的系统是 CentOS，需注意防火墙/服务管理与 Ubuntu 的差异）：

### 步骤 1：完成 UDP2RAW 安装（针对你的解压结果）
1. **进入解压后的目录**（若你是在 `~` 目录解压，直接执行）：
   ```bash
   cd ~  # 回到解压目录（即udp2raw_binaries.tar.gz所在目录）
   ```
2. **选择并移动主程序到系统路径**（全局可调用）：
   ```bash
   # 选择基础版amd64程序（兼容性最好）
   mv udp2raw_amd64 /usr/local/bin/udp2raw
   # 若服务器支持硬件AES加速，可选优化版（性能更好）：
   # mv udp2raw_amd64_hw_aes /usr/local/bin/udp2raw
   ```
3. **赋予执行权限**：
   ```bash
   chmod +x /usr/local/bin/udp2raw
   ```
4. **验证安装**：
   ```bash
   udp2raw -h
   ```
   若输出 UDP2RAW 的帮助信息，说明安装成功。

### 步骤 2：CentOS 系统的防火墙/安全组适配
你的服务器是阿里云 CentOS，需开放 UDP2RAW 监听的 TCP 端口（如 443），分为**系统防火墙（firewalld）**和**阿里云安全组**两层配置：

#### 2.1 开放系统防火墙端口
```bash
# 临时开放443/TCP（重启后失效）
firewall-cmd --add-port=443/tcp --zone=public
# 永久开放443/TCP（重启后生效）
firewall-cmd --add-port=443/tcp --zone=public --permanent
# 重新加载防火墙规则
firewall-cmd --reload
```

#### 2.2 开放阿里云安全组
登录阿里云控制台 → 云服务器 ECS → 实例 → 你的服务器 → 安全组 → 配置规则 → **入方向添加规则**：
- 端口范围：`443/443`
- 协议：`TCP`
- 源地址：`0.0.0.0/0`（或限制为你的客户端 IP，更安全）

### 步骤 3：UDP2RAW 服务端启动（CentOS 适配）
沿用之前的核心参数，直接在你的 CentOS 服务端启动 UDP2RAW（建议后台运行）：
```bash
# 后台启动UDP2RAW服务端，日志输出到/var/log（需先创建日志目录）
mkdir -p /var/log/udp2raw
nohup udp2raw -s -l 0.0.0.0:443 -r 127.0.0.1:51820 -k "your_password" --raw-mode tcp -a > /var/log/udp2raw/udp2raw-server.log 2>&1 &
```

### 步骤 4：CentOS 下设置 UDP2RAW 开机自启（systemd 服务适配）
CentOS 同样支持 systemd 服务，创建服务文件的步骤与 Ubuntu 一致，仅需注意**路径和依赖**：
1. **创建服务文件**：
   ```bash
   vi /etc/systemd/system/udp2raw-server.service
   ```
2. **写入以下内容**（与 Ubuntu 一致，CentOS 兼容）：
   ```ini
   [Unit]
   Description=UDP2RAW Server for WireGuard
   After=network.target wg-quick@wg0.service
   Wants=network.target

   [Service]
   Type=simple
   ExecStart=/usr/local/bin/udp2raw -s -l 0.0.0.0:443 -r 127.0.0.1:51820 -k "your_password" --raw-mode tcp -a
   Restart=on-failure
   RestartSec=5
   StandardOutput=append:/var/log/udp2raw/udp2raw-server.log
   StandardError=append:/var/log/udp2raw/udp2raw-server.log

   [Install]
   WantedBy=multi-user.target
   ```
3. **启用并启动服务**：
   ```bash
   # 重新加载systemd
   systemctl daemon-reload
   # 设置开机自启
   systemctl enable udp2raw-server
   # 启动服务
   systemctl start udp2raw-server
   # 查看服务状态
   systemctl status udp2raw-server
   ```

### 关于解压文件中其他版本的说明
你解压出的其他二进制文件是针对不同架构/优化的版本，用途如下：
| 文件名                  | 适用场景                     |
|-------------------------|------------------------------|
| `udp2raw_arm`           | ARM 32位架构（如树莓派）|
| `udp2raw_arm_asm_aes`   | ARM 架构+汇编AES加速         |
| `udp2raw_mips24kc_be/le`| MIPS 架构（如部分路由器）|
| `udp2raw_x86`           | x86 32位系统                 |
| `*_hw_aes/_asm_aes`     | 硬件/汇编AES加密加速（性能更高）|

你的阿里云服务器是 `x86_64` 架构，选择 `udp2raw_amd64` 即可，若想启用 AES 加速，可替换为 `udp2raw_amd64_hw_aes`（需服务器 CPU 支持 AES-NI 指令集，阿里云服务器默认支持）。

### 后续验证
启动完成后，可通过以下命令检查进程和日志：
```bash
# 查看UDP2RAW进程
ps -ef | grep udp2raw
# 查看日志（排查错误）
tail -f /var/log/udp2raw/udp2raw-server.log
# 查看WireGuard状态
wg show wg0
```
客户端配置与之前一致，只需确保 UDP2RAW 客户端的密钥、封装模式（`tcp`）与服务端匹配，WireGuard 客户端连接本地 UDP2RAW 监听的 `127.0.0.1:51820` 即可。