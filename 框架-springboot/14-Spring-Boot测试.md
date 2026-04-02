# 第14章：Spring Boot测试

## 14.1 测试概述

### 14.1.1 测试类型

| 测试类型 | 说明 | 工具 |
|----------|------|------|
| 单元测试 | 测试单个方法或类 | JUnit, Mockito |
| 集成测试 | 测试多个组件的协作 | Spring Boot Test |
| 端到端测试 | 测试完整的业务流程 | Selenium, Cypress |
| 性能测试 | 测试系统性能 | JMeter, Gatling |

### 14.1.2 测试金字塔

```
        /\
       /  \
      / E2E \
     /--------\
    / Integration\
   /------------\
  /   Unit Tests  \
 /----------------\
```

## 14.2 单元测试

### 14.2.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>

<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <scope>test</scope>
</dependency>

<dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <scope>test</scope>
</dependency>
```

### 14.2.2 Service层测试

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void testFindById() {
        User user = User.builder()
            .id(1L)
            .username("testuser")
            .email("test@example.com")
            .build();

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        UserDTO result = userService.findById(1L);

        assertThat(result).isNotNull();
        assertThat(result.getUsername()).isEqualTo("testuser");
        assertThat(result.getEmail()).isEqualTo("test@example.com");

        verify(userRepository, times(1)).findById(1L);
    }

    @Test
    void testFindByIdNotFound() {
        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(UserNotFoundException.class, () -> {
            userService.findById(1L);
        });

        verify(userRepository, times(1)).findById(1L);
    }

    @Test
    void testCreateUser() {
        UserCreateRequest request = UserCreateRequest.builder()
            .username("newuser")
            .email("new@example.com")
            .password("Password123")
            .build();

        User user = User.builder()
            .id(1L)
            .username("newuser")
            .email("new@example.com")
            .password("encodedPassword")
            .build();

        when(userRepository.existsByUsername("newuser")).thenReturn(false);
        when(userRepository.existsByEmail("new@example.com")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenReturn(user);

        UserDTO result = userService.create(request);

        assertThat(result).isNotNull();
        assertThat(result.getUsername()).isEqualTo("newuser");
        assertThat(result.getEmail()).isEqualTo("new@example.com");

        verify(userRepository, times(1)).existsByUsername("newuser");
        verify(userRepository, times(1)).existsByEmail("new@example.com");
        verify(userRepository, times(1)).save(any(User.class));
    }

    @Test
    void testCreateUserUsernameExists() {
        UserCreateRequest request = UserCreateRequest.builder()
            .username("existinguser")
            .email("new@example.com")
            .password("Password123")
            .build();

        when(userRepository.existsByUsername("existinguser")).thenReturn(true);

        assertThrows(BusinessException.class, () -> {
            userService.create(request);
        });

        verify(userRepository, times(1)).existsByUsername("existinguser");
        verify(userRepository, never()).save(any(User.class));
    }
}
```

