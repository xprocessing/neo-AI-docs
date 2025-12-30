# 第5章：Spring Boot RESTful API开发

## 5.1 RESTful API设计原则

### 5.1.1 RESTful架构风格

REST（Representational State Transfer）是一种软件架构风格，具有以下特点：

- **资源导向**：一切皆资源，通过URI标识
- **统一接口**：使用标准的HTTP方法
- **无状态**：每个请求包含所有必要信息
- **可缓存**：响应可被缓存
- **分层系统**：客户端无需知道是否连接到最终服务器

### 5.1.2 HTTP方法使用规范

| HTTP方法 | 操作 | 幂等性 | 安全性 | 示例 |
|----------|------|--------|--------|------|
| GET | 查询资源 | 是 | 是 | GET /api/users/1 |
| POST | 创建资源 | 否 | 否 | POST /api/users |
| PUT | 完整更新资源 | 是 | 否 | PUT /api/users/1 |
| PATCH | 部分更新资源 | 否 | 否 | PATCH /api/users/1 |
| DELETE | 删除资源 | 是 | 否 | DELETE /api/users/1 |

### 5.1.3 URI设计规范

```java
// 资源命名使用复数名词
GET    /api/users          # 获取用户列表
GET    /api/users/1        # 获取指定用户
POST   /api/users          # 创建用户
PUT    /api/users/1        # 完整更新用户
PATCH  /api/users/1        # 部分更新用户
DELETE /api/users/1        # 删除用户

// 嵌套资源
GET    /api/users/1/orders        # 获取用户1的订单
POST   /api/users/1/orders        # 为用户1创建订单
GET    /api/users/1/orders/2       # 获取用户1的订单2

// 过滤和排序
GET    /api/users?status=active&sort=created_at:desc

// 分页
GET    /api/users?page=1&size=20

// 字段选择
GET    /api/users?fields=id,username,email

// 搜索
GET    /api/users/search?q=keyword
```

## 5.2 RESTful API实现

