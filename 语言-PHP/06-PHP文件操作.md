# PHP文件操作

## 文件基本操作

### 文件读取
```php
<?php
    // 1. file_get_contents() - 读取整个文件
    $content = file_get_contents('data.txt');
    echo $content;
    
    // 读取网络文件
    $webContent = file_get_contents('https://www.example.com');
    echo strlen($webContent);  // 获取文件大小
    
    // 2. file() - 将文件读取为数组（每行一个元素）
    $lines = file('data.txt');
    foreach ($lines as $lineNumber => $line) {
        echo "第" . ($lineNumber + 1) . "行：" . htmlspecialchars($line);
    }
    
    // 3. 使用file()的其他选项
    $lines = file('data.txt', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    
    // 4. fgets() - 逐行读取
    $handle = fopen('data.txt', 'r');
    if ($handle) {
        while (($line = fgets($handle)) !== false) {
            echo "读取：" . htmlspecialchars(trim($line)) . "\n";
        }
        fclose($handle);
    }
    
    // 5. fread() - 读取指定字节数
    $handle = fopen('data.txt', 'r');
    $content = fread($handle, 1024);  // 读取1024字节
    fclose($handle);
    
    // 6. readfile() - 读取文件并直接输出到浏览器
    $bytesRead = readfile('data.txt');
    echo "读取了 $bytesRead 字节";
?>
```

### 文件写入
```php
<?php
    // 1. file_put_contents() - 写入文件
    $data = "Hello, World!\n这是第二行\n";
    $bytes = file_put_contents('output.txt', $data);
    echo "写入了 $bytes 字节";
    
    // 追加模式
    $moreData = "这是追加的内容\n";
    file_put_contents('output.txt', $moreData, FILE_APPEND);
    
    // 锁定写入
    $data = "重要数据";
    file_put_contents('important.txt', $data, LOCK_EX);
    
    // 2. 使用fopen和fwrite
    $handle = fopen('write.txt', 'w');  // 'w'模式会覆盖文件
    if ($handle) {
        fwrite($handle, "第一行\n");
        fwrite($handle, "第二行\n");
        fwrite($handle, "第三行\n");
        fclose($handle);
    }
    
    // 3. 追加模式
    $handle = fopen('append.txt', 'a');
    if ($handle) {
        fwrite($handle, "追加的内容\n");
        fclose($handle);
    }
    
    // 4. 读写模式
    $handle = fopen('readwrite.txt', 'r+');
    if ($handle) {
        // 读取前10个字符
        $content = fread($handle, 10);
        echo "读取内容：" . $content;
        
        // 移动到文件开头
        rewind($handle);
        
        // 写入新内容
        fwrite($handle, "新的开头");
        fclose($handle);
    }
    
    // 5. 格式化写入
    $handle = fopen('formatted.txt', 'w');
    if ($handle) {
        $name = "张三";
        $age = 25;
        $salary = 5000.50;
        
        fprintf($handle, "姓名：%s\n", $name);
        fprintf($handle, "年龄：%d\n", $age);
        fprintf($handle, "薪资：%.2f\n", $salary);
        
        fclose($handle);
    }
?>
```

## 文件信息和管理

### 文件属性检查
```php
<?php
    $filename = 'test.txt';
    
    // 文件存在性检查
    if (file_exists($filename)) {
        echo "文件存在\n";
    } else {
        echo "文件不存在\n";
    }
    
    // 文件类型检查
    if (is_file($filename)) {
        echo "这是一个文件\n";
    }
    
    if (is_dir('logs')) {
        echo "这是一个目录\n";
    }
    
    // 文件可读性检查
    if (is_readable($filename)) {
        echo "文件可读\n";
    }
    
    // 文件可写性检查
    if (is_writable($filename)) {
        echo "文件可写\n";
    }
    
    // 文件可执行性检查
    if (is_executable('script.sh')) {
        echo "文件可执行\n";
    }
    
    // 文件详细信息
    if (file_exists($filename)) {
        echo "文件大小：" . filesize($filename) . " 字节\n";
        echo "最后修改时间：" . date('Y-m-d H:i:s', filemtime($filename)) . "\n";
        echo "最后访问时间：" . date('Y-m-d H:i:s', fileatime($filename)) . "\n";
        echo "文件权限：" . fileperms($filename) . "\n";
        echo "文件所有者：" . fileowner($filename) . "\n";
        echo "文件组：" . filegroup($filename) . "\n";
        echo "文件类型：" . filetype($filename) . "\n";
    }
    
    // 获取文件路径信息
    $filepath = '/var/www/html/project/config/database.php';
    
    echo "目录名：" . dirname($filepath) . "\n";      // /var/www/html/project/config
    echo "文件名：" . basename($filepath) . "\n";      // database.php
    echo "扩展名：" . pathinfo($filepath, PATHINFO_EXTENSION) . "\n"; // php
    echo "文件名（不含扩展名）：" . pathinfo($filepath, PATHINFO_FILENAME) . "\n"; // database
    
    // 完整的pathinfo信息
    $pathInfo = pathinfo($filepath);
    print_r($pathInfo);
?>
```

