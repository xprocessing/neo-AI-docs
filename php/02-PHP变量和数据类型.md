# PHP变量和数据类型

## 变量声明和使用

### 变量命名规则
```php
<?php
    // 变量必须以美元符号 $ 开头
    $name = "张三";
    $age = 25;
    $salary = 5000.50;
    
    // 变量名规则：
    // 1. 必须以字母或下划线开头
    // 2. 只能包含字母、数字和下划线
    // 3. 区分大小写
    $firstName = "李";
    $first_name = "李";  // 推荐使用下划线命名法
    $_private = "私有变量";
    
    // 错误的变量名
    // $123name = "错误";  // 不能以数字开头
    // $user-name = "错误"; // 不能包含连字符
?>
```

### 可变变量
```php
<?php
    $name = "username";
    $username = "admin";
    
    echo $$name;  // 输出 "admin"
    
    // 多重可变变量
    $a = "b";
    $b = "c";
    $c = "hello";
    
    echo $$$a;  // 输出 "hello"
?>
```

## 数据类型

### 标量类型
```php
<?php
    // 1. 整型 (integer)
    $int1 = 123;
    $int2 = -456;
    $int3 = 0x1A;    // 十六进制
    $int4 = 0123;    // 八进制
    $int5 = 0b1010;  // 二进制 (PHP 5.4+)
    
    // 2. 浮点型 (float/double)
    $float1 = 3.14;
    $float2 = 1.2e3; // 科学计数法 (1200)
    $float3 = 7E-10; // 0.0000000007
    
    // 3. 字符串 (string)
    $str1 = '单引号字符串';
    $str2 = "双引号字符串";
    $str3 = "支持转义字符：\n\t\\\"";
    $str4 = '不解析变量：$name';
    $name = "张三";
    $str5 = "解析变量：$name";
    
    // 4. 布尔型 (boolean)
    $bool1 = true;
    $bool2 = false;
    
    // 类型检查
    var_dump(is_int($int1));      // bool(true)
    var_dump(is_string($str1));   // bool(true)
    var_dump(is_bool($bool1));    // bool(true)
    var_dump(is_float($float1));  // bool(true)
?>
```

### 复合类型
```php
<?php
    // 1. 数组 (array)
    $arr1 = array(1, 2, 3);
    $arr2 = [1, 2, 3];  // PHP 5.4+ 简化语法
    
    // 关联数组
    $person = array(
        "name" => "张三",
        "age" => 25,
        "city" => "北京"
    );
    
    // 多维数组
    $users = array(
        array("name" => "张三", "age" => 25),
        array("name" => "李四", "age" => 30)
    );
    
    // 2. 对象 (object)
    class User {
        public $name = "张三";
        public $age = 25;
        
        public function sayHello() {
            return "Hello, I'm " . $this->name;
        }
    }
    
    $user = new User();
    echo $user->name;  // 输出：张三
    echo $user->sayHello();  // 输出：Hello, I'm 张三
?>
```

### 特殊类型
```php
<?php
    // 1. NULL
    $var1 = null;
    $var2;  // 未声明的变量也是null
    
    // 2. 资源 (resource)
    $file = fopen("test.txt", "r");  // 文件资源
    $conn = mysqli_connect("localhost", "user", "pass");  // 数据库连接资源
    
    // 类型检查
    var_dump(is_null($var1));   // bool(true)
    var_dump(is_resource($file)); // bool(true)
    
    // 释放资源
    fclose($file);
    mysqli_close($conn);
?>
```

## 类型转换

### 自动类型转换
```php
<?php
    // 字符串到数字的转换
    $str = "123";
    $num = $str + 5;  // 128
    
    $str2 = "45.6abc";
    $num2 = $str2 + 10;  // 55.6
    
    $str3 = "abc123";
    $num3 = $str3 + 5;  // 5
    
    // 布尔值转换
    $bool = true;
    $result = $bool + 10;  // 11
    
    // 数组转换
    $arr = array(1, 2, 3);
    $count = count($arr);  // 3
?>
```

