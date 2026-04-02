# 第7章：Spring Boot缓存技术

## 7.1 缓存概述

### 7.1.1 为什么需要缓存

- **提升性能**：减少数据库查询，加快响应速度
- **降低负载**：减少数据库压力
- **提高并发**：支持更高的并发访问量

### 7.1.2 常见缓存方案

| 缓存类型 | 特点 | 适用场景 |
|----------|------|----------|
| 本地缓存 | 速度快，容量有限 | 单机应用，小数据量 |
| 分布式缓存 | 容量大，支持集群 | 分布式系统，大数据量 |
| 多级缓存 | 性能最优，实现复杂 | 高并发场景 |

### 7.1.3 Spring Cache抽象

Spring Cache提供了统一的缓存抽象，支持多种缓存实现：

- Caffeine
- Ehcache
- Redis
- Guava Cache
- Simple（内存缓存）

## 7.2 Caffeine缓存

### 7.2.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>

<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

### 7.2.2 Caffeine配置

```java
@Configuration
@EnableCaching
public class CaffeineCacheConfig {

    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .initialCapacity(100)
            .maximumSize(1000)
            .expireAfterWrite(10, TimeUnit.MINUTES)
            .recordStats());
        return cacheManager;
    }

    @Bean
    public Cache<String, Object> userCache() {
        return Caffeine.newBuilder()
            .initialCapacity(50)
            .maximumSize(500)
            .expireAfterWrite(30, TimeUnit.MINUTES)
            .recordStats()
            .build();
    }

    @Bean
    public Cache<String, Object> productCache() {
        return Caffeine.newBuilder()
            .initialCapacity(100)
            .maximumSize(1000)
            .expireAfterWrite(1, TimeUnit.HOURS)
            .recordStats()
            .build();
    }
}
```

### 7.2.3 使用缓存注解

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    @Cacheable(value = "users", key = "#id")
    public User findById(Long id) {
        return userRepository.findById(id).orElse(null);
    }

    @Cacheable(value = "users", key = "#username")
    public User findByUsername(String username) {
        return userRepository.findByUsername(username).orElse(null);
    }

    @CacheEvict(value = "users", key = "#user.id")
    public User update(User user) {
        return userRepository.save(user);
    }

    @CacheEvict(value = "users", key = "#id")
    public void deleteById(Long id) {
        userRepository.deleteById(id);
    }

    @CachePut(value = "users", key = "#result.id")
    public User save(User user) {
        return userRepository.save(user);
    }

    @Caching(evict = {
        @CacheEvict(value = "users", key = "#id"),
        @CacheEvict(value = "userRoles", key = "#id")
    })
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }

    @Cacheable(value = "users", key = "#root.methodName + #userId")
    public List<Order> getUserOrders(Long userId) {
        return orderRepository.findByUserId(userId);
    }
}
```

### 7.2.4 自定义缓存Key生成器

```java
@Configuration
public class CacheConfig {

    @Bean
    public KeyGenerator customKeyGenerator() {
        return (target, method, params) -> {
            StringBuilder sb = new StringBuilder();
            sb.append(target.getClass().getSimpleName());
            sb.append(":");
            sb.append(method.getName());
            sb.append(":");
            for (Object param : params) {
                sb.append(param.toString());
                sb.append(":");
            }
            return sb.toString();
        };
    }
}

@Service
public class ProductService {

    @Cacheable(value = "products", keyGenerator = "customKeyGenerator")
    public Product findProduct(Long id, String category) {
        return productRepository.findByIdAndCategory(id, category);
    }
}
```

## 7.3 Redis缓存

### 7.3.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>

<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-pool2</artifactId>
</dependency>
```

### 7.3.2 Redis配置

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:
      database: 0
      timeout: 5000ms
      lettuce:
        pool:
          max-active: 20
          max-idle: 10
          min-idle: 5
          max-wait: 3000ms
  cache:
    type: redis
    redis:
      time-to-live: 600000
      cache-null-values: false
      key-prefix: "app:"
      use-key-prefix: true