### 文件操作
```php
<?php
    // 1. 复制文件
    $source = 'source.txt';
    $destination = 'backup.txt';
    
    if (copy($source, $destination)) {
        echo "文件复制成功\n";
    } else {
        echo "文件复制失败\n";
    }
    
    // 2. 重命名/移动文件
    if (rename('oldname.txt', 'newname.txt')) {
        echo "文件重命名成功\n";
    }
    
    // 移动文件到其他目录
    if (rename('file.txt', 'backup/file.txt')) {
        echo "文件移动成功\n";
    }
    
    // 3. 删除文件
    if (unlink('temp.txt')) {
        echo "文件删除成功\n";
    }
    
    // 4. 创建临时文件
    $tempFile = tempnam(sys_get_temp_dir(), 'php_');
    echo "临时文件：" . $tempFile . "\n";
    
    // 使用临时文件
    file_put_contents($tempFile, "临时数据");
    
    // 记得删除临时文件
    unlink($tempFile);
    
    // 5. 文件指针操作
    $handle = fopen('largefile.txt', 'r');
    if ($handle) {
        // 获取当前指针位置
        echo "当前位置：" . ftell($handle) . "\n";
        
        // 移动到文件开头
        rewind($handle);
        echo "移动到开头后的位置：" . ftell($handle) . "\n";
        
        // 移动到指定位置
        fseek($handle, 100);
        echo "移动到100字节后的位置：" . ftell($handle) . "\n";
        
        // 从末尾开始移动
        fseek($handle, -10, SEEK_END);
        echo "从末尾移动-10字节后的位置：" . ftell($handle) . "\n";
        
        // 检查是否到达文件末尾
        if (feof($handle)) {
            echo "已到达文件末尾\n";
        }
        
        fclose($handle);
    }
    
    // 6. 文件截断
    $handle = fopen('truncate.txt', 'r+');
    if ($handle) {
        // 将文件截断到100字节
        ftruncate($handle, 100);
        fclose($handle);
    }
?>
```

## 目录操作

### 目录创建和管理
```php
<?php
    // 1. 创建目录
    $dirname = 'mydir';
    
    if (!file_exists($dirname)) {
        if (mkdir($dirname, 0755, true)) {  // true表示递归创建
            echo "目录创建成功\n";
        } else {
            echo "目录创建失败\n";
        }
    }
    
    // 2. 创建多级目录
    $multidir = 'level1/level2/level3';
    mkdir($multidir, 0755, true);
    
    // 3. 删除目录（必须为空）
    if (rmdir('emptydir')) {
        echo "目录删除成功\n";
    }
    
    // 4. 递归删除目录
    function removeDirectory($dir) {
        if (!file_exists($dir)) {
            return true;
        }
        
        if (!is_dir($dir)) {
            return unlink($dir);
        }
        
        foreach (scandir($dir) as $item) {
            if ($item == '.' || $item == '..') {
                continue;
            }
            
            if (!removeDirectory($dir . DIRECTORY_SEPARATOR . $item)) {
                return false;
            }
        }
        
        return rmdir($dir);
    }
    
    removeDirectory('todelete');
    
    // 5. 复制目录
    function copyDirectory($source, $destination) {
        if (!file_exists($destination)) {
            mkdir($destination, 0755, true);
        }
        
        $items = scandir($source);
        foreach ($items as $item) {
            if ($item == '.' || $item == '..') {
                continue;
            }
            
            $sourcePath = $source . DIRECTORY_SEPARATOR . $item;
            $destPath = $destination . DIRECTORY_SEPARATOR . $item;
            
            if (is_dir($sourcePath)) {
                copyDirectory($sourcePath, $destPath);
            } else {
                copy($sourcePath, $destPath);
            }
        }
    }
    
    // 6. 获取当前工作目录
    echo "当前目录：" . getcwd() . "\n";
    
    // 切换目录
    chdir('/tmp');
    echo "切换后的目录：" . getcwd() . "\n";
?>
```

