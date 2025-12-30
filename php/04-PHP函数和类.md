# PHP函数和类

## 函数基础

### 定义和调用函数
```php
<?php
    // 基本函数定义
    function sayHello() {
        return "Hello, World!";
    }
    
    // 调用函数
    echo sayHello();  // 输出：Hello, World!
    
    // 带参数的函数
    function greet($name) {
        return "Hello, " . $name . "!";
    }
    
    echo greet("张三");  // 输出：Hello, 张三!
    
    // 带默认参数的函数
    function createButton($text, $color = "blue", $size = "medium") {
        return "<button style='color: $color; size: $size'>$text</button>";
    }
    
    echo createButton("点击我");  // 使用默认参数
    echo createButton("提交", "green", "large");  // 自定义参数
?>
```

### 参数传递方式
```php
<?php
    // 值传递（默认）
    function doubleValue($number) {
        $number = $number * 2;
        return $number;
    }
    
    $x = 5;
    $result = doubleValue($x);
    echo $x;       // 5 (原值不变)
    echo $result;  // 10
    
    // 引用传递
    function doubleValueByRef(&$number) {
        $number = $number * 2;
    }
    
    $y = 5;
    doubleValueByRef($y);
    echo $y;  // 10 (原值被修改)
    
    // 混合参数类型
    function processMixed($required, $optional = "default", &$reference = null) {
        echo "必须参数：$required\n";
        echo "可选参数：$optional\n";
        if ($reference !== null) {
            $reference = "被修改了";
        }
    }
    
    $var = "原始值";
    processMixed("必须值", "可选值", $var);
    echo $var;  // "被修改了"
?>
```

### 返回值
```php
<?php
    // 单个返回值
    function add($a, $b) {
        return $a + $b;
    }
    
    // 多个返回值（使用数组）
    function getUserInfo($userId) {
        // 模拟数据库查询
        $users = [
            1 => ["name" => "张三", "email" => "zhangsan@email.com", "age" => 25],
            2 => ["name" => "李四", "email" => "lisi@email.com", "age" => 30]
        ];
        
        return $users[$userId] ?? null;
    }
    
    $userInfo = getUserInfo(1);
    if ($userInfo) {
        echo "姓名：" . $userInfo['name'] . "\n";
        echo "邮箱：" . $userInfo['email'] . "\n";
    }
    
    // 使用 list() 或 [] 接收多个值
    function getMinMax($numbers) {
        return [min($numbers), max($numbers)];
    }
    
    $nums = [3, 1, 4, 1, 5, 9];
    [$min, $max] = getMinMax($nums);
    echo "最小值：$min，最大值：$max\n";
    
    // 返回引用
    function &getReference() {
        static $value = 100;
        return $value;
    }
    
    $ref = &getReference();
    $ref = 200;
    echo getReference();  // 200
?>
```

## 函数高级特性

### 可变参数函数
```php
<?php
    // 使用 func_get_args() (PHP 5.5及以下)
    function sumOld() {
        $args = func_get_args();
        $total = 0;
        foreach ($args as $arg) {
            $total += $arg;
        }
        return $total;
    }
    
    echo sumOld(1, 2, 3, 4, 5);  // 15
    
    // 使用 ... 操作符 (PHP 5.6+)
    function sum(...$numbers) {
        return array_sum($numbers);
    }
    
    echo sum(1, 2, 3, 4, 5);  // 15
    
    // 参数解包
    $numbers = [1, 2, 3, 4, 5];
    echo sum(...$numbers);  // 15
    
    // 混合使用
    function processString($prefix, ...$strings) {
        foreach ($strings as $string) {
            echo $prefix . $string . "\n";
        }
    }
    
    processString("项目：", "项目A", "项目B", "项目C");
?>
```

