Redis是一款高性能的开源内存数据库，支持多种数据结构、持久化、分布式等特性，广泛应用于缓存、消息队列、分布式锁等场景。以下从**核心数据结构、常用命令、持久化、高可用、Java客户端使用**等方面详细介绍Redis的用法：


### 一、核心数据结构及常用命令
Redis支持String、Hash、List、Set、ZSet（Sorted Set）等基础数据结构，以及Bitmap、HyperLogLog、Geospatial等特殊类型，每种类型适配不同场景。

#### 1. String（字符串）
最基础的数据类型，可存储字符串、数字、二进制数据（如图片），最大支持512MB。  
**常用命令**：
```bash
SET key value [EX seconds] [PX milliseconds]  # 设置值，可选过期时间
GET key                                       # 获取值
INCR key                                      # 数值自增1（原子操作）
INCRBY key step                               # 数值自增指定步长
APPEND key value                              # 追加字符串
STRLEN key                                    # 获取字符串长度
```
**场景**：缓存热点数据、计数器（阅读量、点赞数）、会话存储。

#### 2. Hash（哈希）
键值对集合，适合存储对象（如用户信息、商品详情），可单独操作字段，节省内存。  
**常用命令**：
```bash
HSET key field value                          # 设置哈希字段值
HGET key field                                # 获取哈希字段值
HMSET key field1 value1 field2 value2         # 批量设置字段
HMGET key field1 field2                       # 批量获取字段
HGETALL key                                   # 获取所有字段和值
HDEL key field                                # 删除字段
HLEN key                                      # 获取字段数量
```
**场景**：存储对象（如`user:1001`的name、age、email）。

#### 3. List（列表）
有序字符串列表，基于双向链表实现，支持两端操作，可作为队列/栈。  
**常用命令**：
```bash
LPUSH key value1 value2                       # 左侧插入元素
RPUSH key value1 value2                       # 右侧插入元素
LPOP key                                      # 左侧弹出元素
RPOP key                                      # 右侧弹出元素
LRANGE key start end                          # 获取指定范围元素（0到-1表示全部）
LLEN key                                      # 获取列表长度
```
**场景**：消息队列（如秒杀订单队列）、最新消息列表。

#### 4. Set（集合）
无序且唯一的字符串集合，支持交集、并集、差集操作。  
**常用命令**：
```bash
SADD key member1 member2                      # 添加元素
SMEMBERS key                                  # 获取所有元素
SISMEMBER key member                          # 判断元素是否存在
SREM key member                               # 删除元素
SINTER key1 key2                              # 求交集
SUNION key1 key2                              # 求并集
SDIFF key1 key2                               # 求差集
SCARD key                                     # 获取集合大小
```
**场景**：标签系统（如用户兴趣标签）、共同好友。

#### 5. ZSet（有序集合）
有序且唯一的集合，每个元素关联分数（score），按分数排序。  
**常用命令**：
```bash
ZADD key score1 member1 score2 member2        # 添加元素（分数+成员）
ZRANGE key start end [WITHSCORES]             # 按分数升序获取元素（带分数）
ZREVRANGE key start end [WITHSCORES]          # 按分数降序获取元素
ZSCORE key member                             # 获取元素分数
ZINCRBY key increment member                  # 增加元素分数
ZCARD key                                     # 获取元素数量
```
**场景**：排行榜（如商品销量榜、用户积分榜）。

#### 6. 特殊类型
- **Bitmap（位图）**：按位存储，适合布尔值场景（如用户签到）。  
  命令：`SETBIT key offset value`、`GETBIT key offset`、`BITCOUNT key`。  
- **Geospatial（地理空间）**：存储地理位置，支持距离计算（如附近的人）。  
  命令：`GEOADD key lon lat member`、`GEORADIUS key lon lat radius m/km`。  
- **HyperLogLog**：基数统计，占用内存极小（如UV统计）。  
  命令：`PFADD key element`、`PFCOUNT key`。


### 二、缓存常用操作
#### 1. 设置过期时间
Redis支持为Key设置过期时间，自动删除过期数据：
```bash
EXPIRE key seconds                # 设置过期时间（秒）
PEXPIRE key milliseconds          # 设置过期时间（毫秒）
SET key value EX 3600             # 设置值并指定过期时间（推荐）
TTL key                           # 查看剩余过期时间（-1永不过期，-2已过期）
```

#### 2. 事务与原子操作
Redis事务通过`MULTI`/`EXEC`实现批量操作，保证原子性（要么全执行，要么全不执行）：
```bash
MULTI                             # 开启事务
SET key1 value1
INCR key2
EXEC                             # 执行事务
```
**注意**：事务中某条命令报错，其他命令仍会执行（Redis事务不支持回滚）。

