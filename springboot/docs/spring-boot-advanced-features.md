# Spring Boot 高级特性

本章将深入探讨 Spring Boot 的高级特性，包括响应式编程、微服务架构、自定义starter开发等。

## 响应式编程

### WebFlux 入门

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

### 响应式控制器

```java
@RestController
@RequestMapping("/api/reactive")
public class ReactiveController {
    
    @Autowired
    private ReactiveUserService userService;
    
    @GetMapping("/users/{id}")
    public Mono<User> getUserById(@PathVariable String id) {
        return userService.findById(id);
    }
    
    @GetMapping("/users")
    public Flux<User> getAllUsers() {
        return userService.findAll();
    }
    
    @PostMapping("/users")
    public Mono<User> createUser(@RequestBody User user) {
        return userService.save(user);
    }
    
    @GetMapping(value = "/users/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<User> streamUsers() {
        return userService.findAll()
            .delayElements(Duration.ofSeconds(1)); // 每秒发送一个用户
    }
}
```

### 响应式服务层

```java
@Service
public class ReactiveUserService {
    
    private final ReactiveUserRepository userRepository;
    
    public ReactiveUserService(ReactiveUserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public Mono<User> findById(String id) {
        return userRepository.findById(id)
            .switchIfEmpty(Mono.error(new UserNotFoundException("User not found: " + id)));
    }
    
    public Flux<User> findAll() {
        return userRepository.findAll()
            .onErrorResume(throwable -> {
                // 错误处理
                System.err.println("Error fetching users: " + throwable.getMessage());
                return Flux.empty();
            });
    }
    
    public Mono<User> save(User user) {
        user.setCreatedAt(Instant.now());
        return userRepository.save(user);
    }
    
    public Mono<Void> deleteById(String id) {
        return userRepository.deleteById(id);
    }
    
    // 复杂的响应式操作
    public Flux<User> findUsersByCriteria(String name, String email) {
        return userRepository.findByNameContainingOrEmailContaining(name, email)
            .filter(user -> user.isActive()) // 过滤活跃用户
            .map(this::enrichUser) // 转换用户信息
            .sort(Comparator.comparing(User::getCreatedAt).reversed()); // 按创建时间排序
    }
    
    private User enrichUser(User user) {
        // 丰富用户信息
        user.setEnriched(true);
        return user;
    }
}
```

### 响应式数据访问

```java
// 使用 Spring Data R2DBC
@Repository
public interface ReactiveUserRepository extends ReactiveCrudRepository<User, String> {
    
    Flux<User> findByEmailContaining(String email);
    
    Flux<User> findByNameContainingOrEmailContaining(String name, String email);
    
    @Query("SELECT * FROM users WHERE created_at > :date")
    Flux<User> findUsersCreatedAfter(@Param("date") Instant date);
    
    @Query("SELECT * FROM users WHERE active = :active")
    Flux<User> findByActiveStatus(@Param("active") boolean active);
}
```

## 自定义 Starter 开发

### Starter 项目结构

```
my-spring-boot-starter/
├── my-spring-boot-starter-autoconfigure/
│   └── src/main/java/
│       └── com/example/starter/
│           ├── MyService.java
│           ├── MyServiceProperties.java
│           ├── MyServiceAutoConfiguration.java
│           └── MyServiceHealthIndicator.java
├── my-spring-boot-starter/
│   └── pom.xml
└── pom.xml
```

### 属性配置类

```java
@ConfigurationProperties(prefix = "my.service")
public class MyServiceProperties {
    
    private String apiKey = "default-key";
    private String endpoint = "https://api.example.com";
    private int timeout = 5000;
    private boolean enabled = true;
    private int maxRetries = 3;
    private Map<String, String> headers = new HashMap<>();
    
    // getters and setters
    public String getApiKey() { return apiKey; }
    public void setApiKey(String apiKey) { this.apiKey = apiKey; }
    
    public String getEndpoint() { return endpoint; }
    public void setEndpoint(String endpoint) { this.endpoint = endpoint; }
    
    public int getTimeout() { return timeout; }
    public void setTimeout(int timeout) { this.timeout = timeout; }
    
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    
    public int getMaxRetries() { return maxRetries; }
    public void setMaxRetries(int maxRetries) { this.maxRetries = maxRetries; }
    
    public Map<String, String> getHeaders() { return headers; }
    public void setHeaders(Map<String, String> headers) { this.headers = headers; }
}
```