```

### 7.3.3 Redis配置类

```java
@Configuration
@EnableCaching
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);

        Jackson2JsonRedisSerializer<Object> serializer = new Jackson2JsonRedisSerializer<>(Object.class);
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        objectMapper.activateDefaultTyping(
            LaissezFaireSubTypeValidator.instance,
            ObjectMapper.DefaultTyping.NON_FINAL);
        serializer.setObjectMapper(objectMapper);

        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);
        template.setValueSerializer(serializer);
        template.setHashValueSerializer(serializer);

        template.afterPropertiesSet();
        return template;
    }

    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()))
            .disableCachingNullValues();

        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        cacheConfigurations.put("users", config.entryTtl(Duration.ofMinutes(10)));
        cacheConfigurations.put("products", config.entryTtl(Duration.ofHours(1)));
        cacheConfigurations.put("config", config.entryTtl(Duration.ofDays(1)));

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .withInitialCacheConfigurations(cacheConfigurations)
            .transactionAware()
            .build();
    }

    @Bean
    public RedissonClient redissonClient() {
        Config config = new Config();
        config.useSingleServer()
            .setAddress("redis://localhost:6379")
            .setPassword(null)
            .setDatabase(0);
        return Redisson.create(config);
    }
}
```

### 7.3.4 Redis工具类

```java
@Component
public class RedisUtil {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    public void set(String key, Object value) {
        redisTemplate.opsForValue().set(key, value);
    }

    public void set(String key, Object value, long timeout, TimeUnit unit) {
        redisTemplate.opsForValue().set(key, value, timeout, unit);
    }

    public Object get(String key) {
        return redisTemplate.opsForValue().get(key);
    }

    public Boolean delete(String key) {
        return redisTemplate.delete(key);
    }

    public Boolean hasKey(String key) {
        return redisTemplate.hasKey(key);
    }

    public Boolean expire(String key, long timeout, TimeUnit unit) {
        return redisTemplate.expire(key, timeout, unit);
    }

    public Long getExpire(String key) {
        return redisTemplate.getExpire(key);
    }

    public void hSet(String key, String field, Object value) {
        redisTemplate.opsForHash().put(key, field, value);
    }

    public Object hGet(String key, String field) {
        return redisTemplate.opsForHash().get(key, field);
    }

    public Map<Object, Object> hGetAll(String key) {
        return redisTemplate.opsForHash().entries(key);
    }

    public void hDelete(String key, Object... fields) {
        redisTemplate.opsForHash().delete(key, fields);
    }

    public Long lPush(String key, Object value) {
        return redisTemplate.opsForList().rightPush(key, value);
    }

    public Object lPop(String key) {
        return redisTemplate.opsForList().leftPop(key);
    }

    public List<Object> lRange(String key, long start, long end) {
        return redisTemplate.opsForList().range(key, start, end);
    }

    public Long lSize(String key) {
        return redisTemplate.opsForList().size(key);
    }

    public void sAdd(String key, Object... values) {
        redisTemplate.opsForSet().add(key, values);
    }

    public Set<Object> sMembers(String key) {
        return redisTemplate.opsForSet().members(key);
    }

    public Boolean sIsMember(String key, Object value) {
        return redisTemplate.opsForSet().isMember(key, value);
    }

    public Long sRemove(String key, Object... values) {
        return redisTemplate.opsForSet().remove(key, values);
    }

    public void zAdd(String key, double score, Object value) {
        redisTemplate.opsForZSet().add(key, value, score);
    }

    public Set<Object> zRange(String key, long start, long end) {
        return redisTemplate.opsForZSet().range(key, start, end);
    }

    public Long zRank(String key, Object value) {
        return redisTemplate.opsForZSet().rank(key, value);
    }

    public Long zRemove(String key, Object... values) {
        return redisTemplate.opsForZSet().remove(key, values);
    }
}
```

## 7.4 多级缓存

### 7.4.1 多级缓存实现

```java
@Component
public class MultiLevelCache {

