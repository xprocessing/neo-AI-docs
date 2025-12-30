# PHP错误处理和调试

## 错误报告配置

### 基本错误报告设置
```php
<?php
    // 错误报告级别
    error_reporting(E_ALL);                    // 报告所有错误
    error_reporting(E_ALL & ~E_DEPRECATED);     // 报告所有错误，除了已弃用的功能
    error_reporting(E_ERROR | E_WARNING | E_PARSE); // 只报告严重错误
    
    // 显示错误（仅开发环境）
    ini_set('display_errors', 1);              // 在页面显示错误
    ini_set('display_startup_errors', 1);       // 显示启动错误
    
    // 记录错误（生产环境）
    ini_set('log_errors', 1);                  // 记录错误到日志
    ini_set('error_log', '/var/log/php_errors.log'); // 错误日志文件
    
    // 完整配置示例
    error_reporting(E_ALL);
    ini_set('display_errors', 0);               // 生产环境不显示错误
    ini_set('log_errors', 1);
    ini_set('error_log', __DIR__ . '/logs/error.log');
    ini_set('max_execution_time', 30);         // 最大执行时间
    ini_set('memory_limit', '256M');           // 内存限制
    
    // 运行时修改错误处理器
    set_error_handler('customErrorHandler');
    set_exception_handler('customExceptionHandler');
    register_shutdown_function('fatalErrorHandler');
    
    // 自定义错误处理函数
    function customErrorHandler($errno, $errstr, $errfile, $errline) {
        $errorTypes = [
            E_ERROR             => 'Error',
            E_WARNING           => 'Warning',
            E_PARSE             => 'Parse Error',
            E_NOTICE            => 'Notice',
            E_CORE_ERROR        => 'Core Error',
            E_CORE_WARNING      => 'Core Warning',
            E_COMPILE_ERROR     => 'Compile Error',
            E_COMPILE_WARNING   => 'Compile Warning',
            E_USER_ERROR        => 'User Error',
            E_USER_WARNING      => 'User Warning',
            E_USER_NOTICE       => 'User Notice',
            E_STRICT            => 'Strict',
            E_RECOVERABLE_ERROR => 'Recoverable Error',
            E_DEPRECATED        => 'Deprecated',
            E_USER_DEPRECATED   => 'User Deprecated'
        ];
        
        $errorType = $errorTypes[$errno] ?? 'Unknown';
        $message = "[$errorType] $errstr in $errfile on line $errline";
        
        // 记录到日志
        error_log($message);
        
        // 开发环境显示错误
        if (ini_get('display_errors')) {
            echo "<div style='color: red; border: 1px solid #f00; padding: 10px; margin: 10px;'>";
            echo "<strong>$errorType:</strong> $errstr<br>";
            echo "<strong>File:</strong> $errfile<br>";
            echo "<strong>Line:</strong> $errline";
            echo "</div>";
        }
        
        // 不执行PHP内置错误处理
        return true;
    }
    
    // 自定义异常处理函数
    function customExceptionHandler($exception) {
        $message = "Uncaught exception: " . $exception->getMessage();
        $message .= " in " . $exception->getFile() . " on line " . $exception->getLine();
        
        error_log($message);
        
        if (ini_get('display_errors')) {
            echo "<div style='color: red; border: 1px solid #f00; padding: 10px; margin: 10px;'>";
            echo "<strong>Fatal Error:</strong> " . htmlspecialchars($exception->getMessage()) . "<br>";
            echo "<strong>File:</strong> " . $exception->getFile() . "<br>";
            echo "<strong>Line:</strong> " . $exception->getLine() . "<br>";
            echo "<strong>Trace:</strong> <pre>" . htmlspecialchars($exception->getTraceAsString()) . "</pre>";
            echo "</div>";
        } else {
            http_response_code(500);
            include 'error_pages/500.html';
        }
        
        exit(1);
    }
    
    // 致命错误处理
    function fatalErrorHandler() {
        $error = error_get_last();
        if ($error !== null && in_array($error['type'], [E_ERROR, E_CORE_ERROR, E_COMPILE_ERROR])) {
            customErrorHandler($error['type'], $error['message'], $error['file'], $error['line']);
        }
    }
?>
```

