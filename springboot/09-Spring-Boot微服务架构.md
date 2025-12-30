# 第9章：Spring Boot微服务架构

## 9.1 微服务概述

### 9.1.1 什么是微服务

微服务架构是一种将单一应用程序开发为一组小型服务的方法，每个服务运行在自己的进程中，并使用轻量级机制（通常是HTTP API）进行通信。

### 9.1.2 微服务特点

- **单一职责**：每个服务专注于单一业务功能
- **独立部署**：服务可以独立部署和扩展
- **技术多样性**：不同服务可以使用不同技术栈
- **去中心化**：服务之间松耦合
- **容错性**：单个服务故障不影响整体

### 9.1.3 微服务 vs 单体架构

| 特性 | 单体架构 | 微服务架构 |
|------|----------|------------|
| 部署 | 整体部署 | 独立部署 |
| 扩展 | 整体扩展 | 按需扩展 |
| 技术栈 | 统一 | 多样 |
| 复杂度 | 低 | 高 |
| 开发效率 | 初期高 | 后期高 |

## 9.2 Spring Cloud基础

### 9.2.1 Spring Cloud核心组件

| 组件 | 功能 | 说明 |
|------|------|------|
| Eureka | 服务注册与发现 | Netflix实现 |
| Consul | 服务注册与发现 | HashiCorp实现 |
| Nacos | 服务注册与发现 | 阿里巴巴实现 |
| Ribbon | 客户端负载均衡 | Netflix实现 |
| OpenFeign | 声明式HTTP客户端 | Netflix实现 |
| Hystrix | 熔断器 | Netflix实现 |
| Resilience4j | 熔断器 | Hystrix替代品 |
| Gateway | API网关 | Spring Cloud实现 |
| Config | 配置中心 | 集中管理配置 |
| Sleuth | 链路追踪 | 分布式追踪 |

### 9.2.2 依赖配置

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>2023.0.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <!-- 服务注册与发现 -->
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
    </dependency>

    <!-- 配置中心 -->
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
    </dependency>

    <!-- 负载均衡 -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-loadbalancer</artifactId>
    </dependency>

    <!-- 声明式HTTP客户端 -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-openfeign</artifactId>
    </dependency>

    <!-- 熔断器 -->
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-spring-boot2</artifactId>
    </dependency>

    <!-- API网关 -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-gateway</artifactId>
    </dependency>

    <!-- 链路追踪 -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-sleuth</artifactId>
    </dependency>
</dependencies>
```

## 9.3 服务注册与发现

### 9.3.1 Nacos服务注册

```yaml
spring:
  application:
    name: user-service
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
        namespace: dev
        group: DEFAULT_GROUP
        metadata:
          version: 1.0.0
          region: beijing
```

### 9.3.2 服务提供者

```java
@SpringBootApplication
@EnableDiscoveryClient
public class UserServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/{id}")
    public UserDTO getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping
    public UserDTO createUser(@Valid @RequestBody UserCreateRequest request) {
        return userService.create(request);
    }
}
```

### 9.3.3 服务消费者

```java
@SpringBootApplication
@EnableDiscoveryClient
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    public OrderDTO createOrder(@Valid @RequestBody OrderCreateRequest request) {
        return orderService.create(request);
    }
}

@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final UserClient userClient;

    public OrderDTO create(OrderCreateRequest request) {
        UserDTO user = userClient.getUser(request.getUserId());
        Order order = Order.builder()
            .userId(request.getUserId())
            .userName(user.getUsername())
            .totalAmount(request.getTotalAmount())
            .status(OrderStatus.PENDING)
            .build();
        order = orderRepository.save(order);
        return OrderDTO.fromEntity(order);
    }
}
```

## 9.4 服务调用

### 9.4.1 RestTemplate调用

```java
@Configuration
public class RestTemplateConfig {

    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

@Service
@RequiredArgsConstructor
public class UserService {

    private final RestTemplate restTemplate;

