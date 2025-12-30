# Spring Boot 缓存

Spring Boot 提供了强大的缓存支持，可以显著提高应用程序的性能。本章将详细介绍如何在 Spring Boot 应用中实现缓存。

## 启用缓存

### 基础配置

```java
@SpringBootApplication
@EnableCaching  // 启用缓存支持
public class CacheApplication {
    public static void main(String[] args) {
        SpringApplication.run(CacheApplication.class, args);
    }
}
```

### 添加缓存依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
<!-- 可选：添加具体的缓存实现 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

## 简单缓存实现

### 使用 ConcurrentHashMap 作为缓存

```java
@Configuration
@EnableCaching
public class SimpleCacheConfig {
    
    @Bean
    public CacheManager cacheManager() {
        SimpleCacheManager cacheManager = new SimpleCacheManager();
        cacheManager.setCaches(Arrays.asList(
            new ConcurrentMapCache("users"),
            new ConcurrentMapCache("products"),
            new ConcurrentMapCache("categories")
        ));
        return cacheManager;
    }
}
```

## 注解驱动的缓存

### @Cacheable 注解

```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    // 基本缓存用法
    @Cacheable("users")
    public User findUserById(Long id) {
        System.out.println("从数据库查询用户: " + id);
        return userRepository.findById(id).orElse(null);
    }
    
    // 使用 SpEL 表达式指定缓存键
    @Cacheable(value = "users", key = "#username")
    public User findUserByUsername(String username) {
        System.out.println("从数据库查询用户: " + username);
        return userRepository.findByUsername(username).orElse(null);
    }
    
    // 复杂的缓存键
    @Cacheable(value = "users", key = "#username + '_' + #type")
    public User findUserByUsernameAndType(String username, String type) {
        System.out.println("从数据库查询用户: " + username + ", type: " + type);
        return userRepository.findByUsernameAndType(username, type);
    }
    
    // 条件缓存
    @Cacheable(value = "users", condition = "#id > 10")
    public User findUserByIdWithCondition(Long id) {
        System.out.println("从数据库查询用户 (条件缓存): " + id);
        return userRepository.findById(id).orElse(null);
    }
    
    // 复杂条件
    @Cacheable(value = "users", condition = "#id != null and #id % 2 == 0")
    public User findUserByIdIfEven(Long id) {
        System.out.println("从数据库查询偶数ID用户: " + id);
        return userRepository.findById(id).orElse(null);
    }
    
    // unless 条件 - 满足条件时不缓存
    @Cacheable(value = "users", unless = "#result == null or #result.email == null")
    public User findUserToCacheIfValid(Long id) {
        System.out.println("从数据库查询用户 (条件缓存): " + id);
        return userRepository.findById(id).orElse(null);
    }
}
```

### @CachePut 注解

```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    // 每次都执行方法并更新缓存
    @CachePut(value = "users", key = "#result.id")
    public User updateUser(User user) {
        System.out.println("更新用户并更新缓存: " + user.getId());
        return userRepository.save(user);
    }
    
    // 条件更新缓存
    @CachePut(value = "users", key = "#result.id", condition = "#user.active")
    public User updateUserIfActive(User user) {
        System.out.println("更新活跃用户并更新缓存: " + user.getId());
        return userRepository.save(user);
    }
}
```

### @CacheEvict 注解

```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    // 清除指定键的缓存
    @CacheEvict(value = "users", key = "#id")
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
    
    // 清除所有缓存
    @CacheEvict(value = "users", allEntries = true)
    public void deleteAllUsers() {
        userRepository.deleteAll();
    }
    
    // 清除条件匹配的缓存
    @CacheEvict(value = "users", key = "#user.id")
    public void updateUserEmail(User user, String newEmail) {
        user.setEmail(newEmail);
        userRepository.save(user);
    }
    
    // 在方法执行前清除缓存
    @CacheEvict(value = "users", key = "#id", beforeInvocation = true)
    public void forceRefreshUser(Long id) {
        // 清除缓存后再执行业务逻辑
        System.out.println("强制刷新用户: " + id);
    }
}
```

### @Caching 注解

