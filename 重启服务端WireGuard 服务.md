在WireGuard配置修改后，需要**重启服务端/客户端的WireGuard服务**才能让配置生效，不同系统（Linux服务端、Linux客户端、Windows客户端）的重启方式不同，以下是详细操作步骤及验证方法：

### 一、Linux服务端重启（核心）
Linux系统中WireGuard通常通过`wg-quick`工具管理，结合系统服务（`systemd`）实现开机自启和重启，主流发行版（Ubuntu/CentOS/Debian）通用：

#### 1. 重启WireGuard服务（指定网卡，默认wg0）
```bash
# 停止服务（可选，也可直接重启）
wg-quick down wg0
# 启动/重启服务（加载新配置）
wg-quick up wg0

# 或通过systemd服务重启（推荐，需先创建服务文件）
systemctl restart wg-quick@wg0
```
**说明**：`wg0`是WireGuard的虚拟网卡名称，需与配置文件名称一致（若配置文件为`wg1.conf`，则对应`wg1`）。

#### 2. 验证服务是否重启成功
```bash
# 查看WireGuard运行状态
wg show wg0
# 查看系统服务状态
systemctl status wg-quick@wg0
```
- 若输出中`interface: wg0`、`public key`、`listening port: 21820`与配置一致，且`Active: active (exited)`，则重启成功。
- 若出现错误，可通过`journalctl -u wg-quick@wg0`查看日志排查（如配置语法错误、端口被占用）。

### 二、Linux客户端重启
操作与服务端一致，仅需指定客户端的WireGuard网卡（通常也是`wg0`，若多网卡可自定义）：
```bash
# 重启客户端WireGuard
wg-quick down wg0 && wg-quick up wg0
# 验证状态
wg show wg0
```

### 三、Windows客户端重启
Windows下WireGuard有**图形界面版**和**命令行版**，重启方式如下：

#### 1. 图形界面版（推荐）
1. 打开WireGuard客户端，找到对应的隧道（如`WG-Client`）。
2. 点击隧道右侧的**Disconnect**（断开），再点击**Connect**（连接），即可完成重启（加载新配置）。

#### 2. 命令行版（管理员权限）
```powershell
# 停止隧道（替换为你的隧道名称，如"WG-Client"）
wg-quick down "WG-Client"
# 启动隧道
wg-quick up "WG-Client"
```

### 四、重启后关键验证步骤
1. **服务端验证客户端连接**：
   在服务端执行`wg show wg0`，若输出中出现客户端的`peer`信息（公钥、允许的IP、最新握手时间），说明客户端已成功连接。
   ```bash
   # 示例正常输出
   peer: HLR8ZUWInMYc+8qn9WR8DxH8fo8X3boHNr0FGILyWh4=
     allowed ips: 10.0.0.3/32
     latest handshake: 10 seconds ago
     transfer: 128 B received, 256 B sent
   ```

2. **客户端验证连通性**：
   - 客户端`ping 10.0.0.1`（服务端VPN内网IP），测试与服务端的互通。
   - 客户端`ping 8.8.8.8`（公网IP），测试是否能通过服务端访问公网（需服务端开启IP转发和iptables规则）。

### 五、常见重启失败排查
1. **端口被占用**：服务端`ListenPort=21820`被其他程序占用，可通过`ss -ulnp | grep 21820`查看占用进程，更换端口或关闭占用程序。
2. **配置语法错误**：用`wg-quick check wg0`检查配置文件语法，重点排查密钥格式、IP网段、命令分隔符（`;`）。
3. **权限问题**：Linux下配置文件（`/etc/wireguard/wg0.conf`）需保证`600`权限（`chmod 600 /etc/wireguard/wg0.conf`），否则WireGuard拒绝加载。