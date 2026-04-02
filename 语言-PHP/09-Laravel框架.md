# Laravel框架

## Laravel基础

### 安装和项目创建
```bash
# 安装Laravel（使用Composer）
composer create-project --prefer-dist laravel/laravel blog

# 安装特定版本
composer create-project --prefer-dist laravel/laravel blog "9.*"

# 创建新的Laravel项目
laravel new blog

# 进入项目目录
cd blog

# 启动开发服务器
php artisan serve
# 访问 http://localhost:8000
```

### 项目结构
```
blog/
├── app/
│   ├── Console/           # Artisan命令
│   ├── Exceptions/        # 异常处理
│   ├── Http/             # HTTP控制器和中间件
│   │   ├── Controllers/   # 控制器
│   │   ├── Middleware/    # 中间件
│   │   └── Requests/      # 表单请求
│   ├── Models/           # 模型
│   ├── Providers/        # 服务提供者
│   └── Traits/           # Trait
├── bootstrap/            # 启动文件
├── config/               # 配置文件
├── database/             # 数据库文件
│   ├── factories/        # 数据工厂
│   ├── migrations/        # 数据库迁移
│   └── seeders/          # 数据填充
├── public/               # 公共资源
│   ├── css/              # CSS文件
│   ├── js/               # JavaScript文件
│   └── index.php         # 入口文件
├── resources/            # 视图和资源
│   ├── lang/             # 语言文件
│   └── views/            # Blade模板
├── routes/               # 路由文件
│   ├── api.php           # API路由
│   ├── channels.php      # 广播频道
│   ├── console.php       # 命令行路由
│   └── web.php           # Web路由
├── storage/              # 存储文件
├── tests/                # 测试文件
├── vendor/               # Composer依赖
├── .env                  # 环境配置
├── .env.example          # 环境配置示例
├── artisan               # Artisan命令行工具
├── composer.json         # Composer配置
└── README.md             # 项目说明
```

## 路由系统

### 基础路由
```php
// routes/web.php

use Illuminate\Support\Facades\Route;

// 基础GET路由
Route::get('/', function () {
    return view('welcome');
});

// 返回字符串
Route::get('/hello', function () {
    return 'Hello, Laravel!';
});

// 返回JSON
Route::get('/api/user', function () {
    return response()->json([
        'name' => '张三',
        'email' => 'zhangsan@example.com'
    ]);
});

// 基础POST路由
Route::post('/submit', function (Illuminate\Http\Request $request) {
    $name = $request->input('name');
    return "提交的名字是：$name";
});

// 多方法路由
Route::match(['get', 'post'], '/form', function () {
    return '支持GET和POST方法';
});

// 任意方法路由
Route::any('/any-method', function () {
    return '支持所有HTTP方法';
});
```

### 路由参数
```php
// 必需参数
Route::get('/user/{id}', function ($id) {
    return "用户ID：$id";
});

// 多个参数
Route::get('/post/{post}/comment/{comment}', function ($postId, $commentId) {
    return "文章ID：$postId，评论ID：$commentId";
});

// 可选参数
Route::get('/user/{name?}', function ($name = 'Guest') {
    return "Hello, $name!";
});

// 参数约束（正则表达式）
Route::get('/user/{id}', function ($id) {
    return "用户ID：$id";
})->where('id', '[0-9]+');

Route::get('/product/{slug}', function ($slug) {
    return "产品Slug：$slug";
})->where('slug', '[a-z0-9-]+');

// 全局约束
Route::pattern('id', '[0-9]+');
Route::pattern('slug', '[a-z0-9-]+');

Route::get('/user/{id}', function ($id) {
    return "用户ID：$id";
});

Route::get('/article/{slug}', function ($slug) {
    return "文章Slug：$slug";
});
```

### 命名路由
```php
// 定义命名路由
Route::get('/user/profile', function () {
    return '用户个人资料';
})->name('profile');

Route::get('/user/{id}', function ($id) {
    return "用户ID：$id";
})->name('user.show');

// 生成URL
$url = route('profile');          // http://localhost/user/profile
$url = route('user.show', 1);     // http://localhost/user/1

// 生成重定向
return redirect()->route('profile');
return redirect()->route('user.show', ['id' => 1]);
```

