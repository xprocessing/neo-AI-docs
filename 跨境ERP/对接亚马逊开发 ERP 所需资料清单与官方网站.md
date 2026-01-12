# 对接亚马逊开发ERP所需资料清单与官方网站

以下是开发亚马逊ERP对接所需的核心资料分类列表及官方资源，帮助你系统了解SP-API（Amazon Selling Partner API）开发流程与技术细节。

---

### 一、核心认证与账号准备资料

| 资料名称 | 说明 | 官方网站 |
|---------|------|---------|
| 解决方案提供商门户账户 | 用于注册应用程序和管理API权限 | https://sellercentral.amazon.com/solutions-providers/register  |
| LWA应用ID和客户端密钥 | Login with Amazon认证凭证 | https://developer.amazon.com/login-with-amazon/console/site/lwa/  |
| AWS访问密钥与密钥 | 用于API请求签名 | https://console.aws.amazon.com/iam/  |
| IAM角色ARN | 授权SP-API访问权限 | https://console.aws.amazon.com/iam/  |
| Refresh Token | 长期授权令牌，用于获取访问令牌 | 需通过OAuth 2.0流程获取  |
| 开发者资料申请表 | 描述应用功能、数据使用和安全措施 | 解决方案提供商门户内提交  |
| 信用卡/借记卡 | 用于账户验证 | 绑定到AWS和解决方案提供商账户  |

---

### 二、官方API文档与指南（SP-API核心）

| 文档类型 | 核心内容 | 官方网站 |
|---------|---------|---------|
| SP-API总览 | 介绍RESTful API架构、认证流程和迁移指南 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/welcome  |
| 入门指南 | 从注册到首次调用的完整步骤 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/onboarding-overview  |
| 认证与授权文档 | OAuth 2.0、AWS SigV4、RDT（受限数据令牌）说明 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/authorization-overview  |
| API参考文档 | 所有API端点、请求参数和响应结构 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/reference  |
| 沙箱测试指南 | 测试环境使用说明，避免影响生产数据 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/sandbox-overview  |
| 数据保护与合规文档 | PII（个人身份信息）处理要求 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/data-protection  |
| 错误代码参考 | 常见错误处理指南 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/error-codes  |

---

### 三、关键业务API分类资料

| API类别 | 功能说明 | 官方文档链接 |
|---------|---------|------------|
| 订单API | 订单列表、详情、买家信息获取 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/orders-api-v0-reference  |
| 库存API | 库存水平、库存调整、库存规划 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/inventory-api-v1-reference |
| 商品信息API | 商品详情、价格、分类、图片管理 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/catalog-items-api-v0-reference |
| 财务API | 交易记录、付款详情、费用计算 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/finances-api-reference |
| 配送API | 卖家自配送和亚马逊物流（FBA）管理 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/merchant-fulfillment-api-v0-use-case-guide  |
| 报告API | 生成和下载销售、库存、广告等报告 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/reports-api-reference |
| 上传数据API | 批量操作商品、订单、库存数据 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/feeds-api-reference |

---

### 四、开发工具与SDK资源

| 工具类型 | 用途 | 官方/推荐链接 |
|---------|------|-------------|
| SP-API模型仓库 | OpenAPI规范和JSON模式定义 | https://github.com/amzn/selling-partner-api-models  |
| 官方SDK | Java、Python、C#等语言客户端 | https://developer-docs.amazon.com/sp-api/docs/code-samples  |
| Postman集合 | 预配置API请求模板 | https://developer-docs.amazon.com/sp-api/docs/postman-collections |
| API健康仪表板 | 监控API可用性和性能 | https://developer-docs.amazon.com/sp-api/docs/api-health-dashboard  |
| SP-API实操训练营 | AWS中国团队提供的中文入门指南 | https://www.spapi.org.cn/cn/intro.html  |

---

### 五、区域与市场特定资料

| 区域 | 终端节点 | AWS区域 | 官方链接 |
|-----|---------|---------|---------|
| 北美 | https://sellingpartnerapi-na.amazon.com | us-east-1 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/regional-endpoints  |
| 欧洲 | https://sellingpartnerapi-eu.amazon.com | eu-west-1 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/regional-endpoints  |
| 远东 | https://sellingpartnerapi-fe.amazon.com | us-west-2 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/regional-endpoints  |
| 中国卖家指南 | 针对中国卖家的特殊要求 | https://developer.amazonservices.com/zh-cn  |

---

### 六、合规与安全必备资料

| 资料名称 | 核心要求 | 官方链接 |
|---------|---------|---------|
| 数据保护协议 | 处理亚马逊数据的合规要求 | 解决方案提供商门户内签署  |
| 安全最佳实践 | API调用安全、数据存储加密指南 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/security-best-practices |
| 隐私政策模板 | 应用需提供的用户隐私说明 | https://developer.amazon.com/docs/login-with-amazon/privacy-notice.html |
| 审计准备指南 | 亚马逊可能进行的安全审计要求 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/audit-readiness  |

---

### 七、MWS到SP-API迁移资料（如适用）

| 迁移资料 | 说明 | 官方链接 |
|---------|------|---------|
| MWS迁移指南 | 从旧版MWS API迁移到SP-API的步骤 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/migrating-from-mws  |
| MWS凭证映射 | 如何将MWS凭证转换为SP-API凭证 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/migration-credentials |
| 过渡期支持说明 | MWS停用时间表和临时解决方案 | https://developer-docs.amazon.com/sp-api/lang-zh_CN/docs/mws-deprecation |

---

### 八、ERP开发关键业务数据模型

| 数据模型 | 核心字段 | 关联API |
|---------|---------|---------|
| 订单模型 | 订单ID、买家信息、商品列表、金额、状态 | 订单API、订单商品API  |
| 库存模型 | ASIN、SKU、可用库存、预留库存、FBA库存 | 库存API、报告API |
| 商品模型 | ASIN、SKU、标题、价格、分类、图片URL | 商品信息API、上传数据API |
| 财务模型 | 交易ID、金额、类型、时间、关联订单 | 财务API、报告API |
| 物流模型 | 配送方式、追踪号、发货地址、物流费用 | 配送API、订单API |

---

### 九、额外资源与社区支持

| 资源类型 | 内容 | 链接 |
|---------|------|------|
| SP-API论坛 | 开发者问答社区 | https://forums.developer.amazon.com/sp-api |
| AWS支持中心 | 技术支持和工单提交 | https://console.aws.amazon.com/support/home |
| 代码示例库 | 官方和第三方开源项目 | https://github.com/amzn/selling-partner-api-models/tree/main/clients  |
| 合作伙伴网络 | 寻找认证解决方案提供商 | https://sellercentral.amazon.com/solutions-providers/  |

---

### 关键注意事项
1. **SP-API已取代MWS API**，新开发必须使用SP-API，旧MWS应用需尽快迁移 
2. **PII数据处理**需申请RDT权限并遵守亚马逊数据保护协议 
3. **沙箱测试**是开发必经阶段，避免直接调用生产环境 
4. **区域差异**：不同市场的API终端节点和AWS区域不同，需对应配置 

需要我整理一份“SP-API对接ERP”的最小可行开发路线图（按周/按步骤），并附上Postman测试用例模板和常见认证错误排查清单吗？