    public UserDTO getUser(Long id) {
        String url = "http://user-service/api/users/" + id;
        return restTemplate.getForObject(url, UserDTO.class);
    }
}
```

### 9.4.2 OpenFeign调用

```java
@SpringBootApplication
@EnableFeignClients
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}

@FeignClient(name = "user-service", path = "/api/users")
public interface UserClient {

    @GetMapping("/{id}")
    UserDTO getUser(@PathVariable("id") Long id);

    @PostMapping
    UserDTO createUser(@RequestBody UserCreateRequest request);

    @GetMapping("/search")
    List<UserDTO> searchUsers(@RequestParam("keyword") String keyword);
}

@Service
@RequiredArgsConstructor
public class OrderService {

    private final UserClient userClient;

    public OrderDTO create(OrderCreateRequest request) {
        UserDTO user = userClient.getUser(request.getUserId());
    }
}
```

### 9.4.3 Feign配置

```java
@Configuration
public class FeignConfig {

    @Bean
    public Logger.Level feignLoggerLevel() {
        return Logger.Level.FULL;
    }

    @Bean
    public Request.Options feignOptions() {
        return new Request.Options(
            5000,
            10000
        );
    }

    @Bean
    public Retryer feignRetryer() {
        return new Retryer.Default(100, 1000, 3);
    }
}

@FeignClient(
    name = "user-service",
    path = "/api/users",
    configuration = FeignConfig.class,
    fallback = UserClientFallback.class
)
public interface UserClient {
}

@Component
public class UserClientFallback implements UserClient {

    @Override
    public UserDTO getUser(Long id) {
        return UserDTO.builder()
            .id(id)
            .username("default")
            .build();
    }

    @Override
    public UserDTO createUser(UserCreateRequest request) {
        throw new ServiceUnavailableException("用户服务不可用");
    }
}
```

## 9.5 负载均衡

### 9.5.1 负载均衡策略

```java
@Configuration
public class LoadBalancerConfig {

    @Bean
    public ReactorLoadBalancer<ServiceInstance> randomLoadBalancer(
            Environment environment,
            LoadBalancerClientFactory loadBalancerClientFactory) {
        String name = environment.getProperty(LoadBalancerClientFactory.PROPERTY_NAME);
        return new RandomLoadBalancer(
            loadBalancerClientFactory.getLazyProvider(name, ServiceInstanceListSupplier.class),
            name
        );
    }

    @Bean
    public ReactorLoadBalancer<ServiceInstance> roundRobinLoadBalancer(
            Environment environment,
            LoadBalancerClientFactory loadBalancerClientFactory) {
        String name = environment.getProperty(LoadBalancerClientFactory.PROPERTY_NAME);
        return new RoundRobinLoadBalancer(
            loadBalancerClientFactory.getLazyProvider(name, ServiceInstanceListSupplier.class),
            name
        );
    }
}
```

### 9.5.2 自定义负载均衡

```java
@Component
public class CustomLoadBalancer implements ReactorServiceInstanceLoadBalancer {

    private final ObjectProvider<ServiceInstanceListSupplier> serviceInstanceListSupplierProvider;

    public CustomLoadBalancer(ObjectProvider<ServiceInstanceListSupplier> serviceInstanceListSupplierProvider) {
        this.serviceInstanceListSupplierProvider = serviceInstanceListSupplierProvider;
    }

    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        ServiceInstanceListSupplier supplier = serviceInstanceListSupplierProvider
            .getIfAvailable(() -> {
                throw new IllegalStateException("No ServiceInstanceListSupplier available");
            });

