# Composer包管理

## Composer基础

### 安装Composer
```bash
# Windows - 下载安装器
# 访问 https://getcomposer.org/Composer-Setup.exe 下载安装

# macOS/Linux - 使用官方安装脚本
curl -sS https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer

# 或使用brew（macOS）
brew install composer

# 验证安装
composer --version
```

### 初始化项目
```bash
# 创建新的Composer项目
composer init

# 交互式创建composer.json
composer init --name="yourname/project" --description="Project description" --author="Your Name <email@example.com>"

# 创建空的composer.json
composer init --quiet --no-interaction

# 快速创建项目
composer init \
  --name="example/my-project" \
  --description="Example project" \
  --author="John Doe <john@example.com>" \
  --type="project" \
  --license="MIT" \
  --require="php:^7.4" \
  --require-dev="phpunit/phpunit:^9.0"
```

## composer.json配置

### 基本结构
```json
{
    "name": "example/my-project",
    "description": "Example project description",
    "version": "1.0.0",
    "type": "project",
    "keywords": ["example", "project"],
    "homepage": "https://github.com/example/project",
    "license": "MIT",
    "authors": [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "homepage": "https://johndoe.com",
            "role": "Developer"
        }
    ],
    "require": {
        "php": "^7.4|^8.0",
        "monolog/monolog": "^2.0",
        "guzzlehttp/guzzle": "^7.0",
        "doctrine/orm": "^2.10"
    },
    "require-dev": {
        "phpunit/phpunit": "^9.0",
        "symfony/var-dumper": "^5.0",
        "phpmd/phpmd": "^2.8"
    },
    "autoload": {
        "psr-4": {
            "App\\": "src/",
            "Example\\": "lib/"
        },
        "psr-0": {
            "Legacy_": "legacy/"
        },
        "classmap": [
            "database/seeds",
            "database/factories"
        ],
        "files": [
            "src/helpers.php"
        ]
    },
    "autoload-dev": {
        "psr-4": {
            "Tests\\": "tests/"
        }
    },
    "scripts": {
        "post-install-cmd": [
            "@php -r \"file_exists('.env') || copy('.env.example', '.env');\"",
            "php artisan key:generate"
        ],
        "post-create-project-cmd": [
            "@php artisan key:generate"
        ],
        "post-autoload-dump": [
            "Illuminate\\Foundation\\ComposerScripts::postAutoloadDump",
            "@php artisan package:discover --ansi"
        ],
        "test": "phpunit",
        "lint": "phpcs --standard=PSR12 src/",
        "fix": "phpcbf --standard=PSR12 src/"
    },
    "config": {
        "sort-packages": true,
        "optimize-autoloader": true,
        "preferred-install": "dist",
        "process-timeout": 600
    },
    "repositories": [
        {
            "type": "composer",
            "url": "https://packages.example.com"
        },
        {
            "type": "vcs",
            "url": "https://github.com/example/private-package"
        }
    ],
    "minimum-stability": "stable",
    "prefer-stable": true
}
```

## 依赖管理

### 安装包
```bash
# 安装最新版本
composer require monolog/monolog

# 安装指定版本
composer require monolog/monolog:2.3.5

# 版本约束
composer require monolog/monolog:^2.0    # >=2.0.0 <3.0.0
composer require monolog/monolog:~2.3    # >=2.3.0 <2.4.0
composer require monolog/monolog:>=2.0   # >=2.0.0
composer require monolog/monolog:2.*      # >=2.0.0 <3.0.0

# 开发依赖
composer require --dev phpunit/phpunit

# 更新composer.json但不安装
composer require monolog/monolog --dry-run

# 仅更新composer.json和lock文件
composer require monolog/monolog --no-update
```

### 移除包
```bash
# 移除包及其依赖
composer remove monolog/monolog

# 移除开发依赖
composer remove --dev phpunit/phpunit

# 仅更新composer.json
composer remove monolog/monolog --no-update

# 更新并优化自动加载
composer remove monolog/monolog && composer dump-autoload
```

