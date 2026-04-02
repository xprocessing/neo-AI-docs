# PHP Web开发基础

## HTTP基础

### HTTP请求处理
```php
<?php
    // 获取HTTP方法
    $method = $_SERVER['REQUEST_METHOD'];
    echo "请求方法：$method\n";
    
    // 获取请求URI
    $uri = $_SERVER['REQUEST_URI'];
    echo "请求URI：$uri\n";
    
    // 获取查询字符串
    $queryString = $_SERVER['QUERY_STRING'];
    echo "查询字符串：$queryString\n";
    
    // 获取协议
    $protocol = $_SERVER['SERVER_PROTOCOL'];
    echo "协议：$protocol\n";
    
    // 检查是否HTTPS
    $isHttps = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on';
    echo "是否HTTPS：" . ($isHttps ? '是' : '否') . "\n";
    
    // 获取客户端IP
    $ip = $_SERVER['REMOTE_ADDR'];
    echo "客户端IP：$ip\n";
    
    // 获取User-Agent
    $userAgent = $_SERVER['HTTP_USER_AGENT'];
    echo "User-Agent：$userAgent\n";
    
    // 获取Referer
    $referer = $_SERVER['HTTP_REFERER'] ?? '无';
    echo "来源页面：$referer\n";
    
    // 获取请求头信息
    function getHeaders() {
        $headers = [];
        foreach ($_SERVER as $key => $value) {
            if (substr($key, 0, 5) === 'HTTP_') {
                $header = str_replace(' ', '-', ucwords(str_replace('_', ' ', strtolower(substr($key, 5)))));
                $headers[$header] = $value;
            }
        }
        return $headers;
    }
    
    $headers = getHeaders();
    echo "所有请求头：\n";
    print_r($headers);
?>
```

### HTTP响应
```php
<?php
    // 设置响应状态码
    http_response_code(200); // OK
    http_response_code(404); // Not Found
    http_response_code(500); // Internal Server Error
    
    // 设置响应头
    header('Content-Type: text/html; charset=utf-8');
    header('Cache-Control: no-cache, no-store, must-revalidate');
    header('Pragma: no-cache');
    header('Expires: 0');
    
    // 设置自定义响应头
    header('X-Custom-Header: CustomValue');
    
    // 重定向
    header('Location: https://www.example.com');
    exit();
    
    // 文件下载
    function downloadFile($filepath, $filename = null) {
        if (!file_exists($filepath)) {
            http_response_code(404);
            echo '文件不存在';
            return;
        }
        
        $filename = $filename ?: basename($filepath);
        $filesize = filesize($filepath);
        $mimeType = mime_content_type($filepath);
        
        header('Content-Type: ' . $mimeType);
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Content-Length: ' . $filesize);
        header('Cache-Control: private, no-transform, no-store, must-revalidate');
        
        readfile($filepath);
        exit;
    }
    
    // JSON响应
    function jsonResponse($data, $statusCode = 200) {
        http_response_code($statusCode);
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
        header('Pragma: no-cache');
        
        echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit;
    }
    
    // CORS设置
    function setCORS() {
        header('Access-Control-Allow-Origin: *');
        header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
        header('Access-Control-Allow-Headers: Content-Type, Authorization');
        header('Access-Control-Allow-Credentials: true');
        header('Access-Control-Max-Age: 3600');
    }
    
    // 处理OPTIONS请求（预检）
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        setCORS();
        exit(0);
    }
    
    // 使用示例
    $data = ['message' => 'Hello World', 'status' => 'success'];
    jsonResponse($data, 200);
?>
```

## 表单处理

### GET和POST数据处理
```php
<?php
    // 获取GET参数
    $name = $_GET['name'] ?? '';
    $page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
    $search = $_GET['search'] ?? '';
    
    // 获取POST数据
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    $email = $_POST['email'] ?? '';
    
    // 获取复选框数据
    $hobbies = $_POST['hobbies'] ?? [];
    if (is_string($hobbies)) {
        $hobbies = [$hobbies]; // 单个复选框
    }
    
    // 获取文件上传
    if (isset($_FILES['avatar'])) {
        $file = $_FILES['avatar'];
        $filename = $file['name'];
        $tmpName = $file['tmp_name'];
        $size = $file['size'];
        $error = $file['error'];
        $type = $file['type'];
    }
    
    // 获取JSON数据
    function getJsonInput() {
        $json = file_get_contents('php://input');
        return json_decode($json, true) ?: [];
    }
    
    $jsonData = getJsonInput();
    
    // 获取原始POST数据
    $rawData = file_get_contents('php://input');
    
    // 获取请求头
    $contentType = $_SERVER['CONTENT_TYPE'] ?? '';
    
    // 根据内容类型处理数据
    function parseRequestBody() {
        $contentType = $_SERVER['CONTENT_TYPE'] ?? '';
        
        if (strpos($contentType, 'application/json') !== false) {
            return getJsonInput();
        } elseif (strpos($contentType, 'application/x-www-form-urlencoded') !== false) {
            return $_POST;
        } elseif (strpos($contentType, 'multipart/form-data') !== false) {
            return $_POST;
        } else {
            return ['raw' => file_get_contents('php://input')];
        }
    }
    
    $requestData = parseRequestBody();
?>
```