### 14.2.3 Controller层测试

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
    void testGetUser() throws Exception {
        UserDTO userDTO = UserDTO.builder()
            .id(1L)
            .username("testuser")
            .email("test@example.com")
            .build();

        when(userService.findById(1L)).thenReturn(userDTO);

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.code").value(200))
            .andExpect(jsonPath("$.data.id").value(1))
            .andExpect(jsonPath("$.data.username").value("testuser"))
            .andExpect(jsonPath("$.data.email").value("test@example.com"));

        verify(userService, times(1)).findById(1L);
    }

    @Test
    void testCreateUser() throws Exception {
        UserCreateRequest request = UserCreateRequest.builder()
            .username("newuser")
            .email("new@example.com")
            .password("Password123")
            .build();

        UserDTO userDTO = UserDTO.builder()
            .id(1L)
            .username("newuser")
            .email("new@example.com")
            .build();

        when(userService.create(any(UserCreateRequest.class))).thenReturn(userDTO);

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.code").value(200))
            .andExpect(jsonPath("$.data.id").value(1))
            .andExpect(jsonPath("$.data.username").value("newuser"));

        verify(userService, times(1)).create(any(UserCreateRequest.class));
    }

    @Test
    void testCreateUserValidationFailed() throws Exception {
        UserCreateRequest request = UserCreateRequest.builder()
            .username("")
            .email("invalid-email")
            .password("123")
            .build();

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isBadRequest());

        verify(userService, never()).create(any(UserCreateRequest.class));
    }
}
```

## 14.3 集成测试

### 14.3.1 Repository层测试

```java
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private UserRepository userRepository;

    @Test
    void testFindById() {
        User user = User.builder()
            .username("testuser")
            .email("test@example.com")
            .password("encodedPassword")
            .build();

        entityManager.persist(user);
        entityManager.flush();

        Optional<User> result = userRepository.findById(user.getId());

        assertThat(result).isPresent();
        assertThat(result.get().getUsername()).isEqualTo("testuser");
        assertThat(result.get().getEmail()).isEqualTo("test@example.com");
    }

    @Test
    void testFindByUsername() {
        User user = User.builder()
            .username("testuser")
            .email("test@example.com")
            .password("encodedPassword")
            .build();

        entityManager.persist(user);
        entityManager.flush();

        Optional<User> result = userRepository.findByUsername("testuser");

        assertThat(result).isPresent();
        assertThat(result.get().getUsername()).isEqualTo("testuser");
    }

    @Test
    void testExistsByUsername() {
        User user = User.builder()
            .username("testuser")
            .email("test@example.com")
            .password("encodedPassword")
            .build();

        entityManager.persist(user);
        entityManager.flush();

        boolean exists = userRepository.existsByUsername("testuser");

        assertThat(exists).isTrue();
    }
}
```

### 14.3.2 Service层集成测试

```java
@SpringBootTest
@Transactional
class UserServiceIntegrationTest {

    @Autowired
    private UserService userService;

    @Autowired
    private UserRepository userRepository;

    @Test
    void testCreateUser() {
        UserCreateRequest request = UserCreateRequest.builder()
            .username("newuser")
            .email("new@example.com")
            .password("Password123")
            .build();

        UserDTO result = userService.create(request);

        assertThat(result).isNotNull();
        assertThat(result.getUsername()).isEqualTo("newuser");
        assertThat(result.getEmail()).isEqualTo("new@example.com");

        Optional<User> user = userRepository.findById(result.getId());
        assertThat(user).isPresent();
        assertThat(user.get().getUsername()).isEqualTo("newuser");
    }

    @Test
    void testUpdateUser() {
        User user = User.builder()
            .username("testuser")
            .email("test@example.com")
            .password("encodedPassword")
            .build();
        user = userRepository.save(user);

        UserUpdateRequest request = UserUpdateRequest.builder()
            .email("updated@example.com")
            .build();

        UserDTO result = userService.update(user.getId(), request);

        assertThat(result.getEmail()).isEqualTo("updated@example.com");

        User updatedUser = userRepository.findById(user.getId()).get();
        assertThat(updatedUser.getEmail()).isEqualTo("updated@example.com");
    }
}
```

### 14.3.3 Controller层集成测试

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private UserService userService;

    @Test
    void testGetUser() throws Exception {
        UserDTO userDTO = UserDTO.builder()
            .id(1L)
            .username("testuser")
            .email("test@example.com")
            .build();

        when(userService.findById(1L)).thenReturn(userDTO);

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.code").value(200))
            .andExpect(jsonPath("$.data.id").value(1))
            .andExpect(jsonPath("$.data.username").value("testuser"));
    }
}
```

## 14.4 Mock测试

### 14.4.1 Mockito基础

