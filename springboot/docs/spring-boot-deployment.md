# Spring Boot 部署和运维

本章将详细介绍 Spring Boot 应用的部署策略、运维实践和生产环境最佳实践。

## 打包和构建

### Maven 打包配置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>my-spring-boot-app</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <!-- 其他依赖 -->
    </dependencies>

    <build>
        <finalName>${project.artifactId}</finalName>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
            
            <!-- 构建信息插件 -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <executions>
                    <execution>
                        <goals>
                            <goal>build-info</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            
            <!-- Git 信息插件 -->
            <plugin>
                <groupId>io.github.git-commit-id</groupId>
                <artifactId>git-commit-id-maven-plugin</artifactId>
                <version>7.0.0</version>
                <executions>
                    <execution>
                        <id>get-the-git-infos</id>
                        <goals>
                            <goal>revision</goal>
                        </goals>
                        <phase>initialize</phase>
                    </execution>
                </executions>
                <configuration>
                    <verbose>true</verbose>
                    <generateGitPropertiesFile>true</generateGitPropertiesFile>
                    <generateGitPropertiesFilename>src/main/resources/git.properties</generateGitPropertiesFilename>
                    <failOnNoGitDirectory>false</failOnNoGitDirectory>
                    <failOnUnableToExtractRepoInfo>false</failOnUnableToExtractRepoInfo>
                    <includeOnlyProperties>
                        <includeOnlyProperty>^git.commit.(time|id.abbr)$</includeOnlyProperty>
                        <includeOnlyProperty>^git.build.(time|version)$</includeOnlyProperty>
                        <includeOnlyProperty>^git.branch$</includeOnlyProperty>
                    </includeOnlyProperties>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### Gradle 打包配置

```gradle
plugins {
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
    id 'java'
}

group = 'com.example'
version = '1.0.0'
sourceCompatibility = '17'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    // 其他依赖
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

// Git 插件
plugins {
    id 'org.ajoberstar.grgit' version '5.2.0'
}

task generateGitProperties {
    doLast {
        def gitPropertiesFile = file("$buildDir/resources/main/git.properties")
        def git = org.ajoberstar.grgit.Grgit.open(currentDir: projectDir)
        
        gitPropertiesFile.parentFile.mkdirs()
        def properties = new Properties()
        properties.setProperty('git.branch', git.branch.current().name)
        properties.setProperty('git.commit.id', git.head().id)
        properties.setProperty('git.commit.time', git.head().time.toString())
        properties.store(gitPropertiesFile.newWriter(), null)
    }
}

processResources.dependsOn generateGitProperties
```

## Docker 部署

### Dockerfile

```dockerfile
# 使用多阶段构建
FROM eclipse-temurin:17-jdk-alpine AS build

# 安装构建依赖
WORKDIR /app
COPY . .

# 构建应用
RUN ./mvnw clean package -DskipTests

# 生产运行时镜像
FROM eclipse-temurin:17-jre-alpine

LABEL maintainer="your-email@example.com"
LABEL description="Spring Boot Application"

# 创建应用用户
RUN addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser

WORKDIR /app

# 从构建阶段复制 JAR 文件
COPY --from=build /app/target/my-spring-boot-app.jar app.jar

# 更改文件所有者
RUN chown appuser:appuser /app/app.jar

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8080

# JVM 参数优化
ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:+UseContainerSupport"

# 启动命令
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

### Docker Compose 配置

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: spring-boot-app
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:mysql://db:3306/myapp
      - SPRING_DATASOURCE_USERNAME=user
      - SPRING_DATASOURCE_PASSWORD=password
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: mysql:8.0
    container_name: mysql-db
    environment:
      MYSQL_DATABASE: myapp
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init:/docker-entrypoint-initdb.d
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: redis-cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

### 应用配置文件

```yaml
# application-docker.yml
server:
  port: 8080

spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:h2:mem:testdb}
    username: ${SPRING_DATASOURCE_USERNAME:sa}
    password: ${SPRING_DATASOURCE_PASSWORD:}
    driver-class-name: ${SPRING_DATASOURCE_DRIVER:org.h2.Driver}
  
  jpa:
    hibernate:
      ddl-auto: ${SPRING_JPA_HIBERNATE_DDL_AUTO:update}
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQL8Dialect
        format_sql: true
  
  redis:
    host: ${SPRING_REDIS_HOST:localhost}
    port: ${SPRING_REDIS_PORT:6379}
    timeout: 2000ms
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env,loggers
  endpoint:
    health:
      show-details: when-authorized
  server:
    port: 8080  # 在容器中使用相同端口

logging:
  level:
    com.example: INFO
    org.springframework.web: INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: /app/logs/application.log
    max-size: 10MB
    max-history: 30
