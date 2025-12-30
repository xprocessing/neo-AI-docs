# Spring Boot 监控和管理

Spring Boot Actuator 提供了生产级的监控和管理功能。本章将详细介绍如何使用 Spring Boot Actuator 来监控和管理应用程序。

## Actuator 入门

### 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

### 基础配置

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,beans,env
  endpoint:
    health:
      show-details: when-authorized
  info:
    build:
      enabled: true
    git:
      mode: full
  metrics:
    export:
      prometheus:
        enabled: true
```

## 内置端点详解

### Health 端点

```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    
    @Override
    public Health health() {
        // 执行健康检查逻辑
        boolean isHealthy = checkHealth();
        
        if (isHealthy) {
            return Health.up()
                .withDetail("database", "Available")
                .withDetail("responseTime", "10ms")
                .build();
        } else {
            return Health.down()
                .withDetail("database", "Unavailable")
                .withDetail("error", "Connection failed")
                .build();
        }
    }
    
    private boolean checkHealth() {
        // 实际的健康检查逻辑
        return true; // 简化示例
    }
}

// 数据库健康指示器
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try (Connection connection = dataSource.getConnection()) {
            if (connection.isValid(1)) {
                return Health.up()
                    .withDetail("database", "Available")
                    .withDetail("validationQuery", "SELECT 1")
                    .build();
            } else {
                return Health.down()
                    .withDetail("database", "Connection failed")
                    .build();
            }
        } catch (SQLException e) {
            return Health.down()
                .withDetail("database", "Connection error")
                .withException(e)
                .build();
        }
    }
}
```

### Info 端点自定义

```java
@Component
public class CustomInfoContributor implements InfoContributor {
    
    @Override
    public void contribute(Info.Builder builder) {
        builder.withDetail("app", Map.of(
            "name", "My Spring Boot Application",
            "version", "1.0.0",
            "description", "A sample Spring Boot application"
        ));
        
        builder.withDetail("build", Map.of(
            "java", System.getProperty("java.version"),
            "jvm", System.getProperty("java.vm.name"),
            "os", System.getProperty("os.name")
        ));
        
        // 添加构建时间
        builder.withDetail("buildTime", LocalDateTime.now().toString());
    }
}

// 或者使用配置文件
# application.yml
info:
  app:
    name: My Spring Boot Application
    version: @project.version@
    description: @project.description@
  build:
    artifact: @project.artifactId@
    name: @project.name@
    version: @project.version@
  java:
    version: ${java.version:unknown}
    vendor: ${java.vendor:unknown}
  os:
    name: ${os.name:unknown}
    arch: ${os.arch:unknown}
    version: ${os.version:unknown}
```

## 自定义端点

### @Endpoint 注解

```java
@Endpoint(id = "custom")
@Component
public class CustomEndpoint {
    
    private final Map<String, Object> customData = new ConcurrentHashMap<>();
    
    @ReadOperation
    public Map<String, Object> getAllCustomData() {
        return new HashMap<>(customData);
    }
    
    @ReadOperation
    public Object getCustomData(@Selector String key) {
        return customData.get(key);
    }
    
    @WriteOperation
    public void updateCustomData(@Selector String key, Map<String, Object> data) {
        customData.put(key, data);
    }
    
    @DeleteOperation
    public void deleteCustomData(@Selector String key) {
        customData.remove(key);
    }
}
```

### @WebEndpoint 注解

```java
@WebEndpoint(id = "user-stats")
@Component
public class UserStatsEndpoint {
    
    @Autowired
    private UserService userService;
    
    @ReadOperation
    public UserStats getUserStats() {
        long totalUsers = userService.getTotalUserCount();
        long activeUsers = userService.getActiveUserCount();
        long inactiveUsers = totalUsers - activeUsers;
        
        return new UserStats(totalUsers, activeUsers, inactiveUsers);
    }
    
    @WriteOperation
    public String resetStats() {
        // 重置统计信息的逻辑
        return "User stats reset successfully";
    }
}

// 统计信息类
class UserStats {
    private final long totalUsers;
    private final long activeUsers;
    private final long inactiveUsers;
    
    public UserStats(long totalUsers, long activeUsers, long inactiveUsers) {
        this.totalUsers = totalUsers;
        this.activeUsers = activeUsers;
        this.inactiveUsers = inactiveUsers;
    }
    
    // getters
    public long getTotalUsers() { return totalUsers; }
    public long getActiveUsers() { return activeUsers; }
    public long getInactiveUsers() { return inactiveUsers; }
}
```

### @JmxEndpoint 注解

```java
@JmxEndpoint(id = "cache-manager")
@Component
public class CacheManagerEndpoint {
    
    @Autowired
    private CacheManager cacheManager;
    
