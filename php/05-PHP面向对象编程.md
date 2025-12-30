# PHP面向对象编程进阶

## 高级OOP特性

### 静态成员和延迟静态绑定
```php
<?php
    class Database {
        private static $connection = null;
        private static $config = [];
        
        // 静态方法
        public static function setConfig($host, $user, $password, $database) {
            self::$config = [
                'host' => $host,
                'user' => $user,
                'password' => $password,
                'database' => $database
            ];
        }
        
        public static function getConnection() {
            if (self::$connection === null) {
                self::$connection = self::createConnection();
            }
            return self::$connection;
        }
        
        private static function createConnection() {
            // 模拟创建连接
            echo "创建数据库连接\n";
            return "Connection to " . self::$config['host'];
        }
        
        public static function closeConnection() {
            if (self::$connection !== null) {
                self::$connection = null;
                echo "关闭数据库连接\n";
            }
        }
    }
    
    // 延迟静态绑定示例
    abstract class Model {
        protected static $table;
        protected static $primaryKey = 'id';
        
        public static function find($id) {
            $table = static::$table;  // 延迟静态绑定
            $primaryKey = static::$primaryKey;
            return "SELECT * FROM {$table} WHERE {$primaryKey} = {$id}";
        }
        
        public static function all() {
            $table = static::$table;
            return "SELECT * FROM {$table}";
        }
        
        public static function create($data) {
            $table = static::$table;
            $columns = implode(', ', array_keys($data));
            $values = implode("', '", array_values($data));
            return "INSERT INTO {$table} ({$columns}) VALUES ('{$values}')";
        }
    }
    
    class User extends Model {
        protected static $table = 'users';
        protected static $primaryKey = 'user_id';
    }
    
    class Product extends Model {
        protected static $table = 'products';
    }
    
    // 使用示例
    Database::setConfig('localhost', 'root', 'password', 'myapp');
    $conn = Database::getConnection();
    
    echo User::find(1);        // SELECT * FROM users WHERE user_id = 1
    echo Product::find(5);      // SELECT * FROM products WHERE id = 5
    echo User::all();           // SELECT * FROM users
    echo Product::create(['name' => '手机', 'price' => 2999]);
?>
```

### 对象克隆
```php
<?php
    class User {
        public $id;
        public $name;
        public $email;
        public $profile;
        
        public function __construct($id, $name, $email) {
            $this->id = $id;
            $this->name = $name;
            $this->email = $email;
            $this->profile = new UserProfile("默认个人资料");
        }
        
        public function __clone() {
            // 深度克隆：克隆嵌套对象
            $this->profile = clone $this->profile;
            $this->id = 0;  // 重置ID
        }
        
        public function getInfo() {
            return "ID: {$this->id}, 姓名: {$this->name}, 邮箱: {$this->email}";
        }
    }
    
    class UserProfile {
        public $bio;
        public $avatar;
        
        public function __construct($bio) {
            $this->bio = $bio;
            $this->avatar = "default.jpg";
        }
        
        public function __clone() {
            // 修改克隆对象的某些属性
            $this->avatar = "cloned_" . $this->avatar;
        }
    }
    
    // 测试克隆
    $user1 = new User(1, "张三", "zhangsan@email.com");
    $user2 = clone $user1;
    
    $user2->name = "李四";
    $user2->email = "lisi@email.com";
    $user2->profile->bio = "李四的个人资料";
    
    echo $user1->getInfo();  // ID: 1, 姓名: 张三, 邮箱: zhangsan@email.com
    echo $user2->getInfo();  // ID: 0, 姓名: 李四, 邮箱: lisi@email.com
    
    // 测试深度克隆
    echo $user1->profile->bio;    // 默认个人资料
    echo $user2->profile->bio;    // 李四的个人资料
?>
```