### 表单验证类
```php
<?php
    class FormValidator {
        private $errors = [];
        private $data;
        private $rules;
        
        public function __construct($data, $rules = []) {
            $this->data = $data;
            $this->rules = $rules;
        }
        
        // 添加验证规则
        public function rule($field, $rules) {
            $this->rules[$field] = $rules;
            return $this;
        }
        
        // 执行验证
        public function validate() {
            foreach ($this->rules as $field => $rules) {
                $value = $this->data[$field] ?? null;
                $fieldRules = explode('|', $rules);
                
                foreach ($fieldRules as $rule) {
                    $this->validateField($field, $value, $rule);
                }
            }
            
            return empty($this->errors);
        }
        
        // 验证单个字段
        private function validateField($field, $value, $rule) {
            $params = [];
            
            // 解析规则参数
            if (strpos($rule, ':') !== false) {
                list($rule, $paramStr) = explode(':', $rule, 2);
                $params = explode(',', $paramStr);
            }
            
            switch ($rule) {
                case 'required':
                    if (empty($value)) {
                        $this->addError($field, "$field 是必填字段");
                    }
                    break;
                    
                case 'email':
                    if (!empty($value) && !filter_var($value, FILTER_VALIDATE_EMAIL)) {
                        $this->addError($field, "$field 必须是有效的邮箱地址");
                    }
                    break;
                    
                case 'min':
                    $min = $params[0] ?? 0;
                    if (strlen($value) < $min) {
                        $this->addError($field, "$field 长度不能少于 $min 个字符");
                    }
                    break;
                    
                case 'max':
                    $max = $params[0] ?? 255;
                    if (strlen($value) > $max) {
                        $this->addError($field, "$field 长度不能超过 $max 个字符");
                    }
                    break;
                    
                case 'numeric':
                    if (!empty($value) && !is_numeric($value)) {
                        $this->addError($field, "$field 必须是数字");
                    }
                    break;
                    
                case 'integer':
                    if (!empty($value) && !filter_var($value, FILTER_VALIDATE_INT)) {
                        $this->addError($field, "$field 必须是整数");
                    }
                    break;
                    
                case 'url':
                    if (!empty($value) && !filter_var($value, FILTER_VALIDATE_URL)) {
                        $this->addError($field, "$field 必须是有效的URL");
                    }
                    break;
                    
                case 'regex':
                    $pattern = $params[0] ?? '';
                    if (!empty($value) && !preg_match($pattern, $value)) {
                        $this->addError($field, "$field 格式不正确");
                    }
                    break;
                    
                case 'in':
                    $allowed = $params ?? [];
                    if (!empty($value) && !in_array($value, $allowed)) {
                        $this->addError($field, "$field 必须是以下值之一：" . implode(', ', $allowed));
                    }
                    break;
            }
        }
        
        // 添加错误
        private function addError($field, $message) {
            if (!isset($this->errors[$field])) {
                $this->errors[$field] = [];
            }
            $this->errors[$field][] = $message;
        }
        
        // 获取错误信息
        public function getErrors() {
            return $this->errors;
        }
        
        // 获取第一个错误
        public function getFirstError($field) {
            return $this->errors[$field][0] ?? '';
        }
        
        // 是否有错误
        public function hasErrors() {
            return !empty($this->errors);
        }
        
        // 获取清理后的数据
        public function getSanitizedData() {
            $sanitized = [];
            
            foreach ($this->data as $key => $value) {
                if (is_string($value)) {
                    $sanitized[$key] = trim($value);
                } else {
                    $sanitized[$key] = $value;
                }
            }
            
            return $sanitized;
        }
    }
    
    // 使用示例
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $validator = new FormValidator($_POST, [
            'username' => 'required|min:3|max:20',
            'email' => 'required|email',
            'age' => 'required|integer|min:18|max:120',
            'password' => 'required|min:6',
            'confirm_password' => 'required',
            'website' => 'url',
            'gender' => 'required|in:male,female,other'
        ]);
        
        if ($validator->validate()) {
            $data = $validator->getSanitizedData();
            echo "验证成功！数据：";
            print_r($data);
        } else {
            echo "验证失败！\n";
            print_r($validator->getErrors());
        }
    }
?>
```