```java
@ExtendWith(MockitoExtension.class)
class MockitoTest {

    @Mock
    private List<String> mockList;

    @Test
    void testMock() {
        when(mockList.get(0)).thenReturn("first");
        when(mockList.size()).thenReturn(5);

        assertThat(mockList.get(0)).isEqualTo("first");
        assertThat(mockList.size()).isEqualTo(5);

        verify(mockList).get(0);
        verify(mockList).size();
    }

    @Test
    void testVerify() {
        mockList.add("one");
        mockList.add("two");

        verify(mockList).add("one");
        verify(mockList).add("two");
        verify(mockList, times(2)).add(anyString());
        verify(mockList, never()).clear();
    }

    @Test
    void testArgumentMatchers() {
        when(mockList.get(anyInt())).thenReturn("element");

        assertThat(mockList.get(0)).isEqualTo("element");
        assertThat(mockList.get(100)).isEqualTo("element");

        verify(mockList).get(anyInt());
    }
}
```

### 14.4.2 Mock外部服务

```java
@ExtendWith(MockitoExtension.class)
class ExternalServiceTest {

    @Mock
    private RestTemplate restTemplate;

    @InjectMocks
    private ExternalService externalService;

    @Test
    void testCallExternalApi() {
        String expectedResponse = "{\"status\":\"success\"}";

        when(restTemplate.getForObject(anyString(), eq(String.class)))
            .thenReturn(expectedResponse);

        String result = externalService.callExternalApi("https://api.example.com");

        assertThat(result).isEqualTo(expectedResponse);

        verify(restTemplate).getForObject(eq("https://api.example.com"), eq(String.class));
    }
}
```

## 14.5 测试配置

### 14.5.1 测试配置文件

```yaml
# application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
  redis:
    host: localhost
    port: 6379
    database: 1
```

### 14.5.2 测试配置类