### 可变函数
```php
<?php
    function add($a, $b) {
        return $a + $b;
    }
    
    function subtract($a, $b) {
        return $a - $b;
    }
    
    function multiply($a, $b) {
        return $a * $b;
    }
    
    // 使用变量调用函数
    $operation = "add";
    $result = $operation(10, 5);  // 15
    
    $operation = "subtract";
    $result = $operation(10, 5);  // 5
    
    // 计算器示例
    function calculate($a, $b, $operation) {
        $validOperations = ["add", "subtract", "multiply", "divide"];
        
        if (!in_array($operation, $validOperations)) {
            throw new InvalidArgumentException("无效的操作");
        }
        
        return $operation($a, $b);
    }
    
    echo calculate(10, 5, "multiply");  // 50
?>
```

### 匿名函数（闭包）
```php
<?php
    // 基本匿名函数
    $greet = function($name) {
        return "Hello, $name!";
    };
    
    echo $greet("张三");  // Hello, 张三!
    
    // 作为参数传递
    $numbers = [1, 2, 3, 4, 5];
    $squared = array_map(function($n) {
        return $n * $n;
    }, $numbers);
    
    print_r($squared);  // [1, 4, 9, 16, 25]
    
    // 使用 use 关键字捕获外部变量
    $multiplier = 3;
    $multiply = function($n) use ($multiplier) {
        return $n * $multiplier;
    };
    
    echo $multiply(4);  // 12
    
    // 按引用捕获
    $count = 0;
    $counter = function() use (&$count) {
        $count++;
        return $count;
    };
    
    echo $counter();  // 1
    echo $counter();  // 2
    echo $count;      // 2
    
    // 作为回调函数
    $users = [
        ["name" => "张三", "age" => 25],
        ["name" => "李四", "age" => 30],
        ["name" => "王五", "age" => 20]
    ];
    
    // 按年龄排序
    usort($users, function($a, $b) {
        return $a['age'] - $b['age'];
    });
    
    // 自定义排序函数
    function sortBy($array, $key, $ascending = true) {
        usort($array, function($a, $b) use ($key, $ascending) {
            $result = $a[$key] <=> $b[$key];
            return $ascending ? $result : -$result;
        });
        return $array;
    }
    
    $sortedByName = sortBy($users, 'name');
    $sortedByAgeDesc = sortBy($users, 'age', false);
?>
```

### 递归函数
```php
<?php
    // 阶乘计算
    function factorial($n) {
        if ($n <= 1) {
            return 1;
        }
        return $n * factorial($n - 1);
    }
    
    echo factorial(5);  // 120
    
    // 斐波那契数列
    function fibonacci($n) {
        if ($n <= 2) {
            return 1;
        }
        return fibonacci($n - 1) + fibonacci($n - 2);
    }
    
    // 优化版斐波那契（使用记忆化）
    function fibonacciMemo($n, &$memo = []) {
        if (isset($memo[$n])) {
            return $memo[$n];
        }
        
        if ($n <= 2) {
            return 1;
        }
        
        $memo[$n] = fibonacciMemo($n - 1, $memo) + fibonacciMemo($n - 2, $memo);
        return $memo[$n];
    }
    
    // 目录遍历
    function listFiles($dir, $recursive = false) {
        $files = [];
        
        if (is_dir($dir)) {
            $items = scandir($dir);
            foreach ($items as $item) {
                if ($item == '.' || $item == '..') {
                    continue;
                }
                
                $path = $dir . DIRECTORY_SEPARATOR . $item;
                if (is_file($path)) {
                    $files[] = $path;
                } elseif ($recursive && is_dir($path)) {
                    $files = array_merge($files, listFiles($path, true));
                }
            }
        }
        
        return $files;
    }
?>
```

## 类的基础

