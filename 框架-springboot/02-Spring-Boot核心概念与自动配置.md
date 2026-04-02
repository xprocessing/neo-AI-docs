# 第2章：Spring Boot核心概念与自动配置

## 2.1 Spring Boot核心注解

### 2.1.1 @SpringBootApplication

`@SpringBootApplication` 是一个复合注解，包含了三个核心注解：

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = {
    @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
    @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class)
})
public @interface SpringBootApplication {
    // ...
}
```

#### @SpringBootConfiguration

标记为Spring配置类，等同于`@Configuration`：

```java
@SpringBootConfiguration
public class AppConfig {
    @Bean
    public UserService userService() {
        return new UserService();
    }
}
```

#### @EnableAutoConfiguration

开启自动配置，是Spring Boot的核心：

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@AutoConfigurationPackage
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {
    // ...
}
```

#### @ComponentScan

自动扫描组件：

```java
@SpringBootApplication
@ComponentScan(basePackages = "com.example.demo")
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

### 2.1.2 其他核心注解

#### @RestController

组合了`@Controller`和`@ResponseBody`：

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
}
```

#### @ConfigurationProperties

绑定配置属性：

```java
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private String name;
    private String version;
    private Database database;

    public static class Database {
        private String url;
        private String username;
        private String password;

        // getters and setters
    }

    // getters and setters
}
```

配置文件：

```yaml
app:
  name: demo-app
  version: 1.0.0
  database:
    url: jdbc:mysql://localhost:3306/demo
    username: root
    password: root
```

#### @Value

注入配置值：

```java
@Component
public class MyComponent {

    @Value("${app.name}")
    private String appName;

    @Value("${app.version:1.0.0}")
    private String appVersion;

    @Value("#{systemProperties['user.home']}")
    private String userHome;
}
```

#### @Conditional

条件化装配Bean：

```java
@Configuration
public class ConditionalConfig {

    @Bean
    @ConditionalOnProperty(name = "cache.enabled", havingValue = "true")
    public CacheManager cacheManager() {
        return new SimpleCacheManager();
    }

    @Bean
    @ConditionalOnClass(RedisTemplate.class)
    public RedisTemplate<String, Object> redisTemplate() {
        return new RedisTemplate<>();
    }

    @Bean
    @ConditionalOnMissingBean(DataSource.class)
    public DataSource defaultDataSource() {
        return new HikariDataSource();
    }
}
```

## 2.2 自动配置原理

### 2.2.1 自动配置流程

```
1. @EnableAutoConfiguration
   ↓
2. AutoConfigurationImportSelector
   ↓
3. 读取 spring.factories / spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
   ↓
4. 过滤条件（@Conditional）
   ↓
5. 注册Bean
```

### 2.2.2 自动配置源码分析

#### AutoConfigurationImportSelector

```java
public class AutoConfigurationImportSelector implements DeferredImportSelector {

    @Override
    public String[] selectImports(AnnotationMetadata annotationMetadata) {
        if (!isEnabled(annotationMetadata)) {
            return NO_IMPORTS;
        }
        AutoConfigurationEntry autoConfigurationEntry =
            getAutoConfigurationEntry(annotationMetadata);
        return StringUtils.toStringArray(autoConfigurationEntry.getConfigurations());
    }

    protected AutoConfigurationEntry getAutoConfigurationEntry(
            AnnotationMetadata annotationMetadata) {
        if (!isEnabled(annotationMetadata)) {
            return EMPTY_ENTRY;
        }
        AnnotationAttributes attributes = getAttributes(annotationMetadata);
        List<String> configurations = getCandidateConfigurations(annotationMetadata, attributes);
        configurations = removeDuplicates(configurations);
        Set<String> exclusions = getExclusions(annotationMetadata, attributes);
        checkExcludedClasses(configurations, exclusions);
        configurations.removeAll(exclusions);
        configurations = getConfigurationClassFilter().filter(configurations);
        fireAutoConfigurationImportEvents(configurations, exclusions);
        return new AutoConfigurationEntry(configurations, exclusions);
    }

    protected List<String> getCandidateConfigurations(
            AnnotationMetadata metadata, AnnotationAttributes attributes) {
        List<String> configurations = SpringFactoriesLoader.loadFactoryNames(
            getSpringFactoriesLoaderFactoryClass(), getBeanClassLoader());
        Assert.notEmpty(configurations,
            "No auto configuration classes found in META-INF/spring.factories");
        return configurations;
    }
}
```