    @ReadOperation
    public Map<String, Object> getCacheInfo() {
        Map<String, Object> info = new HashMap<>();
        Collection<String> cacheNames = cacheManager.getCacheNames();
        
        for (String cacheName : cacheNames) {
            Cache cache = cacheManager.getCache(cacheName);
            info.put(cacheName, Map.of(
                "name", cache.getName(),
                "size", getCacheSize(cache)
            ));
        }
        
        return info;
    }
    
    @WriteOperation
    public String clearCache(@Selector String cacheName) {
        Cache cache = cacheManager.getCache(cacheName);
        if (cache != null) {
            cache.clear();
            return "Cache " + cacheName + " cleared successfully";
        }
        return "Cache " + cacheName + " not found";
    }
    
    private int getCacheSize(Cache cache) {
        // 根据具体缓存实现获取大小
        return 0; // 简化示例
    }
}
```

## 指标监控

### 自定义指标

```java
@Component
public class CustomMetricsService {
    
    private final MeterRegistry meterRegistry;
    private final Counter processedOrdersCounter;
    private final Timer orderProcessingTimer;
    private final Gauge activeUsersGauge;
    private final DistributionSummary orderAmountSummary;
    
    public CustomMetricsService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        // 计数器：统计处理的订单数量
        this.processedOrdersCounter = Counter.builder("orders.processed")
            .description("Number of processed orders")
            .register(meterRegistry);
        
        // 计时器：测量订单处理时间
        this.orderProcessingTimer = Timer.builder("order.processing.duration")
            .description("Order processing duration")
            .register(meterRegistry);
        
        // 分布摘要：记录订单金额分布
        this.orderAmountSummary = DistributionSummary.builder("order.amount")
            .description("Order amount distribution")
            .baseUnit("currency")
            .register(meterRegistry);
        
        // 仪表盘：显示活跃用户数
        this.activeUsersGauge = Gauge.builder("users.active")
            .description("Number of active users")
            .register(meterRegistry, this, CustomMetricsService::getActiveUserCount);
    }
    
    public void recordOrderProcessed(double amount) {
        processedOrdersCounter.increment();
        orderAmountSummary.record(amount);
    }
    
    public <T> T timeOrderProcessing(Supplier<T> operation) {
        return orderProcessingTimer.recordCallable(operation::get);
    }
    
    public long getActiveUserCount() {
        // 返回当前活跃用户数
        return 100; // 示例值
    }
}
```

### 业务指标监控

```java
@Service
public class OrderService {
    
    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);
    
    @Autowired
    private CustomMetricsService metricsService;
    
    @Autowired
    private OrderRepository orderRepository;
    
    public Order processOrder(Order order) {
        return metricsService.timeOrderProcessing(() -> {
            try {
                // 业务处理逻辑
                Order savedOrder = orderRepository.save(order);
                
                // 记录指标
                metricsService.recordOrderProcessed(order.getAmount());
                
                logger.info("Order processed successfully: {}", order.getId());
                return savedOrder;
            } catch (Exception e) {
                logger.error("Error processing order: {}", order.getId(), e);
                
                // 记录错误指标
                Counter.builder("orders.errors")
                    .tags("type", e.getClass().getSimpleName())
                    .register(meterRegistry)
                    .increment();
                
                throw e;
            }
        });
    }
}
```

## 日志管理

### 日志端点配置

```yaml
logging:
  level:
    com.example: DEBUG
    org.springframework.web: INFO
    org.springframework.security: INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: application.log
    max-size: 10MB
    max-history: 30
```

### 动态日志级别管理

```java
@RestController
@RequestMapping("/api/logs")
public class LogController {
    
    private final LoggingSystem loggingSystem;
    
    public LogController(LoggingSystem loggingSystem) {
        this.loggingSystem = loggingSystem;
    }
    
    @PutMapping("/level/{loggerName}")
    public ResponseEntity<String> setLogLevel(
            @PathVariable String loggerName, 
            @RequestParam String level) {
        
        try {
            loggingSystem.setLogLevel(loggerName, LogLevel.valueOf(level.toUpperCase()));
            return ResponseEntity.ok("Log level set to " + level + " for " + loggerName);
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body("Error setting log level: " + e.getMessage());
        }
    }
    
    @GetMapping("/config")
    public ResponseEntity<Map<String, String>> getLogConfiguration() {
        Map<String, String> config = new HashMap<>();
        // 获取当前日志配置
        return ResponseEntity.ok(config);
    }
}
```

## 应用程序信息端点

### 自定义构建信息

```java
@Component
public class BuildInfoContributor implements InfoContributor {
    
