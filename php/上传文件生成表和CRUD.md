以下是一个完整的PHP实现方案，包含**JSON/CSV文件上传自动建表**、**增删改查**、**批量导入导出**功能。代码结构清晰，注释详细，可直接部署测试。

### 环境要求
- PHP 7.4+（推荐8.0+）
- MySQL 5.7+
- Apache/Nginx（开启重写可选，非必须）
- 配置php.ini：`upload_max_filesize = 20M`、`post_max_size = 20M`、`max_execution_time = 300`

### 整体文件结构
```
├── config.php       // 配置文件（数据库、上传路径）
├── db.php           // 数据库连接类
├── index.php        // 前端主页面（所有功能入口）
├── upload.php       // 文件上传&自动建表处理
├── crud.php         // 增删改查处理
├── import_export.php// 批量导入导出处理
├── uploads/         // 文件上传目录（需777权限）
└── export/          // 导出文件目录（需777权限）
```

### 1. 配置文件 `config.php`
```php
<?php
// 数据库配置
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', 'root'); // 你的MySQL密码
define('DB_NAME', 'file_to_db'); // 需先创建该数据库

// 上传配置
define('UPLOAD_DIR', __DIR__ . '/uploads/');
define('EXPORT_DIR', __DIR__ . '/export/');
define('ALLOWED_TYPES', ['json', 'csv']);
define('MAX_FILE_SIZE', 20 * 1024 * 1024); // 20MB

// 创建目录（如果不存在）
if (!is_dir(UPLOAD_DIR)) mkdir(UPLOAD_DIR, 0777, true);
if (!is_dir(EXPORT_DIR)) mkdir(EXPORT_DIR, 0777, true);

// 字符编码
header('Content-Type: text/html; charset=utf-8');
```

### 2. 数据库连接类 `db.php`
```php
<?php
require_once 'config.php';

class DB {
    private static $pdo = null;

    // 获取PDO连接
    public static function getInstance() {
        if (self::$pdo === null) {
            try {
                $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4";
                self::$pdo = new PDO($dsn, DB_USER, DB_PASS);
                self::$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                self::$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
            } catch (PDOException $e) {
                die("数据库连接失败：" . $e->getMessage());
            }
        }
        return self::$pdo;
    }

    // 执行SQL（返回受影响行数）
    public static function exec($sql, $params = []) {
        $stmt = self::getInstance()->prepare($sql);
        $stmt->execute($params);
        return $stmt->rowCount();
    }

    // 查询单条数据
    public static function getOne($sql, $params = []) {
        $stmt = self::getInstance()->prepare($sql);
        $stmt->execute($params);
        return $stmt->fetch();
    }

    // 查询多条数据
    public static function getAll($sql, $params = []) {
        $stmt = self::getInstance()->prepare($sql);
        $stmt->execute($params);
        return $stmt->fetchAll();
    }

    // 获取最后插入的ID
    public static function lastInsertId() {
        return self::getInstance()->lastInsertId();
    }

    // 获取数据库中所有表名
    public static function getTables() {
        $sql = "SHOW TABLES";
        $tables = self::getAll($sql);
        $result = [];
        foreach ($tables as $table) {
            $result[] = reset($table);
        }
        return $result;
    }

    // 获取表的字段信息
    public static function getTableFields($tableName) {
        $sql = "DESCRIBE " . self::escapeTableName($tableName);
        return self::getAll($sql);
    }

    // 转义表名/字段名（防止SQL注入）
    public static function escapeTableName($name) {
        return "`" . str_replace("`", "``", $name) . "`";
    }
}
```

### 3. 前端主页面 `index.php`
```php
<?php
require_once 'db.php';