### 自动配置类

```java
@Configuration
@EnableConfigurationProperties(MyServiceProperties.class)
@ConditionalOnProperty(prefix = "my.service", name = "enabled", havingValue = "true", matchIfMissing = true)
@ConditionalOnClass(MyService.class)
public class MyServiceAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public MyService myService(MyServiceProperties properties) {
        return new MyService(properties);
    }
    
    @Bean
    @ConditionalOnMissingBean
    @ConditionalOnEnabledHealthIndicator("my-service")
    public MyServiceHealthIndicator myServiceHealthIndicator(MyService myService) {
        return new MyServiceHealthIndicator(myService);
    }
    
    @Bean
    @ConditionalOnMissingBean
    public MyServiceManager myServiceManager(MyService myService) {
        return new MyServiceManager(myService);
    }
}
```

### Starter 依赖配置

```xml
<!-- my-spring-boot-starter/pom.xml -->
<dependencies>
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>my-spring-boot-starter-autoconfigure</artifactId>
        <version>${project.version}</version>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>
</dependencies>
```

### 配置元数据

```json
// src/main/resources/META-INF/additional-spring-configuration-metadata.json
{
  "properties": [
    {
      "name": "my.service.api-key",
      "type": "java.lang.String",
      "description": "The API key for the service.",
      "defaultValue": "default-key"
    },
    {
      "name": "my.service.endpoint",
      "type": "java.lang.String",
      "description": "The service endpoint URL.",
      "defaultValue": "https://api.example.com"
    },
    {
      "name": "my.service.timeout",
      "type": "java.lang.Integer",
      "description": "Request timeout in milliseconds.",
      "defaultValue": 5000
    },
    {
      "name": "my.service.enabled",
      "type": "java.lang.Boolean",
      "description": "Whether the service is enabled.",
      "defaultValue": true
    },
    {
      "name": "my.service.max-retries",
      "type": "java.lang.Integer",
      "description": "Maximum number of retry attempts.",
      "defaultValue": 3
    }
  ]
}
```

## 事件驱动架构

### 自定义事件

```java
// 用户注册事件
public class UserRegistrationEvent extends ApplicationEvent {
    private final User user;
    
    public UserRegistrationEvent(Object source, User user) {
        super(source);
        this.user = user;
    }
    
    public User getUser() {
        return user;
    }
}

// 订单创建事件
public class OrderCreatedEvent extends ApplicationEvent {
    private final Order order;
    private final String userId;
    
    public OrderCreatedEvent(Object source, Order order, String userId) {
        super(source);
        this.order = order;
        this.userId = userId;
    }
    
    public Order getOrder() { return order; }
    public String getUserId() { return userId; }
}
```

### 事件监听器

```java
@Component
public class EventListeners {
    
    private static final Logger logger = LoggerFactory.getLogger(EventListeners.class);
    
    @EventListener
    @Async
    public void handleUserRegistration(UserRegistrationEvent event) {
        User user = event.getUser();
        logger.info("Processing user registration for: {}", user.getUsername());
        
        // 异步处理用户注册后续操作
        processUserRegistration(user);
    }
    
    @EventListener
    @Order(1) // 指定执行顺序
    public void handleOrderCreated(OrderCreatedEvent event) {
        Order order = event.getOrder();
        logger.info("Processing order creation: {}", order.getId());
        
        // 发送订单确认邮件
        sendOrderConfirmation(order);
    }
    
    @EventListener
    @Order(2) // 在订单确认后执行
    public void handleOrderCreatedSecond(OrderCreatedEvent event) {
        Order order = event.getOrder();
        logger.info("Updating user stats for order: {}", order.getId());
        
        // 更新用户统计信息
        updateUserStats(event.getUserId());
    }
    
    // 条件事件监听
    @EventListener(condition = "#event.order.getAmount() > 1000")
    public void handleLargeOrder(OrderCreatedEvent event) {
        Order order = event.getOrder();
        logger.info("Large order detected: {} with amount: {}", 
            order.getId(), order.getAmount());
        
        // 触发额外的验证流程
        triggerAdditionalValidation(order);
    }
    
    // 监听多种事件类型
    @EventListener
    public void handleAnyEvent(ApplicationEvent event) {
        if (event instanceof UserRegistrationEvent) {
            logger.info("User registration event received");
        } else if (event instanceof OrderCreatedEvent) {
            logger.info("Order created event received");
        }
    }
    
    private void processUserRegistration(User user) {
        // 实现用户注册后的处理逻辑
        logger.info("User registration processed for: {}", user.getUsername());
    }
    
    private void sendOrderConfirmation(Order order) {
        // 发送订单确认逻辑
        logger.info("Order confirmation sent for: {}", order.getId());
    }
    
    private void updateUserStats(String userId) {
        // 更新用户统计
        logger.info("User stats updated for: {}", userId);
    }
    
    private void triggerAdditionalValidation(Order order) {
        // 额外验证逻辑
        logger.info("Additional validation triggered for order: {}", order.getId());
    }
}
```

