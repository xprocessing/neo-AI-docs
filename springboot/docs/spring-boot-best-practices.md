# Spring Boot 最佳实践总结

本章总结了在使用 Spring Boot 开发应用程序时的最佳实践，涵盖项目结构、代码组织、性能优化、安全实践等方面。

## 项目结构最佳实践

### 推荐的项目结构

```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── example/
│   │           └── demo/
│   │               ├── DemoApplication.java
│   │               ├── controller/          # 控制器层
│   │               │   ├── advice/          # 全局异常处理
│   │               │   └── dto/             # 数据传输对象
│   │               ├── service/             # 业务逻辑层
│   │               │   ├── impl/            # 服务实现类
│   │               │   └── dto/             # 业务数据对象
│   │               ├── repository/          # 数据访问层
│   │               ├── model/               # 实体类
│   │               ├── config/              # 配置类
│   │               ├── util/                # 工具类
│   │               └── exception/           # 自定义异常
│   ├── resources/
│   │   ├── application.yml                # 主配置文件
│   │   ├── application-dev.yml            # 开发环境配置
│   │   ├── application-test.yml           # 测试环境配置
│   │   ├── application-prod.yml           # 生产环境配置
│   │   ├── static/                        # 静态资源
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── images/
│   │   └── templates/                     # 模板文件
│   │       ├── fragments/                 # 模板片段
│   │       └── pages/                     # 页面模板
└── test/
    └── java/
        └── com/
            └── example/
                └── demo/
                    ├── controller/
                    ├── service/
                    └── repository/
```

### 包命名规范

```java
// 推荐的包结构
package com.example.projectname;

// 按功能模块组织
com.example.ecommerce.user
com.example.ecommerce.product
com.example.ecommerce.order
com.example.ecommerce.payment

// 或按层次组织
com.example.ecommerce.controller
com.example.ecommerce.service
com.example.ecommerce.repository
com.example.ecommerce.model
```

## 配置管理最佳实践

### 外部化配置

```yaml
# application.yml - 主配置文件
spring:
  application:
    name: my-spring-boot-app
  profiles:
    active: dev
  datasource:
    # 数据库配置使用环境变量
    url: ${DATABASE_URL:jdbc:h2:mem:testdb}
    username: ${DATABASE_USERNAME:sa}
    password: ${DATABASE_PASSWORD:}
  jpa:
    hibernate:
      ddl-auto: ${JPA_DDL_AUTO:validate}
    show-sql: ${JPA_SHOW_SQL:false}

# 配置属性类
@ConfigurationProperties(prefix = "app.feature")
@Component
public class FeatureProperties {
    private boolean newFeatureEnabled = false;
    private int maxUploadSize = 10485760; // 10MB
    private Map<String, String> settings = new HashMap<>();
    
    // getters and setters
    public boolean isNewFeatureEnabled() { return newFeatureEnabled; }
    public void setNewFeatureEnabled(boolean newFeatureEnabled) { this.newFeatureEnabled = newFeatureEnabled; }
    
    public int getMaxUploadSize() { return maxUploadSize; }
    public void setMaxUploadSize(int maxUploadSize) { this.maxUploadSize = maxUploadSize; }
    
    public Map<String, String> getSettings() { return settings; }
    public void setSettings(Map<String, String> settings) { this.settings = settings; }
}
```

### 配置验证

```java
@ConfigurationProperties(prefix = "app.mail")
@Validated
@Component
public class MailProperties {
    
    @NotBlank
    private String host;
    
    @Min(1)
    @Max(65535)
    private int port = 587;
    
    @Email
    private String from;
    
    @AssertTrue(message = "SSL must be enabled for port 465")
    private boolean validatePortAndSsl() {
        return port != 465 || isSslEnabled();
    }
    
    private boolean sslEnabled = false;
    
    // getters and setters
    public String getHost() { return host; }
    public void setHost(String host) { this.host = host; }
    
    public int getPort() { return port; }
    public void setPort(int port) { this.port = port; }
    
    public String getFrom() { return from; }
    public void setFrom(String from) { this.from = from; }
    
    public boolean isSslEnabled() { return sslEnabled; }
    public void setSslEnabled(boolean sslEnabled) { this.sslEnabled = sslEnabled; }
}
```

## 数据访问最佳实践

### Repository 层最佳实践

