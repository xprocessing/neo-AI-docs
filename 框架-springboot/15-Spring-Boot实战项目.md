# 第15章：Spring Boot实战项目

## 15.1 项目概述

### 15.1.1 项目背景

本章将通过一个完整的电商订单管理系统实战项目，综合运用前面章节所学的Spring Boot技术栈。该项目将涵盖用户管理、商品管理、订单处理、支付集成、消息通知等核心功能模块。

**项目名称**：电商订单管理系统（E-Commerce Order Management System）

**技术栈**：
- Spring Boot 3.2.x
- Spring Security + JWT
- Spring Data JPA + MySQL
- Redis + Caffeine（多级缓存）
- RabbitMQ（消息队列）
- Elasticsearch（商品搜索）
- MinIO（文件存储）
- Docker + Docker Compose
- Prometheus + Grafana（监控）

### 15.1.2 项目架构

```
ecommerce-order-system/
├── ecommerce-common/          # 公共模块
├── ecommerce-user/            # 用户服务
├── ecommerce-product/         # 商品服务
├── ecommerce-order/           # 订单服务
├── ecommerce-payment/         # 支付服务
├── ecommerce-notification/    # 通知服务
└── ecommerce-gateway/         # 网关服务
```

**微服务架构图**：

```
                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Gateway   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
   │  User   │      │  Product  │      │  Order  │
   │ Service │      │  Service  │      │ Service │
   └────┬────┘      └─────┬─────┘      └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
   │ Payment │      │ Notification│      │  Redis  │
   │ Service │      │  Service   │      │  Cache  │
   └────┬────┘      └─────┬─────┘      └─────────┘
        │                  │
        └──────────────────┼──────────────────┐
                           │                  │
                    ┌──────▼──────┐     ┌─────▼─────┐
                    │   MySQL     │     │  RabbitMQ │
                    │  Database   │     │   Queue   │
                    └─────────────┘     └───────────┘
```

## 15.2 项目搭建

### 15.2.1 父工程配置