### 环境配置文件
```php
<?php
    // config/error_handler.php
    
    class ErrorHandler {
        private $environment;
        private $logFile;
        
        public function __construct($environment = 'production') {
            $this->environment = $environment;
            $this->logFile = __DIR__ . '/../logs/error.log';
            $this->setupErrorHandler();
        }
        
        private function setupErrorHandler() {
            // 根据环境配置错误报告
            if ($this->environment === 'development') {
                error_reporting(E_ALL);
                ini_set('display_errors', 1);
                ini_set('display_startup_errors', 1);
            } else {
                error_reporting(E_ALL & ~E_DEPRECATED & ~E_STRICT);
                ini_set('display_errors', 0);
                ini_set('display_startup_errors', 0);
                ini_set('log_errors', 1);
                ini_set('error_log', $this->logFile);
            }
            
            // 设置错误和异常处理
            set_error_handler([$this, 'handleError']);
            set_exception_handler([$this, 'handleException']);
            register_shutdown_function([$this, 'handleShutdown']);
        }
        
        public function handleError($errno, $errstr, $errfile, $errline) {
            $errorData = [
                'type' => $this->getErrorType($errno),
                'message' => $errstr,
                'file' => $errfile,
                'line' => $errline,
                'timestamp' => date('Y-m-d H:i:s'),
                'context' => $this->getContext()
            ];
            
            $this->logError($errorData);
            
            if ($this->environment === 'development') {
                $this->displayError($errorData);
            }
            
            return true; // 阻止PHP内置错误处理
        }
        
        public function handleException($exception) {
            $errorData = [
                'type' => get_class($exception),
                'message' => $exception->getMessage(),
                'file' => $exception->getFile(),
                'line' => $exception->getLine(),
                'trace' => $exception->getTraceAsString(),
                'timestamp' => date('Y-m-d H:i:s'),
                'context' => $this->getContext()
            ];
            
            $this->logError($errorData);
            
            if ($this->environment === 'development') {
                $this->displayException($errorData);
            } else {
                $this->displayErrorPage(500);
            }
        }
        
        public function handleShutdown() {
            $error = error_get_last();
            if ($error !== null && in_array($error['type'], [E_ERROR, E_CORE_ERROR, E_COMPILE_ERROR])) {
                $this->handleError($error['type'], $error['message'], $error['file'], $error['line']);
            }
        }
        
        private function getErrorType($errno) {
            $types = [
                E_ERROR => 'Fatal Error',
                E_WARNING => 'Warning',
                E_PARSE => 'Parse Error',
                E_NOTICE => 'Notice',
                E_CORE_ERROR => 'Core Error',
                E_CORE_WARNING => 'Core Warning',
                E_COMPILE_ERROR => 'Compile Error',
                E_COMPILE_WARNING => 'Compile Warning',
                E_USER_ERROR => 'User Error',
                E_USER_WARNING => 'User Warning',
                E_USER_NOTICE => 'User Notice',
                E_STRICT => 'Strict Notice',
                E_RECOVERABLE_ERROR => 'Recoverable Error',
                E_DEPRECATED => 'Deprecated',
                E_USER_DEPRECATED => 'User Deprecated'
            ];
            
            return $types[$errno] ?? 'Unknown Error';
        }
        
        private function getContext() {
            $context = [];
            
            // 获取请求信息
            if (isset($_SERVER['REQUEST_METHOD'])) {
                $context['request'] = [
                    'method' => $_SERVER['REQUEST_METHOD'],
                    'uri' => $_SERVER['REQUEST_URI'] ?? '',
                    'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
                    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? ''
                ];
            }
            
            // 获取POST数据
            if (!empty($_POST)) {
                $context['post'] = $_POST;
            }
            
            return $context;
        }
        
        private function logError($errorData) {
            $logMessage = sprintf(
                "[%s] %s: %s in %s on line %d\n",
                $errorData['timestamp'],
                $errorData['type'],
                $errorData['message'],
                $errorData['file'],
                $errorData['line']
            );
            
            if (!empty($errorData['context'])) {
                $logMessage .= "Context: " . json_encode($errorData['context']) . "\n";
            }
            
            if (isset($errorData['trace'])) {
                $logMessage .= "Trace: " . $errorData['trace'] . "\n";
            }
            
            error_log($logMessage . "\n", 3, $this->logFile);
        }
        
        private function displayError($errorData) {
            echo '<div style="background: #fff; border: 2px solid #ff0000; padding: 20px; margin: 20px; font-family: Arial, sans-serif;">';
            echo '<h2 style="color: #ff0000; margin-top: 0;">' . htmlspecialchars($errorData['type']) . '</h2>';
            echo '<p><strong>Message:</strong> ' . htmlspecialchars($errorData['message']) . '</p>';
            echo '<p><strong>File:</strong> ' . htmlspecialchars($errorData['file']) . '</p>';
            echo '<p><strong>Line:</strong> ' . $errorData['line'] . '</p>';
            
            if (!empty($errorData['context'])) {
                echo '<h3>Context:</h3>';
                echo '<pre>' . htmlspecialchars(json_encode($errorData['context'], JSON_PRETTY_PRINT)) . '</pre>';
            }
            
            if (isset($errorData['trace'])) {
                echo '<h3>Stack Trace:</h3>';
                echo '<pre>' . htmlspecialchars($errorData['trace']) . '</pre>';
            }
            
            echo '</div>';
        }
        
        private function displayException($errorData) {
            $this->displayError($errorData);
        }
        
        private function displayErrorPage($code) {
            http_response_code($code);
            $errorPage = __DIR__ . "/../error_pages/{$code}.html";
            if (file_exists($errorPage)) {
                include $errorPage;
            } else {
                echo "<h1>Error {$code}</h1><p>Something went wrong.</p>";
            }
        }
    }
    
    // 使用
    $environment = $_ENV['APP_ENV'] ?? 'production';
    $errorHandler = new ErrorHandler($environment);
?>
```