    @Autowired
    private CacheManager caffeineCacheManager;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    public <T> T get(String cacheName, String key, Class<T> type) {
        Cache caffeineCache = caffeineCacheManager.getCache(cacheName);
        if (caffeineCache != null) {
            Cache.ValueWrapper wrapper = caffeineCache.get(key);
            if (wrapper != null) {
                return (T) wrapper.get();
            }
        }

        Object value = redisTemplate.opsForValue().get(cacheName + ":" + key);
        if (value != null) {
            if (caffeineCache != null) {
                caffeineCache.put(key, value);
            }
            return (T) value;
        }

        return null;
    }

    public void put(String cacheName, String key, Object value) {
        Cache caffeineCache = caffeineCacheManager.getCache(cacheName);
        if (caffeineCache != null) {
            caffeineCache.put(key, value);
        }
        redisTemplate.opsForValue().set(cacheName + ":" + key, value);
    }

    public void evict(String cacheName, String key) {
        Cache caffeineCache = caffeineCacheManager.getCache(cacheName);
        if (caffeineCache != null) {
            caffeineCache.evict(key);
        }
        redisTemplate.delete(cacheName + ":" + key);
    }

    public void clear(String cacheName) {
        Cache caffeineCache = caffeineCacheManager.getCache(cacheName);
        if (caffeineCache != null) {
            caffeineCache.clear();
        }
        Set<String> keys = redisTemplate.keys(cacheName + ":*");
        if (keys != null && !keys.isEmpty()) {
            redisTemplate.delete(keys);
        }
    }
}
```

### 7.4.2 多级缓存注解

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface MultiLevelCacheable {
    String cacheName();
    String key();
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface MultiLevelCacheEvict {
    String cacheName();
    String key();
}

@Aspect
@Component
public class MultiLevelCacheAspect {

    @Autowired
    private MultiLevelCache multiLevelCache;

    @Around("@annotation(multiLevelCacheable)")
    public Object aroundCacheable(ProceedingJoinPoint joinPoint,
                                  MultiLevelCacheable multiLevelCacheable) throws Throwable {
        String cacheName = multiLevelCacheable.cacheName();
        String key = multiLevelCacheable.key();

        Object result = multiLevelCache.get(cacheName, key, Object.class);
        if (result != null) {
            return result;
        }

        result = joinPoint.proceed();
        if (result != null) {
            multiLevelCache.put(cacheName, key, result);
        }

        return result;
    }

    @After("@annotation(multiLevelCacheEvict)")
    public void afterEvict(JoinPoint joinPoint,
                           MultiLevelCacheEvict multiLevelCacheEvict) {
        String cacheName = multiLevelCacheEvict.cacheName();
        String key = multiLevelCacheEvict.key();
        multiLevelCache.evict(cacheName, key);
    }
}
```

## 7.5 缓存注解详解

### 7.5.1 @Cacheable

```java
@Cacheable(
    value = "users",
    key = "#id",
    condition = "#id > 0",
    unless = "#result == null"
)
public User findById(Long id) {
    return userRepository.findById(id).orElse(null);
}

@Cacheable(
    value = "users",
    keyGenerator = "customKeyGenerator",
    cacheResolver = "customCacheResolver"
)
public User findUser(String username, String email) {
    return userRepository.findByUsernameOrEmail(username, email);
}
```

### 7.5.2 @CachePut

```java
@CachePut(
    value = "users",
    key = "#user.id"
)
public User update(User user) {
    return userRepository.save(user);
}
```

### 7.5.3 @CacheEvict

```java
@CacheEvict(
    value = "users",
    key = "#id"
)
public void deleteById(Long id) {
    userRepository.deleteById(id);
}

@CacheEvict(
    value = "users",
    allEntries = true
)
public void clearAllUsers() {
}

@CacheEvict(
    value = "users",
    key = "#id",
    beforeInvocation = true
)
public void deleteWithException(Long id) {
    userRepository.deleteById(id);
}
```

### 7.5.4 @Caching

```java
@Caching(
    cacheable = {
        @Cacheable(value = "users", key = "#username"),
        @Cacheable(value = "userEmails", key = "#email")
    }
)
public User findByUsernameOrEmail(String username, String email) {
    return userRepository.findByUsernameOrEmail(username, email);
}

@Caching(
    evict = {
        @CacheEvict(value = "users", key = "#user.id"),
        @CacheEvict(value = "userRoles", key = "#user.id"),
        @CacheEvict(value = "userPermissions", key = "#user.id")
    }
)
public void deleteUser(User user) {
    userRepository.delete(user);
}
```

