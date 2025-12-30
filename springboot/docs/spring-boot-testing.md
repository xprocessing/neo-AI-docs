# Spring Boot 测试

Spring Boot 提供了强大的测试支持，包括单元测试、集成测试和端到端测试。本章将详细介绍各种测试技术。

## 测试依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

## 单元测试

### 业务逻辑测试

```java
// 被测试的业务类
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public User createUser(String username, String email) {
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("Username cannot be empty");
        }
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Invalid email format");
        }
        
        User user = new User();
        user.setUsername(username);
        user.setEmail(email);
        return userRepository.save(user);
    }
    
    public Optional<User> findUserById(Long id) {
        return userRepository.findById(id);
    }
    
    public List<User> findAllUsers() {
        return userRepository.findAll();
    }
}

// 单元测试
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @InjectMocks
    private UserService userService;
    
    @Test
    @DisplayName("创建用户 - 成功")
    void createUser_Success() {
        // 准备测试数据
        String username = "testuser";
        String email = "test@example.com";
        
        User mockUser = new User();
        mockUser.setUsername(username);
        mockUser.setEmail(email);
        mockUser.setId(1L);
        
        when(userRepository.save(any(User.class))).thenReturn(mockUser);
        
        // 执行测试
        User result = userService.createUser(username, email);
        
        // 验证结果
        assertThat(result).isNotNull();
        assertThat(result.getUsername()).isEqualTo(username);
        assertThat(result.getEmail()).isEqualTo(email);
        verify(userRepository, times(1)).save(any(User.class));
    }
    
    @Test
    @DisplayName("创建用户 - 用户名为空时抛出异常")
    void createUser_UsernameEmpty_ThrowsException() {
        // 执行测试并验证异常
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.createUser("", "test@example.com")
        );
        
        assertThat(exception.getMessage()).isEqualTo("Username cannot be empty");
    }
    
    @Test
    @DisplayName("创建用户 - 邮箱格式错误时抛出异常")
    void createUser_InvalidEmail_ThrowsException() {
        // 执行测试并验证异常
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.createUser("testuser", "invalid-email")
        );
        
        assertThat(exception.getMessage()).isEqualTo("Invalid email format");
    }
    
    @Test
    @DisplayName("查找用户 - 存在用户")
    void findUserById_UserExists_ReturnsUser() {
        // 准备测试数据
        Long userId = 1L;
        User mockUser = new User();
        mockUser.setId(userId);
        mockUser.setUsername("testuser");
        
        when(userRepository.findById(userId)).thenReturn(Optional.of(mockUser));
        
        // 执行测试
        Optional<User> result = userService.findUserById(userId);
        
        // 验证结果
        assertThat(result).isPresent();
        assertThat(result.get().getId()).isEqualTo(userId);
        verify(userRepository, times(1)).findById(userId);
    }
    
    @Test
    @DisplayName("查找用户 - 用户不存在")
    void findUserById_UserNotExists_ReturnsEmpty() {
        // 准备测试数据
        Long userId = 1L;
        
        when(userRepository.findById(userId)).thenReturn(Optional.empty());
        
        // 执行测试
        Optional<User> result = userService.findUserById(userId);
        
        // 验证结果
        assertThat(result).isEmpty();
        verify(userRepository, times(1)).findById(userId);
    }
}
```

## Spring Boot 集成测试

### @SpringBootTest 注解

```java
@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE) // 使用实际数据库
class UserServiceIntegrationTest {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Test
    @DisplayName("集成测试 - 创建用户并保存到数据库")
    void createUser_SaveToDatabase() {
        // 准备测试数据
        String username = "integration_test";
        String email = "integration@test.com";
        
        // 执行测试
        User user = userService.createUser(username, email);
        
        // 验证结果
        assertThat(user.getId()).isNotNull();
        assertThat(user.getUsername()).isEqualTo(username);
        assertThat(user.getEmail()).isEqualTo(email);
        
        // 从数据库验证
        User savedUser = entityManager.find(User.class, user.getId());
        assertThat(savedUser).isNotNull();
        assertThat(savedUser.getUsername()).isEqualTo(username);
    }
}
```

### Web 层测试