## 异常处理

### 自定义异常类
```php
<?php
    // 基础异常类
    class BaseException extends Exception {
        protected $data;
        protected $errorCode;
        
        public function __construct($message = "", $code = 0, $data = null, Throwable $previous = null) {
            parent::__construct($message, $code, $previous);
            $this->data = $data;
            $this->errorCode = $code;
        }
        
        public function getData() {
            return $this->data;
        }
        
        public function getErrorCode() {
            return $this->errorCode;
        }
        
        public function toArray() {
            return [
                'error' => true,
                'message' => $this->getMessage(),
                'code' => $this->getCode(),
                'error_code' => $this->errorCode,
                'data' => $this->data,
                'file' => $this->getFile(),
                'line' => $this->getLine(),
                'trace' => $this->getTraceAsString()
            ];
        }
    }
    
    // 数据验证异常
    class ValidationException extends BaseException {
        protected $errors;
        
        public function __construct($errors = [], $message = "Validation failed") {
            $this->errors = $errors;
            parent::__construct($message, 422, $errors);
        }
        
        public function getErrors() {
            return $this->errors;
        }
    }
    
    // 数据库异常
    class DatabaseException extends BaseException {
        protected $query;
        protected $bindings;
        
        public function __construct($message, $query = null, $bindings = [], $code = 500) {
            $this->query = $query;
            $this->bindings = $bindings;
            parent::__construct($message, $code, [
                'query' => $query,
                'bindings' => $bindings
            ]);
        }
        
        public function getQuery() {
            return $this->query;
        }
        
        public function getBindings() {
            return $this->bindings;
        }
    }
    
    // 认证异常
    class AuthenticationException extends BaseException {
        public function __construct($message = "Authentication failed") {
            parent::__construct($message, 401);
        }
    }
    
    // 授权异常
    class AuthorizationException extends BaseException {
        protected $permission;
        
        public function __construct($permission, $message = "Access denied") {
            $this->permission = $permission;
            parent::__construct($message, 403, ['permission' => $permission]);
        }
        
        public function getPermission() {
            return $this->permission;
        }
    }
    
    // 资源未找到异常
    class NotFoundException extends BaseException {
        protected $resource;
        protected $id;
        
        public function __construct($resource, $id = null, $message = null) {
            $this->resource = $resource;
            $this->id = $id;
            
            if (!$message) {
                $message = $id ? "$resource with ID $id not found" : "$resource not found";
            }
            
            parent::__construct($message, 404, [
                'resource' => $resource,
                'id' => $id
            ]);
        }
        
        public function getResource() {
            return $this->resource;
        }
        
        public function getId() {
            return $this->id;
        }
    }
    
    // 使用示例
    try {
        // 模拟验证失败
        $errors = [
            'name' => 'Name is required',
            'email' => 'Email is invalid'
        ];
        throw new ValidationException($errors);
        
    } catch (ValidationException $e) {
        echo "Validation failed: " . $e->getMessage() . "\n";
        print_r($e->getErrors());
        
    } catch (DatabaseException $e) {
        echo "Database error: " . $e->getMessage() . "\n";
        echo "Query: " . $e->getQuery() . "\n";
        
    } catch (NotFoundException $e) {
        echo "Not found: " . $e->getMessage() . "\n";
        echo "Resource: " . $e->getResource() . "\n";
        
    } catch (BaseException $e) {
        echo "Application error: " . $e->getMessage() . "\n";
        echo "Error data: " . json_encode($e->getData()) . "\n";
        
    } catch (Exception $e) {
        echo "General error: " . $e->getMessage() . "\n";
    }
?>
```

