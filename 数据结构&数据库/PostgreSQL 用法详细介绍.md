PostgreSQL是一款功能强大的开源关系型数据库，支持复杂数据类型、高级SQL特性、事务ACID、扩展性强，广泛应用于企业级应用、数据分析等场景。以下从核心功能、常用操作、高级特性等方面详细介绍其用法：


### 一、基础操作
#### 1. 数据库管理
- **创建数据库**  
  ```sql
  CREATE DATABASE mydb;
  ```
  可指定字符集、所有者：  
  ```sql
  CREATE DATABASE mydb WITH ENCODING 'UTF8' OWNER user1;
  ```

- **连接数据库**  
  命令行工具`psql`：  
  ```bash
  psql -U username -d mydb -h localhost
  ```

- **删除数据库**  
  ```sql
  DROP DATABASE IF EXISTS mydb;
  ```

#### 2. 表管理
- **创建表**  
  支持丰富数据类型（如数组、JSON、几何类型等）：  
  ```sql
  CREATE TABLE users (
      id SERIAL PRIMARY KEY,  -- 自增主键（SERIAL为PostgreSQL自增类型）
      name VARCHAR(50) NOT NULL,
      email VARCHAR(100) UNIQUE,
      age INT CHECK (age > 0),  -- 约束
      tags TEXT[],  -- 数组类型
      profile JSONB,  -- JSONB类型（支持索引）
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

- **修改表结构**  
  ```sql
  -- 添加列
  ALTER TABLE users ADD COLUMN phone VARCHAR(20);
  
  -- 修改列类型
  ALTER TABLE users ALTER COLUMN age TYPE SMALLINT;
  
  -- 删除列
  ALTER TABLE users DROP COLUMN phone;
  
  -- 添加约束
  ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);
  ```

- **删除表**  
  ```sql
  DROP TABLE IF EXISTS users;
  ```


### 二、数据操作
#### 1. 插入数据
```sql
-- 普通插入
INSERT INTO users (name, email, age, tags)
VALUES ('Alice', 'alice@example.com', 25, ARRAY['java', 'python']);

-- 插入JSON数据
INSERT INTO users (name, profile)
VALUES ('Bob', '{"city": "Beijing", "job": "engineer"}'::JSONB);

-- 批量插入
INSERT INTO users (name, age) VALUES ('Charlie', 30), ('David', 28);
```

#### 2. 查询数据
- **基础查询**  
  ```sql
  SELECT name, age FROM users WHERE age > 25;
  ```

- **数组类型查询**  
  ```sql
  -- 包含元素的数组
  SELECT * FROM users WHERE 'python' = ANY (tags);
  
  -- 数组长度
  SELECT name, array_length(tags, 1) AS tag_count FROM users;
  ```

- **JSONB类型查询**  
  ```sql
  -- 查询JSON字段属性
  SELECT name, profile->>'city' AS city FROM users;
  
  -- 按JSON属性过滤
  SELECT * FROM users WHERE profile @> '{"job": "engineer"}'::JSONB;
  ```

- **分页查询**  
  PostgreSQL推荐用`LIMIT/OFFSET`或游标，更高效的分页可结合主键：  
  ```sql
  SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 20;  -- 第3页，每页10条
  ```

#### 3. 更新数据
```sql
UPDATE users 
SET age = age + 1, profile = profile || '{"update_time": "2024-01-01"}'::JSONB
WHERE name = 'Alice';
```

#### 4. 删除数据
```sql
DELETE FROM users WHERE age < 18;
```


### 三、高级特性
#### 1. 索引优化
- **普通索引**  
  ```sql
  CREATE INDEX idx_users_email ON users(email);
  ```

- **JSONB索引**  
  ```sql
  -- GIN索引（支持JSONB复杂查询）
  CREATE INDEX idx_users_profile ON users USING GIN (profile);
  ```

- **部分索引**  
  只对满足条件的数据建索引，节省空间：  
  ```sql
  CREATE INDEX idx_users_age ON users(age) WHERE age > 20;
  ```

#### 2. 窗口函数
支持排名、分组统计等高级分析，常用函数：`ROW_NUMBER()`、`RANK()`、`SUM() OVER()`：  
```sql
-- 按年龄分组排名
SELECT 
    name, age,
    ROW_NUMBER() OVER (PARTITION BY age ORDER BY id) AS row_num,
    AVG(age) OVER () AS avg_age