### 表单生成器
```php
<?php
    class FormBuilder {
        private $fields = [];
        private $attributes = [];
        private $errors = [];
        
        public function __construct($action = '', $method = 'POST', $attributes = []) {
            $this->attributes['action'] = $action;
            $this->attributes['method'] = $method;
            $this->attributes = array_merge($this->attributes, $attributes);
        }
        
        // 文本输入
        public function text($name, $label = '', $value = '', $attributes = []) {
            $this->fields[] = [
                'type' => 'text',
                'name' => $name,
                'label' => $label,
                'value' => $value,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 密码输入
        public function password($name, $label = '', $attributes = []) {
            $this->fields[] = [
                'type' => 'password',
                'name' => $name,
                'label' => $label,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 邮箱输入
        public function email($name, $label = '', $value = '', $attributes = []) {
            $this->fields[] = [
                'type' => 'email',
                'name' => $name,
                'label' => $label,
                'value' => $value,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 文本域
        public function textarea($name, $label = '', $value = '', $attributes = []) {
            $this->fields[] = [
                'type' => 'textarea',
                'name' => $name,
                'label' => $label,
                'value' => $value,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 下拉选择
        public function select($name, $label = '', $options = [], $selected = '', $attributes = []) {
            $this->fields[] = [
                'type' => 'select',
                'name' => $name,
                'label' => $label,
                'options' => $options,
                'selected' => $selected,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 复选框
        public function checkbox($name, $label = '', $value = '1', $checked = false, $attributes = []) {
            $this->fields[] = [
                'type' => 'checkbox',
                'name' => $name,
                'label' => $label,
                'value' => $value,
                'checked' => $checked,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 单选框
        public function radio($name, $label = '', $value = '1', $checked = false, $attributes = []) {
            $this->fields[] = [
                'type' => 'radio',
                'name' => $name,
                'label' => $label,
                'value' => $value,
                'checked' => $checked,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 文件上传
        public function file($name, $label = '', $attributes = []) {
            $this->fields[] = [
                'type' => 'file',
                'name' => $name,
                'label' => $label,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 提交按钮
        public function submit($text = '提交', $attributes = []) {
            $this->fields[] = [
                'type' => 'submit',
                'text' => $text,
                'attributes' => $attributes
            ];
            return $this;
        }
        
        // 设置错误信息
        public function setErrors($errors) {
            $this->errors = $errors;
            return $this;
        }
        
        // 渲染表单
        public function render() {
            $html = '<form';
            foreach ($this->attributes as $key => $value) {
                $html .= ' ' . $key . '="' . htmlspecialchars($value) . '"';
            }
            $html .= '>' . "\n";
            
            foreach ($this->fields as $field) {
                $html .= $this->renderField($field);
            }
            
            $html .= '</form>';
            return $html;
        }
        
        // 渲染字段
        private function renderField($field) {
            $html = '<div class="form-group">' . "\n";
            
            if (!empty($field['label'])) {
                $html .= '  <label for="' . $field['name'] . '">' . htmlspecialchars($field['label']) . '</label>' . "\n";
            }
            
            // 显示错误信息
            if (isset($this->errors[$field['name']])) {
                $html .= '  <div class="error-message">' . htmlspecialchars($this->errors[$field['name']][0]) . '</div>' . "\n";
            }
            
            switch ($field['type']) {
                case 'text':
                case 'email':
                case 'password':
                    $html .= $this->renderInput($field);
                    break;
                case 'textarea':
                    $html .= $this->renderTextarea($field);
                    break;
                case 'select':
                    $html .= $this->renderSelect($field);
                    break;
                case 'checkbox':
                    $html .= $this->renderCheckbox($field);
                    break;
                case 'radio':
                    $html .= $this->renderRadio($field);
                    break;
                case 'file':
                    $html .= $this->renderFile($field);
                    break;
                case 'submit':
                    $html .= $this->renderSubmit($field);
                    break;
            }
            
            $html .= '</div>' . "\n";
            return $html;
        }
        
        // 渲染输入框
        private function renderInput($field) {
            $attributes = $field['attributes'];
            $attributes['type'] = $field['type'];
            $attributes['name'] = $field['name'];
            if (isset($field['value'])) {
                $attributes['value'] = $field['value'];
            }
            if (isset($this->errors[$field['name']])) {
                $attributes['class'] = ($attributes['class'] ?? '') . ' error';
            }
            
            $attrStr = '';
            foreach ($attributes as $key => $value) {
                $attrStr .= ' ' . $key . '="' . htmlspecialchars($value) . '"';
            }
            
            return '  <input' . $attrStr . '>' . "\n";
        }
        
        // 渲染文本域
        private function renderTextarea($field) {
            $attributes = $field['attributes'];
            $attributes['name'] = $field['name'];
            if (isset($this->errors[$field['name']])) {
                $attributes['class'] = ($attributes['class'] ?? '') . ' error';
            }
            
            $attrStr = '';
            foreach ($attributes as $key => $value) {
                $attrStr .= ' ' . $key . '="' . htmlspecialchars($value) . '"';
            }
            
            $value = isset($field['value']) ? htmlspecialchars($field['value']) : '';
            return '  <textarea' . $attrStr . '>' . $value . '</textarea>' . "\n";
        }
        
        // 渲染下拉选择
        private function renderSelect($field) {
            $attributes = $field['attributes'];
            $attributes['name'] = $field['name'];
            if (isset($this->errors[$field['name']])) {
                $attributes['class'] = ($attributes['class'] ?? '') . ' error';
            }
            
            $attrStr = '';
            foreach ($attributes as $key => $value) {
                $attrStr .= ' ' . $key . '="' . htmlspecialchars($value) . '"';
            }
            
            $html = '  <select' . $attrStr . '>' . "\n";
            
            foreach ($field['options'] as $value => $label) {
                $selected = ($value == $field['selected']) ? ' selected' : '';
                $html .= '    <option value="' . htmlspecialchars($value) . '"' . $selected . '>' . htmlspecialchars($label) . '</option>' . "\n";
            }
            
            $html .= '  </select>' . "\n";
            return $html;
        }
        
        // 渲染复选框
        private function renderCheckbox($field) {
            $attributes = $field['attributes'];
            $attributes['type'] = 'checkbox';
            $attributes['name'] = $field['name'];
            $attributes['value'] = $field['value'];
            if ($field['checked']) {
                $attributes['checked'] = 'checked';
            }
            
            $attrStr = '';
            foreach ($attributes as $key => $value) {
                $attrStr .= ' ' . $key . '="' . htmlspecialchars($value) . '"';
            }
            
            return '  <input' . $attrStr . '> ' . htmlspecialchars($field['label']) . "\n";
        }
        
        // 渲染单选框
        private function renderRadio($field) {
            $attributes = $field['attributes'];
            $attributes['type'] = 'radio';
            $attributes['name'] = $field['name'];
            $attributes['value'] = $field['value'];
            if ($field['checked']) {
                $attributes['checked'] = 'checked';
            }
            
            $attrStr = '';
            foreach ($attributes as $key => $value) {
                $attrStr .= ' ' . $key . '="' . htmlspecialchars($value) . '"';
            }
            
            return '  <input' . $attrStr . '> ' . htmlspecialchars($field['label']) . "\n";
        }
        
        // 渲染文件上传
        private function renderFile($field) {
            $attributes = $field['attributes'];
            $attributes['type'] = 'file';
            $attributes['name'] = $field['name'];
            if (isset($this->errors[$field['name']])) {
                $attributes['class'] = ($attributes['class'] ?? '') . ' error';
            }
            
            $attrStr = '';
            foreach ($attributes as $key => $value) {
                $attrStr .= ' ' . $key . '="' . htmlspecialchars($value) . '"';
            }
            
            return '  <input' . $attrStr . '>' . "\n";
        }
        
        // 渲染提交按钮
        private function renderSubmit($field) {
            $attributes = $field['attributes'];
            $attributes['type'] = 'submit';
            $attributes['value'] = $field['text'];
            
            $attrStr = '';
            foreach ($attributes as $key => $value) {
                $attrStr .= ' ' . $key . '="' . htmlspecialchars($value) . '"';
            }
            
            return '  <input' . $attrStr . '>' . "\n";
        }
    }
    
    // 使用示例
    $form = new FormBuilder('/register.php', 'POST', ['class' => 'user-form']);
    
    $form->text('username', '用户名', '', ['placeholder' => '请输入用户名'])
         ->email('email', '邮箱地址', '', ['placeholder' => '请输入邮箱'])
         ->password('password', '密码')
         ->select('gender', '性别', ['male' => '男', 'female' => '女', 'other' => '其他'])
         ->checkbox('agree', '我同意服务条款', '1', false)
         ->submit('注册');
    
    // 设置错误信息
    $errors = [
        'username' => ['用户名不能为空']
    ];
    $form->setErrors($errors);
    
    echo $form->render();
?>
```