### 异常处理最佳实践
```php
<?php
    class UserService {
        private $db;
        
        public function __construct($database) {
            $this->db = $database;
        }
        
        public function createUser($userData) {
            try {
                // 验证输入数据
                $this->validateUserData($userData);
                
                // 检查邮箱是否已存在
                if ($this->emailExists($userData['email'])) {
                    throw new BaseException('Email already exists', 409);
                }
                
                // 插入用户
                $userId = $this->insertUser($userData);
                
                return $userId;
                
            } catch (ValidationException $e) {
                // 重新抛出验证异常
                throw $e;
                
            } catch (DatabaseException $e) {
                // 记录数据库错误
                error_log("Database error in createUser: " . $e->getMessage());
                throw new DatabaseException("Failed to create user", $e->getQuery(), $e->getBindings());
                
            } catch (Exception $e) {
                // 捕获其他异常并包装
                error_log("Unexpected error in createUser: " . $e->getMessage());
                throw new BaseException("Failed to create user", 500, null, $e);
            }
        }
        
        private function validateUserData($userData) {
            $errors = [];
            
            if (empty($userData['name'])) {
                $errors['name'] = 'Name is required';
            }
            
            if (empty($userData['email'])) {
                $errors['email'] = 'Email is required';
            } elseif (!filter_var($userData['email'], FILTER_VALIDATE_EMAIL)) {
                $errors['email'] = 'Email is invalid';
            }
            
            if (empty($userData['password'])) {
                $errors['password'] = 'Password is required';
            } elseif (strlen($userData['password']) < 8) {
                $errors['password'] = 'Password must be at least 8 characters';
            }
            
            if (!empty($errors)) {
                throw new ValidationException($errors);
            }
        }
        
        private function emailExists($email) {
            try {
                $stmt = $this->db->prepare("SELECT id FROM users WHERE email = ?");
                $stmt->execute([$email]);
                return $stmt->fetch() !== false;
            } catch (PDOException $e) {
                throw new DatabaseException("Failed to check email existence", $stmt->queryString, [$email]);
            }
        }
        
        private function insertUser($userData) {
            try {
                $stmt = $this->db->prepare("
                    INSERT INTO users (name, email, password, created_at) 
                    VALUES (?, ?, ?, NOW())
                ");
                
                $hashedPassword = password_hash($userData['password'], PASSWORD_DEFAULT);
                $stmt->execute([
                    $userData['name'],
                    $userData['email'],
                    $hashedPassword
                ]);
                
                return $this->db->lastInsertId();
                
            } catch (PDOException $e) {
                throw new DatabaseException("Failed to insert user", $stmt->queryString, [
                    $userData['name'],
                    $userData['email'],
                    $hashedPassword
                ]);
            }
        }
        
        public function getUser($id) {
            try {
                $stmt = $this->db->prepare("SELECT * FROM users WHERE id = ?");
                $stmt->execute([$id]);
                $user = $stmt->fetch(PDO::FETCH_ASSOC);
                
                if (!$user) {
                    throw new NotFoundException('User', $id);
                }
                
                // 移除敏感信息
                unset($user['password']);
                
                return $user;
                
            } catch (PDOException $e) {
                throw new DatabaseException("Failed to get user", $stmt->queryString, [$id]);
            }
        }
    }
    
    // 使用示例
    $userService = new UserService($database);
    
    try {
        // 创建用户
        $userData = [
            'name' => 'John Doe',
            'email' => 'john@example.com',
            'password' => 'password123'
        ];
        
        $userId = $userService->createUser($userData);
        echo "User created with ID: $userId\n";
        
        // 获取用户
        $user = $userService->getUser($userId);
        echo "User: " . json_encode($user) . "\n";
        
    } catch (ValidationException $e) {
        http_response_code(422);
        echo json_encode([
            'error' => 'validation_failed',
            'message' => $e->getMessage(),
            'errors' => $e->getErrors()
        ]);
        
    } catch (NotFoundException $e) {
        http_response_code(404);
        echo json_encode([
            'error' => 'not_found',
            'message' => $e->getMessage(),
            'resource' => $e->getResource(),
            'id' => $e->getId()
        ]);
        
    } catch (DatabaseException $e) {
        http_response_code(500);
        echo json_encode([
            'error' => 'database_error',
            'message' => 'Database operation failed'
        ]);
        error_log("Database error: " . $e->getMessage());
        
    } catch (BaseException $e) {
        http_response_code($e->getCode());
        echo json_encode($e->toArray());
        
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode([
            'error' => 'internal_error',
            'message' => 'Internal server error'
        ]);
        error_log("Unexpected error: " . $e->getMessage());
    }
?>
```

## 调试技术