### 更新包
```bash
# 更新所有包
composer update

# 更新指定包
composer update monolog/monolog

# 更新多个包
composer update monolog/monolog guzzlehttp/guzzle

# 仅更新lock文件中的包版本
composer update --lock

# 不更新开发依赖
composer update --no-dev

# 检查过时的包
composer outdated

# 交互式更新
composer update --interactive
```

## 自动加载

### PSR-4自动加载
```json
{
    "autoload": {
        "psr-4": {
            "App\\": "src/",
            "Example\\Project\\": "lib/Project/",
            "Tests\\": "tests/",
            "Database\\Seeders\\": "database/seeders/"
        }
    }
}
```

```php
<?php
// src/User.php
namespace App;

class User {
    public function __construct() {
        echo "User class loaded!";
    }
}

// 使用自动加载的类
<?php
// index.php
require_once 'vendor/autoload.php';

use App\User;
use Database\Seeders\DatabaseSeeder;

$user = new User();
$seeder = new DatabaseSeeder();
```

### PSR-0自动加载
```json
{
    "autoload": {
        "psr-0": {
            "Legacy_": "legacy/",
            "Zend_": "library/"
        }
    }
}
```

### 类映射自动加载
```json
{
    "autoload": {
        "classmap": [
            "database/seeds",
            "database/factories",
            "app/Console/Commands"
        ]
    }
}
```

### 文件自动加载
```json
{
    "autoload": {
        "files": [
            "src/helpers.php",
            "src/constants.php",
            "vendor/laravel/framework/src/Illuminate/Support/helpers.php"
        ]
    }
}
```

```php
<?php
// src/helpers.php
if (!function_exists('helper_function')) {
    function helper_function($param) {
        return "Helper called with: " . $param;
    }
}

// 使用
<?php
require_once 'vendor/autoload.php';
echo helper_function('test');
```

### 生成自动加载文件
```bash
# 生成自动加载文件
composer dump-autoload

# 优化自动加载（生产环境）
composer dump-autoload --optimize

# 生成类映射（更快的加载）
composer dump-autoload --classmap-authoritative

# 不扫描文件系统
composer dump-autoload --no-dev
```

## 项目管理

### 创建项目
```bash
# 从packagist创建项目
composer create-project laravel/laravel my-laravel-app

# 创建特定版本
composer create-project laravel/laravel my-laravel-app "8.*"

# 从VCS仓库创建
composer create-project --repository-url=https://github.com/example/project my-project

# 无交互创建
composer create-project laravel/laravel my-app --no-interaction

# 安装到指定目录
composer create-project laravel/laravel .  # 当前目录
```

### 安装依赖
```bash
# 安装所有依赖
composer install

# 仅安装生产依赖
composer install --no-dev

# 优化自动加载器
composer install --optimize-autoloader

# 跳过脚本执行
composer install --no-scripts

# 首选dist包（更快）
composer install --prefer-dist

# 首选源码包（适合开发）
composer install --prefer-source
```

### 查看信息
```bash
# 显示包信息
composer show monolog/monolog

# 显示所有已安装的包
composer show --installed

# 显示树形结构
composer show --tree

# 显示为什么安装某个包
composer depends monolog/monolog
composer prohibits monolog/monolog:2.3.0

# 搜索包
composer search monolog

# 显示包主页
composer home monolog/monolog

# 显示许可证
composer licenses
```

## 版本控制

### 版本约束
```json
{
    "require": {
        "monolog/monolog": "1.0",        // 精确版本
        "guzzlehttp/guzzle": ">=2.0",    // 大于等于2.0
        "doctrine/orm": "<2.5",           // 小于2.5
        "symfony/console": ">=2.0,<3.0", // 范围
        "phpunit/phpunit": "^2.5",       // >=2.5.0 <3.0.0 (兼容语义化版本)
        "zendframework/zendframework": "~2.3", // >=2.3.0 <2.4.0
        "swiftmailer/swiftmailer": "2.*"  // >=2.0.0 <3.0.0
    }
}
```