### 路由群组
```php
// 中间件群组
Route::middleware(['auth', 'verified'])->group(function () {
    Route::get('/dashboard', function () {
        return '仪表板';
    });
    
    Route::get('/profile', function () {
        return '个人资料';
    });
});

// 前缀群组
Route::prefix('admin')->group(function () {
    Route::get('/dashboard', function () {
        return '管理员仪表板';
    });
    
    Route::get('/users', function () {
        return '用户管理';
    });
});

// 命名空间群组
Route::namespace('Admin')->group(function () {
    Route::get('/admin/users', 'UserController@index');
    Route::get('/admin/posts', 'PostController@index');
});

// 子域名路由
Route::domain('admin.example.com')->group(function () {
    Route::get('/user', function () {
        return '子域名路由';
    });
});

// 组合使用
Route::prefix('api/v1')
    ->middleware('api')
    ->namespace('Api\V1')
    ->group(function () {
        Route::get('/users', 'UserController@index');
        Route::post('/users', 'UserController@store');
    });
```

### 控制器路由
```php
// 基础控制器路由
Route::get('/users', 'UserController@index');
Route::get('/users/{id}', 'UserController@show');
Route::post('/users', 'UserController@store');
Route::put('/users/{id}', 'UserController@update');
Route::delete('/users/{id}', 'UserController@destroy');

// 资源路由（自动生成CRUD路由）
Route::resource('articles', 'ArticleController');

// 部分资源路由
Route::resource('photos', 'PhotoController')->only([
    'index', 'show'
]);

Route::resource('photos', 'PhotoController')->except([
    'create', 'store', 'update', 'destroy'
]);

// API资源路由（排除create和edit）
Route::apiResource('products', 'ProductController');
```

## 控制器

### 控制器创建
```bash
# 创建控制器
php artisan make:controller UserController

# 创建资源控制器
php artisan make:controller ArticleController --resource

# 创建API资源控制器
php artisan make:controller Api\ProductController --api
```

### 控制器实现
```php
<?php
// app/Http/Controllers/UserController.php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;

class UserController extends Controller
{
    // 显示用户列表
    public function index()
    {
        $users = User::paginate(10);
        return view('users.index', compact('users'));
    }
    
    // 显示创建用户表单
    public function create()
    {
        return view('users.create');
    }
    
    // 存储新用户
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users',
            'password' => 'required|string|min:8|confirmed',
        ]);
        
        User::create([
            'name' => $validated['name'],
            'email' => $validated['email'],
            'password' => bcrypt($validated['password']),
        ]);
        
        return redirect()->route('users.index')
            ->with('success', '用户创建成功！');
    }
    
    // 显示单个用户
    public function show($id)
    {
        $user = User::findOrFail($id);
        return view('users.show', compact('user'));
    }
    
    // 显示编辑用户表单
    public function edit($id)
    {
        $user = User::findOrFail($id);
        return view('users.edit', compact('user'));
    }
    
    // 更新用户
    public function update(Request $request, $id)
    {
        $user = User::findOrFail($id);
        
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users,email,' . $id,
        ]);
        
        $user->update($validated);
        
        return redirect()->route('users.show', $id)
            ->with('success', '用户更新成功！');
    }
    
    // 删除用户
    public function destroy($id)
    {
        $user = User::findOrFail($id);
        $user->delete();
        
        return redirect()->route('users.index')
            ->with('success', '用户删除成功！');
    }
}

// API控制器示例
<?php
// app/Http/Controllers/Api/UserController.php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User;

class UserController extends Controller
{
    // 返回JSON响应
    public function index()
    {
        $users = User::all();
        return response()->json([
            'status' => 'success',
            'data' => $users
        ]);
    }
    
    // 返回单个用户
    public function show($id)
    {
        $user = User::find($id);
        
        if (!$user) {
            return response()->json([
                'status' => 'error',
                'message' => '用户不存在'
            ], 404);
        }
        
        return response()->json([
            'status' => 'success',
            'data' => $user
        ]);
    }
    
    // 使用API资源
    public function showWithResource($id)
    {
        $user = User::findOrFail($id);
        return new UserResource($user);
    }
}
```

## 数据库和Eloquent ORM

### 数据库配置
```env
# .env文件
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=laravel
DB_USERNAME=root
DB_PASSWORD=password
```

