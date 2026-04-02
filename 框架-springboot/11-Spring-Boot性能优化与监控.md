# 第11章：Spring Boot性能优化与监控

## 11.1 性能优化概述

### 11.1.1 性能优化目标

- **响应时间**：降低请求响应时间
- **吞吐量**：提高系统处理能力
- **资源利用率**：提高CPU、内存等资源利用率
- **稳定性**：保证系统稳定运行

### 11.1.2 性能优化方向

| 优化方向 | 说明 |
|----------|------|
| 数据库优化 | SQL优化、索引优化、连接池配置 |
| 缓存优化 | 多级缓存、缓存预热 |
| 代码优化 | 算法优化、减少IO操作 |
| 并发优化 | 线程池、异步处理 |
| JVM优化 | 内存分配、垃圾回收 |

## 11.2 JVM优化

### 11.2.1 JVM参数配置

```bash
java -Xms2g -Xmx2g -Xmn1g \
     -XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=512m \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:ParallelGCThreads=4 \
     -XX:ConcGCThreads=2 \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/logs/heapdump.hprof \
     -Xlog:gc*:file=/logs/gc.log:time,tags:filecount=10,filesize=100M \
     -jar app.jar
```

### 11.2.2 JVM监控

```java
@RestController
@RequestMapping("/actuator/jvm")
public class JvmMonitorController {

    @Autowired
    private MemoryMXBean memoryMXBean;

    @Autowired
    private ThreadMXBean threadMXBean;

    @Autowired
    private RuntimeMXBean runtimeMXBean;

    @GetMapping("/memory")
    public Map<String, Object> getMemoryInfo() {
        MemoryUsage heapUsage = memoryMXBean.getHeapMemoryUsage();
        MemoryUsage nonHeapUsage = memoryMXBean.getNonHeapMemoryUsage();

        Map<String, Object> info = new HashMap<>();
        info.put("heapInit", heapUsage.getInit());
        info.put("heapUsed", heapUsage.getUsed());
        info.put("heapCommitted", heapUsage.getCommitted());
        info.put("heapMax", heapUsage.getMax());
        info.put("nonHeapInit", nonHeapUsage.getInit());
        info.put("nonHeapUsed", nonHeapUsage.getUsed());
        info.put("nonHeapCommitted", nonHeapUsage.getCommitted());
        info.put("nonHeapMax", nonHeapUsage.getMax());
        return info;
    }

    @GetMapping("/threads")
    public Map<String, Object> getThreadInfo() {
        Map<String, Object> info = new HashMap<>();
        info.put("threadCount", threadMXBean.getThreadCount());
        info.put("peakThreadCount", threadMXBean.getPeakThreadCount());
        info.put("daemonThreadCount", threadMXBean.getDaemonThreadCount());
        info.put("totalStartedThreadCount", threadMXBean.getTotalStartedThreadCount());
        return info;
    }

    @GetMapping("/runtime")
    public Map<String, Object> getRuntimeInfo() {
        Map<String, Object> info = new HashMap<>();
        info.put("startTime", new Date(runtimeMXBean.getStartTime()));
        info.put("uptime", runtimeMXBean.getUptime());
        info.put("systemProperties", runtimeMXBean.getSystemProperties());
        info.put("jvmName", runtimeMXBean.getVmName());
        info.put("jvmVersion", runtimeMXBean.getVmVersion());
        return info;
    }
}
```

## 11.3 数据库优化

### 11.3.1 连接池配置

```yaml
spring:
  datasource:
    hikari:
      minimum-idle: 10
      maximum-pool-size: 50
      idle-timeout: 600000
      max-lifetime: 1800000
      connection-timeout: 30000
      connection-test-query: SELECT 1
      pool-name: SpringBootHikariCP
```

### 11.3.2 SQL优化