## Session和Cookie

### Session管理
```php
<?php
    // 启动Session
    session_start();
    
    // 设置Session数据
    $_SESSION['user_id'] = 123;
    $_SESSION['username'] = '张三';
    $_SESSION['login_time'] = time();
    $_SESSION['cart'] = [
        ['id' => 1, 'name' => '商品A', 'price' => 100],
        ['id' => 2, 'name' => '商品B', 'price' => 200]
    ];
    
    // 获取Session数据
    $userId = $_SESSION['user_id'] ?? null;
    $username = $_SESSION['username'] ?? '';
    
    // 检查Session是否存在
    if (isset($_SESSION['user_id'])) {
        echo "用户已登录，ID：" . $_SESSION['user_id'];
    }
    
    // 删除Session数据
    unset($_SESSION['cart']);
    
    // 销毁所有Session数据
    session_destroy();
    
    // Session配置
    ini_set('session.cookie_lifetime', 3600); // Cookie有效期1小时
    ini_set('session.gc_maxlifetime', 3600);   // Session数据有效期1小时
    ini_set('session.use_strict_mode', 1);     // 严格模式
    ini_set('session.cookie_httponly', 1);      // HTTP Only
    ini_set('session.cookie_secure', 1);       // 仅HTTPS
    ini_set('session.cookie_samesite', 'Lax'); // SameSite属性
    
    // Session工具类
    class SessionManager {
        private static $instance = null;
        private $sessionLifetime = 3600;
        
        public static function getInstance() {
            if (self::$instance === null) {
                self::$instance = new self();
            }
            return self::$instance;
        }
        
        private function __construct() {
            $this->configureSession();
            if (session_status() === PHP_SESSION_NONE) {
                session_start();
            }
        }
        
        private function configureSession() {
            ini_set('session.cookie_lifetime', $this->sessionLifetime);
            ini_set('session.gc_maxlifetime', $this->sessionLifetime);
            ini_set('session.use_strict_mode', 1);
            ini_set('session.cookie_httponly', 1);
            ini_set('session.cookie_secure', isset($_SERVER['HTTPS']));
            ini_set('session.cookie_samesite', 'Lax');
        }
        
        public function set($key, $value) {
            $_SESSION[$key] = $value;
            return $this;
        }
        
        public function get($key, $default = null) {
            return $_SESSION[$key] ?? $default;
        }
        
        public function has($key) {
            return isset($_SESSION[$key]);
        }
        
        public function remove($key) {
            unset($_SESSION[$key]);
            return $this;
        }
        
        public function flash($key, $value) {
            $_SESSION['flash'][$key] = $value;
            return $this;
        }
        
        public function getFlash($key, $default = null) {
            $value = $_SESSION['flash'][$key] ?? $default;
            $this->removeFlash($key);
            return $value;
        }
        
        private function removeFlash($key) {
            unset($_SESSION['flash'][$key]);
            if (empty($_SESSION['flash'])) {
                unset($_SESSION['flash']);
            }
        }
        
        public function regenerateId() {
            session_regenerate_id(true);
            return $this;
        }
        
        public function destroy() {
            $_SESSION = [];
            if (ini_get('session.use_cookies')) {
                $params = session_get_cookie_params();
                setcookie(session_name(), '', time() - 42000,
                    $params['path'], $params['domain'],
                    $params['secure'], $params['httponly']
                );
            }
            session_destroy();
            return $this;
        }
    }
    
    // 使用Session管理器
    $session = SessionManager::getInstance();
    
    $session->set('user', ['id' => 123, 'name' => '张三']);
    $session->flash('message', '登录成功');
    
    $user = $session->get('user');
    $message = $session->getFlash('message');
?>
```