        return supplier.get(request).next()
            .map(serviceInstances -> processInstanceResponse(serviceInstances));
    }

    private Response<ServiceInstance> processInstanceResponse(List<ServiceInstance> instances) {
        if (instances.isEmpty()) {
            return new EmptyResponse();
        }

        ServiceInstance instance = selectInstance(instances);
        return new DefaultResponse(instance);
    }

    private ServiceInstance selectInstance(List<ServiceInstance> instances) {
        return instances.get(ThreadLocalRandom.current().nextInt(instances.size()));
    }
}
```

## 9.6 熔断器

### 9.6.1 Resilience4j配置

```yaml
resilience4j:
  circuitbreaker:
    instances:
      user-service:
        register-health-indicator: true
        sliding-window-size: 10
        minimum-number-of-calls: 5
        permitted-number-of-calls-in-half-open-state: 3
        automatic-transition-from-open-to-half-open-enabled: true
        wait-duration-in-open-state: 10s
        failure-rate-threshold: 50
        event-consumer-buffer-size: 10
        record-exceptions:
          - java.io.IOException
        ignore-exceptions:
          - java.lang.IllegalArgumentException

  retry:
    instances:
      user-service:
        max-attempts: 3
        wait-duration: 1s
        retry-exceptions:
          - java.io.IOException
        ignore-exceptions:
          - java.lang.IllegalArgumentException

  timelimiter:
    instances:
      user-service:
        timeout-duration: 3s
```

### 9.6.2 熔断器使用

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final UserClient userClient;

    @CircuitBreaker(name = "user-service", fallbackMethod = "getUserFallback")
    @Retry(name = "user-service")
    @TimeLimiter(name = "user-service")
    public UserDTO getUser(Long id) {
        return userClient.getUser(id);
    }

    public UserDTO getUserFallback(Long id, Exception e) {
        return UserDTO.builder()
            .id(id)
            .username("fallback")
            .build();
    }
}
```

### 9.6.3 熔断器监控

```java
@RestController
@RequestMapping("/actuator/circuitbreakers")
public class CircuitBreakerController {

    @Autowired
    private CircuitBreakerRegistry circuitBreakerRegistry;

    @GetMapping("/{name}")
    public CircuitBreaker.State getCircuitBreakerState(@PathVariable String name) {
        CircuitBreaker circuitBreaker = circuitBreakerRegistry.find(name)
            .orElseThrow(() -> new IllegalArgumentException("Circuit breaker not found"));
        return circuitBreaker.getState();
    }

    @GetMapping("/{name}/metrics")
    public CircuitBreaker.Metrics getCircuitBreakerMetrics(@PathVariable String name) {
        CircuitBreaker circuitBreaker = circuitBreakerRegistry.find(name)
            .orElseThrow(() -> new IllegalArgumentException("Circuit breaker not found"));
        return circuitBreaker.getMetrics();
    }
}
```

## 9.7 API网关

### 9.7.1 Gateway配置

```yaml
spring:
  application:
    name: api-gateway
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
    gateway:
      discovery:
        locator:
          enabled: true
          lower-case-service-id: true
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=0
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=0
      default-filters:
        - name: Retry
          args:
            retries: 3
            statuses: BAD_GATEWAY,SERVICE_UNAVAILABLE
        - name: RequestRateLimiter
          args:
            redis-rate-limiter.replenishRate: 10
            redis-rate-limiter.burstCapacity: 20
```

### 9.7.2 网关过滤器

```java
@Component
public class AuthFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");

        if (token == null || !token.startsWith("Bearer ")) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        token = token.substring(7);
        if (!validateToken(token)) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        return chain.filter(exchange);
    }

    private boolean validateToken(String token) {
        return true;
    }

    @Override
    public int getOrder() {
        return -100;
    }
}

@Component
public class LoggingFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getURI().getPath();
        String method = request.getMethod().name();

        System.out.println("Request: " + method + " " + path);

        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            ServerHttpResponse response = exchange.getResponse();
            System.out.println("Response: " + response.getStatusCode());
        }));
    }

    @Override
    public int getOrder() {
        return -1;
    }
}
```

### 9.7.3 限流配置

```java
@Configuration
public class RateLimiterConfig {

    @Bean
    public RedisRateLimiter redisRateLimiter(ReactiveRedisTemplate<String, String> redisTemplate,
                                           RedisScript<Long> redisScript,
                                           Validator validator) {
        return new DefaultRedisRateLimiter(redisTemplate, redisScript, validator);
    }

    @Bean
    public RedisScript<Long> redisScript() {
        DefaultRedisScript<Long> redisScript = new DefaultRedisScript<>();
        redisScript.setScriptSource(new ResourceScriptSource(
            new ClassPathResource("META-INF/scripts/request_rate_limiter.lua")));
        redisScript.setResultType(Long.class);
        return redisScript;
    }
}
```

