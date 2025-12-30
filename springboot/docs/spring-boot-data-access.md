# Spring Boot 数据访问

Spring Boot 提供了多种数据访问方式，包括JPA、JDBC、MyBatis等。本章将详细介绍各种数据访问技术。

## Spring Data JPA

### 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <scope>runtime</scope>
</dependency>
```

### 实体类定义

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String username;
    
    @Column(nullable = false)
    private String email;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Enumerated(EnumType.STRING)
    private UserRole role;
    
    // constructors, getters and setters
    public User() {}
    
    public User(String username, String email) {
        this.username = username;
        this.email = email;
        this.createdAt = LocalDateTime.now();
    }
    
    // ... getter and setter methods
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public UserRole getRole() { return role; }
    public void setRole(UserRole role) { this.role = role; }
}

enum UserRole {
    ADMIN, USER, MODERATOR
}
```

### Repository 接口

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // 基于方法名的查询
    Optional<User> findByUsername(String username);
    List<User> findByEmailContaining(String email);
    List<User> findByRole(UserRole role);
    
    // 自定义查询
    @Query("SELECT u FROM User u WHERE u.createdAt > :date")
    List<User> findUsersCreatedAfter(@Param("date") LocalDateTime date);
    
    // 使用原生SQL
    @Query(value = "SELECT * FROM users WHERE username LIKE %:keyword%", nativeQuery = true)
    List<User> findByUsernameContainingNative(@Param("keyword") String keyword);
    
    // 更新操作
    @Modifying
    @Query("UPDATE User u SET u.email = :email WHERE u.id = :id")
    int updateUserEmail(@Param("id") Long id, @Param("email") String email);
}
```

### Service 层实现

```java
@Service
@Transactional
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    public Optional<User> getUserById(Long id) {
        return userRepository.findById(id);
    }
    
    public User saveUser(User user) {
        if (user.getCreatedAt() == null) {
            user.setCreatedAt(LocalDateTime.now());
        }
        return userRepository.save(user);
    }
    
    public void deleteUser(User user) {
        userRepository.delete(user);
    }
    
    public List<User> searchUsers(String keyword) {
        return userRepository.findByUsernameContainingNative(keyword);
    }
    
    @Transactional(readOnly = true)
    public Page<User> getUsers(Pageable pageable) {
        return userRepository.findAll(pageable);
    }
}
```

## Spring JDBC

### 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jdbc</artifactId>
</dependency>
```

### JDBC 操作示例

```java
@Service
public class UserJdbcService {
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    public List<User> findAllUsers() {
        String sql = "SELECT id, username, email, created_at, role FROM users";
        return jdbcTemplate.query(sql, new UserRowMapper());
    }
    
    public User findById(Long id) {
        String sql = "SELECT id, username, email, created_at, role FROM users WHERE id = ?";
        return jdbcTemplate.queryForObject(sql, new Object[]{id}, new UserRowMapper());
    }
    
    public int createUser(String username, String email) {
        String sql = "INSERT INTO users (username, email, created_at, role) VALUES (?, ?, ?, ?)";
        return jdbcTemplate.update(sql, username, email, LocalDateTime.now(), "USER");
    }
    
    public int updateUserEmail(Long id, String newEmail) {
        String sql = "UPDATE users SET email = ? WHERE id = ?";
        return jdbcTemplate.update(sql, newEmail, id);
    }
    
    public int deleteUser(Long id) {
        String sql = "DELETE FROM users WHERE id = ?";
        return jdbcTemplate.update(sql, id);
    }
    
    // 行映射器
    private static class UserRowMapper implements RowMapper<User> {
        @Override
        public User mapRow(ResultSet rs, int rowNum) throws SQLException {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setUsername(rs.getString("username"));
            user.setEmail(rs.getString("email"));
            user.setCreatedAt(rs.getObject("created_at", LocalDateTime.class));
            user.setRole(UserRole.valueOf(rs.getString("role")));
            return user;
        }
    }
}
```

## 事务管理

### 声明式事务

```java
@Service
public class TransactionalUserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Transactional
    public void createUserWithOrder(User user, Order order) {
        // 保存用户
        userRepository.save(user);
        
        // 保存订单
        order.setUser(user);
        orderRepository.save(order);
        
        // 如果这里抛出异常，整个事务会回滚
    }
    
    @Transactional(rollbackFor = Exception.class)
    public void complexOperation() {
        try {
            // 执行多个数据库操作
            // 如果任何操作失败，所有操作都会回滚
        } catch (Exception e) {
            // 记录日志
            throw e; // 重新抛出异常以触发回滚
        }
    }
    
    @Transactional(readOnly = true)
    public List<User> readOnlyOperation() {
        // 只读事务，可以提高性能
        return userRepository.findAll();
    }
}
```

## 数据库连接池配置

在 `application.yml` 中配置：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useUnicode=true&characterEncoding=utf8&useSSL=false
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 20000
      idle-timeout: 300000
      max-lifetime: 1200000
      auto-commit: true
      pool-name: MyHikariPool
```

## 数据库初始化

### schema.sql 和 data.sql

创建 `src/main/resources/schema.sql`：

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) DEFAULT 'USER'
);
```

创建 `src/main/resources/data.sql`：

```sql
INSERT INTO users (username, email, role) VALUES 
('admin', 'admin@example.com', 'ADMIN'),
('user1', 'user1@example.com', 'USER'),
('user2', 'user2@example.com', 'USER');
```

在 `application.yml` 中启用：

```yaml
spring:
  sql:
    init:
      mode: always  # always, embedded, never
  datasource:
    initialization-mode: always
```

## 多数据源配置

```java
@Configuration
public class MultipleDataSourceConfig {
    
    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    @ConfigurationProperties("spring.datasource.secondary")
    public DataSource secondaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    @Primary
    public JdbcTemplate primaryJdbcTemplate(@Qualifier("primaryDataSource") DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
    
    @Bean
    public JdbcTemplate secondaryJdbcTemplate(@Qualifier("secondaryDataSource") DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
}
```

对应的配置：

```yaml
spring:
  datasource:
    primary:
      url: jdbc:mysql://localhost:3306/primary_db
      username: root
      password: password
      driver-class-name: com.mysql.cj.jdbc.Driver
    secondary:
      url: jdbc:mysql://localhost:3306/secondary_db
      username: root
      password: password
      driver-class-name: com.mysql.cj.jdbc.Driver
```