### Cookie管理
```php
<?php
    // 设置Cookie
    setcookie('username', '张三', time() + 3600, '/', '', false, true);
    setcookie('theme', 'dark', time() + 86400 * 30, '/', '', true, true);
    
    // 获取Cookie
    $username = $_COOKIE['username'] ?? '';
    $theme = $_COOKIE['theme'] ?? 'light';
    
    // 删除Cookie
    setcookie('username', '', time() - 3600, '/');
    
    // Cookie工具类
    class CookieManager {
        private static $defaultOptions = [
            'expires' => 0,
            'path' => '/',
            'domain' => '',
            'secure' => false,
            'httponly' => true,
            'samesite' => 'Lax'
        ];
        
        public static function set($name, $value, $options = []) {
            $options = array_merge(self::$defaultOptions, $options);
            
            if (!is_numeric($options['expires'])) {
                $options['expires'] = strtotime($options['expires']);
            }
            
            // 构建Cookie头
            $header = sprintf(
                '%s=%s; expires=%s; path=%s; samesite=%s',
                $name,
                rawurlencode($value),
                gmdate('D, d-M-Y H:i:s T', $options['expires']),
                $options['path'],
                $options['samesite']
            );
            
            if (!empty($options['domain'])) {
                $header .= '; domain=' . $options['domain'];
            }
            
            if ($options['secure']) {
                $header .= '; secure';
            }
            
            if ($options['httponly']) {
                $header .= '; httponly';
            }
            
            header('Set-Cookie: ' . $header, false);
        }
        
        public static function get($name, $default = null) {
            return $_COOKIE[$name] ?? $default;
        }
        
        public static function has($name) {
            return isset($_COOKIE[$name]);
        }
        
        public static function remove($name, $options = []) {
            $options = array_merge(self::$defaultOptions, $options);
            $options['expires'] = time() - 3600;
            self::set($name, '', $options);
        }
        
        public static function clear($path = '/') {
            foreach ($_COOKIE as $name => $value) {
                self::remove($name, ['path' => $path]);
            }
        }
        
        // 安全Cookie设置
        public static function setSecure($name, $value, $expires = '+1 day') {
            self::set($name, $value, [
                'expires' => $expires,
                'secure' => true,
                'httponly' => true,
                'samesite' => 'Strict'
            ]);
        }
    }
    
    // 使用Cookie管理器
    CookieManager::setSecure('auth_token', 'abc123');
    $token = CookieManager::get('auth_token');
?>
```

