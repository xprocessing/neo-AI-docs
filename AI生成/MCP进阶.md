MCP的深入用法涵盖**复杂工具设计、上下文会话管理、多数据源集成、安全认证、流式响应、多模态交互**等高级特性，这些功能能满足企业级应用的需求，让MCP服务更健壮、灵活和安全。以下是具体的深入用法解析：


## 一、复杂工具设计：参数验证与结构化输出
基础工具仅处理简单参数，深入场景中需**严格参数校验**、**嵌套结构**和**结构化返回**，可结合`Pydantic`实现类型安全（MCP原生支持Pydantic模型）。

### 1. 复杂参数校验（Pydantic集成）
```python
from mcp import McpServer, tool
from pydantic import BaseModel, Field, validator
from typing import List, Optional

# 定义结构化参数模型
class OrderQuery(BaseModel):
    user_id: str = Field(description="用户ID，格式为字母+数字组合")
    order_status: Optional[List[str]] = Field(default=["pending", "completed"], description="订单状态列表")
    start_date: str = Field(description="开始日期，格式YYYY-MM-DD")

    # 自定义参数校验
    @validator("user_id")
    def validate_user_id(cls, v):
        if not v.replace("_", "").isalnum():
            raise ValueError("用户ID只能包含字母、数字和下划线")
        return v

    @validator("start_date")
    def validate_date(cls, v):
        from datetime import datetime
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("日期格式错误，需为YYYY-MM-DD")

server = McpServer("Advanced Order Service")

# 绑定Pydantic模型作为参数
@tool("query_orders", "查询用户订单", parameters_schema=OrderQuery)
def query_orders(params: OrderQuery) -> dict:
    # 模拟数据库查询
    mock_orders = [
        {"order_id": "ORD123", "status": "completed", "amount": 99.9},
        {"order_id": "ORD456", "status": "pending", "amount": 199.9}
    ]
    # 根据参数过滤
    filtered = [o for o in mock_orders if o["status"] in params.order_status]
    return {
        "user_id": params.user_id,
        "count": len(filtered),
        "orders": filtered,
        "query_params": params.dict()
    }

server.run(transport="stdio")
```
**优势**：自动生成参数校验逻辑，AI调用时会严格遵循参数规则，减少无效请求；返回结构化数据，AI能更精准解析结果。


### 2. 工具依赖与上下文传递
MCP支持工具间共享上下文（如会话状态、用户身份），通过`context`参数实现跨工具数据传递。

```python
from mcp import McpServer, tool, Context

server = McpServer("Contextual Service")

# 初始化会话上下文
@tool("init_session", "初始化用户会话")
def init_session(user_id: str, context: Context) -> str:
    # 存储会话数据（内存级，生产环境可用Redis）
    context.set("user_session", {
        "user_id": user_id,
        "session_start": datetime.now().isoformat(),
        "history": []
    })
    return f"会话已初始化，用户ID：{user_id}"

# 读取上下文并记录操作
@tool("record_operation", "记录用户操作", context=True)
def record_operation(action: str, context: Context) -> str:
    session = context.get("user_session")
    if not session:
        raise ValueError("请先调用init_session初始化会话")
    
    session["history"].append({
        "action": action,
        "timestamp": datetime.now().isoformat()
    })
    context.set("user_session", session)  # 更新上下文
    return f"操作已记录，当前会话历史：{len(session['history'])}条"

# 查询会话上下文
@tool("get_session", "获取会话信息", context=True)
def get_session(context: Context) -> dict:
    return context.get("user_session", {})
```
**核心**：`Context`对象是会话级存储（默认内存，可扩展为Redis/Memcached），实现工具间状态共享，适合用户会话跟踪、多步骤任务（如订单流程）。


## 二、数据源深度集成：文件/数据库/API
MCP的**数据源（Data Sources）** 特性支持AI直接查询结构化数据（如数据库、CSV）或非结构化数据（如PDF），无需编写工具调用逻辑。