### 对象序列化
```php
<?php
    class User {
        public $id;
        public $name;
        public $email;
        private $password;
        private $lastLogin;
        
        public function __construct($id, $name, $email, $password) {
            $this->id = $id;
            $this->name = $name;
            $this->email = $email;
            $this->password = $password;
            $this->lastLogin = new DateTime();
        }
        
        // 序列化时调用
        public function __sleep() {
            // 只序列化需要的属性
            return ['id', 'name', 'email'];
        }
        
        // 反序列化时调用
        public function __wakeup() {
            // 重新初始化一些属性
            $this->lastLogin = new DateTime();
            echo "用户对象已反序列化\n";
        }
        
        // 自定义序列化方法
        public function serialize() {
            $data = [
                'id' => $this->id,
                'name' => $this->name,
                'email' => $this->email,
                'lastLogin' => $this->lastLogin->format('Y-m-d H:i:s')
            ];
            return serialize($data);
        }
        
        public function unserialize($serialized) {
            $data = unserialize($serialized);
            $this->id = $data['id'];
            $this->name = $data['name'];
            $this->email = $data['email'];
            $this->lastLogin = DateTime::createFromFormat('Y-m-d H:i:s', $data['lastLogin']);
            $this->password = ''; // 重置密码
        }
        
        public function getInfo() {
            return "用户：{$this->name} ({$this->email})";
        }
    }
    
    // 基本序列化
    $user = new User(1, "张三", "zhangsan@email.com", "password123");
    
    // 序列化对象
    $serialized = serialize($user);
    echo $serialized;
    
    // 保存到文件
    file_put_contents('user.dat', $serialized);
    
    // 从文件读取并反序列化
    $loaded = file_get_contents('user.dat');
    $restoredUser = unserialize($loaded);
    
    echo $restoredUser->getInfo();
    
    // 使用自定义序列化
    $customSerialized = $user->serialize();
    $newUser = new User(0, "", "", "");
    $newUser->unserialize($customSerialized);
    echo $newUser->getInfo();
?>
```

## 设计模式

### 单例模式
```php
<?php
    class Database {
        private static $instance = null;
        private $connection;
        
        private function __construct() {
            // 私有构造函数防止外部实例化
            $this->connection = $this->createConnection();
        }
        
        private function __clone() {
            // 防止克隆
        }
        
        public function __wakeup() {
            // 防止反序列化
            throw new Exception("Cannot unserialize singleton");
        }
        
        public static function getInstance() {
            if (self::$instance === null) {
                self::$instance = new self();
            }
            return self::$instance;
        }
        
        private function createConnection() {
            // 模拟数据库连接
            return new PDO("mysql:host=localhost;dbname=myapp", "root", "password");
        }
        
        public function getConnection() {
            return $this->connection;
        }
        
        public function query($sql, $params = []) {
            $stmt = $this->connection->prepare($sql);
            $stmt->execute($params);
            return $stmt;
        }
    }
    
    // 使用单例
    $db1 = Database::getInstance();
    $db2 = Database::getInstance();
    
    // 两者是同一个实例
    if ($db1 === $db2) {
        echo "这是同一个实例\n";
    }
    
    $result = $db1->query("SELECT * FROM users WHERE id = ?", [1]);
?>
```