```

## Kubernetes 部署

### Deployment 配置

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-boot-app
  labels:
    app: spring-boot-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spring-boot-app
  template:
    metadata:
      labels:
        app: spring-boot-app
    spec:
      containers:
      - name: spring-boot-app
        image: your-registry/spring-boot-app:latest
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "k8s"
        - name: JAVA_OPTS
          value: "-Xms512m -Xmx1024m -XX:+UseG1GC"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: logs-volume
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: spring-boot-app-service
spec:
  selector:
    app: spring-boot-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

## 环境配置管理

### 多环境配置

```yaml
# application.yml (通用配置)
spring:
  application:
    name: my-spring-boot-app
  profiles:
    active: @spring.profiles.active@  # Maven 属性占位符

server:
  servlet:
    context-path: /api
  compression:
    enabled: true
    mime-types: text/html,text/xml,text/plain,text/css,text/javascript,application/javascript,application/json
    min-response-size: 1024

# application-dev.yml (开发环境)
spring:
  datasource:
    url: jdbc:h2:mem:devdb
    username: sa
    password:
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true

logging:
  level:
    com.example: DEBUG
    org.springframework.web: DEBUG

# application-test.yml (测试环境)
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/testdb
    username: testuser
    password: testpassword
    driver-class-name: com.mysql.cj.jdbc.Driver

# application-prod.yml (生产环境)
spring:
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USERNAME}
    password: ${DATABASE_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 20000
      idle-timeout: 300000
      max-lifetime: 1200000
      leak-detection-threshold: 60000

logging:
  level:
    com.example: INFO
    org.springframework.web: WARN
  file:
    name: /var/log/app/application.log

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: never
```

## 启动脚本

### Linux 启动脚本

```bash
#!/bin/bash
# spring-boot-app.sh - Spring Boot Application Control Script

APP_NAME="spring-boot-app"
APP_JAR="my-spring-boot-app.jar"
JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:+UseContainerSupport"
PID_FILE="/var/run/$APP_NAME.pid"
LOG_FILE="/var/log/$APP_NAME.log"
CONFIG_FILE="/etc/$APP_NAME/application.yml"

# 检查 Java 是否安装
if ! command -v java &> /dev/null; then
    echo "Java is not installed. Exiting."
    exit 1
fi

# 检查应用是否正在运行
is_running() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if kill -0 $PID 2>/dev/null; then
            return 0
        else
            rm -f $PID_FILE
        fi
    fi
    return 1
}

case "$1" in
    start)
        if is_running; then
            echo "$APP_NAME is already running."
            exit 1
        fi
        
        echo "Starting $APP_NAME..."
        nohup java $JAVA_OPTS -jar $APP_JAR --spring.config.location=$CONFIG_FILE >> $LOG_FILE 2>&1 &
        echo $! > $PID_FILE
        echo "$APP_NAME started with PID $(cat $PID_FILE)"
        ;;
        
    stop)
        if is_running; then
            PID=$(cat $PID_FILE)
            echo "Stopping $APP_NAME (PID: $PID)..."
            kill $PID
            rm -f $PID_FILE
            echo "$APP_NAME stopped."
        else
            echo "$APP_NAME is not running."
        fi
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        if is_running; then
            PID=$(cat $PID_FILE)
            echo "$APP_NAME is running with PID: $PID"
        else
            echo "$APP_NAME is not running."
        fi
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
```

### Windows 启动脚本

```batch
@echo off
setlocal

set APP_NAME=spring-boot-app
set APP_JAR=my-spring-boot-app.jar
set JAVA_OPTS=-Xms512m -Xmx1024m -XX:+UseG1GC
set PID_FILE=%TEMP%\%APP_NAME%.pid
set LOG_FILE=%TEMP%\%APP_NAME%.log
set CONFIG_FILE=application.yml

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="status" goto status

echo Usage: %0 {start^|stop^|restart^|status}
goto end

:start
echo Starting %APP_NAME%...
start "Spring Boot App" /MIN java %JAVA_OPTS% -jar %APP_JAR% --spring.config.location=%CONFIG_FILE% > %LOG_FILE% 2>&1
echo %ERRORLEVEL% > %PID_FILE%
echo %APP_NAME% started.
goto end

:stop
if exist %PID_FILE% (
    echo Stopping %APP_NAME%...
    for /f %%i in (%PID_FILE%) do taskkill /PID %%i /F
    del %PID_FILE%
    echo %APP_NAME% stopped.
) else (
    echo %APP_NAME% is not running.
)
goto end

:restart
call :stop
timeout /t 2 /nobreak
call :start
goto end

:status
if exist %PID_FILE% (
    echo %APP_NAME% is running.
) else (
    echo %APP_NAME% is not running.
)
goto end