### 稳定性标志
```json
{
    "require": {
        "monolog/monolog": "~1.0@stable",    // 稳定版
        "some/package": "@dev",                // 开发版
        "another/package": "@alpha",          // Alpha版
        "beta/package": "@beta",              // Beta版
        "rc/package": "@RC"                   // RC版
    },
    "minimum-stability": "stable",           // 最低稳定性
    "prefer-stable": true                     // 优先使用稳定版
}
```

## 私有仓库

### 配置私有仓库
```json
{
    "repositories": [
        {
            "type": "composer",
            "url": "https://packages.example.com"
        },
        {
            "type": "vcs",
            "url": "https://github.com/example/private-package"
        },
        {
            "type": "git",
            "url": "https://git.example.com/package.git"
        },
        {
            "type": "svn",
            "url": "https://svn.example.com/package/trunk"
        },
        {
            "type": "pear",
            "url": "https://pear.example.com"
        },
        {
            "type": "artifact",
            "url": "path/to/zips/"
        }
    ],
    "require": {
        "example/private-package": "dev-master"
    }
}
```

### Packagist认证
```bash
# 设置认证令牌
composer config http-basic.packagist.com username token

# 或在auth.json中配置
{
    "http-basic": {
        "packagist.org": {
            "username": "your-username",
            "password": "your-api-token"
        },
        "packages.example.com": {
            "username": "your-username",
            "password": "your-password"
        }
    }
}
```

## 全局命令

### 全局安装包
```bash
# 全局安装
composer global require friendsofphp/php-cs-fixer
composer global require laravel/installer

# 添加全局bin目录到PATH
export PATH="$HOME/.composer/vendor/bin:$PATH"

# Windows
set PATH=%APPDATA%\Composer\vendor\bin;%PATH%

# 显示全局安装的包
composer global show

# 更新全局包
composer global update

# 移除全局包
composer global remove friendsofphp/php-cs-fixer
```

### 常用全局包
```bash
# 代码格式化
composer global require friendsofphp/php-cs-fixer

# 静态分析
composer global require phpstan/phpstan
composer global require psalm/phar

# Laravel安装器
composer global require laravel/installer

# Symfony CLI
composer global require symfony/cli

# Composer预览
composer global require composer/composer-preview:dev-main
```

## 脚本和钩子

### 脚本定义
```json
{
    "scripts": {
        "pre-install-cmd": "echo '准备安装'",
        "post-install-cmd": [
            "echo '安装完成'",
            "@php artisan key:generate",
            "chmod -R 755 storage bootstrap/cache"
        ],
        "pre-update-cmd": "echo '准备更新'",
        "post-update-cmd": [
            "@php artisan package:discover --ansi",
            "@php artisan migrate"
        ],
        "post-autoload-dump": [
            "@php artisan package:discover --ansi"
        ],
        "test": "phpunit",
        "test-coverage": "phpunit --coverage-html coverage",
        "lint": "phpcs --standard=PSR12 src/ tests/",
        "lint-fix": "phpcbf --standard=PSR12 src/ tests/",
        "static-analysis": "phpstan analyse src/ --level=8",
        "check": [
            "@lint",
            "@test",
            "@static-analysis"
        ],
        "deploy": [
            "@php artisan config:cache",
            "@php artisan route:cache",
            "@php artisan view:cache"
        ]
    },
    "scripts-descriptions": {
        "test": "运行单元测试",
        "lint": "检查代码风格",
        "lint-fix": "修复代码风格问题",
        "static-analysis": "运行静态分析",
        "check": "运行所有检查",
        "deploy": "准备生产部署"
    }
}
```

