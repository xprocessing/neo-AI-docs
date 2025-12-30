Redis的操作基于**命令集**而非“语法词”，其命令按功能可分为Key操作、数据结构操作、事务/脚本、服务器管理等类别。以下是Redis核心命令的分类及使用方式，覆盖所有常用操作场景：


### 一、通用Key操作命令
用于管理Redis中的键（Key），适用于所有数据类型。

| 命令                | 作用                                                                 | 使用示例                     |
|---------------------|----------------------------------------------------------------------|------------------------------|
| `DEL key [key...]`  | 删除一个或多个键                                                     | `DEL user:1001 product:200`  |
| `EXISTS key`        | 判断键是否存在（返回1存在，0不存在）                                 | `EXISTS name`                |
| `EXPIRE key seconds`| 设置键的过期时间（秒）                                               | `EXPIRE token 3600`          |
| `PEXPIRE key ms`    | 设置过期时间（毫秒）                                                 | `PEXPIRE token 3600000`      |
| `TTL key`           | 查看剩余过期时间（-1永不过期，-2已过期）                             | `TTL token`                  |
| `PTTL key`          | 查看剩余过期时间（毫秒）                                             | `PTTL token`                 |
| `PERSIST key`       | 移除键的过期时间（变为永久）                                         | `PERSIST token`              |
| `KEYS pattern`      | 匹配键（`*`匹配所有，`?`匹配单个字符，生产环境慎用）                 | `KEYS user:*`                |
| `RENAME oldkey newkey` | 重命名键（newkey存在则覆盖）                                        | `RENAME name username`       |
| `RENAMENX oldkey newkey` | 重命名键（newkey不存在时才执行）                                   | `RENAMENX name username`     |
| `TYPE key`          | 查看键的数据类型（string/hash/list/set/zset等）                      | `TYPE user:1001`             |
| `SCAN cursor [MATCH pattern] [COUNT count]` | 迭代键（替代KEYS，安全遍历） | `SCAN 0 MATCH user:* COUNT 10` |


### 二、String（字符串）命令
String是Redis最基础的数据类型，存储字符串、数字或二进制数据（最大512MB）。

| 命令                  | 作用                                                                 | 使用示例                          |
|-----------------------|----------------------------------------------------------------------|-----------------------------------|
| `SET key value [EX seconds] [PX ms] [NX|XX]` | 设置值（NX：键不存在时设，XX：键存在时设）| `SET name Redis EX 3600 NX`       |
| `GET key`             | 获取值                                                               | `GET name`                        |
| `GETSET key value`    | 设置新值并返回旧值（原子操作）                                       | `GETSET counter 0`                |
| `MSET key value [key value...]` | 批量设置值                                                           | `MSET a 1 b 2 c 3`                |
| `MGET key [key...]`   | 批量获取值                                                           | `MGET a b c`                      |
| `INCR key`            | 数值自增1（原子操作，非数字则报错）                                  | `INCR counter`                    |
| `INCRBY key increment`| 数值自增指定步长                                                     | `INCRBY counter 5`                |
| `DECR key`            | 数值自减1                                                             | `DECR counter`                    |
| `DECRBY key decrement`| 数值自减指定步长                                                     | `DECRBY counter 3`                |
| `APPEND key value`    | 追加字符串到原值末尾                                                 | `APPEND name "_test"`             |
| `STRLEN key`          | 获取字符串长度                                                       | `STRLEN name`                     |
| `SUBSTR key start end`| 截取字符串（start/end为索引，负数表示倒数）                          | `SUBSTR name 0 3`                 |


### 三、Hash（哈希）命令
Hash用于存储键值对集合（类似Java的Map），适合存储对象（如用户信息）。

