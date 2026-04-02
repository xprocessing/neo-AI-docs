# PHP基础语法

## PHP标记

PHP代码必须包含在特殊的标记中：

```php
<?php
    // PHP代码在这里
    echo "Hello, World!";
?>
```

**简短标记（不推荐在生产环境使用）：**
```php
<? 
    echo "简短标记";
?>

<?= "直接输出表达式" ?>  // 等同于 <?php echo "直接输出表达式"; ?>
```

## 注释

```php
<?php
    // 单行注释
    
    # 也是单行注释（Shell风格）
    
    /*
     * 多行注释
     * 可以跨越多行
     */
    
    /**
     * 文档注释
     * 用于生成API文档
     * @param string $name 参数说明
     * @return string 返回值说明
     */
    function greet($name) {
        return "Hello, " . $name;
    }
?>
```

## 输出内容

```php
<?php
    // echo - 输出一个或多个字符串
    echo "Hello World";
    echo "Hello", "World"; // 可以输出多个字符串
    
    // print - 输出字符串（返回值总是1）
    print "Hello World";
    
    // print_r - 打印数组或对象（易于阅读）
    $arr = array(1, 2, 3);
    print_r($arr);
    
    // var_dump - 显示变量类型和值
    $str = "Hello";
    var_dump($str);
    
    // printf - 格式化输出
    $name = "张三";
    $age = 25;
    printf("姓名：%s，年龄：%d", $name, $age);
?>
```

## 语句结束符

```php
<?php
    echo "语句1";     // 每个语句以分号结束
    
    echo "语句2"; echo "语句3"; // 同一行可以有多个语句
    
    echo "语句4"  // PHP结束标记前的语句可以省略分号
?>
```

## 大小写敏感

```php
<?php
    // 变量名区分大小写
    $name = "张三";
    $NAME = "李四";
    echo $name; // 输出：张三
    echo $NAME; // 输出：李四
    
    // 函数名不区分大小写
    function hello() {
        return "Hello";
    }
    echo hello();   // Hello
    echo HELLO();   // Hello
    echo HeLLo();   // Hello
    
    // 类名不区分大小写（但建议保持一致）
    class MyClass {}
    $obj = new myclass(); // 可以
?>
```

## 引入文件

```php
<?php
    // include - 引入文件，如果失败只产生警告
    include 'config.php';
    
    // require - 引入文件，如果失败产生致命错误
    require 'database.php';
    
    // include_once - 只引入一次（避免重复包含）
    include_once 'functions.php';
    
    // require_once - 只引入一次（失败时致命错误）
    require_once 'classes.php';
?>
```

## 第一个PHP程序

```php
<!DOCTYPE html>
<html>
<head>
    <title>我的第一个PHP页面</title>
</head>
<body>
    <h1>
        <?php 
            $greeting = "欢迎来到PHP世界";
            echo $greeting; 
        ?>
    </h1>
    
    <p>
        当前时间：<?php echo date('Y-m-d H:i:s'); ?>
    </p>
</body>
</html>
```

## 嵌入HTML中的PHP

```php
<?php
    $pageTitle = "用户列表";
    $users = array("张三", "李四", "王五");
?>

<!DOCTYPE html>
<html>
<head>
    <title><?php echo $pageTitle; ?></title>
</head>
<body>
    <h1><?php echo $pageTitle; ?></h1>
    
    <ul>
        <?php foreach ($users as $user): ?>
            <li><?php echo htmlspecialchars($user); ?></li>
        <?php endforeach; ?>
    </ul>
</body>
</html>
```

## 开发环境配置检查

```php
<?php
    // 显示PHP信息
    phpinfo();
    
    // 检查PHP版本
    echo "PHP版本：" . phpversion() . "\n";
    
    // 检查扩展是否加载
    if (extension_loaded('mysqli')) {
        echo "MySQLi扩展已加载\n";
    } else {
        echo "MySQLi扩展未加载\n";
    }
    
    // 显示已加载的扩展
    print_r(get_loaded_extensions());
?>
```

## 最佳实践

1. **始终使用 `<?php ?>` 标记**：避免使用简短标记以确保代码的可移植性。
2. **文件编码**：保存PHP文件时使用UTF-8编码（无BOM）。
3. **错误报告**：开发时开启所有错误报告：
   ```php
   error_reporting(E_ALL);
   ini_set('display_errors', 1);
   ```
4. **代码缩进**：使用4个空格进行缩进，保持代码整洁。
5. **命名规范**：变量和函数使用小写字母和下划线，类名使用帕斯卡命名法。