# PHP控制结构

## 条件语句

### if语句
```php
<?php
    $score = 85;
    
    // 基本if语句
    if ($score >= 60) {
        echo "及格";
    }
    
    // if-else语句
    if ($score >= 80) {
        echo "优秀";
    } else {
        echo "良好";
    }
    
    // if-elseif-else语句
    if ($score >= 90) {
        echo "优秀";
    } elseif ($score >= 80) {
        echo "良好";
    } elseif ($score >= 60) {
        echo "及格";
    } else {
        echo "不及格";
    }
    
    // 嵌套if语句
    $age = 20;
    $hasLicense = true;
    
    if ($age >= 18) {
        if ($hasLicense) {
            echo "可以开车";
        } else {
            echo "需要先考取驾照";
        }
    } else {
        echo "年龄不够";
    }
?>
```

### switch语句
```php
<?php
    $day = "Monday";
    
    switch ($day) {
        case "Monday":
            echo "星期一";
            break;
        case "Tuesday":
            echo "星期二";
            break;
        case "Wednesday":
            echo "星期三";
            break;
        case "Thursday":
            echo "星期四";
            break;
        case "Friday":
            echo "星期五";
            break;
        case "Saturday":
        case "Sunday":
            echo "周末";
            break;
        default:
            echo "无效的日期";
            break;
    }
    
    // switch的另一种用法
    $grade = 'B';
    switch ($grade) {
        case 'A':
        case 'B':
            echo "成绩优秀";
            break;
        case 'C':
            echo "成绩良好";
            break;
        case 'D':
            echo "成绩及格";
            break;
        case 'F':
            echo "需要补考";
            break;
    }
    
    // switch表达式 (PHP 8.0+)
    $result = match ($grade) {
        'A', 'B' => '优秀',
        'C' => '良好',
        'D' => '及格',
        'F' => '需要补考',
        default => '未知等级'
    };
    echo $result;
?>
```

### 三元运算符
```php
<?php
    $age = 20;
    
    // 基本三元运算符
    $status = ($age >= 18) ? "成年" : "未成年";
    echo $status;
    
    // 嵌套三元运算符
    $score = 75;
    $result = ($score >= 90) ? "优秀" : 
              (($score >= 80) ? "良好" : 
              (($score >= 60) ? "及格" : "不及格"));
    echo $result;
    
    // PHP 7+ 空合并运算符
    $name = $_GET['name'] ?? "匿名用户";
    
    // PHP 7+ 三元运算符简写
    $username = $_GET['username'] ?: 'guest';
?>
```

## 循环语句

### for循环
```php
<?php
    // 基本for循环
    for ($i = 1; $i <= 10; $i++) {
        echo $i . " ";
    }
    
    // 倒序循环
    for ($i = 10; $i >= 1; $i--) {
        echo $i . " ";
    }
    
    // 多个初始化和更新
    for ($i = 0, $j = 10; $i < $j; $i++, $j--) {
        echo "i=$i, j=$j ";
    }
    
    // 循环控制
    for ($i = 1; $i <= 20; $i++) {
        if ($i % 2 == 0) {
            continue;  // 跳过偶数
        }
        if ($i > 15) {
            break;     // 超过15就退出
        }
        echo $i . " ";
    }
?>
```

### while循环
```php
<?php
    // while循环
    $count = 1;
    while ($count <= 5) {
        echo "计数：$count\n";
        $count++;
    }
    
    // 无限循环（需要break）
    $number = 1;
    while (true) {
        echo $number . " ";
        $number++;
        if ($number > 10) {
            break;
        }
    }
    
    // 读取文件行
    $lines = file("data.txt");
    $i = 0;
    while ($i < count($lines)) {
        echo $lines[$i];
        $i++;
    }
?>
```

### do-while循环
```php
<?php
    // do-while循环（至少执行一次）
    $count = 1;
    do {
        echo "计数：$count\n";
        $count++;
    } while ($count <= 5);
    
    // 即使条件为false也会执行一次
    $i = 10;
    do {
        echo "这会执行一次：$i\n";
        $i++;
    } while ($i < 5);
    
    // 菜单驱动的程序
    do {
        echo "1. 添加记录\n";
        echo "2. 查看记录\n";
        echo "3. 退出\n";
        echo "请选择：";
        
        $choice = trim(fgets(STDIN));
        
        switch ($choice) {
            case '1':
                echo "添加记录...\n";
                break;
            case '2':
                echo "查看记录...\n";
                break;
            case '3':
                echo "退出程序\n";
                break;
            default:
                echo "无效选择\n";
        }
    } while ($choice != '3');
?>
```

