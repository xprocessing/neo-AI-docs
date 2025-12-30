# PHP数据库操作

## PDO (PHP Data Objects)

### PDO基础连接
```php
<?php
    // 数据库连接配置
    $host = 'localhost';
    $dbname = 'test_db';
    $username = 'root';
    $password = 'password';
    $charset = 'utf8mb4';
    
    // DSN (Data Source Name)
    $dsn = "mysql:host=$host;dbname=$dbname;charset=$charset";
    
    // PDO选项
    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,    // 异常模式
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC, // 关联数组模式
        PDO::ATTR_EMULATE_PREPARES => false,              // 禁用预处理模拟
        PDO::ATTR_PERSISTENT => true,                    // 持久连接
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES $charset"
    ];
    
    try {
        // 创建PDO连接
        $pdo = new PDO($dsn, $username, $password, $options);
        echo "数据库连接成功！";
    } catch (PDOException $e) {
        die("数据库连接失败：" . $e->getMessage());
    }
    
    // 获取数据库信息
    echo "PDO驱动：" . $pdo->getAttribute(PDO::ATTR_DRIVER_NAME) . "\n";
    echo "数据库版本：" . $pdo->getAttribute(PDO::ATTR_SERVER_VERSION) . "\n";
    echo "连接状态：" . $pdo->getAttribute(PDO::ATTR_CONNECTION_STATUS) . "\n";
?>
```

### PDO查询操作
```php
<?php
    class Database {
        private $pdo;
        
        public function __construct($host, $dbname, $username, $password) {
            $dsn = "mysql:host=$host;dbname=$dbname;charset=utf8mb4";
            $options = [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ];
            
            try {
                $this->pdo = new PDO($dsn, $username, $password, $options);
            } catch (PDOException $e) {
                throw new Exception("数据库连接失败：" . $e->getMessage());
            }
        }
        
        // 查询单条记录
        public function queryOne($sql, $params = []) {
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute($params);
            return $stmt->fetch();
        }
        
        // 查询多条记录
        public function queryAll($sql, $params = []) {
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute($params);
            return $stmt->fetchAll();
        }
        
        // 查询单个值
        public function queryScalar($sql, $params = []) {
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute($params);
            return $stmt->fetchColumn();
        }
        
        // 插入数据
        public function insert($table, $data) {
            $columns = implode(', ', array_keys($data));
            $placeholders = ':' . implode(', :', array_keys($data));
            
            $sql = "INSERT INTO $table ($columns) VALUES ($placeholders)";
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute($data);
            
            return $this->pdo->lastInsertId();
        }
        
        // 更新数据
        public function update($table, $data, $where, $whereParams = []) {
            $setClause = [];
            foreach ($data as $column => $value) {
                $setClause[] = "$column = :$column";
            }
            $setSql = implode(', ', $setClause);
            
            $sql = "UPDATE $table SET $setSql WHERE $where";
            $stmt = $this->pdo->prepare($sql);
            
            // 合并参数
            $params = array_merge($data, $whereParams);
            $stmt->execute($params);
            
            return $stmt->rowCount();
        }
        
        // 删除数据
        public function delete($table, $where, $params = []) {
            $sql = "DELETE FROM $table WHERE $where";
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute($params);
            
            return $stmt->rowCount();
        }
        
        // 开始事务
        public function beginTransaction() {
            return $this->pdo->beginTransaction();
        }
        
        // 提交事务
        public function commit() {
            return $this->pdo->commit();
        }
        
        // 回滚事务
        public function rollback() {
            return $this->pdo->rollback();
        }
        
        // 获取PDO实例
        public function getPdo() {
            return $this->pdo;
        }
    }
    
    // 使用示例
    $db = new Database('localhost', 'test_db', 'root', 'password');
    
    // 查询用户
    $user = $db->queryOne("SELECT * FROM users WHERE id = ?", [1]);
    echo "用户名：" . ($user['name'] ?? '未找到') . "\n";
    
    // 查询所有用户
    $users = $db->queryAll("SELECT * FROM users WHERE status = ? ORDER BY created_at DESC", ['active']);
    foreach ($users as $user) {
        echo $user['name'] . " - " . $user['email'] . "\n";
    }
    
    // 统计用户数量
    $count = $db->queryScalar("SELECT COUNT(*) FROM users");
    echo "总用户数：$count\n";
    
    // 插入新用户
    $newUserId = $db->insert('users', [
        'name' => '张三',
        'email' => 'zhangsan@email.com',
        'password' => password_hash('123456', PASSWORD_DEFAULT),
        'created_at' => date('Y-m-d H:i:s')
    ]);
    echo "新用户ID：$newUserId\n";
    
    // 更新用户信息
    $affected = $db->update('users', 
        ['email' => 'new@email.com', 'updated_at' => date('Y-m-d H:i:s')], 
        'id = ?', 
        [1]
    );
    echo "更新了 $affected 行\n";
    
    // 删除用户
    $deleted = $db->delete('users', 'id = ?', [1]);
    echo "删除了 $deleted 行\n";
?>
```