## 9.8 配置中心

### 9.8.1 Nacos配置

```yaml
spring:
  application:
    name: user-service
  cloud:
    nacos:
      config:
        server-addr: localhost:8848
        namespace: dev
        group: DEFAULT_GROUP
        file-extension: yaml
        shared-configs:
          - data-id: common.yaml
            group: DEFAULT_GROUP
            refresh: true
```

### 9.8.2 动态刷新配置

```java
@RestController
@RefreshScope
public class ConfigController {

    @Value("${app.config.value}")
    private String configValue;

    @GetMapping("/config")
    public String getConfig() {
        return configValue;
    }
}
```

## 9.9 链路追踪

### 9.9.1 Sleuth配置

```yaml
spring:
  application:
    name: user-service
  sleuth:
    zipkin:
      base-url: http://localhost:9411
    sampler:
      probability: 1.0
```

### 9.9.2 自定义追踪

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final UserClient userClient;
    private final Tracer tracer;

    public OrderDTO create(OrderCreateRequest request) {
        Span newSpan = tracer.nextSpan().name("create-order");
        try (Tracer.SpanInScope ws = tracer.withSpan(newSpan.start())) {
            UserDTO user = userClient.getUser(request.getUserId());
            newSpan.tag("user.id", String.valueOf(user.getId()));
            newSpan.event("user-retrieved");
            return createOrder(request, user);
        } finally {
            newSpan.end();
        }
    }
}
```

## 9.10 互联网大厂真实项目代码示例

### 9.10.1 阿里巴巴Nacos配置

```java
package com.alibaba.cloud.config;

import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableDiscoveryClient
public class NacosDiscoveryConfig {
}
```

### 9.10.2 腾讯云Feign客户端

```java
package com.tencent.cloud.feign;

import com.tencent.cloud.dto.UserDTO;
import com.tencent.cloud.request.UserCreateRequest;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

@FeignClient(
    name = "user-service",
    path = "/api/v1/users",
    fallbackFactory = UserClientFallbackFactory.class
)
public interface UserClient {

    @GetMapping("/{id}")
    UserDTO getUser(@PathVariable("id") Long id);

    @PostMapping
    UserDTO createUser(@RequestBody UserCreateRequest request);

    @GetMapping("/username/{username}")
    UserDTO getUserByUsername(@PathVariable("username") String username);
}

@Component
public class UserClientFallbackFactory implements FallbackFactory<UserClient> {

    @Override
    public UserClient create(Throwable cause) {
        return new UserClient() {
            @Override
            public UserDTO getUser(Long id) {
                return UserDTO.builder()
                    .id(id)
                    .username("fallback")
                    .build();
            }

            @Override
            public UserDTO createUser(UserCreateRequest request) {
                throw new ServiceUnavailableException("用户服务不可用");
            }

            @Override
            public UserDTO getUserByUsername(String username) {
                return UserDTO.builder()
                    .username("fallback")
                    .build();
            }
        };
    }
}
```

### 9.10.3 美团网关配置

```java
package com.meituan.gateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayConfig {

    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("user-service", r -> r
                .path("/api/users/**")
                .filters(f -> f
                    .stripPrefix(0)
                    .retry(retryConfig -> retryConfig
                        .setRetries(3)
                        .setBackoff(Duration.ofMillis(100), Duration.ofMillis(500), 2, true)))
                .uri("lb://user-service"))
            .route("order-service", r -> r
                .path("/api/orders/**")
                .filters(f -> f
                    .stripPrefix(0)
                    .requestRateLimiter(rateLimiterConfig -> rateLimiterConfig
                        .setRateLimiter(redisRateLimiter())
                        .setKeyResolver(userKeyResolver())))
                .uri("lb://order-service"))
            .build();
    }

    @Bean
    public RedisRateLimiter redisRateLimiter() {
        return new RedisRateLimiter(10, 20);
    }

    @Bean
    public KeyResolver userKeyResolver() {
        return exchange -> exchange.getRequest().getQueryParams()
            .getFirst("user")
            .map(userId -> Mono.just(userId))
            .orElse(Mono.just("anonymous"));
    }
}
```

### 9.10.4 字节跳动熔断器

```java
package com.bytedance.resilience;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import io.github.resilience4j.timelimiter.annotation.TimeLimiter;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeoutException;