### 工厂模式
```php
<?php
    // 抽象产品
    interface Vehicle {
        public function drive();
        public function stop();
        public function getInfo();
    }
    
    // 具体产品
    class Car implements Vehicle {
        private $brand;
        private $model;
        
        public function __construct($brand, $model) {
            $this->brand = $brand;
            $this->model = $model;
        }
        
        public function drive() {
            return "{$this->brand} {$this->model} 正在行驶";
        }
        
        public function stop() {
            return "{$this->brand} {$this->model} 已停止";
        }
        
        public function getInfo() {
            return "汽车：{$this->brand} {$this->model}";
        }
    }
    
    class Motorcycle implements Vehicle {
        private $brand;
        private $type;
        
        public function __construct($brand, $type) {
            $this->brand = $brand;
            $this->type = $type;
        }
        
        public function drive() {
            return "{$this->brand} {$this->type}摩托车 飞驰中";
        }
        
        public function stop() {
            return "{$this->brand} {$this->type}摩托车 已刹车";
        }
        
        public function getInfo() {
            return "摩托车：{$this->brand} {$this->type}";
        }
    }
    
    // 抽象工厂
    abstract class VehicleFactory {
        abstract public function createVehicle($brand, $model);
    }
    
    // 具体工厂
    class CarFactory extends VehicleFactory {
        public function createVehicle($brand, $model) {
            return new Car($brand, $model);
        }
    }
    
    class MotorcycleFactory extends VehicleFactory {
        public function createVehicle($brand, $model) {
            return new Motorcycle($brand, $model);
        }
    }
    
    // 简单工厂
    class SimpleVehicleFactory {
        public static function create($type, $brand, $model) {
            switch (strtolower($type)) {
                case 'car':
                    return new Car($brand, $model);
                case 'motorcycle':
                    return new Motorcycle($brand, $model);
                default:
                    throw new InvalidArgumentException("不支持的车辆类型：$type");
            }
        }
    }
    
    // 使用示例
    $carFactory = new CarFactory();
    $car = $carFactory->createVehicle("丰田", "卡罗拉");
    echo $car->getInfo();  // 汽车：丰田 卡罗拉
    
    $motorcycle = SimpleVehicleFactory::create("motorcycle", "本田", "CBR650R");
    echo $motorcycle->getInfo();  // 摩托车：本田 CBR650R
?>
```

### 观察者模式
```php
<?php
    // 主题接口
    interface Subject {
        public function attach(Observer $observer);
        public function detach(Observer $observer);
        public function notify();
    }
    
    // 观察者接口
    interface Observer {
        public function update(Subject $subject);
    }
    
    // 具体主题
    class WeatherStation implements Subject {
        private $observers = [];
        private $temperature;
        private $humidity;
        
        public function attach(Observer $observer) {
            if (!in_array($observer, $this->observers)) {
                $this->observers[] = $observer;
            }
        }
        
        public function detach(Observer $observer) {
            $key = array_search($observer, $this->observers);
            if ($key !== false) {
                unset($this->observers[$key]);
            }
        }
        
        public function notify() {
            foreach ($this->observers as $observer) {
                $observer->update($this);
            }
        }
        
        public function setMeasurements($temperature, $humidity) {
            $this->temperature = $temperature;
            $this->humidity = $humidity;
            $this->notify();
        }
        
        public function getTemperature() {
            return $this->temperature;
        }
        
        public function getHumidity() {
            return $this->humidity;
        }
    }
    
    // 具体观察者
    class TemperatureDisplay implements Observer {
        public function update(Subject $subject) {
            if ($subject instanceof WeatherStation) {
                echo "温度显示器：当前温度 " . $subject->getTemperature() . "°C\n";
            }
        }
    }
    
    class HumidityDisplay implements Observer {
        public function update(Subject $subject) {
            if ($subject instanceof WeatherStation) {
                echo "湿度显示器：当前湿度 " . $subject->getHumidity() . "%\n";
            }
        }
    }
    
    class WeatherApp implements Observer {
        public function update(Subject $subject) {
            if ($subject instanceof WeatherStation) {
                $temp = $subject->getTemperature();
                $humidity = $subject->getHumidity();
                echo "天气应用：温度 {$temp}°C，湿度 {$humidity}%\n";
                
                // 智能建议
                if ($temp > 30) {
                    echo "建议：天气炎热，注意防暑\n";
                } elseif ($temp < 10) {
                    echo "建议：天气寒冷，注意保暖\n";
                }
            }
        }
    }
    
    // 使用示例
    $weatherStation = new WeatherStation();
    
    $tempDisplay = new TemperatureDisplay();
    $humidityDisplay = new HumidityDisplay();
    $weatherApp = new WeatherApp();
    
    // 注册观察者
    $weatherStation->attach($tempDisplay);
    $weatherStation->attach($humidityDisplay);
    $weatherStation->attach($weatherApp);
    
    // 更新天气数据
    $weatherStation->setMeasurements(25, 60);
    echo "-----\n";
    $weatherStation->setMeasurements(32, 75);
    
    // 移除观察者
    $weatherStation->detach($humidityDisplay);
    echo "-----\n";
    $weatherStation->setMeasurements(8, 45);
?>
```