FROM users;
```

#### 3. 公共表表达式（CTE）
简化复杂查询，支持递归查询：  
```sql
-- 非递归CTE
WITH user_stats AS (
    SELECT age, COUNT(*) AS count FROM users GROUP BY age
)
SELECT * FROM user_stats WHERE count > 5;

-- 递归CTE（查询树形结构，如部门层级）
WITH RECURSIVE dept_tree AS (
    SELECT id, name, parent_id FROM departments WHERE parent_id IS NULL
    UNION ALL
    SELECT d.id, d.name, d.parent_id FROM departments d
    JOIN dept_tree dt ON d.parent_id = dt.id
)
SELECT * FROM dept_tree;
```

#### 4. 事务与锁
- **事务控制**  
  ```sql
  BEGIN;  -- 开启事务
  UPDATE users SET age = 26 WHERE name = 'Alice';
  INSERT INTO orders (user_id, amount) VALUES (1, 100);
  COMMIT;  -- 提交事务
  -- ROLLBACK;  -- 回滚事务
  ```

- **悲观锁**  
  ```sql
  SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- 行级锁
  ```

#### 5. 存储过程与函数
支持PL/pgSQL、Python等语言编写存储过程：  
```sql
-- 创建函数
CREATE OR REPLACE FUNCTION get_user_count(age_limit INT)
RETURNS INT AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM users WHERE age > age_limit);
END;
$$ LANGUAGE plpgsql;

-- 调用函数
SELECT get_user_count(20);
```

#### 6. 触发器
触发自动操作（如数据变更时记录日志）：  
```sql
-- 创建日志表
CREATE TABLE user_logs (id SERIAL, user_id INT, action VARCHAR(20), create_time TIMESTAMP DEFAULT NOW());

-- 创建触发器函数
CREATE OR REPLACE FUNCTION log_user_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_logs (user_id, action) VALUES (NEW.id, TG_OP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 绑定触发器到users表
CREATE TRIGGER trigger_user_change
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION log_user_change();
```


### 四、数据导入导出
#### 1. 导出数据
```bash
# 导出整个数据库
pg_dump -U username -d mydb -f mydb_backup.sql

# 导出指定表
pg_dump -U username -d mydb -t users -f users_backup.sql
```

#### 2. 导入数据
```bash
# 导入SQL文件
psql -U username -d mydb -f mydb_backup.sql

# 导入CSV文件
COPY users (name, email, age) FROM '/tmp/users.csv' DELIMITER ',' CSV HEADER;
```


### 五、常用扩展
PostgreSQL支持丰富扩展，增强功能：  
- **pg_stat_statements**：分析SQL执行性能  
  ```sql
  CREATE EXTENSION pg_stat_statements;
  ```
- **hstore**：键值对类型  
  ```sql
  CREATE EXTENSION hstore;
  ```
- **postgis**：地理信息处理扩展  


### 六、性能优化建议
1. 合理创建索引（避免过度索引），优先使用`EXPLAIN`分析执行计划：  
   ```sql
   EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;
   ```
2. 批量操作使用`COPY`而非`INSERT`循环；  
3. 大表查询避免`SELECT *`，只取需要的列；  
4. 使用连接池（如PgBouncer）优化连接管理。

PostgreSQL的功能远不止于此，其对SQL标准的高度兼容和丰富的扩展生态，使其能满足从简单应用到复杂数据分析的各类需求。