**pom.xml**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.ecommerce</groupId>
    <artifactId>ecommerce-order-system</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    
    <modules>
        <module>ecommerce-common</module>
        <module>ecommerce-user</module>
        <module>ecommerce-product</module>
        <module>ecommerce-order</module>
        <module>ecommerce-payment</module>
        <module>ecommerce-notification</module>
        <module>ecommerce-gateway</module>
    </modules>
    
    <properties>
        <java.version>17</java.version>
        <spring-boot.version>3.2.0</spring-boot.version>
        <spring-cloud.version>2023.0.0</spring-cloud.version>
        <mysql.version>8.0.33</mysql.version>
        <mybatis-plus.version>3.5.4</mybatis-plus.version>
        <druid.version>1.2.20</druid.version>
        <hutool.version>5.8.23</hutool.version>
        <knife4j.version>4.3.0</knife4j.version>
        <jwt.version>0.12.3</jwt.version>
    </properties>
    
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring-boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            
            <dependency>
                <groupId>com.baomidou</groupId>
                <artifactId>mybatis-plus-boot-starter</artifactId>
                <version>${mybatis-plus.version}</version>
            </dependency>
            
            <dependency>
                <groupId>mysql</groupId>
                <artifactId>mysql-connector-java</artifactId>
                <version>${mysql.version}</version>
            </dependency>
            
            <dependency>
                <groupId>com.alibaba</groupId>
                <artifactId>druid-spring-boot-starter</artifactId>
                <version>${druid.version}</version>
            </dependency>
            
            <dependency>
                <groupId>cn.hutool</groupId>
                <artifactId>hutool-all</artifactId>
                <version>${hutool.version}</version>
            </dependency>
            
            <dependency>
                <groupId>com.github.xiaoymin</groupId>
                <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
                <version>${knife4j.version}</version>
            </dependency>
            
            <dependency>
                <groupId>io.jsonwebtoken</groupId>
                <artifactId>jjwt-api</artifactId>
                <version>${jwt.version}</version>
            </dependency>
            
            <dependency>
                <groupId>io.jsonwebtoken</groupId>
                <artifactId>jjwt-impl</artifactId>
                <version>${jwt.version}</version>
            </dependency>
            
            <dependency>
                <groupId>io.jsonwebtoken</groupId>
                <artifactId>jjwt-jackson</artifactId>
                <version>${jwt.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
    
    <build>
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
        </plugins>
    </build>
</project>
```

### 15.2.2 公共模块配置

**ecommerce-common/pom.xml**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>com.ecommerce</groupId>
        <artifactId>ecommerce-order-system</artifactId>
        <version>1.0.0</version>
    </parent>
    
    <artifactId>ecommerce-common</artifactId>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-boot-starter</artifactId>
        </dependency>
        
        <dependency>
            <groupId>cn.hutool</groupId>
            <artifactId>hutool-all</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
        </dependency>
        
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-impl</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-jackson</artifactId>
            <scope>runtime</scope>
        </dependency>
    </dependencies>
</project>
```

**统一响应结果类**：

```java
package com.ecommerce.common.result;

import lombok.Data;
import java.io.Serializable;

@Data
public class Result<T> implements Serializable {
    
    private Integer code;
    private String message;
    private T data;
    private Long timestamp;
    
    public Result() {
        this.timestamp = System.currentTimeMillis();
    }
    
    public Result(Integer code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }
    
    public static <T> Result<T> success() {
        return new Result<>(200, "操作成功", null);
    }
    
    public static <T> Result<T> success(T data) {
        return new Result<>(200, "操作成功", data);
    }
    
    public static <T> Result<T> success(String message, T data) {
        return new Result<>(200, message, data);
    }
    
    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }
    
    public static <T> Result<T> error(Integer code, String message) {
        return new Result<>(code, message, null);
    }
}
```

**分页查询结果类**：

```java
package com.ecommerce.common.result;

import lombok.Data;
import java.util.List;

@Data
public class PageResult<T> {
    
    private Long total;
    private List<T> records;
    private Long current;
    private Long size;
    private Long pages;
    
    public PageResult(Long total, List<T> records, Long current, Long size) {
        this.total = total;
        this.records = records;
        this.current = current;
        this.size = size;
        this.pages = (total + size - 1) / size;
    }
    
    public static <T> PageResult<T> of(Long total, List<T> records, Long current, Long size) {
        return new PageResult<>(total, records, current, size);
    }
}
```

**JWT工具类**：

```java
package com.ecommerce.common.utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Map;

@Component
public class JwtUtils {
    
    @Value("${jwt.secret:ecommerce-secret-key-2024}")
    private String secret;
    
    @Value("${jwt.expiration:86400000}")
    private Long expiration;
    
    private SecretKey getSecretKey() {
        return Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }
    
    public String generateToken(Long userId, String username, Map<String, Object> claims) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);
        
        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claims(claims)
                .claim("username", username)
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(getSecretKey())
                .compact();
    }
    
    public Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(getSecretKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
    
    public Long getUserId(String token) {
        Claims claims = parseToken(token);
        return Long.parseLong(claims.getSubject());
    }
    
    public String getUsername(String token) {
        Claims claims = parseToken(token);
        return claims.get("username", String.class);
    }
    
    public Boolean isTokenExpired(String token) {
        Claims claims = parseToken(token);
        return claims.getExpiration().before(new Date());
    }
    
    public Boolean validateToken(String token) {
        try {
            return !isTokenExpired(token);
        } catch (Exception e) {
            return false;
        }
    }
}
```

**自定义异常**：

```java
package com.ecommerce.common.exception;

import lombok.Getter;

@Getter
public class BusinessException extends RuntimeException {
    
    private Integer code;
    
    public BusinessException(String message) {
        super(message);
        this.code = 500;
    }
    
    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }
    
    public BusinessException(String message, Throwable cause) {
        super(message, cause);
        this.code = 500;
    }
}
```

**全局异常处理器**：

```java
package com.ecommerce.common.exception;

import com.ecommerce.common.result.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(BusinessException.class)
    public Result<?> handleBusinessException(BusinessException e) {
        log.error("业务异常：{}", e.getMessage());
        return Result.error(e.getCode(), e.getMessage());
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<?> handleValidationException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));
        log.error("参数校验异常：{}", message);
        return Result.error(400, message);
    }
    
    @ExceptionHandler(BindException.class)
    public Result<?> handleBindException(BindException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));
        log.error("参数绑定异常：{}", message);
        return Result.error(400, message);
    }
    
    @ExceptionHandler(Exception.class)
    public Result<?> handleException(Exception e) {
        log.error("系统异常：", e);
        return Result.error("系统繁忙，请稍后重试");
    }
}
```

## 15.3 用户服务实现

### 15.3.1 用户服务配置

**ecommerce-user/pom.xml**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>com.ecommerce</groupId>
        <artifactId>ecommerce-order-system</artifactId>
        <version>1.0.0</version>
    </parent>
    
    <artifactId>ecommerce-user</artifactId>
    
    <dependencies>
        <dependency>
            <groupId>com.ecommerce</groupId>
            <artifactId>ecommerce-common</artifactId>
            <version>1.0.0</version>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>
        
        <dependency>
            <groupId>com.github.ben-manes.caffeine</groupId>
            <artifactId>caffeine</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
        </dependency>
        
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid-spring-boot-starter</artifactId>
        </dependency>
    </dependencies>
</project>
```

**application.yml**：

```yaml
server:
  port: 8001

spring:
  application:
    name: ecommerce-user
  
  datasource:
    type: com.alibaba.druid.pool.DruidDataSource
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/ecommerce_user?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: root
    password: root
    druid:
      initial-size: 5
      min-idle: 5
      max-active: 20
      max-wait: 60000
      test-while-idle: true
      test-on-borrow: false
      test-on-return: false
      validation-query: SELECT 1
      time-between-eviction-runs-millis: 60000
      min-evictable-idle-time-millis: 300000
  
  data:
    redis:
      host: localhost
      port: 6379
      password:
      database: 0
      lettuce:
        pool:
          max-active: 8
          max-wait: -1ms
          max-idle: 8
          min-idle: 0
      timeout: 3000ms
  
  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=1000,expireAfterWrite=10m

mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.ecommerce.user.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl
  global-config:
    db-config:
      id-type: auto
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0

jwt:
  secret: ecommerce-user-secret-key-2024
  expiration: 86400000

logging:
  level:
    com.ecommerce.user: debug
```

### 15.3.2 用户实体类

```java
package com.ecommerce.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("user")
public class User {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String username;
    
    private String password;
    
    private String email;
    
    private String phone;
    
    private String nickname;
    
    private String avatar;
    
    private Integer status;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    
    @TableLogic
    private Integer deleted;
}
```

```java
package com.ecommerce.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("user_role")
public class UserRole {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long userId;
    
    private Long roleId;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
```

```java
package com.ecommerce.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("role")
public class Role {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String roleName;
    
    private String roleCode;
    
    private String description;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
```

```java
package com.ecommerce.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("permission")
public class Permission {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String permissionName;
    
    private String permissionCode;
    
    private String url;
    
    private String method;
    
    private Long parentId;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
```

### 15.3.3 用户DTO类

```java
package com.ecommerce.user.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

@Data
public class UserRegisterDTO {
    
    @NotBlank(message = "用户名不能为空")
    @Pattern(regexp = "^[a-zA-Z0-9_]{4,20}$", message = "用户名必须是4-20位的字母、数字或下划线")
    private String username;
    
    @NotBlank(message = "密码不能为空")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d]{8,20}$", 
             message = "密码必须包含大小写字母和数字，长度8-20位")
    private String password;
    
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;
    
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;
}
```

```java
package com.ecommerce.user.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UserLoginDTO {
    
    @NotBlank(message = "用户名不能为空")
    private String username;
    
    @NotBlank(message = "密码不能为空")
    private String password;
}
```

```java
package com.ecommerce.user.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserDTO {
    
    private Long id;
    private String username;
    private String email;
    private String phone;
    private String nickname;
    private String avatar;
    private Integer status;
}
```

### 15.3.4 用户Mapper接口

```java
package com.ecommerce.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.ecommerce.user.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}
```

```java
package com.ecommerce.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.ecommerce.user.entity.Role;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface RoleMapper extends BaseMapper<Role> {
}
```

```java
package com.ecommerce.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.ecommerce.user.entity.Permission;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PermissionMapper extends BaseMapper<Permission> {
}
```

### 15.3.5 用户服务层

```java
package com.ecommerce.user.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.ecommerce.user.dto.UserDTO;
import com.ecommerce.user.dto.UserLoginDTO;
import com.ecommerce.user.dto.UserRegisterDTO;
import com.ecommerce.user.entity.User;

public interface UserService extends IService<User> {
    
    void register(UserRegisterDTO userRegisterDTO);
    
    String login(UserLoginDTO userLoginDTO);
    
    UserDTO getUserInfo(Long userId);
    
    void updateUserInfo(Long userId, UserDTO userDTO);
    
    void changePassword(Long userId, String oldPassword, String newPassword);
}
```

```java
package com.ecommerce.user.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.crypto.digest.BCrypt;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.ecommerce.common.exception.BusinessException;
import com.ecommerce.common.utils.JwtUtils;
import com.ecommerce.user.dto.UserDTO;
import com.ecommerce.user.dto.UserLoginDTO;
import com.ecommerce.user.dto.UserRegisterDTO;
import com.ecommerce.user.entity.User;
import com.ecommerce.user.mapper.UserMapper;
import com.ecommerce.user.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
    
    private final JwtUtils jwtUtils;
    private final RedisTemplate<String, Object> redisTemplate;
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void register(UserRegisterDTO userRegisterDTO) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, userRegisterDTO.getUsername())
                .or()
                .eq(User::getEmail, userRegisterDTO.getEmail());
        
        User existUser = this.getOne(wrapper);
        if (existUser != null) {
            if (existUser.getUsername().equals(userRegisterDTO.getUsername())) {
                throw new BusinessException("用户名已存在");
            }
            if (existUser.getEmail().equals(userRegisterDTO.getEmail())) {
                throw new BusinessException("邮箱已被注册");
            }
        }
        
        User user = new User();
        user.setUsername(userRegisterDTO.getUsername());
        user.setPassword(BCrypt.hashpw(userRegisterDTO.getPassword()));
        user.setEmail(userRegisterDTO.getEmail());
        user.setPhone(userRegisterDTO.getPhone());
        user.setNickname(userRegisterDTO.getUsername());
        user.setStatus(1);
        
        this.save(user);
    }
    
    @Override
    public String login(UserLoginDTO userLoginDTO) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, userLoginDTO.getUsername());
        
        User user = this.getOne(wrapper);
        if (user == null) {
            throw new BusinessException("用户名或密码错误");
        }
        
        if (!BCrypt.checkpw(userLoginDTO.getPassword(), user.getPassword())) {
            throw new BusinessException("用户名或密码错误");
        }
        
        if (user.getStatus() != 1) {
            throw new BusinessException("账号已被禁用");
        }
        
        Map<String, Object> claims = new HashMap<>();
        claims.put("email", user.getEmail());
        claims.put("phone", user.getPhone());
        
        String token = jwtUtils.generateToken(user.getId(), user.getUsername(), claims);
        
        String tokenKey = "user:token:" + user.getId();
        redisTemplate.opsForValue().set(tokenKey, token, 24, TimeUnit.HOURS);
        
        return token;
    }
    
    @Override
    @Cacheable(value = "user", key = "#userId")
    public UserDTO getUserInfo(Long userId) {
        User user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        UserDTO userDTO = new UserDTO();
        BeanUtil.copyProperties(user, userDTO);
        return userDTO;
    }
    
    @Override
    @CacheEvict(value = "user", key = "#userId")
    @Transactional(rollbackFor = Exception.class)
    public void updateUserInfo(Long userId, UserDTO userDTO) {
        User user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        if (userDTO.getNickname() != null) {
            user.setNickname(userDTO.getNickname());
        }
        if (userDTO.getAvatar() != null) {
            user.setAvatar(userDTO.getAvatar());
        }
        if (userDTO.getPhone() != null) {
            user.setPhone(userDTO.getPhone());
        }
        
        this.updateById(user);
    }
    
    @Override
    @CacheEvict(value = "user", key = "#userId")
    @Transactional(rollbackFor = Exception.class)
    public void changePassword(Long userId, String oldPassword, String newPassword) {
        User user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        if (!BCrypt.checkpw(oldPassword, user.getPassword())) {
            throw new BusinessException("原密码错误");
        }
        
        user.setPassword(BCrypt.hashpw(newPassword));
        this.updateById(user);
        
        String tokenKey = "user:token:" + userId;
        redisTemplate.delete(tokenKey);
    }
}
```

### 15.3.6 用户控制器

```java
package com.ecommerce.user.controller;

