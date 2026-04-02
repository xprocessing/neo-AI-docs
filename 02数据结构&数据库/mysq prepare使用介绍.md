# MySQL PREPARE（预处理语句/预编译语句）完整使用介绍
## 一、什么是 PREPARE 预处理语句
`PREPARE` 是 MySQL 从 **4.1版本开始原生支持** 的**预处理（预编译）语句** 语法，也常被称为「动态SQL」。

它的核心逻辑是：**将一条SQL语句「模板化」，先对SQL的「结构」进行编译解析，再单独传入参数执行**，把「SQL编译」和「参数赋值执行」拆分为两个独立的步骤，区别于直接执行的静态SQL。

### 核心语法（完整四步，缺一不可）
MySQL 预处理语句的使用遵循固定的**4步语法规范**，顺序不能颠倒，语法格式如下：
```sql
-- 1. 定义预处理语句：编译SQL模板，stmt_name是自定义的预处理语句名称，? 是占位符
PREPARE stmt_name FROM 'SQL模板语句(包含?)';

-- 2. 为占位符赋值：用SET给用户变量赋值，变量名自定义（如@var1、@id）
SET @var1 = 值1, @var2 = 值2;

-- 3. 执行预处理语句：传入赋值后的变量，执行编译好的SQL模板
EXECUTE stmt_name [USING @var1, @var2, ...];

-- 4. 释放预处理语句：释放占用的内存资源，必做优化（会话关闭也会自动释放）
DEALLOCATE PREPARE stmt_name;
```
> 补充：释放语法也可以写 `DROP PREPARE stmt_name`，和 `DEALLOCATE PREPARE` 完全等价，推荐写前者。

---

## 二、为什么要使用 PREPARE 预处理语句（核心2大优势，重中之重）
预处理语句是MySQL中**高性能+高安全**的SQL执行方式，也是生产环境的推荐写法，核心优势有2个，优先级分先后：

### ✅ 优势1：**彻底防止 SQL 注入攻击**（最核心价值）
SQL注入的根源是：**拼接字符串形式的静态SQL** 会把传入的「参数值」当作「SQL语法的一部分」解析执行。
比如恶意拼接 `OR 1=1`、`DROP TABLE` 等内容，MySQL会把这些参数解析成SQL指令执行，造成数据泄露/删除。

而预处理语句中，**`? 占位符` 是「值占位」，参数和SQL模板完全分离**：
- 第一步编译时，MySQL只解析SQL的「结构」（比如`SELECT * FROM user WHERE id=?`的查询逻辑）；
- 第二步传入的参数，**只会被当作「纯数据值」处理，永远不会被解析成SQL语法**；
无论传入什么特殊字符，都只是普通值，彻底杜绝了SQL注入的可能。

### ✅ 优势2：**大幅提升重复执行的SQL效率**
对于需要**多次执行、结构相同、仅参数不同**的SQL（比如循环查询不同id的用户、批量插入数据），预处理的效率优势极其明显：
- 静态SQL：每执行一次，MySQL都要做「语法解析→语义校验→执行计划生成→编译」的完整流程，重复执行会重复做这些工作；
- 预处理SQL：**只在 PREPARE 阶段做1次编译解析**，后续每次执行（EXECUTE）都直接复用编译好的执行计划，只需要传入新参数即可。

> 测试数据：同一条SQL重复执行1000次，预处理语句的执行效率比静态SQL提升 **30% ~ 80%**，执行次数越多，优势越大。

---

## 三、PREPARE 核心规则：占位符 `?` 的使用限制（高频踩坑点）
`?` 是预处理语句的「参数占位符」，也是最核心的语法，但MySQL对它的使用有**严格的限制**，这是**100%会遇到的坑**，必须牢记：
### ✅ 占位符 `?` 支持的场景：**仅能替代「数据值」**
`?` 只能用来表示 SQL 中需要传入的「具体数据」，比如 `WHERE` 条件的值、`INSERT` 的字段值、`UPDATE` 的赋值内容，例如：
```sql
-- ✅ 正确：? 替代 id的数值、name的字符串值
PREPARE stmt FROM 'SELECT * FROM user WHERE id=? AND name=?';
PREPARE stmt2 FROM 'INSERT INTO user(name, age) VALUES(?, ?)';
```

### ❌ 占位符 `?` 不支持的场景（绝对不能用）
`?` **不能替代任何SQL语法关键字/标识符**，仅能替代「值」，以下场景全部无效：
1. 数据库名、表名、字段名（如 `SELECT ? FROM user` 想替代字段名，不行）；
2. SQL关键字（如 `SELECT * FROM user ?` 想替代 `ORDER BY id`，不行）；
3. 函数名、运算符、分组/排序/分页关键字（如 `LIMIT ?` 部分版本兼容，但不推荐）；
4. 字符串的引号、拼接符（如 `WHERE name='?'` 不需要加引号，MySQL会自动处理）。

---

## 四、基础使用案例（3类高频场景，直接套用）
### ✅ 案例1：单占位符 - 条件查询（最常用）
需求：根据用户ID查询用户信息，用预处理语句实现，防止注入+复用执行计划。
```sql
-- 1. 定义预处理语句，? 替代id的值
PREPARE sel_user FROM 'SELECT id, name, age FROM user WHERE id = ?';

-- 2. 为占位符赋值
SET @user_id = 10;

-- 3. 执行预处理语句
EXECUTE sel_user USING @user_id;

-- 4. 释放资源
DEALLOCATE PREPARE sel_user;
```