## 7.6 缓存预热

```java
@Component
@RequiredArgsConstructor
public class CacheWarmupService {

    private final UserService userService;
    private final ProductService productService;

    @PostConstruct
    public void warmupCache() {
        warmupUserCache();
        warmupProductCache();
    }

    private void warmupUserCache() {
        List<User> users = userService.findAll();
        users.forEach(user -> {
            userService.findById(user.getId());
        });
    }

    private void warmupProductCache() {
        List<Product> products = productService.findAll();
        products.forEach(product -> {
            productService.findById(product.getId());
        });
    }
}
```

## 7.7 互联网大厂真实项目代码示例

### 7.7.1 阿里巴巴缓存配置

```java
package com.alibaba.cache.config;

import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import java.util.concurrent.TimeUnit;

@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    @Primary
    public CacheManager caffeineCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .initialCapacity(100)
            .maximumSize(10000)
            .expireAfterWrite(30, TimeUnit.MINUTES)
            .recordStats());
        return cacheManager;
    }

    @Bean("shortTermCacheManager")
    public CacheManager shortTermCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .initialCapacity(50)
            .maximumSize(500)
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .recordStats());
        return cacheManager;
    }

    @Bean("longTermCacheManager")
    public CacheManager longTermCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .initialCapacity(200)
            .maximumSize(20000)
            .expireAfterWrite(2, TimeUnit.HOURS)
            .recordStats());
        return cacheManager;
    }
}
```

### 7.7.2 腾讯云Redis配置

```java
package com.tencent.cloud.cache.config;

import com.fasterxml.jackson.annotation.JsonAutoDetect;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.jsontype.impl.LaissezFaireSubTypeValidator;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.*;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableCaching
public class RedisCacheConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);

        Jackson2JsonRedisSerializer<Object> serializer = new Jackson2JsonRedisSerializer<>(Object.class);
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setVisibility(PropertyAccessor.ALL, JsonAutoDetect.Visibility.ANY);
        objectMapper.activateDefaultTyping(
            LaissezFaireSubTypeValidator.instance,
            ObjectMapper.DefaultTyping.NON_FINAL,
            JsonTypeInfo.As.PROPERTY);
        serializer.setObjectMapper(objectMapper);

        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);
        template.setValueSerializer(serializer);
        template.setHashValueSerializer(serializer);

        template.afterPropertiesSet();
        return template;
    }

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()))
            .disableCachingNullValues();

        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        cacheConfigurations.put("userCache", defaultConfig.entryTtl(Duration.ofMinutes(10)));
        cacheConfigurations.put("productCache", defaultConfig.entryTtl(Duration.ofHours(1)));
        cacheConfigurations.put("configCache", defaultConfig.entryTtl(Duration.ofDays(1)));

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig)
            .withInitialCacheConfigurations(cacheConfigurations)
            .transactionAware()
            .build();
    }
}
```

### 7.7.3 美团多级缓存

```java
package com.meituan.cache;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

@Component
public class MultiLevelCache {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private final Cache<String, Object> localCache = Caffeine.newBuilder()
        .maximumSize(10000)
        .expireAfterWrite(5, TimeUnit.MINUTES)
        .build();

    public <T> T get(String key, Class<T> type) {
        Object value = localCache.getIfPresent(key);
        if (value != null) {
            return (T) value;
        }

        value = redisTemplate.opsForValue().get(key);
        if (value != null) {
            localCache.put(key, value);
            return (T) value;
        }

        return null;
    }

    public void put(String key, Object value) {
        localCache.put(key, value);
        redisTemplate.opsForValue().set(key, value, 30, TimeUnit.MINUTES);
    }

    public void evict(String key) {
        localCache.invalidate(key);
        redisTemplate.delete(key);
    }

    public void clear() {
        localCache.invalidateAll();
    }
}
```

### 7.7.4 字节跳动缓存注解