## 路由系统

### 简单路由实现
```php
<?php
    class Router {
        private $routes = [];
        private $notFoundHandler;
        
        // 添加路由
        public function add($method, $path, $handler) {
            $this->routes[] = [
                'method' => strtoupper($method),
                'path' => $path,
                'handler' => $handler
            ];
        }
        
        // GET路由
        public function get($path, $handler) {
            $this->add('GET', $path, $handler);
        }
        
        // POST路由
        public function post($path, $handler) {
            $this->add('POST', $path, $handler);
        }
        
        // PUT路由
        public function put($path, $handler) {
            $this->add('PUT', $path, $handler);
        }
        
        // DELETE路由
        public function delete($path, $handler) {
            $this->add('DELETE', $path, $handler);
        }
        
        // 设置404处理器
        public function setNotFoundHandler($handler) {
            $this->notFoundHandler = $handler;
        }
        
        // 路由调度
        public function dispatch() {
            $method = $_SERVER['REQUEST_METHOD'];
            $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
            
            foreach ($this->routes as $route) {
                if ($route['method'] === $method && $this->matchPath($route['path'], $path)) {
                    $params = $this->extractParams($route['path'], $path);
                    return $this->callHandler($route['handler'], $params);
                }
            }
            
            // 404处理
            if ($this->notFoundHandler) {
                return $this->callHandler($this->notFoundHandler);
            }
            
            http_response_code(404);
            echo "404 Not Found";
        }
        
        // 路径匹配
        private function matchPath($routePath, $requestPath) {
            $routePattern = preg_replace('/\{[^}]+\}/', '([^/]+)', $routePath);
            $routePattern = '#^' . $routePattern . '$#';
            return preg_match($routePattern, $requestPath);
        }
        
        // 提取参数
        private function extractParams($routePath, $requestPath) {
            $params = [];
            
            $routeParts = explode('/', trim($routePath, '/'));
            $requestParts = explode('/', trim($requestPath, '/'));
            
            foreach ($routeParts as $index => $part) {
                if (preg_match('/\{([^}]+)\}/', $part, $matches)) {
                    $paramName = $matches[1];
                    $params[$paramName] = $requestParts[$index] ?? null;
                }
            }
            
            return $params;
        }
        
        // 调用处理器
        private function callHandler($handler, $params = []) {
            if (is_callable($handler)) {
                return call_user_func_array($handler, $params);
            } elseif (is_string($handler)) {
                list($class, $method) = explode('@', $handler);
                if (class_exists($class)) {
                    $controller = new $class();
                    if (method_exists($controller, $method)) {
                        return call_user_func_array([$controller, $method], $params);
                    }
                }
            }
            
            throw new Exception("Invalid route handler");
        }
    }
    
    // 使用示例
    $router = new Router();
    
    // 路由定义
    $router->get('/', function() {
        echo "首页";
    });
    
    $router->get('/about', function() {
        echo "关于我们";
    });
    
    // 带参数的路由
    $router->get('/user/{id}', function($id) {
        echo "用户ID：$id";
    });
    
    $router->get('/post/{id}/comment/{commentId}', function($id, $commentId) {
        echo "文章ID：$id，评论ID：$commentId";
    });
    
    // 控制器路由
    $router->get('/users', 'UserController@index');
    $router->get('/users/create', 'UserController@create');
    $router->post('/users', 'UserController@store');
    $router->get('/users/{id}', 'UserController@show');
    $router->get('/users/{id}/edit', 'UserController@edit');
    $router->put('/users/{id}', 'UserController@update');
    $router->delete('/users/{id}', 'UserController@destroy');
    
    // 404处理
    $router->setNotFoundHandler(function() {
        http_response_code(404);
        include 'views/404.php';
    });
    
    // 调度路由
    $router->dispatch();
    
    // 控制器示例
    class UserController {
        public function index() {
            echo "用户列表";
        }
        
        public function create() {
            echo "创建用户表单";
        }
        
        public function store() {
            echo "保存用户";
        }
        
        public function show($id) {
            echo "显示用户：$id";
        }
        
        public function edit($id) {
            echo "编辑用户：$id";
        }
        
        public function update($id) {
            echo "更新用户：$id";
        }
        
        public function destroy($id) {
            echo "删除用户：$id";
        }
    }
?>
```