```java
// 使用接口定义查询方法
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 方法名查询 - 简单查询
    List<User> findByEmail(String email);
    List<User> findByActiveTrue();
    List<User> findByEmailContainingIgnoreCase(String email);
    
    // 自定义查询 - 复杂查询
    @Query("SELECT u FROM User u WHERE u.createdAt > :date AND u.active = true")
    List<User> findActiveUsersCreatedAfter(@Param("date") LocalDateTime date);
    
    // 原生查询 - 需要复杂SQL时使用
    @Query(value = "SELECT * FROM users u WHERE u.last_login > ?1", nativeQuery = true)
    List<User> findRecentActiveUsers(LocalDateTime lastLoginDate);
    
    // 分页查询
    Page<User> findByRole(UserRole role, Pageable pageable);
    
    // 更新查询
    @Modifying
    @Query("UPDATE User u SET u.lastLogin = :loginTime WHERE u.id = :userId")
    int updateLastLogin(@Param("userId") Long userId, @Param("loginTime") LocalDateTime loginTime);
    
    // 批量操作
    @Modifying
    @Query("UPDATE User u SET u.active = false WHERE u.lastLogin < :cutoffDate")
    int deactivateInactiveUsers(@Param("cutoffDate") LocalDateTime cutoffDate);
}

// Repository 实现类 - 处理复杂业务逻辑
@Repository
public class UserRepositoryImpl implements UserRepositoryCustom {
    
    @PersistenceContext
    private EntityManager entityManager;
    
    @Override
    public List<User> findUsersWithCustomCriteria(UserSearchCriteria criteria) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> root = query.from(User.class);
        
        List<Predicate> predicates = new ArrayList<>();
        
        if (criteria.getMinAge() != null) {
            predicates.add(cb.greaterThanOrEqualTo(root.get("age"), criteria.getMinAge()));
        }
        
        if (criteria.getEmailDomain() != null) {
            predicates.add(cb.like(root.get("email"), "%" + criteria.getEmailDomain()));
        }
        
        query.where(predicates.toArray(new Predicate[0]));
        
        return entityManager.createQuery(query).getResultList();
    }
}

// 自定义接口
public interface UserRepositoryCustom {
    List<User> findUsersWithCustomCriteria(UserSearchCriteria criteria);
}

// 主 Repository 接口继承自定义接口
public interface UserRepository extends JpaRepository<User, Long>, UserRepositoryCustom {
    // 继承所有方法
}
```

### Service 层最佳实践

```java
@Service
@Transactional(readOnly = true)  // 默认只读事务
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    @Autowired
    private EmailService emailService;
    
    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }
    
    public List<User> findAll() {
        return userRepository.findAll();
    }
    
    @Transactional  // 读写事务
    public User save(User user) {
        if (user.getId() == null) {
            user.setPassword(passwordEncoder.encode(user.getPassword()));
            user.setCreatedAt(LocalDateTime.now());
        } else {
            user.setUpdatedAt(LocalDateTime.now());
        }
        User savedUser = userRepository.save(user);
        
        // 异步发送通知
        CompletableFuture.runAsync(() -> 
            emailService.sendWelcomeEmail(savedUser.getEmail(), savedUser.getUsername()));
        
        return savedUser;
    }
    
    @Transactional
    public void deleteById(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
        
        // 软删除而不是硬删除
        user.setActive(false);
        user.setDeletedAt(LocalDateTime.now());
        userRepository.save(user);
    }
    
    @Transactional
    public User updateEmail(Long userId, String newEmail) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + userId));
        
        user.setEmail(newEmail);
        user.setUpdatedAt(LocalDateTime.now());
        
        return userRepository.save(user);
    }
    
    // 批量操作
    @Transactional
    public void batchUpdateUsers(List<UserUpdateRequest> updateRequests) {
        for (UserUpdateRequest request : updateRequests) {
            updateEmail(request.getUserId(), request.getNewEmail());
        }
    }
    
    // 事务传播示例
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logUserAction(Long userId, String action) {
        // 在新的事务中记录用户操作
        UserActionLog log = new UserActionLog();
        log.setUserId(userId);
        log.setAction(action);
        log.setTimestamp(LocalDateTime.now());
        // 保存日志，即使主事务回滚也保留
    }
}
```

## 安全最佳实践

