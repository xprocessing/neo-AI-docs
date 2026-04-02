### Redis 核心解析
Redis（Remote Dictionary Server）是一款**开源的高性能键值对内存数据库**，兼顾内存存储的高性能和磁盘持久化的可靠性，支持丰富的数据结构，广泛应用于缓存、分布式锁、消息队列、排行榜等场景。

---

## 一、核心特性
1. **内存优先 + 持久化**：数据默认存储在内存中（读写速度达10万+/s），支持RDB、AOF两种持久化方式，避免数据丢失。
2. **丰富的数据结构**：除基础字符串外，原生支持Hash、List、Set、ZSet等，满足复杂业务场景。
3. **原子操作**：所有命令原子性执行，支持事务、Lua脚本进一步保证复杂逻辑的原子性。
4. **高可用**：支持主从复制、哨兵（Sentinel）、集群（Cluster），实现故障自动转移和水平扩展。
5. **轻量易用**：单进程模型（避免线程切换开销），命令简洁，支持多种客户端（Java/Python/Go等）。

---

## 二、核心数据结构（附场景+命令）
| 数据结构 | 核心特点                | 典型场景                  | 常用命令                     |
|----------|-------------------------|---------------------------|------------------------------|
| String   | 字符串/数字/二进制，最大512MB | 缓存、计数器、分布式锁    | set/get/incr/decr/mset/nx    |
| Hash     | 键值对集合，适合存储对象    | 用户信息、商品属性        | hset/hget/hgetall/hdel/hmget |
| List     | 双向链表，有序可重复        | 消息队列、最新列表        | lpush/rpush/lpop/rpop/lrange |
| Set      | 无序不重复集合，支持交集/并集 | 标签、好友去重、抽奖      | sadd/smembers/sinter/sunion  |
| ZSet     | 有序不重复（按分数排序）     | 排行榜、延时队列          | zadd/zrange/zrevrange/zscore |
| 扩展结构 | BitMap（位图）/HyperLogLog/Geo | 签到、UV统计、附近的人    | setbit/bitcount/pfadd/geoadd |

### 示例命令（Redis-CLI）
```bash
# 1. String：计数器（文章阅读量）
set article:1001:read 0
incr article:1001:read  # 原子自增，返回1
get article:1001:read   # 输出"1"

# 2. Hash：存储用户信息
hset user:1 name "张三" age 25 gender "男"
hgetall user:1  # 输出 {name:张三, age:25, gender:男}

# 3. ZSet：排行榜（用户积分）
zadd score_rank 100 "张三" 90 "李四" 95 "王五"
zrevrange score_rank 0 -1 withscores  # 降序输出排行（张三100 > 王五95 > 李四90）
```

---

## 三、关键机制
### 1. 持久化
| 方式 | 原理                          | 优点                  | 缺点                  |
|------|-------------------------------|-----------------------|-----------------------|
| RDB  | 定时生成内存数据的快照文件     | 文件小、恢复速度快    | 可能丢失最近数据      |
| AOF  | 记录所有写命令，重启时重放     | 数据更安全（秒级持久化） | 文件大、恢复速度慢    |
| 混合持久化 | RDB + AOF 结合（Redis 4.0+） | 兼顾速度和安全性      | -                     |

### 2. 高可用方案
- **主从复制**：1主N从，主库写、从库读（读写分离），从库同步主库数据。
- **哨兵（Sentinel）**：监控主从节点，主库故障时自动将从库升级为主库，解决主从的“人工故障转移”问题。
- **集群（Cluster）**：将数据分片存储在多个节点（默认16384个槽位），支持水平扩展，单集群最大1000+节点。

### 3. 缓存常见问题与解决方案
| 问题         | 现象                                  | 解决方案                                  |
|--------------|---------------------------------------|-------------------------------------------|
| 缓存穿透     | 请求不存在的key，直接打穿到数据库      | 布隆过滤器拦截、缓存空值（设置短期过期）  |
| 缓存击穿     | 热点key过期瞬间，大量请求打数据库      | 热点key永不过期、互斥锁（nx命令）          |
| 缓存雪崩     | 大量key同时过期，数据库压力骤增        | 过期时间加随机值、主从+哨兵、熔断降级     |
| 缓存与DB一致性 | 缓存和数据库数据不一致                | 先更DB再删缓存（延迟双删）、分布式事务    |

---

## 四、典型应用场景
1. **缓存**：存储热点数据（如商品详情、用户信息），减轻数据库压力（核心场景）。
2. **分布式锁**：通过 `set key value nx ex 30` 实现（nx=仅当key不存在时设置，ex=自动过期避免死锁）。
3. **计数器**：点赞数、阅读量、接口限流（incr原子自增）。
4. **排行榜**：基于ZSet实现实时排名（如游戏战力、商品销量）。
5. **消息队列**：List（简单队列）、Stream（支持消费组，替代kafka轻量场景）。
6. **限流**：令牌桶/漏桶算法（incr+expire控制单位时间请求数）。

---

## 五、进阶优化
1. **内存优化**：
   - 合理设置过期时间，避免内存泄漏；
   - 用Hash存储对象（比多个String节省内存）；
   - 禁用大key（如10万元素的List），避免阻塞Redis。
2. **性能调优**：
   - 关闭不必要的持久化（纯缓存场景）；
   - 调整内存淘汰策略（如volatile-lru：淘汰过期key中最近最少使用的）；
   - 使用管道（Pipeline）批量执行命令，减少网络IO。
3. **分布式锁最佳实践**：
   ```bash
   # 正确实现：原子设置key+过期时间，避免死锁
   set lock:order 123 nx ex 30
   # 释放锁（Lua脚本保证原子性，避免误删其他客户端的锁）
   if redis.call('get',KEYS[1]) == ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end
   ```

---

## 六、快速入门
### 1. 安装（Linux）
```bash
# 下载解压
wget https://download.redis.io/releases/redis-7.2.4.tar.gz
tar -zxvf redis-7.2.4.tar.gz && cd redis-7.2.4
# 编译安装
make && make install
# 启动（前台）
redis-server
# 启动（后台，修改redis.conf：daemonize yes）
redis-server /etc/redis.conf
# 连接客户端
redis-cli
```

### 2. 客户端示例（Java - Spring Boot）
```java
// 1. 引入依赖
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>

// 2. 使用RedisTemplate
@Autowired
private StringRedisTemplate redisTemplate;

// 缓存用户信息
public void cacheUser(Long userId, User user) {
    redisTemplate.opsForValue().set("user:" + userId, JSON.toJSONString(user), 1, TimeUnit.HOURS);
}

// 获取缓存
public User getCachedUser(Long userId) {
    String json = redisTemplate.opsForValue().get("user:" + userId);
    return JSON.parseObject(json, User.class);
}
```

---

## 七、进阶方向
- Lua脚本：封装复杂原子逻辑（如分布式锁释放、批量操作）；
- Redis Stream：支持消费组、消息确认，替代List做可靠消息队列；
- Redis Cluster 分片原理：槽位映射、迁移与重分片；
- 内存模型：压缩列表、跳表等底层结构优化；
- 监控与运维：Redis-cli、Redis Insight、Prometheus+Grafana。

Redis的核心优势是**高性能+灵活的数据结构+高可用**，核心设计思路是“把合适的场景交给合适的工具”——用内存解决性能问题，用持久化和集群解决可靠性/扩展性问题。