### foreach循环
```php
<?php
    // 遍历索引数组
    $fruits = ["apple", "banana", "orange"];
    foreach ($fruits as $fruit) {
        echo $fruit . "\n";
    }
    
    // 遍历关联数组
    $person = [
        "name" => "张三",
        "age" => 25,
        "city" => "北京"
    ];
    foreach ($person as $key => $value) {
        echo "$key: $value\n";
    }
    
    // 遍历多维数组
    $users = [
        ["name" => "张三", "age" => 25],
        ["name" => "李四", "age" => 30],
        ["name" => "王五", "age" => 28]
    ];
    
    foreach ($users as $user) {
        echo "姓名：" . $user['name'] . "，年龄：" . $user['age'] . "\n";
    }
    
    // 引用遍历（可以修改原数组）
    $numbers = [1, 2, 3, 4, 5];
    foreach ($numbers as &$number) {
        $number *= 2;  // 每个元素乘以2
    }
    unset($number);  // 取消引用
    
    print_r($numbers);  // [2, 4, 6, 8, 10]
?>
```

## 跳转语句

### break和continue
```php
<?php
    // break示例
    for ($i = 1; $i <= 10; $i++) {
        if ($i == 5) {
            break;  // 退出循环
        }
        echo $i . " ";
    }
    // 输出：1 2 3 4
    
    // continue示例
    for ($i = 1; $i <= 10; $i++) {
        if ($i % 2 == 0) {
            continue;  // 跳过本次循环
        }
        echo $i . " ";
    }
    // 输出：1 3 5 7 9
    
    // 嵌套循环中的break和continue
    for ($i = 1; $i <= 3; $i++) {
        echo "外层循环 $i:\n";
        for ($j = 1; $j <= 3; $j++) {
            if ($j == 2) {
                continue 2;  // 跳到外层循环的下一次迭代
            }
            echo "  内层循环 $j\n";
        }
    }
    
    // break带参数（指定跳出几层循环）
    for ($i = 1; $i <= 3; $i++) {
        for ($j = 1; $j <= 3; $j++) {
            if ($i == 2 && $j == 2) {
                break 2;  // 跳出两层循环
            }
            echo "$i-$j ";
        }
    }
?>
```

### goto语句（PHP 5.3+）
```php
<?php
    // goto示例（谨慎使用）
    $i = 0;
    start:
    echo $i . " ";
    $i++;
    
    if ($i < 5) {
        goto start;
    }
    
    // 跳出多重循环的替代方案
    for ($i = 0; $i < 10; $i++) {
        for ($j = 0; $j < 10; $j++) {
            for ($k = 0; $k < 10; $k++) {
                if ($i == 5 && $j == 5 && $k == 5) {
                    goto end;  // 直接跳出三层循环
                }
                echo "$i-$j-$k ";
            }
        }
    }
    end:
    echo "跳出循环\n";
?>
```

## 包含文件控制

### include和require的错误处理
```php
<?php
    // include - 包含失败时产生警告，继续执行
    if (@include 'config.php') {
        echo "配置文件加载成功";
    } else {
        echo "配置文件不存在，使用默认配置";
    }
    
    // require - 包含失败时产生致命错误，停止执行
    try {
        require 'essential.php';  // 必须的文件
    } catch (Error $e) {
        die("关键文件缺失，无法继续执行");
    }
    
    // include_once和require_once
    include_once 'functions.php';  // 只包含一次
    require_once 'database.php';
    
    // 条件包含
    if ($debug_mode) {
        include 'debug_tools.php';
    }
    
    // 动态包含
    $page = $_GET['page'] ?? 'home';
    $file = "pages/$page.php";
    
    if (file_exists($file)) {
        include $file;
    } else {
        include 'pages/404.php';
    }
?>
```

## 混合语法

### HTML中的控制结构
```php
<?php
    $users = ["张三", "李四", "王五"];
    $isLoggedIn = true;
?>

<!DOCTYPE html>
<html>
<head>
    <title>用户列表</title>
</head>
<body>
    <?php if ($isLoggedIn): ?>
        <h1>欢迎回来</h1>
        
        <ul>
            <?php foreach ($users as $user): ?>
                <li><?php echo htmlspecialchars($user); ?></li>
            <?php endforeach; ?>
        </ul>
    <?php else: ?>
        <h1>请先登录</h1>
        <p><a href="login.php">登录</a></p>
    <?php endif; ?>
    
    <?php for ($i = 1; $i <= 5; $i++): ?>
        <p>段落 <?php echo $i; ?></p>
    <?php endfor; ?>
</body>
</html>
```