### PDO预处理语句
```php
<?php
    class PreparedStatements {
        private $pdo;
        
        public function __construct($pdo) {
            $this->pdo = $pdo;
        }
        
        // 命名占位符
        public function insertUser($name, $email, $age) {
            $sql = "INSERT INTO users (name, email, age, created_at) 
                    VALUES (:name, :email, :age, NOW())";
            
            $stmt = $this->pdo->prepare($sql);
            $stmt->bindParam(':name', $name, PDO::PARAM_STR);
            $stmt->bindParam(':email', $email, PDO::PARAM_STR);
            $stmt->bindParam(':age', $age, PDO::PARAM_INT);
            
            return $stmt->execute();
        }
        
        // 问号占位符
        public function getUsersByAge($minAge, $maxAge) {
            $sql = "SELECT id, name, email, age FROM users 
                    WHERE age BETWEEN ? AND ? ORDER BY age";
            
            $stmt = $this->pdo->prepare($sql);
            $stmt->bindValue(1, $minAge, PDO::PARAM_INT);
            $stmt->bindValue(2, $maxAge, PDO::PARAM_INT);
            $stmt->execute();
            
            return $stmt->fetchAll();
        }
        
        // 批量插入
        public function batchInsertUsers($users) {
            $sql = "INSERT INTO users (name, email, age, created_at) 
                    VALUES (?, ?, ?, NOW())";
            
            $stmt = $this->pdo->prepare($sql);
            
            $this->pdo->beginTransaction();
            
            try {
                foreach ($users as $user) {
                    $stmt->execute([$user['name'], $user['email'], $user['age']]);
                }
                $this->pdo->commit();
                return true;
            } catch (Exception $e) {
                $this->pdo->rollback();
                throw $e;
            }
        }
        
        // 使用IN语句
        public function getUsersByIds($ids) {
            if (empty($ids)) {
                return [];
            }
            
            // 创建占位符
            $placeholders = str_repeat('?,', count($ids) - 1) . '?';
            $sql = "SELECT * FROM users WHERE id IN ($placeholders)";
            
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute($ids);
            
            return $stmt->fetchAll();
        }
        
        // 动态查询构建
        public function searchUsers($filters) {
            $sql = "SELECT * FROM users WHERE 1=1";
            $params = [];
            
            // 动态添加条件
            if (!empty($filters['name'])) {
                $sql .= " AND name LIKE :name";
                $params[':name'] = '%' . $filters['name'] . '%';
            }
            
            if (!empty($filters['email'])) {
                $sql .= " AND email LIKE :email";
                $params[':email'] = '%' . $filters['email'] . '%';
            }
            
            if (!empty($filters['min_age'])) {
                $sql .= " AND age >= :min_age";
                $params[':min_age'] = $filters['min_age'];
            }
            
            if (!empty($filters['max_age'])) {
                $sql .= " AND age <= :max_age";
                $params[':max_age'] = $filters['max_age'];
            }
            
            // 排序
            $sql .= " ORDER BY " . ($filters['sort'] ?? 'id DESC');
            
            // 分页
            if (!empty($filters['limit'])) {
                $offset = $filters['offset'] ?? 0;
                $sql .= " LIMIT $offset, " . $filters['limit'];
            }
            
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute($params);
            
            return $stmt->fetchAll();
        }
    }
    
    // 使用示例
    $db = new Database('localhost', 'test_db', 'root', 'password');
    $prepared = new PreparedStatements($db->getPdo());
    
    // 插入用户
    $prepared->insertUser('李四', 'lisi@email.com', 28);
    
    // 查询年龄在20-30之间的用户
    $users = $prepared->getUsersByAge(20, 30);
    
    // 批量插入
    $newUsers = [
        ['name' => '王五', 'email' => 'wangwu@email.com', 'age' => 25],
        ['name' => '赵六', 'email' => 'zhaoliu@email.com', 'age' => 32],
        ['name' => '钱七', 'email' => 'qianqi@email.com', 'age' => 29]
    ];
    $prepared->batchInsertUsers($newUsers);
    
    // 根据ID列表查询
    $users = $prepared->getUsersByIds([1, 3, 5]);
    
    // 搜索用户
    $filters = [
        'name' => '张',
        'min_age' => 20,
        'max_age' => 40,
        'sort' => 'name ASC',
        'limit' => 10
    ];
    $searchResults = $prepared->searchUsers($filters);
?>
```