import com.ecommerce.common.result.Result;
import com.ecommerce.user.dto.UserDTO;
import com.ecommerce.user.dto.UserLoginDTO;
import com.ecommerce.user.dto.UserRegisterDTO;
import com.ecommerce.user.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "用户管理")
@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {
    
    private final UserService userService;
    
    @Operation(summary = "用户注册")
    @PostMapping("/register")
    public Result<Void> register(@Valid @RequestBody UserRegisterDTO userRegisterDTO) {
        userService.register(userRegisterDTO);
        return Result.success();
    }
    
    @Operation(summary = "用户登录")
    @PostMapping("/login")
    public Result<String> login(@Valid @RequestBody UserLoginDTO userLoginDTO) {
        String token = userService.login(userLoginDTO);
        return Result.success(token);
    }
    
    @Operation(summary = "获取用户信息")
    @GetMapping("/info/{userId}")
    public Result<UserDTO> getUserInfo(@PathVariable Long userId) {
        UserDTO userDTO = userService.getUserInfo(userId);
        return Result.success(userDTO);
    }
    
    @Operation(summary = "更新用户信息")
    @PutMapping("/info/{userId}")
    public Result<Void> updateUserInfo(@PathVariable Long userId, @RequestBody UserDTO userDTO) {
        userService.updateUserInfo(userId, userDTO);
        return Result.success();
    }
    
    @Operation(summary = "修改密码")
    @PutMapping("/password/{userId}")
    public Result<Void> changePassword(
            @PathVariable Long userId,
            @RequestParam String oldPassword,
            @RequestParam String newPassword) {
        userService.changePassword(userId, oldPassword, newPassword);
        return Result.success();
    }
}
```

## 15.4 商品服务实现

### 15.4.1 商品服务配置

**ecommerce-product/pom.xml**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>com.ecommerce</groupId>
        <artifactId>ecommerce-order-system</artifactId>
        <version>1.0.0</version>
    </parent>
    
    <artifactId>ecommerce-product</artifactId>
    
    <dependencies>
        <dependency>
            <groupId>com.ecommerce</groupId>
            <artifactId>ecommerce-common</artifactId>
            <version>1.0.0</version>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>
        
        <dependency>
            <groupId>com.github.ben-manes.caffeine</groupId>
            <artifactId>caffeine</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-elasticsearch</artifactId>
        </dependency>
        
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
        </dependency>
        
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid-spring-boot-starter</artifactId>
        </dependency>
    </dependencies>
</project>
```