### 调试工具类
```php
<?php
    class Debugger {
        private static $logs = [];
        private static $startTimes = [];
        private static $enabled = true;
        
        // 启用/禁用调试
        public static function enable($enabled = true) {
            self::$enabled = $enabled;
        }
        
        // 输出变量信息
        public static function dump($var, $label = null, $die = false) {
            if (!self::$enabled) return;
            
            $backtrace = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 1);
            $file = $backtrace[0]['file'] ?? 'unknown';
            $line = $backtrace[0]['line'] ?? 'unknown';
            
            echo "<div style='background: #f8f8f8; border: 1px solid #ddd; padding: 10px; margin: 10px; font-family: monospace;'>";
            
            if ($label) {
                echo "<strong style='color: #d00;'>{$label}:</strong><br>";
            }
            
            echo "<strong>File:</strong> {$file}<br>";
            echo "<strong>Line:</strong> {$line}<br>";
            echo "<strong>Type:</strong> " . gettype($var) . "<br>";
            
            if (is_object($var)) {
                echo "<strong>Class:</strong> " . get_class($var) . "<br>";
            }
            
            if (is_array($var) || is_object($var)) {
                echo "<strong>Content:</strong><br>";
                echo "<pre style='background: #fff; padding: 10px; border: 1px solid #ccc;'>";
                print_r($var);
                echo "</pre>";
            } else {
                echo "<strong>Value:</strong> " . htmlspecialchars(var_export($var, true)) . "<br>";
            }
            
            echo "</div>";
            
            if ($die) {
                die("Debug terminated");
            }
        }
        
        // 简化的调试输出
        public static function d($var, $label = null) {
            self::dump($var, $label, true);
        }
        
        // 记录日志
        public static function log($message, $level = 'info') {
            if (!self::$enabled) return;
            
            $timestamp = date('Y-m-d H:i:s');
            $backtrace = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 1);
            $file = basename($backtrace[0]['file'] ?? 'unknown');
            $line = $backtrace[0]['line'] ?? 'unknown';
            
            $logEntry = "[{$timestamp}] [{$level}] {$file}:{$line} - {$message}";
            self::$logs[] = $logEntry;
            
            // 同时写入错误日志
            error_log($logEntry);
        }
        
        // 开始计时
        public static function startTimer($name) {
            if (!self::$enabled) return;
            self::$startTimes[$name] = microtime(true);
        }
        
        // 结束计时并返回时间
        public static function endTimer($name) {
            if (!self::$enabled) return 0;
            
            if (!isset(self::$startTimes[$name])) {
                self::log("Timer '$name' was not started", 'warning');
                return 0;
            }
            
            $endTime = microtime(true);
            $elapsed = $endTime - self::$startTimes[$name];
            unset(self::$startTimes[$name]);
            
            self::log("Timer '$name': {$elapsed} seconds");
            return $elapsed;
        }
        
        // 测量函数执行时间
        public static function measure($callback, $label = 'Function execution') {
            if (!self::$enabled) {
                return $callback();
            }
            
            $start = microtime(true);
            $result = $callback();
            $end = microtime(true);
            
            $elapsed = $end - $start;
            self::log("$label: {$elapsed} seconds");
            
            return $result;
        }
        
        // 计算内存使用
        public static function memoryUsage($label = 'Memory usage') {
            if (!self::$enabled) return;
            
            $current = memory_get_usage(true);
            $peak = memory_get_peak_usage(true);
            
            $currentFormatted = self::formatBytes($current);
            $peakFormatted = self::formatBytes($peak);
            
            self::log("$label - Current: $currentFormatted, Peak: $peakFormatted");
        }
        
        // 获取调用栈
        public static function getTrace($limit = 10) {
            if (!self::$enabled) return [];
            
            $backtrace = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, $limit + 1);
            array_shift($backtrace); // 移除当前函数
            
            $trace = [];
            foreach ($backtrace as $index => $call) {
                $trace[] = [
                    'index' => $index,
                    'function' => $call['function'] ?? 'unknown',
                    'class' => $call['class'] ?? null,
                    'file' => basename($call['file'] ?? 'unknown'),
                    'line' => $call['line'] ?? 'unknown'
                ];
            }
            
            return $trace;
        }
        
        // 显示调用栈
        public static function trace($limit = 10) {
            if (!self::$enabled) return;
            
            $trace = self::getTrace($limit);
            
            echo "<div style='background: #f8f8f8; border: 1px solid #ddd; padding: 10px; margin: 10px; font-family: monospace;'>";
            echo "<strong>Call Stack:</strong><br>";
            echo "<table style='width: 100%; border-collapse: collapse;'>";
            echo "<tr><th style='border: 1px solid #ddd; padding: 5px;'>#</th><th style='border: 1px solid #ddd; padding: 5px;'>Function</th><th style='border: 1px solid #ddd; padding: 5px;'>File</th><th style='border: 1px solid #ddd; padding: 5px;'>Line</th></tr>";
            
            foreach ($trace as $call) {
                $function = $call['class'] ? $call['class'] . '::' . $call['function'] : $call['function'];
                echo "<tr>";
                echo "<td style='border: 1px solid #ddd; padding: 5px;'>{$call['index']}</td>";
                echo "<td style='border: 1px solid #ddd; padding: 5px;'>{$function}</td>";
                echo "<td style='border: 1px solid #ddd; padding: 5px;'>{$call['file']}</td>";
                echo "<td style='border: 1px solid #ddd; padding: 5px;'>{$call['line']}</td>";
                echo "</tr>";
            }
            
            echo "</table>";
            echo "</div>";
        }
        
        // 获取所有日志
        public static function getLogs() {
            return self::$logs;
        }
        
        // 清除日志
        public static function clearLogs() {
            self::$logs = [];
        }
        
        // 格式化字节大小
        private static function formatBytes($bytes, $precision = 2) {
            $units = ['B', 'KB', 'MB', 'GB', 'TB'];
            
            for ($i = 0; $bytes > 1024 && $i < count($units) - 1; $i++) {
                $bytes /= 1024;
            }
            
            return round($bytes, $precision) . ' ' . $units[$i];
        }
        
        // 条件调试
        public static function if($condition, $callback) {
            if ($condition && self::$enabled) {
                $callback();
            }
        }
        
        // 循环调试
        public static function loop($array, $callback) {
            if (!self::$enabled) {
                foreach ($array as $key => $value) {
                    $callback($key, $value);
                }
                return;
            }
            
            echo "<div style='background: #f8f8f8; border: 1px solid #ddd; padding: 10px; margin: 10px;'>";
            echo "<strong>Loop Debug:</strong><br>";
            
            foreach ($array as $key => $value) {
                echo "<div style='border-left: 3px solid #007acc; padding-left: 10px; margin: 5px 0;'>";
                echo "<strong>Iteration: $key</strong><br>";
                echo "<pre style='background: #fff; padding: 5px; margin: 5px 0;'>";
                print_r($value);
                echo "</pre>";
                echo "</div>";
                
                $callback($key, $value);
            }
            
            echo "</div>";
        }
    }
    
    // 使用示例
    Debugger::enable();
    
    // 基础调试
    $user = ['name' => 'John', 'email' => 'john@example.com'];
    Debugger::dump($user, 'User Data');
    
    // 日志记录
    Debugger::log('User logged in', 'info');
    Debugger::log('Database connection failed', 'error');
    
    // 性能测量
    Debugger::startTimer('database_query');
    // 模拟数据库查询
    usleep(100000); // 100ms
    Debugger::endTimer('database_query');
    
    // 内存使用
    $largeArray = range(1, 10000);
    Debugger::memoryUsage('After creating large array');
    
    // 测量函数执行时间
    $result = Debugger::measure(function() {
        $sum = 0;
        for ($i = 0; $i < 1000000; $i++) {
            $sum += $i;
        }
        return $sum;
    }, 'Sum calculation');
    
    // 调用栈跟踪
    function outerFunction() {
        innerFunction();
    }
    
    function innerFunction() {
        Debugger::trace();
    }
    
    outerFunction();
    
    // 条件调试
    $debug = true;
    Debugger::if($debug, function() {
        echo "Debug information: Only shown when debug is true";
    });
    
    // 循环调试
    $users = [
        ['name' => 'John', 'role' => 'admin'],
        ['name' => 'Jane', 'role' => 'user'],
        ['name' => 'Bob', 'role' => 'user']
    ];
    
    Debugger::loop($users, function($index, $user) {
        // 在实际应用中可能需要对每个用户进行某些操作
    });
    
    // 获取调试日志
    $logs = Debugger::getLogs();
    echo "<h3>Debug Logs:</h3>";
    echo "<pre>" . implode("\n", $logs) . "</pre>";
?>
```