### 强制类型转换
```php
<?php
    $str = "123.45abc";
    
    // 转换为整型
    $int = (int)$str;        // 123
    $int2 = intval($str);    // 123
    
    // 转换为浮点型
    $float = (float)$str;    // 123.45
    $float2 = floatval($str); // 123.45
    
    // 转换为字符串
    $num = 123;
    $str = (string)$num;     // "123"
    $str2 = strval($num);    // "123"
    
    // 转换为布尔型
    $value = 0;
    $bool = (bool)$value;    // false
    $bool2 = boolval($value); // false
    
    // 转换为数组
    $obj = new stdClass();
    $arr = (array)$obj;      // 对象转换为数组
    
    // 转换为对象
    $arr = array("name" => "张三");
    $obj = (object)$arr;     // 数组转换为对象
?>
```

## 字符串操作

### 字符串定义和连接
```php
<?php
    // 单引号和双引号
    $single = '这是单引号字符串';
    $double = "这是双引号字符串";
    
    // 字符串连接
    $str1 = "Hello";
    $str2 = "World";
    $result = $str1 . " " . $str2;  // "Hello World"
    
    // Heredoc语法
    $html = <<<HTML
    <!DOCTYPE html>
    <html>
    <head><title>标题</title></head>
    <body>
        <h1>内容</h1>
    </body>
    </html>
HTML;
    
    // Nowdoc语法 (PHP 5.3+)
    $text = <<<'TEXT'
    这是Nowdoc字符串
    不会解析变量和特殊字符
TEXT;
?>
```

### 字符串函数
```php
<?php
    $text = "Hello World Programming";
    
    // 长度
    echo strlen($text);  // 25
    
    // 查找
    echo strpos($text, "World");  // 6
    echo strpos($text, "PHP");    // false
    
    // 提取子字符串
    echo substr($text, 6, 5);    // "World"
    echo substr($text, -11);     // "Programming"
    
    // 替换
    echo str_replace("World", "PHP", $text);  // "Hello PHP Programming"
    
    // 大小写转换
    echo strtoupper($text);  // "HELLO WORLD PROGRAMMING"
    echo strtolower($text);  // "hello world programming"
    echo ucfirst($text);    // "Hello world programming"
    echo ucwords($text);     // "Hello World Programming"
    
    // 去除空白
    $trimmed = "  hello  ";
    echo trim($trimmed);     // "hello"
    echo ltrim($trimmed);    // "hello  "
    echo rtrim($trimmed);    // "  hello"
    
    // 分割和连接
    $str = "apple,banana,orange";
    $arr = explode(",", $str);  // ["apple", "banana", "orange"]
    $newStr = implode(" | ", $arr);  // "apple | banana | orange"
    
    // 安全输出（防止XSS）
    $userInput = "<script>alert('hack')</script>";
    echo htmlspecialchars($userInput);  // 转义HTML特殊字符
?>
```

## 常量

### 定义常量
```php
<?php
    // 使用 define() 函数
    define("SITE_NAME", "我的网站");
    define("MAX_USERS", 1000);
    define("PI", 3.14159);
    
    // const 关键字 (PHP 5.3+)
    const APP_VERSION = "1.0.0";
    const DEBUG_MODE = true;
    
    // 类常量
    class Database {
        const HOST = "localhost";
        const PORT = 3306;
        const CHARSET = "utf8mb4";
    }
    
    // 使用常量
    echo SITE_NAME;           // "我的网站"
    echo Database::HOST;      // "localhost"
    
    // 魔术常量
    echo __LINE__;    // 当前行号
    echo __FILE__;    // 当前文件路径
    echo __DIR__;     // 当前目录路径
    echo __FUNCTION__; // 当前函数名
    echo __CLASS__;   // 当前类名
    echo __METHOD__;  // 当前方法名
    echo __NAMESPACE__; // 当前命名空间
?>
```