### 15.4.2 商品实体类

```java
package com.ecommerce.product.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("product")
public class Product {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String productCode;
    
    private String productName;
    
    private String productImage;
    
    private BigDecimal price;
    
    private Integer stock;
    
    private Long categoryId;
    
    private String description;
    
    private Integer status;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    
    @TableLogic
    private Integer deleted;
}
```

```java
package com.ecommerce.product.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("category")
public class Category {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String categoryName;
    
    private Long parentId;
    
    private Integer sort;
    
    private Integer status;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
```

### 15.4.3 商品DTO类

```java
package com.ecommerce.product.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class ProductCreateDTO {
    
    @NotBlank(message = "商品编码不能为空")
    private String productCode;
    
    @NotBlank(message = "商品名称不能为空")
    private String productName;
    
    @NotNull(message = "商品价格不能为空")
    @Positive(message = "商品价格必须大于0")
    private BigDecimal price;
    
    @NotNull(message = "库存不能为空")
    private Integer stock;
    
    @NotNull(message = "分类ID不能为空")
    private Long categoryId;
    
    private String productImage;
    
    private String description;
}
```

```java
package com.ecommerce.product.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ProductDTO {
    
    private Long id;
    private String productCode;
    private String productName;
    private String productImage;
    private BigDecimal price;
    private Integer stock;
    private Long categoryId;
    private String categoryName;
    private String description;
    private Integer status;
}
```

```java
package com.ecommerce.product.dto;

import lombok.Data;

@Data
public class ProductQueryDTO {
    
    private String productName;
    
    private Long categoryId;
    
    private Integer status;
    
    private Integer current = 1;
    
    private Integer size = 10;
}
```

### 15.4.4 商品服务层

```java
package com.ecommerce.product.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.ecommerce.product.dto.ProductCreateDTO;
import com.ecommerce.product.dto.ProductDTO;
import com.ecommerce.product.dto.ProductQueryDTO;
import com.ecommerce.product.entity.Product;

public interface ProductService extends IService<Product> {
    
    void createProduct(ProductCreateDTO productCreateDTO);
    
    void updateProduct(Long productId, ProductCreateDTO productCreateDTO);
    
    void deleteProduct(Long productId);
    
    ProductDTO getProductById(Long productId);
    
    Page<ProductDTO> getProductPage(ProductQueryDTO queryDTO);
    
    void decreaseStock(Long productId, Integer quantity);
    
    void increaseStock(Long productId, Integer quantity);
}
```

