# 第3章：Spring Boot Web开发

## 3.1 RESTful API开发

### 3.1.1 @RestController注解

`@RestController`是`@Controller`和`@ResponseBody`的组合注解，用于创建RESTful风格的API。

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping
    public List<User> getAllUsers() {
        return userService.findAll();
    }

    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        return userService.findById(id);
    }

    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }

    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User user) {
        user.setId(id);
        return userService.save(user);
    }

    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        userService.deleteById(id);
    }
}
```

### 3.1.2 请求参数绑定

#### @PathVariable

```java
@GetMapping("/users/{userId}/orders/{orderId}")
public Order getOrder(@PathVariable Long userId, @PathVariable Long orderId) {
    return orderService.findByUserIdAndOrderId(userId, orderId);
}
```

#### @RequestParam

```java
@GetMapping("/users")
public Page<User> getUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(required = false) String keyword) {
    return userService.searchUsers(page, size, keyword);
}
```

#### @RequestBody

```java
@PostMapping("/users")
public User createUser(@Valid @RequestBody UserCreateRequest request) {
    return userService.createUser(request);
}
```

#### @RequestHeader

```java
@GetMapping("/users/profile")
public UserProfile getUserProfile(@RequestHeader("Authorization") String token) {
    String userId = jwtService.getUserIdFromToken(token);
    return userService.getUserProfile(userId);
}
```

#### @CookieValue

```java
@GetMapping("/users/preferences")
public UserPreferences getPreferences(@CookieValue(value = "userPrefs", defaultValue = "") String prefs) {
    return userService.parsePreferences(prefs);
}
```

### 3.1.3 请求体验证

#### 使用Validation注解

```java
public class UserCreateRequest {

    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20之间")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d]{8,}$",
             message = "密码必须包含大小写字母和数字，至少8位")
    private String password;

    @Email(message = "邮箱格式不正确")
    @NotBlank(message = "邮箱不能为空")
    private String email;

    @Min(value = 18, message = "年龄必须大于等于18")
    @Max(value = 120, message = "年龄必须小于等于120")
    private Integer age;

    @NotNull(message = "性别不能为空")
    private Gender gender;

    public enum Gender {
        MALE, FEMALE, OTHER
    }
}
```

#### 全局异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(
            MethodArgumentNotValidException ex) {
        List<String> errors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            .collect(Collectors.toList());

        ErrorResponse response = ErrorResponse.builder()
            .code(400)
            .message("参数验证失败")
            .errors(errors)
            .timestamp(LocalDateTime.now())
            .build();

        return ResponseEntity.badRequest().body(response);
    }

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException ex) {
        ErrorResponse response = ErrorResponse.builder()
            .code(ex.getCode())
            .message(ex.getMessage())
            .timestamp(LocalDateTime.now())
            .build();
        return ResponseEntity.status(ex.getHttpStatus()).body(response);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleException(Exception ex) {
        ErrorResponse response = ErrorResponse.builder()
            .code(500)
            .message("系统内部错误")
            .timestamp(LocalDateTime.now())
            .build();
        return ResponseEntity.internalServerError().body(response);
    }
}
```

## 3.2 统一响应格式

### 3.2.1 统一响应对象

```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponse<T> {

    private Integer code;
    private String message;
    private T data;
    private Long timestamp;

    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
            .code(200)
            .message("success")
            .data(data)
            .timestamp(System.currentTimeMillis())
            .build();
    }

    public static <T> ApiResponse<T> success(String message, T data) {
        return ApiResponse.<T>builder()
            .code(200)
            .message(message)
            .data(data)
            .timestamp(System.currentTimeMillis())
            .build();
    }

    public static <T> ApiResponse<T> error(Integer code, String message) {
        return ApiResponse.<T>builder()
            .code(code)
            .message(message)
            .timestamp(System.currentTimeMillis())
            .build();
    }

    public static <T> ApiResponse<T> error(BusinessException ex) {
        return ApiResponse.<T>builder()
            .code(ex.getCode())
            .message(ex.getMessage())
            .timestamp(System.currentTimeMillis())
            .build();
    }
}
```

### 3.2.2 使用统一响应

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    @Autowired
    private ProductService productService;

    @GetMapping("/{id}")
    public ApiResponse<Product> getProduct(@PathVariable Long id) {
        Product product = productService.findById(id);
        return ApiResponse.success(product);
    }

    @PostMapping
    public ApiResponse<Product> createProduct(@Valid @RequestBody ProductCreateRequest request) {
        Product product = productService.create(request);
        return ApiResponse.success("创建成功", product);
    }

    @GetMapping
    public ApiResponse<Page<Product>> getProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Page<Product> products = productService.findAll(page, size);
        return ApiResponse.success(products);
    }
}
```

### 3.2.3 响应包装器

```java
@RestControllerAdvice
public class ResponseAdvice implements ResponseBodyAdvice<Object> {