### 替代语法
```php
<?php
    // if的替代语法
    if ($condition):
        // 代码块
    elseif ($another_condition):
        // 代码块
    else:
        // 代码块
    endif;
    
    // for的替代语法
    for ($i = 0; $i < 10; $i++):
        // 循环体
    endfor;
    
    // while的替代语法
    while ($condition):
        // 循环体
    endwhile;
    
    // foreach的替代语法
    foreach ($array as $value):
        // 循环体
    endforeach;
    
    // switch的替代语法
    switch ($value):
        case 1:
            // 代码
            break;
        case 2:
            // 代码
            break;
        default:
            // 代码
            break;
    endswitch;
?>
```

## 实际应用示例

### 表单处理
```php
<?php
    $errors = [];
    $success = false;
    
    if ($_SERVER['REQUEST_METHOD'] == 'POST') {
        $name = trim($_POST['name'] ?? '');
        $email = trim($_POST['email'] ?? '');
        $age = intval($_POST['age'] ?? 0);
        
        // 验证
        if (empty($name)) {
            $errors[] = "姓名不能为空";
        }
        
        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $errors[] = "请输入有效的邮箱地址";
        }
        
        if ($age < 18 || $age > 120) {
            $errors[] = "年龄必须在18-120之间";
        }
        
        if (empty($errors)) {
            // 处理数据
            $success = true;
        }
    }
?>

<!DOCTYPE html>
<html>
<head>
    <title>用户注册</title>
</head>
<body>
    <h1>用户注册</h1>
    
    <?php if ($success): ?>
        <div class="success">注册成功！</div>
    <?php endif; ?>
    
    <?php if (!empty($errors)): ?>
        <div class="errors">
            <?php foreach ($errors as $error): ?>
                <p><?php echo htmlspecialchars($error); ?></p>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
    
    <form method="POST">
        <div>
            <label>姓名：</label>
            <input type="text" name="name" 
                   value="<?php echo htmlspecialchars($_POST['name'] ?? ''); ?>">
        </div>
        <div>
            <label>邮箱：</label>
            <input type="email" name="email"
                   value="<?php echo htmlspecialchars($_POST['email'] ?? ''); ?>">
        </div>
        <div>
            <label>年龄：</label>
            <input type="number" name="age"
                   value="<?php echo htmlspecialchars($_POST['age'] ?? ''); ?>">
        </div>
        <button type="submit">注册</button>
    </form>
</body>
</html>
```

### 数据处理
```php
<?php
    // 处理CSV数据
    function processCsvData($filename) {
        if (!file_exists($filename)) {
            return false;
        }
        
        $data = [];
        $handle = fopen($filename, 'r');
        
        if ($handle === false) {
            return false;
        }
        
        // 跳过标题行
        fgetcsv($handle);
        
        while (($row = fgetcsv($handle)) !== false) {
            if (count($row) >= 3) {
                $data[] = [
                    'name' => trim($row[0]),
                    'email' => trim($row[1]),
                    'age' => intval($row[2])
                ];
            }
        }
        
        fclose($handle);
        return $data;
    }
    
    // 数据过滤和统计
    function analyzeData($data) {
        $total = count($data);
        $ageSum = 0;
        $domains = [];
        
        foreach ($data as $person) {
            $ageSum += $person['age'];
            
            // 统计邮箱域名
            $parts = explode('@', $person['email']);
            if (count($parts) == 2) {
                $domain = $parts[1];
                $domains[$domain] = ($domains[$domain] ?? 0) + 1;
            }
        }
        
        $avgAge = $total > 0 ? round($ageSum / $total, 2) : 0;
        
        return [
            'total_users' => $total,
            'average_age' => $avgAge,
            'email_domains' => $domains
        ];
    }
    
    // 使用示例
    $csvFile = 'users.csv';
    $userData = processCsvData($csvFile);
    
    if ($userData !== false) {
        $analysis = analyzeData($userData);
        
        echo "用户总数：" . $analysis['total_users'] . "\n";
        echo "平均年龄：" . $analysis['average_age'] . "\n";
        echo "邮箱域名分布：\n";
        
        foreach ($analysis['email_domains'] as $domain => $count) {
            echo "  $domain: $count\n";
        }
    }
?>
```

## 最佳实践

1. **避免深层嵌套**：使用早期返回或break来减少嵌套层级。
2. **清晰的条件**：使用有意义的变量名来提高条件判断的可读性。
3. **适当的循环**：选择最适合的循环类型（for、while、foreach）。
4. **异常处理**：对可能出现错误的情况进行适当的错误处理。
5. **代码简洁**：避免过于复杂的控制结构，保持代码的清晰和可维护性。