```java
@TestConfiguration
public class TestConfig {

    @Bean
    @Primary
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    @Primary
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

## 14.6 测试工具

### 14.6.1 AssertJ断言

```java
@Test
void testAssertJ() {
    User user = User.builder()
        .id(1L)
        .username("testuser")
        .email("test@example.com")
        .build();

    assertThat(user)
        .isNotNull()
        .hasFieldOrProperty("id")
        .hasFieldOrPropertyWithValue("username", "testuser")
        .hasFieldOrPropertyWithValue("email", "test@example.com");

    assertThat(user.getUsername())
        .isNotEmpty()
        .hasSize(8)
        .startsWith("test")
        .endsWith("user");

    List<User> users = Arrays.asList(user);
    assertThat(users)
        .hasSize(1)
        .contains(user)
        .doesNotContainNull();
}
```

### 14.6.2 JsonPath断言

```java
@Test
void testJsonPath() throws Exception {
    String json = "{\"user\":{\"id\":1,\"username\":\"testuser\"}}";

    mockMvc.perform(get("/api/users/1"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.user.id").value(1))
        .andExpect(jsonPath("$.user.username").value("testuser"))
        .andExpect(jsonPath("$.user.id").isNumber())
        .andExpect(jsonPath("$.user.username").isString());
}
```

## 14.7 互联网大厂真实项目代码示例

### 14.7.1 阿里巴巴单元测试

```java
package com.alibaba.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void testFindById() {
        Long userId = 1L;
        User user = User.builder()
            .id(userId)
            .username("testuser")
            .build();

        when(userRepository.findById(userId)).thenReturn(Optional.of(user));

        UserDTO result = userService.findById(userId);

        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(userId);
        assertThat(result.getUsername()).isEqualTo("testuser");

        verify(userRepository, times(1)).findById(userId);
    }
}
```

### 14.7.2 腾讯云集成测试

```java
package com.tencent.cloud.integration;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testGetUser() throws Exception {
        mockMvc.perform(get("/api/v1/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.code").value(200))
            .andExpect(jsonPath("$.data.id").value(1));
    }

    @Test
    void testCreateUser() throws Exception {
        String requestBody = "{\"username\":\"newuser\",\"email\":\"new@example.com\"}";

        mockMvc.perform(post("/api/v1/users")
                .contentType("application/json")
                .content(requestBody))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.code").value(200));
    }
}
```

### 14.7.3 美团Mock测试

```java
package com.meituan.test;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private OrderService orderService;

    @Test
    void testCreateOrder() {
        Long userId = 1L;
        Long productId = 1L;
        Integer quantity = 2;

        User user = User.builder().id(userId).build();
        Product product = Product.builder().id(productId).price(100.0).build();

        when(userRepository.findById(userId)).thenReturn(Optional.of(user));
        when(productRepository.findById(productId)).thenReturn(Optional.of(product));

        OrderDTO result = orderService.createOrder(userId, productId, quantity);

        assertThat(result).isNotNull();
        assertThat(result.getTotalAmount()).isEqualTo(200.0);

        verify(userRepository).findById(userId);
        verify(productRepository).findById(productId);
    }
}
```

### 14.7.4 字节跳动Controller测试

```java
package com.bytedance.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void testGetUser() throws Exception {
        UserDTO userDTO = UserDTO.builder()
            .id(1L)
            .username("testuser")
            .build();

        given(userService.findById(1L)).willReturn(userDTO);

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.code").value(200))
            .andExpect(jsonPath("$.data.id").value(1))
            .andExpect(jsonPath("$.data.username").value("testuser"));
    }
}
```

### 14.7.5 京东健康Repository测试

```java
package com.jd.health.repository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class PatientRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private PatientRepository patientRepository;

    @Test
    void testFindById() {
        Patient patient = Patient.builder()
            .name("张三")
            .age(30)
            .gender("男")
            .build();

        entityManager.persist(patient);
        entityManager.flush();

        Patient result = patientRepository.findById(patient.getId()).orElse(null);

        assertThat(result).isNotNull();
        assertThat(result.getName()).isEqualTo("张三");
        assertThat(result.getAge()).isEqualTo(30);
        assertThat(result.getGender()).isEqualTo("男");
    }
}
```

### 14.7.6 拼多多Service测试

```java
package com.pdd.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @Mock
    private CacheService cacheService;

    @InjectMocks
    private ProductService productService;

    private Product product;

    @BeforeEach
    void setUp() {
        product = Product.builder()
            .id(1L)
            .name("测试商品")
            .price(100.0)
            .build();
    }

    @Test
    void testGetProduct() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(cacheService.get("product:1", Product.class)).thenReturn(null);

        ProductDTO result = productService.getProduct(1L);

        assertThat(result).isNotNull();
        assertThat(result.getName()).isEqualTo("测试商品");

        verify(productRepository).findById(1L);
        verify(cacheService).get("product:1", Product.class);
    }

    @Test
    void testGetProductFromCache() {
        ProductDTO cachedProduct = ProductDTO.builder()
            .id(1L)
            .name("缓存商品")
            .build();

        when(cacheService.get("product:1", Product.class)).thenReturn(cachedProduct);

        ProductDTO result = productService.getProduct(1L);

        assertThat(result).isNotNull();
        assertThat(result.getName()).isEqualTo("缓存商品");

        verify(cacheService).get("product:1", Product.class);
        verify(productRepository, never()).findById(anyLong());
    }
}
```

## 14.8 最佳实践

1. **测试金字塔**：单元测试 > 集成测试 > 端到端测试
2. **测试隔离**：每个测试独立运行
3. **Mock外部依赖**：避免依赖外部服务
4. **测试覆盖率**：保持合理的测试覆盖率
5. **测试命名**：清晰描述测试目的
6. **持续集成**：集成到CI/CD流程

## 14.9 小结

本章介绍了Spring Boot测试的核心内容，包括：

- 单元测试
- 集成测试
- Mock测试
- 测试配置
- 测试工具

通过本章学习，你应该能够：

- 编写单元测试
- 编写集成测试
- 使用Mock进行测试
- 配置测试环境
- 使用测试工具

下一章将介绍Spring Boot的实战项目。