### 5.2.1 基础CRUD操作

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping
    public ApiResponse<Page<UserDTO>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt,desc") String sort) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sort));
        Page<UserDTO> users = userService.findAll(pageable);
        return ApiResponse.success(users);
    }

    @GetMapping("/{id}")
    public ApiResponse<UserDTO> getUser(@PathVariable Long id) {
        UserDTO user = userService.findById(id);
        return ApiResponse.success(user);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResponse<UserDTO> createUser(@Valid @RequestBody UserCreateRequest request) {
        UserDTO user = userService.create(request);
        return ApiResponse.success("用户创建成功", user);
    }

    @PutMapping("/{id}")
    public ApiResponse<UserDTO> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UserUpdateRequest request) {
        UserDTO user = userService.update(id, request);
        return ApiResponse.success("用户更新成功", user);
    }

    @PatchMapping("/{id}")
    public ApiResponse<UserDTO> patchUser(
            @PathVariable Long id,
            @RequestBody Map<String, Object> fields) {
        UserDTO user = userService.patch(id, fields);
        return ApiResponse.success("用户部分更新成功", user);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }

    @GetMapping("/search")
    public ApiResponse<Page<UserDTO>> searchUsers(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<UserDTO> users = userService.search(keyword, pageable);
        return ApiResponse.success(users);
    }
}
```

### 5.2.2 DTO对象设计

```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDTO {
    private Long id;
    private String username;
    private String email;
    private String phoneNumber;
    private Gender gender;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserCreateRequest {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20之间")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d]{8,}$",
             message = "密码必须包含大小写字母和数字，至少8位")
    private String password;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phoneNumber;

    @NotNull(message = "性别不能为空")
    private Gender gender;

    private LocalDate birthDate;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserUpdateRequest {
    @Email(message = "邮箱格式不正确")
    private String email;

    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phoneNumber;

    private Gender gender;

    private LocalDate birthDate;
}
```

### 5.2.3 分页查询

```java
@Data
public class PageRequest {
    private int page = 0;
    private int size = 20;
    private String sort = "createdAt,desc";

    public org.springframework.data.domain.PageRequest toPageable() {
        String[] sortArray = sort.split(",");
        Sort.Direction direction = sortArray.length > 1
            ? Sort.Direction.fromString(sortArray[1])
            : Sort.Direction.ASC;
        return org.springframework.data.domain.PageRequest.of(page, size,
            Sort.by(direction, sortArray[0]));
    }
}

@RestController
@RequestMapping("/api/products")
public class ProductController {

    @GetMapping
    public ApiResponse<Page<ProductDTO>> getProducts(PageRequest pageRequest) {
        Page<ProductDTO> products = productService.findAll(pageRequest.toPageable());
        return ApiResponse.success(products);
    }
}
```

### 5.2.4 批量操作

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @PostMapping("/batch")
    public ApiResponse<List<UserDTO>> batchCreateUsers(
            @Valid @RequestBody List<UserCreateRequest> requests) {
        List<UserDTO> users = userService.batchCreate(requests);
        return ApiResponse.success("批量创建成功", users);
    }

    @PutMapping("/batch")
    public ApiResponse<List<UserDTO>> batchUpdateUsers(
            @Valid @RequestBody List<UserUpdateRequest> requests) {
        List<UserDTO> users = userService.batchUpdate(requests);
        return ApiResponse.success("批量更新成功", users);
    }

    @DeleteMapping("/batch")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void batchDeleteUsers(@RequestBody List<Long> ids) {
        userService.batchDelete(ids);
    }
}
```

## 5.3 API版本控制

### 5.3.1 URL路径版本控制

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserV1Controller {

    @GetMapping("/{id}")
    public ApiResponse<UserV1DTO> getUser(@PathVariable Long id) {
        return ApiResponse.success(userService.findV1ById(id));
    }
}

@RestController
@RequestMapping("/api/v2/users")
public class UserV2Controller {

    @GetMapping("/{id}")
    public ApiResponse<UserV2DTO> getUser(@PathVariable Long id) {
        return ApiResponse.success(userService.findV2ById(id));
    }
}
```

### 5.3.2 请求头版本控制

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping(value = "/{id}", headers = "X-API-Version=1")
    public ApiResponse<UserV1DTO> getUserV1(@PathVariable Long id) {
        return ApiResponse.success(userService.findV1ById(id));
    }

    @GetMapping(value = "/{id}", headers = "X-API-Version=2")
    public ApiResponse<UserV2DTO> getUserV2(@PathVariable Long id) {
        return ApiResponse.success(userService.findV2ById(id));
    }
}
```

### 5.3.3 自定义版本注解

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface ApiVersion {
    int value();
}

@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    @ApiVersion(1)
    public ApiResponse<UserV1DTO> getUserV1(@PathVariable Long id) {
        return ApiResponse.success(userService.findV1ById(id));
    }

    @GetMapping("/{id}")
    @ApiVersion(2)
    public ApiResponse<UserV2DTO> getUserV2(@PathVariable Long id) {
        return ApiResponse.success(userService.findV2ById(id));
    }
}

@Configuration
public class ApiVersionConfig implements WebMvcRegistrations {

    @Override
    public RequestMappingHandlerMapping getRequestMappingHandlerMapping() {
        return new ApiVersionRequestMappingHandlerMapping();
    }
}

public class ApiVersionRequestMappingHandlerMapping extends RequestMappingHandlerMapping {

    @Override
    protected RequestCondition<ApiVersionCondition> getCustomTypeCondition(
            Class<?> handlerType) {
        ApiVersion apiVersion = AnnotationUtils.findAnnotation(handlerType, ApiVersion.class);
        return createCondition(apiVersion);
    }