### 类的定义和实例化
```php
<?php
    // 基本类定义
    class User {
        // 属性
        public $name;
        public $email;
        private $age;
        protected $status = 'active';
        
        // 构造方法
        public function __construct($name, $email, $age) {
            $this->name = $name;
            $this->email = $email;
            $this->age = $age;
        }
        
        // 方法
        public function getInfo() {
            return "姓名：{$this->name}，邮箱：{$this->email}";
        }
        
        public function getAge() {
            return $this->age;
        }
        
        public function setAge($age) {
            if ($age >= 0 && $age <= 150) {
                $this->age = $age;
                return true;
            }
            return false;
        }
        
        // 析构方法
        public function __destruct() {
            echo "用户 {$this->name} 对象被销毁\n";
        }
    }
    
    // 实例化对象
    $user1 = new User("张三", "zhangsan@email.com", 25);
    $user2 = new User("李四", "lisi@email.com", 30);
    
    // 访问属性和方法
    echo $user1->name;           // 张三
    echo $user1->getInfo();      // 姓名：张三，邮箱：zhangsan@email.com
    echo $user1->getAge();       // 25
    
    // 调用公共方法
    $user1->setAge(26);
    echo $user1->getAge();       // 26
    
    // 不能访问私有属性
    // echo $user1->age;  // 错误：不能访问私有属性
?>
```

### 属性和方法
```php
<?php
    class Product {
        // 静态属性
        public static $count = 0;
        
        // 实例属性
        public $id;
        public $name;
        public $price;
        private $stock;
        
        // 静态方法
        public static function getCount() {
            return self::$count;
        }
        
        // 构造方法
        public function __construct($id, $name, $price, $stock) {
            $this->id = $id;
            $this->name = $name;
            $this->price = $price;
            $this->stock = $stock;
            self::$count++;
        }
        
        // 实例方法
        public function getInfo() {
            return "商品：{$this->name}，价格：¥{$this->price}";
        }
        
        public function sell($quantity) {
            if ($quantity <= $this->stock) {
                $this->stock -= $quantity;
                return true;
            }
            return false;
        }
        
        public function restock($quantity) {
            $this->stock += $quantity;
        }
        
        public function getStock() {
            return $this->stock;
        }
        
        // 魔术方法
        public function __toString() {
            return "Product(#{$this->id}: {$this->name})";
        }
        
        public function __get($name) {
            if ($name === 'stock') {
                return $this->stock;
            }
            return null;
        }
        
        public function __set($name, $value) {
            if ($name === 'stock' && is_numeric($value) && $value >= 0) {
                $this->stock = $value;
            }
        }
    }
    
    // 使用示例
    $product1 = new Product(1, "笔记本电脑", 5999, 10);
    $product2 = new Product(2, "手机", 2999, 20);
    
    echo Product::getCount();  // 2
    
    echo $product1->getInfo();  // 商品：笔记本电脑，价格：¥5999
    echo $product1;             // Product(#1: 笔记本电脑)
    
    // 通过魔术方法访问私有属性
    echo $product1->stock;     // 10 (通过__get)
    $product1->stock = 15;     // 通过__set
    echo $product1->getStock(); // 15
?>
```