    @Override
    public boolean supports(MethodParameter returnType,
                           Class<? extends HttpMessageConverter<?>> converterType) {
        return !returnType.getParameterType().equals(ApiResponse.class)
            && !returnType.getParameterType().equals(ResponseEntity.class)
            && !returnType.hasMethodAnnotation(NoWrapResponse.class);
    }

    @Override
    public Object beforeBodyWrite(Object body, MethodParameter returnType,
                                 MediaType selectedContentType,
                                 Class<? extends HttpMessageConverter<?>> selectedConverterType,
                                 ServerHttpRequest request, ServerHttpResponse response) {
        if (body instanceof String) {
            return JsonUtils.toJson(ApiResponse.success(body));
        }
        return ApiResponse.success(body);
    }
}

@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface NoWrapResponse {
}
```

## 3.3 文件上传下载

### 3.3.1 文件上传

#### 单文件上传

```java
@RestController
@RequestMapping("/api/files")
public class FileUploadController {

    @Value("${file.upload.path}")
    private String uploadPath;

    @PostMapping("/upload")
    public ApiResponse<String> uploadFile(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            throw new BusinessException("文件不能为空");
        }

        String originalFilename = file.getOriginalFilename();
        String extension = originalFilename.substring(originalFilename.lastIndexOf("."));
        String filename = UUID.randomUUID() + extension;
        String filepath = uploadPath + filename;

        try {
            File dest = new File(filepath);
            if (!dest.getParentFile().exists()) {
                dest.getParentFile().mkdirs();
            }
            file.transferTo(dest);
            return ApiResponse.success("/files/" + filename);
        } catch (IOException e) {
            throw new BusinessException("文件上传失败");
        }
    }
}
```

#### 多文件上传

```java
@PostMapping("/uploads")
public ApiResponse<List<String>> uploadFiles(@RequestParam("files") MultipartFile[] files) {
    List<String> fileUrls = new ArrayList<>();

    for (MultipartFile file : files) {
        if (!file.isEmpty()) {
            String fileUrl = uploadFile(file);
            fileUrls.add(fileUrl);
        }
    }

    return ApiResponse.success(fileUrls);
}
```

### 3.3.2 文件下载

```java
@GetMapping("/download/{filename}")
public void downloadFile(@PathVariable String filename,
                        HttpServletResponse response) throws IOException {
    String filepath = uploadPath + filename;
    File file = new File(filepath);

    if (!file.exists()) {
        throw new BusinessException("文件不存在");
    }

    response.setContentType("application/octet-stream");
    response.setHeader("Content-Disposition",
        "attachment; filename=" + URLEncoder.encode(filename, "UTF-8"));

    try (InputStream in = new FileInputStream(file);
         OutputStream out = response.getOutputStream()) {
        byte[] buffer = new byte[1024];
        int len;
        while ((len = in.read(buffer)) > 0) {
            out.write(buffer, 0, len);
        }
    }
}
```

### 3.3.3 配置文件上传限制

```yaml
spring:
  servlet:
    multipart:
      enabled: true
      max-file-size: 10MB
      max-request-size: 100MB
      file-size-threshold: 2MB
      location: ${java.io.tmpdir}
```

## 3.4 静态资源处理

### 3.4.1 静态资源配置

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**")
            .addResourceLocations("classpath:/static/");

        registry.addResourceHandler("/uploads/**")
            .addResourceLocations("file:/path/to/uploads/");

        registry.addResourceHandler("/swagger-ui/**")
            .addResourceLocations("classpath:/META-INF/resources/webjars/springfox-swagger-ui/");
    }
}
```

### 3.4.2 欢迎页面配置

```java
@Configuration
public class WelcomePageConfig implements WebMvcConfigurer {

    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        registry.addViewController("/").setViewName("forward:/index.html");
        registry.setOrder(Ordered.HIGHEST_PRECEDENCE);
    }
}
```

## 3.5 跨域配置

### 3.5.1 注解方式

```java
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*", maxAge = 3600)
public class ApiController {

    @GetMapping("/data")
    public String getData() {
        return "data";
    }
}
```

