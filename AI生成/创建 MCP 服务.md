# MCP是什么及如何创建

## MCP的定义

**MCP(Model Context Protocol)**是由Anthropic公司于2024年11月推出的**开放标准协议**，被称为"AI应用的USB-C"，用于标准化大语言模型(LLM)与外部工具、数据源的交互方式。

它解决了AI模型只能"对话"却无法"执行操作"的局限，使ChatGPT、Claude等模型能够安全访问：
- 数据库查询
- 文件管理
- API服务
- 自定义功能
- 等等

## MCP的核心架构

MCP采用**客户端-服务器(C/S)架构**，包含三大组件：

1. **MCP Hosts**: 运行AI模型的应用(如Claude Desktop、Cursor)
2. **MCP Clients**: 在Host内负责与服务器通信的模块
3. **MCP Servers**: 核心组件，通过标准化协议提供工具和数据

## 创建MCP服务的步骤

### 1. 准备开发环境

**Python环境**（推荐，最简单）：
```bash
# 创建项目目录
mkdir my-mcp-server
cd my-mcp-server

# 安装MCP库
pip install mcp
```

**TypeScript环境**：
```bash
# 创建项目
npm init -y
npm install @modelcontextprotocol/sdk
```

### 2. 编写基础MCP服务器代码

**Python版本**：
```python
# main.py
from mcp import McpServer, tool

# 创建MCP服务器实例
server = McpServer("My First MCP Server")

# 定义一个可被AI调用的工具
@tool("greet", "向用户打招呼")
def greet(name: str) -> str:
    return f"你好, {name}!"

# 启动服务器（stdio传输方式，适合本地测试）
server.run(transport="stdio")
```

**TypeScript版本**：
```typescript
// src/index.ts
import { McpServer, tool } from "@modelcontextprotocol/sdk";

// 创建服务器
const server = new McpServer("My First MCP Server");

// 定义工具
@tool("greet", "向用户打招呼")
function greet(name: string): string {
    return `你好, ${name}!`;
}

// 启动服务器
server.run({ transport: "stdio" });
```

### 3. 定义更多功能

MCP服务器可提供三类主要功能：

- **工具(Tools)**: 执行特定操作的函数（如查询天气、发送邮件）
- **提示模板(Prompts)**: 预定义的对话模板，帮助用户完成任务
- **数据源(Data Sources)**: 提供访问文件、数据库的能力

**示例：添加一个天气查询工具**：
```python
import requests
from mcp import McpServer, tool

server = McpServer("Weather MCP Server")

@tool("get_weather", "查询城市天气")
def get_weather(city: str) -> str:
    # 调用天气API
    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q={city}")
    data = response.json()
    return f"{city} 当前天气: {data['current']['condition']['text']}, 温度: {data['current']['temp_c']}°C"

server.run(transport="stdio")
```

### 4. 启动并测试服务

**本地测试(Stdio模式)**：
```bash
# Python
python main.py

# TypeScript
npm run start
```

Stdio模式下，服务器通过命令行与MCP客户端通信，适合开发调试。

**远程服务(SSE/HTTP模式)**：
如需远程访问，需配置SSE(Server-Sent Events)或HTTP传输：
```python
# 使用SSE传输（需配合网关如Higress）
server.run(transport="sse", host="0.0.0.0", port=8080)
```

### 5. 连接到AI模型

将MCP服务器连接到支持MCP的AI应用（如Claude Desktop）：

1. 在AI应用中找到MCP设置
2. 添加服务器地址（如`http://your-server.com`或`stdio://`）
3. 授权访问权限
4. 开始使用服务！

## 总结

MCP是AI与外部世界连接的"通用接口"，通过简单几步即可创建自己的MCP服务，让AI模型能够执行各种操作。

**创建MCP服务的核心步骤**：
1. 安装依赖
2. 编写服务器代码，定义工具
3. 启动服务
4. 在AI应用中连接使用

现在，你可以开发各种MCP服务，如文件管理器、数据库查询工具、API集成等，让AI真正成为你的全能助手！