## MySQLi

### MySQLi面向对象方式
```php
<?php
    class MySQLiDatabase {
        private $mysqli;
        
        public function __construct($host, $username, $password, $database, $port = 3306) {
            try {
                $this->mysqli = new mysqli($host, $username, $password, $database, $port);
                
                if ($this->mysqli->connect_error) {
                    throw new Exception("连接失败：" . $this->mysqli->connect_error);
                }
                
                // 设置字符集
                $this->mysqli->set_charset("utf8mb4");
                
            } catch (Exception $e) {
                throw new Exception("数据库连接失败：" . $e->getMessage());
            }
        }
        
        // 执行查询（返回结果集）
        public function query($sql) {
            $result = $this->mysqli->query($sql);
            
            if ($result === false) {
                throw new Exception("查询失败：" . $this->mysqli->error);
            }
            
            return $result;
        }
        
        // 获取单条记录
        public function fetchOne($sql) {
            $result = $this->query($sql);
            return $result->fetch_assoc();
        }
        
        // 获取多条记录
        public function fetchAll($sql) {
            $result = $this->query($sql);
            return $result->fetch_all(MYSQLI_ASSOC);
        }
        
        // 预处理查询
        public function prepare($sql) {
            $stmt = $this->mysqli->prepare($sql);
            
            if ($stmt === false) {
                throw new Exception("预处理失败：" . $this->mysqli->error);
            }
            
            return $stmt;
        }
        
        // 执行预处理语句
        public function execute($stmt, $params = [], $types = '') {
            if (!empty($params)) {
                // 绑定参数
                if (empty($types)) {
                    // 自动推断参数类型
                    $bindTypes = '';
                    $bindParams = [];
                    
                    foreach ($params as $param) {
                        if (is_int($param)) {
                            $bindTypes .= 'i';
                        } elseif (is_float($param)) {
                            $bindTypes .= 'd';
                        } else {
                            $bindTypes .= 's';
                        }
                        $bindParams[] = $param;
                    }
                    
                    array_unshift($bindParams, $bindTypes);
                    $stmt->bind_param(...$bindParams);
                } else {
                    $bindParams = array_merge([$types], $params);
                    $stmt->bind_param(...$bindParams);
                }
            }
            
            if (!$stmt->execute()) {
                throw new Exception("执行失败：" . $stmt->error);
            }
            
            return $stmt;
        }
        
        // 获取插入的ID
        public function insertId() {
            return $this->mysqli->insert_id;
        }
        
        // 获取影响的行数
        public function affectedRows() {
            return $this->mysqli->affected_rows;
        }
        
        // 开始事务
        public function beginTransaction() {
            $this->mysqli->autocommit(false);
            return true;
        }
        
        // 提交事务
        public function commit() {
            $result = $this->mysqli->commit();
            $this->mysqli->autocommit(true);
            return $result;
        }
        
        // 回滚事务
        public function rollback() {
            $this->mysqli->rollback();
            $this->mysqli->autocommit(true);
        }
        
        // 转义字符串
        public function escape($string) {
            return $this->mysqli->real_escape_string($string);
        }
        
        // 关闭连接
        public function close() {
            if ($this->mysqli) {
                $this->mysqli->close();
            }
        }
        
        // 析构函数
        public function __destruct() {
            $this->close();
        }
    }
    
    // 使用示例
    $db = new MySQLiDatabase('localhost', 'root', 'password', 'test_db');
    
    // 查询用户
    $user = $db->fetchOne("SELECT * FROM users WHERE id = 1");
    echo $user['name'] ?? '未找到用户';
    
    // 查询所有用户
    $users = $db->fetchAll("SELECT * FROM users WHERE status = 'active'");
    
    // 预处理插入
    $stmt = $db->prepare("INSERT INTO users (name, email, age) VALUES (?, ?, ?)");
    $db->execute($stmt, ['张三', 'zhangsan@email.com', 25], 'ssi');
    echo "插入的用户ID：" . $db->insertId();
    
    // 预处理更新
    $stmt = $db->prepare("UPDATE users SET name = ? WHERE id = ?");
    $db->execute($stmt, ['李四', 1]);
    echo "影响的行数：" . $db->affectedRows();
?>
```