:end
endlocal
```

## 性能调优

### JVM 调优参数

```bash
# 生产环境 JVM 参数示例
JAVA_OPTS="
  -Xms2g                    # 初始堆大小
  -Xmx4g                    # 最大堆大小
  -XX:MetaspaceSize=256m     # 元空间初始大小
  -XX:MaxMetaspaceSize=512m  # 元空间最大大小
  -XX:+UseG1GC              # 使用 G1 垃圾收集器
  -XX:MaxGCPauseMillis=200   # 最大 GC 暂停时间
  -XX:G1HeapRegionSize=16m   # G1 堆区域大小
  -XX:+UseStringDeduplication # 字符串去重
  -XX:+UseCompressedOops     # 压缩普通对象指针
  -XX:+UseCompressedClassPointers # 压缩类指针
  -XX:+AlwaysPreTouch        # 启动时提交所有内存
  -Djava.security.egd=file:/dev/./urandom # 解决随机数生成器慢的问题
"
```

### 应用性能配置

```yaml
# application-prod.yml
server:
  undertow:
    # Undertow 性能调优
    threads:
      io: 2 # IO 线程数
      worker: 32 # 工作线程数
    buffer-size: 1024 # 缓冲区大小
    direct-buffers: true

spring:
  datasource:
    # 数据库连接池优化
    hikari:
      maximum-pool-size: 20
      minimum-idle: 10
      connection-timeout: 20000
      idle-timeout: 300000
      max-lifetime: 1200000
      connection-test-query: SELECT 1
      validation-timeout: 5000
      leak-detection-threshold: 60000

  jpa:
    # JPA 性能优化
    properties:
      hibernate:
        generate_statistics: false
        order_inserts: true
        order_updates: true
        batch_size: 25
        jdbc:
          batch_size: 25
          fetch_size: 50

  redis:
    # Redis 连接优化
    timeout: 2000ms
    lettuce:
      pool:
        max-active: 20
        max-idle: 10
        min-idle: 5
        max-wait: 2000ms

# 缓存配置
spring:
  cache:
    type: redis
    redis:
      time-to-live: 3600000 # 1小时

# Actuator 配置（生产环境）
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: never
    metrics:
      enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
    distribution:
      percentiles-histogram:
        all: true
      sla:
        http.server.requests: 100ms, 500ms, 1000ms
```

## 日志管理

### 日志配置

```xml
<!-- logback-spring.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <include resource="org/springframework/boot/logging/logback/defaults.xml"/>
    
    <springProfile name="dev">
        <include resource="org/springframework/boot/logging/logback/console-appender.xml"/>
        <root level="INFO">
            <appender-ref ref="CONSOLE"/>
        </root>
    </springProfile>
    
    <springProfile name="!dev">
        <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
            <file>logs/application.log</file>
            <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
                <pattern>${FILE_LOG_PATTERN}</pattern>
            </encoder>
            <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
                <fileNamePattern>logs/application.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
                <maxFileSize>100MB</maxFileSize>
                <maxHistory>30</maxHistory>
                <totalSizeCap>3GB</totalSizeCap>
            </rollingPolicy>
        </appender>
        
        <appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
            <appender-ref ref="FILE"/>
            <queueSize>512</queueSize>
            <discardingThreshold>0</discardingThreshold>
        </appender>
        
        <root level="INFO">
            <appender-ref ref="ASYNC_FILE"/>
        </root>
    </springProfile>
    
    <!-- 特定包的日志级别 -->
    <logger name="com.example" level="DEBUG" additivity="false">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="ASYNC_FILE"/>
    </logger>
</configuration>
```

## 监控和告警

### 自定义健康指示器

```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try (Connection connection = dataSource.getConnection()) {
            if (connection.isValid(2)) {
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

@Component
public class ExternalServiceHealthIndicator implements HealthIndicator {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Override
    public Health health() {
        try {
            ResponseEntity<String> response = restTemplate
                .getForEntity("http://external-service/health", String.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                return Health.up()
                    .withDetail("externalService", "Available")
                    .withDetail("responseTime", response.getHeaders().get("Response-Time"))
                    .build();
            } else {
                return Health.down()
                    .withDetail("externalService", "Service returned: " + response.getStatusCode())
                    .build();
            }
        } catch (Exception e) {
            return Health.down()
                .withDetail("externalService", "Service unavailable")
                .withException(e)
                .build();
        }
    }
}
```

## 部署最佳实践

### 部署检查清单

1. **配置验证**
   - 确保所有环境特定的配置都已正确设置
   - 验证数据库连接参数
   - 检查外部服务的连接信息

2. **安全检查**
   - 禁用生产环境的调试功能
   - 验证 Actuator 端点的安全性
   - 确保敏感信息不硬编码在配置中

3. **性能调优**
   - 设置合适的 JVM 参数
   - 配置适当的连接池大小
   - 启用缓存和压缩

4. **监控设置**
   - 配置健康检查端点
   - 设置日志级别和输出
   - 启用必要的指标收集

5. **备份和恢复**
   - 制定数据库备份策略
   - 设置配置文件版本控制
   - 准备回滚计划