### 策略模式
```php
<?php
    // 策略接口
    interface PaymentStrategy {
        public function pay($amount);
        public function validate();
    }
    
    // 具体策略
    class CreditCardPayment implements PaymentStrategy {
        private $cardNumber;
        private $cvv;
        private $expiryDate;
        
        public function __construct($cardNumber, $cvv, $expiryDate) {
            $this->cardNumber = $cardNumber;
            $this->cvv = $cvv;
            $this->expiryDate = $expiryDate;
        }
        
        public function validate() {
            // 简单验证
            return strlen($this->cardNumber) == 16 && 
                   strlen($this->cvv) == 3;
        }
        
        public function pay($amount) {
            if (!$this->validate()) {
                return "信用卡信息无效";
            }
            return "使用信用卡支付 ¥{$amount} 成功";
        }
    }
    
    class AlipayPayment implements PaymentStrategy {
        private $account;
        private $password;
        
        public function __construct($account, $password) {
            $this->account = $account;
            $this->password = $password;
        }
        
        public function validate() {
            return !empty($this->account) && !empty($this->password);
        }
        
        public function pay($amount) {
            if (!$this->validate()) {
                return "支付宝账户信息无效";
            }
            return "使用支付宝支付 ¥{$amount} 成功";
        }
    }
    
    class WeChatPayment implements PaymentStrategy {
        private $openid;
        
        public function __construct($openid) {
            $this->openid = $openid;
        }
        
        public function validate() {
            return !empty($this->openid);
        }
        
        public function pay($amount) {
            if (!$this->validate()) {
                return "微信用户信息无效";
            }
            return "使用微信支付 ¥{$amount} 成功";
        }
    }
    
    // 上下文
    class ShoppingCart {
        private $paymentStrategy;
        private $items = [];
        
        public function setPaymentStrategy(PaymentStrategy $strategy) {
            $this->paymentStrategy = $strategy;
        }
        
        public function addItem($name, $price) {
            $this->items[] = ['name' => $name, 'price' => $price];
        }
        
        public function getTotal() {
            return array_sum(array_column($this->items, 'price'));
        }
        
        public function checkout() {
            if (!$this->paymentStrategy) {
                return "请设置支付方式";
            }
            
            $total = $this->getTotal();
            return $this->paymentStrategy->pay($total);
        }
        
        public function getItems() {
            return $this->items;
        }
    }
    
    // 使用示例
    $cart = new ShoppingCart();
    $cart->addItem("笔记本电脑", 5999);
    $cart->addItem("鼠标", 99);
    $cart->addItem("键盘", 299);
    
    // 使用信用卡支付
    $creditCard = new CreditCardPayment("4111111111111111", "123", "12/25");
    $cart->setPaymentStrategy($creditCard);
    echo $cart->checkout();  // 使用信用卡支付 ¥6397 成功
    
    // 切换到支付宝
    $alipay = new AlipayPayment("user@example.com", "password");
    $cart->setPaymentStrategy($alipay);
    echo $cart->checkout();  // 使用支付宝支付 ¥6397 成功
    
    // 切换到微信支付
    $wechat = new WeChatPayment("openid123456");
    $cart->setPaymentStrategy($wechat);
    echo $cart->checkout();  // 使用微信支付 ¥6397 成功
?>
```

## 反射和动态调用