### 1. 数据库数据源（SQLite集成）
```python
from mcp import McpServer, DataSource
from sqlalchemy import create_engine, text
import pandas as pd

server = McpServer("Database MCP Server")

# 定义SQL数据源
class SQLDataSource(DataSource):
    def __init__(self):
        self.engine = create_engine("sqlite:///mydb.db")
        # 初始化测试表
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    price REAL,
                    stock INTEGER
                )
            """))
            conn.execute(text("INSERT OR IGNORE INTO products VALUES (1, 'Laptop', 5999, 10), (2, 'Phone', 3999, 20)"))
            conn.commit()

    async def query(self, query: str, **kwargs) -> pd.DataFrame:
        """AI可直接执行SQL查询，返回DataFrame"""
        try:
            df = pd.read_sql(text(query), self.engine)
            return df
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})

# 注册数据源
server.register_data_source("product_db", SQLDataSource())

server.run(transport="sse", host="0.0.0.0", port=8080)
```
**效果**：AI可直接提问“查询库存大于15的产品”，MCP会将自然语言转为SQL并执行，返回结果（需配合AI的SQL生成能力，如Claude的SQL插件）。


### 2. 非结构化数据源（PDF解析）
```python
from mcp import McpServer, DataSource
import PyPDF2
import pandas as pd

class PDFDataSource(DataSource):
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    async def query(self, page_num: int = None, **kwargs) -> pd.DataFrame:
        """提取PDF文本，支持按页码查询"""
        with open(self.pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            if page_num is None:
                text = "\n".join([page.extract_text() for page in reader.pages])
            else:
                text = reader.pages[page_num-1].extract_text()
        
        return pd.DataFrame({"page": [page_num or "all"], "content": [text]})

server = McpServer("PDF MCP Server")
server.register_data_source("report_pdf", PDFDataSource("annual_report.pdf"))

server.run(transport="stdio")
```
**应用场景**：AI可直接分析PDF文档内容，无需手动提取文本。


## 三、提示模板（Prompts）：标准化对话流程
MCP的**提示模板**允许预定义对话模板，AI可直接调用模板完成标准化任务（如生成邮件、写测试用例），避免重复编写提示词。

```python
from mcp import McpServer, PromptTemplate

server = McpServer("Prompt Template Server")

# 定义邮件生成模板
email_template = PromptTemplate(
    name="generate_email",
    description="生成商务邮件",
    template="""
    收件人：{recipient}
    主题：{subject}
    正文：
    尊敬的{recipient}：
    {content}
    
    此致
    {sender}
    {date}
    """,
    parameters=["recipient", "subject", "content", "sender", "date"]
)

# 定义测试用例模板
test_template = PromptTemplate(
    name="generate_testcase",
    description="生成API测试用例",
    template="""
    API名称：{api_name}
    请求方法：{method}
    测试用例：
    1. 正常请求：{normal_request} → 预期响应：{normal_response}
    2. 参数缺失：{missing_param_request} → 预期响应：{error_response}
    """,
    parameters=["api_name", "method", "normal_request", "normal_response", "missing_param_request", "error_response"]
)

# 注册模板
server.register_prompt_template(email_template)
server.register_prompt_template(test_template)

server.run(transport="stdio")
```
**使用方式**：AI可调用`generate_email`模板，传入参数直接生成规范邮件，提升对话效率。


## 四、安全与认证：保护MCP服务
生产环境中需对MCP服务做**认证授权**，防止未授权访问。MCP支持JWT、API Key等认证方式。

### 1. API Key认证
```python
from mcp import McpServer, tool
from mcp.auth import AuthMiddleware

server = McpServer("Authenticated MCP Server")

# 定义合法API Key列表（生产环境建议存储在环境变量/数据库）
VALID_API_KEYS = {"user1_key": "user1", "admin_key": "admin"}

# 实现认证中间件
class APIKeyAuth(AuthMiddleware):
    async def authenticate(self, request):
        """从请求头获取API Key并验证"""
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in VALID_API_KEYS:
            raise PermissionError("无效的API Key")
        # 将用户信息存入请求上下文
        request.context["user"] = VALID_API_KEYS[api_key]
        return True

# 注册认证中间件
server.add_middleware(APIKeyAuth())

# 受保护的工具（需认证）
@tool("admin_operation", "管理员操作", require_auth=True)
def admin_operation(context) -> str:
    user = context.get("user")
    if user != "admin":
        raise PermissionError("仅管理员可执行此操作")
    return "管理员操作执行成功"

server.run(transport="sse", host="0.0.0.0", port=8080)
```


### 2. JWT认证（更安全的会话认证）
```python
import jwt
from datetime import datetime, timedelta
from mcp import McpServer
from mcp.auth import AuthMiddleware

SECRET_KEY = "your-secret-key"  # 生产环境用环境变量

class JWTAuth(AuthMiddleware):
    async def authenticate(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # 检查token过期
            if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                raise PermissionError("Token已过期")
            request.context["user"] = payload["sub"]
            return True
        except jwt.InvalidTokenError:
            raise PermissionError("无效的JWT Token")

server = McpServer("JWT Auth Server")
server.add_middleware(JWTAuth())

# 生成Token的工具（公开接口）
@tool("generate_token", "生成访问Token", require_auth=False)
def generate_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

server.run(transport="sse", port=8080)
```


