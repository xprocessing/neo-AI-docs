# MongoDB 全面介绍（附SpringBoot整合示例）
MongoDB 是由 MongoDB Inc. 开发的**开源、跨平台、文档型 NoSQL 数据库**，诞生于2007年，主打「灵活、高性能、易扩展」，以类 JSON 的 BSON 格式存储数据，摆脱了关系型数据库的固定表结构约束，是目前最主流的 NoSQL 数据库之一。

## 一、核心定位与设计理念
MongoDB 的核心目标是解决**关系型数据库（如MySQL）在大数据量、高并发、灵活扩展场景下的痛点**：
- 放弃「表-行-列」的固定结构，采用「文档」存储，适配快速迭代的业务（如互联网产品）；
- 原生支持分布式扩展（分片、副本集），适配海量数据存储；
- 优化读写性能，主打高吞吐量的读写操作（如日志、用户行为数据）。

## 二、核心概念（对比关系型数据库）
MongoDB 的核心概念与关系型数据库有对应关系，但设计逻辑完全不同，对比理解更易上手：

| MongoDB 概念       | 关系型数据库（MySQL） | 说明                                                                 |
|--------------------|-----------------------|----------------------------------------------------------------------|
| Database（数据库） | Database（数据库）    | 逻辑隔离的数据集，一个MongoDB实例可创建多个Database                  |
| Collection（集合） | Table（表）           | 存储文档的容器，无固定结构（无需定义字段、类型），相当于「无Schema的表」 |
| Document（文档）   | Row（行）             | 最小数据单元，BSON格式（二进制JSON），字段可嵌套、数组，如`{_id: 1, name: "张三", age: 20}` |
| Field（字段）      | Column（列）          | 文档中的键值对，字段类型灵活（字符串、数字、数组、嵌套文档等）|
| `_id` 字段         | 主键（Primary Key）   | 每个文档默认的唯一标识，MongoDB自动生成（ObjectId类型），也可自定义   |
| Index（索引）      | Index（索引）         | 支持单字段、复合、地理空间、文本索引等，优化查询性能                 |
| 无Schema           | 表结构（Schema）      | 同一集合的文档可拥有不同字段（如一个文档有`age`，另一个可无）|

### 关键：BSON 格式
MongoDB 以 BSON（Binary JSON）存储数据，是 JSON 的二进制扩展，支持更多数据类型（如日期、二进制、ObjectId、浮点数等），示例：
```json
{
  "_id": ObjectId("65487f3e8a7b6c5d4e3f2a1b"), // 自动生成的唯一ID
  "username": "zhangsan",
  "age": 25,
  "address": { // 嵌套文档
    "province": "北京",
    "city": "北京市"
  },
  "hobbies": ["篮球", "编程"], // 数组
  "createTime": ISODate("2025-12-10T08:00:00Z") // 日期类型
}
```

## 三、核心特点
### 1. 面向文档，Schema 自由
- 无需提前定义表结构，文档字段可灵活增删，适配频繁变更的业务（如社交APP的用户动态、电商商品属性）；
- 同一集合的文档可差异化存储（如部分商品有`spec`字段，部分无），无需像MySQL一样加 nullable 列。

### 2. 高性能
- 内存映射存储：将数据文件映射到内存，优先从内存读取，大幅提升读写速度；
- 原生支持索引：覆盖单字段、复合、地理空间、文本索引，查询效率接近关系型数据库；
- 写入优化：支持批量写入、异步写入，高并发场景下吞吐量优于MySQL。

### 3. 高可用（副本集）
- 副本集（Replica Set）：由主节点（Primary）+ 从节点（Secondary）组成，主节点故障自动切换到从节点，无单点故障；
- 数据自动同步：从节点实时同步主节点数据，支持读写分离（读请求分发到从节点）。

### 4. 易扩展（分片集群）
- 分片（Sharding）：将海量数据拆分到多个「分片服务器」，按分片键（如用户ID、时间）分布数据，支持水平扩展；
- 自动分片管理：MongoDB自动处理数据分片、路由，对应用层透明。