| 命令                          | 作用                                                                 | 使用示例                          |
|-------------------------------|----------------------------------------------------------------------|-----------------------------------|
| `HSET key field value [field value...]` | 设置哈希字段值（批量）| `HSET user:1001 name Alice age 25`|
| `HGET key field`              | 获取哈希字段值                                                       | `HGET user:1001 name`             |
| `HMSET key field value [field value...]` | 批量设置哈希字段（已废弃，用HSET替代）| `HMSET user:1001 email a@test.com`|
| `HMGET key field [field...]`  | 批量获取哈希字段值                                                   | `HMGET user:1001 name age`        |
| `HGETALL key`                 | 获取哈希所有字段和值                                                 | `HGETALL user:1001`               |
| `HDEL key field [field...]`   | 删除哈希字段                                                         | `HDEL user:1001 age`              |
| `HLEN key`                    | 获取哈希字段数量                                                     | `HLEN user:1001`                  |
| `HEXISTS key field`           | 判断哈希字段是否存在                                                 | `HEXISTS user:1001 name`          |
| `HKEYS key`                   | 获取哈希所有字段名                                                   | `HKEYS user:1001`                 |
| `HVALS key`                   | 获取哈希所有字段值                                                   | `HVALS user:1001`                 |
| `HINCRBY key field increment` | 哈希字段数值自增（原子操作）                                         | `HINCRBY user:1001 score 10`      |


### 四、List（列表）命令
List是有序字符串列表（双向链表实现），支持两端插入/弹出，适合队列/栈场景。

| 命令                          | 作用                                                                 | 使用示例                          |
|-------------------------------|----------------------------------------------------------------------|-----------------------------------|
| `LPUSH key value [value...]`  | 左侧插入一个或多个元素                                               | `LPUSH messages Hello Redis`      |
| `RPUSH key value [value...]`  | 右侧插入一个或多个元素                                               | `RPUSH messages World`            |
| `LPOP key`                    | 左侧弹出一个元素                                                     | `LPOP messages`                   |
| `RPOP key`                    | 右侧弹出一个元素                                                     | `RPOP messages`                   |
| `LPUSHX key value`            | 键存在时左侧插入元素                                                 | `LPUSHX messages Test`            |
| `RPUSHX key value`            | 键存在时右侧插入元素                                                 | `RPUSHX messages Test`            |
| `LRANGE key start end`        | 获取指定范围元素（0开始，-1表示最后一个）                            | `LRANGE messages 0 -1`            |
| `LLEN key`                    | 获取列表长度                                                         | `LLEN messages`                   |
| `LREM key count value`        | 删除count个值为value的元素（count>0从左删，<0从右删，=0删所有）       | `LREM messages 2 Hello`           |
| `LINDEX key index`            | 获取指定索引的元素                                                   | `LINDEX messages 1`               |
| `LSET key index value`        | 设置指定索引的元素值                                                 | `LSET messages 0 Hi`              |
| `BLPOP key [key...] timeout`  | 阻塞式左侧弹出（无元素时等待timeout秒，0永久等）                     | `BLPOP messages 5`                |
| `BRPOP key [key...] timeout`  | 阻塞式右侧弹出                                                       | `BRPOP messages 5`                |


### 五、Set（集合）命令
Set是无序、唯一的字符串集合，支持交集、并集、差集操作。

| 命令                          | 作用                                                                 | 使用示例                          |
|-------------------------------|----------------------------------------------------------------------|-----------------------------------|
| `SADD key member [member...]` | 添加一个或多个元素（自动去重）                                       | `SADD tags Java Redis MySQL`      |
| `SMEMBERS key`                | 获取集合所有元素                                                     | `SMEMBERS tags`                   |
| `SISMEMBER key member`        | 判断元素是否在集合中                                                 | `SISMEMBER tags Python`           |
| `SREM key member [member...]` | 删除一个或多个元素                                                   | `SREM tags MySQL`                 |
| `SCARD key`                   | 获取集合元素数量                                                     | `SCARD tags`                      |
| `SINTER key [key...]`         | 求多个集合的交集                                                     | `SINTER tags1 tags2`              |
| `SUNION key [key...]`         | 求多个集合的并集                                                     | `SUNION tags1 tags2`              |
| `SDIFF key [key...]`          | 求多个集合的差集（key1 - key2 - ...）                                | `SDIFF tags1 tags2`               |
| `SMOVE source dest member`    | 将元素从source集合移到dest集合                                       | `SMOVE tags1 tags2 Java`          |
| `SPOP key [count]`            | 随机弹出count个元素（默认1个）                                       | `SPOP tags 2`                     |
| `SRANDMEMBER key [count]`     | 随机获取count个元素（不弹出）                                         | `SRANDMEMBER tags 2`              |