### 数据库迁移
```bash
# 创建迁移
php artisan make:migration create_users_table

# 创建模型和迁移
php artisan make:model User -m

# 运行迁移
php artisan migrate

# 回滚迁移
php artisan migrate:rollback

# 重置迁移
php artisan migrate:reset

# 重新运行所有迁移
php artisan migrate:fresh
```

### 迁移文件示例
```php
<?php
// database/migrations/2023_01_01_000000_create_users_table.php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateUsersTable extends Migration
{
    public function up()
    {
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('email')->unique();
            $table->timestamp('email_verified_at')->nullable();
            $table->string('password');
            $table->rememberToken();
            $table->timestamps();
            
            // 索引
            $table->index('email');
        });
    }
    
    public function down()
    {
        Schema::dropIfExists('users');
    }
}
```

### 模型创建
```bash
# 创建模型
php artisan make:model User

# 创建模型和迁移
php artisan make:model User -m

# 创建模型、迁移和控制器
php artisan make:model User -mc

# 创建模型、迁移、控制器和资源控制器
php artisan make:model User -mcr
```

### 模型定义
```php
<?php
// app/Models/User.php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Model
{
    use HasFactory, Notifiable, HasApiTokens;
    
    // 可填充字段
    protected $fillable = [
        'name',
        'email',
        'password',
    ];
    
    // 隐藏字段
    protected $hidden = [
        'password',
        'remember_token',
    ];
    
    // 字段类型转换
    protected $casts = [
        'email_verified_at' => 'datetime',
        'is_active' => 'boolean',
        'metadata' => 'array',
    ];
    
    // 默认值
    protected $attributes = [
        'is_active' => true,
    ];
    
    // 访问器
    public function getFullNameAttribute()
    {
        return $this->first_name . ' ' . $this->last_name;
    }
    
    // 修改器
    public function setPasswordAttribute($value)
    {
        $this->attributes['password'] = bcrypt($value);
    }
    
    // 查询作用域
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }
    
    public function scopeRecent($query, $days = 7)
    {
        return $query->where('created_at', '>=', now()->subDays($days));
    }
    
    // 关联关系
    public function posts()
    {
        return $this->hasMany(Post::class);
    }
    
    public function profile()
    {
        return $this->hasOne(Profile::class);
    }
    
    public function roles()
    {
        return $this->belongsToMany(Role::class);
    }
}
```

### Eloquent查询
```php
<?php
// 基础查询
$users = User::all();
$user = User::find(1);
$users = User::where('active', true)->get();

// 分页查询
$users = User::paginate(10);
$users = User::simplePagulate(10);

// 链式查询
$activeUsers = User::where('active', true)
    ->orderBy('created_at', 'desc')
    ->take(10)
    ->get();

// 使用作用域
$recentActiveUsers = User::active()->recent(30)->get();

// 条件查询
$users = User::when($request->input('active'), function ($query, $active) {
    return $query->where('active', $active);
})->get();

// 创建记录
$user = User::create([
    'name' => '张三',
    'email' => 'zhangsan@example.com',
    'password' => bcrypt('password'),
]);

// 更新记录
$user->update(['name' => '李四']);

// 删除记录
$user->delete();
User::destroy(1);
User::destroy([1, 2, 3]);

// 软删除
class Post extends Model
{
    use SoftDeletes;
    
    protected $dates = ['deleted_at'];
}

// 软删除查询
$posts = Post::withTrashed()->get();
$posts = Post::onlyTrashed()->get();
$post->restore();
```

## Blade模板引擎

### Blade基础语法
```php
<!-- resources/views/layouts/app.blade.php -->

<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'Laravel应用')</title>
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
</head>
<body>
    <header>
        @include('partials.navigation')
    </header>
    
    <main>
        @yield('content')
    </main>
    
    <footer>
        <p>&copy; {{ date('Y') }} Laravel应用</p>
    </footer>
    
    @stack('scripts')
</body>
</html>
```

### 模板继承和包含
```php
<!-- resources/views/users/index.blade.php -->

@extends('layouts.app')

@section('title', '用户列表')

@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>用户列表</h1>
            
            @if($users->count() > 0)
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>姓名</th>
                            <th>邮箱</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($users as $user)
                            <tr>
                                <td>{{ $user->id }}</td>
                                <td>{{ $user->name }}</td>
                                <td>{{ $user->email }}</td>
                                <td>{{ $user->created_at->format('Y-m-d') }}</td>
                                <td>
                                    <a href="{{ route('users.show', $user->id) }}" class="btn btn-primary">查看</a>
                                    <a href="{{ route('users.edit', $user->id) }}" class="btn btn-warning">编辑</a>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
                
                <!-- 分页链接 -->
                {{ $users->links() }}
            @else
                <p>暂无用户数据</p>
            @endif
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script src="{{ asset('js/users.js') }}"></script>
@endpush
```