### MySQLi事务处理
```php
<?php
    class TransactionManager {
        private $db;
        private $inTransaction = false;
        
        public function __construct(MySQLiDatabase $db) {
            $this->db = $db;
        }
        
        // 开始事务
        public function begin() {
            if (!$this->inTransaction) {
                $this->db->beginTransaction();
                $this->inTransaction = true;
            }
            return $this;
        }
        
        // 执行多个操作
        public function execute($operations) {
            $this->begin();
            
            try {
                $results = [];
                foreach ($operations as $operation) {
                    $result = $this->executeOperation($operation);
                    $results[] = $result;
                }
                
                $this->commit();
                return $results;
            } catch (Exception $e) {
                $this->rollback();
                throw $e;
            }
        }
        
        // 执行单个操作
        private function executeOperation($operation) {
            $type = $operation['type'] ?? 'query';
            $sql = $operation['sql'] ?? '';
            $params = $operation['params'] ?? [];
            $types = $operation['types'] ?? '';
            
            switch ($type) {
                case 'query':
                    return $this->db->query($sql);
                case 'fetch_one':
                    return $this->db->fetchOne($sql);
                case 'fetch_all':
                    return $this->db->fetchAll($sql);
                case 'prepare':
                    $stmt = $this->db->prepare($sql);
                    return $this->db->execute($stmt, $params, $types);
                default:
                    throw new Exception("不支持的操作类型：$type");
            }
        }
        
        // 提交事务
        public function commit() {
            if ($this->inTransaction) {
                $this->db->commit();
                $this->inTransaction = false;
            }
            return $this;
        }
        
        // 回滚事务
        public function rollback() {
            if ($this->inTransaction) {
                $this->db->rollback();
                $this->inTransaction = false;
            }
            return $this;
        }
        
        // 检查是否在事务中
        public function isInTransaction() {
            return $this->inTransaction;
        }
    }
    
    // 转账示例
    function transferMoney($db, $fromUserId, $toUserId, $amount) {
        $transaction = new TransactionManager($db);
        
        $operations = [
            // 检查发送方余额
            [
                'type' => 'fetch_one',
                'sql' => 'SELECT balance FROM accounts WHERE user_id = ? FOR UPDATE',
                'params' => [$fromUserId],
                'types' => 'i'
            ],
            // 检查接收方账户
            [
                'type' => 'fetch_one',
                'sql' => 'SELECT balance FROM accounts WHERE user_id = ? FOR UPDATE',
                'params' => [$toUserId],
                'types' => 'i'
            ],
            // 扣除发送方金额
            [
                'type' => 'prepare',
                'sql' => 'UPDATE accounts SET balance = balance - ? WHERE user_id = ?',
                'params' => [$amount, $fromUserId],
                'types' => 'di'
            ],
            // 增加接收方金额
            [
                'type' => 'prepare',
                'sql' => 'UPDATE accounts SET balance = balance + ? WHERE user_id = ?',
                'params' => [$amount, $toUserId],
                'types' => 'di'
            ],
            // 记录交易
            [
                'type' => 'prepare',
                'sql' => 'INSERT INTO transactions (from_user_id, to_user_id, amount, created_at) VALUES (?, ?, ?, NOW())',
                'params' => [$fromUserId, $toUserId, $amount],
                'types' => 'iid'
            ]
        ];
        
        return $transaction->execute($operations);
    }
    
    // 使用示例
    $db = new MySQLiDatabase('localhost', 'root', 'password', 'bank_db');
    
    try {
        $results = transferMoney($db, 1, 2, 1000);
        echo "转账成功！";
    } catch (Exception $e) {
        echo "转账失败：" . $e->getMessage();
    }
?>
```