## 数组操作

### 数组创建和访问
```php
<?php
    // 索引数组
    $fruits = array("apple", "banana", "orange");
    $fruits2 = ["apple", "banana", "orange"];  // 简化语法
    
    echo $fruits[0];  // "apple"
    $fruits[1] = "grape";  // 修改元素
    
    // 关联数组
    $person = array(
        "name" => "张三",
        "age" => 25,
        "city" => "北京"
    );
    
    echo $person["name"];  // "张三"
    $person["email"] = "zhangsan@email.com";  // 添加元素
    
    // 混合数组
    $mixed = [
        "first",
        "name" => "张三",
        20,
        "city" => "北京"
    ];
?>
```

### 数组常用函数
```php
<?php
    $arr = [3, 1, 4, 1, 5, 9, 2, 6];
    
    // 排序
    sort($arr);           // 升序排序
    rsort($arr);          // 降序排序
    asort($assoc);        // 关联数组按键值排序
    ksort($assoc);        // 关联数组按键排序
    
    // 搜索
    $index = array_search(4, $arr);  // 查找元素索引
    $exists = in_array(5, $arr);      // 检查元素是否存在
    
    // 添加和删除
    array_push($arr, 10);  // 在末尾添加
    array_pop($arr);        // 从末尾删除
    array_shift($arr);      // 从开头删除
    array_unshift($arr, 0); // 在开头添加
    
    // 数组合并
    $arr1 = [1, 2, 3];
    $arr2 = [4, 5, 6];
    $merged = array_merge($arr1, $arr2);  // [1,2,3,4,5,6]
    
    // 数组切片
    $slice = array_slice($arr, 2, 3);  // 从索引2开始取3个元素
    
    // 键值操作
    $keys = array_keys($assoc);         // 获取所有键
    $values = array_values($assoc);     // 获取所有值
    $flipped = array_flip($assoc);      // 交换键和值
    
    // 数组遍历
    foreach ($arr as $value) {
        echo $value . "\n";
    }
    
    foreach ($assoc as $key => $value) {
        echo "$key: $value\n";
    }
?>
```

## 变量作用域

### 全局和局部变量
```php
<?php
    $globalVar = "全局变量";
    
    function testScope() {
        $localVar = "局部变量";
        global $globalVar;  // 声明使用全局变量
        
        echo $globalVar;  // 访问全局变量
        echo $localVar;   // 访问局部变量
        
        // 使用 $GLOBALS 超全局数组
        echo $GLOBALS['globalVar'];
    }
    
    testScope();
    
    // 静态变量
    function counter() {
        static $count = 0;  // 只初始化一次
        $count++;
        return $count;
    }
    
    echo counter();  // 1
    echo counter();  // 2
    echo counter();  // 3
?>
```

### 超全局变量
```php
<?php
    // $_GET - URL参数
    // $_POST - POST数据
    // $_REQUEST - GET和POST数据
    // $_SERVER - 服务器和环境信息
    // $_FILES - 上传文件信息
    // $_COOKIE - Cookie数据
    // $_SESSION - Session数据
    // $_ENV - 环境变量
    // $GLOBALS - 全局变量引用
    
    echo $_SERVER['PHP_SELF'];     // 当前脚本路径
    echo $_SERVER['REQUEST_METHOD']; // 请求方法
    echo $_SERVER['HTTP_USER_AGENT']; // 用户代理信息
?>
```

## 最佳实践

1. **变量命名**：使用有意义的变量名，遵循命名规范。
2. **类型检查**：在需要严格类型检查时使用类型声明。
3. **NULL检查**：在使用变量前检查是否为NULL。
4. **字符串安全**：输出用户输入时使用htmlspecialchars()防止XSS。
5. **数组操作**：使用内置函数而不是手动循环来操作数组。
6. **常量使用**：对于不会改变的值使用常量而不是变量。