### Blade组件
```php
<!-- resources/views/components/alert.blade.php -->

@props(['type' => 'info', 'message'])

<div class="alert alert-{{ $type }}" role="alert">
    {{ $message }}
</div>

<!-- 使用组件 -->
<x-alert type="success" message="操作成功！" />
<x-alert type="danger" :message="$error" />

<!-- 匿名组件 -->
@props(['title'])

<div class="card">
    <div class="card-header">
        <h3>{{ $title }}</h3>
    </div>
    <div class="card-body">
        {{ $slot }}
    </div>
</div>

<!-- 使用匿名组件 -->
<x-card title="用户信息">
    <p>用户名：{{ $user->name }}</p>
    <p>邮箱：{{ $user->email }}</p>
</x-card>
```

### Blade指令
```php
<!-- 条件语句 -->
@if($user->isActive())
    <p>用户是活跃的</p>
@elseif($user->isPending())
    <p>用户待审核</p>
@else
    <p>用户未激活</p>
@endif

@unless($user->isAdmin())
    <p>普通用户</p>
@endunless

@isset($user->profile)
    <p>{{ $user->profile->bio }}</p>
@endisset

@empty($user->posts)
    <p>用户还没有发布文章</p>
@endempty

<!-- 循环语句 -->
@foreach($users as $user)
    <p>{{ $user->name }}</p>
@endforeach

@forelse($users as $user)
    <p>{{ $user->name }}</p>
@empty
    <p>没有用户</p>
@endforelse

@while($item = array_shift($items))
    <p>{{ $item }}</p>
@endwhile

<!-- 循环变量 -->
@foreach($users as $user)
    @if($loop->first)
        <p>第一个用户</p>
    @endif
    
    @if($loop->last)
        <p>最后一个用户</p>
    @endif
    
    <p>{{ $loop->index }}: {{ $user->name }}</p>
@endforeach

<!-- 原生PHP -->
@php
    $total = $users->count();
    echo "总计：$total 个用户";
@endphp

<!-- 包含视图 -->
@include('partials.header', ['title' => '用户管理'])

<!-- 包含如果存在 -->
@includeIf('partials.ads')

<!-- 包含第一个存在的视图 -->
@includeFirst(['custom.header', 'partials.header'])

<!-- 视图组合器 -->
@once
    @push('scripts')
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    @endpush
@endonce
```

## 中间件

### 创建中间件
```bash
# 创建中间件
php artisan make:middleware CheckAge
php artisan make:middleware EnsureTokenIsValid
```

### 中间件实现
```php
<?php
// app/Http/Middleware/CheckAge.php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class CheckAge
{
    public function handle(Request $request, Closure $next)
    {
        if ($request->age < 18) {
            return redirect('home');
        }
        
        return $next($request);
    }
}

// app/Http/Middleware/EnsureTokenIsValid.php

<?php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class EnsureTokenIsValid
{
    public function handle(Request $request, Closure $next)
    {
        $token = $request->header('Authorization');
        
        if (!$token || $token !== 'valid-token') {
            return response()->json(['error' => 'Invalid token'], 401);
        }
        
        return $next($request);
    }
}
```