```java
package com.ecommerce.product.service.impl;

import cn.hutool.core.bean.BeanUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.ecommerce.common.exception.BusinessException;
import com.ecommerce.product.dto.ProductCreateDTO;
import com.ecommerce.product.dto.ProductDTO;
import com.ecommerce.product.dto.ProductQueryDTO;
import com.ecommerce.product.entity.Category;
import com.ecommerce.product.entity.Product;
import com.ecommerce.product.mapper.CategoryMapper;
import com.ecommerce.product.mapper.ProductMapper;
import com.ecommerce.product.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProductServiceImpl extends ServiceImpl<ProductMapper, Product> implements ProductService {
    
    private final CategoryMapper categoryMapper;
    private final RedisTemplate<String, Object> redisTemplate;
    
    @Override
    @CacheEvict(value = "product", allEntries = true)
    @Transactional(rollbackFor = Exception.class)
    public void createProduct(ProductCreateDTO productCreateDTO) {
        LambdaQueryWrapper<Product> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Product::getProductCode, productCreateDTO.getProductCode());
        
        Product existProduct = this.getOne(wrapper);
        if (existProduct != null) {
            throw new BusinessException("商品编码已存在");
        }
        
        Product product = new Product();
        BeanUtil.copyProperties(productCreateDTO, product);
        product.setStatus(1);
        
        this.save(product);
    }
    
    @Override
    @CacheEvict(value = "product", allEntries = true)
    @Transactional(rollbackFor = Exception.class)
    public void updateProduct(Long productId, ProductCreateDTO productCreateDTO) {
        Product product = this.getById(productId);
        if (product == null) {
            throw new BusinessException("商品不存在");
        }
        
        BeanUtil.copyProperties(productCreateDTO, product);
        this.updateById(product);
    }
    
    @Override
    @CacheEvict(value = "product", allEntries = true)
    @Transactional(rollbackFor = Exception.class)
    public void deleteProduct(Long productId) {
        Product product = this.getById(productId);
        if (product == null) {
            throw new BusinessException("商品不存在");
        }
        
        this.removeById(productId);
    }
    
    @Override
    @Cacheable(value = "product", key = "#productId")
    public ProductDTO getProductById(Long productId) {
        Product product = this.getById(productId);
        if (product == null) {
            throw new BusinessException("商品不存在");
        }
        
        Category category = categoryMapper.selectById(product.getCategoryId());
        
        ProductDTO productDTO = new ProductDTO();
        BeanUtil.copyProperties(product, productDTO);
        if (category != null) {
            productDTO.setCategoryName(category.getCategoryName());
        }
        
        return productDTO;
    }
    
    @Override
    public Page<ProductDTO> getProductPage(ProductQueryDTO queryDTO) {
        LambdaQueryWrapper<Product> wrapper = new LambdaQueryWrapper<>();
        
        if (queryDTO.getProductName() != null && !queryDTO.getProductName().isEmpty()) {
            wrapper.like(Product::getProductName, queryDTO.getProductName());
        }
        if (queryDTO.getCategoryId() != null) {
            wrapper.eq(Product::getCategoryId, queryDTO.getCategoryId());
        }
        if (queryDTO.getStatus() != null) {
            wrapper.eq(Product::getStatus, queryDTO.getStatus());
        }
        
        wrapper.orderByDesc(Product::getCreateTime);
        
        Page<Product> page = this.page(new Page<>(queryDTO.getCurrent(), queryDTO.getSize()), wrapper);
        
        List<ProductDTO> productDTOList = page.getRecords().stream()
                .map(product -> {
                    Category category = categoryMapper.selectById(product.getCategoryId());
                    ProductDTO productDTO = new ProductDTO();
                    BeanUtil.copyProperties(product, productDTO);
                    if (category != null) {
                        productDTO.setCategoryName(category.getCategoryName());
                    }
                    return productDTO;
                })
                .collect(Collectors.toList());
        
        Page<ProductDTO> resultPage = new Page<>(page.getCurrent(), page.getSize(), page.getTotal());
        resultPage.setRecords(productDTOList);
        
        return resultPage;
    }
    
    @Override
    @CacheEvict(value = "product", key = "#productId")
    @Transactional(rollbackFor = Exception.class)
    public void decreaseStock(Long productId, Integer quantity) {
        Product product = this.getById(productId);
        if (product == null) {
            throw new BusinessException("商品不存在");
        }
        
        if (product.getStock() < quantity) {
            throw new BusinessException("库存不足");
        }
        
        String lockKey = "product:stock:lock:" + productId;
        Boolean locked = redisTemplate.opsForValue().setIfAbsent(lockKey, "1", 10, TimeUnit.SECONDS);
        
        if (Boolean.TRUE.equals(locked)) {
            try {
                Product currentProduct = this.getById(productId);
                if (currentProduct.getStock() < quantity) {
                    throw new BusinessException("库存不足");
                }
                
                currentProduct.setStock(currentProduct.getStock() - quantity);
                this.updateById(currentProduct);
            } finally {
                redisTemplate.delete(lockKey);
            }
        } else {
            throw new BusinessException("系统繁忙，请稍后重试");
        }
    }
    
    @Override
    @CacheEvict(value = "product", key = "#productId")
    @Transactional(rollbackFor = Exception.class)
    public void increaseStock(Long productId, Integer quantity) {
        Product product = this.getById(productId);
        if (product == null) {
            throw new BusinessException("商品不存在");
        }
        
        product.setStock(product.getStock() + quantity);
        this.updateById(product);
    }
}
```

### 15.4.5 商品控制器

```java
package com.ecommerce.product.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ecommerce.common.result.Result;
import com.ecommerce.product.dto.ProductCreateDTO;
import com.ecommerce.product.dto.ProductDTO;
import com.ecommerce.product.dto.ProductQueryDTO;
import com.ecommerce.product.service.ProductService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "商品管理")
@RestController
@RequestMapping("/api/product")
@RequiredArgsConstructor
public class ProductController {
    
    private final ProductService productService;
    
    @Operation(summary = "创建商品")
    @PostMapping
    public Result<Void> createProduct(@Valid @RequestBody ProductCreateDTO productCreateDTO) {
        productService.createProduct(productCreateDTO);
        return Result.success();
    }
    
    @Operation(summary = "更新商品")
    @PutMapping("/{productId}")
    public Result<Void> updateProduct(
            @PathVariable Long productId,
            @Valid @RequestBody ProductCreateDTO productCreateDTO) {
        productService.updateProduct(productId, productCreateDTO);
        return Result.success();
    }
    
    @Operation(summary = "删除商品")
    @DeleteMapping("/{productId}")
    public Result<Void> deleteProduct(@PathVariable Long productId) {
        productService.deleteProduct(productId);
        return Result.success();
    }
    
    @Operation(summary = "获取商品详情")
    @GetMapping("/{productId}")
    public Result<ProductDTO> getProductById(@PathVariable Long productId) {
        ProductDTO productDTO = productService.getProductById(productId);
        return Result.success(productDTO);
    }
    
    @Operation(summary = "分页查询商品")
    @PostMapping("/page")
    public Result<Page<ProductDTO>> getProductPage(@RequestBody ProductQueryDTO queryDTO) {
        Page<ProductDTO> page = productService.getProductPage(queryDTO);
        return Result.success(page);
    }
}
```

## 15.5 订单服务实现

### 15.5.1 订单服务配置

**ecommerce-order/pom.xml**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>com.ecommerce</groupId>
        <artifactId>ecommerce-order-system</artifactId>
        <version>1.0.0</version>
    </parent>
    
    <artifactId>ecommerce-order</artifactId>
    
    <dependencies>
        <dependency>
            <groupId>com.ecommerce</groupId>
            <artifactId>ecommerce-common</artifactId>
            <version>1.0.0</version>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-amqp</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-elasticsearch</artifactId>
        </dependency>
        
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
        </dependency>
        
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid-spring-boot-starter</artifactId>
        </dependency>
    </dependencies>
</project>
```

**application.yml**：

```yaml
server:
  port: 8003

spring:
  application:
    name: ecommerce-order
  
  datasource:
    type: com.alibaba.druid.pool.DruidDataSource
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/ecommerce_order?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: root
    password: root
    druid:
      initial-size: 5
      min-idle: 5
      max-active: 20
  
  data:
    redis:
      host: localhost
      port: 6379
      database: 1
  
  rabbitmq:
    host: localhost
    port: 5672
    username: guest
    password: guest
    virtual-host: /
    listener:
      simple:
        acknowledge-mode: manual
        prefetch: 1
        concurrency: 5
        max-concurrency: 10

mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.ecommerce.order.entity

logging:
  level:
    com.ecommerce.order: debug
```

### 15.5.2 订单实体类

```java
package com.ecommerce.order.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("order_info")
public class Order {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String orderNo;
    
    private Long userId;
    
    private BigDecimal totalAmount;
    
    private Integer status;
    
    private String receiverName;
    
    private String receiverPhone;
    
    private String receiverAddress;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    
    @TableLogic
    private Integer deleted;
}
```

```java
package com.ecommerce.order.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("order_item")
public class OrderItem {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long orderId;
    
    private Long productId;
    
    private String productName;
    
    private String productImage;
    
    private BigDecimal price;
    
    private Integer quantity;
    
    private BigDecimal totalPrice;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
```

### 15.5.3 订单DTO类

```java
package com.ecommerce.order.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;
import java.util.List;

@Data
public class OrderCreateDTO {
    
    @NotEmpty(message = "订单项不能为空")
    private List<OrderItemDTO> orderItems;
    
    @NotBlank(message = "收货人姓名不能为空")
    private String receiverName;
    
    @NotBlank(message = "收货人电话不能为空")
    private String receiverPhone;
    
    @NotBlank(message = "收货地址不能为空")
    private String receiverAddress;
    
    @Data
    public static class OrderItemDTO {
        
        @NotNull(message = "商品ID不能为空")
        private Long productId;
        
        @NotNull(message = "商品数量不能为空")
        private Integer quantity;
    }
}
```

```java
package com.ecommerce.order.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderDTO {
    
    private Long id;
    private String orderNo;
    private Long userId;
    private BigDecimal totalAmount;
    private Integer status;
    private String receiverName;
    private String receiverPhone;
    private String receiverAddress;
    private List<OrderItemDTO> orderItems;
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OrderItemDTO {
        private Long id;
        private Long productId;
        private String productName;
        private String productImage;
        private BigDecimal price;
        private Integer quantity;
        private BigDecimal totalPrice;
    }
}
```

### 15.5.4 订单服务层

```java
package com.ecommerce.order.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.ecommerce.order.dto.OrderCreateDTO;
import com.ecommerce.order.dto.OrderDTO;
import com.ecommerce.order.entity.Order;

public interface OrderService extends IService<Order> {
    
    String createOrder(Long userId, OrderCreateDTO orderCreateDTO);
    
    OrderDTO getOrderByOrderNo(String orderNo);
    
    Page<OrderDTO> getOrderPage(Long userId, Integer current, Integer size);
    
    void cancelOrder(String orderNo);
    
    void payOrder(String orderNo);
}
```

```java
package com.ecommerce.order.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.IdUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.ecommerce.common.exception.BusinessException;
import com.ecommerce.order.dto.OrderCreateDTO;
import com.ecommerce.order.dto.OrderDTO;
import com.ecommerce.order.entity.Order;
import com.ecommerce.order.entity.OrderItem;
import com.ecommerce.order.feign.ProductFeignClient;
import com.ecommerce.order.mapper.OrderItemMapper;
import com.ecommerce.order.mapper.OrderMapper;
import com.ecommerce.order.mq.OrderMessageProducer;
import com.ecommerce.order.service.OrderService;
import lombok.RequiredArgsConstructor;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OrderServiceImpl extends ServiceImpl<OrderMapper, Order> implements OrderService {
    
    private final OrderItemMapper orderItemMapper;
    private final ProductFeignClient productFeignClient;
    private final OrderMessageProducer orderMessageProducer;
    private final RedisTemplate<String, Object> redisTemplate;
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public String createOrder(Long userId, OrderCreateDTO orderCreateDTO) {
        String orderNo = IdUtil.getSnowflakeNextIdStr();
        
        BigDecimal totalAmount = BigDecimal.ZERO;
        
        for (OrderCreateDTO.OrderItemDTO itemDTO : orderCreateDTO.getOrderItems()) {
            var productResponse = productFeignClient.getProductById(itemDTO.getProductId());
            if (productResponse.getCode() != 200) {
                throw new BusinessException("商品不存在");
            }
            
            OrderDTO.ProductDTO product = productResponse.getData();
            BigDecimal itemTotal = product.getPrice().multiply(new BigDecimal(itemDTO.getQuantity()));
            totalAmount = totalAmount.add(itemTotal);
            
            productFeignClient.decreaseStock(itemDTO.getProductId(), itemDTO.getQuantity());
        }
        
        Order order = new Order();
        order.setOrderNo(orderNo);
        order.setUserId(userId);
        order.setTotalAmount(totalAmount);
        order.setStatus(0);
        order.setReceiverName(orderCreateDTO.getReceiverName());
        order.setReceiverPhone(orderCreateDTO.getReceiverPhone());
        order.setReceiverAddress(orderCreateDTO.getReceiverAddress());
        
        this.save(order);
        
        for (OrderCreateDTO.OrderItemDTO itemDTO : orderCreateDTO.getOrderItems()) {
            var productResponse = productFeignClient.getProductById(itemDTO.getProductId());
            OrderDTO.ProductDTO product = productResponse.getData();
            
            OrderItem orderItem = new OrderItem();
            orderItem.setOrderId(order.getId());
            orderItem.setProductId(itemDTO.getProductId());
            orderItem.setProductName(product.getProductName());
            orderItem.setProductImage(product.getProductImage());
            orderItem.setPrice(product.getPrice());
            orderItem.setQuantity(itemDTO.getQuantity());
            orderItem.setTotalPrice(product.getPrice().multiply(new BigDecimal(itemDTO.getQuantity())));
            
            orderItemMapper.insert(orderItem);
        }
        
        String orderKey = "order:info:" + orderNo;
        redisTemplate.opsForValue().set(orderKey, order, 30, TimeUnit.MINUTES);
        
        orderMessageProducer.sendOrderCreatedMessage(orderNo, userId, totalAmount);
        
        return orderNo;
    }
    
    @Override
    public OrderDTO getOrderByOrderNo(String orderNo) {
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Order::getOrderNo, orderNo);
        
        Order order = this.getOne(wrapper);
        if (order == null) {
            throw new BusinessException("订单不存在");
        }
        
        LambdaQueryWrapper<OrderItem> itemWrapper = new LambdaQueryWrapper<>();
        itemWrapper.eq(OrderItem::getOrderId, order.getId());
        
        List<OrderItem> orderItems = orderItemMapper.selectList(itemWrapper);
        
        List<OrderDTO.OrderItemDTO> orderItemDTOList = orderItems.stream()
                .map(item -> {
                    OrderDTO.OrderItemDTO itemDTO = new OrderDTO.OrderItemDTO();
                    BeanUtil.copyProperties(item, itemDTO);
                    return itemDTO;
                })
                .collect(Collectors.toList());
        
        OrderDTO orderDTO = new OrderDTO();
        BeanUtil.copyProperties(order, orderDTO);
        orderDTO.setOrderItems(orderItemDTOList);
        
        return orderDTO;
    }
    