@Service
public class UserService {

    @CircuitBreaker(
        name = "user-service",
        fallbackMethod = "getUserFallback"
    )
    @Retry(
        name = "user-service",
        fallbackMethod = "getUserFallback"
    )
    @TimeLimiter(
        name = "user-service",
        fallbackMethod = "getUserFallback"
    )
    public CompletableFuture<UserDTO> getUserAsync(Long id) {
        return CompletableFuture.supplyAsync(() -> {
            return userClient.getUser(id);
        });
    }

    public CompletableFuture<UserDTO> getUserFallback(Long id, Exception e) {
        if (e instanceof TimeoutException) {
            return CompletableFuture.completedFuture(
                UserDTO.builder()
                    .id(id)
                    .username("timeout-fallback")
                    .build()
            );
        }
        return CompletableFuture.completedFuture(
            UserDTO.builder()
                .id(id)
                .username("fallback")
                .build()
        );
    }
}
```

### 9.10.5 京东健康服务调用

```java
package com.jd.health.service;

import com.jd.health.feign.PatientClient;
import com.jd.health.feign.DoctorClient;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AppointmentService {

    private final PatientClient patientClient;
    private final DoctorClient doctorClient;

    @CircuitBreaker(name = "patient-service", fallbackMethod = "getPatientFallback")
    @Retry(name = "patient-service")
    public PatientDTO getPatient(Long patientId) {
        return patientClient.getPatient(patientId);
    }

    public PatientDTO getPatientFallback(Long patientId, Exception e) {
        return PatientDTO.builder()
            .id(patientId)
            .name("未知患者")
            .build();
    }

    @CircuitBreaker(name = "doctor-service", fallbackMethod = "getDoctorFallback")
    @Retry(name = "doctor-service")
    public DoctorDTO getDoctor(Long doctorId) {
        return doctorClient.getDoctor(doctorId);
    }

    public DoctorDTO getDoctorFallback(Long doctorId, Exception e) {
        return DoctorDTO.builder()
            .id(doctorId)
            .name("未知医生")
            .build();
    }
}
```

### 9.10.6 拼多多配置中心

```java
package com.pdd.config;

import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.stereotype.Component;

@Component
@RefreshScope
public class AppConfig {

    private String configValue;
    private Integer timeout;
    private Boolean featureEnabled;

    public String getConfigValue() {
        return configValue;
    }

    public void setConfigValue(String configValue) {
        this.configValue = configValue;
    }

    public Integer getTimeout() {
        return timeout;
    }

    public void setTimeout(Integer timeout) {
        this.timeout = timeout;
    }

    public Boolean getFeatureEnabled() {
        return featureEnabled;
    }

    public void setFeatureEnabled(Boolean featureEnabled) {
        this.featureEnabled = featureEnabled;
    }
}
```

## 9.11 最佳实践

1. **服务拆分**：按业务领域拆分服务
2. **API设计**：使用RESTful风格
3. **容错机制**：实现熔断和降级
4. **配置管理**：使用配置中心统一管理
5. **链路追踪**：实现分布式追踪
6. **监控告警**：监控服务健康状态

## 9.12 小结

本章介绍了Spring Boot微服务架构的核心内容，包括：

- 微服务概述
- 服务注册与发现
- 服务调用
- 负载均衡
- 熔断器
- API网关
- 配置中心
- 链路追踪

通过本章学习，你应该能够：

- 理解微服务架构
- 实现服务注册与发现
- 使用Feign进行服务调用
- 实现熔断和降级
- 配置API网关
- 使用配置中心

下一章将介绍Spring Boot的分布式事务。