```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Test
    @DisplayName("GET /api/users - 返回用户列表")
    void getAllUsers_ReturnsUserList() throws Exception {
        // 准备测试数据
        List<User> users = Arrays.asList(
            createUser("user1", "user1@example.com"),
            createUser("user2", "user2@example.com")
        );
        
        when(userService.findAllUsers()).thenReturn(users);
        
        // 执行请求
        mockMvc.perform(get("/api/users")
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].username", is("user1")))
                .andExpect(jsonPath("$[1].username", is("user2")));
    }
    
    @Test
    @DisplayName("POST /api/users - 创建新用户")
    void createUser_ValidUser_ReturnsCreatedUser() throws Exception {
        // 准备测试数据
        User inputUser = createUser("newuser", "newuser@example.com");
        User savedUser = createUser("newuser", "newuser@example.com");
        savedUser.setId(1L);
        
        when(userService.createUser(anyString(), anyString())).thenReturn(savedUser);
        
        // 执行请求
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(inputUser)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id", is(1)))
                .andExpect(jsonPath("$.username", is("newuser")));
    }
    
    @Test
    @DisplayName("POST /api/users - 创建用户时用户名为空返回错误")
    void createUser_EmptyUsername_ReturnsError() throws Exception {
        // 准备测试数据
        User invalidUser = createUser("", "test@example.com");
        
        // 执行请求
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidUser)))
                .andExpect(status().isBadRequest());
    }
    
    private User createUser(String username, String email) {
        User user = new User();
        user.setUsername(username);
        user.setEmail(email);
        return user;
    }
}
```

### 数据访问层测试

```java
@DataJpaTest
class UserRepositoryTest {
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    @DisplayName("根据用户名查找用户")
    void findByUsername_UserExists_ReturnsUser() {
        // 准备测试数据
        User user = new User();
        user.setUsername("testuser");
        user.setEmail("test@example.com");
        
        entityManager.persistAndFlush(user);
        
        // 执行测试
        Optional<User> found = userRepository.findByUsername("testuser");
        
        // 验证结果
        assertThat(found).isPresent();
        assertThat(found.get().getUsername()).isEqualTo("testuser");
        assertThat(found.get().getEmail()).isEqualTo("test@example.com");
    }
    
    @Test
    @DisplayName("根据邮箱包含内容查找用户")
    void findByEmailContaining_ReturnsMatchingUsers() {
        // 准备测试数据
        User user1 = new User();
        user1.setUsername("user1");
        user1.setEmail("test1@example.com");
        
        User user2 = new User();
        user2.setUsername("user2");
        user2.setEmail("test2@example.com");
        
        User user3 = new User();
        user3.setUsername("user3");
        user3.setEmail("other@gmail.com");
        
        entityManager.persist(user1);
        entityManager.persist(user2);
        entityManager.persist(user3);
        entityManager.flush();
        
        // 执行测试
        List<User> foundUsers = userRepository.findByEmailContaining("example.com");
        
        // 验证结果
        assertThat(foundUsers).hasSize(2);
        assertThat(foundUsers).extracting(User::getEmail)
            .contains("test1@example.com", "test2@example.com");
    }
    
    @Test
    @DisplayName("根据角色查找用户")
    void findByRole_ReturnsMatchingUsers() {
        // 准备测试数据
        User admin = new User();
        admin.setUsername("admin");
        admin.setEmail("admin@example.com");
        admin.setRole(UserRole.ADMIN);
        
        User user = new User();
        user.setUsername("regular_user");
        user.setEmail("user@example.com");
        user.setRole(UserRole.USER);
        
        entityManager.persist(admin);
        entityManager.persist(user);
        entityManager.flush();
        
        // 执行测试
        List<User> admins = userRepository.findByRole(UserRole.ADMIN);
        
        // 验证结果
        assertThat(admins).hasSize(1);
        assertThat(admins.get(0).getRole()).isEqualTo(UserRole.ADMIN);
        assertThat(admins.get(0).getUsername()).isEqualTo("admin");
    }
}
```

## 测试配置

### 测试专用配置

```java
@TestConfiguration
public class TestConfig {
    
    @Bean
    @Primary
    public EmailService emailServiceMock() {
        return Mockito.mock(EmailService.class);
    }
    
    @Bean
    @Primary
    public PaymentService paymentServiceMock() {
        return Mockito.mock(PaymentService.class);
    }
}
```

### 使用测试配置