## RESTful API开发

### API响应处理
```php
<?php
    class ApiResponse {
        private $statusCode;
        private $data;
        private $message;
        private $headers = [];
        
        public function __construct($statusCode = 200, $data = null, $message = '') {
            $this->statusCode = $statusCode;
            $this->data = $data;
            $this->message = $message;
        }
        
        // 成功响应
        public static function success($data = null, $message = 'Success') {
            return new self(200, $data, $message);
        }
        
        // 创建成功响应
        public static function created($data = null, $message = 'Created') {
            return new self(201, $data, $message);
        }
        
        // 无内容响应
        public static function noContent($message = 'No Content') {
            return new self(204, null, $message);
        }
        
        // 错误响应
        public static function error($statusCode, $message, $data = null) {
            return new self($statusCode, $data, $message);
        }
        
        // 验证错误响应
        public static function validationError($errors) {
            return new self(422, $errors, 'Validation Error');
        }
        
        // 未找到响应
        public static function notFound($message = 'Not Found') {
            return new self(404, null, $message);
        }
        
        // 未授权响应
        public static function unauthorized($message = 'Unauthorized') {
            return new self(401, null, $message);
        }
        
        // 禁止访问响应
        public static function forbidden($message = 'Forbidden') {
            return new self(403, null, $message);
        }
        
        // 服务器错误响应
        public static function serverError($message = 'Internal Server Error') {
            return new self(500, null, $message);
        }
        
        // 添加响应头
        public function withHeader($name, $value) {
            $this->headers[$name] = $value;
            return $this;
        }
        
        // 发送响应
        public function send() {
            // 设置状态码
            http_response_code($this->statusCode);
            
            // 设置响应头
            foreach ($this->headers as $name => $value) {
                header("$name: $value");
            }
            
            // 设置默认JSON头
            if (!headers_sent()) {
                header('Content-Type: application/json; charset=utf-8');
                header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
                header('Pragma: no-cache');
            }
            
            // 构建响应数据
            $response = [
                'status' => $this->statusCode,
                'message' => $this->message,
                'data' => $this->data
            ];
            
            // 输出JSON
            echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            exit;
        }
    }
    
    // API基础控制器
    abstract class ApiController {
        protected $request;
        protected $response;
        
        public function __construct() {
            $this->request = new ApiRequest();
            $this->response = new ApiResponse();
        }
        
        // 获取请求数据
        protected function getRequestData() {
            return $this->request->getData();
        }
        
        // 获取查询参数
        protected function getQueryParam($key, $default = null) {
            return $this->request->getQueryParam($key, $default);
        }
        
        // 获取路径参数
        protected function getPathParam($key, $default = null) {
            return $this->request->getPathParam($key, $default);
        }
        
        // 验证输入
        protected function validate($rules, $data = null) {
            $data = $data ?: $this->getRequestData();
            $validator = new ApiValidator($data, $rules);
            
            if (!$validator->validate()) {
                ApiResponse::validationError($validator->getErrors())->send();
            }
            
            return $validator->getValidatedData();
        }
    }
    
    // API请求类
    class ApiRequest {
        private $data;
        private $queryParams;
        private $pathParams;
        
        public function __construct() {
            $this->parseRequest();
        }
        
        private function parseRequest() {
            // 解析查询参数
            $this->queryParams = $_GET;
            
            // 解析请求体
            $contentType = $_SERVER['CONTENT_TYPE'] ?? '';
            if (strpos($contentType, 'application/json') !== false) {
                $this->data = json_decode(file_get_contents('php://input'), true) ?: [];
            } else {
                $this->data = $_POST;
            }
        }
        
        public function getData() {
            return $this->data;
        }
        
        public function getQueryParam($key, $default = null) {
            return $this->queryParams[$key] ?? $default;
        }
        
        public function getPathParam($key, $default = null) {
            return $this->pathParams[$key] ?? $default;
        }
        
        public function setPathParams($params) {
            $this->pathParams = $params;
        }
    }
    
    // API验证器
    class ApiValidator {
        private $data;
        private $rules;
        private $errors = [];
        private $validated = [];
        
        public function __construct($data, $rules) {
            $this->data = $data;
            $this->rules = $rules;
        }
        
        public function validate() {
            foreach ($this->rules as $field => $fieldRules) {
                $value = $this->data[$field] ?? null;
                
                if (!$this->validateField($field, $value, $fieldRules)) {
                    return false;
                }
            }
            
            return empty($this->errors);
        }
        
        private function validateField($field, $value, $rules) {
            $rulesList = explode('|', $rules);
            
            foreach ($rulesList as $rule) {
                if (!$this->applyRule($field, $value, $rule)) {
                    return false;
                }
            }
            
            $this->validated[$field] = $value;
            return true;
        }
        
        private function applyRule($field, $value, $rule) {
            if ($rule === 'required' && (is_null($value) || $value === '')) {
                $this->errors[$field][] = "$field is required";
                return false;
            }
            
            if (is_null($value) && $rule !== 'required') {
                return true; // 非必填字段为空时跳过其他验证
            }
            
            if (strpos($rule, 'max:') === 0) {
                $max = substr($rule, 4);
                if (strlen($value) > (int)$max) {
                    $this->errors[$field][] = "$field must not be more than $max characters";
                    return false;
                }
            }
            
            if (strpos($rule, 'min:') === 0) {
                $min = substr($rule, 4);
                if (strlen($value) < (int)$min) {
                    $this->errors[$field][] = "$field must be at least $min characters";
                    return false;
                }
            }
            
            if ($rule === 'email' && !filter_var($value, FILTER_VALIDATE_EMAIL)) {
                $this->errors[$field][] = "$field must be a valid email";
                return false;
            }
            
            return true;
        }
        
        public function getErrors() {
            return $this->errors;
        }
        
        public function getValidatedData() {
            return $this->validated;
        }
    }
    
    // 使用示例
    class UserController extends ApiController {
        public function index() {
            $users = [
                ['id' => 1, 'name' => '张三', 'email' => 'zhangsan@email.com'],
                ['id' => 2, 'name' => '李四', 'email' => 'lisi@email.com']
            ];
            
            ApiResponse::success($users)->send();
        }
        
        public function show() {
            $id = $this->getPathParam('id');
            
            // 模拟数据库查询
            $user = ['id' => $id, 'name' => '用户' . $id, 'email' => "user{$id}@email.com"];
            
            ApiResponse::success($user)->send();
        }
        
        public function store() {
            $data = $this->validate([
                'name' => 'required|max:50',
                'email' => 'required|email|max:100'
            ]);
            
            // 保存用户...
            
            ApiResponse::created($data, 'User created successfully')->send();
        }
        
        public function update() {
            $id = $this->getPathParam('id');
            $data = $this->validate([
                'name' => 'sometimes|required|max:50',
                'email' => 'sometimes|required|email|max:100'
            ]);
            
            // 更新用户...
            
            ApiResponse::success($data, 'User updated successfully')->send();
        }
        
        public function destroy() {
            $id = $this->getPathParam('id');
            
            // 删除用户...
            
            ApiResponse::noContent('User deleted successfully')->send();
        }
    }
?>
```

## 最佳实践

1. **安全性**：始终验证和清理用户输入，防止XSS、SQL注入等攻击。
2. **RESTful设计**：遵循REST原则设计API接口。
3. **状态管理**：合理使用Session和Cookie管理用户状态。
4. **错误处理**：提供友好的错误信息和适当的HTTP状态码。
5. **性能优化**：使用缓存、压缩等技术提高性能。
6. **文档规范**：为API提供完整的文档说明。
7. **版本控制**：为API设计版本控制机制。