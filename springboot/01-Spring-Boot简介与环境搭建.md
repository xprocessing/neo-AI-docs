# 第1章：Spring Boot简介与环境搭建

## 1.1 Spring Boot简介

### 1.1.1 什么是Spring Boot

Spring Boot是由Pivotal团队提供的全新框架，其设计目的是用来简化新Spring应用的初始搭建以及开发过程。该框架使用了特定的方式来进行配置，从而使开发人员不再需要定义样板化的配置。

### 1.1.2 Spring Boot核心特性

- **独立运行的Spring应用**：可以直接打包为jar，通过java -jar运行
- **内嵌Servlet容器**：无需部署WAR文件
- **自动配置**：根据项目依赖自动配置Spring应用
- **提供生产就绪功能**：如指标、健康检查、外部化配置
- **无代码生成和XML配置**：告别繁琐的XML配置

### 1.1.3 Spring Boot vs 传统Spring

| 特性 | 传统Spring | Spring Boot |
|------|-----------|-------------|
| 配置方式 | XML配置/Java配置 | 自动配置 + 简化配置 |
| 项目搭建 | 需要多个配置文件 | Starters快速搭建 |
| 部署方式 | 需要Web容器 | 内嵌容器，直接运行 |
| 开发效率 | 较低 | 大幅提升 |

## 1.2 环境搭建

### 1.2.1 JDK安装与配置

#### 推荐JDK版本
- Spring Boot 3.x：JDK 17+
- Spring Boot 2.x：JDK 8+

#### 验证JDK安装

```bash
java -version
```

### 1.2.2 Maven配置

#### Maven安装

下载Maven并配置环境变量，验证安装：

```bash
mvn -version
```

#### Maven settings.xml配置（阿里云镜像）

```xml
<mirrors>
    <mirror>
        <id>aliyunmaven</id>
        <mirrorOf>*</mirrorOf>
        <name>阿里云公共仓库</name>
        <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
</mirrors>

<profiles>
    <profile>
        <id>jdk-17</id>
        <activation>
            <activeByDefault>true</activeByDefault>
            <jdk>17</jdk>
        </activation>
        <properties>
            <maven.compiler.source>17</maven.compiler.source>
            <maven.compiler.target>17</maven.compiler.target>
            <maven.compiler.compilerVersion>17</maven.compiler.compilerVersion>
        </properties>
    </profile>
</profiles>
```

### 1.2.3 IDE选择

推荐IDE：
- **IntelliJ IDEA**（推荐）：社区版免费，Ultimate版支持Spring Boot
- **Eclipse**：配合Spring Tools Suite插件
- **VS Code**：配合Spring Boot Extension Pack

## 1.3 创建第一个Spring Boot项目

### 1.3.1 方式一：Spring Initializr网页创建

访问 https://start.spring.io/ 进行项目初始化：

```xml
<!-- pom.xml 示例 -->
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
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <description>Demo project for Spring Boot</description>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### 1.3.2 方式二：IDEA创建项目

1. File -> New -> Project
2. 选择Spring Initializr
3. 填写项目信息
4. 选择依赖（Web -> Spring Web）
5. 完成创建

### 1.3.3 第一个Spring Boot应用

#### 启动类

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

#### Controller

```java
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }
}
```

#### 运行应用

```bash
mvn spring-boot:run
```

访问 http://localhost:8080/hello

## 1.4 Spring Boot项目结构

```
demo
├── src
│   ├── main
│   │   ├── java
│   │   │   └── com
│   │   │       └── example
│   │   │           └── demo
│   │   │               ├── DemoApplication.java       # 启动类
│   │   │               ├── controller                 # 控制器层
│   │   │               ├── service                    # 服务层
│   │   │               ├── dao                        # 数据访问层
│   │   │               ├── entity                     # 实体类
│   │   │               └── config                     # 配置类
│   │   └── resources
│   │       ├── application.yml                        # 配置文件
│   │       ├── application-dev.yml                    # 开发环境配置
│   │       ├── application-prod.yml                   # 生产环境配置
│   │       ├── static                                 # 静态资源
│   │       ├── templates                               # 模板文件
│   │       └── logback-spring.xml                     # 日志配置
│   └── test                                           # 测试代码
└── pom.xml
```

## 1.5 常用Starters介绍

### 1.5.1 Web开发

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

### 1.5.2 数据访问

```xml
<!-- JPA -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<!-- MyBatis -->
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.3</version>
</dependency>

<!-- MongoDB -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb</artifactId>
</dependency>
```

### 1.5.3 安全

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

### 1.5.4 缓存

```xml
<!-- Redis -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

### 1.5.5 消息队列

```xml
<!-- RabbitMQ -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>

<!-- Kafka -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

### 1.5.6 监控

```xml
<!-- Actuator -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