### 目录内容读取
```php
<?php
    // 1. 基本目录读取
    $dir = 'images';
    if (is_dir($dir)) {
        $files = scandir($dir);
        foreach ($files as $file) {
            if ($file != '.' && $file != '..') {
                echo $file . "\n";
            }
        }
    }
    
    // 2. 使用目录句柄
    $handle = opendir('documents');
    if ($handle) {
        echo "目录内容：\n";
        while (($file = readdir($handle)) !== false) {
            if ($file != '.' && $file != '..') {
                $filepath = 'documents/' . $file;
                $type = is_dir($filepath) ? '[目录]' : '[文件]';
                $size = is_file($filepath) ? filesize($filepath) : 0;
                echo "$type $file ($size 字节)\n";
            }
        }
        closedir($handle);
    }
    
    // 3. 递归遍历目录
    function listDirectory($dir, $level = 0) {
        $indent = str_repeat('  ', $level);
        
        if (is_dir($dir)) {
            $items = scandir($dir);
            foreach ($items as $item) {
                if ($item == '.' || $item == '..') {
                    continue;
                }
                
                $path = $dir . DIRECTORY_SEPARATOR . $item;
                
                if (is_dir($path)) {
                    echo $indent . "[目录] $item\n";
                    listDirectory($path, $level + 1);
                } else {
                    $size = filesize($path);
                    echo $indent . "[文件] $item ($size 字节)\n";
                }
            }
        }
    }
    
    listDirectory('project');
    
    // 4. 使用DirectoryIterator（面向对象方式）
    $iterator = new DirectoryIterator('logs');
    foreach ($iterator as $fileInfo) {
        if ($fileInfo->isDot()) continue;
        
        if ($fileInfo->isFile()) {
            echo "文件：" . $fileInfo->getFilename() . 
                 "，大小：" . $fileInfo->getSize() . " 字节，" .
                 "修改时间：" . date('Y-m-d', $fileInfo->getMTime()) . "\n";
        } elseif ($fileInfo->isDir()) {
            echo "目录：" . $fileInfo->getFilename() . "\n";
        }
    }
    
    // 5. 递归目录迭代器
    $recursiveIterator = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator('src')
    );
    
    foreach ($recursiveIterator as $file) {
        if ($file->isFile() && $file->getExtension() === 'php') {
            echo "PHP文件：" . $file->getPathname() . "\n";
        }
    }
?>
```

## 文件上传处理

### 基本文件上传
```php
<?php
    // HTML表单
    /*
    <form action="upload.php" method="POST" enctype="multipart/form-data">
        <input type="file" name="userfile">
        <input type="submit" value="上传">
    </form>
    */
    
    // 处理上传
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['userfile'])) {
        $uploadDir = 'uploads/';
        $uploadFile = $uploadDir . basename($_FILES['userfile']['name']);
        
        // 检查文件是否上传成功
        if ($_FILES['userfile']['error'] === UPLOAD_ERR_OK) {
            // 验证文件大小（5MB限制）
            $maxSize = 5 * 1024 * 1024;  // 5MB
            if ($_FILES['userfile']['size'] > $maxSize) {
                die("文件太大，最大允许5MB");
            }
            
            // 验证文件类型
            $allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
            $finfo = finfo_open(FILEINFO_MIME_TYPE);
            $mimeType = finfo_file($finfo, $_FILES['userfile']['tmp_name']);
            finfo_close($finfo);
            
            if (!in_array($mimeType, $allowedTypes)) {
                die("只允许上传JPEG、PNG和GIF图片");
            }
            
            // 创建上传目录（如果不存在）
            if (!file_exists($uploadDir)) {
                mkdir($uploadDir, 0755, true);
            }
            
            // 移动上传的文件
            if (move_uploaded_file($_FILES['userfile']['tmp_name'], $uploadFile)) {
                echo "文件上传成功！<br>";
                echo "原始文件名：" . $_FILES['userfile']['name'] . "<br>";
                echo "文件类型：" . $_FILES['userfile']['type'] . "<br>";
                echo "文件大小：" . $_FILES['userfile']['size'] . " 字节<br>";
                echo "临时文件名：" . $_FILES['userfile']['tmp_name'] . "<br>";
                echo "保存路径：" . $uploadFile . "<br>";
            } else {
                echo "文件上传失败！";
            }
        } else {
            echo "上传错误：" . $_FILES['userfile']['error'];
        }
    }
?>
```

