# SQL外键（Foreign Key）详细介绍与使用举例
外键（Foreign Key，简称FK）是关系型数据库中**用于建立和强制两个表之间关联关系的约束**，它通过引用另一张表的主键（Primary Key）或唯一键（Unique Key），实现表间的**参照完整性**，是关系型数据库三大完整性约束（实体完整性、参照完整性、域完整性）的核心组成部分。

## 一、外键的基本概念
- **外键所在表**：称为**从表/子表（Child Table）**，外键是从表中的一列/多列。
- **被引用的表**：称为**主表/父表（Parent Table）**，被引用的列必须是主表的主键或唯一约束列。
- **核心逻辑**：从表的外键值必须是主表中已存在的值（或NULL，若外键列允许为空），否则数据库会拒绝执行插入/更新操作。

## 二、外键的核心作用
1. **维护参照完整性**：防止插入无效的关联数据（如评论表引用不存在的名言ID），避免数据孤立。
2. **限制非法修改/删除**：默认情况下，主表中被从表引用的数据无法被随意删除或修改主键，防止引用关系失效。
3. **建立表间关系**：明确表之间的**一对多、多对多、一对一**关系，是数据库设计中“范式”的重要体现。

## 三、外键的创建方式
外键可在**创建表时定义**，也可在**表创建后通过ALTER TABLE添加**，不同数据库的语法基本一致（细微差异主要在命名和引擎配置）。

### 3.1 创建表时定义外键
语法格式：
```sql
CREATE TABLE 从表名 (
    列名1 数据类型 [约束],
    列名2 数据类型 [约束],
    -- 外键列
    外键列 数据类型,
    -- 定义外键约束
    FOREIGN KEY (外键列) REFERENCES 主表名(被引用列)
    [ON DELETE 级联规则] [ON UPDATE 级联规则]
);
```

### 3.2 表创建后添加外键
若表已存在，通过`ALTER TABLE`添加外键：
```sql
ALTER TABLE 从表名
ADD CONSTRAINT 外键名  -- 可选：为外键命名，便于后续删除/修改
FOREIGN KEY (外键列) REFERENCES 主表名(被引用列)
[ON DELETE 级联规则] [ON UPDATE 级联规则];
```

> 注：外键名若不手动指定，数据库会自动生成一个默认名称（如MySQL的`fk_xxx`）。

## 四、外键的使用场景举例
以下示例基于**MySQL InnoDB引擎**（MyISAM不支持外键），涵盖数据库中最常见的**一对多、多对多、一对一**三种关系。

### 4.1 场景1：一对多关系（最常用）
**关系说明**：主表的一条记录可对应从表的多条记录，从表的一条记录仅对应主表的一条记录。
**示例**：用户表（`users`）与订单表（`orders`），一个用户可下多个订单，一个订单仅属于一个用户。

#### 步骤1：创建主表（用户表）
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,  -- 主键
    user_name VARCHAR(50) NOT NULL,
    user_phone VARCHAR(20) UNIQUE,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;  -- 必须指定InnoDB引擎（MySQL）
```

#### 步骤2：创建从表（订单表），并定义外键
```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    order_num VARCHAR(30) NOT NULL UNIQUE,
    order_amount DECIMAL(10,2) NOT NULL,
    user_id INT,  -- 外键列，关联用户表的user_id
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- 定义外键约束，引用用户表的user_id
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE = InnoDB;
```

#### 步骤3：验证外键约束
1. **插入有效数据**：先插入主表数据，再插入从表关联数据（正常执行）。
   ```sql
   -- 插入用户（主表）
   INSERT INTO users (user_name, user_phone) VALUES ('张三', '13800138000');
   -- 插入订单（从表），引用存在的user_id=1
   INSERT INTO orders (order_num, order_amount, user_id) VALUES ('ORD2025001', 99.9, 1);
   ```

2. **插入无效数据**：从表引用主表不存在的`user_id=99`（数据库报错）。
   ```sql
   -- 报错：Cannot add or update a child row: a foreign key constraint fails
   INSERT INTO orders (order_num, order_amount, user_id) VALUES ('ORD2025002', 199.9, 99);
   ```

3. **删除主表被引用的数据**：删除`user_id=1`的用户（数据库报错，因为订单表引用了该ID）。
   ```sql
   -- 报错：Cannot delete or update a parent row: a foreign key constraint fails
   DELETE FROM users WHERE user_id = 1;
   ```

### 4.2 场景2：多对多关系
**关系说明**：表A的一条记录可对应表B的多条记录，表B的一条记录也可对应表A的多条记录。
**实现方式**：需创建**中间关联表**，关联表中包含两个外键，分别引用两张主表的主键。
**示例**：学生表（`students`）与课程表（`courses`），一个学生可选多门课程，一门课程可被多个学生选择。

#### 步骤1：创建两张主表
```sql
-- 学生表（主表1）
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_name VARCHAR(50) NOT NULL,
    grade VARCHAR(20)
) ENGINE = InnoDB;

