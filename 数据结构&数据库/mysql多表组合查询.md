在MySQL中，多表组合查询是数据库操作的核心场景，主要通过**连接查询（JOIN）**、**子查询**、**联合查询（UNION）**等方式实现。以下结合**电商场景的示例表**（用户表、订单表、商品表、订单详情表），详细讲解各类多表查询的用法。

### 一、准备示例表和测试数据
首先创建4个关联表，并插入测试数据，表之间的关联关系为：
- `user`（用户表）的`id` → `order`（订单表）的`user_id`（外键）
- `order`（订单表）的`id` → `order_detail`（订单详情表）的`order_id`（外键）
- `product`（商品表）的`id` → `order_detail`（订单详情表）的`product_id`（外键）

#### 1. 创建表结构
```sql
-- 用户表
CREATE TABLE `user` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `age` INT COMMENT '年龄',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT '用户表';

-- 订单表
CREATE TABLE `order` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
  `order_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '订单编号',
  `user_id` INT COMMENT '关联用户ID',
  `order_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
  `total_amount` DECIMAL(10,2) COMMENT '订单总金额',
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE SET NULL
) COMMENT '订单表';

-- 商品表
CREATE TABLE `product` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID',
  `product_name` VARCHAR(100) NOT NULL COMMENT '商品名称',
  `price` DECIMAL(10,2) NOT NULL COMMENT '商品单价',
  `stock` INT DEFAULT 0 COMMENT '库存'
) COMMENT '商品表';

-- 订单详情表
CREATE TABLE `order_detail` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '详情ID',
  `order_id` INT COMMENT '关联订单ID',
  `product_id` INT COMMENT '关联商品ID',
  `num` INT DEFAULT 1 COMMENT '购买数量',
  FOREIGN KEY (`order_id`) REFERENCES `order`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`product_id`) REFERENCES `product`(`id`) ON DELETE SET NULL
) COMMENT '订单详情表';
```

#### 2. 插入测试数据
```sql
-- 插入用户
INSERT INTO `user` (username, age) VALUES ('张三', 25), ('李四', 30), ('王五', 28);

-- 插入商品
INSERT INTO `product` (product_name, price, stock) VALUES 
('手机', 2999.99, 100), 
('电脑', 5999.99, 50), 
('耳机', 199.99, 200);

-- 插入订单
INSERT INTO `order` (order_no, user_id, total_amount) VALUES 
('ORD20251225001', 1, 3199.98), 
('ORD20251225002', 1, 5999.99), 
('ORD20251225003', 2, 199.99),
('ORD20251225004', NULL, 2999.99); -- 无关联用户的订单

-- 插入订单详情
INSERT INTO `order_detail` (order_id, product_id, num) VALUES 
(1, 1, 1), (1, 3, 1), -- 订单1：手机+耳机
(2, 2, 1),             -- 订单2：电脑
(3, 3, 1),             -- 订单3：耳机
(4, 1, 1);             -- 订单4：手机
```

### 二、核心多表查询示例
#### 1. 内连接（INNER JOIN）
**作用**：只返回多个表中**关联条件匹配**的记录（最常用的连接方式）。  
**语法**：`SELECT 字段 FROM 表1 INNER JOIN 表2 ON 关联条件 [WHERE 筛选条件]`

**示例1**：查询有订单的用户及其订单信息
```sql
SELECT 
  u.id AS 用户ID,
  u.username AS 用户名,
  o.id AS 订单ID,
  o.order_no AS 订单编号,
  o.total_amount AS 订单金额
FROM `user` u
INNER JOIN `order` o ON u.id = o.user_id;
```
**结果说明**：仅返回`user`和`order`中`user_id`匹配的记录（张三、李四的订单，王五无订单则不显示，订单4无用户也不显示）。

#### 2. 左外连接（LEFT JOIN）
**作用**：返回**左表的所有记录**，以及右表中关联条件匹配的记录；若右表无匹配，返回`NULL`。  
**语法**：`SELECT 字段 FROM 表1 LEFT JOIN 表2 ON 关联条件`

**示例2**：查询所有用户的订单信息（包括无订单的用户）
```sql
SELECT 
  u.id AS 用户ID,
  u.username AS 用户名,
  o.id AS 订单ID,
  o.order_no AS 订单编号
FROM `user` u
LEFT JOIN `order` o ON u.id = o.user_id;
```
**结果说明**：王五（无订单）的订单字段会显示`NULL`，左表（`user`）的所有记录都被保留。