### 高级文件上传
```php
<?php
    class FileUploader {
        private $uploadDir;
        private $allowedTypes;
        private $maxSize;
        private $errors = [];
        
        public function __construct($uploadDir = 'uploads/', $maxSize = 5242880) {
            $this->uploadDir = rtrim($uploadDir, '/') . '/';
            $this->maxSize = $maxSize;
            $this->allowedTypes = [
                'image/jpeg', 'image/png', 'image/gif',
                'application/pdf', 'text/plain',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ];
        }
        
        public function setAllowedTypes(array $types) {
            $this->allowedTypes = $types;
        }
        
        public function upload($fileField, $customName = null) {
            if (!isset($_FILES[$fileField])) {
                $this->errors[] = "没有找到上传文件字段";
                return false;
            }
            
            $file = $_FILES[$fileField];
            
            // 检查上传错误
            if ($file['error'] !== UPLOAD_ERR_OK) {
                $this->errors[] = $this->getUploadErrorMessage($file['error']);
                return false;
            }
            
            // 验证文件大小
            if ($file['size'] > $this->maxSize) {
                $this->errors[] = "文件太大，最大允许" . $this->maxSize . "字节";
                return false;
            }
            
            // 验证文件类型
            $finfo = finfo_open(FILEINFO_MIME_TYPE);
            $mimeType = finfo_file($finfo, $file['tmp_name']);
            finfo_close($finfo);
            
            if (!in_array($mimeType, $this->allowedTypes)) {
                $this->errors[] = "不支持的文件类型：$mimeType";
                return false;
            }
            
            // 生成文件名
            $filename = $customName ?: $this->generateUniqueName($file['name']);
            $uploadPath = $this->uploadDir . $filename;
            
            // 确保上传目录存在
            if (!file_exists($this->uploadDir)) {
                mkdir($this->uploadDir, 0755, true);
            }
            
            // 移动文件
            if (move_uploaded_file($file['tmp_name'], $uploadPath)) {
                return [
                    'original_name' => $file['name'],
                    'filename' => $filename,
                    'path' => $uploadPath,
                    'size' => $file['size'],
                    'type' => $mimeType
                ];
            } else {
                $this->errors[] = "文件移动失败";
                return false;
            }
        }
        
        private function generateUniqueName($originalName) {
            $extension = pathinfo($originalName, PATHINFO_EXTENSION);
            return uniqid() . '_' . time() . '.' . $extension;
        }
        
        private function getUploadErrorMessage($errorCode) {
            switch ($errorCode) {
                case UPLOAD_ERR_INI_SIZE:
                    return "上传的文件超过了php.ini中upload_max_filesize指令限制的大小";
                case UPLOAD_ERR_FORM_SIZE:
                    return "上传文件的大小超过了HTML表单中MAX_FILE_SIZE选项指定的值";
                case UPLOAD_ERR_PARTIAL:
                    return "文件只有部分被上传";
                case UPLOAD_ERR_NO_FILE:
                    return "没有文件被上传";
                case UPLOAD_ERR_NO_TMP_DIR:
                    return "找不到临时文件夹";
                case UPLOAD_ERR_CANT_WRITE:
                    return "文件写入失败";
                default:
                    return "未知上传错误";
            }
        }
        
        public function getErrors() {
            return $this->errors;
        }
        
        public function hasErrors() {
            return !empty($this->errors);
        }
    }
    
    // 使用示例
    $uploader = new FileUploader('uploads/', 10 * 1024 * 1024);  // 10MB限制
    
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $result = $uploader->upload('document');
        
        if ($result !== false) {
            echo "文件上传成功！<br>";
            echo "文件名：" . $result['filename'] . "<br>";
            echo "文件大小：" . $result['size'] . " 字节<br>";
            echo "文件路径：" . $result['path'] . "<br>";
        } else {
            echo "上传失败：<br>";
            foreach ($uploader->getErrors() as $error) {
                echo "- $error<br>";
            }
        }
    }
?>
```