### 认证和授权

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())  // 在 REST API 中禁用 CSRF
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))  // 无状态会话
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/public/**", "/api/auth/**", "/health", "/info").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.POST, "/api/users").hasRole("USER")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(withDefaults()))  // JWT 认证
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(new CustomAuthenticationEntryPoint())
                .accessDeniedHandler(new CustomAccessDeniedHandler()));
        
        return http.build();
    }
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);  // 使用更强的加密强度
    }
    
    @Bean
    public UserDetailsService userDetailsService() {
        return new CustomUserDetailsService();
    }
}

// 自定义权限评估器
@Component("permissionEvaluator")
public class CustomPermissionEvaluator implements PermissionEvaluator {
    
    @Override
    public boolean hasPermission(Authentication authentication, Object targetDomainObject, Object permission) {
        if (authentication == null || targetDomainObject == null || permission == null) {
            return false;
        }
        
        String username = authentication.getName();
        String perm = permission.toString();
        
        if (targetDomainObject instanceof User) {
            User user = (User) targetDomainObject;
            return hasUserPermission(username, user, perm);
        }
        
        return false;
    }
    
    private boolean hasUserPermission(String username, User targetUser, String permission) {
        // 实现自定义权限逻辑
        if ("read".equals(permission)) {
            return true; // 所有用户可读
        } else if ("write".equals(permission)) {
            return username.equals(targetUser.getUsername()); // 只能修改自己的信息
        } else if ("delete".equals(permission)) {
            return "ADMIN".equals(getUserRole(username)); // 只有管理员可删除
        }
        
        return false;
    }
    
    private String getUserRole(String username) {
        // 获取用户角色的逻辑
        return "USER";
    }
    
    @Override
    public boolean hasPermission(Authentication authentication, Serializable targetId, 
                               String targetType, Object permission) {
        return false;
    }
}
```

## 性能优化最佳实践

### 缓存策略

```java
@Service
public class CachedUserService {
    
    @Autowired
    private UserRepository userRepository;
    
    // 频繁读取的数据使用缓存
    @Cacheable(value = "users", key = "#id", unless = "#result == null")
    public User findById(Long id) {
        return userRepository.findById(id).orElse(null);
    }
    
    // 更新时清除缓存
    @CacheEvict(value = "users", key = "#user.id")
    @Transactional
    public User update(User user) {
        return userRepository.save(user);
    }
    
    // 批量操作后清除相关缓存
    @Caching(
        evict = {
            @CacheEvict(value = "users", allEntries = true),
            @CacheEvict(value = "userSummaries", allEntries = true)
        }
    )
    @Transactional
    public void updateUserRole(Long userId, String newRole) {
        userRepository.updateRole(userId, newRole);
    }
    
    // 使用缓存优化复杂查询
    @Cacheable(value = "userStatistics", key = "'summary_' + #period")
    public UserStatistics getStatistics(String period) {
        // 复杂的统计查询
        return calculateUserStatistics(period);
    }
    
    private UserStatistics calculateUserStatistics(String period) {
        // 统计逻辑
        return new UserStatistics();
    }
}
```

### 数据库优化

```java
@Repository
public class OptimizedUserRepository {
    
    @PersistenceContext
    private EntityManager entityManager;
    
    // 使用投影减少数据传输
    @Query("SELECT new com.example.dto.UserSummaryDto(u.id, u.username, u.email, u.createdAt) FROM User u WHERE u.active = true")
    List<UserSummaryDto> findActiveUserSummaries();
    
    // 使用 JOIN FETCH 优化 N+1 查询
    @Query("SELECT DISTINCT u FROM User u LEFT JOIN FETCH u.roles WHERE u.active = true")
    List<User> findActiveUsersWithRoles();
    
    // 批量操作
    @Modifying
    @Query("UPDATE User u SET u.lastLogin = :loginTime WHERE u.id IN :userIds")
    int batchUpdateLastLogin(@Param("userIds") List<Long> userIds, 
                           @Param("loginTime") LocalDateTime loginTime);
    
    // 使用原生查询优化复杂统计
    @Query(value = "SELECT u.role, COUNT(*) as count FROM users u WHERE u.active = true GROUP BY u.role", 
           nativeQuery = true)
    List<Object[]> getUserRoleStatistics();
    
    // 分页查询优化
    public Page<User> findUsersWithCriteria(UserSearchCriteria criteria, Pageable pageable) {
        // 使用 Criteria API 构建动态查询
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> root = query.from(User.class);
        
        List<Predicate> predicates = buildPredicates(cb, root, criteria);
        query.where(predicates.toArray(new Predicate[0]));
        query.orderBy(cb.desc(root.get("createdAt")));
        
        // 获取总数
        CriteriaQuery<Long> countQuery = cb.createQuery(Long.class);
        Root<User> countRoot = countQuery.from(User.class);
        countQuery.select(cb.count(countRoot)).where(predicates.toArray(new Predicate[0]));
        long total = entityManager.createQuery(countQuery).getSingleResult();
        
        // 获取数据
        List<User> users = entityManager.createQuery(query)
            .setFirstResult((int) pageable.getOffset())
            .setMaxResults(pageable.getPageSize())
            .getResultList();
        
        return new PageImpl<>(users, pageable, total);
    }
    
    private List<Predicate> buildPredicates(CriteriaBuilder cb, Root<User> root, UserSearchCriteria criteria) {
        List<Predicate> predicates = new ArrayList<>();
        
        if (criteria.getActive() != null) {
            predicates.add(cb.equal(root.get("active"), criteria.getActive()));
        }
        
        if (criteria.getRole() != null) {
            predicates.add(cb.equal(root.get("role"), criteria.getRole()));
        }
        
        if (criteria.getCreatedAtAfter() != null) {
            predicates.add(cb.greaterThanOrEqualTo(root.get("createdAt"), criteria.getCreatedAtAfter()));
        }
        
        return predicates;
    }
}
```

## 测试最佳实践

### 分层测试策略

```java
// 单元测试 - 测试业务逻辑
@ExtendWith(MockitoExtension.class)
class UserServiceUnitTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private PasswordEncoder passwordEncoder;
    
    @InjectMocks
    private UserService userService;
    
    @Test
    @DisplayName("创建用户 - 成功")
    void createUser_Success() {
        // 准备测试数据
        User inputUser = new User();
        inputUser.setUsername("testuser");
        inputUser.setEmail("test@example.com");
        inputUser.setPassword("password");
        
        User savedUser = new User();
        savedUser.setId(1L);
        savedUser.setUsername("testuser");
        savedUser.setEmail("test@example.com");
        
        when(passwordEncoder.encode(anyString())).thenReturn("encoded_password");
        when(userRepository.save(any(User.class))).thenReturn(savedUser);
        
        // 执行测试
        User result = userService.save(inputUser);
        
        // 验证结果
        assertThat(result).isNotNull();
        assertThat(result.getId()).isNotNull();
        verify(passwordEncoder).encode("password");
        verify(userRepository).save(any(User.class));
    }
}

// 集成测试 - 测试数据访问
@DataJpaTest
class UserRepositoryIntegrationTest {
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    @DisplayName("保存和查找用户")
    void saveAndFindUser() {
        // 准备测试数据
        User user = new User();
        user.setUsername("testuser");
        user.setEmail("test@example.com");
        user.setActive(true);
        
        // 执行保存
        User savedUser = userRepository.save(user);
        entityManager.flush();
        
        // 验证保存
        assertThat(savedUser.getId()).isNotNull();
        assertThat(savedUser.getUsername()).isEqualTo("testuser");
        
        // 验证查找
        Optional<User> foundUser = userRepository.findById(savedUser.getId());
        assertThat(foundUser).isPresent();
        assertThat(foundUser.get().getUsername()).isEqualTo("testuser");
    }
}

// 端到端测试 - 测试 Web 层
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class UserControllerE2ETest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @LocalServerPort
    private int port;
    
    @Test
    @DisplayName("创建用户 API 测试")
    void createUserApiTest() {
        // 准备测试数据
        UserCreateRequest request = new UserCreateRequest();
        request.setUsername("apitestuser");
        request.setEmail("api@example.com");
        request.setPassword("password123");
        
        // 执行请求
        ResponseEntity<UserResponse> response = restTemplate
            .postForEntity("/api/users", request, UserResponse.class);
        
        // 验证响应
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getUsername()).isEqualTo("apitestuser");
    }
}
```

## 监控和日志最佳实践

### 结构化日志

```java
@Service
public class UserServiceWithLogging {
    
    private static final Logger logger = LoggerFactory.getLogger(UserServiceWithLogging.class);
    
    private final MeterRegistry meterRegistry;
    
    public UserServiceWithLogging(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }
    
    public User findById(Long id) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            User user = userRepository.findById(id).orElse(null);
            
            if (user != null) {
                logger.info("User found - ID: {}, Username: {}", id, user.getUsername());
                meterRegistry.counter("user.find.success").increment();
            } else {
                logger.warn("User not found - ID: {}", id);
                meterRegistry.counter("user.find.not_found").increment();
            }
            
            return user;
        } catch (Exception e) {
            logger.error("Error finding user - ID: {}", id, e);
            meterRegistry.counter("user.find.error").increment(
                Tags.of("error", e.getClass().getSimpleName()));
            throw e;
        } finally {
            sample.stop(Timer.builder("user.find.duration")
                .register(meterRegistry));
        }
    }
    
    @Retryable(value = {DataAccessException.class}, maxAttempts = 3, backoff = @Backoff(delay = 1000))
    public User saveWithRetry(User user) {
        try {
            User savedUser = userRepository.save(user);
            logger.info("User saved successfully - ID: {}", savedUser.getId());
            return savedUser;
        } catch (DataAccessException e) {
            logger.error("Database error saving user - Username: {}", user.getUsername(), e);
            throw e;
        }
    }
    
    @Recover
    public User recoverFromSaveFailure(DataAccessException e, User user) {
        logger.error("Failed to save user after retries - Username: {}", user.getUsername(), e);
        throw new UserServiceException("Could not save user after multiple attempts", e);
    }
}
```

## 部署和运维最佳实践

### 健康检查和监控

```java
@Component
public class ApplicationHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    @Override
    public Health health() {
        // 检查数据库连接
        boolean dbHealthy = checkDatabaseHealth();
        // 检查 Redis 连接
        boolean redisHealthy = checkRedisHealth();
        
        Health.Builder builder = dbHealthy && redisHealthy ? Health.up() : Health.down();
        
        return builder
            .withDetail("database", dbHealthy ? "Available" : "Unavailable")
            .withDetail("redis", redisHealthy ? "Available" : "Unavailable")
            .withDetail("timestamp", Instant.now())
            .build();
    }
    
    private boolean checkDatabaseHealth() {
        try (Connection connection = dataSource.getConnection()) {
            return connection.isValid(2);
        } catch (SQLException e) {
            return false;
        }
    }
    
    private boolean checkRedisHealth() {
        try {
            redisTemplate.opsForValue().get("health-check-key");
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}

// 自定义指标收集
@Component
public class BusinessMetricsCollector {
    
    private final MeterRegistry meterRegistry;
    
    public BusinessMetricsCollector(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }
    
    public void recordUserRegistration(String source) {
        Counter.builder("user.registrations")
            .description("Number of user registrations")
            .tags("source", source)
            .register(meterRegistry)
            .increment();
    }
    
    public <T> T timeOperation(String operationName, Supplier<T> operation) {
        return Timer.builder("business.operation.duration")
            .description("Business operation duration")
            .tag("operation", operationName)
            .register(meterRegistry)
            .recordCallable(operation::get);
    }
}
```

## 代码质量最佳实践

### 统一异常处理

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFoundException(UserNotFoundException e) {
        logger.warn("User not found: {}", e.getMessage());
        ErrorResponse error = new ErrorResponse("USER_NOT_FOUND", e.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(MethodArgumentNotValidException e) {
        Map<String, String> errors = new HashMap<>();
        e.getBindingResult().getFieldErrors().forEach(error -> 
            errors.put(error.getField(), error.getDefaultMessage()));
        
        logger.warn("Validation failed: {}", errors);
        ErrorResponse error = new ErrorResponse("VALIDATION_ERROR", "Validation failed", errors);
        return ResponseEntity.badRequest().body(error);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception e) {
        logger.error("Unexpected error occurred", e);
        ErrorResponse error = new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}

// 统一响应格式
public class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;
    private long timestamp;
    
    public static <T> ApiResponse<T> success(T data) {
        ApiResponse<T> response = new ApiResponse<>();
        response.success = true;
        response.data = data;
        response.timestamp = System.currentTimeMillis();
        return response;
    }
    
    public static <T> ApiResponse<T> error(String message) {
        ApiResponse<T> response = new ApiResponse<>();
        response.success = false;
        response.message = message;
        response.timestamp = System.currentTimeMillis();
        return response;
    }
    
    // getters and setters
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public T getData() { return data; }
    public void setData(T data) { this.data = data; }
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
}
```

## 总结

Spring Boot 开发的最佳实践涵盖了以下关键方面：

1. **项目结构**：采用清晰的分层架构和包组织
2. **配置管理**：使用外部化配置和属性验证
3. **数据访问**：优化 Repository 和 Service 层实现
4. **安全性**：实施全面的安全措施
5. **性能优化**：使用缓存、数据库优化等技术
6. **测试策略**：实施分层测试方法
7. **监控日志**：实现结构化日志和指标收集
8. **代码质量**：统一异常处理和响应格式

遵循这些最佳实践可以构建出高质量、可维护、可扩展的 Spring Boot 应用程序。