#### 3. 右外连接（RIGHT JOIN）
**作用**：返回**右表的所有记录**，以及左表中关联条件匹配的记录；若左表无匹配，返回`NULL`。  
**语法**：`SELECT 字段 FROM 表1 RIGHT JOIN 表2 ON 关联条件`

**示例3**：查询所有订单的用户信息（包括无关联用户的订单）
```sql
SELECT 
  o.id AS 订单ID,
  o.order_no AS 订单编号,
  u.username AS 用户名
FROM `user` u
RIGHT JOIN `order` o ON u.id = o.user_id;
```
**结果说明**：订单4（无关联用户）的`用户名`字段显示`NULL`，右表（`order`）的所有记录都被保留。

#### 4. 全外连接（FULL JOIN）
**MySQL不直接支持`FULL JOIN`**，需通过`LEFT JOIN + UNION + RIGHT JOIN`实现，返回两个表的所有记录，无匹配则显示`NULL`。

**示例4**：查询所有用户和所有订单的关联信息
```sql
-- 左连接结果
SELECT u.id AS 用户ID, u.username, o.id AS 订单ID, o.order_no
FROM `user` u
LEFT JOIN `order` o ON u.id = o.user_id
UNION
-- 右连接排除重复的交集部分
SELECT u.id AS 用户ID, u.username, o.id AS 订单ID, o.order_no
FROM `user` u
RIGHT JOIN `order` o ON u.id = o.user_id
WHERE u.id IS NULL;
```
**结果说明**：包含所有用户（即使无订单）和所有订单（即使无用户）的记录。

#### 5. 多表连接（3张及以上表）
**场景**：查询用户的订单详情及商品信息（关联`user`、`order`、`order_detail`、`product`）。

**示例5**：查询张三的所有订单及购买的商品详情
```sql
SELECT 
  u.username AS 用户名,
  o.order_no AS 订单编号,
  p.product_name AS 商品名称,
  od.num AS 购买数量,
  p.price AS 商品单价,
  (od.num * p.price) AS 小计
FROM `user` u
INNER JOIN `order` o ON u.id = o.user_id
INNER JOIN `order_detail` od ON o.id = od.order_id
INNER JOIN `product` p ON od.product_id = p.id
WHERE u.username = '张三';
```
**结果说明**：返回张三的每笔订单对应的商品、数量、单价和小计金额。

#### 6. 交叉连接（CROSS JOIN）
**作用**：返回两个表的**笛卡尔积**（左表每条记录与右表每条记录组合），一般需结合`WHERE`筛选，否则结果集过大。

**示例6**：查询用户与商品的笛卡尔积（仅演示，实际很少用）
```sql
SELECT u.username, p.product_name
FROM `user` u
CROSS JOIN `product` p
WHERE u.id = 1; -- 筛选张三与所有商品的组合
```

#### 7. 子查询作为关联表
**场景**：先通过子查询筛选出特定数据，再与其他表连接查询。

**示例7**：查询购买过“手机”的用户信息
```sql
-- 子查询先找到包含手机的订单ID，再关联用户
SELECT DISTINCT u.id, u.username
FROM `user` u
INNER JOIN `order` o ON u.id = o.user_id
INNER JOIN (
  SELECT order_id FROM `order_detail` 
  WHERE product_id = (SELECT id FROM `product` WHERE product_name = '手机')
) od ON o.id = od.order_id;
```
**结果说明**：`DISTINCT`去重，返回所有购买过手机的用户（张三）。

#### 8. 联合查询（UNION / UNION ALL）
**作用**：合并多个`SELECT`语句的结果集（要求字段数、字段类型一致）。  
- `UNION`：去重并排序；  
- `UNION ALL`：保留重复记录，效率更高。

**示例8**：查询所有用户和商品的名称（仅演示联合逻辑）
```sql
SELECT username AS 名称, '用户' AS 类型 FROM `user`
UNION ALL
SELECT product_name AS 名称, '商品' AS 类型 FROM `product`;
```

### 三、关键注意事项
1. **关联条件（ON）与筛选条件（WHERE）**：`ON`用于定义表之间的关联关系，`WHERE`用于筛选最终结果；
2. **外键与连接**：外键是逻辑约束，不影响连接查询，但能保证数据完整性；
3. **别名**：多表查询时建议为表和字段起别名，避免字段名冲突；
4. **性能优化**：对关联字段建立索引（如`user.id`、`order.user_id`），避免大表笛卡尔积。

以上示例覆盖了MySQL多表查询的核心场景，可根据实际业务需求灵活组合使用。