### 事件发布服务

```java
@Service
public class EventPublisherService {
    
    @Autowired
    private ApplicationEventPublisher eventPublisher;
    
    public void publishUserRegistrationEvent(User user) {
        UserRegistrationEvent event = new UserRegistrationEvent(this, user);
        eventPublisher.publishEvent(event);
    }
    
    public void publishOrderCreatedEvent(Order order, String userId) {
        OrderCreatedEvent event = new OrderCreatedEvent(this, order, userId);
        eventPublisher.publishEvent(event);
    }
    
    // 批量发布事件
    public void publishMultipleEvents(List<ApplicationEvent> events) {
        events.forEach(eventPublisher::publishEvent);
    }
    
    // 带事务的事件发布
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleAfterCommit(OrderCreatedEvent event) {
        // 仅在事务成功提交后执行
        logger.info("Order processed after transaction commit: {}", event.getOrder().getId());
    }
    
    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void handleAfterRollback(OrderCreatedEvent event) {
        // 仅在事务回滚后执行
        logger.warn("Order processing rolled back: {}", event.getOrder().getId());
    }
}
```

## 条件化配置

### 自定义条件注解

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Conditional(OnCloudPlatformCondition.class)
public @interface ConditionalOnCloudPlatform {
    CloudPlatform value();
}

public enum CloudPlatform {
    CLOUD_FOUNDRY, KUBERNETES, HEROKU
}

class OnCloudPlatformCondition implements Condition {
    
    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        String platform = context.getEnvironment()
            .getProperty("cloud.platform", CloudPlatform.class, CloudPlatform.CLOUD_FOUNDRY)
            .name();
        
        Map<String, Object> attributes = metadata
            .getAnnotationAttributes(ConditionalOnCloudPlatform.class.getName());
        CloudPlatform requiredPlatform = (CloudPlatform) attributes.get("value");
        
        return platform.equalsIgnoreCase(requiredPlatform.name());
    }
}
```

### 复杂条件配置

```java
@Configuration
public class ConditionalConfig {
    
    // 基于类路径存在特定类的条件
    @Bean
    @ConditionalOnClass(RedisTemplate.class)
    public RedisService redisService() {
        return new RedisServiceImpl();
    }
    
    // 基于缺少特定类的条件
    @Bean
    @ConditionalOnMissingClass("org.springframework.data.redis.core.RedisTemplate")
    public InMemoryService inMemoryService() {
        return new InMemoryServiceImpl();
    }
    
    // 基于属性存在的条件
    @Bean
    @ConditionalOnProperty(name = "my.custom.feature.enabled", havingValue = "true", matchIfMissing = false)
    public CustomFeatureService customFeatureService() {
        return new CustomFeatureServiceImpl();
    }
    
    // 基于Bean存在的条件
    @Bean
    @ConditionalOnBean(name = "dataSource")
    public DatabaseService databaseService() {
        return new DatabaseServiceImpl();
    }
    
    // 基于缺少Bean的条件
    @Bean
    @ConditionalOnMissingBean
    public DefaultService defaultService() {
        return new DefaultServiceImpl();
    }
    
    // 组合条件
    @Bean
    @ConditionalOnProperty(prefix = "cache", name = "type", havingValue = "redis")
    @ConditionalOnClass(RedisTemplate.class)
    public CacheService redisCacheService() {
        return new RedisCacheServiceImpl();
    }
}
```

## 国际化和本地化

### 消息资源文件

```properties
# src/main/resources/messages.properties
welcome.message=Welcome to our application
user.not.found=User not found
validation.required=This field is required
validation.email=Please enter a valid email address