## CSV文件处理

### CSV读写操作
```php
<?php
    // 1. 写入CSV文件
    $data = [
        ['姓名', '年龄', '邮箱'],
        ['张三', 25, 'zhangsan@email.com'],
        ['李四', 30, 'lisi@email.com'],
        ['王五', 28, 'wangwu@email.com']
    ];
    
    $file = fopen('users.csv', 'w');
    
    // 添加BOM以支持中文Excel显示
    fwrite($file, "\xEF\xBB\xBF");
    
    foreach ($data as $row) {
        fputcsv($file, $row);
    }
    
    fclose($file);
    
    // 2. 读取CSV文件
    $file = fopen('users.csv', 'r');
    $users = [];
    
    // 跳过BOM
    if (fgets($file) !== false) {
        fseek($file, 0);
    }
    
    // 读取数据
    while (($row = fgetcsv($file)) !== false) {
        $users[] = [
            'name' => $row[0],
            'age' => intval($row[1]),
            'email' => $row[2]
        ];
    }
    
    fclose($file);
    
    // 3. 处理带有引号的CSV
    function parseCsvLine($line) {
        $fields = [];
        $field = '';
        $inQuotes = false;
        $len = strlen($line);
        
        for ($i = 0; $i < $len; $i++) {
            $char = $line[$i];
            
            if ($char === '"') {
                if ($inQuotes && $i + 1 < $len && $line[$i + 1] === '"') {
                    $field .= '"';
                    $i++;  // 跳过下一个引号
                } else {
                    $inQuotes = !$inQuotes;
                }
            } elseif ($char === ',' && !$inQuotes) {
                $fields[] = $field;
                $field = '';
            } else {
                $field .= $char;
            }
        }
        
        $fields[] = $field;
        return $fields;
    }
    
    // 4. CSV数据处理类
    class CsvHandler {
        private $filename;
        private $headers;
        private $data;
        
        public function __construct($filename) {
            $this->filename = $filename;
            $this->load();
        }
        
        private function load() {
            if (!file_exists($this->filename)) {
                throw new Exception("文件不存在：$this->filename");
            }
            
            $file = fopen($this->filename, 'r');
            $this->data = [];
            
            // 读取标题行
            if (($header = fgetcsv($file)) !== false) {
                $this->headers = $header;
                
                // 读取数据行
                while (($row = fgetcsv($file)) !== false) {
                    $this->data[] = array_combine($this->headers, $row);
                }
            }
            
            fclose($file);
        }
        
        public function getData() {
            return $this->data;
        }
        
        public function getHeaders() {
            return $this->headers;
        }
        
        public function filter($column, $value) {
            return array_filter($this->data, function($row) use ($column, $value) {
                return $row[$column] === $value;
            });
        }
        
        public function save($data = null) {
            $file = fopen($this->filename, 'w');
            
            // 写入标题
            fputcsv($file, $this->headers);
            
            // 写入数据
            $dataToSave = $data ?: $this->data;
            foreach ($dataToSave as $row) {
                fputcsv($file, array_values($row));
            }
            
            fclose($file);
        }
        
        public function addRow($row) {
            if (count($row) !== count($this->headers)) {
                throw new Exception("列数不匹配");
            }
            
            $newRow = array_combine($this->headers, $row);
            $this->data[] = $newRow;
            return $newRow;
        }
    }
    
    // 使用CSV处理器
    $csv = new CsvHandler('products.csv');
    $products = $csv->getData();
    
    // 过滤产品
    $electronics = $csv->filter('category', '电子产品');
    
    // 添加新产品
    $csv->addRow(['手机', '电子产品', '2999', '100']);
    $csv->save();
?>
```

## 文件锁定