## 数据库抽象层

### ActiveRecord模式
```php
<?php
    abstract class ActiveRecord {
        protected static $pdo;
        protected $tableName;
        protected $primaryKey = 'id';
        protected $attributes = [];
        protected $dirty = [];
        
        public function __construct($data = []) {
            foreach ($data as $key => $value) {
                $this->$key = $value;
            }
        }
        
        // 设置PDO连接
        public static function setConnection($pdo) {
            self::$pdo = $pdo;
        }
        
        // 获取表名
        protected static function getTableName() {
            $className = static::class;
            $model = new $className;
            return $model->tableName;
        }
        
        // 查找单条记录
        public static function find($id) {
            $tableName = static::getTableName();
            $primaryKey = (new static)->primaryKey;
            
            $sql = "SELECT * FROM $tableName WHERE $primaryKey = ?";
            $stmt = self::$pdo->prepare($sql);
            $stmt->execute([$id]);
            
            $data = $stmt->fetch(PDO::FETCH_ASSOC);
            return $data ? new static($data) : null;
        }
        
        // 查找所有记录
        public static function all() {
            $tableName = static::getTableName();
            
            $sql = "SELECT * FROM $tableName";
            $stmt = self::$pdo->query($sql);
            
            $models = [];
            while ($data = $stmt->fetch(PDO::FETCH_ASSOC)) {
                $models[] = new static($data);
            }
            
            return $models;
        }
        
        // 条件查询
        public static function where($condition, $params = []) {
            $tableName = static::getTableName();
            
            $sql = "SELECT * FROM $tableName WHERE $condition";
            $stmt = self::$pdo->prepare($sql);
            $stmt->execute($params);
            
            $models = [];
            while ($data = $stmt->fetch(PDO::FETCH_ASSOC)) {
                $models[] = new static($data);
            }
            
            return $models;
        }
        
        // 插入记录
        public function save() {
            $tableName = $this->tableName;
            $primaryKey = $this->primaryKey;
            
            // 如果有主键值，则更新；否则插入
            if (!empty($this->$primaryKey)) {
                return $this->update();
            } else {
                return $this->insert();
            }
        }
        
        // 插入新记录
        private function insert() {
            $tableName = $this->tableName;
            $primaryKey = $this->primaryKey;
            
            $columns = [];
            $values = [];
            $params = [];
            
            foreach ($this->attributes as $key => $value) {
                if ($key !== $primaryKey) {
                    $columns[] = $key;
                    $placeholders[] = ":$key";
                    $params[":$key"] = $value;
                }
            }
            
            $columnsStr = implode(', ', $columns);
            $placeholdersStr = implode(', ', $placeholders);
            
            $sql = "INSERT INTO $tableName ($columnsStr) VALUES ($placeholdersStr)";
            $stmt = self::$pdo->prepare($sql);
            $stmt->execute($params);
            
            $this->$primaryKey = self::$pdo->lastInsertId();
            return true;
        }
        
        // 更新记录
        private function update() {
            $tableName = $this->tableName;
            $primaryKey = $this->primaryKey;
            
            $setClause = [];
            $params = [];
            
            foreach ($this->dirty as $key) {
                if (isset($this->attributes[$key]) && $key !== $primaryKey) {
                    $setClause[] = "$key = :$key";
                    $params[":$key"] = $this->attributes[$key];
                }
            }
            
            if (empty($setClause)) {
                return true; // 没有需要更新的字段
            }
            
            $setClauseStr = implode(', ', $setClause);
            $params[":$primaryKey"] = $this->$primaryKey;
            
            $sql = "UPDATE $tableName SET $setClauseStr WHERE $primaryKey = :$primaryKey";
            $stmt = self::$pdo->prepare($sql);
            $stmt->execute($params);
            
            $this->dirty = []; // 清空脏字段
            return $stmt->rowCount() > 0;
        }
        
        // 删除记录
        public function delete() {
            $tableName = $this->tableName;
            $primaryKey = $this->primaryKey;
            
            if (empty($this->$primaryKey)) {
                return false;
            }
            
            $sql = "DELETE FROM $tableName WHERE $primaryKey = ?";
            $stmt = self::$pdo->prepare($sql);
            return $stmt->execute([$this->$primaryKey]);
        }
        
        // 魔术方法：设置属性
        public function __set($name, $value) {
            $this->attributes[$name] = $value;
            $this->dirty[] = $name; // 标记为脏字段
        }
        
        // 魔术方法：获取属性
        public function __get($name) {
            return $this->attributes[$name] ?? null;
        }
        
        // 魔术方法：检查属性是否存在
        public function __isset($name) {
            return isset($this->attributes[$name]);
        }
        
        // 魔术方法：删除属性
        public function __unset($name) {
            unset($this->attributes[$name]);
        }
        
        // 将对象转换为数组
        public function toArray() {
            return $this->attributes;
        }
    }
    
    // 用户模型
    class User extends ActiveRecord {
        protected $tableName = 'users';
        protected $primaryKey = 'id';
        
        // 自定义方法
        public function getPosts() {
            return Post::where('user_id = ?', [$this->id]);
        }
        
        public function isActive() {
            return $this->status === 'active';
        }
        
        public function getDisplayName() {
            return $this->name ?: '匿名用户';
        }
    }
    
    // 文章模型
    class Post extends ActiveRecord {
        protected $tableName = 'posts';
        
        public function getAuthor() {
            return User::find($this->user_id);
        }
        
        public function getComments() {
            return Comment::where('post_id = ?', [$this->id]);
        }
    }
    
    class Comment extends ActiveRecord {
        protected $tableName = 'comments';
    }
    
    // 使用示例
    Database::setConnection($pdo); // 设置数据库连接
    
    // 创建新用户
    $user = new User();
    $user->name = '张三';
    $user->email = 'zhangsan@email.com';
    $user->status = 'active';
    $user->save(); // 插入
    
    echo "新用户ID：" . $user->id;
    
    // 查找用户
    $foundUser = User::find(1);
    if ($foundUser) {
        echo "找到用户：" . $foundUser->getDisplayName();
        
        // 修改用户信息
        $foundUser->name = '李四';
        $foundUser->save(); // 更新
    }
    
    // 条件查询
    $activeUsers = User::where('status = ?', ['active']);
    foreach ($activeUsers as $user) {
        echo $user->name;
    }
    
    // 关联查询
    $user = User::find(1);
    $posts = $user->getPosts();
    foreach ($posts as $post) {
        echo $post->title;
        $comments = $post->getComments();
    }
?>
```