### 2.2.3 自定义自动配置

#### 创建自动配置类

```java
@Configuration
@ConditionalOnClass(HelloService.class)
@EnableConfigurationProperties(HelloProperties.class)
public class HelloAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public HelloService helloService(HelloProperties properties) {
        HelloService helloService = new HelloService();
        helloService.setMessage(properties.getMessage());
        return helloService;
    }
}
```

#### 创建配置属性类

```java
@ConfigurationProperties(prefix = "hello")
public class HelloProperties {

    private String message = "Hello World";

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
```

#### 注册自动配置

在 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 中：

```
com.example.autoconfigure.HelloAutoConfiguration
```

#### 使用自定义Starter

```java
@RestController
public class HelloController {

    @Autowired
    private HelloService helloService;

    @GetMapping("/hello")
    public String hello() {
        return helloService.sayHello();
    }
}
```

配置文件：

```yaml
hello:
  message: Hello Spring Boot!
```

## 2.3 条件注解详解

### 2.3.1 @ConditionalOnClass

类路径中存在指定类时生效：

```java
@Configuration
@ConditionalOnClass(name = "com.mysql.cj.jdbc.Driver")
public class MySqlAutoConfiguration {

    @Bean
    public DataSource dataSource() {
        return new HikariDataSource();
    }
}
```

### 2.3.2 @ConditionalOnMissingClass

类路径中不存在指定类时生效：

```java
@Configuration
@ConditionalOnMissingClass("com.mysql.cj.jdbc.Driver")
public class H2AutoConfiguration {

    @Bean
    public DataSource dataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }
}
```

### 2.3.3 @ConditionalOnBean

容器中存在指定Bean时生效：

```java
@Configuration
public class CacheConfiguration {

    @Bean
    @ConditionalOnBean(RedisTemplate.class)
    public CacheManager redisCacheManager(RedisTemplate redisTemplate) {
        RedisCacheManager cacheManager = new RedisCacheManager(redisTemplate);
        cacheManager.setCacheNames(Arrays.asList("users", "products"));
        return cacheManager;
    }
}
```

### 2.3.4 @ConditionalOnMissingBean

容器中不存在指定Bean时生效：

```java
@Configuration
public class DefaultConfiguration {

    @Bean
    @ConditionalOnMissingBean(PasswordEncoder.class)
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### 2.3.5 @ConditionalOnProperty

配置属性满足条件时生效：

```java
@Configuration
@ConditionalOnProperty(
    prefix = "feature",
    name = "enabled",
    havingValue = "true",
    matchIfMissing = false
)
public class FeatureConfiguration {

    @Bean
    public FeatureService featureService() {
        return new FeatureService();
    }
}
```

配置：

```yaml
feature:
  enabled: true
```

### 2.3.6 @ConditionalOnExpression

SpEL表达式为true时生效：

```java
@Configuration
@ConditionalOnExpression("'${environment}' == 'prod' and '${feature.enabled}' == 'true'")
public class ProductionConfiguration {

    @Bean
    public ProductionService productionService() {
        return new ProductionService();
    }
}
```

### 2.3.7 @ConditionalOnResource

资源存在时生效：

```java
@Configuration
@ConditionalOnResource(resources = "classpath:custom-config.xml")
public class CustomResourceConfiguration {

    @Bean
    public CustomConfig customConfig() {
        return new CustomConfig();
    }
}
```

### 2.3.8 @ConditionalOnWebApplication

Web应用时生效：

```java
@Configuration
@ConditionalOnWebApplication
public class WebConfiguration {

    @Bean
    public WebMvcConfigurer webMvcConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                    .allowedOrigins("*")
                    .allowedMethods("*");
            }
        };
    }
}
```

### 2.3.9 @ConditionalOnNotWebApplication

非Web应用时生效：

```java
@Configuration
@ConditionalOnNotWebApplication
public class CommandLineConfiguration {