### ✅ 案例2：多占位符 - 新增/修改数据
需求：批量新增用户，SQL结构相同，仅参数不同，用预处理语句提升效率。
```sql
-- 1. 定义预处理语句，2个?分别替代name和age的值
PREPARE ins_user FROM 'INSERT INTO user(name, age) VALUES(?, ?)';

-- 2. 赋值并执行第1条数据
SET @name1 = '张三', @age1 = 20;
EXECUTE ins_user USING @name1, @age1;

-- 复用编译好的模板，直接赋值执行第2条数据（无需重新PREPARE）
SET @name2 = '李四', @age2 = 22;
EXECUTE ins_user USING @name2, @age2;

-- 3. 释放资源
DEALLOCATE PREPARE ins_user;
```

### ✅ 案例3：动态SQL（解决「?不能替代表名/字段名」的问题）
需求：需要动态指定查询的「表名」或「字段名」，比如根据不同业务查询不同表，此时用 **字符串拼接** 实现，这是预处理语句的进阶用法。
```sql
-- 场景：动态指定表名和字段名，查询数据
SET @table_name = 'user';   -- 动态表名
SET @field_name = 'name';   -- 动态字段名
SET @id = 10;               -- 动态值

-- 核心：用CONCAT拼接SQL模板字符串，再传给PREPARE
SET @sql_template = CONCAT('SELECT id, ', @field_name, ' FROM ', @table_name, ' WHERE id = ?');

-- 后续步骤不变
PREPARE dyn_sql FROM @sql_template;
EXECUTE dyn_sql USING @id;
DEALLOCATE PREPARE dyn_sql;
```
> 注意：动态拼接表名/字段名时，**必须对传入的表名/字段名做白名单校验**（比如判断是否是允许的表名），防止注入风险！

---

## 五、PREPARE 重要补充说明（必知的6个细节）
### 1. 预处理语句的「作用域」：当前会话（Session）有效
MySQL的预处理语句是**会话级别的资源**：
- 同一个会话内，定义的预处理语句可以重复执行（EXECUTE）；
- 会话关闭（比如断开连接）后，该会话内的所有预处理语句会被自动释放；
- 不同会话之间的预处理语句相互独立，互不影响。

### 2. 支持的SQL语句类型
预处理语句支持绝大多数MySQL常用语句，包括：
- DML：SELECT、INSERT、UPDATE、DELETE（最常用）；
- DDL：CREATE TABLE、ALTER TABLE（较少用）；
- 其他：SHOW、DESC、CALL（存储过程）等。

### 3. 变量的使用规范
- 预处理语句中必须使用 **用户变量（@xxx）**，不能使用局部变量（比如存储过程中的 DECLARE 变量）；
- 多个变量在 EXECUTE 时，**顺序必须和 PREPARE 中的 ? 占位符完全一致**。

### 4. 预处理语句的「重定义」
如果在同一个会话中，对已存在的预处理语句名称重新执行 `PREPARE`，MySQL会自动覆盖原有的语句，无需手动释放。

### 5. 性能优化建议
- 对于**只执行1次**的SQL，预处理语句的效率和静态SQL几乎无差别（甚至多了编译步骤），此时可以不用；
- 对于**执行≥2次**的SQL，预处理语句的效率优势会立刻体现，强烈推荐使用；
- 生产环境中，**一定要手动执行 DEALLOCATE PREPARE**，避免大量未释放的预处理语句占用内存。

### 6. 与编程语言中预处理的关系
Java（JDBC）、PHP（PDO）、Python（pymysql）等编程语言中提供的「预处理语句」，**底层本质都是调用MySQL的原生 PREPARE 语法**，编程语言只是做了封装，核心逻辑完全一致。

---

## 六、完整综合示例（生产级写法）
```sql
-- 需求：查询指定表的指定字段，根据ID过滤，支持重复执行，防止注入，完整释放资源
-- 1. 定义动态参数（可外部传入）
SET @db_table = 'user';
SET @db_field = 'id, name, age, phone';
SET @filter_id = 15;

-- 2. 拼接SQL模板（表名/字段名动态，值用占位符）
SET @sql = CONCAT('SELECT ', @db_field, ' FROM ', @db_table, ' WHERE id = ?');

-- 3. 预处理核心流程
PREPARE query_stmt FROM @sql;
EXECUTE query_stmt USING @filter_id;
DEALLOCATE PREPARE query_stmt;

-- 复用模板，查询另一个ID，无需重新PREPARE
SET @filter_id = 16;
PREPARE query_stmt FROM @sql;
EXECUTE query_stmt USING @filter_id;
DEALLOCATE PREPARE query_stmt;
```

---

## ✅ 总结（核心知识点速记）
1. `PREPARE` 是MySQL原生的预处理语句，**4步核心语法**：定义 → 赋值 → 执行 → 释放；
2. 两大核心价值：**彻底防SQL注入**（优先级最高） + **提升重复执行效率**；
3. 核心坑点：占位符 `?` **仅能替代数据值**，不能替代表名、字段名、关键字；
4. 作用域：会话级，会话关闭自动释放，推荐手动释放；
5. 适用场景：多次执行的SQL、有外部参数传入的SQL（生产环境必用）；
6. 动态表名/字段名：用 `CONCAT` 拼接SQL模板，再做预处理，记得白名单校验。

预处理语句是MySQL开发的必备技能，掌握它能让你的SQL代码既安全又高效，也是生产环境的标准写法！