### 注册中间件
```php
<?php
// app/Http/Kernel.php

protected $middleware = [
    // 全局中间件
    \App\Http\Middleware\TrustProxies::class,
    \Fruitcake\Cors\HandleCors::class,
    \App\Http\Middleware\PreventRequestsDuringMaintenance::class,
    \Illuminate\Foundation\Http\Middleware\ValidatePostSize::class,
    \App\Http\Middleware\TrimStrings::class,
    \Illuminate\Foundation\Http\Middleware\ConvertEmptyStringsToNull::class,
];

protected $middlewareGroups = [
    'web' => [
        \App\Http\Middleware\EncryptCookies::class,
        \Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse::class,
        \Illuminate\Session\Middleware\StartSession::class,
        \Illuminate\View\Middleware\ShareErrorsFromSession::class,
        \App\Http\Middleware\VerifyCsrfToken::class,
        \Illuminate\Routing\Middleware\SubstituteBindings::class,
    ],
    
    'api' => [
        \Laravel\Sanctum\Http\Middleware\EnsureFrontendRequestsAreStateful::class,
        'throttle:api',
        \Illuminate\Routing\Middleware\SubstituteBindings::class,
    ],
];

protected $routeMiddleware = [
    'auth' => \App\Http\Middleware\Authenticate::class,
    'auth.basic' => \Illuminate\Auth\Middleware\AuthenticateWithBasicAuth::class,
    'auth.session' => \Illuminate\Session\Middleware\AuthenticateSession::class,
    'cache.headers' => \Illuminate\Http\Middleware\SetCacheHeaders::class,
    'can' => \Illuminate\Auth\Middleware\Authorize::class,
    'guest' => \App\Http\Middleware\RedirectIfAuthenticated::class,
    'password.confirm' => \Illuminate\Auth\Middleware\RequirePassword::class,
    'signed' => \Illuminate\Routing\Middleware\ValidateSignature::class,
    'throttle' => \Illuminate\Routing\Middleware\ThrottleRequests::class,
    'verified' => \Illuminate\Auth\Middleware\EnsureEmailIsVerified::class,
    'age' => \App\Http\Middleware\CheckAge::class,
];
```

### 使用中间件
```php
// 路由中使用中间件
Route::get('/profile', function () {
    return '需要认证的路由';
})->middleware('auth');

Route::get('/admin', function () {
    return '管理员页面';
})->middleware(['auth', 'age:18']);

// 应用中间件到路由群组
Route::middleware(['auth'])->group(function () {
    Route::get('/dashboard', function () {
        return '仪表板';
    });
    
    Route::get('/profile', function () {
        return '个人资料';
    });
});

// 控制器中使用中间件
<?php
// app/Http/Controllers/AdminController.php

class AdminController extends Controller
{
    public function __construct()
    {
        $this->middleware('auth');
        $this->middleware('age:18')->only('index');
        $this->middleware('permission:admin')->except('show');
    }
    
    public function index()
    {
        return '管理员仪表板';
    }
    
    public function show()
    {
        return '显示信息';
    }
}
```

## 表单验证

### 控制器验证
```php
<?php
// app/Http/Controllers/UserController.php

public function store(Request $request)
{
    $validated = $request->validate([
        'name' => 'required|string|max:255',
        'email' => 'required|string|email|max:255|unique:users',
        'password' => 'required|string|min:8|confirmed',
        'age' => 'required|integer|min:18',
        'avatar' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:2048',
    ]);
    
    // 验证通过后的逻辑
    User::create($validated);
    
    return redirect()->route('users.index')
        ->with('success', '用户创建成功！');
}

// 自定义验证消息
public function store(Request $request)
{
    $validated = $request->validate([
        'name' => 'required|string|max:255',
        'email' => 'required|email|unique:users',
    ], [
        'name.required' => '姓名是必填项',
        'name.max' => '姓名不能超过255个字符',
        'email.required' => '邮箱是必填项',
        'email.email' => '请输入有效的邮箱地址',
        'email.unique' => '该邮箱已被使用',
    ]);
    
    User::create($validated);
    
    return redirect()->back()->with('success', '注册成功！');
}
```

### 表单请求验证
```bash
# 创建表单请求
php artisan make:request StoreUserRequest
php artisan make:request UpdateUserRequest
```