    @Bean
    public CommandLineRunner commandLineRunner() {
        return args -> {
            System.out.println("Running in non-web mode");
        };
    }
}
```

## 2.4 Bean的生命周期

### 2.4.1 Bean生命周期回调

#### 初始化回调

```java
@Component
public class MyBean implements InitializingBean {

    @PostConstruct
    public void init() {
        System.out.println("@PostConstruct called");
    }

    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("InitializingBean.afterPropertiesSet() called");
    }

    @Bean(initMethod = "customInit")
    public MyBean myBean() {
        return new MyBean();
    }

    public void customInit() {
        System.out.println("customInit() called");
    }
}
```

#### 销毁回调

```java
@Component
public class MyBean implements DisposableBean {

    @PreDestroy
    public void destroy() {
        System.out.println("@PreDestroy called");
    }

    @Override
    public void destroy() throws Exception {
        System.out.println("DisposableBean.destroy() called");
    }

    @Bean(destroyMethod = "customDestroy")
    public MyBean myBean() {
        return new MyBean();
    }

    public void customDestroy() {
        System.out.println("customDestroy() called");
    }
}
```

### 2.4.2 Bean作用域

```java
@Component
@Scope("singleton")
public class SingletonBean {
}

@Component
@Scope("prototype")
public class PrototypeBean {
}

@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestBean {
}

@Component
@Scope(value = WebApplicationContext.SCOPE_SESSION, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class SessionBean {
}
```

## 2.5 互联网大厂真实项目代码示例

### 2.5.1 阿里巴巴Nacos自动配置

```java
package com.alibaba.cloud.nacos;

import com.alibaba.cloud.nacos.registry.NacosAutoServiceRegistration;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.cloud.client.serviceregistry.AutoServiceRegistrationAutoConfiguration;
import org.springframework.context.annotation.Bean;

@AutoConfiguration(after = AutoServiceRegistrationAutoConfiguration.class)
@ConditionalOnProperty(value = "spring.cloud.nacos.discovery.enabled",
    matchIfMissing = true)
@EnableConfigurationProperties(NacosDiscoveryProperties.class)
public class NacosDiscoveryAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public NacosServiceDiscovery nacosServiceDiscovery(
            NacosDiscoveryProperties discoveryProperties) {
        return new NacosServiceDiscovery(discoveryProperties);
    }

    @Bean
    @ConditionalOnBean(AutoServiceRegistrationProperties.class)
    public NacosAutoServiceRegistration nacosAutoServiceRegistration(
            NacosServiceRegistry registry,
            NacosRegistration registration,
            NacosDiscoveryProperties nacosDiscoveryProperties) {
        return new NacosAutoServiceRegistration(registry, registration,
            nacosDiscoveryProperties);
    }
}
```

### 2.5.2 腾讯云条件配置

```java
package com.tencent.cloud.common.config;

import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConditionalOnClass(name = "com.tencentcloudapi.cvm.v20170312.CvmClient")
@ConditionalOnProperty(prefix = "tencent.cloud.cvm", name = "enabled", havingValue = "true")
public class TencentCvmAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public CvmClient cvmClient(CvmProperties properties) {
        Credential cred = new Credential(properties.getSecretId(),
            properties.getSecretKey());
        ClientProfile clientProfile = new ClientProfile();
        return new CvmClient(cred, properties.getRegion(), clientProfile);
    }
}
```

### 2.5.3 美团多数据源配置

```java
package com.meituan.datasource.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class MultiDataSourceConfig {

    @Bean
    @Primary
    @ConfigurationProperties(prefix = "spring.datasource.primary")
    public DataSource primaryDataSource() {
        return HikariDataSource();
    }

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.secondary")
    @ConditionalOnProperty(name = "spring.datasource.secondary.enabled", havingValue = "true")
    public DataSource secondaryDataSource() {
        return HikariDataSource();
    }

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.readonly")
    @ConditionalOnProperty(name = "spring.datasource.readonly.enabled", havingValue = "true")
    public DataSource readonlyDataSource() {
        return HikariDataSource();
    }
}
```

### 2.5.4 字节跳动动态配置

```java
package com.bytedance.config;

import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;
import java.util.concurrent.ThreadPoolExecutor;