```java
package com.bytedance.cache.annotation;

import java.lang.annotation.*;
import java.util.concurrent.TimeUnit;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface CacheExpire {

    long timeout() default 30;

    TimeUnit timeUnit() default TimeUnit.MINUTES;
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface CacheKey {

    String value() default "";
}

@Aspect
@Component
public class CacheAspect {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Around("@annotation(cacheExpire)")
    public Object aroundCache(ProceedingJoinPoint joinPoint, CacheExpire cacheExpire) throws Throwable {
        String cacheKey = generateCacheKey(joinPoint);

        Object cachedValue = redisTemplate.opsForValue().get(cacheKey);
        if (cachedValue != null) {
            return cachedValue;
        }

        Object result = joinPoint.proceed();
        if (result != null) {
            redisTemplate.opsForValue().set(cacheKey, result,
                cacheExpire.timeout(), cacheExpire.timeUnit());
        }

        return result;
    }

    private String generateCacheKey(JoinPoint joinPoint) {
        StringBuilder keyBuilder = new StringBuilder();
        keyBuilder.append(joinPoint.getTarget().getClass().getSimpleName());
        keyBuilder.append(":");
        keyBuilder.append(joinPoint.getSignature().getName());
        keyBuilder.append(":");

        Object[] args = joinPoint.getArgs();
        for (Object arg : args) {
            keyBuilder.append(arg.toString());
            keyBuilder.append(":");
        }

        return keyBuilder.toString();
    }
}
```

### 7.7.5 京东健康缓存更新

```java
package com.jd.health.cache;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class CacheUpdateAspect {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Around("@annotation(com.jd.health.annotation.CacheUpdate)")
    public Object updateCache(ProceedingJoinPoint joinPoint) throws Throwable {
        Object result = joinPoint.proceed();

        String cacheKey = generateCacheKey(joinPoint);
        redisTemplate.opsForValue().set(cacheKey, result);

        return result;
    }

    private String generateCacheKey(JoinPoint joinPoint) {
        StringBuilder keyBuilder = new StringBuilder();
        keyBuilder.append("cache:");
        keyBuilder.append(joinPoint.getTarget().getClass().getSimpleName());
        keyBuilder.append(":");
        keyBuilder.append(joinPoint.getSignature().getName());
        keyBuilder.append(":");

        Object[] args = joinPoint.getArgs();
        for (Object arg : args) {
            keyBuilder.append(arg.toString());
            keyBuilder.append(":");
        }

        return keyBuilder.toString();
    }
}
```

### 7.7.6 拼多多缓存统计

```java
package com.pdd.cache.monitor;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.stats.CacheStats;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class CacheMonitor {

    @Autowired
    private Map<String, Cache<String, Object>> caffeineCaches;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Scheduled(fixedRate = 60000)
    public void monitorCache() {
        caffeineCaches.forEach((name, cache) -> {
            CacheStats stats = cache.stats();
            System.out.println("Cache: " + name);
            System.out.println("  Hit Rate: " + stats.hitRate());
            System.out.println("  Hit Count: " + stats.hitCount());
            System.out.println("  Miss Count: " + stats.missCount());
            System.out.println("  Load Success Count: " + stats.loadSuccessCount());
            System.out.println("  Load Failure Count: " + stats.loadFailureCount());
            System.out.println("  Total Load Time: " + stats.totalLoadTime() + "ns");
            System.out.println("  Eviction Count: " + stats.evictionCount());
        });
    }
}
```

## 7.8 最佳实践

1. **合理设置缓存过期时间**：避免缓存雪崩
2. **使用多级缓存**：提升缓存命中率
3. **缓存预热**：系统启动时加载热点数据
4. **监控缓存指标**：命中率、加载时间等
5. **避免缓存穿透**：使用布隆过滤器
6. **防止缓存雪崩**：设置随机过期时间

## 7.9 小结

本章介绍了Spring Boot缓存技术的核心内容，包括：

- Caffeine本地缓存
- Redis分布式缓存
- 多级缓存实现
- 缓存注解详解
- 缓存预热

通过本章学习，你应该能够：

- 使用Caffeine进行本地缓存
- 集成Redis进行分布式缓存
- 实现多级缓存
- 合理使用缓存注解
- 监控缓存性能

下一章将介绍Spring Boot的消息队列技术。