```java
@Repository
public class UserRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public List<User> findUsersWithPagination(int offset, int limit) {
        String sql = "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?";
        return jdbcTemplate.query(sql, new Object[]{limit, offset}, new UserRowMapper());
    }

    public List<User> findUsersByKeyword(String keyword) {
        String sql = "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?";
        return jdbcTemplate.query(sql, new Object[]{"%" + keyword + "%", "%" + keyword + "%"},
            new UserRowMapper());
    }

    public User findUserWithOrders(Long userId) {
        String sql = "SELECT u.*, o.id as order_id, o.order_no, o.total_amount " +
                     "FROM users u LEFT JOIN orders o ON u.id = o.user_id " +
                     "WHERE u.id = ?";
        return jdbcTemplate.query(sql, new Object[]{userId}, new UserWithOrdersResultSetExtractor());
    }
}
```

### 11.3.3 批量操作

```java
@Service
public class BatchService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Transactional
    public void batchInsertUsers(List<User> users) {
        String sql = "INSERT INTO users (username, email, created_at) VALUES (?, ?, NOW())";

        jdbcTemplate.batchUpdate(sql, users, users.size(),
            (ps, user) -> {
                ps.setString(1, user.getUsername());
                ps.setString(2, user.getEmail());
            });
    }

    @Transactional
    public void batchUpdateUsers(List<User> users) {
        String sql = "UPDATE users SET email = ?, updated_at = NOW() WHERE id = ?";

        jdbcTemplate.batchUpdate(sql, users, users.size(),
            (ps, user) -> {
                ps.setString(1, user.getEmail());
                ps.setLong(2, user.getId());
            });
    }
}
```

## 11.4 异步处理

### 11.4.1 异步配置

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(200);
        executor.setThreadNamePrefix("async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(60);
        executor.initialize();
        return executor;
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return new CustomAsyncExceptionHandler();
    }
}

public class CustomAsyncExceptionHandler implements AsyncUncaughtExceptionHandler {

    @Override
    public void handleUncaughtException(Throwable ex, Method method, Object... params) {
        System.out.println("Async method " + method.getName() + " threw exception: " + ex);
    }
}
```

### 11.4.2 异步服务

```java
@Service
public class AsyncService {

    @Async
    public CompletableFuture<String> asyncMethod1() {
        try {
            Thread.sleep(1000);
            return CompletableFuture.completedFuture("Method 1 completed");
        } catch (InterruptedException e) {
            return CompletableFuture.failedFuture(e);
        }
    }

    @Async
    public CompletableFuture<String> asyncMethod2() {
        try {
            Thread.sleep(1500);
            return CompletableFuture.completedFuture("Method 2 completed");
        } catch (InterruptedException e) {
            return CompletableFuture.failedFuture(e);
        }
    }

    public CompletableFuture<Void> executeMultipleAsyncTasks() {
        CompletableFuture<String> task1 = asyncMethod1();
        CompletableFuture<String> task2 = asyncMethod2();

        return CompletableFuture.allOf(task1, task2)
            .thenAccept(v -> {
                System.out.println("All tasks completed");
            });
    }
}
```

## 11.5 Actuator监控

### 11.5.1 Actuator配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /actuator
  endpoint:
    health:
      show-details: always
      show-components: always
    metrics:
      enabled: true
    prometheus:
      enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
    tags:
      application: ${spring.application.name}
      environment: ${spring.profiles.active}
```

### 11.5.2 自定义健康检查

```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {

    @Autowired
    private DataSource dataSource;

    @Override
    public Health health() {
        try (Connection connection = dataSource.getConnection()) {
            if (connection.isValid(1)) {
                return Health.up()
                    .withDetail("database", "MySQL")
                    .withDetail("url", connection.getMetaData().getURL())
                    .build();
            }
        } catch (SQLException e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
        return Health.down().build();
    }
}

@Component
public class RedisHealthIndicator implements HealthIndicator {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Override
    public Health health() {
        try {
            redisTemplate.getConnectionFactory().getConnection().ping();
            return Health.up()
                .withDetail("redis", "Redis")
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```