    @Override
    protected RequestCondition<ApiVersionCondition> getCustomMethodCondition(
            Method method) {
        ApiVersion apiVersion = AnnotationUtils.findAnnotation(method, ApiVersion.class);
        return createCondition(apiVersion);
    }

    private ApiVersionCondition createCondition(ApiVersion apiVersion) {
        return apiVersion != null ? new ApiVersionCondition(apiVersion.value()) : null;
    }
}
```

## 5.4 HATEOAS实现

### 5.4.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-hateoas</artifactId>
</dependency>
```

### 5.4.2 资源模型

```java
@Data
@EqualsAndHashCode(callSuper = true)
public class UserResource extends RepresentationModel<UserResource> {
    private Long id;
    private String username;
    private String email;

    public static UserResource of(User user) {
        UserResource resource = new UserResource();
        resource.setId(user.getId());
        resource.setUsername(user.getUsername());
        resource.setEmail(user.getEmail());

        resource.add(linkTo(methodOn(UserController.class).getUser(user.getId())).withSelfRel());
        resource.add(linkTo(methodOn(UserController.class).getUsers()).withRel("users"));
        resource.add(linkTo(methodOn(UserController.class).getUserOrders(user.getId()))
            .withRel("orders"));

        return resource;
    }
}
```

### 5.4.3 控制器实现

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public EntityModel<UserDTO> getUser(@PathVariable Long id) {
        UserDTO user = userService.findById(id);
        EntityModel<UserDTO> resource = EntityModel.of(user);

        resource.add(linkTo(methodOn(UserController.class).getUser(id)).withSelfRel());
        resource.add(linkTo(methodOn(UserController.class).getUsers()).withRel("users"));
        resource.add(linkTo(methodOn(UserController.class).getUserOrders(id)).withRel("orders"));

        return resource;
    }

    @GetMapping
    public CollectionModel<EntityModel<UserDTO>> getUsers() {
        List<UserDTO> users = userService.findAll();
        List<EntityModel<UserDTO>> userResources = users.stream()
            .map(user -> EntityModel.of(user,
                linkTo(methodOn(UserController.class).getUser(user.getId())).withSelfRel()))
            .collect(Collectors.toList());

        CollectionModel<EntityModel<UserDTO>> resource = CollectionModel.of(userResources);
        resource.add(linkTo(methodOn(UserController.class).getUsers()).withSelfRel());

        return resource;
    }
}
```

## 5.5 API文档集成

### 5.5.1 SpringDoc OpenAPI配置

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.2.0</version>
</dependency>
```

```java
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Spring Boot API")
                .version("1.0.0")
                .description("Spring Boot RESTful API 文档")
                .contact(new Contact()
                    .name("API Support")
                    .email("support@example.com")))
            .servers(List.of(
                new Server().url("http://localhost:8080").description("开发环境"),
                new Server().url("https://api.example.com").description("生产环境")
            ))
            .components(new Components()
                .addSecuritySchemes("bearer-jwt",
                    new SecurityScheme()
                        .type(SecurityScheme.Type.HTTP)
                        .scheme("bearer")
                        .bearerFormat("JWT")))
            .addSecurityItem(new SecurityRequirement().addList("bearer-jwt"));
    }
}
```

### 5.5.2 API注解使用

