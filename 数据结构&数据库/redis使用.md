Redis是一款高性能的键值对NoSQL数据库，支持多种数据结构，常用于缓存、分布式锁、消息队列等场景。以下从**核心命令、数据结构用法、实战场景、Java集成**等方面介绍Redis的常用用法：


### 一、基础命令操作
#### 1. 连接与基础管理
```bash
redis-cli                    # 连接本地Redis（默认6379端口）
redis-cli -h 127.0.0.1 -p 6379 -a password  # 连接远程Redis
PING                         # 测试连接（返回PONG表示正常）
SELECT 1                     # 切换数据库（Redis默认16个库，0-15）
FLUSHDB                      # 清空当前数据库
FLUSHALL                     # 清空所有数据库
```

#### 2. 通用Key操作
```bash
SET key value [EX seconds]   # 设置键值对，可选过期时间
GET key                      # 获取值
DEL key                      # 删除键
EXISTS key                   # 判断键是否存在
EXPIRE key 60                # 设置键过期时间（60秒）
TTL key                      # 查看剩余过期时间（-1永不过期，-2已过期）
KEYS *                       # 匹配所有键（生产环境慎用，性能差）
RENAME oldkey newkey         # 重命名键
```


### 二、核心数据结构用法
#### 1. String（字符串）
最基础类型，存储字符串、数字、二进制数据（最大512MB）。  
```bash
SET name "Redis"             # 设置字符串
GET name                     # 获取值 → "Redis"
INCR counter                 # 数字自增（原子操作）→ 1
INCRBY counter 5             # 自增指定步长 → 6
APPEND name "_test"          # 追加字符串 → "Redis_test"
STRLEN name                  # 获取长度 → 10
```
**场景**：缓存热点数据、计数器、会话存储。

#### 2. Hash（哈希）
存储对象（键值对集合），可单独操作字段，节省内存。  
```bash
HSET user:1001 name "Alice" age 25  # 设置用户字段
HGET user:1001 name                 # 获取单个字段 → "Alice"
HMGET user:1001 name age            # 批量获取字段 → ["Alice", "25"]
HGETALL user:1001                   # 获取所有字段和值 → ["name","Alice","age","25"]
HDEL user:1001 age                  # 删除字段
HLEN user:1001                      # 字段数量 → 1
```
**场景**：存储用户信息、商品详情。

#### 3. List（列表）
有序字符串列表，基于双向链表实现，支持两端操作。  
```bash
LPUSH messages "Hello"      # 左侧插入 → ["Hello"]
RPUSH messages "World"      # 右侧插入 → ["Hello", "World"]
LPOP messages               # 左侧弹出 → "Hello"
RPOP messages               # 右侧弹出 → "World"
LRANGE messages 0 -1        # 获取所有元素（0到-1表示全部）
LLEN messages               # 列表长度 → 0
```
**场景**：消息队列、最新消息列表。

#### 4. Set（集合）
无序、唯一的字符串集合，支持交集/并集/差集。  
```bash
SADD tags "Java" "Redis"    # 添加元素 → 2
SMEMBERS tags               # 获取所有元素 → ["Java", "Redis"]
SISMEMBER tags "Python"     # 判断元素是否存在 → 0（不存在）
SINTER tags1 tags2          # 求两个集合的交集
SUNION tags1 tags2          # 求并集
SCARD tags                  # 集合大小 → 2
```
**场景**：标签系统、共同好友。

#### 5. ZSet（有序集合）
有序、唯一的集合，元素关联分数（score），按分数排序。  
```bash
ZADD rank 100 "Alice" 90 "Bob"  # 添加元素（分数+成员）
ZRANGE rank 0 -1 WITHSCORES     # 升序获取（带分数）→ ["Bob",90,"Alice",100]
ZREVRANGE rank 0 0              # 降序获取第一名 → ["Alice"]
ZSCORE rank "Alice"             # 获取分数 → 100
ZINCRBY rank 10 "Bob"           # 分数增加10 → 100
```
**场景**：排行榜、用户积分系统。


### 三、实战场景用法
#### 1. 缓存热点数据
```bash
# 缓存商品信息（设置1小时过期）
SET product:1001 '{"id":1001,"name":"Redis实战","price":59.9}' EX 3600
GET product:1001  # 获取缓存数据
```

#### 2. 分布式锁
利用`SETNX`（原子操作）实现：
```bash
# 获取锁（expire避免死锁）
SET lock:order:1001 "requestId" NX EX 30
# 释放锁（需验证requestId，避免误删）
if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end
```

#### 3. 限流（接口访问次数限制）
```bash
# 接口每分钟访问次数限制
INCR api:limit:user1:2024052010
EXPIRE api:limit:user1:2024052010 60  # 60秒过期
GET api:limit:user1:2024052010       # 获取当前访问次数
```

#### 4. 消息队列（List实现）
```bash
# 生产者发送消息
LPUSH queue:order "order1001"
# 消费者消费消息
RPOP queue:order
```


### 四、Java集成Redis（Spring Boot）
#### 1. 依赖引入
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

#### 2. 配置Redis
```yaml
spring:
  redis:
    host: localhost
    port: 6379
    password:  # 无密码则留空
    database: 0
```

#### 3. 常用操作示例
```java
@Autowired
private RedisTemplate<String, Object> redisTemplate;

// String操作
public void stringOps() {
    ValueOperations<String, Object> ops = redisTemplate.opsForValue();
    ops.set("name", "Redis", 1, TimeUnit.HOURS); // 设置值+过期时间
    String name = (String) ops.get("name");
}

// Hash操作
public void hashOps() {
    HashOperations<String, String, Object> ops = redisTemplate.opsForHash();
    ops.put("user:1001", "name", "Alice");
    ops.put("user:1001", "age", 25);
    Map<String, Object> user = ops.entries("user:1001");
}

// ZSet排行榜
public void zsetOps() {
    ZSetOperations<String, Object> ops = redisTemplate.opsForZSet();
    ops.add("rank", "Alice", 100);
    ops.add("rank", "Bob", 90);
    Set<Object> top1 = ops.reverseRange("rank", 0, 0); // 第一名
}
```


### 五、高级特性用法
#### 1. 持久化配置
- **RDB**：定时生成数据快照（性能优，可能丢数据）  
  配置：`save 900 1`（900秒内1次修改触发快照）  
- **AOF**：记录所有写命令（数据安全，文件较大）  
  配置：`appendonly yes` + `appendfsync everysec`（每秒同步）

#### 2. 主从复制
从库配置：`replicaof 主库IP 主库端口`（Redis 5.0+），实现读写分离。

#### 3. 集群模式
```bash
# 创建Redis集群（3主3从）
redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381 --cluster-replicas 1
```


### 六、注意事项
1. **避免大Key**：拆分大Hash/List，防止阻塞Redis；  
2. **合理设置过期时间**：防止内存溢出；  
3. **防范缓存问题**：缓存穿透（布隆过滤器）、缓存击穿（互斥锁）、缓存雪崩（过期时间随机化）；  
4. **原子操作**：利用Redis命令原子性（如`INCR`、`SETNX`）解决并发问题。

Redis的用法核心是结合其数据结构特性，适配不同业务场景，通过高效的命令和配置实现性能优化。