# src/main/resources/messages_zh.properties
welcome.message=\u6B22\u8FCE\u4F7F\u7528\u6211\u4EEC\u7684\u5E94\u7528
user.not.found=\u7528\u6237\u4E0D\u5B58\u5728
validation.required=\u8FD9\u4E2A\u5B57\u6BB5\u662F\u5FC5\u586B\u7684
validation.email=\u8BF7\u8F93\u5165\u4E00\u4E2A\u6709\u6548\u7684\u90AE\u7BB1\u5730\u5740

# src/main/resources/messages_en.properties
welcome.message=Welcome to our application
user.not.found=User not found
validation.required=This field is required
validation.email=Please enter a valid email address
```

### 国际化配置

```java
@Configuration
public class I18nConfig {
    
    @Bean
    public MessageSource messageSource() {
        ReloadableResourceBundleMessageSource messageSource = 
            new ReloadableResourceBundleMessageSource();
        messageSource.setBasename("classpath:messages");
        messageSource.setDefaultEncoding("UTF-8");
        messageSource.setCacheSeconds(10); // 设置缓存时间，0表示不缓存
        messageSource.setFallbackToSystemLocale(false);
        return messageSource;
    }
    
    @Bean
    public LocaleResolver localeResolver() {
        SessionLocaleResolver resolver = new SessionLocaleResolver();
        resolver.setDefaultLocale(Locale.ENGLISH);
        return resolver;
    }
    
    @Bean
    public LocaleChangeInterceptor localeChangeInterceptor() {
        LocaleChangeInterceptor interceptor = new LocaleChangeInterceptor();
        interceptor.setParamName("lang");
        return interceptor;
    }
    
    @Bean
    public WebMvcConfigurer webMvcConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addInterceptors(InterceptorRegistry registry) {
                registry.addInterceptor(localeChangeInterceptor());
            }
        };
    }
}
```

### 国际化服务

```java
@Service
public class I18nService {
    
    @Autowired
    private MessageSource messageSource;
    
    @Autowired
    private LocaleResolver localeResolver;
    
    public String getMessage(String code, Locale locale) {
        return messageSource.getMessage(code, null, locale);
    }
    
    public String getMessage(String code, Object[] args, Locale locale) {
        return messageSource.getMessage(code, args, locale);
    }
    
    public String getMessage(String code, HttpServletRequest request) {
        Locale locale = localeResolver.resolveLocale(request);
        return messageSource.getMessage(code, null, locale);
    }
    
    public String getLocalizedMessage(String code, Object[] args, HttpServletRequest request) {
        Locale locale = localeResolver.resolveLocale(request);
        return messageSource.getMessage(code, args, locale, locale);
    }
}
```

## 自定义验证注解

### 自定义验证注解

```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = StrongPasswordValidator.class)
@Documented
public @interface StrongPassword {
    String message() default "Password must contain at least one uppercase, one lowercase, one number and one special character";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

// 验证器实现
public class StrongPasswordValidator implements ConstraintValidator<StrongPassword, String> {
    
    private static final String PASSWORD_PATTERN = 
        "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#&()–[{}]:;',?/*~$^+=<>]).{8,}$";
    
    private Pattern pattern = Pattern.compile(PASSWORD_PATTERN);
    
    @Override
    public boolean isValid(String password, ConstraintValidatorContext context) {
        if (password == null) {
            return false;
        }
        
        Matcher matcher = pattern.matcher(password);
        return matcher.matches();
    }
}
```

### 使用自定义验证

```java
public class UserRegistrationDto {
    
    @NotBlank(message = "{validation.username.required}")
    @Size(min = 3, max = 50, message = "{validation.username.size}")
    private String username;
    
    @Email(message = "{validation.email.format}")
    @NotBlank(message = "{validation.email.required}")
    private String email;
    
    @StrongPassword
    private String password;
    
    @AssertTrue(message = "{validation.terms.accepted}")
    private boolean termsAccepted;
    
    // constructors, getters and setters
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    
    public boolean isTermsAccepted() { return termsAccepted; }
    public void setTermsAccepted(boolean termsAccepted) { this.termsAccepted = termsAccepted; }
}
```

## 函数式编程

### 函数式端点

```java
@Configuration
public class RouterConfig {
    