```java
@RestController
@RequestMapping("/api/users")
@Tag(name = "用户管理", description = "用户相关的API")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "获取用户列表", description = "分页获取用户列表")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "成功",
            content = @Content(schema = @Schema(implementation = Page.class))),
        @ApiResponse(responseCode = "400", description = "参数错误")
    })
    @GetMapping
    public ApiResponse<Page<UserDTO>> getUsers(
            @Parameter(description = "页码，从0开始") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "每页大小") @RequestParam(defaultValue = "20") int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<UserDTO> users = userService.findAll(pageable);
        return ApiResponse.success(users);
    }

    @Operation(summary = "获取用户详情", description = "根据ID获取用户详情")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "成功",
            content = @Content(schema = @Schema(implementation = UserDTO.class))),
        @ApiResponse(responseCode = "404", description = "用户不存在")
    })
    @GetMapping("/{id}")
    public ApiResponse<UserDTO> getUser(
            @Parameter(description = "用户ID", required = true) @PathVariable Long id) {
        UserDTO user = userService.findById(id);
        return ApiResponse.success(user);
    }

    @Operation(summary = "创建用户", description = "创建新用户")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "创建成功"),
        @ApiResponse(responseCode = "400", description = "参数验证失败")
    })
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResponse<UserDTO> createUser(
            @Parameter(description = "用户创建请求", required = true)
            @Valid @RequestBody UserCreateRequest request) {
        UserDTO user = userService.create(request);
        return ApiResponse.success("用户创建成功", user);
    }
}
```

### 5.5.3 Schema定义

```java
@Schema(description = "用户DTO")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDTO {

    @Schema(description = "用户ID", example = "1")
    private Long id;

    @Schema(description = "用户名", example = "john_doe", required = true)
    private String username;

    @Schema(description = "邮箱", example = "john@example.com", required = true)
    private String email;

    @Schema(description = "手机号", example = "13800138000")
    private String phoneNumber;

    @Schema(description = "性别", example = "MALE")
    private Gender gender;

    @Schema(description = "创建时间", example = "2024-01-01T00:00:00")
    private LocalDateTime createdAt;

    @Schema(description = "更新时间", example = "2024-01-01T00:00:00")
    private LocalDateTime updatedAt;
}

@Schema(description = "用户创建请求")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserCreateRequest {

    @Schema(description = "用户名", example = "john_doe", required = true,
            minLength = 3, maxLength = 20)
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20之间")
    private String username;

    @Schema(description = "密码", example = "Password123", required = true,
            pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d]{8,}$")
    @NotBlank(message = "密码不能为空")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d]{8,}$",
             message = "密码必须包含大小写字母和数字，至少8位")
    private String password;

    @Schema(description = "邮箱", example = "john@example.com", required = true)
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;
}
```

## 5.6 互联网大厂真实项目代码示例

### 5.6.1 阿里巴巴API设计

```java
package com.alibaba.openapi.controller;

import com.alibaba.common.result.Result;
import com.alibaba.openapi.dto.UserDTO;
import com.alibaba.openapi.request.UserCreateRequest;
import com.alibaba.openapi.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import javax.validation.constraints.Min;

@Tag(name = "用户管理", description = "用户管理相关接口")
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Validated
public class UserController {

    private final UserService userService;

    @Operation(summary = "分页查询用户列表")
    @GetMapping
    public Result<Page<UserDTO>> listUsers(
            @RequestParam(defaultValue = "0") @Min(0) Integer page,
            @RequestParam(defaultValue = "20") @Min(1) Integer size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<UserDTO> users = userService.listUsers(pageable);
        return Result.success(users);
    }

    @Operation(summary = "根据ID查询用户")
    @GetMapping("/{id}")
    public Result<UserDTO> getUser(@PathVariable Long id) {
        UserDTO user = userService.getUserById(id);
        return Result.success(user);
    }

    @Operation(summary = "创建用户")
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Result<UserDTO> createUser(@Valid @RequestBody UserCreateRequest request) {
        UserDTO user = userService.createUser(request);
        return Result.success(user);
    }

    @Operation(summary = "更新用户")
    @PutMapping("/{id}")
    public Result<UserDTO> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UserCreateRequest request) {
        UserDTO user = userService.updateUser(id, request);
        return Result.success(user);
    }

    @Operation(summary = "删除用户")
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
    }
}
```

### 5.6.2 腾讯云API响应封装

