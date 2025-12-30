# Spring Boot Web 开发

Spring Boot 提供了强大的Web开发支持，让构建Web应用变得简单快捷。

## RESTful API 开发

### 基础控制器

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }
    
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        return userService.getUserById(id)
                .orElseThrow(() -> new UserNotFoundException("User not found with id: " + id));
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        User savedUser = userService.saveUser(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedUser);
    }
    
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @Valid @RequestBody User userDetails) {
        User user = userService.getUserById(id)
                .orElseThrow(() -> new UserNotFoundException("User not found with id: " + id));
        
        user.setName(userDetails.getName());
        user.setEmail(userDetails.getEmail());
        return userService.saveUser(user);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteUser(@PathVariable Long id) {
        User user = userService.getUserById(id)
                .orElseThrow(() -> new UserNotFoundException("User not found with id: " + id));
        
        userService.deleteUser(user);
        return ResponseEntity.ok().build();
    }
}
```

### 请求参数处理

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    // 路径变量
    @GetMapping("/{id}")
    public Product getProduct(@PathVariable Long id) {
        return productService.findById(id);
    }
    
    // 查询参数
    @GetMapping
    public List<Product> getProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String category) {
        return productService.findByCategory(category, PageRequest.of(page, size));
    }
    
    // 请求体
    @PostMapping
    public Product createProduct(@RequestBody Product product) {
        return productService.save(product);
    }
    
    // 请求头
    @GetMapping("/info")
    public Map<String, String> getInfo(@RequestHeader("User-Agent") String userAgent) {
        Map<String, String> info = new HashMap<>();
        info.put("userAgent", userAgent);
        return info;
    }
}
```

## 模板引擎

### Thymeleaf 配置和使用

添加依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

控制器：

```java
@Controller
public class HomeController {
    
    @Autowired
    private ProductService productService;
    
    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("products", productService.getAllProducts());
        model.addAttribute("title", "首页");
        return "index";
    }
    
    @GetMapping("/product/{id}")
    public String productDetail(@PathVariable Long id, Model model) {
        model.addAttribute("product", productService.findById(id));
        return "product-detail";
    }
}
```

Thymeleaf 模板 (templates/index.html)：

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <title th:text="${title}">默认标题</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>产品列表</h1>
    <div th:if="${#lists.isEmpty(products)}">
        <p>暂无产品</p>
    </div>
    <div th:unless="${#lists.isEmpty(products)}">
        <ul>
            <li th:each="product : ${products}">
                <a th:href="@{/product/{id}(id=${product.id})}" th:text="${product.name}">产品名</a>
                - <span th:text="${product.price}">价格</span>
            </li>
        </ul>
    </div>
</body>
</html>
```

## 静态资源处理

Spring Boot 默认从以下位置提供静态资源：

- `classpath:/static/`
- `classpath:/public/`
- `classpath:/resources/`
- `classpath:/META-INF/resources/`

配置静态资源路径：

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**")
                .addResourceLocations("classpath:/static/");
        
        // 映射外部目录
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:/path/to/uploads/");
    }
}
```

## 异常处理

### 全局异常处理器

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFoundException(UserNotFoundException ex) {
        ErrorResponse error = new ErrorResponse("USER_NOT_FOUND", ex.getMessage());
        return new ResponseEntity<>(error, HttpStatus.NOT_FOUND);
    }
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(ValidationException ex) {
        ErrorResponse error = new ErrorResponse("VALIDATION_ERROR", ex.getMessage());
        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception ex) {
        ErrorResponse error = new ErrorResponse("INTERNAL_ERROR", "内部服务器错误");
        return new ResponseEntity<>(error, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}

// 错误响应类
class ErrorResponse {
    private String code;
    private String message;
    private long timestamp;
    
    public ErrorResponse(String code, String message) {
        this.code = code;
        this.message = message;
        this.timestamp = System.currentTimeMillis();
    }
    
    // getters and setters
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
}
```

## 数据验证

### Bean Validation

```java
public class User {
    @NotNull(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20个字符之间")
    private String username;
    
    @NotNull(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;
    
    @Min(value = 18, message = "年龄不能小于18岁")
    @Max(value = 100, message = "年龄不能大于100岁")
    private int age;
    
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;
    
    // constructors, getters and setters
}
```

控制器中使用验证：

```java
@PostMapping
public ResponseEntity<?> createUser(@Valid @RequestBody User user, BindingResult bindingResult) {
    if (bindingResult.hasErrors()) {
        List<String> errors = bindingResult.getFieldErrors()
                .stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .collect(Collectors.toList());
        return ResponseEntity.badRequest().body(errors);
    }
    
    User savedUser = userService.saveUser(user);
    return ResponseEntity.ok(savedUser);
}
```