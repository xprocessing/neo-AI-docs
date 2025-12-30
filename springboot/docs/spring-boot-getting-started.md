# Spring Boot 入门指南

Spring Boot 是一个基于 Spring 框架的快速开发框架，它简化了 Spring 应用的搭建和开发过程。本指南将带您从零开始了解 Spring Boot。

## 核心特性

1. **自动配置**：Spring Boot 可以根据类路径中的依赖自动配置应用程序
2. **起步依赖**：简化 Maven/Gradle 配置，提供一系列预定义的依赖组合
3. **嵌入式服务器**：内置 Tomcat、Jetty 或 Undertow，无需部署 WAR 文件
4. **生产就绪特性**：提供健康检查、指标监控等功能

## 快速开始

创建一个简单的 Spring Boot 应用：

```java
@SpringBootApplication
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}

@RestController
class HelloController {
    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }
}
```

## 项目结构

```
src
├── main
│   ├── java
│   │   └── com
│   │       └── example
│   │           └── demo
│   │               ├── DemoApplication.java
│   │               ├── controller
│   │               ├── service
│   │               ├── repository
│   │               └── model
│   └── resources
│       ├── application.properties
│       ├── static
│       └── templates
└── test
    └── java
        └── com
            └── example
                └── demo
```

## 依赖管理

在 `pom.xml` 中添加 Spring Boot 起步依赖：

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
</dependencies>
```

## 运行应用

使用以下命令运行应用：

```bash
mvn spring-boot:run
```

或者打包后运行：

```bash
mvn package
java -jar target/demo-0.0.1-SNAPSHOT.jar
```