### 继承
```php
<?php
    // 父类
    class Vehicle {
        protected $brand;
        protected $model;
        protected $year;
        
        public function __construct($brand, $model, $year) {
            $this->brand = $brand;
            $this->model = $model;
            $this->year = $year;
        }
        
        public function start() {
            return "{$this->brand} {$this->model} 启动了";
        }
        
        public function stop() {
            return "{$this->brand} {$this->model} 停止了";
        }
        
        public function getInfo() {
            return "{$this->year}年 {$this->brand} {$this->model}";
        }
    }
    
    // 子类
    class Car extends Vehicle {
        private $doors;
        private $fuelType;
        
        public function __construct($brand, $model, $year, $doors, $fuelType) {
            // 调用父类构造方法
            parent::__construct($brand, $model, $year);
            
            $this->doors = $doors;
            $this->fuelType = $fuelType;
        }
        
        // 重写父类方法
        public function start() {
            $parentStart = parent::start();
            return $parentStart . "（燃油类型：{$this->fuelType}）";
        }
        
        // 新增方法
        public function openTrunk() {
            return "后备箱已打开";
        }
        
        public function getDetailedInfo() {
            return $this->getInfo() . "，{$this->doors}门，{$this->fuelType}";
        }
    }
    
    // 另一个子类
    class Motorcycle extends Vehicle {
        private $type;
        
        public function __construct($brand, $model, $year, $type) {
            parent::__construct($brand, $model, $year);
            $this->type = $type;
        }
        
        public function wheelie() {
            return "{$this->brand} {$this->model} 正在翘头！";
        }
        
        public function getInfo() {
            return parent::getInfo() . "（{$this->type}摩托车）";
        }
    }
    
    // 使用示例
    $car = new Car("丰田", "卡罗拉", 2022, 4, "汽油");
    echo $car->start();              // 丰田 卡罗拉 启动了（燃油类型：汽油）
    echo $car->getDetailedInfo();    // 2022年 丰田 卡罗拉，4门，汽油
    
    $motorcycle = new Motorcycle("本田", "CBR650R", 2021, "运动型");
    echo $motorcycle->start();       // 本田 CBR650R 启动了
    echo $motorcycle->wheelie();     // 本田 CBR650R 正在翘头！
?>
```

### 接口和抽象类
```php
<?php
    // 接口定义
    interface Logger {
        public function log($message);
        public function error($errorMessage);
    }
    
    interface Database {
        public function connect();
        public function query($sql);
        public function disconnect();
    }
    
    // 抽象类
    abstract class Animal {
        protected $name;
        protected $age;
        
        public function __construct($name, $age) {
            $this->name = $name;
            $this->age = $age;
        }
        
        // 具体方法
        public function getInfo() {
            return "{$this->name}，{$this->age}岁";
        }
        
        // 抽象方法（子类必须实现）
        abstract public function makeSound();
        abstract public function move();
    }
    
    // 实现接口
    class FileLogger implements Logger {
        private $logFile;
        
        public function __construct($filename) {
            $this->logFile = $filename;
        }
        
        public function log($message) {
            $timestamp = date('Y-m-d H:i:s');
            $logEntry = "[{$timestamp}] INFO: {$message}\n";
            file_put_contents($this->logFile, $logEntry, FILE_APPEND);
        }
        
        public function error($errorMessage) {
            $timestamp = date('Y-m-d H:i:s');
            $logEntry = "[{$timestamp}] ERROR: {$errorMessage}\n";
            file_put_contents($this->logFile, $logEntry, FILE_APPEND);
        }
    }
    
    // 继承抽象类
    class Dog extends Animal {
        public function makeSound() {
            return "汪汪汪";
        }
        
        public function move() {
            return "奔跑";
        }
        
        public function wagTail() {
            return "摇尾巴";
        }
    }
    
    class Cat extends Animal {
        public function makeSound() {
            return "喵喵喵";
        }
        
        public function move() {
            return "潜行";
        }
        
        public function purr() {
            return "呼噜呼噜";
        }
    }
    
    // 使用示例
    $logger = new FileLogger("app.log");
    $logger->log("应用启动");
    $logger->error("数据库连接失败");
    
    $dog = new Dog("旺财", 3);
    echo $dog->getInfo() . "说：" . $dog->makeSound();  // 旺财，3岁说：汪汪汪
    
    $cat = new Cat("咪咪", 2);
    echo $cat->getInfo() . "正在" . $cat->move();       // 咪咪，2岁正在潜行
?>
```

## 命名空间