## 五、流式响应：处理大数据/实时输出
对于耗时任务（如大文件处理、批量查询），MCP支持**流式响应**，实时返回结果而非等待全部完成。

```python
from mcp import McpServer, tool
import asyncio

server = McpServer("Streaming MCP Server")

@tool("stream_logs", "流式返回系统日志")
async def stream_logs(log_file: str) -> str:
    """异步流式读取日志文件，逐行返回"""
    with open(log_file, "r") as f:
        for line in f:
            yield line.strip()  # 使用yield实现流式输出
            await asyncio.sleep(0.1)  # 模拟延迟

server.run(transport="sse", port=8080)
```
**效果**：AI端会实时接收每一行日志，无需等待文件读取完毕，适合处理大文件或实时监控场景。


## 六、多模态支持：处理图片/音频
MCP支持多模态交互（如接收图片URL并分析内容），结合OCR或视觉模型实现跨模态处理。

```python
from mcp import McpServer, tool
import requests
from PIL import Image
from io import BytesIO
import pytesseract

server = McpServer("Multimodal MCP Server")

@tool("analyze_image", "分析图片内容（OCR+描述）")
async def analyze_image(image_url: str) -> dict:
    # 下载图片
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    # OCR提取文本
    text = pytesseract.image_to_string(img)
    
    # 调用视觉模型（如CLIP）生成描述（需安装transformers）
    from transformers import CLIPProcessor, CLIPModel
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    inputs = processor(images=img, return_tensors="pt")
    # 此处可结合文本提示生成描述，简化示例直接返回OCR结果
    return {
        "ocr_text": text,
        "image_size": img.size,
        "format": img.format
    }

server.run(transport="stdio")
```


## 七、错误处理与日志：提升服务稳定性
### 1. 自定义错误处理
```python
from mcp import McpServer, tool, McpError

server = McpServer("Error Handling Server")

# 自定义异常
class BusinessError(McpError):
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code

@tool("divide", "除法运算")
def divide(a: float, b: float) -> float:
    if b == 0:
        raise BusinessError("除数不能为0", code="DIVISION_BY_ZERO")
    return a / b

# 全局错误处理器
@server.error_handler(BusinessError)
def handle_business_error(error: BusinessError):
    return {
        "error": error.message,
        "code": error.code,
        "status": "failed"
    }

server.run(transport="stdio")
```


### 2. 日志集成（使用logging模块）
```python
import logging
from mcp import McpServer, tool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("mcp_server.log"), logging.StreamHandler()]
)
logger = logging.getLogger("mcp_server")

server = McpServer("Logging MCP Server")

@tool("critical_operation", "关键操作")
def critical_operation():
    logger.info("关键操作执行开始")
    try:
        # 业务逻辑
        result = "操作成功"
        logger.info(f"关键操作执行完成：{result}")
        return result
    except Exception as e:
        logger.error(f"关键操作失败：{str(e)}", exc_info=True)
        raise

server.run(transport="sse", port=8080)
```


## 八、部署与扩展：生产环境最佳实践
### 1. 多进程/多线程部署
使用`uvicorn`或`gunicorn`实现多进程部署，提升并发能力：
```bash
# 安装依赖
pip install uvicorn gunicorn

# 启动命令（gunicorn）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker mcp_server:server
```


### 2. 负载均衡（Nginx反向代理）
```nginx
# nginx.conf
server {
    listen 80;
    server_name mcp.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # 支持SSE流式响应
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        chunked_transfer_encoding off;
    }
}
```


## 总结：深入用法的核心价值
MCP的深入用法围绕**“增强工具能力、保障安全性、提升可扩展性”**展开，通过结构化参数、上下文管理、数据源集成、认证授权等特性，可构建企业级的AI协作服务：
- **复杂业务场景**：支持多步骤任务、会话跟踪、批量处理；
- **安全合规**：认证授权、日志审计满足企业安全要求；
- **高性能**：流式响应、多进程部署适配高并发；
- **多模态**：打通文本、图片、音频的交互壁垒。

结合这些特性，你可以开发如“AI驱动的智能客服后台”“企业知识库查询系统”“自动化数据分析工具”等复杂MCP服务，真正释放AI的生产力！