### 3.5.2 全局配置

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOriginPatterns("*")
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("*")
            .allowCredentials(true)
            .maxAge(3600);
    }
}
```

### 3.5.3 基于Filter的跨域配置

```java
@Component
public class CorsFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                        FilterChain chain) throws IOException, ServletException {
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        HttpServletRequest httpRequest = (HttpServletRequest) request;

        httpResponse.setHeader("Access-Control-Allow-Origin", "*");
        httpResponse.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        httpResponse.setHeader("Access-Control-Allow-Headers", "*");
        httpResponse.setHeader("Access-Control-Allow-Credentials", "true");
        httpResponse.setHeader("Access-Control-Max-Age", "3600");

        if ("OPTIONS".equalsIgnoreCase(httpRequest.getMethod())) {
            httpResponse.setStatus(HttpServletResponse.SC_OK);
            return;
        }

        chain.doFilter(request, response);
    }
}
```

## 3.6 拦截器

### 3.6.1 登录拦截器

```java
@Component
public class LoginInterceptor implements HandlerInterceptor {

    @Autowired
    private JwtService jwtService;

    @Override
    public boolean preHandle(HttpServletRequest request,
                           HttpServletResponse response,
                           Object handler) throws Exception {
        if (handler instanceof HandlerMethod) {
            HandlerMethod handlerMethod = (HandlerMethod) handler;
            NoAuth noAuth = handlerMethod.getMethodAnnotation(NoAuth.class);
            if (noAuth != null) {
                return true;
            }
        }

        String token = request.getHeader("Authorization");
        if (StringUtils.isEmpty(token)) {
            throw new UnauthorizedException("未登录");
        }

        try {
            String userId = jwtService.getUserIdFromToken(token);
            request.setAttribute("userId", userId);
            return true;
        } catch (Exception e) {
            throw new UnauthorizedException("登录已过期");
        }
    }
}

@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface NoAuth {
}
```

### 3.6.2 注册拦截器

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Autowired
    private LoginInterceptor loginInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loginInterceptor)
            .addPathPatterns("/api/**")
            .excludePathPatterns("/api/auth/login", "/api/auth/register");
    }
}
```

## 3.7 过滤器

### 3.7.1 请求日志过滤器

```java
@Component
@Slf4j
public class RequestLoggingFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                   HttpServletResponse response,
                                   FilterChain filterChain) throws ServletException, IOException {
        long startTime = System.currentTimeMillis();
        String requestId = UUID.randomUUID().toString();

        MDC.put("requestId", requestId);

        try {
            log.info("Request: {} {} {}", requestId, request.getMethod(), request.getRequestURI());
            filterChain.doFilter(request, response);
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            log.info("Response: {} {} {} - Status: {} - Duration: {}ms",
                requestId, request.getMethod(), request.getRequestURI(),
                response.getStatus(), duration);
            MDC.clear();
        }
    }
}
```

### 3.7.2 请求包装过滤器

```java
public class RequestWrapper extends HttpServletRequestWrapper {

    private final byte[] body;

    public RequestWrapper(HttpServletRequest request) throws IOException {
        super(request);
        this.body = StreamUtils.copyToByteArray(request.getInputStream());
    }

    @Override
    public ServletInputStream getInputStream() {
        return new ServletInputStream() {
            private final ByteArrayInputStream inputStream = new ByteArrayInputStream(body);

            @Override
            public boolean isFinished() {
                return inputStream.available() == 0;
            }

            @Override
            public boolean isReady() {
                return true;
            }

            @Override
            public void setReadListener(ReadListener listener) {
            }

            @Override
            public int read() {
                return inputStream.read();
            }
        };
    }

    @Override
    public BufferedReader getReader() {
        return new BufferedReader(new InputStreamReader(getInputStream()));
    }

    public byte[] getBody() {
        return body;
    }
}
```

## 3.8 异步处理

### 3.8.1 异步Controller

```java
@RestController
@RequestMapping("/api/async")
public class AsyncController {

    @Autowired
    private AsyncTaskService asyncTaskService;

    @GetMapping("/task")
    public CompletableFuture<String> asyncTask() {
        return CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(3000);
                return "Task completed";
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @GetMapping("/execute")
    public CompletableFuture<String> executeAsyncTask() {
        return asyncTaskService.executeTask();
    }
}

@Service
public class AsyncTaskService {

    @Async
    public CompletableFuture<String> executeTask() {
        try {
            Thread.sleep(3000);
            return CompletableFuture.completedFuture("Async task completed");
        } catch (InterruptedException e) {
            return CompletableFuture.failedFuture(e);
        }
    }
}
```