@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean(name = "taskExecutor")
    @ConditionalOnExpression("'${async.enabled}' == 'true'")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(200);
        executor.setThreadNamePrefix("async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

### 2.5.5 京东健康自定义条件注解

```java
package com.jd.health.condition;

import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.type.AnnotatedTypeMetadata;

public class OnKubernetesCondition implements Condition {

    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        String env = context.getEnvironment().getProperty("app.env", "local");
        return "k8s".equalsIgnoreCase(env);
    }
}

@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Conditional(OnKubernetesCondition)
public @interface ConditionalOnKubernetes {
}

@Configuration
public class HealthConfig {

    @Bean
    @ConditionalOnKubernetes
    public KubernetesHealthIndicator kubernetesHealthIndicator() {
        return new KubernetesHealthIndicator();
    }
}
```

### 2.5.6 拼多多配置属性绑定

```java
package com.pdd.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "pdd.mq")
public class MqProperties {

    private RocketMQ rocketMQ = new RocketMQ();

    private RabbitMQ rabbitMQ = new RabbitMQ();

    @Data
    public static class RocketMQ {
        private String nameServer;
        private String producerGroup;
        private Integer retryTimesWhenSendFailed = 2;
        private Integer sendMsgTimeout = 3000;
    }

    @Data
    public static class RabbitMQ {
        private String host;
        private Integer port = 5672;
        private String username;
        private String password;
        private String virtualHost;
    }
}
```

### 2.5.7 网易云环境感知配置

```java
package com.netease.config;

import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class EnvironmentAwareConfig {

    @Bean
    @ConditionalOnExpression("'${app.env}' == 'dev' or '${app.env}' == 'test'")
    public DevTestFeature devTestFeature() {
        return new DevTestFeature();
    }

    @Bean
    @ConditionalOnExpression("'${app.env}' == 'prod'")
    public ProdFeature prodFeature() {
        return new ProdFeature();
    }

    @Bean
    @ConditionalOnExpression("'${app.env}' == 'staging'")
    public StagingFeature stagingFeature() {
        return new StagingFeature();
    }
}
```

## 2.6 自定义Starter开发

### 2.6.1 Starter结构

```
my-spring-boot-starter
├── pom.xml
└── src
    └── main
        ├── java
        │   └── com.example.autoconfigure
        │       ├── MyAutoConfiguration.java
        │       └── MyProperties.java
        └── resources
            └── META-INF
                └── spring
                    └── org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

### 2.6.2 完整示例

#### pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>my-spring-boot-starter</artifactId>
    <version>1.0.0</version>
    <name>my-spring-boot-starter</name>
    <description>My Custom Spring Boot Starter</description>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-autoconfigure</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-configuration-processor</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>
</project>
```

#### MyProperties.java

```java
package com.example.autoconfigure;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "my.starter")
public class MyProperties {

    private String name = "default";
    private boolean enabled = true;
    private int timeout = 1000;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public int getTimeout() {
        return timeout;
    }

    public void setTimeout(int timeout) {
        this.timeout = timeout;
    }
}
```

#### MyAutoConfiguration.java

```java
package com.example.autoconfigure;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(MyProperties.class)
@ConditionalOnProperty(prefix = "my.starter", name = "enabled", havingValue = "true",
    matchIfMissing = true)
public class MyAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MyService myService(MyProperties properties) {
        MyService service = new MyService();
        service.setName(properties.getName());
        service.setTimeout(properties.getTimeout());
        return service;
    }
}
```

#### AutoConfiguration.imports

```
com.example.autoconfigure.MyAutoConfiguration
```

## 2.7 最佳实践

1. **合理使用条件注解**：避免过度复杂的条件判断
2. **提供默认配置**：确保Starter开箱即用
3. **文档完善**：提供详细的配置说明
4. **版本兼容**：保持向后兼容性
5. **性能考虑**：避免自动配置影响启动速度

## 2.8 小结

本章深入讲解了Spring Boot的核心概念与自动配置原理，包括：

- 核心注解的使用
- 自动配置的工作原理
- 条件注解的详细说明
- Bean的生命周期管理
- 自定义Starter的开发

通过本章学习，你应该能够：

- 理解Spring Boot自动配置的原理
- 熟练使用各种条件注解
- 开发自定义Starter
- 掌握Bean的生命周期管理

下一章将介绍Spring Boot的Web开发。