## 数据库连接池

### 简单连接池实现
```php
<?php
    class ConnectionPool {
        private $config;
        private $pool = [];
        private $maxConnections;
        private $currentConnections = 0;
        private $timeout = 30; // 连接超时时间
        
        public function __construct($config, $maxConnections = 10) {
            $this->config = $config;
            $this->maxConnections = $maxConnections;
        }
        
        // 获取连接
        public function getConnection() {
            // 检查池中是否有可用连接
            if (!empty($this->pool)) {
                $connection = array_pop($this->pool);
                if ($this->isConnectionValid($connection)) {
                    return $connection;
                }
            }
            
            // 如果还能创建新连接
            if ($this->currentConnections < $this->maxConnections) {
                $connection = $this->createConnection();
                if ($connection) {
                    $this->currentConnections++;
                    return $connection;
                }
            }
            
            // 等待连接可用（简单实现）
            return $this->waitForConnection();
        }
        
        // 释放连接
        public function releaseConnection($connection) {
            if ($this->isConnectionValid($connection)) {
                $this->pool[] = $connection;
            } else {
                $this->currentConnections--;
            }
        }
        
        // 创建新连接
        private function createConnection() {
            try {
                $dsn = "mysql:host={$this->config['host']};dbname={$this->config['database']};charset=utf8mb4";
                $options = [
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES => false,
                    PDO::ATTR_TIMEOUT => $this->timeout,
                    PDO::ATTR_PERSISTENT => true
                ];
                
                $pdo = new PDO($dsn, $this->config['username'], $this->config['password'], $options);
                $pdo->setAttribute(PDO::ATTR_PERSISTENT, true);
                
                return $pdo;
            } catch (PDOException $e) {
                error_log("创建数据库连接失败：" . $e->getMessage());
                return null;
            }
        }
        
        // 检查连接是否有效
        private function isConnectionValid($connection) {
            if (!$connection instanceof PDO) {
                return false;
            }
            
            try {
                $connection->query("SELECT 1");
                return true;
            } catch (PDOException $e) {
                return false;
            }
        }
        
        // 等待连接可用
        private function waitForConnection() {
            $maxWaitTime = 5; // 最大等待5秒
            $waitedTime = 0;
            
            while ($waitedTime < $maxWaitTime) {
                if (!empty($this->pool)) {
                    $connection = array_pop($this->pool);
                    if ($this->isConnectionValid($connection)) {
                        return $connection;
                    }
                }
                
                usleep(100000); // 等待100ms
                $waitedTime += 0.1;
            }
            
            throw new Exception("获取数据库连接超时");
        }
        
        // 关闭所有连接
        public function closeAll() {
            foreach ($this->pool as $connection) {
                $connection = null;
            }
            $this->pool = [];
            $this->currentConnections = 0;
        }
        
        // 获取池状态
        public function getStatus() {
            return [
                'pool_size' => count($this->pool),
                'total_connections' => $this->currentConnections,
                'max_connections' => $this->maxConnections
            ];
        }
    }
    
    // 连接池管理器
    class PoolManager {
        private static $pools = [];
        
        public static function register($name, ConnectionPool $pool) {
            self::$pools[$name] = $pool;
        }
        
        public static function getPool($name) {
            return self::$pools[$name] ?? null;
        }
        
        public static function getConnection($poolName) {
            $pool = self::getPool($poolName);
            if (!$pool) {
                throw new Exception("连接池 '$poolName' 不存在");
            }
            
            return $pool->getConnection();
        }
        
        public static function releaseConnection($poolName, $connection) {
            $pool = self::getPool($poolName);
            if ($pool) {
                $pool->releaseConnection($connection);
            }
        }
    }
    
    // 使用示例
    $config = [
        'host' => 'localhost',
        'database' => 'test_db',
        'username' => 'root',
        'password' => 'password'
    ];
    
    // 创建连接池
    $pool = new ConnectionPool($config, 20);
    PoolManager::register('main', $pool);
    
    // 在应用中使用连接池
    function queryWithPool($sql, $params = []) {
        $connection = PoolManager::getConnection('main');
        
        try {
            $stmt = $connection->prepare($sql);
            $stmt->execute($params);
            $result = $stmt->fetchAll();
            
            return $result;
        } finally {
            PoolManager::releaseConnection('main', $connection);
        }
    }
    
    // 执行查询
    $users = queryWithPool("SELECT * FROM users LIMIT 10");
    
    // 查看连接池状态
    $status = $pool->getStatus();
    print_r($status);
    
    // 应用结束时关闭所有连接
    register_shutdown_function(function() use ($pool) {
        $pool->closeAll();
    });
?>
```

## 最佳实践

1. **使用预处理语句**：防止SQL注入，提高安全性。
2. **错误处理**：使用try-catch处理数据库异常。
3. **连接管理**：合理使用连接池，避免连接泄露。
4. **事务处理**：在需要数据一致性的操作中使用事务。
5. **索引优化**：为频繁查询的字段创建索引。
6. **分页查询**：对大数据集使用分页避免内存溢出。
7. **数据验证**：在应用层验证数据，减少数据库负担。
8. **日志记录**：记录重要的数据库操作和错误。