### 运行脚本
```bash
# 运行自定义脚本
composer run-script test
composer run-script deploy

# 简写方式
composer test
composer lint-fix

# 传递参数
composer test -- --verbose
```

## 性能优化

### 优化技巧
```bash
# 优化自动加载（生产环境）
composer dump-autoload --optimize

# 生成类映射（最快）
composer dump-autoload --classmap-authoritative

# 下载压缩包而不是源码
composer install --prefer-dist

# 并行下载（需要插件）
composer global require hirak/prestissimo
composer install --prefer-dist

# 缓存
composer config cache-files-maxsize "500MiB"
composer config cache-files-ttl "86400"

# 清除缓存
composer clear-cache

# 显示诊断信息
composer diagnose

# 显示内存使用
composer install --profile
```

### 生产环境配置
```json
{
    "config": {
        "optimize-autoloader": true,
        "apcu-autoloader": true,
        "sort-packages": true,
        "process-timeout": 300,
        "cache-files-ttl": 86400,
        "cache-files-maxsize": "500MiB"
    },
    "scripts": {
        "post-install-cmd": [
            "@php artisan config:cache",
            "@php artisan route:cache",
            "@php artisan view:cache"
        ]
    }
}
```

## 最佳实践

### 项目结构建议
```
project/
├── src/                    # 主要源代码
│   ├── Controller/         # 控制器
│   ├── Model/             # 模型
│   ├── Service/           # 服务层
│   └── Utility/           # 工具类
├── tests/                  # 测试文件
├── config/                 # 配置文件
├── public/                 # 公共文件
├── templates/              # 模板文件
├── docs/                   # 文档
├── composer.json
├── composer.lock
└── README.md
```

### composer.json最佳实践
```json
{
    "name": "vendor/project-name",
    "description": "Clear, concise project description",
    "type": "project",
    "license": "MIT",
    "require": {
        "php": "^7.4|^8.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^9.0"
    },
    "autoload": {
        "psr-4": {
            "Vendor\\Project\\": "src/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Vendor\\Project\\Tests\\": "tests/"
        }
    },
    "config": {
        "sort-packages": true,
        "optimize-autoloader": true
    },
    "scripts": {
        "test": "phpunit",
        "check": [
            "@test"
        ]
    }
}
```

### 版本管理建议
```bash
# 1. 锁定主要依赖版本
composer require monolog/monolog:^2.3

# 2. 使用semantic versioning
composer require symfony/console:^5.2

# 3. 定期更新依赖
composer update --dry-run  # 查看更新内容
composer update monolog/monolog  # 更新特定包

# 4. 检查安全漏洞
composer audit

# 5. 定期清理缓存
composer clear-cache
```

### 团队协作
```bash
# 1. 提交composer.json和composer.lock
git add composer.json composer.lock
git commit -m "Add new dependency"

# 2. 新成员clone后安装
git clone https://github.com/example/project.git
cd project
composer install

# 3. 保持composer.lock同步
composer update
git add composer.lock
git commit -m "Update dependencies"

# 4. 环境一致性
composer install --no-dev  # 生产环境
composer install           # 开发环境
```

### 安全建议
```bash
# 1. 检查已知安全漏洞
composer audit

# 2. 定期更新依赖
composer update --dry-run
composer update

# 3. 使用最新稳定版
composer require --prefer-stable

# 4. 不要直接修改vendor目录
# 始终通过composer安装和更新包

# 5. 限制composer执行权限
chmod +x composer.phar
```

## 故障排除

### 常见问题解决
```bash
# 内存限制问题
php -d memory_limit=512M composer install

# SSL证书问题
composer config secure-http false

# 代理设置
composer config http-proxy http://proxy:port
composer config https-proxy https://proxy:port

# 镜像源（中国）
composer config repo.packagist composer https://mirrors.aliyun.com/composer/

# 恢复官方源
composer config repo.packagist composer https://packagist.org

# 清除所有配置
composer config --clear

# 详细调试信息
composer install --verbose --profile
```