### 11.5.3 自定义指标

```java
@Component
public class CustomMetrics {

    private final MeterRegistry meterRegistry;
    private final Counter orderCounter;
    private final Timer orderTimer;

    public CustomMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.orderCounter = Counter.builder("order.count")
            .description("订单数量")
            .tag("type", "total")
            .register(meterRegistry);

        this.orderTimer = Timer.builder("order.processing.time")
            .description("订单处理时间")
            .register(meterRegistry);
    }

    public void incrementOrderCount() {
        orderCounter.increment();
    }

    public void recordOrderProcessingTime(long milliseconds) {
        orderTimer.record(milliseconds, TimeUnit.MILLISECONDS);
    }

    public void recordOrderStatus(String status) {
        Counter.builder("order.count")
            .description("订单数量")
            .tag("status", status)
            .register(meterRegistry)
            .increment();
    }
}
```

## 11.6 Prometheus集成

### 11.6.1 Prometheus配置

```yaml
management:
  metrics:
    export:
      prometheus:
        enabled: true
    distribution:
      percentiles-histogram:
        http.server.requests: true
      slo:
        http.server.requests: 100ms,200ms,500ms,1s,2s
```

### 11.6.2 Prometheus配置文件

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'spring-boot-app'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['localhost:8080']
        labels:
          application: 'demo-app'
          environment: 'dev'
```

## 11.7 Grafana集成

### 11.7.1 Grafana数据源配置

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://localhost:9090",
  "access": "proxy",
  "isDefault": true
}
```

### 11.7.2 Grafana仪表盘

```json
{
  "dashboard": {
    "title": "Spring Boot应用监控",
    "panels": [
      {
        "title": "JVM内存使用",
        "targets": [
          {
            "expr": "jvm_memory_used_bytes{area=\"heap\"}"
          }
        ]
      },
      {
        "title": "HTTP请求速率",
        "targets": [
          {
            "expr": "rate(http_server_requests_seconds_count[1m])"
          }
        ]
      },
      {
        "title": "HTTP请求延迟",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_server_requests_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

## 11.8 互联网大厂真实项目代码示例

### 11.8.1 阿里巴巴性能监控

```java
package com.alibaba.monitor;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.stereotype.Component;

@Component
public class AlibabaMetrics {

    private final Counter requestCounter;
    private final Timer requestTimer;
    private final Counter errorCounter;

    public AlibabaMetrics(MeterRegistry meterRegistry) {
        this.requestCounter = Counter.builder("http.requests.total")
            .description("Total HTTP requests")
            .register(meterRegistry);

        this.requestTimer = Timer.builder("http.requests.duration")
            .description("HTTP request duration")
            .register(meterRegistry);

        this.errorCounter = Counter.builder("http.requests.errors")
            .description("Total HTTP errors")
            .register(meterRegistry);
    }

    public void recordRequest() {
        requestCounter.increment();
    }

    public void recordRequestDuration(long milliseconds) {
        requestTimer.record(milliseconds, TimeUnit.MILLISECONDS);
    }

    public void recordError() {
        errorCounter.increment();
    }
}
```

### 11.8.2 腾讯云JVM优化

```java
package com.tencent.cloud.config;

import org.springframework.context.annotation.Configuration;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

@Configuration
public class ThreadPoolConfig {