### 六、ZSet（有序集合）命令
ZSet是有序、唯一的集合，元素关联分数（score），按分数排序。

| 命令                                  | 作用                                                                 | 使用示例                          |
|---------------------------------------|----------------------------------------------------------------------|-----------------------------------|
| `ZADD key score member [score member...]` | 添加元素（score为排序依据，member唯一）| `ZADD rank 100 Alice 90 Bob`      |
| `ZRANGE key start end [WITHSCORES]`   | 按score升序获取元素（WITHSCORES返回分数）                             | `ZRANGE rank 0 -1 WITHSCORES`     |
| `ZREVRANGE key start end [WITHSCORES]`| 按score降序获取元素                                                   | `ZREVRANGE rank 0 0 WITHSCORES`   |
| `ZSCORE key member`                   | 获取元素的score                                                      | `ZSCORE rank Alice`               |
| `ZINCRBY key increment member`        | 增加元素的score（原子操作）                                           | `ZINCRBY rank 5 Bob`              |
| `ZCARD key`                           | 获取ZSet元素数量                                                     | `ZCARD rank`                      |
| `ZCOUNT key min max`                  | 统计score在[min,max]范围内的元素数量                                 | `ZCOUNT rank 80 100`              |
| `ZREM key member [member...]`         | 删除元素                                                             | `ZREM rank Bob`                   |
| `ZRANK key member`                    | 获取元素的升序排名（从0开始）                                         | `ZRANK rank Alice`                |
| `ZREVRANK key member`                 | 获取元素的降序排名                                                   | `ZREVRANK rank Alice`             |
| `ZINTERSTORE destkey numkeys key [key...]` | 求多个ZSet的交集并存储到destkey                                     | `ZINTERSTORE rank_inter 2 rank1 rank2` |


### 七、特殊数据类型命令
#### 1. Bitmap（位图）
按位存储，适合布尔值场景（如签到）。

| 命令                  | 作用                                                                 | 使用示例                          |
|-----------------------|----------------------------------------------------------------------|-----------------------------------|
| `SETBIT key offset value` | 设置指定位的值（0/1）| `SETBIT sign:1001 0 1`（第0天签到） |
| `GETBIT key offset`   | 获取指定位的值                                                       | `GETBIT sign:1001 0`              |
| `BITCOUNT key [start end]` | 统计1的位数（start/end为字节索引）| `BITCOUNT sign:1001`              |
| `BITOP op destkey key [key...]` | 位图运算（AND/OR/XOR/NOT）| `BITOP OR sign:total sign:1001 sign:1002` |

#### 2. Geospatial（地理空间）
存储地理位置，支持距离计算（如附近的人）。

| 命令                          | 作用                                                                 | 使用示例                          |
|-------------------------------|----------------------------------------------------------------------|-----------------------------------|
| `GEOADD key lon lat member [lon lat member...]` | 添加地理位置 | `GEOADD city 116.40 39.90 Beijing`|
| `GEOPOS key member [member...]` | 获取地理位置的经纬度                                                 | `GEOPOS city Beijing`             |
| `GEODIST key member1 member2 [unit]` | 计算两点距离（unit：m/km/mi/ft）| `GEODIST city Beijing Shanghai km`|
| `GEORADIUS key lon lat radius unit [WITHCOORD] [WITHDIST]` | 根据坐标搜索附近的位置 | `GEORADIUS city 116.40 39.90 10 km` |

#### 3. HyperLogLog
基数统计（如UV），占用内存极小（最多12KB）。

| 命令                  | 作用                                                                 | 使用示例                          |
|-----------------------|----------------------------------------------------------------------|-----------------------------------|
| `PFADD key element [element...]` | 添加元素到HyperLogLog                                               | `PFADD uv:20240520 user1 user2`   |
| `PFCOUNT key [key...]`| 统计基数（不同元素数量）                                             | `PFCOUNT uv:20240520`             |
| `PFMERGE destkey key [key...]` | 合并多个HyperLogLog到destkey                                         | `PFMERGE uv:total uv:20240520 uv:20240521` |