    @Override
    public void contribute(Info.Builder builder) {
        try {
            // 从 git.properties 文件读取构建信息
            Properties gitProperties = new Properties();
            try (InputStream gitStream = getClass().getClassLoader()
                    .getResourceAsStream("git.properties")) {
                if (gitStream != null) {
                    gitProperties.load(gitStream);
                }
            }
            
            Map<String, Object> gitInfo = new HashMap<>();
            gitInfo.put("branch", gitProperties.getProperty("git.branch"));
            gitInfo.put("commit.id", gitProperties.getProperty("git.commit.id"));
            gitInfo.put("commit.time", gitProperties.getProperty("git.commit.time"));
            
            builder.withDetail("git", gitInfo);
            
            // 从 build-info.properties 读取构建信息
            Properties buildProperties = new Properties();
            try (InputStream buildStream = getClass().getClassLoader()
                    .getResourceAsStream("build-info.properties")) {
                if (buildStream != null) {
                    buildProperties.load(buildStream);
                }
            }
            
            Map<String, Object> buildInfo = new HashMap<>();
            buildInfo.put("artifact", buildProperties.getProperty("build.artifact"));
            buildInfo.put("name", buildProperties.getProperty("build.name"));
            buildInfo.put("version", buildProperties.getProperty("build.version"));
            buildInfo.put("time", buildProperties.getProperty("build.time"));
            
            builder.withDetail("build", buildInfo);
            
        } catch (IOException e) {
            builder.withDetail("error", "Could not load build info: " + e.getMessage());
        }
    }
}
```

## 安全配置

### Actuator 端点安全

```java
@Configuration
@EnableWebSecurity
public class ActuatorSecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/actuator/shutdown").hasRole("ADMIN")
                .requestMatchers("/actuator/**").hasRole("MONITOR")
                .anyRequest().authenticated()
            )
            .httpBasic(withDefaults()); // 启用 HTTP Basic 认证
        
        return http.build();
    }
}
```

### 端点访问控制

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,beans,env,loggers
      base-path: /management  # 更改端点基础路径
  endpoint:
    health:
      show-details: when-authorized
    shutdown:
      enabled: true  # 启用关闭端点（生产环境需谨慎）
  server:
    port: 8081  # 将管理端点部署到不同端口
```

## 自定义监控

### 应用状态监控

```java
@Component
public class ApplicationStatusIndicator implements HealthIndicator {
    
    private volatile boolean serviceAvailable = true;
    
    @Override
    public Health health() {
        if (serviceAvailable) {
            return Health.up()
                .withDetail("status", "Service is running normally")
                .withDetail("uptime", getUptime())
                .build();
        } else {
            return Health.down()
                .withDetail("status", "Service is temporarily unavailable")
                .build();
        }
    }
    
    public void setServiceAvailable(boolean available) {
        this.serviceAvailable = available;
    }
    
    private String getUptime() {
        long uptime = ManagementFactory.getRuntimeMXBean().getUptime();
        long seconds = uptime / 1000;
        long hours = seconds / 3600;
        long minutes = (seconds % 3600) / 60;
        seconds = seconds % 60;
        
        return String.format("%02d:%02d:%02d", hours, minutes, seconds);
    }
}
```

### 性能监控

```java
@Component
public class PerformanceMonitor {
    
    private final MeterRegistry meterRegistry;
    
    public PerformanceMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }
    
    @EventListener
    public void handleServletRequest(ServletRequestHandledEvent event) {
        Timer.builder("http.requests")
            .tag("method", event.getMethod())
            .tag("status", String.valueOf(event.getStatus()))
            .tag("uri", event.getRequestUri())
            .register(meterRegistry)
            .record(event.getProcessingTimeMicros(), TimeUnit.MICROSECONDS);
    }
    
    @EventListener
    public void handleContextRefresh(ContextRefreshedEvent event) {
        Gauge.builder("application.uptime")
            .register(meterRegistry, this, PerformanceMonitor::getApplicationUptime);
    }
    
    private double getApplicationUptime() {
        return ManagementFactory.getRuntimeMXBean().getUptime() / 1000.0; // 秒
    }
}
```

## Prometheus 集成

### Prometheus 配置

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  metrics:
    export:
      prometheus:
        enabled: true
  prometheus:
    metrics:
      export:
        enabled: true
```

### 添加依赖

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

现在监控端点将在 `/actuator/prometheus` 提供 Prometheus 格式的指标。

## Grafana 面板配置

创建一个简单的 Grafana 面板 JSON 配置：

```json
{
  "dashboard": {
    "id": null,
    "title": "Spring Boot Application Dashboard",
    "panels": [
      {
        "id": 1,
        "title": "HTTP Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{uri}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "JVM Memory",
        "type": "graph",
        "targets": [
          {
            "expr": "jvm_memory_used_bytes",
            "legendFormat": "{{area}} - {{id}}"
          }
        ]
      }
    ]
  }
}
```