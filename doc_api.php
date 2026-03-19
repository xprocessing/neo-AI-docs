<?php
/**
 * neo-AI-docs 文档接口
 * 所有文件均放在neo-AI-docs目录下
 */
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Origin: *"); // 开发环境，生产环境请限制域名

// 定义文档根目录（当前文件所在目录，即neo-AI-docs）
$DOC_ROOT = __DIR__ . '/';

// 确保目录存在（理论上必然存在，做个兜底）
if (!is_dir($DOC_ROOT)) {
    echo json_encode([
        'code' => 404,
        'msg' => '文档目录不存在: ' . $DOC_ROOT
    ]);
    exit;
}

// 获取请求动作
$action = $_GET['action'] ?? '';

switch ($action) {
    // 扫描文档目录结构（排除自身php/html文件）
    case 'scan':
        $files = scanDocFiles($DOC_ROOT);
        echo json_encode([
            'code' => 200,
            'data' => $files
        ]);
        break;

    // 读取Markdown文件内容
    case 'read':
        $filePath = $_GET['path'] ?? '';
        // 安全校验：防止路径遍历攻击
        $realPath = realpath($DOC_ROOT . '/' . $filePath);
        
        // 校验逻辑：必须在neo-AI-docs目录内，且不是接口/页面文件
        if (!$realPath || strpos($realPath, $DOC_ROOT) !== 0 || !file_exists($realPath)) {
            echo json_encode([
                'code' => 403,
                'msg' => '文件不存在或无访问权限'
            ]);
            exit;
        }
        
        // 排除php/html文件，只允许md文件
        $basename = basename($realPath);
        if (in_array($basename, ['doc_api.php', 'index.html']) || pathinfo($realPath, PATHINFO_EXTENSION) !== 'md') {
            echo json_encode([
                'code' => 400,
                'msg' => '仅支持读取Markdown文件(.md)'
            ]);
            exit;
        }
        
        // 读取文件内容
        $content = file_get_contents($realPath);
        echo json_encode([
            'code' => 200,
            'data' => [
                'content' => $content,
                'name' => pathinfo($realPath, PATHINFO_FILENAME)
            ]
        ]);
        break;

    default:
        echo json_encode([
            'code' => 400,
            'msg' => '无效的请求动作，支持：scan, read'
        ]);
        break;
}

/**
 * 递归扫描文档目录，返回Markdown文件列表（排除php/html文件）
 * @param string $dir 扫描目录
 * @param string $prefix 路径前缀（用于生成相对路径）
 * @return array 文件列表
 */
function scanDocFiles($dir, $prefix = '') {
    $files = [];
    $items = scandir($dir);
    
    foreach ($items as $item) {
        // 跳过隐藏文件、上级目录、接口文件和页面文件
        if ($item === '.' || $item === '..' || $item === 'doc_api.php' || $item === 'index.html') continue;
        
        $fullPath = $dir . '/' . $item;
        $relativePath = $prefix . $item;
        
        if (is_dir($fullPath)) {
            // 递归扫描子目录
            $subFiles = scanDocFiles($fullPath, $relativePath . '/');
            $files = array_merge($files, $subFiles);
        } elseif (pathinfo($fullPath, PATHINFO_EXTENSION) === 'md') {
            // 只收集Markdown文件
            $files[] = [
                'path' => $relativePath,
                'name' => pathinfo($fullPath, PATHINFO_FILENAME),
                'category' => $prefix ?: '根目录' // 用上级目录作为分类
            ];
        }
    }
    
    return $files;
}
?>