    @Override
    public Page<OrderDTO> getOrderPage(Long userId, Integer current, Integer size) {
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Order::getUserId, userId);
        wrapper.orderByDesc(Order::getCreateTime);
        
        Page<Order> page = this.page(new Page<>(current, size), wrapper);
        
        List<OrderDTO> orderDTOList = page.getRecords().stream()
                .map(order -> {
                    OrderDTO orderDTO = new OrderDTO();
                    BeanUtil.copyProperties(order, orderDTO);
                    return orderDTO;
                })
                .collect(Collectors.toList());
        
        Page<OrderDTO> resultPage = new Page<>(page.getCurrent(), page.getSize(), page.getTotal());
        resultPage.setRecords(orderDTOList);
        
        return resultPage;
    }
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void cancelOrder(String orderNo) {
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Order::getOrderNo, orderNo);
        
        Order order = this.getOne(wrapper);
        if (order == null) {
            throw new BusinessException("订单不存在");
        }
        
        if (order.getStatus() != 0) {
            throw new BusinessException("订单状态不允许取消");
        }
        
        order.setStatus(4);
        this.updateById(order);
        
        LambdaQueryWrapper<OrderItem> itemWrapper = new LambdaQueryWrapper<>();
        itemWrapper.eq(OrderItem::getOrderId, order.getId());
        
        List<OrderItem> orderItems = orderItemMapper.selectList(itemWrapper);
        
        for (OrderItem orderItem : orderItems) {
            productFeignClient.increaseStock(orderItem.getProductId(), orderItem.getQuantity());
        }
        
        orderMessageProducer.sendOrderCancelledMessage(orderNo, order.getUserId());
    }
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void payOrder(String orderNo) {
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Order::getOrderNo, orderNo);
        
        Order order = this.getOne(wrapper);
        if (order == null) {
            throw new BusinessException("订单不存在");
        }
        
        if (order.getStatus() != 0) {
            throw new BusinessException("订单状态不允许支付");
        }
        
        order.setStatus(1);
        this.updateById(order);
        
        orderMessageProducer.sendOrderPaidMessage(orderNo, order.getUserId(), order.getTotalAmount());
    }
}
```

### 15.5.5 订单消息生产者

```java
package com.ecommerce.order.mq;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class OrderMessageProducer {
    
    private final RabbitTemplate rabbitTemplate;
    private final ObjectMapper objectMapper;
    
    public void sendOrderCreatedMessage(String orderNo, Long userId, BigDecimal totalAmount) {
        Map<String, Object> message = new HashMap<>();
        message.put("orderNo", orderNo);
        message.put("userId", userId);
        message.put("totalAmount", totalAmount);
        message.put("eventType", "ORDER_CREATED");
        
        try {
            rabbitTemplate.convertAndSend("order.exchange", "order.created", objectMapper.writeValueAsString(message));
            log.info("订单创建消息发送成功：{}", orderNo);
        } catch (Exception e) {
            log.error("订单创建消息发送失败：{}", orderNo, e);
        }
    }
    
    public void sendOrderPaidMessage(String orderNo, Long userId, BigDecimal totalAmount) {
        Map<String, Object> message = new HashMap<>();
        message.put("orderNo", orderNo);
        message.put("userId", userId);
        message.put("totalAmount", totalAmount);
        message.put("eventType", "ORDER_PAID");
        
        try {
            rabbitTemplate.convertAndSend("order.exchange", "order.paid", objectMapper.writeValueAsString(message));
            log.info("订单支付消息发送成功：{}", orderNo);
        } catch (Exception e) {
            log.error("订单支付消息发送失败：{}", orderNo, e);
        }
    }
    
    public void sendOrderCancelledMessage(String orderNo, Long userId) {
        Map<String, Object> message = new HashMap<>();
        message.put("orderNo", orderNo);
        message.put("userId", userId);
        message.put("eventType", "ORDER_CANCELLED");
        
        try {
            rabbitTemplate.convertAndSend("order.exchange", "order.cancelled", objectMapper.writeValueAsString(message));
            log.info("订单取消消息发送成功：{}", orderNo);
        } catch (Exception e) {
            log.error("订单取消消息发送失败：{}", orderNo, e);
        }
    }
}
```

### 15.5.6 订单控制器

```java
package com.ecommerce.order.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ecommerce.common.result.Result;
import com.ecommerce.order.dto.OrderCreateDTO;
import com.ecommerce.order.dto.OrderDTO;
import com.ecommerce.order.service.OrderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "订单管理")
@RestController
@RequestMapping("/api/order")
@RequiredArgsConstructor
public class OrderController {
    
    private final OrderService orderService;
    
    @Operation(summary = "创建订单")
    @PostMapping
    public Result<String> createOrder(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody OrderCreateDTO orderCreateDTO) {
        String orderNo = orderService.createOrder(userId, orderCreateDTO);
        return Result.success(orderNo);
    }
    
    @Operation(summary = "获取订单详情")
    @GetMapping("/{orderNo}")
    public Result<OrderDTO> getOrderByOrderNo(@PathVariable String orderNo) {
        OrderDTO orderDTO = orderService.getOrderByOrderNo(orderNo);
        return Result.success(orderDTO);
    }
    