### 反射基础
```php
<?php
    class User {
        public $id;
        public $name;
        private $email;
        protected $age;
        
        public function __construct($id, $name, $email, $age) {
            $this->id = $id;
            $this->name = $name;
            $this->email = $email;
            $this->age = $age;
        }
        
        public function getName() {
            return $this->name;
        }
        
        public function setName($name) {
            $this->name = $name;
        }
        
        private function getSecret() {
            return "这是私有方法";
        }
        
        protected function getProtectedInfo() {
            return "保护信息：{$this->age}";
        }
    }
    
    // 反射类
    $reflectionClass = new ReflectionClass('User');
    
    echo "类名：" . $reflectionClass->getName() . "\n";
    echo "文件：" . $reflectionClass->getFileName() . "\n";
    echo "开始行：" . $reflectionClass->getStartLine() . "\n";
    echo "结束行：" . $reflectionClass->getEndLine() . "\n";
    
    // 获取属性
    $properties = $reflectionClass->getProperties();
    echo "类属性：\n";
    foreach ($properties as $property) {
        $modifiers = Reflection::getModifierNames($property->getModifiers());
        echo "  " . implode(' ', $modifiers) . " " . $property->getName() . "\n";
    }
    
    // 获取方法
    $methods = $reflectionClass->getMethods();
    echo "类方法：\n";
    foreach ($methods as $method) {
        $modifiers = Reflection::getModifierNames($method->getModifiers());
        echo "  " . implode(' ', $modifiers) . " " . $method->getName() . "()\n";
    }
    
    // 创建实例
    $instance = $reflectionClass->newInstanceArgs([1, "张三", "zhangsan@email.com", 25]);
    echo "实例创建成功：" . $instance->getName() . "\n";
    
    // 调用私有方法
    $secretMethod = $reflectionClass->getMethod('getSecret');
    $secretMethod->setAccessible(true);  // 使私有方法可访问
    echo $secretMethod->invoke($instance) . "\n";
    
    // 访问私有属性
    $emailProperty = $reflectionClass->getProperty('email');
    $emailProperty->setAccessible(true);
    echo "私有邮箱：" . $emailProperty->getValue($instance) . "\n";
    
    // 修改私有属性
    $emailProperty->setValue($instance, "new@email.com");
    echo "修改后的邮箱：" . $emailProperty->getValue($instance) . "\n";
?>
```

### 动态方法调用
```php
<?php
    class MathUtils {
        public static function add($a, $b) {
            return $a + $b;
        }
        
        public static function multiply($a, $b) {
            return $a * $b;
        }
        
        public static function divide($a, $b) {
            if ($b == 0) {
                throw new InvalidArgumentException("除数不能为0");
            }
            return $a / $b;
        }
        
        public static function power($base, $exponent) {
            return pow($base, $exponent);
        }
    }
    
    // 动态调用静态方法
    $operation = 'add';
    $result = MathUtils::$operation(10, 5);  // 15
    
    // 使用 call_user_func
    $operation = 'multiply';
    $result = call_user_func(['MathUtils', $operation], 4, 3);  // 12
    
    // 使用 call_user_func_array
    $operation = 'power';
    $args = [2, 8];
    $result = call_user_func_array(['MathUtils', $operation], $args);  // 256
    
    // 动态方法调用类
    class Calculator {
        private $history = [];
        
        public function calculate($operation, ...$args) {
            if (method_exists($this, $operation)) {
                $result = $this->$operation(...$args);
                $this->history[] = [
                    'operation' => $operation,
                    'args' => $args,
                    'result' => $result,
                    'time' => date('Y-m-d H:i:s')
                ];
                return $result;
            } else {
                throw new BadMethodCallException("方法 $operation 不存在");
            }
        }
        
        public function add($a, $b) {
            return $a + $b;
        }
        
        public function subtract($a, $b) {
            return $a - $b;
        }
        
        public function getHistory() {
            return $this->history;
        }
    }
    
    // 使用动态计算器
    $calc = new Calculator();
    echo $calc->calculate('add', 10, 5);      // 15
    echo $calc->calculate('subtract', 20, 8); // 12
    
    print_r($calc->getHistory());
?>
```