```java
@SpringBootTest(classes = {MyApplication.class, TestConfig.class})
class ServiceWithExternalDependenciesTest {
    
    @Autowired
    private OrderService orderService;
    
    @MockBean
    private EmailService emailService;
    
    @MockBean
    private PaymentService paymentService;
    
    @Test
    @DisplayName("创建订单 - 成功处理")
    void createOrder_Success() {
        // 准备测试数据
        Order order = new Order();
        order.setAmount(BigDecimal.valueOf(100.00));
        order.setUserId(1L);
        
        when(paymentService.processPayment(any(PaymentRequest.class))).thenReturn(true);
        when(emailService.sendConfirmationEmail(any(String.class), any(String.class))).thenReturn(true);
        
        // 执行测试
        Order result = orderService.createOrder(order);
        
        // 验证结果
        assertThat(result).isNotNull();
        assertThat(result.getStatus()).isEqualTo(OrderStatus.CONFIRMED);
        
        verify(paymentService, times(1)).processPayment(any(PaymentRequest.class));
        verify(emailService, times(1)).sendConfirmationEmail(any(String.class), any(String.class));
    }
}
```

## REST Assured 测试

添加依赖：

```xml
<dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>rest-assured</artifactId>
    <scope>test</scope>
</dependency>
```

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(locations = "classpath:application-test.properties")
class RestApiIntegrationTest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @LocalServerPort
    private int port;
    
    private String baseUrl;
    
    @BeforeEach
    void setUp() {
        baseUrl = "http://localhost:" + port + "/api";
    }
    
    @Test
    @DisplayName("测试用户 API 端点")
    void testUserEndpoints() {
        // 测试获取所有用户
        ResponseEntity<String> response = restTemplate.getForEntity(baseUrl + "/users", String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        
        // 使用 REST Assured 进行更复杂的测试
        given()
            .contentType(MediaType.APPLICATION_JSON_VALUE)
            .when()
                .get(baseUrl + "/users")
            .then()
                .statusCode(HttpStatus.OK.value())
                .body("size()", greaterThan(0));
    }
}
```

## 测试数据初始化

### 使用 @Sql 注解

```java
@SpringBootTest
@Sql(scripts = "/test-data.sql", executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD)
@Sql(scripts = "/cleanup.sql", executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)
class UserServiceWithSqlTest {
    
    @Autowired
    private UserService userService;
    
    @Test
    @DisplayName("使用SQL脚本初始化数据")
    void findUserWithInitializedData() {
        List<User> users = userService.findAllUsers();
        assertThat(users).isNotEmpty();
        
        Optional<User> user = userService.findUserById(1L);
        assertThat(user).isPresent();
        assertThat(user.get().getUsername()).isEqualTo("testuser1");
    }
}
```

test-data.sql:

```sql
INSERT INTO users (id, username, email, created_at, role) VALUES
(1, 'testuser1', 'test1@example.com', NOW(), 'USER'),
(2, 'testuser2', 'test2@example.com', NOW(), 'USER'),
(3, 'admin', 'admin@example.com', NOW(), 'ADMIN');
```

## 测试最佳实践

### 参数化测试

```java
class ValidationTest {
    
    @ParameterizedTest
    @ValueSource(strings = {"", "   ", null})
    @DisplayName("用户名为空或空白时验证失败")
    void validateUsername_InvalidInputs(String invalidUsername) {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> validateUsername(invalidUsername)
        );
        
        assertThat(exception.getMessage()).contains("Username cannot be empty");
    }
    
    @ParameterizedTest
    @CsvSource({
        "valid@example.com, true",
        "invalid-email, false",
        "user@domain.co.uk, true",
        "@invalid.com, false",
        "valid@domain.org, true"
    })
    @DisplayName("邮箱验证测试")
    void validateEmail_WithVariousInputs(String email, boolean expectedValid) {
        boolean result = isValidEmail(email);
        assertEquals(expectedValid, result, 
            "Email validation failed for: " + email);
    }
    
    private boolean isValidEmail(String email) {
        return email != null && email.contains("@");
    }
    
    private void validateUsername(String username) {
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("Username cannot be empty");
        }
    }
}
```

### 测试套件

```java
@Suite
@SelectPackages("com.example.tests.unit")
@SelectClasses({UserServiceTest.class, OrderServiceTest.class})
@IncludeClassNamePatterns(".*Test")
public class UnitTestSuite {
    // 测试套件配置
}
```