### 3.8.2 异步配置

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(200);
        executor.setThreadNamePrefix("async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return new AsyncExceptionHandler();
    }
}

public class AsyncExceptionHandler implements AsyncUncaughtExceptionHandler {

    @Override
    public void handleUncaughtException(Throwable ex, Method method, Object... params) {
        log.error("Async method {} threw exception: {}", method.getName(), ex.getMessage(), ex);
    }
}
```

## 3.9 WebSocket

### 3.9.1 WebSocket配置

```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(chatHandler(), "/ws/chat")
            .setAllowedOriginPatterns("*");
    }

    @Bean
    public ChatHandler chatHandler() {
        return new ChatHandler();
    }
}
```

### 3.9.2 WebSocket处理器

```java
@Component
public class ChatHandler extends TextWebSocketHandler {

    private static final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        String userId = getUserId(session);
        sessions.put(userId, session);
        sendMessageToAll("User " + userId + " joined");
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) {
        String userId = getUserId(session);
        String payload = message.getPayload();
        sendMessageToAll(userId + ": " + payload);
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        String userId = getUserId(session);
        sessions.remove(userId);
        sendMessageToAll("User " + userId + " left");
    }

    private void sendMessageToAll(String message) {
        sessions.values().forEach(session -> {
            try {
                session.sendMessage(new TextMessage(message));
            } catch (IOException e) {
                log.error("Failed to send message", e);
            }
        });
    }

    private String getUserId(WebSocketSession session) {
        return session.getUri().getQuery().split("=")[1];
    }
}
```

### 3.9.3 STOMP配置

```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketMessageBrokerConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
            .setAllowedOriginPatterns("*")
            .withSockJS();
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.enableSimpleBroker("/topic", "/queue");
        registry.setApplicationDestinationPrefixes("/app");
        registry.setUserDestinationPrefix("/user");
    }
}

@Controller
public class ChatController {

    @MessageMapping("/chat.sendMessage")
    @SendTo("/topic/public")
    public ChatMessage sendMessage(@Payload ChatMessage chatMessage) {
        return chatMessage;
    }

    @MessageMapping("/chat.addUser")
    @SendTo("/topic/public")
    public ChatMessage addUser(@Payload ChatMessage chatMessage,
                               SimpMessageHeaderAccessor headerAccessor) {
        headerAccessor.getSessionAttributes().put("username", chatMessage.getSender());
        return chatMessage;
    }
}
```

## 3.10 互联网大厂真实项目代码示例

### 3.10.1 阿里巴巴统一响应处理

```java
package com.alibaba.common.result;

import com.alibaba.common.exception.ErrorCode;
import lombok.Data;

@Data
public class Result<T> {

    private Integer code;
    private String message;
    private T data;
    private Long timestamp;

    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.setCode(200);
        result.setMessage("success");
        result.setData(data);
        result.setTimestamp(System.currentTimeMillis());
        return result;
    }

    public static <T> Result<T> error(ErrorCode errorCode) {
        Result<T> result = new Result<>();
        result.setCode(errorCode.getCode());
        result.setMessage(errorCode.getMessage());
        result.setTimestamp(System.currentTimeMillis());
        return result;
    }

    public static <T> Result<T> error(Integer code, String message) {
        Result<T> result = new Result<>();
        result.setCode(code);
        result.setMessage(message);
        result.setTimestamp(System.currentTimeMillis());
        return result;
    }
}
```

### 3.10.2 腾讯云文件上传

```java
package com.tencent.cloud.controller;

import com.tencent.cloud.service.FileStorageService;
import com.tencent.cloud.vo.UploadResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/storage")
public class FileStorageController {

    @Autowired
    private FileStorageService fileStorageService;

    @PostMapping("/upload")
    public UploadResult uploadFile(@RequestParam("file") MultipartFile file,
                                   @RequestParam(required = false) String path) {
        return fileStorageService.upload(file, path);
    }

    @PostMapping("/batch-upload")
    public UploadResult batchUpload(@RequestParam("files") MultipartFile[] files) {
        return fileStorageService.batchUpload(files);
    }

    @DeleteMapping("/delete")
    public void deleteFile(@RequestParam String fileKey) {
        fileStorageService.delete(fileKey);
    }

    @GetMapping("/presigned-url")
    public String getPresignedUrl(@RequestParam String fileKey,
                                   @RequestParam(defaultValue = "3600") long expireSeconds) {
        return fileStorageService.generatePresignedUrl(fileKey, expireSeconds);
    }
}
```

### 3.10.3 美团全局异常处理

```java
package com.meituan.framework.exception;