### 生产环境调试
```php
<?php
    class ProductionDebugger {
        private static $instance;
        private $logFile;
        private $sensitiveKeys = ['password', 'token', 'secret', 'key', 'credit_card'];
        
        private function __construct() {
            $this->logFile = __DIR__ . '/../logs/production.log';
            $this->ensureLogDirectory();
        }
        
        public static function getInstance() {
            if (!self::$instance) {
                self::$instance = new self();
            }
            return self::$instance;
        }
        
        private function ensureLogDirectory() {
            $logDir = dirname($this->logFile);
            if (!is_dir($logDir)) {
                mkdir($logDir, 0755, true);
            }
        }
        
        // 安全记录数据
        public function log($level, $message, $context = []) {
            $sanitizedContext = $this->sanitizeContext($context);
            
            $logEntry = [
                'timestamp' => date('Y-m-d H:i:s'),
                'level' => strtoupper($level),
                'message' => $message,
                'context' => $sanitizedContext,
                'request_id' => $this->getRequestId(),
                'user_id' => $this->getCurrentUserId(),
                'ip' => $this->getClientIp(),
                'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
            ];
            
            $this->writeLog($logEntry);
        }
        
        private function sanitizeContext($context) {
            $sanitized = [];
            
            foreach ($context as $key => $value) {
                if (in_array(strtolower($key), $this->sensitiveKeys)) {
                    $sanitized[$key] = '***REDACTED***';
                } elseif (is_array($value) || is_object($value)) {
                    $sanitized[$key] = $this->sanitizeRecursive($value);
                } else {
                    $sanitized[$key] = $value;
                }
            }
            
            return $sanitized;
        }
        
        private function sanitizeRecursive($data) {
            if (is_array($data)) {
                $sanitized = [];
                foreach ($data as $key => $value) {
                    if (in_array(strtolower($key), $this->sensitiveKeys)) {
                        $sanitized[$key] = '***REDACTED***';
                    } elseif (is_array($value) || is_object($value)) {
                        $sanitized[$key] = $this->sanitizeRecursive($value);
                    } else {
                        $sanitized[$key] = $value;
                    }
                }
                return $sanitized;
            } elseif (is_object($data)) {
                // 对于对象，只记录类名
                return get_class($data) . ' object';
            } else {
                return $data;
            }
        }
        
        private function writeLog($logEntry) {
            $jsonLog = json_encode($logEntry, JSON_UNESCAPED_UNICODE);
            file_put_contents($this->logFile, $jsonLog . "\n", FILE_APPEND | LOCK_EX);
            
            // 轮转日志文件
            $this->rotateLogIfNeeded();
        }
        
        private function rotateLogIfNeeded() {
            $maxSize = 10 * 1024 * 1024; // 10MB
            
            if (file_exists($this->logFile) && filesize($this->logFile) > $maxSize) {
                $backupFile = $this->logFile . '.' . date('Y-m-d-H-i-s');
                rename($this->logFile, $backupFile);
            }
        }
        
        private function getRequestId() {
            static $requestId;
            if (!$requestId) {
                $requestId = uniqid('req_', true);
            }
            return $requestId;
        }
        
        private function getCurrentUserId() {
            // 根据你的认证系统获取当前用户ID
            return $_SESSION['user_id'] ?? null;
        }
        
        private function getClientIp() {
            $ipKeys = ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR'];
            
            foreach ($ipKeys as $key) {
                if (!empty($_SERVER[$key])) {
                    $ips = explode(',', $_SERVER[$key]);
                    $ip = trim($ips[0]);
                    if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
                        return $ip;
                    }
                }
            }
            
            return $_SERVER['REMOTE_ADDR'] ?? 'unknown';
        }
        
        // 记录异常
        public function logException(Exception $e) {
            $context = [
                'exception_type' => get_class($e),
                'file' => $e->getFile(),
                'line' => $e->getLine(),
                'trace' => $e->getTraceAsString(),
                'code' => $e->getCode()
            ];
            
            $this->log('error', $e->getMessage(), $context);
        }
        
        // 记录性能数据
        public function logPerformance($label, $duration, $memory = null) {
            $context = [
                'label' => $label,
                'duration_seconds' => $duration,
                'memory_bytes' => $memory,
                'memory_peak_bytes' => memory_get_peak_usage(true)
            ];
            
            $this->log('performance', "Performance: $label", $context);
        }
        
        // 记录API调用
        public function logApiCall($endpoint, $method, $duration, $statusCode, $request = [], $response = []) {
            $context = [
                'endpoint' => $endpoint,
                'method' => $method,
                'duration_seconds' => $duration,
                'status_code' => $statusCode,
                'request' => $request,
                'response_size_bytes' => strlen(json_encode($response))
            ];
            
            $this->log('api', "API Call: $method $endpoint", $context);
        }
    }
    
    // 使用示例
    $debugger = ProductionDebugger::getInstance();
    
    // 记录信息
    $debugger->log('info', 'User logged in successfully', [
        'user_id' => 123,
        'login_method' => 'password'
    ]);
    
    // 记录错误
    $debugger->log('error', 'Database connection failed', [
        'database' => 'main_db',
        'error_code' => 'CONNECTION_TIMEOUT'
    ]);
    
    // 记录异常
    try {
        throw new DatabaseException('Connection failed', 'SELECT * FROM users', []);
    } catch (Exception $e) {
        $debugger->logException($e);
    }
    
    // 记录性能
    $debugger->logPerformance('API request', 0.5, 1024*1024);
    
    // 记录API调用
    $debugger->logApiCall('/api/users', 'GET', 0.2, 200, [], [
        'users' => [/* user data */]
    ]);
?>
```