```php
<?php
// app/Http/Requests/StoreUserRequest.php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class StoreUserRequest extends FormRequest
{
    public function authorize()
    {
        return true; // 设置为false则返回403错误
    }
    
    public function rules()
    {
        return [
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:8|confirmed',
            'age' => 'required|integer|min:18|max:120',
            'phone' => 'nullable|string|regex:/^1[3-9]\d{9}$/',
            'avatar' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:2048',
            'bio' => 'nullable|string|max:500',
        ];
    }
    
    public function messages()
    {
        return [
            'name.required' => '姓名是必填项',
            'email.required' => '邮箱是必填项',
            'email.email' => '请输入有效的邮箱地址',
            'email.unique' => '该邮箱已被使用',
            'password.required' => '密码是必填项',
            'password.min' => '密码至少需要8个字符',
            'password.confirmed' => '两次输入的密码不一致',
            'age.required' => '年龄是必填项',
            'age.min' => '年龄不能小于18岁',
            'age.max' => '年龄不能大于120岁',
            'phone.regex' => '请输入有效的手机号码',
            'avatar.image' => '请上传图片文件',
            'avatar.mimes' => '只支持JPEG、PNG、JPG、GIF格式',
            'avatar.max' => '图片大小不能超过2MB',
        ];
    }
    
    public function attributes()
    {
        return [
            'name' => '姓名',
            'email' => '邮箱',
            'password' => '密码',
            'age' => '年龄',
            'phone' => '手机号码',
            'avatar' => '头像',
            'bio' => '个人简介',
        ];
    }
}

// 在控制器中使用
<?php
// app/Http/Controllers/UserController.php

use App\Http\Requests\StoreUserRequest;

public function store(StoreUserRequest $request)
{
    // 验证已经通过，$request中包含验证过的数据
    $validated = $request->validated();
    
    // 创建用户
    $user = User::create($validated);
    
    return redirect()->route('users.show', $user->id)
        ->with('success', '用户创建成功！');
}
```

## Artisan命令

### 常用Artisan命令
```bash
# 项目创建
composer create-project laravel/laravel project-name
laravel new project-name

# 服务器启动
php artisan serve
php artisan serve --host=127.0.0.1 --port=8080

# 路由查看
php artisan route:list
php artisan route:list --name=users

# 数据库操作
php artisan migrate
php artisan migrate:rollback
php artisan migrate:fresh
php artisan migrate:refresh --seed

# 数据填充
php artisan db:seed
php artisan db:seed --class=UsersTableSeeder

# 模型和迁移
php artisan make:model User -m
php artisan make:model Post -mcr

# 控制器
php artisan make:controller UserController
php artisan make:controller UserController --resource
php artisan make:controller Api/UserController --api

# 中间件
php artisan make:middleware CheckAge

# 表单请求
php artisan make:request StoreUserRequest

# 缓存操作
php artisan cache:clear
php artisan config:clear
php artisan route:clear
php artisan view:clear

# 队列
php artisan queue:work
php artisan queue:failed-table

# 日志
php artisan log:clear

# 环境配置
php artisan env
```

### 自定义Artisan命令
```bash
# 创建命令
php artisan make:command SendEmailsCommand
```

```php
<?php
// app/Console/Commands/SendEmailsCommand.php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\User;
use Illuminate\Support\Facades\Mail;

class SendEmailsCommand extends Command
{
    protected $signature = 'emails:send {user? : The ID of the user} {--queue : Whether to queue the job}';
    
    protected $description = 'Send emails to users';
    
    public function __construct()
    {
        parent::__construct();
    }
    
    public function handle()
    {
        $userId = $this->argument('user');
        $shouldQueue = $this->option('queue');
        
        if ($userId) {
            $user = User::find($userId);
            if (!$user) {
                $this->error("User with ID {$userId} not found");
                return 1;
            }
            $this->sendEmailToUser($user, $shouldQueue);
        } else {
            $users = User::where('receive_emails', true)->get();
            
            $this->withProgressBar($users, function ($user) use ($shouldQueue) {
                $this->sendEmailToUser($user, $shouldQueue);
            });
            
            $this->newLine();
            $this->info("Emails sent to {$users->count()} users");
        }
        
        return 0;
    }
    
    private function sendEmailToUser($user, $shouldQueue)
    {
        if ($shouldQueue) {
            // 队列发送
            dispatch(new SendEmailJob($user));
        } else {
            // 立即发送
            Mail::to($user->email)->send(new WelcomeEmail($user));
        }
    }
}

// 注册命令
<?php
// app/Console/Kernel.php

protected $commands = [
    \App\Console\Commands\SendEmailsCommand::class,
];
```

## 最佳实践

1. **代码组织**：遵循PSR-4自动加载规范，合理组织代码结构。
2. **命名规范**：使用有意义的变量和函数名，遵循Laravel命名约定。
3. **数据库设计**：使用迁移管理数据库结构，保持数据一致性。
4. **安全性**：使用Laravel内置的安全功能，如CSRF保护、输入验证等。
5. **缓存策略**：合理使用缓存提高应用性能。
6. **测试**：编写单元测试和功能测试确保代码质量。
7. **错误处理**：使用异常处理器统一处理应用错误。