### 文件锁机制
```php
<?php
    // 1. 基本文件锁定
    $file = 'counter.txt';
    $handle = fopen($file, 'r+');
    
    // 获取独占锁
    if (flock($handle, LOCK_EX)) {
        // 读取当前计数
        $count = intval(fread($handle, filesize($file) ?: 0));
        
        // 增加计数
        $count++;
        
        // 回到文件开头
        rewind($handle);
        
        // 写入新计数
        fwrite($handle, $count);
        
        // 释放锁
        flock($handle, LOCK_UN);
        
        echo "计数器值：$count";
    } else {
        echo "无法获取文件锁";
    }
    
    fclose($handle);
    
    // 2. 文件锁工具类
    class FileLock {
        private $filename;
        private $handle;
        private $locked = false;
        
        public function __construct($filename) {
            $this->filename = $filename;
        }
        
        public function acquire($mode = LOCK_EX, $blocking = true) {
            $this->handle = fopen($this->filename, 'c+');  // c+模式创建文件但不截断
            
            if ($blocking) {
                $this->locked = flock($this->handle, $mode);
            } else {
                $this->locked = flock($this->handle, $mode | LOCK_NB);
            }
            
            return $this->locked;
        }
        
        public function release() {
            if ($this->locked && $this->handle) {
                flock($this->handle, LOCK_UN);
                $this->locked = false;
                return true;
            }
            return false;
        }
        
        public function write($data) {
            if (!$this->locked) {
                throw new Exception("文件未锁定");
            }
            
            ftruncate($this->handle, 0);
            rewind($this->handle);
            return fwrite($this->handle, $data);
        }
        
        public function read() {
            if (!$this->locked) {
                throw new Exception("文件未锁定");
            }
            
            rewind($this->handle);
            return stream_get_contents($this->handle);
        }
        
        public function __destruct() {
            $this->release();
            if ($this->handle) {
                fclose($this->handle);
            }
        }
    }
    
    // 使用文件锁
    $lock = new FileLock('shared_data.txt');
    
    if ($lock->acquire(LOCK_EX)) {
        $data = $lock->read();
        $dataArray = json_decode($data ?: '{}', true);
        
        // 修改数据
        $dataArray['last_updated'] = date('Y-m-d H:i:s');
        $dataArray['counter'] = ($dataArray['counter'] ?? 0) + 1;
        
        // 写回数据
        $lock->write(json_encode($dataArray, JSON_PRETTY_PRINT));
        $lock->release();
        
        echo "数据更新成功";
    } else {
        echo "无法获取文件锁";
    }
    
    // 3. 进程间通信示例
    function sendMessage($message) {
        $lock = new FileLock('message_queue.txt');
        
        if ($lock->acquire(LOCK_EX)) {
            $currentData = $lock->read();
            $messages = json_decode($currentData ?: '[]', true);
            
            $messages[] = [
                'message' => $message,
                'timestamp' => time(),
                'process_id' => getmypid()
            ];
            
            $lock->write(json_encode($messages, JSON_PRETTY_PRINT));
            $lock->release();
            
            return true;
        }
        
        return false;
    }
    
    function receiveMessages() {
        $lock = new FileLock('message_queue.txt');
        
        if ($lock->acquire(LOCK_EX)) {
            $data = $lock->read();
            $messages = json_decode($data ?: '[]', true);
            
            // 清空消息队列
            $lock->write('[]');
            $lock->release();
            
            return $messages;
        }
        
        return [];
    }
    
    // 发送消息
    sendMessage("测试消息1");
    sendMessage("测试消息2");
    
    // 接收消息
    $receivedMessages = receiveMessages();
    foreach ($receivedMessages as $msg) {
        echo "收到消息：" . $msg['message'] . 
             "，时间：" . date('Y-m-d H:i:s', $msg['timestamp']) . "\n";
    }
?>
```

## 最佳实践

1. **错误处理**：始终检查文件操作的返回值。
2. **路径处理**：使用DIRECTORY_SEPARATOR来处理不同操作系统的路径分隔符。
3. **文件权限**：合理设置文件和目录的权限。
4. **内存管理**：处理大文件时，逐行读取而不是一次性读取整个文件。
5. **安全检查**：验证上传文件的类型和大小，防止恶意文件上传。
6. **文件锁定**：在多进程环境中使用文件锁定防止数据竞争。
7. **备份机制**：在重要文件操作前创建备份。