// 获取所有表
$tables = DB::getTables();
// 当前选中的表
$currentTable = isset($_GET['table']) ? $_GET['table'] : ($tables ? $tables[0] : '');
// 获取表字段
$fields = $currentTable ? DB::getTableFields($currentTable) : [];
// 获取表数据
$tableData = [];
if ($currentTable) {
    $sql = "SELECT * FROM " . DB::escapeTableName($currentTable) . " LIMIT 100"; // 限制显示100条
    $tableData = DB::getAll($sql);
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>文件上传自动建表 & CRUD</title>
    <style>
        * {margin:0; padding:0; box-sizing:border-box;}
        body {padding:20px; font-family:Arial, sans-serif;}
        .container {max-width:1200px; margin:0 auto;}
        .tab {margin:20px 0; padding:10px; background:#f5f5f5; border-radius:5px;}
        .btn {padding:8px 16px; background:#007bff; color:#fff; border:none; border-radius:4px; cursor:pointer;}
        .btn-danger {background:#dc3545;}
        .btn-success {background:#28a745;}
        .btn-secondary {background:#6c757d;}
        input, select, textarea {padding:8px; margin:5px 0; border:1px solid #ddd; border-radius:4px;}
        table {width:100%; border-collapse:collapse; margin:10px 0;}
        th, td {padding:8px; border:1px solid #ddd; text-align:left;}
        th {background:#f0f0f0;}
        .alert {padding:10px; margin:10px 0; border-radius:4px;}
        .alert-success {background:#d4edda; color:#155724;}
        .alert-danger {background:#f8d7da; color:#721c24;}
        .hidden {display:none;}
    </style>
</head>
<body>
<div class="container">
    <h1>文件上传自动建表 & 数据管理</h1>

    <!-- 1. 文件上传 & 自动建表区域 -->
    <div class="tab">
        <h3>第一步：上传JSON/CSV文件自动生成数据表</h3>
        <?php if (isset($_GET['msg'])): ?>
            <div class="alert <?= strpos($_GET['msg'], '成功') ? 'alert-success' : 'alert-danger' ?>">
                <?= $_GET['msg'] ?>
            </div>
        <?php endif; ?>
        <form action="upload.php" method="post" enctype="multipart/form-data">
            <div>
                <label>数据表名：</label>
                <input type="text" name="table_name" required placeholder="例如：user_data（仅字母、数字、下划线）" pattern="^[a-zA-Z0-9_]+$">
            </div>
            <div>
                <label>选择文件：</label>
                <input type="file" name="file" accept=".json,.csv" required>
                <small>仅支持JSON/CSV格式，最大20MB</small>
            </div>
            <button type="submit" class="btn">上传并生成数据表</button>
        </form>
    </div>

    <!-- 2. 数据表选择 & 数据管理区域 -->
    <?php if ($tables): ?>
    <div class="tab">
        <h3>第二步：数据管理（增删改查）</h3>
        <div>
            <label>选择数据表：</label>
            <select onchange="location.href='?table='+this.value">
                <?php foreach ($tables as $table): ?>
                    <option <?= $table == $currentTable ? 'selected' : '' ?> value="<?= $table ?>">
                        <?= $table ?>
                    </option>
                <?php endforeach; ?>
            </select>

            <!-- 批量导入导出按钮 -->
            <button class="btn btn-success" onclick="document.getElementById('import-form').classList.toggle('hidden')">
                批量导入数据
            </button>
            <a href="import_export.php?action=export&table=<?= $currentTable ?>" class="btn btn-secondary">
                导出当前表数据
            </a>
        </div>

        <!-- 批量导入表单 -->
        <form id="import-form" class="hidden" action="import_export.php" method="post" enctype="multipart/form-data">
            <input type="hidden" name="table_name" value="<?= $currentTable ?>">
            <div>
                <label>导入文件（JSON/CSV）：</label>
                <input type="file" name="file" accept=".json,.csv" required>
                <button type="submit" class="btn btn-success">确认导入</button>
            </div>
        </form>

        <!-- 新增数据表单 -->
        <div style="margin:10px 0;">
            <h4>新增数据</h4>
            <form action="crud.php" method="post">
                <input type="hidden" name="action" value="add">
                <input type="hidden" name="table_name" value="<?= $currentTable ?>">
                <?php foreach ($fields as $field): ?>
                    <?php if ($field['Field'] == 'id' && $field['Extra'] == 'auto_increment') continue; ?>
                    <div>
                        <label><?= $field['Field'] ?>：</label>
                        <input type="text" name="data[<?= $field['Field'] ?>]" required>
                    </div>
                <?php endforeach; ?>
                <button type="submit" class="btn">新增</button>
            </form>
        </div>

        <!-- 数据列表 -->
        <h4>数据列表（最多显示100条）</h4>
        <?php if ($tableData): ?>
            <table>
                <thead>
                    <tr>
                        <?php foreach ($fields as $field): ?>
                            <th><?= $field['Field'] ?></th>
                        <?php endforeach; ?>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($tableData as $row): ?>
                        <tr>
                            <?php foreach ($fields as $field): ?>
                                <td><?= htmlspecialchars($row[$field['Field']] ?? '') ?></td>
                            <?php endforeach; ?>
                            <td>
                                <button class="btn btn-secondary" onclick="editRow(<?= json_encode($row) ?>, '<?= $currentTable ?>')">编辑</button>
                                <a href="crud.php?action=delete&table=<?= $currentTable ?>&id=<?= $row['id'] ?>" class="btn btn-danger" onclick="return confirm('确定删除？')">删除</a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p>当前表暂无数据</p>
        <?php endif; ?>
    </div>

    <!-- 编辑数据弹窗（隐藏） -->
    <div id="edit-modal" class="hidden" style="position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:#fff; padding:20px; border:1px solid #ddd; z-index:999;">
        <h4>编辑数据</h4>
        <form id="edit-form" action="crud.php" method="post">
            <input type="hidden" name="action" value="edit">
            <input type="hidden" name="table_name" id="edit-table">
            <input type="hidden" name="id" id="edit-id">
            <div id="edit-fields"></div>
            <button type="submit" class="btn">保存修改</button>
            <button type="button" class="btn btn-secondary" onclick="document.getElementById('edit-modal').classList.add('hidden')">取消</button>
        </form>
    </div>
    <?php else: ?>
        <div class="alert alert-secondary">暂无数据表，请先上传文件生成</div>
    <?php endif; ?>
</div>

<script>
// 编辑行数据
function editRow(row, tableName) {
    const modal = document.getElementById('edit-modal');
    const tableInput = document.getElementById('edit-table');
    const idInput = document.getElementById('edit-id');
    const fieldsDiv = document.getElementById('edit-fields');
    
    tableInput.value = tableName;
    idInput.value = row.id;
    fieldsDiv.innerHTML = '';

    // 生成编辑字段
    for (const [key, value] of Object.entries(row)) {
        if (key === 'id') continue; // ID不允许编辑
        fieldsDiv.innerHTML += `
            <div>
                <label>${key}：</label>
                <input type="text" name="data[${key}]" value="${htmlEscape(value)}" required>
            </div>
        `;
    }

    modal.classList.remove('hidden');
}

// HTML转义
function htmlEscape(str) {
    return str.toString().replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
</script>
</body>
</html>
```

### 4. 文件上传&自动建表 `upload.php`
```php
<?php
require_once 'db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: index.php?msg=非法请求');
    exit;
}

// 验证表名
$tableName = trim($_POST['table_name']);
if (!preg_match('/^[a-zA-Z0-9_]+$/', $tableName)) {
    header('Location: index.php?msg=表名仅允许字母、数字、下划线');
    exit;
}

// 验证文件
if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
    header('Location: index.php?msg=文件上传失败');
    exit;
}

$file = $_FILES['file'];
$fileExt = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));

// 验证文件类型和大小
if (!in_array($fileExt, ALLOWED_TYPES) || $file['size'] > MAX_FILE_SIZE) {
    header('Location: index.php?msg=文件类型或大小不符合要求');
    exit;
}

// 移动文件到上传目录
$fileName = uniqid() . '.' . $fileExt;
$filePath = UPLOAD_DIR . $fileName;
if (!move_uploaded_file($file['tmp_name'], $filePath)) {
    header('Location: index.php?msg=文件保存失败');
    exit;
}

try {
    // 解析文件内容
    if ($fileExt === 'json') {
        $content = file_get_contents($filePath);
        $data = json_decode($content, true);
        if (json_last_error() !== JSON_ERROR_NONE || !is_array($data) || empty($data)) {
            throw new Exception('JSON文件解析失败或内容为空');
        }
        // 取第一条数据作为字段模板
        $firstRow = reset($data);
    } elseif ($fileExt === 'csv') {
        $handle = fopen($filePath, 'r');
        if (!$handle) throw new Exception('CSV文件打开失败');
        
        // 读取表头
        $header = fgetcsv($handle);
        if (!$header || empty($header)) throw new Exception('CSV无表头');
        
        // 读取第一条数据
        $firstRow = fgetcsv($handle);
        fclose($handle);
        
        if (!$firstRow || count($firstRow) !== count($header)) {
            throw new Exception('CSV数据格式错误');
        }
        
        // 组合成关联数组
        $firstRow = array_combine($header, $firstRow);
        $data = [$firstRow]; // 仅用于建表，导入数据在import_export.php处理
    }

    // 分析字段类型，生成建表SQL
    $fieldsSql = [];
    $fieldsSql[] = '`id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY'; // 主键ID

    foreach ($firstRow as $field => $value) {
        $field = trim($field);
        if (empty($field)) continue;
        $field = DB::escapeTableName($field);

        // 推断字段类型
        if (is_numeric($value)) {
            if (is_int($value + 0)) {
                $type = 'INT'; // 整数
            } else {
                $type = 'FLOAT'; // 浮点数
            }
        } elseif (strtotime($value) !== false) {
            $type = 'DATETIME'; // 日期时间
        } else {
            $type = 'VARCHAR(255)'; // 字符串（默认长度255）
        }

        $fieldsSql[] = "{$field} {$type} NOT NULL DEFAULT ''";
    }

    $createSql = "CREATE TABLE IF NOT EXISTS " . DB::escapeTableName($tableName) . " (" . implode(', ', $fieldsSql) . ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";
    DB::exec($createSql);

    // 导入第一条数据（验证表结构）
    $columns = array_keys($firstRow);
    $placeholders = rtrim(str_repeat('?,', count($columns)), ',');
    $insertSql = "INSERT INTO " . DB::escapeTableName($tableName) . " (" . implode(',', array_map([DB::class, 'escapeTableName'], $columns)) . ") VALUES ({$placeholders})";
    DB::exec($insertSql, array_values($firstRow));

    // 删除临时文件
    unlink($filePath);

    header('Location: index.php?msg=数据表创建成功&table=' . $tableName);
} catch (Exception $e) {
    // 清理临时文件
    if (file_exists($filePath)) unlink($filePath);
    header('Location: index.php?msg=建表失败：' . $e->getMessage());
}
```

### 5. 增删改查处理 `crud.php`
```php
<?php
require_once 'db.php';

$action = isset($_REQUEST['action']) ? $_REQUEST['action'] : '';
$tableName = isset($_REQUEST['table_name']) ? trim($_REQUEST['table_name']) : '';

// 验证表名
if (!preg_match('/^[a-zA-Z0-9_]+$/', $tableName)) {
    header('Location: index.php?msg=表名非法');
    exit;
}

try {
    switch ($action) {
        // 新增数据
        case 'add':
            $data = $_POST['data'] ?? [];
            if (empty($data)) throw new Exception('无新增数据');
            
            $columns = array_keys($data);
            $placeholders = rtrim(str_repeat('?,', count($columns)), ',');
            $sql = "INSERT INTO " . DB::escapeTableName($tableName) . " (" . implode(',', array_map([DB::class, 'escapeTableName'], $columns)) . ") VALUES ({$placeholders})";
            DB::exec($sql, array_values($data));
            header('Location: index.php?msg=数据新增成功&table=' . $tableName);
            break;

        // 编辑数据
        case 'edit':
            $id = intval($_POST['id']);
            $data = $_POST['data'] ?? [];
            if (empty($data) || $id <= 0) throw new Exception('参数错误');
            
            $setClause = [];
            $params = [];
            foreach ($data as $key => $value) {
                $setClause[] = DB::escapeTableName($key) . ' = ?';
                $params[] = $value;
            }
            $params[] = $id;
            
            $sql = "UPDATE " . DB::escapeTableName($tableName) . " SET " . implode(',', $setClause) . " WHERE id = ?";
            DB::exec($sql, $params);
            header('Location: index.php?msg=数据修改成功&table=' . $tableName);
            break;

        // 删除数据
        case 'delete':
            $id = intval($_GET['id']);
            if ($id <= 0) throw new Exception('ID错误');
            
            $sql = "DELETE FROM " . DB::escapeTableName($tableName) . " WHERE id = ?";
            DB::exec($sql, [$id]);
            header('Location: index.php?msg=数据删除成功&table=' . $tableName);
            break;

        default:
            throw new Exception('非法操作');
    }
} catch (Exception $e) {
    header('Location: index.php?msg=' . urlencode($e->getMessage()) . '&table=' . $tableName);
}
```

### 6. 批量导入导出 `import_export.php`
```php
<?php
require_once 'db.php';

$action = isset($_GET['action']) ? $_GET['action'] : (isset($_POST['action']) ? $_POST['action'] : '');
$tableName = isset($_REQUEST['table_name']) ? trim($_REQUEST['table_name']) : '';

// 验证表名
if (!preg_match('/^[a-zA-Z0-9_]+$/', $tableName)) {
    header('Location: index.php?msg=表名非法');
    exit;
}

try {
    // 批量导入
    if ($action === '' && $_SERVER['REQUEST_METHOD'] === 'POST') {
        // 验证文件
        if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
            throw new Exception('文件上传失败');
        }

        $file = $_FILES['file'];
        $fileExt = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (!in_array($fileExt, ALLOWED_TYPES) || $file['size'] > MAX_FILE_SIZE) {
            throw new Exception('文件类型或大小不符合要求');
        }

        // 保存文件
        $fileName = uniqid() . '.' . $fileExt;
        $filePath = UPLOAD_DIR . $fileName;
        if (!move_uploaded_file($file['tmp_name'], $filePath)) {
            throw new Exception('文件保存失败');
        }

        // 解析文件并导入
        if ($fileExt === 'json') {
            $content = file_get_contents($filePath);
            $data = json_decode($content, true);
            if (json_last_error() !== JSON_ERROR_NONE || !is_array($data) || empty($data)) {
                throw new Exception('JSON解析失败或内容为空');
            }
        } elseif ($fileExt === 'csv') {
            $handle = fopen($filePath, 'r');
            if (!$handle) throw new Exception('CSV打开失败');
            $header = fgetcsv($handle); // 表头
            $data = [];
            while ($row = fgetcsv($handle)) {
                if (count($row) !== count($header)) continue; // 跳过格式错误的行
                $data[] = array_combine($header, $row);
            }
            fclose($handle);
            if (empty($data)) throw new Exception('CSV无数据');
        }

        // 批量插入
        $firstRow = reset($data);
        $columns = array_keys($firstRow);
        $placeholders = rtrim(str_repeat('?,', count($columns)), ',');
        $sql = "INSERT INTO " . DB::escapeTableName($tableName) . " (" . implode(',', array_map([DB::class, 'escapeTableName'], $columns)) . ") VALUES ({$placeholders})";

        $pdo = DB::getInstance();
        $pdo->beginTransaction(); // 事务
        $stmt = $pdo->prepare($sql);
        $count = 0;

        foreach ($data as $row) {
            $stmt->execute(array_values($row));
            $count++;
        }

        $pdo->commit();
        unlink($filePath); // 删除临时文件

        header('Location: index.php?msg=成功导入' . $count . '条数据&table=' . $tableName);

    // 导出数据
    } elseif ($action === 'export') {
        $exportType = isset($_GET['type']) ? $_GET['type'] : 'csv'; // 默认CSV
        if (!in_array($exportType, ALLOWED_TYPES)) $exportType = 'csv';

        // 获取表数据和字段
        $fields = DB::getTableFields($tableName);
        $fieldNames = array_column($fields, 'Field');
        $data = DB::getAll("SELECT * FROM " . DB::escapeTableName($tableName));

        if (empty($data)) throw new Exception('表中无数据');

        // 生成文件名
        $fileName = $tableName . '_' . date('YmdHis') . '.' . $exportType;
        $filePath = EXPORT_DIR . $fileName;

        // 生成导出文件
        if ($exportType === 'csv') {
            $handle = fopen($filePath, 'w');
            fputcsv($handle, $fieldNames); // 写入表头
            foreach ($data as $row) {
                fputcsv($handle, $row);
            }
            fclose($handle);
        } elseif ($exportType === 'json') {
            file_put_contents($filePath, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
        }

        // 下载文件
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . $fileName . '"');
        header('Content-Length: ' . filesize($filePath));
        readfile($filePath);
        unlink($filePath); // 下载后删除临时文件
        exit;

    } else {
        throw new Exception('非法操作');
    }
} catch (Exception $e) {
    header('Location: index.php?msg=' . urlencode($e->getMessage()) . '&table=' . $tableName);
}
```

### 使用说明
1. **创建数据库**：先在MySQL中创建名为 `file_to_db` 的数据库（或修改`config.php`中的`DB_NAME`）。
2. **权限设置**：给`uploads/`和`export/`目录赋予777权限（Linux/Mac：`chmod -R 777 uploads export`）。
3. **部署运行**：将所有文件放到Web服务器根目录（如XAMPP的htdocs），访问`http://localhost/文件名/index.php`。
4. **测试流程**：
   - 准备JSON/CSV文件（示例如下），上传并输入表名，生成数据表。
   - 在数据管理区域进行增删改查、批量导入导出。

### 示例文件
#### JSON示例（user.json）
```json
[
    {"name": "张三", "age": 25, "email": "zhangsan@test.com", "create_time": "2025-01-01 12:00:00"},
    {"name": "李四", "age": 30, "email": "lisi@test.com", "create_time": "2025-01-02 12:00:00"}
]
```

#### CSV示例（user.csv）
```csv
name,age,email,create_time
张三,25,zhangsan@test.com,2025-01-01 12:00:00
李四,30,lisi@test.com,2025-01-02 12:00:00
```

### 安全优化建议（生产环境）
1. 增加用户登录验证，限制访问权限。
2. 对上传文件进行更严格的校验（如内容格式、恶意代码）。
3. 表名/字段名增加前缀，避免冲突。
4. 批量导入时限制单次导入行数（如1000行），防止内存溢出。
5. 关闭PHP错误显示（`display_errors = Off`），错误日志写入文件。
6. 使用HTTPS协议传输数据。
7. 定期清理`uploads/`和`export/`目录的临时文件。