```java
package com.tencent.cloud.common.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;

import java.io.Serializable;

@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> implements Serializable {

    private static final long serialVersionUID = 1L;

    private Integer code;
    private String message;
    private T data;
    private String requestId;
    private Long timestamp;

    public ApiResponse() {
        this.timestamp = System.currentTimeMillis();
    }

    public ApiResponse(Integer code, String message) {
        this();
        this.code = code;
        this.message = message;
    }

    public ApiResponse(Integer code, String message, T data) {
        this(code, message);
        this.data = data;
    }

    public static <T> ApiResponse<T> success() {
        return new ApiResponse<>(200, "success");
    }

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(200, "success", data);
    }

    public static <T> ApiResponse<T> success(String message, T data) {
        return new ApiResponse<>(200, message, data);
    }

    public static <T> ApiResponse<T> error(Integer code, String message) {
        return new ApiResponse<>(code, message);
    }

    public static <T> ApiResponse<T> error(ErrorCode errorCode) {
        return new ApiResponse<>(errorCode.getCode(), errorCode.getMessage());
    }

    public ApiResponse<T> requestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
}
```

### 5.6.3 美团分页查询

```java
package com.meituan.api.controller;

import com.meituan.common.page.PageResult;
import com.meituan.common.request.PageRequest;
import com.meituan.dto.OrderDTO;
import com.meituan.service.OrderService;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @Operation(summary = "分页查询订单")
    @GetMapping
    public PageResult<OrderDTO> listOrders(PageRequest pageRequest) {
        return orderService.listOrders(pageRequest);
    }

    @Operation(summary = "根据用户ID查询订单")
    @GetMapping("/user/{userId}")
    public PageResult<OrderDTO> listOrdersByUserId(
            @PathVariable Long userId,
            PageRequest pageRequest) {
        return orderService.listOrdersByUserId(userId, pageRequest);
    }
}

@Data
public class PageRequest {
    private Integer pageNum = 1;
    private Integer pageSize = 20;
    private String orderBy = "created_at";
    private String order = "desc";

    public int getOffset() {
        return (pageNum - 1) * pageSize;
    }
}

@Data
public class PageResult<T> {
    private List<T> records;
    private Long total;
    private Integer pageNum;
    private Integer pageSize;
    private Integer pages;

    public static <T> PageResult<T> of(List<T> records, Long total, PageRequest pageRequest) {
        PageResult<T> result = new PageResult<>();
        result.setRecords(records);
        result.setTotal(total);
        result.setPageNum(pageRequest.getPageNum());
        result.setPageSize(pageRequest.getPageSize());
        result.setPages((int) Math.ceil((double) total / pageRequest.getPageSize()));
        return result;
    }
}
```

### 5.6.4 字节跳动批量操作

```java
package com.bytedance.api.controller;

import com.bytedance.common.result.Result;
import com.bytedance.dto.UserDTO;
import com.bytedance.request.UserBatchCreateRequest;
import com.bytedance.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Validated
public class UserController {

    private final UserService userService;

    @Operation(summary = "批量创建用户")
    @PostMapping("/batch")
    public Result<List<UserDTO>> batchCreateUsers(
            @Valid @RequestBody UserBatchCreateRequest request) {
        List<UserDTO> users = userService.batchCreateUsers(request.getUsers());
        return Result.success(users);
    }

    @Operation(summary = "批量更新用户")
    @PutMapping("/batch")
    public Result<List<UserDTO>> batchUpdateUsers(
            @Valid @RequestBody UserBatchCreateRequest request) {
        List<UserDTO> users = userService.batchUpdateUsers(request.getUsers());
        return Result.success(users);
    }

    @Operation(summary = "批量删除用户")
    @DeleteMapping("/batch")
    public Result<Void> batchDeleteUsers(@RequestBody List<Long> ids) {
        userService.batchDeleteUsers(ids);
        return Result.success();
    }
}

@Data
public class UserBatchCreateRequest {
    @Valid
    private List<UserCreateRequest> users;
}
```

### 5.6.5 京东健康版本控制

