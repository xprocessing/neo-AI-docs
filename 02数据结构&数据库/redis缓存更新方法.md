你想解决的核心问题是：当数据库中的数据发生更新后，如何让 Redis 缓存中的对应数据也能及时同步更新，避免出现缓存数据与数据库数据不一致的情况。

这是实际开发中非常常见的缓存一致性问题，我会为你介绍几种主流且实用的解决方案，从简单到复杂，你可以根据自己的业务场景选择。

### 一、方案1：更新数据库后主动更新/删除缓存（最常用）
这是最简单、最直接的方案，核心思路是在执行数据库更新操作（增/删/改）的代码逻辑中，同步更新或删除 Redis 中的对应缓存。

#### 实现思路
1. 执行数据库的更新操作（UPDATE/INSERT/DELETE）。
2. 操作成功后，**删除** 对应缓存（推荐）或 **更新** 缓存。
   - 删除缓存：下次查询时会从数据库重新加载最新数据到 Redis，实现最终一致。
   - 更新缓存：直接把最新数据写入 Redis，实时性更高，但要注意代码冗余。

#### 代码示例（Python + Redis + MySQL）
```python
import redis
import pymysql

# 初始化 Redis 连接
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
# 初始化 MySQL 连接
db_conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='test_db'
)
cursor = db_conn.cursor()

def update_user_info(user_id, new_name):
    """更新用户信息，并同步更新缓存"""
    try:
        # 1. 更新数据库
        update_sql = "UPDATE user SET name = %s WHERE id = %s"
        cursor.execute(update_sql, (new_name, user_id))
        db_conn.commit()
        
        # 2. 删除对应的 Redis 缓存（推荐）
        cache_key = f"user:{user_id}"
        redis_client.delete(cache_key)
        
        # （可选）也可以直接更新缓存
        # new_user_info = get_user_from_db(user_id)  # 重新查询最新数据
        # redis_client.set(cache_key, json.dumps(new_user_info), ex=3600)
        
        return True
    except Exception as e:
        db_conn.rollback()
        print(f"更新失败：{e}")
        return False
    finally:
        cursor.close()
        db_conn.close()

# 调用示例
update_user_info(1, "新名字")
```

#### 注意事项
- 必须保证 **先更新数据库，后操作缓存**：如果先删缓存再更数据库，在高并发场景下可能出现“缓存击穿”（另一个请求在数据库更新完成前查询，会把旧数据重新写入缓存）。
- 适合大多数中小规模业务，实现简单、维护成本低。

### 二、方案2：使用缓存过期时间（兜底方案）
即使做了主动更新，也建议给缓存设置过期时间（TTL），作为“兜底”方案——如果因代码bug、网络异常等原因导致缓存未更新，过期后会自动失效，重新从数据库加载最新数据。

```python
# 设置缓存时指定过期时间（例如 1 小时）
redis_client.set(f"user:{user_id}", json.dumps(user_info), ex=3600)
```

### 三、方案3：基于消息队列的异步更新（高并发场景）
对于高并发、高可用要求的场景，可通过消息队列（如 RabbitMQ、Kafka）实现“数据库更新 → 发消息 → 消费消息更新缓存”的异步流程，避免更新数据库时同步操作缓存导致接口响应变慢。

#### 实现流程
1. 业务系统更新数据库后，向消息队列发送一条“数据更新”消息（包含数据ID、操作类型等）。
2. 独立的消费服务监听消息队列，收到消息后，删除/更新 Redis 中对应的缓存。
3. （可选）增加重试机制，确保消息消费失败后能重新处理，避免缓存不一致。

#### 核心代码示例（生产者）
```python
def update_user_info_with_mq(user_id, new_name):
    try:
        # 1. 更新数据库
        update_sql = "UPDATE user SET name = %s WHERE id = %s"
        cursor.execute(update_sql, (new_name, user_id))
        db_conn.commit()
        
        # 2. 发送消息到 MQ（示例用 RabbitMQ）
        import pika
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='cache_update_queue', durable=True)
        # 消息内容：用户ID + 操作类型
        message = f"{user_id}:update"
        channel.basic_publish(
            exchange='',
            routing_key='cache_update_queue',
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # 持久化消息
        )
        connection.close()
        return True
    except Exception as e:
        db_conn.rollback()
        print(f"更新失败：{e}")
        return False
```

#### 核心代码示例（消费者）
```python
def consume_cache_update():
    import pika
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='cache_update_queue', durable=True)
    
    def callback(ch, method, properties, body):
        # 解析消息
        user_id, op = body.decode().split(':')
        # 删除对应缓存
        cache_key = f"user:{user_id}"
        redis_client.delete(cache_key)
        # 确认消息已消费
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='cache_update_queue', on_message_callback=callback)
    channel.start_consuming()

# 启动消费者
consume_cache_update()
```

### 四、方案4：数据库binlog同步（终极方案）
对于超大规模、多系统共享数据的场景，可通过监听数据库的 binlog（二进制日志）来感知数据变化，自动同步到 Redis。

#### 实现思路
1. 使用 Canal（阿里开源）、MaxWell 等工具监听 MySQL 的 binlog。
2. 当数据库数据更新时，binlog 工具捕获到变更事件，解析出数据ID和变更内容。
3. 调用 Redis API 删除/更新对应缓存。

#### 优势
- 无需侵入业务代码，对业务系统无耦合。
- 能捕获所有数据库变更（包括手动改库、其他系统改库），一致性最高。
- 适合跨系统、大规模的缓存同步场景。

### 总结
1. **中小业务首选**：更新数据库后 **主动删除/更新缓存** + 设置缓存过期时间，实现简单、成本低。
2. **高并发场景**：使用 **消息队列异步更新**，避免同步操作缓存影响接口性能。
3. **超大规模/跨系统场景**：基于 **数据库binlog同步**（Canal），一致性和通用性最优。
4. 核心原则：无论用哪种方案，都要保证 **“先更数据库，后操作缓存”**，并设置缓存过期时间作为兜底，避免缓存永久不一致。