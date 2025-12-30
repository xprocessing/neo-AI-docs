PHP中使用Redis主要通过**Redis扩展**（`phpredis`）或**Predis库**（纯PHP实现），以下是两种方式的详细用法：


### 一、环境准备
#### 1. 安装phpredis扩展（推荐，性能更高）
- **Linux**：  
  ```bash
  # 安装依赖
  pecl install redis
  # 配置php.ini（添加扩展）
  echo "extension=redis.so" >> /etc/php.ini
  # 重启Web服务（如nginx/apache）或php-fpm
  ```

- **Windows**：  
  下载对应PHP版本的`php_redis.dll`（[PECL官网](https://pecl.php.net/package/redis)），放入`ext`目录，在`php.ini`中添加`extension=php_redis.dll`，重启服务。

#### 2. 安装Predis（纯PHP库，无需扩展）
通过Composer安装：  
```bash
composer require predis/predis
```


### 二、phpredis扩展用法
#### 1. 连接Redis
```php
// 创建Redis实例
$redis = new Redis();

// 连接本地Redis（默认端口6379）
$redis->connect('127.0.0.1', 6379);

// 带密码连接（若设置了密码）
// $redis->auth('your_password');

// 选择数据库（默认0库）
$redis->select(1);

// 测试连接
echo $redis->ping(); // 返回PONG表示连接成功
```

#### 2. 核心数据结构操作
##### （1）String（字符串）
```php
// 设置值（可选过期时间）
$redis->set('name', 'Redis');
$redis->setex('token', 3600, 'abc123'); // 1小时过期

// 获取值
echo $redis->get('name'); // 输出Redis

// 原子自增/自减
$redis->incr('counter');       // 自增1
$redis->incrBy('counter', 5);  // 自增5
$redis->decr('counter');       // 自减1

// 追加字符串
$redis->append('name', '_test'); // name变为Redis_test
```

##### （2）Hash（哈希）
```php
// 设置哈希字段
$redis->hSet('user:1001', 'name', 'Alice');
$redis->hSet('user:1001', 'age', 25);

// 批量设置
$redis->hMSet('user:1001', [
    'email' => 'alice@test.com',
    'city' => 'Beijing'
]);

// 获取字段值
echo $redis->hGet('user:1001', 'name'); // Alice

// 获取所有字段和值
$user = $redis->hGetAll('user:1001');
print_r($user); // 输出所有字段

// 删除字段
$redis->hDel('user:1001', 'age');
```

##### （3）List（列表）
```php
// 左侧/右侧插入元素
$redis->lPush('messages', 'Hello');
$redis->rPush('messages', 'World');

// 左侧/右侧弹出元素
echo $redis->lPop('messages'); // Hello
echo $redis->rPop('messages'); // World

// 获取列表范围元素
$list = $redis->lRange('messages', 0, -1); // 获取所有元素
```

##### （4）Set（集合）
```php
// 添加元素
$redis->sAdd('tags', 'Java', 'Redis', 'PHP');

// 获取所有元素
$tags = $redis->sMembers('tags');

// 判断元素是否存在
var_dump($redis->sIsMember('tags', 'PHP')); // true

// 交集/并集
$redis->sAdd('tags2', 'Redis', 'MySQL');
$inter = $redis->sInter('tags', 'tags2'); // 交集：Redis
```

##### （5）ZSet（有序集合）
```php
// 添加元素（分数+成员）
$redis->zAdd('rank', 100, 'Alice', 90, 'Bob');

// 按分数升序/降序获取
$rankAsc = $redis->zRange('rank', 0, -1, true); // 带分数
$rankDesc = $redis->zRevRange('rank', 0, -1, true);

// 获取元素分数
echo $redis->zScore('rank', 'Alice'); // 100
```

#### 3. 通用Key操作
```php
// 删除键
$redis->del('name');

// 设置过期时间
$redis->expire('token', 60); // 60秒过期

// 判断键是否存在
var_dump($redis->exists('name')); // false

// 查看键类型
echo $redis->type('user:1001'); // hash
```

#### 4. 关闭连接
```php
$redis->close();
```


### 三、Predis库用法
Predis是纯PHP实现的Redis客户端，无需扩展，用法类似phpredis：

#### 1. 连接Redis
```php
require 'vendor/autoload.php'; // 引入Composer自动加载

$client = new Predis\Client([
    'scheme' => 'tcp',
    'host'   => '127.0.0.1',
    'port'   => 6379,
    'password' => 'your_password', // 可选
    'database' => 1, // 可选
]);

// 测试连接
echo $client->ping(); // PONG
```

#### 2. 数据操作（示例）
```php
// String操作
$client->set('name', 'Predis');
echo $client->get('name'); // Predis

// Hash操作
$client->hSet('user:1002', 'name', 'Bob');
$user = $client->hGetAll('user:1002');

// ZSet操作
$client->zAdd('rank', ['Charlie' => 80]);
```


### 四、实战场景示例
#### 1. 缓存热点数据
```php
// 查询商品信息（先查缓存，再查数据库）
function getProduct($id) {
    $redis = new Redis();
    $redis->connect('127.0.0.1', 6379);
    
    $key = "product:$id";
    // 查缓存
    if ($redis->exists($key)) {
        return json_decode($redis->get($key), true);
    }
    
    // 缓存未命中，查数据库（示例）
    $product = [
        'id' => $id,
        'name' => 'Redis实战',
        'price' => 59.9
    ];
    
    // 存入缓存（1小时过期）
    $redis->setex($key, 3600, json_encode($product));
    return $product;
}

print_r(getProduct(1001));
```

#### 2. 分布式锁
```php
// 获取锁
function lock($key, $expire = 30) {
    $redis = new Redis();
    $redis->connect('127.0.0.1', 6379);
    $requestId = uniqid(); // 唯一标识
    // SETNX + EXPIRE原子操作（Redis 2.6.12+支持set的NX/EX参数）
    $result = $redis->set($key, $requestId, ['nx', 'ex' => $expire]);
    return $result ? $requestId : false;
}

// 释放锁
function unlock($key, $requestId) {
    $redis = new Redis();
    $redis->connect('127.0.0.1', 6379);
    // Lua脚本保证原子性
    $script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end";
    return $redis->eval($script, [$key, $requestId], 1);
}

// 使用锁
$lockKey = 'order:lock:1001';
$requestId = lock($lockKey);
if ($requestId) {
    // 执行业务逻辑（如扣减库存）
    echo "处理订单...";
    unlock($lockKey, $requestId);
} else {
    echo "锁被占用，请稍后重试";
}
```


### 五、注意事项
1. **连接池**：生产环境建议使用连接池（如`phpredis`的`RedisCluster`或第三方连接池工具），避免频繁创建/关闭连接；  
2. **序列化**：存储复杂数据（如数组/对象）时，需用`json_encode`/`json_decode`序列化；  
3. **异常处理**：添加try-catch捕获连接或操作异常；  
4. **性能**：phpredis扩展性能优于Predis，生产环境优先选择phpredis。

PHP操作Redis的核心是通过客户端库调用Redis命令，语法与Redis原生命令高度一致，只需掌握数据结构和命令对应关系即可灵活使用。