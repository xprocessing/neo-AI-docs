# Spring Boot 配置管理

Spring Boot 提供了强大的配置管理功能，允许开发者通过多种方式配置应用程序。

## application.properties vs application.yml

Spring Boot 支持多种配置文件格式，最常用的是 `.properties` 和 `.yml`。

### application.properties 示例

```properties
# 服务器配置
server.port=8080
server.servlet.context-path=/api

# 数据库配置
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
spring.datasource.username=root
spring.datasource.password=password
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# 自定义配置
app.name=My Spring Boot App
app.version=1.0.0
```

### application.yml 示例

```yaml
server:
  port: 8080
  servlet:
    context-path: /api

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver

app:
  name: My Spring Boot App
  version: 1.0.0
```

## 配置类和 @ConfigurationProperties

创建配置类来映射配置属性：

```java
@Component
@ConfigurationProperties(prefix = "app.database")
public class DatabaseProperties {
    private String url;
    private String username;
    private String password;
    private int maxPoolSize = 10;
    
    // getters and setters
    public String getUrl() {
        return url;
    }
    
    public void setUrl(String url) {
        this.url = url;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    public int getMaxPoolSize() {
        return maxPoolSize;
    }
    
    public void setMaxPoolSize(int maxPoolSize) {
        this.maxPoolSize = maxPoolSize;
    }
}
```

对应的配置：

```yaml
app:
  database:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
    max-pool-size: 20
```

## 配置文件优先级

Spring Boot 按以下顺序加载配置，后面的会覆盖前面的：

1. 默认属性（通过 SpringApplication.setDefaultProperties 设置）
2. @PropertySource 注解
3. 配置文件 (application.properties 或 application.yml)
4. 命令行参数
5. 环境变量

## Profile 配置

创建不同环境的配置文件：

```
application.yml          # 通用配置
application-dev.yml      # 开发环境
application-test.yml     # 测试环境
application-prod.yml     # 生产环境
```

激活 Profile 的方式：

```java
@SpringBootApplication
public class MyApplication {
    public static void main(String[] args) {
        System.setProperty("spring.profiles.active", "dev");
        SpringApplication.run(MyApplication.class, args);
    }
}
```

或者在配置文件中：

```yaml
spring:
  profiles:
    active: dev
```

## 使用 @Value 注解

直接注入配置值：

```java
@RestController
public class ConfigController {
    @Value("${app.name}")
    private String appName;
    
    @Value("${server.port}")
    private int port;
    
    @GetMapping("/config")
    public Map<String, Object> getConfig() {
        Map<String, Object> config = new HashMap<>();
        config.put("appName", appName);
        config.put("port", port);
        return config;
    }
}
```