#### 3. Lua脚本
通过Lua脚本实现复杂原子操作（如分布式锁）：
```lua
-- 释放分布式锁的Lua脚本
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
```


### 三、持久化机制
Redis数据默认存储在内存中，持久化可避免数据丢失，支持两种方式：

#### 1. RDB（快照）
在指定时间间隔内生成数据快照（.rdb文件），适合备份和灾难恢复。  
**配置**：
```conf
save 900 1        # 900秒内至少1次修改则触发快照
save 300 10       # 300秒内至少10次修改则触发快照
save 60 10000     # 60秒内至少10000次修改则触发快照
```
**优点**：恢复速度快；**缺点**：可能丢失最近的数据。

#### 2. AOF（追加日志）
记录所有写命令到日志文件（.aof文件），重启时重放命令恢复数据。  
**配置**：
```conf
appendonly yes                    # 开启AOF
appendfsync everysec              # 每秒同步一次（平衡性能与安全性）
```
**优点**：数据安全性高；**缺点**：文件体积大，恢复速度慢。

#### 3. 混合持久化（Redis 4.0+）
结合RDB和AOF，快照+增量命令日志，兼顾性能与安全性。


### 四、高可用与分布式
#### 1. 主从复制
实现数据备份和读写分离：
- **主库（Master）**：处理写操作，同步数据到从库；  
- **从库（Slave）**：处理读操作，从主库同步数据。  
**配置**（从库）：
```conf
replicaof master_ip master_port  # Redis 5.0+用replicaof，旧版用slaveof
```

#### 2. 哨兵模式（Sentinel）
监控主从库，自动故障转移（主库宕机时选举新主库）。  
**配置示例**：
```conf
sentinel monitor mymaster 127.0.0.1 6379 2  # 监控主库，2个哨兵同意则判定故障
sentinel down-after-milliseconds mymaster 30000  # 30秒无响应则标记为宕机
```

#### 3. 集群模式（Cluster）
分片存储数据，支持水平扩展（最多16384个哈希槽），每个节点负责部分槽位。  
**创建集群**：
```bash
redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381 --cluster-replicas 1
```


### 五、Java客户端使用（以Spring Data Redis为例）
Spring Boot集成Redis步骤：

#### 1. 引入依赖
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

#### 2. 配置Redis连接
```yaml
spring:
  redis:
    host: localhost
    port: 6379
    password:  # 无密码则留空
    database: 0  # 默认数据库
    lettuce:
      pool:
        max-active: 8  # 最大连接数
        max-idle: 8    # 最大空闲连接
        min-idle: 0    # 最小空闲连接
```

#### 3. 常用操作示例
```java
@Autowired
private RedisTemplate<String, Object> redisTemplate;

// String操作
public void stringOps() {
    ValueOperations<String, Object> ops = redisTemplate.opsForValue();
    ops.set("name", "Redis", 1, TimeUnit.HOURS);  // 设置值并过期1小时
    String name = (String) ops.get("name");
    ops.increment("count");  // 自增
}

// Hash操作
public void hashOps() {
    HashOperations<String, String, Object> ops = redisTemplate.opsForHash();
    ops.put("user:1001", "name", "Alice");
    ops.put("user:1001", "age", 25);
    Map<String, Object> user = ops.entries("user:1001");
}

// List操作
public void listOps() {
    ListOperations<String, Object> ops = redisTemplate.opsForList();
    ops.leftPush("messages", "Hello");
    ops.rightPush("messages", "Redis");
    List<Object> messages = ops.range("messages", 0, -1);
}

// 分布式锁
public boolean tryLock(String lockKey, String requestId, long expireTime) {
    return redisTemplate.opsForValue().setIfAbsent(lockKey, requestId, expireTime, TimeUnit.SECONDS);
}
```


### 六、常见问题与优化
#### 1. 缓存穿透
**问题**：请求不存在的Key，穿透到数据库。  
**解决**：缓存空值、布隆过滤器拦截无效Key。

#### 2. 缓存击穿
**问题**：热点Key过期瞬间，大量请求穿透到数据库。  
**解决**：热点Key永不过期、互斥锁更新缓存。

#### 3. 缓存雪崩
**问题**：大量Key同时过期或Redis宕机，请求全部穿透到数据库。  
**解决**：过期时间随机化、Redis集群高可用、服务降级。

#### 4. 性能优化
- 避免大Key（拆分大Hash/List）；  
- 使用Pipeline批量操作；  
- 合理设置过期时间，定期清理无效Key；  
- 开启Redis持久化时选择合适策略。


### 七、总结
Redis凭借高性能、丰富的数据结构和灵活的部署模式，成为分布式系统中不可或缺的组件。掌握其核心数据结构、命令和最佳实践，可有效解决缓存、并发、数据存储等问题，提升系统性能和稳定性。