### 5. 丰富的查询与操作
- 支持类SQL的查询语法（`find`/`update`/`delete`），支持条件筛选、排序、分页、聚合（Aggregation）；
- 支持原子操作（如`$inc`自增、`$push`向数组加元素）、地理空间查询（如「附近的人」）、文本检索。

## 四、适用场景
MongoDB 并非替代关系型数据库，而是互补，以下场景优先选MongoDB：
1. **大数据量、高并发读写**：如用户行为日志、操作日志、埋点数据（亿级数据存储+高写入QPS）；
2. **灵活的业务模型**：如社交APP（用户动态、评论，字段频繁变更）、电商商品（不同品类属性差异大）；
3. **地理位置相关**：如外卖配送、打车APP（LBS查询，MongoDB原生支持地理空间索引）；
4. **快速迭代的项目**：初创产品，无需提前设计复杂表结构，快速上线、灵活调整；
5. **缓存层**：替代Redis存储结构化数据（如用户会话、临时数据），支持复杂查询。

### 不适用场景
- 强事务要求：如金融交易、银行系统（MongoDB 4.0+支持多文档事务，但性能和完整性不如MySQL）；
- 复杂多表关联查询：如ERP、财务系统（MongoDB关联查询（`$lookup`）性能差，不如MySQL的JOIN）；
- 严格的Schema约束：如政府、医疗数据（需固定字段、数据校验）。

## 五、MongoDB 基本操作（Mongo Shell 示例）
Mongo Shell 是 MongoDB 自带的命令行工具，以下是核心CRUD操作：

### 1. 基础准备
```bash
# 连接MongoDB（本地默认端口27017）
mongo

# 创建/切换数据库（不存在则创建）
use test_db

# 创建集合（插入文档时自动创建，也可手动）
db.createCollection("user")
```

### 2. 插入文档（CREATE）
```javascript
// 插入单条
db.user.insertOne({
  username: "zhangsan",
  age: 20,
  address: { province: "上海", city: "上海市" },
  hobbies: ["游戏", "音乐"]
});

// 插入多条
db.user.insertMany([
  { username: "lisi", age: 22, hobbies: ["读书"] },
  { username: "wangwu", age: 25, address: { province: "北京" } }
]);
```

### 3. 查询文档（READ）
```javascript
// 查询所有
db.user.find();

// 条件查询（age>20）
db.user.find({ age: { $gt: 20 } });

// 投影查询（只返回username和age，隐藏_id）
db.user.find({ age: { $gt: 20 } }, { username: 1, age: 1, _id: 0 });

// 排序（age降序）+ 分页（跳过1条，取1条）
db.user.find().sort({ age: -1 }).skip(1).limit(1);

// 按嵌套字段查询（address.province="北京"）
db.user.find({ "address.province": "北京" });
```

### 4. 更新文档（UPDATE）
```javascript
// 更新单条（将zhangsan的age改为21）
db.user.updateOne(
  { username: "zhangsan" },
  { $set: { age: 21 } }
);

// 更新多条（age<25的用户，添加字段createTime）
db.user.updateMany(
  { age: { $lt: 25 } },
  { $set: { createTime: new Date() } }
);
```

### 5. 删除文档（DELETE）
```javascript
// 删除单条
db.user.deleteOne({ username: "wangwu" });

// 删除多条（age>20）
db.user.deleteMany({ age: { $gt: 20 } });
```

## 六、SpringBoot 整合 MongoDB（实战示例）
SpringBoot 提供了 `spring-boot-starter-data-mongodb` 依赖，简化MongoDB操作，以下是核心步骤：

### 1. 引入依赖（pom.xml）
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb</artifactId>
</dependency>
```

### 2. 配置MongoDB连接（application.yml）
```yaml
spring:
  data:
    mongodb:
      uri: mongodb://localhost:27017/test_db # 单机版
      # 副本集配置：mongodb://node1:27017,node2:27017,node3:27017/test_db?replicaSet=rs0
      # 认证配置：mongodb://username:password@localhost:27017/test_db?authSource=admin