## 日志系统

### 自定义日志类
```php
<?php
    class Logger {
        private static $instance;
        private $logFile;
        private $maxFileSize;
        private $maxFiles;
        private $logLevel;
        
        const EMERGENCY = 'emergency';
        const ALERT     = 'alert';
        const CRITICAL  = 'critical';
        const ERROR     = 'error';
        const WARNING   = 'warning';
        const NOTICE    = 'notice';
        const INFO      = 'info';
        const DEBUG     = 'debug';
        
        private static $levels = [
            self::DEBUG     => 0,
            self::INFO      => 1,
            self::NOTICE    => 2,
            self::WARNING   => 3,
            self::ERROR     => 4,
            self::CRITICAL  => 5,
            self::ALERT     => 6,
            self::EMERGENCY => 7
        ];
        
        public function __construct($config = []) {
            $this->logFile = $config['log_file'] ?? __DIR__ . '/../logs/app.log';
            $this->maxFileSize = $config['max_file_size'] ?? 10 * 1024 * 1024; // 10MB
            $this->maxFiles = $config['max_files'] ?? 5;
            $this->logLevel = $config['log_level'] ?? self::INFO;
            
            $this->ensureLogDirectory();
        }
        
        public static function getInstance($config = []) {
            if (!self::$instance) {
                self::$instance = new self($config);
            }
            return self::$instance;
        }
        
        private function ensureLogDirectory() {
            $logDir = dirname($this->logFile);
            if (!is_dir($logDir)) {
                mkdir($logDir, 0755, true);
            }
        }
        
        public function emergency($message, $context = []) {
            $this->log(self::EMERGENCY, $message, $context);
        }
        
        public function alert($message, $context = []) {
            $this->log(self::ALERT, $message, $context);
        }
        
        public function critical($message, $context = []) {
            $this->log(self::CRITICAL, $message, $context);
        }
        
        public function error($message, $context = []) {
            $this->log(self::ERROR, $message, $context);
        }
        
        public function warning($message, $context = []) {
            $this->log(self::WARNING, $message, $context);
        }
        
        public function notice($message, $context = []) {
            $this->log(self::NOTICE, $message, $context);
        }
        
        public function info($message, $context = []) {
            $this->log(self::INFO, $message, $context);
        }
        
        public function debug($message, $context = []) {
            $this->log(self::DEBUG, $message, $context);
        }
        
        public function log($level, $message, $context = []) {
            if (self::$levels[$level] < self::$levels[$this->logLevel]) {
                return; // 跳过低级别日志
            }
            
            $record = $this->formatRecord($level, $message, $context);
            $this->write($record);
            $this->rotateIfNeeded();
        }
        
        private function formatRecord($level, $message, $context) {
            $timestamp = date('Y-m-d H:i:s');
            $contextString = empty($context) ? '' : ' ' . json_encode($context, JSON_UNESCAPED_UNICODE);
            
            return "[$timestamp] [$level] $message$contextString";
        }
        
        private function write($record) {
            file_put_contents($this->logFile, $record . "\n", FILE_APPEND | LOCK_EX);
        }
        
        private function rotateIfNeeded() {
            if (!file_exists($this->logFile) || filesize($this->logFile) < $this->maxFileSize) {
                return;
            }
            
            // 创建备份文件
            $backupFile = $this->logFile . '.' . date('Y-m-d-H-i-s');
            rename($this->logFile, $backupFile);
            
            // 清理旧文件
            $this->cleanOldLogs();
        }
        
        private function cleanOldLogs() {
            $logDir = dirname($this->logFile);
            $files = glob($logDir . '/app.log.*');
            
            if (count($files) <= $this->maxFiles) {
                return;
            }
            
            // 按修改时间排序
            usort($files, function($a, $b) {
                return filemtime($a) - filemtime($b);
            });
            
            // 删除最旧的文件
            $toDelete = count($files) - $this->maxFiles;
            for ($i = 0; $i < $toDelete; $i++) {
                unlink($files[$i]);
            }
        }
        
        // 设置日志级别
        public function setLogLevel($level) {
            if (isset(self::$levels[$level])) {
                $this->logLevel = $level;
            }
        }
        
        // 获取日志文件大小
        public function getLogSize() {
            return file_exists($this->logFile) ? filesize($this->logFile) : 0;
        }
        
        // 清空日志
        public function clear() {
            if (file_exists($this->logFile)) {
                unlink($this->logFile);
            }
        }
        
        // 读取最近的日志
        public function recentLogs($lines = 50) {
            if (!file_exists($this->logFile)) {
                return [];
            }
            
            $content = file_get_contents($this->logFile);
            $logLines = explode("\n", trim($content));
            
            return array_slice($logLines, -$lines);
        }
    }
    
    // 使用示例
    $logger = Logger::getInstance([
        'log_file' => __DIR__ . '/logs/custom.log',
        'log_level' => Logger::DEBUG,
        'max_file_size' => 5 * 1024 * 1024, // 5MB
        'max_files' => 10
    ]);
    
    // 记录不同级别的日志
    $logger->debug('Debug message', ['debug_info' => 'some debug data']);
    $logger->info('Application started', ['version' => '1.0.0']);
    $logger->warning('Low disk space', ['free_space' => '1GB']);
    $logger->error('Database connection failed', ['error' => 'Connection timeout']);
    $logger->critical('System crash', ['error_code' => 'FATAL_ERROR']);
    
    // 读取最近的日志
    $recentLogs = $logger->recentLogs(10);
    foreach ($recentLogs as $logLine) {
        echo $logLine . "\n";
    }
?>
```

## 最佳实践

1. **错误处理策略**：
   - 开发环境显示所有错误信息
   - 生产环境记录错误但避免敏感信息泄露
   - 使用适当的HTTP状态码

2. **日志记录原则**：
   - 记录足够的上下文信息
   - 避免记录敏感数据
   - 使用结构化日志格式
   - 定期清理和轮转日志文件

3. **调试技巧**：
   - 使用断点调试而不是echo
   - 记录关键数据流
   - 监控性能指标
   - 使用版本控制管理调试代码

4. **异常处理**：
   - 创建有意义的自定义异常
   - 不要捕获太宽泛的异常
   - 提供有用的错误信息
   - 记录异常的完整上下文

5. **监控和告警**：
   - 设置关键错误告警
   - 监控日志文件大小
   - 定期检查错误趋势
   - 实施健康检查机制