-- 课程表（主表2）
CREATE TABLE courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(50) NOT NULL,
    teacher VARCHAR(50)
) ENGINE = InnoDB;
```

#### 步骤2：创建中间关联表（学生-课程表），定义复合外键
```sql
CREATE TABLE student_course (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    score INT,
    -- 外键1：引用学生表的student_id
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    -- 外键2：引用课程表的course_id
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    -- 唯一约束：防止同一学生重复选同一课程
    UNIQUE KEY uk_student_course (student_id, course_id)
) ENGINE = InnoDB;
```

#### 步骤3：插入数据验证
```sql
-- 插入学生
INSERT INTO students (student_name, grade) VALUES ('李四', '高一'), ('王五', '高二');
-- 插入课程
INSERT INTO courses (course_name, teacher) VALUES ('数学', '张老师'), ('英语', '李老师');
-- 插入选课记录（中间表）
INSERT INTO student_course (student_id, course_id, score) VALUES (1,1,90), (1,2,85), (2,1,95);
```

### 4.3 场景3：一对一关系
**关系说明**：表A的一条记录仅对应表B的一条记录，反之亦然。
**实现方式**：将从表的外键设为**唯一约束（UNIQUE）**，确保外键值不重复。
**示例**：用户表（`users`）与用户详情表（`user_details`），一个用户仅对应一份详情。

#### 步骤1：创建主表（用户表，复用之前的`users`表）
#### 步骤2：创建从表（用户详情表），外键加唯一约束
```sql
CREATE TABLE user_details (
    detail_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE,  -- 唯一约束，实现一对一
    address VARCHAR(200),
    age INT,
    gender ENUM('男','女','未知'),
    -- 定义外键，引用用户表的user_id
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE = InnoDB;
```

#### 步骤3：插入数据验证
```sql
-- 插入用户详情（一对一关联user_id=1）
INSERT INTO user_details (user_id, address, age, gender) VALUES (1, '北京市朝阳区', 25, '男');
-- 再次插入user_id=1的详情（报错，因为UNIQUE约束）
INSERT INTO user_details (user_id, address, age, gender) VALUES (1, '上海市浦东新区', 26, '男');
```

## 五、外键的级联操作
默认情况下，外键会**阻止删除/修改主表被引用的数据**，但可通过`ON DELETE`和`ON UPDATE`指定**级联规则**，让数据库自动处理从表的关联数据。

### 常用级联规则
| 规则                | 作用                                                                 |
|---------------------|----------------------------------------------------------------------|
| `ON DELETE CASCADE` | 主表数据删除时，从表关联数据**自动删除**                             |
| `ON UPDATE CASCADE` | 主表主键更新时，从表外键**自动同步更新**                             |
| `ON DELETE SET NULL`| 主表数据删除时，从表外键列设为NULL（需外键列允许为空）               |
| `ON DELETE RESTRICT`| 默认规则，拒绝删除主表被引用的数据（与`NO ACTION`效果一致）          |

### 示例：级联删除
修改订单表的外键，添加`ON DELETE CASCADE`：
```sql
-- 先删除原有外键（需先查询外键名，MySQL可通过SHOW CREATE TABLE orders查看）
ALTER TABLE orders DROP FOREIGN KEY fk_orders_users;  -- 假设外键名是fk_orders_users

-- 重新添加外键，指定级联删除
ALTER TABLE orders
ADD CONSTRAINT fk_orders_users
FOREIGN KEY (user_id) REFERENCES users(user_id)
ON DELETE CASCADE  -- 删除用户时，自动删除该用户的所有订单
ON UPDATE CASCADE; -- 更新用户ID时，自动更新订单的user_id
```

验证级联删除：
```sql
-- 删除user_id=1的用户，订单表中该用户的订单会被自动删除
DELETE FROM users WHERE user_id = 1;
-- 查询订单表，user_id=1的订单已不存在
SELECT * FROM orders WHERE user_id = 1;
```

## 六、外键的删除
若需移除外键约束，使用`ALTER TABLE`语句，语法如下（不同数据库需指定外键名）：
```sql
-- 1. 查看外键名（以MySQL为例）
SHOW CREATE TABLE 从表名;  -- 在结果中找到CONSTRAINT后的外键名

-- 2. 删除外键
ALTER TABLE 从表名 DROP FOREIGN KEY 外键名;

-- 示例：删除订单表的外键fk_orders_users
ALTER TABLE orders DROP FOREIGN KEY fk_orders_users;
```

## 七、外键的注意事项
1. **存储引擎支持**：MySQL的`InnoDB`引擎支持外键，`MyISAM`不支持；PostgreSQL、SQL Server、Oracle均原生支持外键。
2. **数据类型一致**：外键列与被引用列的**数据类型必须完全一致**（如均为`INT`，长度、符号属性也需一致）。
3. **被引用列的要求**：被引用列必须是主表的**主键**或**唯一约束（UNIQUE）**列，否则无法创建外键。
4. **外键的可空性**：外键列允许为NULL时，可插入无关联的NULL值；若设为`NOT NULL`，则必须引用主表的有效数据。
5. **复合外键**：外键可由多列组成（复合外键），需确保复合外键与主表的复合主键/唯一键一一对应。
6. **性能影响**：外键会增加插入、更新、删除的开销（需检查关联数据），但对查询性能无影响；高并发场景需权衡数据完整性与性能。

## 总结
外键是实现数据库参照完整性的核心工具，通过建立表间关联，避免了无效数据的产生。在实际开发中，需根据业务场景选择合适的外键规则（如级联删除/置空），并结合数据库引擎特性合理设计，同时注意多对多关系需通过中间表实现。