## 1.6 配置文件详解

### 1.6.1 配置文件格式

Spring Boot支持两种配置文件格式：

#### application.properties

```properties
server.port=8080
spring.application.name=demo
```

#### application.yml（推荐）

```yaml
server:
  port: 8080

spring:
  application:
    name: demo
```

### 1.6.2 多环境配置

```yaml
# application.yml
spring:
  profiles:
    active: dev

---
# application-dev.yml
server:
  port: 8080

---
# application-prod.yml
server:
  port: 80
```

### 1.6.3 常用配置项

```yaml
server:
  port: 8080
  servlet:
    context-path: /api
  tomcat:
    threads:
      max: 200
      min-spare: 10

spring:
  application:
    name: demo
  datasource:
    url: jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=utf8
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true

logging:
  level:
    root: INFO
    com.example.demo: DEBUG
  file:
    name: logs/demo.log
```

## 1.7 互联网大厂真实项目代码示例

### 1.7.1 阿里巴巴Nacos配置示例

```java
package com.alibaba.nacos.example.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RefreshScope
@RestController
public class ConfigController {

    @Value("${user.name:default}")
    private String userName;

    @Value("${user.age:18}")
    private Integer userAge;

    @GetMapping("/user")
    public String getUser() {
        return "Name: " + userName + ", Age: " + userAge;
    }
}
```

### 1.7.2 腾讯云Spring Boot启动类

```java
package com.tencent.cloud.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableDiscoveryClient
@EnableAsync
@EnableScheduling
public class TencentCloudApplication {

    public static void main(String[] args) {
        SpringApplication application = new SpringApplication(TencentCloudApplication.class);
        application.setAdditionalProfiles("dev");
        application.run(args);
    }
}
```

### 1.7.3 美团Spring Boot配置类

```java
package com.meituan.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.json.Jackson2ObjectMapperBuilder;

@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper(Jackson2ObjectMapperBuilder builder) {
        ObjectMapper objectMapper = builder.createXmlMapper(false).build();
        objectMapper.registerModule(new JavaTimeModule());
        objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        return objectMapper;
    }
}
```

### 1.7.4 字节跳动多环境配置

```yaml
# application.yml
spring:
  profiles:
    active: ${ENV:dev}
  application:
    name: byte-dance-service
  cloud:
    nacos:
      discovery:
        server-addr: ${NACOS_SERVER:localhost:8848}
        namespace: ${NACOS_NAMESPACE:public}
      config:
        server-addr: ${NACOS_SERVER:localhost:8848}
        file-extension: yaml
        namespace: ${NACOS_NAMESPACE:public}

---
# application-dev.yml
server:
  port: 8080

logging:
  level:
    root: DEBUG
    com.bytedance: DEBUG

---
# application-prod.yml
server:
  port: 80

logging:
  level:
    root: INFO
    com.bytedance: INFO
```

### 1.7.5 京东健康自定义Banner

```java
package com.jd.health.config;

import org.springframework.boot.Banner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.core.env.Environment;

@SpringBootApplication
public class JdHealthApplication {

    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(JdHealthApplication.class);
        app.setBanner((environment, sourceClass, out) -> {
            out.println("""

                  ██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗███████╗
                 ██╔════╝██╔═══██╗██╔════╝██╔══██╗████╗ ████║██╔════╝
                 ██║     ██║   ██║█████╗  ███████║██╔████╔██║███████╗
                 ██║     ██║   ██║██╔══╝  ██╔══██║██║╚██╔╝██║╚════██║
                 ╚██████╗╚██████╔╝███████╗██║  ██║██║ ╚═╝ ██║███████║
                  ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
                """);
        });
        app.run(args);
    }
}
```

## 1.8 常见问题与解决方案

### 1.8.1 端口被占用

```yaml
server:
  port: 8081
```

### 1.8.2 中文乱码

```yaml
server:
  servlet:
    encoding:
      charset: UTF-8
      enabled: true
      force: true
```

### 1.8.3 依赖冲突

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

## 1.9 最佳实践

1. **使用Starters**：快速集成常用功能
2. **遵循约定优于配置**：减少不必要的配置
3. **合理使用 profiles**：区分不同环境配置
4. **统一异常处理**：提供友好的错误信息
5. **日志规范**：使用统一的日志格式
6. **版本管理**：使用spring-boot-starter-parent统一管理版本

## 1.10 小结

本章介绍了Spring Boot的基本概念、环境搭建、项目创建和配置管理。通过本章学习，你应该能够：

- 理解Spring Boot的核心特性和优势
- 搭建Spring Boot开发环境
- 创建并运行第一个Spring Boot应用
- 熟悉Spring Boot项目结构
- 掌握常用Starters和配置文件的使用

下一章将深入讲解Spring Boot的核心概念与自动配置原理。