```

### 3. 定义实体类（映射Collection）
```java
package com.example.demo.entity;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.util.List;
import java.util.Date;

@Data
@Document(collection = "user") // 映射MongoDB的user集合
public class User {
    @Id // 映射_id字段
    private String id; // MongoDB默认ObjectId为字符串类型

    @Field("username") // 映射文档的username字段（字段名一致可省略）
    private String username;

    private Integer age;

    // 嵌套文档
    private Address address;

    // 数组
    private List<String> hobbies;

    private Date createTime;

    // 嵌套实体类
    @Data
    public static class Address {
        private String province;
        private String city;
    }
}
```

### 4. 定义Repository（数据访问层）
继承 `MongoRepository`，自动获得CRUD方法：
```java
package com.example.demo.repository;

import com.example.demo.entity.User;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserRepository extends MongoRepository<User, String> {
    // 自定义查询（按方法名自动生成SQL）
    List<User> findByAgeGreaterThan(Integer age);

    // 按用户名查询
    User findByUsername(String username);
}
```

### 5. 服务层与控制层
```java
// Service层
package com.example.demo.service;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;

@Service
public class UserService {
    @Resource
    private UserRepository userRepository;

    // 新增用户
    public User addUser(User user) {
        user.setCreateTime(new Date());
        return userRepository.save(user);
    }

    // 按年龄查询
    public List<User> findByAge(Integer age) {
        return userRepository.findByAgeGreaterThan(age);
    }

    // 查询所有
    public List<User> findAll() {
        return userRepository.findAll();
    }
}

// Controller层
package com.example.demo.controller;

import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {
    @Resource
    private UserService userService;

    @PostMapping("/add")
    public User addUser(@RequestBody User user) {
        return userService.addUser(user);
    }

    @GetMapping("/age/{age}")
    public List<User> findByAge(@PathVariable Integer age) {
        return userService.findByAge(age);
    }

    @GetMapping("/all")
    public List<User> findAll() {
        return userService.findAll();
    }
}
```

## 七、MongoDB 优缺点总结
### 优点
1. **灵活性高**：无固定Schema，适配快速迭代的业务；
2. **高性能**：内存映射+索引优化，高并发读写吞吐量高；
3. **易扩展**：原生支持副本集（高可用）、分片（水平扩展）；
4. **功能丰富**：支持地理空间查询、文本检索、聚合分析；
5. **开发友好**：BSON接近JSON，前端/后端解析成本低。

### 缺点
1. **事务支持弱**：4.0+支持多文档事务，但性能和隔离性不如MySQL，不适合强事务场景；
2. **关联查询差**：`$lookup` 实现关联查询，性能远低于MySQL的JOIN；
3. **占用空间大**：BSON存储冗余，且无压缩（默认），占用磁盘比MySQL多；
4. **复杂查询性能低**：多条件、多维度聚合查询，性能不如关系型数据库；
5. **数据一致性弱**：最终一致性，不适合金融级数据存储。

## 八、MongoDB vs MySQL 选型建议
| 维度         | MongoDB                | MySQL                      |
|--------------|------------------------|----------------------------|
| 数据结构     | 文档型（灵活）| 关系型（固定表结构）|
| 事务支持     | 弱（多文档事务）| 强（ACID）|
| 扩展方式     | 水平扩展（分片）| 先垂直后水平（分库分表）|
| 查询能力     | 简单查询快，复杂关联慢 | 复杂关联查询快             |
| 适用场景     | 大数据、高并发、灵活模型 | 事务、复杂关联、强一致性   |

**选型原则**：
- 核心业务（如订单、支付）用MySQL；
- 非核心、高并发、灵活结构的场景（如日志、用户行为、社交动态）用MongoDB；
- 混合场景：MySQL存储核心数据，MongoDB做缓存/扩展存储。