### 基本用法
```php
<?php
    // 命名空间声明
    namespace App\Models;
    
    class User {
        public $id;
        public $name;
        
        public function __construct($id, $name) {
            $this->id = $id;
            $this->name = $name;
        }
    }
    
    namespace App\Controllers;
    
    class UserController {
        private $userModel;
        
        public function __construct() {
            // 使用完全限定名称
            $this->userModel = new \App\Models\User(1, "张三");
        }
        
        public function show() {
            return $this->userModel->name;
        }
    }
    
    namespace App\Services;
    
    class UserService {
        // 导入类
        use \App\Models\User;
        
        public function createUser($name) {
            return new User(2, $name);
        }
    }
    
    namespace {
        // 全局命名空间
        // 使用 use 导入
        use App\Controllers\UserController;
        use App\Models\User as UserModel;
        
        $controller = new UserController();
        echo $controller->show();
        
        $user = new UserModel(3, "李四");
        echo $user->name;
    }
?>
```

### 多文件命名空间
```php
<?php
    // 文件：src/Models/User.php
    namespace App\Models;
    
    class User {
        public $id;
        public $name;
    }
    
    // 文件：src/Controllers/UserController.php
    namespace App\Controllers;
    
    use App\Models\User;
    
    class UserController {
        public function create($name) {
            return new User(rand(1, 1000), $name);
        }
    }
    
    // 文件：index.php
    require_once 'src/Models/User.php';
    require_once 'src/Controllers/UserController.php';
    
    use App\Controllers\UserController;
    
    $controller = new UserController();
    $user = $controller->create("王五");
    echo $user->name;  // 王五
?>
```

## Trait（特征）

### 基本用法
```php
<?php
    // 定义 Trait
    trait Loggable {
        protected $logs = [];
        
        public function log($message) {
            $timestamp = date('Y-m-d H:i:s');
            $this->logs[] = "[{$timestamp}] {$message}";
        }
        
        public function getLogs() {
            return $this->logs;
        }
        
        public function clearLogs() {
            $this->logs = [];
        }
    }
    
    trait Timestampable {
        public $createdAt;
        public $updatedAt;
        
        public function setCreatedAt() {
            $this->createdAt = date('Y-m-d H:i:s');
        }
        
        public function setUpdatedAt() {
            $this->updatedAt = date('Y-m-d H:i:s');
        }
        
        public function getTimestamps() {
            return [
                'created' => $this->createdAt,
                'updated' => $this->updatedAt
            ];
        }
    }
    
    // 使用 Trait
    class Product {
        use Loggable, Timestampable;
        
        public $id;
        public $name;
        
        public function __construct($id, $name) {
            $this->id = $id;
            $this->name = $name;
            $this->setCreatedAt();
            $this->log("产品创建：{$name}");
        }
        
        public function updateName($newName) {
            $oldName = $this->name;
            $this->name = $newName;
            $this->setUpdatedAt();
            $this->log("产品名称从 {$oldName} 更新为 {$newName}");
        }
    }
    
    class User {
        use Loggable, Timestampable;
        
        public $id;
        public $name;
        
        public function __construct($id, $name) {
            $this->id = $id;
            $this->name = $name;
            $this->setCreatedAt();
            $this->log("用户创建：{$name}");
        }
        
        public function changeName($newName) {
            $oldName = $this->name;
            $this->name = $newName;
            $this->setUpdatedAt();
            $this->log("用户名从 {$oldName} 更新为 {$newName}");
        }
    }
    
    // 使用示例
    $product = new Product(1, "笔记本电脑");
    $product->updateName("游戏笔记本");
    
    $user = new User(1, "张三");
    $user->changeName("张小三");
    
    // 获取日志
    echo "产品日志：\n";
    print_r($product->getLogs());
    
    echo "用户日志：\n";
    print_r($user->getLogs());
?>
```

## 最佳实践

1. **单一职责原则**：每个函数和类应该只做一件事。
2. **命名规范**：使用清晰、描述性的名称。
3. **参数验证**：在函数开始时验证参数。
4. **错误处理**：适当使用异常处理错误情况。
5. **代码复用**：使用继承、Trait等方式复用代码。
6. **文档注释**：为复杂的函数和类添加文档注释。
7. **访问控制**：合理使用public、private、protected修饰符。