    @Bean
    public RouterFunction<ServerResponse> route(UserHandler userHandler) {
        return RouterFunctions
            .route(RequestPredicates.GET("/api/users"), userHandler::getAllUsers)
            .andRoute(RequestPredicates.GET("/api/users/{id}"), userHandler::getUserById)
            .andRoute(RequestPredicates.POST("/api/users"), userHandler::createUser)
            .andRoute(RequestPredicates.PUT("/api/users/{id}"), userHandler::updateUser)
            .andRoute(RequestPredicates.DELETE("/api/users/{id}"), userHandler::deleteUser);
    }
}

@Component
public class UserHandler {
    
    @Autowired
    private UserService userService;
    
    public ServerResponse getAllUsers(ServerRequest request) {
        Flux<User> users = userService.findAll();
        return ServerResponse.ok()
            .contentType(MediaType.APPLICATION_JSON)
            .body(users, User.class);
    }
    
    public ServerResponse getUserById(ServerRequest request) {
        String id = request.pathVariable("id");
        Mono<User> user = userService.findById(id);
        return ServerResponse.ok()
            .contentType(MediaType.APPLICATION_JSON)
            .body(user, User.class);
    }
    
    public ServerResponse createUser(ServerRequest request) {
        Mono<User> userMono = request.bodyToMono(User.class);
        Mono<User> savedUser = userMono.flatMap(userService::save);
        
        return ServerResponse.status(HttpStatus.CREATED)
            .contentType(MediaType.APPLICATION_JSON)
            .body(savedUser, User.class);
    }
    
    public ServerResponse updateUser(ServerRequest request) {
        String id = request.pathVariable("id");
        Mono<User> userMono = request.bodyToMono(User.class);
        
        Mono<User> updatedUser = userMono.flatMap(user -> 
            userService.findById(id)
                .flatMap(existingUser -> {
                    existingUser.setName(user.getName());
                    existingUser.setEmail(user.getEmail());
                    return userService.save(existingUser);
                }));
        
        return ServerResponse.ok()
            .contentType(MediaType.APPLICATION_JSON)
            .body(updatedUser, User.class);
    }
    
    public ServerResponse deleteUser(ServerRequest request) {
        String id = request.pathVariable("id");
        Mono<Void> deletion = userService.deleteById(id);
        
        return ServerResponse.ok()
            .build(deletion);
    }
}
```

## AOP 高级应用

### 自定义切面

```java
@Aspect
@Component
public class LoggingAspect {
    
    private static final Logger logger = LoggerFactory.getLogger(LoggingAspect.class);
    
    // 方法执行时间统计
    @Around("@annotation(LogExecutionTime)")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long startTime = System.currentTimeMillis();
        Object result;
        
        try {
            result = joinPoint.proceed();
        } finally {
            long endTime = System.currentTimeMillis();
            long executionTime = endTime - startTime;
            
            String className = joinPoint.getTarget().getClass().getSimpleName();
            String methodName = joinPoint.getSignature().getName();
            
            logger.info("Method {}#{} executed in {} ms", 
                className, methodName, executionTime);
        }
        
        return result;
    }
    
    // 参数日志记录
    @Before("@annotation(LogParameters)")
    public void logParameters(JoinPoint joinPoint) {
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        
        logger.info("Method {}#{} called with parameters: {}", 
            className, methodName, Arrays.toString(args));
    }
    
    // 返回值日志记录
    @AfterReturning(pointcut = "@annotation(LogResult)", returning = "result")
    public void logResult(JoinPoint joinPoint, Object result) {
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        
        logger.info("Method {}#{} returned: {}", className, methodName, result);
    }
    
    // 异常日志记录
    @AfterThrowing(pointcut = "@annotation(LogExceptions)", throwing = "exception")
    public void logException(JoinPoint joinPoint, Exception exception) {
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        
        logger.error("Method {}#{} threw exception: {}", 
            className, methodName, exception.getMessage(), exception);
    }
}

// 自定义注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface LogExecutionTime {
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface LogParameters {
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface LogResult {
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface LogExceptions {
}
```

### 使用自定义注解

```java
@Service
public class BusinessService {
    
    @LogExecutionTime
    @LogParameters
    @LogResult
    @LogExceptions
    public User processUser(String userId) {
        // 模拟业务处理
        try {
            Thread.sleep(100); // 模拟处理时间
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        User user = new User();
        user.setId(userId);
        user.setName("Processed User");
        return user;
    }
    
    @LogExecutionTime
    public List<User> processUsers(List<String> userIds) {
        return userIds.stream()
            .map(this::processUser)
            .collect(Collectors.toList());
    }
}
```