```java
@Service
public class UserService {
    
    @Caching(
        evict = {
            @CacheEvict(value = "users", key = "#user.id"),
            @CacheEvict(value = "userSummaries", key = "'all'")
        }
    )
    public User updateUserAndClearCaches(User user) {
        return userRepository.save(user);
    }
    
    @Caching(
        put = {
            @CachePut(value = "users", key = "#result.id"),
            @CachePut(value = "userEmails", key = "#result.email")
        }
    )
    public User updateUserInfo(User user) {
        return userRepository.save(user);
    }
}
```

## Redis 缓存配置

### Redis 配置

```java
@Configuration
@EnableCaching
public class RedisCacheConfig {
    
    @Bean
    public LettuceConnectionFactory redisConnectionFactory() {
        return new LettuceConnectionFactory(
            new RedisStandaloneConfiguration("localhost", 6379));
    }
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate() {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory());
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.afterPropertiesSet();
        return template;
    }
    
    @Bean
    public CacheManager cacheManager() {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofHours(1))  // 设置缓存过期时间
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return RedisCacheManager.builder(redisConnectionFactory())
            .cacheDefaults(config)
            .build();
    }
}
```

### 在 application.yml 中配置 Redis

```yaml
spring:
  redis:
    host: localhost
    port: 6379
    timeout: 2000ms
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0
  cache:
    type: redis
    redis:
      time-to-live: 3600000  # 1小时，单位毫秒
```

## 自定义缓存实现

### 自定义缓存注解

```java
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Cacheable(value = "default", keyGenerator = "customKeyGenerator")
public @interface CustomCacheable {
    String value() default "";
    String key() default "";
    String condition() default "";
}
```

### 自定义键生成器

```java
@Component
public class CustomKeyGenerator implements KeyGenerator {
    
    @Override
    public Object generate(Object target, Method method, Object... params) {
        StringBuilder key = new StringBuilder();
        key.append(target.getClass().getSimpleName());
        key.append("_").append(method.getName());
        
        for (Object param : params) {
            key.append("_").append(param.toString());
        }
        
        return key.toString();
    }
}
```

### 在配置中注册自定义键生成器

```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public KeyGenerator customKeyGenerator() {
        return new CustomKeyGenerator();
    }
    
    @Bean
    public CacheManager cacheManager() {
        SimpleCacheManager cacheManager = new SimpleCacheManager();
        cacheManager.setCaches(Arrays.asList(
            new ConcurrentMapCache("users"),
            new ConcurrentMapCache("products"),
            new ConcurrentMapCache("categories")
        ));
        return cacheManager;
    }
}
```

## 缓存监控和管理

### 缓存统计服务

```java
@Service
public class CacheStatisticsService {
    
    @Autowired
    private CacheManager cacheManager;
    
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        
        if (cacheManager instanceof CompositeCacheManager) {
            CompositeCacheManager composite = (CompositeCacheManager) cacheManager;
            for (CacheResolver resolver : composite.getCacheResolvers()) {
                // 处理复合缓存管理器
            }
        }
        
        Collection<String> cacheNames = cacheManager.getCacheNames();
        for (String cacheName : cacheNames) {
            Cache cache = cacheManager.getCache(cacheName);
            if (cache != null) {
                stats.put(cacheName, getCacheInfo(cache));
            }
        }
        
        return stats;
    }
    
    private Map<String, Object> getCacheInfo(Cache cache) {
        Map<String, Object> info = new HashMap<>();
        // 根据具体缓存实现获取统计信息
        info.put("name", cache.getName());
        // 注意：不是所有缓存实现都提供统计信息
        return info;
    }
    
    public void clearAllCaches() {
        Collection<String> cacheNames = cacheManager.getCacheNames();
        for (String cacheName : cacheNames) {
            cacheManager.getCache(cacheName).clear();
        }
    }
    
    public void clearCache(String cacheName) {
        Cache cache = cacheManager.getCache(cacheName);
        if (cache != null) {
            cache.clear();
        }
    }
}
```

## 缓存最佳实践

### 缓存策略选择