import com.meituan.framework.result.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<?> handleBusinessException(BusinessException e) {
        log.warn("Business exception: {}", e.getMessage());
        return Result.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<?> handleValidationException(MethodArgumentNotValidException e) {
        FieldError fieldError = e.getBindingResult().getFieldError();
        String message = fieldError != null ? fieldError.getDefaultMessage() : "参数验证失败";
        log.warn("Validation exception: {}", message);
        return Result.error(400, message);
    }

    @ExceptionHandler(BindException.class)
    public Result<?> handleBindException(BindException e) {
        FieldError fieldError = e.getFieldError();
        String message = fieldError != null ? fieldError.getDefaultMessage() : "参数绑定失败";
        log.warn("Bind exception: {}", message);
        return Result.error(400, message);
    }

    @ExceptionHandler(Exception.class)
    public Result<?> handleException(Exception e) {
        log.error("System exception", e);
        return Result.error(500, "系统内部错误");
    }
}
```

### 3.10.4 字节跳动请求日志

```java
package com.bytedance.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;
import org.springframework.web.util.ContentCachingResponseWrapper;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Slf4j
@Component
public class RequestLoggingFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                   HttpServletResponse response,
                                   FilterChain filterChain) throws ServletException, IOException {
        ContentCachingRequestWrapper requestWrapper = new ContentCachingRequestWrapper(request);
        ContentCachingResponseWrapper responseWrapper = new ContentCachingResponseWrapper(response);

        long startTime = System.currentTimeMillis();

        try {
            filterChain.doFilter(requestWrapper, responseWrapper);
        } finally {
            long duration = System.currentTimeMillis() - startTime;

            String requestBody = new String(requestWrapper.getContentAsByteArray(),
                StandardCharsets.UTF_8);
            String responseBody = new String(responseWrapper.getContentAsByteArray(),
                StandardCharsets.UTF_8);

            log.info("Request: {} {} | Body: {} | Response: {} | Status: {} | Duration: {}ms",
                request.getMethod(), request.getRequestURI(),
                requestBody, responseBody, response.getStatus(), duration);

            responseWrapper.copyBodyToResponse();
        }
    }
}
```

### 3.10.5 京东健康拦截器

```java
package com.jd.health.interceptor;

import com.jd.health.util.JwtUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@Slf4j
@Component
public class AuthInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                           HttpServletResponse response,
                           Object handler) {
        if (!(handler instanceof HandlerMethod)) {
            return true;
        }

        HandlerMethod handlerMethod = (HandlerMethod) handler;
        NoAuth noAuth = handlerMethod.getMethodAnnotation(NoAuth.class);
        if (noAuth != null) {
            return true;
        }

        String token = request.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            throw new UnauthorizedException("未登录");
        }

        token = token.substring(7);
        try {
            Long userId = JwtUtil.getUserId(token);
            request.setAttribute("userId", userId);
            return true;
        } catch (Exception e) {
            throw new UnauthorizedException("登录已过期");
        }
    }
}
```

### 3.10.6 拼多多跨域配置

```java
package com.pdd.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

@Configuration
public class CorsConfig {

    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOriginPattern("*");
        config.setAllowCredentials(true);
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
```

### 3.10.7 网易云WebSocket

```java
package com.netease.websocket;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.*;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
            .setAllowedOriginPatterns("*")
            .withSockJS();
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.enableSimpleBroker("/topic", "/queue");
        registry.setApplicationDestinationPrefixes("/app");
        registry.setUserDestinationPrefix("/user");
    }
}
```

## 3.11 最佳实践

1. **统一响应格式**：提供一致的API响应结构
2. **参数验证**：使用Validation注解进行参数校验
3. **全局异常处理**：统一处理各类异常
4. **日志记录**：记录请求和响应信息
5. **安全控制**：使用拦截器进行权限验证
6. **异步处理**：合理使用异步提升性能
7. **文件上传**：限制文件大小和类型

## 3.12 小结

本章介绍了Spring Boot Web开发的核心内容，包括：

- RESTful API开发
- 统一响应格式
- 文件上传下载
- 静态资源处理
- 跨域配置
- 拦截器和过滤器
- 异步处理
- WebSocket

通过本章学习，你应该能够：

- 开发RESTful风格的API
- 实现文件上传下载功能
- 配置跨域和拦截器
- 处理全局异常
- 使用WebSocket进行实时通信

下一章将介绍Spring Boot的数据访问技术。
