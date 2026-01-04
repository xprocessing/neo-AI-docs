## **第一阶段：基础入门（2-3周）**
- **Java基础巩固**
  - 核心语法：数据类型、运算符、控制流程、数组
  - 面向对象：封装、继承、多态、抽象类与接口
  - 集合框架：List/Set/Map、Stream API、Lambda表达式
  - 异常处理：try-catch、自定义异常、异常链
  - Java 8+新特性：Optional、CompletableFuture、日期时间API
- **开发环境搭建**
  - JDK 8/11安装与环境变量配置
  - Maven/Gradle依赖管理工具使用
  - IDE配置：IntelliJ IDEA/Eclipse插件安装
  - Spring Initializr项目生成
- **Spring Boot核心概念**
  - 约定大于配置理念
  - 自动配置原理初探
  - 起步依赖（Starter）机制
- **第一个Spring Boot项目**
  - Hello World接口开发
  - 项目结构解析
  - 启动类与注解说明
  - 单元测试入门

## **第二阶段：核心知识深入（3-4周）**
### **配置体系**
- 配置文件：application.properties/yml语法
- 多环境配置：profile切换
- 自定义配置：@ConfigurationProperties、@Value
- 外部化配置：环境变量、命令行参数
### **Web开发**
- RESTful API设计
  - @RestController、@RequestMapping系列注解
  - 请求参数接收：@RequestParam、@PathVariable、@RequestBody
  - 响应处理：ResponseEntity、统一结果封装
- 数据校验：JSR-380、@Validated、自定义校验
- 异常处理：@ControllerAdvice全局异常捕获
- 跨域解决方案：@CrossOrigin、CorsFilter
### **数据持久化**
- MySQL/PostgreSQL数据库集成
- MyBatis整合
  - 注解版XML版使用
  - 分页插件：PageHelper
  - 事务管理：@Transactional
- Spring Data JPA
  - 实体类映射、Repository接口
  - JPQL查询、Specification动态查询
- Redis缓存集成
  - 缓存注解：@Cacheable、@CacheEvict
  - 分布式缓存配置
### **安全框架**
- Spring Security入门
  - 内存用户认证、数据库用户认证
  - 密码加密：BCryptPasswordEncoder
  - 角色权限控制：@PreAuthorize
- JWT令牌认证
  - Token生成与解析
  - 过滤器实现无状态登录

## **第三阶段：高级特性与扩展（2-3周）**
### **核心原理深入**
- 自动配置原理
  - @EnableAutoConfiguration流程
  - 条件注解：@ConditionalOnClass等
  - 自定义Starter开发
- 启动流程分析
  - SpringApplication.run()执行过程
  - 监听器、初始化器扩展
- 依赖注入与Bean生命周期
  - @Autowired、@Resource区别
  - Bean的作用域、生命周期回调
### **性能优化**
- 异步编程：@Async、线程池配置
- 定时任务：@Scheduled、Quartz集成
- 数据库优化
  - 连接池配置：HikariCP参数调优
  - 慢查询分析、索引优化
- 接口性能监控：Spring Boot Actuator
### **消息队列集成**
- RabbitMQ
  - 交换机、队列、绑定配置
  - 消息可靠性投递、消费确认
- Kafka
  - 生产者、消费者配置
  - 消息分区、偏移量管理
### **微服务基础**
- Spring Cloud入门
  - 服务注册与发现：Nacos/Eureka
  - 配置中心：Spring Cloud Config/Nacos Config
  - 服务调用：OpenFeign
  - 网关：Spring Cloud Gateway

## **第四阶段：实战项目（4-6周）**
### **项目一：个人博客系统**
- 功能模块
  - 用户管理：注册、登录、权限控制
  - 文章管理：发布、编辑、分类、标签
  - 评论系统：多级评论、点赞
  - 后台管理：数据统计、系统配置
- 技术栈：Spring Boot + MyBatis + MySQL + Redis + Vue
- 项目目标：掌握单体应用开发流程
### **项目二：电商订单系统**
- 功能模块
  - 订单创建、支付、发货、退款
  - 库存扣减、分布式事务
  - 消息通知：邮件、短信
  - 接口文档：Swagger/OpenAPI
- 技术栈：Spring Boot + Spring Cloud + RabbitMQ + Redis + MySQL
- 项目目标：理解微服务架构设计

## **第五阶段：面试与进阶（1-2周）**
### **高频面试题**
- Spring Boot基础
  - 自动配置原理、起步依赖机制
  - 配置加载顺序、Bean的加载顺序
- 数据访问
  - 事务传播机制、事务失效场景
  - MyBatis与JPA对比
- 性能优化
  - 缓存穿透、击穿、雪崩解决方案
  - 异步编程实现方式
### **进阶学习方向**
- 云原生：Docker容器化、Kubernetes部署
- 服务网格：Istio入门
- 响应式编程：Spring WebFlux
- 架构设计：DDD领域驱动设计
### **学习资源推荐**
- 官方文档：Spring Boot Reference Guide
- 书籍：《Spring Boot实战》《Spring Cloud微服务实战》
- 课程：极客时间《Spring Boot核心技术与实战》
- 社区：Stack Overflow、Spring中文社区