    public ExecutorService customThreadPool() {
        return new ThreadPoolExecutor(
            10,
            50,
            60L,
            TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(200),
            new ThreadPoolExecutor.CallerRunsPolicy()
        );
    }
}
```

### 11.8.3 美团数据库优化

```java
package com.meituan.repository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class OptimizedUserRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public List<User> findUsersWithOptimization(int page, int size) {
        int offset = (page - 1) * size;
        String sql = "SELECT id, username, email FROM users " +
                     "WHERE status = 'ACTIVE' " +
                     "ORDER BY created_at DESC " +
                     "LIMIT ? OFFSET ?";
        return jdbcTemplate.query(sql, new Object[]{size, offset}, new UserRowMapper());
    }

    public User findUserWithOrdersOptimized(Long userId) {
        String sql = "SELECT u.*, o.id as order_id, o.order_no, o.total_amount " +
                     "FROM users u " +
                     "LEFT JOIN orders o ON u.id = o.user_id " +
                     "WHERE u.id = ? " +
                     "ORDER BY o.created_at DESC " +
                     "LIMIT 10";
        return jdbcTemplate.query(sql, new Object[]{userId}, new UserWithOrdersResultSetExtractor());
    }
}
```

### 11.8.4 字节跳动异步处理

```java
package com.bytedance.async;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.concurrent.CompletableFuture;

@Service
public class AsyncOrderService {

    @Async("orderTaskExecutor")
    public CompletableFuture<String> processOrderAsync(Long orderId) {
        try {
            Thread.sleep(1000);
            return CompletableFuture.completedFuture("Order " + orderId + " processed");
        } catch (InterruptedException e) {
            return CompletableFuture.failedFuture(e);
        }
    }

    @Async("orderTaskExecutor")
    public CompletableFuture<String> sendNotificationAsync(Long userId, String message) {
        try {
            Thread.sleep(500);
            return CompletableFuture.completedFuture("Notification sent to user " + userId);
        } catch (InterruptedException e) {
            return CompletableFuture.failedFuture(e);
        }
    }
}
```

### 11.8.5 京东健康健康检查

```java
package com.jd.health.health;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class DatabaseHealthIndicator implements HealthIndicator {

    @Autowired
    private DataSource dataSource;

    @Override
    public Health health() {
        try (Connection connection = dataSource.getConnection()) {
            if (connection.isValid(1)) {
                return Health.up()
                    .withDetail("database", "MySQL")
                    .withDetail("url", connection.getMetaData().getURL())
                    .withDetail("version", connection.getMetaData().getDatabaseProductVersion())
                    .build();
            }
        } catch (SQLException e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
        return Health.down().build();
    }
}
```

### 11.8.6 拼多多性能监控

```java
package com.pdd.monitor;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.stereotype.Component;

import java.util.concurrent.atomic.AtomicLong;

@Component
public class PerformanceMonitor {

    private final Counter orderCounter;
    private final Timer orderTimer;
    private final AtomicLong activeOrders = new AtomicLong(0);

    public PerformanceMonitor(MeterRegistry meterRegistry) {
        this.orderCounter = Counter.builder("pdd.orders.total")
            .description("Total orders")
            .register(meterRegistry);

        this.orderTimer = Timer.builder("pdd.orders.duration")
            .description("Order processing duration")
            .register(meterRegistry);

        Gauge.builder("pdd.orders.active", activeOrders, AtomicLong::get)
            .description("Active orders")
            .register(meterRegistry);
    }

    public void recordOrder() {
        orderCounter.increment();
        activeOrders.incrementAndGet();
    }

    public void recordOrderDuration(long milliseconds) {
        orderTimer.record(milliseconds, TimeUnit.MILLISECONDS);
        activeOrders.decrementAndGet();
    }
}
```

## 11.9 最佳实践

1. **JVM调优**：根据应用特点配置JVM参数
2. **数据库优化**：优化SQL语句和索引
3. **连接池配置**：合理配置连接池大小
4. **异步处理**：使用异步提升性能
5. **缓存策略**：合理使用缓存
6. **监控告警**：建立完善的监控体系

## 11.10 小结

本章介绍了Spring Boot性能优化与监控的核心内容，包括：

- JVM优化
- 数据库优化
- 异步处理
- Actuator监控
- Prometheus集成
- Grafana集成

通过本章学习，你应该能够：

- 优化JVM参数
- 优化数据库性能
- 实现异步处理
- 配置Actuator监控
- 集成Prometheus和Grafana
- 建立性能监控体系

下一章将介绍Spring Boot的容器化部署。