## 高级特性

### 魔术方法进阶
```php
<?php
    class MagicMethods {
        private $data = [];
        private $readOnlyProperties = ['id', 'created_at'];
        
        public function __construct($id = null) {
            $this->data['id'] = $id ?: uniqid();
            $this->data['created_at'] = date('Y-m-d H:i:s');
        }
        
        // 访问不存在或不可访问的属性
        public function __get($name) {
            if (array_key_exists($name, $this->data)) {
                return $this->data[$name];
            }
            
            // 动态属性
            $method = 'get' . ucfirst($name);
            if (method_exists($this, $method)) {
                return $this->$method();
            }
            
            throw new InvalidArgumentException("属性 $name 不存在");
        }
        
        // 设置不存在或不可访问的属性
        public function __set($name, $value) {
            if (in_array($name, $this->readOnlyProperties)) {
                throw new InvalidArgumentException("属性 $name 是只读的");
            }
            
            $this->data[$name] = $value;
        }
        
        // 检查属性是否存在
        public function __isset($name) {
            return array_key_exists($name, $this->data);
        }
        
        // 删除属性
        public function __unset($name) {
            if (in_array($name, $this->readOnlyProperties)) {
                throw new InvalidArgumentException("不能删除只读属性 $name");
            }
            
            unset($this->data[$name]);
        }
        
        // 调用不存在的方法
        public function __call($name, $arguments) {
            // 方法链式调用
            if (strpos($name, 'set') === 0) {
                $property = strtolower(substr($name, 3));
                if (count($arguments) > 0) {
                    $this->data[$property] = $arguments[0];
                    return $this;  // 返回自身支持链式调用
                }
            }
            
            throw new BadMethodCallException("方法 $name 不存在");
        }
        
        // 调用不存在的静态方法
        public static function __callStatic($name, $arguments) {
            echo "调用静态方法 $name，参数：" . implode(', ', $arguments) . "\n";
            
            // 工厂方法模拟
            if ($name === 'create') {
                return new self(...$arguments);
            }
        }
        
        // 将对象转换为字符串
        public function __toString() {
            return json_encode($this->data, JSON_UNESCAPED_UNICODE);
        }
        
        // 将对象调用为函数
        public function __invoke($value) {
            if (is_string($value)) {
                $this->data['name'] = $value;
            } elseif (is_array($value)) {
                $this->data = array_merge($this->data, $value);
            }
            return $this;
        }
        
        // 克隆对象
        public function __clone() {
            // 重置ID和创建时间
            $this->data['id'] = uniqid();
            $this->data['created_at'] = date('Y-m-d H:i:s');
        }
        
        // 调试信息
        public function __debugInfo() {
            return [
                'id' => $this->data['id'],
                'created_at' => $this->data['created_at'],
                'properties_count' => count($this->data)
            ];
        }
    }
    
    // 使用示例
    $obj = MagicMethods::create();  // 静态调用
    
    // 设置和获取属性
    $obj->name = "张三";
    $obj->email = "zhangsan@email.com";
    
    echo $obj->name;  // 张三
    
    // 链式调用
    $obj->setAge(25)->setCity("北京");
    
    // 函数式调用
    $obj(["phone" => "13800138000"]);
    
    // 对象转字符串
    echo $obj;  // JSON格式的数据
    
    // 克隆
    $clonedObj = clone $obj;
    
    // 调试
    var_dump($obj);
?>
```

## 最佳实践

1. **SOLID原则**：遵循单一职责、开闭、里氏替换、接口隔离、依赖倒置原则。
2. **设计模式**：适当使用设计模式解决特定问题，避免过度设计。
3. **封装性**：合理使用访问修饰符，保护内部状态。
4. **接口编程**：面向接口而不是具体实现编程。
5. **依赖注入**：使用依赖注入提高代码的可测试性和灵活性。
6. **自动加载**：使用自动加载机制管理类文件。
7. **文档注释**：为类、方法、属性添加完整的文档注释。