```java
@Service
public class ProductService {
    
    @Autowired
    private ProductRepository productRepository;
    
    // 读多写少的数据使用 @Cacheable
    @Cacheable(value = "products", key = "#id", unless = "#result == null")
    public Product findProductById(Long id) {
        return productRepository.findById(id).orElse(null);
    }
    
    // 频繁更新的数据使用 @CachePut
    @CachePut(value = "products", key = "#result.id")
    public Product updateProduct(Product product) {
        return productRepository.save(product);
    }
    
    // 删除操作后清理缓存
    @CacheEvict(value = "products", key = "#id")
    public void deleteProduct(Long id) {
        productRepository.deleteById(id);
    }
    
    // 批量操作后清理相关缓存
    @Caching(
        evict = {
            @CacheEvict(value = "products", allEntries = true),
            @CacheEvict(value = "productSummaries", allEntries = true)
        }
    )
    public void updateProductCategory(Long categoryId, String newName) {
        // 批量更新产品分类
        productRepository.updateCategoryById(categoryId, newName);
    }
}
```

### 缓存穿透、击穿、雪崩防护

```java
@Service
public class SafeUserService {
    
    @Autowired
    private UserRepository userRepository;
    
    // 防止缓存穿透：对空结果也进行缓存
    @Cacheable(value = "users", key = "#id", unless = "#result == null")
    public User findUserSafely(Long id) {
        User user = userRepository.findById(id).orElse(null);
        if (user == null) {
            // 创建一个空对象或特殊标记来防止缓存穿透
            user = new User(); // 或者使用特殊标记对象
        }
        return user;
    }
    
    // 使用分布式锁防止缓存击穿
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    public User findUserWithLock(Long id) {
        String cacheKey = "user:" + id;
        String lockKey = "lock:user:" + id;
        
        // 尝试获取分布式锁
        Boolean lockAcquired = redisTemplate.opsForValue()
            .setIfAbsent(lockKey, "locked", Duration.ofSeconds(10));
            
        if (Boolean.TRUE.equals(lockAcquired)) {
            try {
                // 双重检查，确保只有一个线程查询数据库
                User cachedUser = (User) redisTemplate.opsForValue().get(cacheKey);
                if (cachedUser != null) {
                    return cachedUser;
                }
                
                // 查询数据库
                User user = userRepository.findById(id).orElse(null);
                
                // 存入缓存
                if (user != null) {
                    redisTemplate.opsForValue().set(cacheKey, user, Duration.ofMinutes(30));
                }
                
                return user;
            } finally {
                // 释放锁
                redisTemplate.delete(lockKey);
            }
        } else {
            // 等待一段时间后重试或返回缓存值
            try {
                Thread.sleep(100);
                return (User) redisTemplate.opsForValue().get(cacheKey);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return null;
            }
        }
    }
}
```

## 缓存配置示例

### 多种缓存配置

```java
@Configuration
@EnableCaching
public class MultiCacheConfig {
    
    // 本地缓存配置
    @Bean
    public CacheManager localCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(10, TimeUnit.MINUTES)
            .recordStats());
        return cacheManager;
    }
    
    // Redis 缓存配置
    @Bean
    public CacheManager redisCacheManager() {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofHours(1))
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return RedisCacheManager.builder(redisConnectionFactory())
            .cacheDefaults(config)
            .build();
    }
    
    // 组合缓存管理器
    @Bean
    public CacheManager multiCacheManager() {
        CompositeCacheManager cacheManager = new CompositeCacheManager();
        cacheManager.setCacheManagers(Arrays.asList(
            localCacheManager(),
            redisCacheManager()
        ));
        cacheManager.setFallbackToNoOpCache(true);
        return cacheManager;
    }
    
    @Bean
    public LettuceConnectionFactory redisConnectionFactory() {
        return new LettuceConnectionFactory(
            new RedisStandaloneConfiguration("localhost", 6379));
    }
}
```

在 `application.yml` 中配置：

```yaml
spring:
  cache:
    type: composite
    cache-names: users,products,categories
  redis:
    host: localhost
    port: 6379
    timeout: 2000ms
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0

# 自定义缓存配置
cache:
  local:
    enabled: true
    spec: maximumSize=1000,expireAfterWrite=10m
  redis:
    enabled: true
    time-to-live: 3600000
```