    @Operation(summary = "分页查询订单")
    @GetMapping("/page")
    public Result<Page<OrderDTO>> getOrderPage(
            @RequestHeader("X-User-Id") Long userId,
            @RequestParam(defaultValue = "1") Integer current,
            @RequestParam(defaultValue = "10") Integer size) {
        Page<OrderDTO> page = orderService.getOrderPage(userId, current, size);
        return Result.success(page);
    }
    
    @Operation(summary = "取消订单")
    @PutMapping("/{orderNo}/cancel")
    public Result<Void> cancelOrder(@PathVariable String orderNo) {
        orderService.cancelOrder(orderNo);
        return Result.success();
    }
    
    @Operation(summary = "支付订单")
    @PutMapping("/{orderNo}/pay")
    public Result<Void> payOrder(@PathVariable String orderNo) {
        orderService.payOrder(orderNo);
        return Result.success();
    }
}
```

## 15.6 Docker部署

### 15.6.1 Docker Compose配置

**docker-compose.yml**：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: ecommerce-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ecommerce
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init-sql:/docker-entrypoint-initdb.d
    networks:
      - ecommerce-network

  redis:
    image: redis:7-alpine
    container_name: ecommerce-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - ecommerce-network

  rabbitmq:
    image: rabbitmq:3.12-management
    container_name: ecommerce-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    networks:
      - ecommerce-network

  elasticsearch:
    image: elasticsearch:8.11.0
    container_name: ecommerce-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - ecommerce-network

  prometheus:
    image: prom/prometheus:latest
    container_name: ecommerce-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    networks:
      - ecommerce-network

  grafana:
    image: grafana/grafana:latest
    container_name: ecommerce-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - ecommerce-network

volumes:
  mysql-data:
  redis-data:
  rabbitmq-data:
  elasticsearch-data:
  prometheus-data:
  grafana-data:

networks:
  ecommerce-network:
    driver: bridge
```

**prometheus.yml**：

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ecommerce-user'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['host.docker.internal:8001']

  - job_name: 'ecommerce-product'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['host.docker.internal:8002']

  - job_name: 'ecommerce-order'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['host.docker.internal:8003']
```

### 15.6.2 应用Dockerfile

**ecommerce-user/Dockerfile**：

```dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/ecommerce-user-1.0.0.jar app.jar

EXPOSE 8001

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**ecommerce-product/Dockerfile**：

```dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/ecommerce-product-1.0.0.jar app.jar

EXPOSE 8002

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**ecommerce-order/Dockerfile**：

```dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/ecommerce-order-1.0.0.jar app.jar

EXPOSE 8003

ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 15.6.3 部署脚本

**deploy.sh**：

```bash
#!/bin/bash

echo "开始构建项目..."

mvn clean package -DskipTests

echo "构建Docker镜像..."

docker build -t ecommerce-user:1.0.0 ./ecommerce-user
docker build -t ecommerce-product:1.0.0 ./ecommerce-product
docker build -t ecommerce-order:1.0.0 ./ecommerce-order

echo "启动Docker容器..."

docker-compose up -d

echo "等待服务启动..."

sleep 30

echo "部署完成！"
echo "用户服务: http://localhost:8001"
echo "商品服务: http://localhost:8002"
echo "订单服务: http://localhost:8003"
echo "RabbitMQ管理界面: http://localhost:15672"
echo "Grafana: http://localhost:3000"
```

## 15.7 项目总结

### 15.7.1 技术亮点

1. **微服务架构**：采用Spring Boot微服务架构，各服务独立部署、独立扩展
2. **安全认证**：基于JWT的无状态认证，结合Spring Security实现权限控制
3. **多级缓存**：Caffeine本地缓存 + Redis分布式缓存，提升系统性能
4. **消息队列**：使用RabbitMQ实现异步解耦，提高系统吞吐量
5. **分布式锁**：基于Redis实现分布式锁，保证数据一致性
6. **监控告警**：集成Prometheus + Grafana实现系统监控
7. **容器化部署**：使用Docker + Docker Compose实现一键部署

### 15.7.2 性能优化

1. **数据库优化**：
   - 使用Druid连接池
   - 合理设置索引
   - 使用MyBatis-Plus优化SQL

2. **缓存优化**：
   - 热点数据缓存
   - 多级缓存策略
   - 缓存预热

3. **异步处理**：
   - 消息队列异步处理
   - 线程池异步执行

4. **JVM优化**：
   - 堆内存设置
   - GC参数调优

### 15.7.3 扩展方向

1. **服务治理**：引入Nacos实现服务注册与发现
2. **API网关**：使用Spring Cloud Gateway统一入口
3. **配置中心**：使用Nacos Config实现配置管理
4. **链路追踪**：集成Skywalking实现全链路追踪
5. **限流降级**：使用Sentinel实现流量控制
6. **搜索优化**：使用Elasticsearch实现商品搜索
7. **分布式事务**：使用Seata实现分布式事务

### 15.7.4 最佳实践

1. **代码规范**：
   - 遵循阿里巴巴Java开发手册
   - 统一异常处理
   - 统一响应格式

2. **安全实践**：
   - 敏感数据加密
   - SQL注入防护
   - XSS攻击防护

3. **测试实践**：
   - 单元测试覆盖核心业务
   - 集成测试验证接口
   - 压力测试评估性能

4. **运维实践**：
   - 日志规范输出
   - 监控指标采集
   - 告警规则配置

## 15.8 小结

本章通过一个完整的电商订单管理系统实战项目，综合运用了前面章节所学的Spring Boot技术栈。项目涵盖了用户管理、商品管理、订单处理、消息通知等核心功能，展示了如何在实际项目中应用Spring Boot的各种特性。

通过本章的学习，读者应该能够：
1. 理解微服务架构的设计思想
2. 掌握Spring Boot项目的搭建流程
3. 熟练使用Spring Boot集成各种中间件
4. 掌握Docker容器化部署的方法
5. 了解系统监控和性能优化的技巧

在实际开发中，读者可以根据项目需求选择合适的技术方案，不断优化和改进系统架构，构建高质量的企业级应用。