```java
package com.jd.health.api.v1;

import com.jd.health.common.result.Result;
import com.jd.health.dto.PatientDTO;
import com.jd.health.service.PatientService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "患者管理V1", description = "患者管理相关接口V1")
@RestController
@RequestMapping("/api/v1/patients")
@RequiredArgsConstructor
public class PatientV1Controller {

    private final PatientService patientService;

    @Operation(summary = "获取患者详情V1")
    @GetMapping("/{id}")
    public Result<PatientDTO> getPatient(@PathVariable Long id) {
        return Result.success(patientService.getPatientV1(id));
    }
}

package com.jd.health.api.v2;

import com.jd.health.common.result.Result;
import com.jd.health.dto.PatientV2DTO;
import com.jd.health.service.PatientService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "患者管理V2", description = "患者管理相关接口V2")
@RestController
@RequestMapping("/api/v2/patients")
@RequiredArgsConstructor
public class PatientV2Controller {

    private final PatientService patientService;

    @Operation(summary = "获取患者详情V2")
    @GetMapping("/{id}")
    public Result<PatientV2DTO> getPatient(@PathVariable Long id) {
        return Result.success(patientService.getPatientV2(id));
    }
}
```

### 5.6.6 拼多多HATEOAS实现

```java
package com.pdd.api.controller;

import com.pdd.dto.ProductDTO;
import com.pdd.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.hateoas.EntityModel;
import org.springframework.hateoas.Link;
import org.springframework.hateoas.server.mvc.WebMvcLinkBuilder;
import org.springframework.web.bind.annotation.*;

import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.linkTo;
import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.methodOn;

@RestController
@RequestMapping("/api/v1/products")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    @GetMapping("/{id}")
    public EntityModel<ProductDTO> getProduct(@PathVariable Long id) {
        ProductDTO product = productService.getProductById(id);

        EntityModel<ProductDTO> resource = EntityModel.of(product);

        Link selfLink = linkTo(methodOn(ProductController.class).getProduct(id)).withSelfRel();
        Link productsLink = linkTo(methodOn(ProductController.class).getProducts()).withRel("products");
        Link reviewsLink = linkTo(methodOn(ProductReviewController.class)
            .getProductReviews(id)).withRel("reviews");

        resource.add(selfLink, productsLink, reviewsLink);

        return resource;
    }

    @GetMapping
    public CollectionModel<EntityModel<ProductDTO>> getProducts() {
        List<ProductDTO> products = productService.getAllProducts();

        List<EntityModel<ProductDTO>> productResources = products.stream()
            .map(product -> {
                EntityModel<ProductDTO> resource = EntityModel.of(product);
                Link selfLink = linkTo(methodOn(ProductController.class)
                    .getProduct(product.getId())).withSelfRel();
                resource.add(selfLink);
                return resource;
            })
            .collect(Collectors.toList());

        CollectionModel<EntityModel<ProductDTO>> resource = CollectionModel.of(productResources);
        Link selfLink = linkTo(methodOn(ProductController.class).getProducts()).withSelfRel();
        resource.add(selfLink);

        return resource;
    }
}
```

## 5.7 最佳实践

1. **遵循RESTful设计原则**：使用正确的HTTP方法和URI设计
2. **统一响应格式**：提供一致的API响应结构
3. **完善的API文档**：使用Swagger/OpenAPI自动生成文档
4. **版本控制**：合理规划API版本演进
5. **参数验证**：使用Validation注解进行参数校验
6. **错误处理**：提供清晰的错误信息和错误码

## 5.8 小结

本章介绍了Spring Boot RESTful API开发的核心内容，包括：

- RESTful API设计原则
- 基础CRUD操作实现
- API版本控制
- HATEOAS实现
- API文档集成
- 批量操作

通过本章学习，你应该能够：

- 设计符合RESTful规范的API
- 实现完整的CRUD操作
- 进行API版本管理
- 集成API文档
- 实现批量操作

下一章将介绍Spring Boot的安全框架Spring Security。