### 八、事务与脚本命令
#### 1. 事务（Transaction）
批量执行命令，保证原子性（要么全执行，要么全不执行）。

| 命令                  | 作用                                                                 | 使用示例                          |
|-----------------------|----------------------------------------------------------------------|-----------------------------------|
| `MULTI`               | 开启事务                                                             | `MULTI`                           |
| `EXEC`                | 执行事务（提交）| `EXEC`                            |
| `DISCARD`             | 放弃事务（回滚）| `DISCARD`                         |
| `WATCH key [key...]`  | 监视键（事务执行前键被修改则事务取消）                               | `WATCH counter`                   |
| `UNWATCH`             | 取消监视                                                             | `UNWATCH`                         |

#### 2. Lua脚本
通过Lua脚本实现复杂原子操作（替代事务，支持条件判断）。

| 命令                  | 作用                                                                 | 使用示例                          |
|-----------------------|----------------------------------------------------------------------|-----------------------------------|
| `EVAL script numkeys key [key...] arg [arg...]` | 执行Lua脚本 | `EVAL "return redis.call('GET', KEYS[1])" 1 name` |
| `EVALSHA sha1 numkeys key [key...] arg [arg...]` | 执行已缓存的Lua脚本（通过SHA1）| `EVALSHA 123456 1 name`           |
| `SCRIPT LOAD script`  | 缓存Lua脚本并返回SHA1                                                | `SCRIPT LOAD "return redis.call('GET', KEYS[1])"` |


### 九、服务器管理命令
用于管理Redis服务器状态、配置等。

| 命令                  | 作用                                                                 | 使用示例                          |
|-----------------------|----------------------------------------------------------------------|-----------------------------------|
| `PING`                | 测试连接（返回PONG）| `PING`                            |
| `INFO [section]`      | 获取服务器信息（section：server/cluster/memory等）                   | `INFO memory`                     |
| `CONFIG GET parameter`| 获取配置参数                                                         | `CONFIG GET maxmemory`            |
| `CONFIG SET parameter value` | 设置配置参数（无需重启）| `CONFIG SET maxmemory 1GB`        |
| `FLUSHDB`             | 清空当前数据库                                                       | `FLUSHDB`                         |
| `FLUSHALL`            | 清空所有数据库                                                       | `FLUSHALL`                        |
| `SAVE`                | 手动触发RDB持久化（阻塞）| `SAVE`                            |
| `BGSAVE`              | 后台触发RDB持久化（非阻塞）| `BGSAVE`                          |
| `LASTSAVE`            | 获取最后一次RDB持久化时间戳                                          | `LASTSAVE`                        |
| `SHUTDOWN [SAVE/NOSAVE]` | 关闭服务器（可选保存数据）| `SHUTDOWN SAVE`                   |


### 十、集群相关命令（Redis Cluster）
用于管理Redis集群（分片存储，高可用）。

| 命令                          | 作用                                                                 | 使用示例                          |
|-------------------------------|----------------------------------------------------------------------|-----------------------------------|
| `CLUSTER INFO`                | 获取集群信息                                                         | `CLUSTER INFO`                    |
| `CLUSTER NODES`               | 查看集群节点列表                                                     | `CLUSTER NODES`                   |
| `CLUSTER MEET ip port`        | 将节点加入集群                                                       | `CLUSTER MEET 127.0.0.1 6380`     |
| `CLUSTER ADDSLOTS slot [slot...]` | 分配哈希槽给节点                                                     | `CLUSTER ADDSLOTS 0-5460`         |
| `CLUSTER REPLICATE node-id`   | 将当前节点设为指定节点的从节点                                       | `CLUSTER REPLICATE abc123`        |


### 总结
Redis的命令按数据类型和功能分类，需结合业务场景选择：  
- 简单键值用**String**，对象存储用**Hash**，有序列表用**List**，去重集合用**Set**，排序场景用**ZSet**；  
- 特殊场景（签到、地理位置、UV统计）用Bitmap/Geospatial/HyperLogLog；  
- 并发控制用事务或Lua脚本，集群部署用Cluster命令。  

所有命令均通过`redis-cli`或客户端SDK（如Java的Jedis/Spring Data Redis）执行，语法简洁且支持原子操作，是Redis高性能的核心保障。