# MySQL vs PostgreSQL 建表语法核心区别｜极简对照版

我给你整理**最实用、最常踩坑**的差异，直接复制就能用，适合程序员快速对照。

---

## 一、最基础建表语句对比

### MySQL

```SQL

CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### PostgreSQL

```SQL

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,  -- 或 GENERATED AS IDENTITY
    name VARCHAR(50) NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 二、10 个核心语法区别（必记）

### 1. 自增主键

- **MySQL**：`AUTO_INCREMENT`

- **PG**：`SERIAL` / `BIGSERIAL` / `GENERATED AS IDENTITY`（推荐）

### 2. 字符串类型

- **MySQL**：`VARCHAR(n)` / `CHAR(n)` / `TEXT`

- **PG**：`VARCHAR(n)` / `CHAR(n)` / `TEXT`（无长度限制，性能更好）

### 3. 时间类型

- **MySQL**：`DATETIME` / `TIMESTAMP`

- **PG**：只有 `TIMESTAMP` / `TIMESTAMPTZ`（带时区，推荐）

### 4. 布尔类型

- **MySQL**：`TINYINT(1)` 模拟布尔

- **PG**：原生 `BOOLEAN`（true/false/null）

### 5. 分页语法

- **MySQL**：`LIMIT n, m`

- **PG**：`LIMIT n OFFSET m`

### 6. 引号规则

- **MySQL**：用 **反引号 ** **` `** 包裹关键字/字段

- **PG**：用 **双引号 ""** 包裹（如表名叫 user 必须加）

### 7. 主键无符号

- **MySQL**：`INT UNSIGNED`

- **PG**：不支持无符号，直接用 `BIGINT`

### 8. 注释语法

- **MySQL**：字段后直接写 `COMMENT '用户名'`

- **PG**：必须单独写 `COMMENT ON COLUMN user.name IS '用户名';`

### 9. 模糊匹配

- **MySQL**：`LIKE` 不区分大小写

- **PG**：`LIKE` 区分，`ILIKE` 不区分

### 10. 分页大表性能

- **MySQL**：深度分页慢

- **PG**：OFFSET 也慢，但有更好的优化方案

---

## 三、完整建表示例对照（最实用）

### MySQL 完整版

```SQL

CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(32) NOT NULL COMMENT '账号',
    age TINYINT UNSIGNED NULL COMMENT '年龄',
    status TINYINT(1) DEFAULT 1 COMMENT '状态 1=正常',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COMMENT = '用户表';
```

### PostgreSQL 完整版

```SQL

CREATE TABLE "user" (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(32) NOT NULL,
    age SMALLINT,
    status BOOLEAN DEFAULT TRUE,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PG 必须单独加注释
COMMENT ON TABLE "user" IS '用户表';
COMMENT ON COLUMN "user".id IS '用户ID';
COMMENT ON COLUMN "user".username IS '账号';
```

---

## 四、快速记忆口诀

1. **自增**：MySQL AUTO_INCREMENT，PG IDENTITY/SERIAL

2. **引号**：MySQL 反引号，PG 双引号

3. **布尔**：MySQL TINYINT，PG BOOLEAN

4. **时间**：MySQL DATETIME，PG TIMESTAMP

5. **注释**：MySQL 直接写，PG 单独句

6. **关键字表名**：PG 必须加双引号，否则报错

---

### 总结

- 90% 基础字段语法**通用**

- 真正差异只有：**自增、引号、布尔、时间、注释、无符号**

- 如果有现成的 MySQL 建表语句，可以**一键帮你转换成 PG 版本**


> （注：文档部分内容可能由 AI 生成）