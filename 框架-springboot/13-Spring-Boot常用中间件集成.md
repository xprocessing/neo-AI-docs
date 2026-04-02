# 第13章：Spring Boot常用中间件集成

## 13.1 Elasticsearch集成

### 13.1.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-elasticsearch</artifactId>
</dependency>
```

### 13.1.2 Elasticsearch配置

```yaml
spring:
  elasticsearch:
    uris: http://localhost:9200
    username: elastic
    password: changeme
    connection-timeout: 5s
    socket-timeout: 30s
```

### 13.1.3 实体类定义

```java
@Document(indexName = "products")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProductDocument {

    @Id
    private String id;

    @Field(type = FieldType.Text, analyzer = "ik_max_word")
    private String name;

    @Field(type = FieldType.Keyword)
    private String category;

    @Field(type = FieldType.Double)
    private Double price;

    @Field(type = FieldType.Integer)
    private Integer stock;

    @Field(type = FieldType.Keyword)
    private String brand;

    @Field(type = FieldType.Text, analyzer = "ik_max_word")
    private String description;

    @Field(type = FieldType.Date)
    private LocalDateTime createdAt;

    @Field(type = FieldType.Date)
    private LocalDateTime updatedAt;
}
```

### 13.1.4 Repository接口

```java
@Repository
public interface ProductRepository extends ElasticsearchRepository<ProductDocument, String> {

    List<ProductDocument> findByNameContaining(String name);

    List<ProductDocument> findByCategory(String category);

    List<ProductDocument> findByBrand(String brand);

    List<ProductDocument> findByPriceBetween(Double minPrice, Double maxPrice);

    @Query("{\"bool\": {\"must\": [{\"match\": {\"name\": \"?0\"}}, {\"term\": {\"category\": \"?1\"}}]}}")
    List<ProductDocument> findByNameAndCategory(String name, String category);

    @Query("{\"range\": {\"price\": {\"gte\": ?0, \"lte\": ?1}}}")
    List<ProductDocument> findByPriceRange(Double minPrice, Double maxPrice);
}
```

### 13.1.5 服务实现

```java
@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    public ProductDocument save(ProductDocument product) {
        return productRepository.save(product);
    }

    public List<ProductDocument> saveAll(List<ProductDocument> products) {
        return productRepository.saveAll(products);
    }

    public Optional<ProductDocument> findById(String id) {
        return productRepository.findById(id);
    }

    public List<ProductDocument> findAll() {
        return productRepository.findAll();
    }

    public List<ProductDocument> search(String keyword) {
        return productRepository.findByNameContaining(keyword);
    }

    public List<ProductDocument> searchByCategory(String category) {
        return productRepository.findByCategory(category);
    }

    public List<ProductDocument> searchByPriceRange(Double minPrice, Double maxPrice) {
        return productRepository.findByPriceRange(minPrice, maxPrice);
    }

    public void deleteById(String id) {
        productRepository.deleteById(id);
    }

    public void deleteAll() {
        productRepository.deleteAll();
    }
}
```

## 13.2 MongoDB集成

### 13.2.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb</artifactId>
</dependency>
```

### 13.2.2 MongoDB配置

```yaml
spring:
  data:
    mongodb:
      host: localhost
      port: 27017
      database: demo
      username: admin
      password: admin
      authentication-database: admin
      auto-index-creation: true
```

### 13.2.3 实体类定义

```java
@Document(collection = "users")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {

    @Id
    private String id;

    @Indexed(unique = true)
    private String username;

    @Indexed(unique = true)
    private String email;

    private String password;

    private String phoneNumber;

    private Gender gender;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @DBRef
    private List<Order> orders;

    public enum Gender {
        MALE, FEMALE, OTHER
    }
}
```

### 13.2.4 Repository接口

```java
@Repository
public interface UserRepository extends MongoRepository<User, String> {

    Optional<User> findByUsername(String username);

    Optional<User> findByEmail(String email);

    List<User> findByGender(Gender gender);

    List<User> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);

    @Query("{'username': ?0}")
    Optional<User> findUserByUsername(String username);

    @Query("{'email': ?0, 'password': ?1}")
    Optional<User> findByEmailAndPassword(String email, String password);

    @Query("{'createdAt': {$gte: ?0, $lte: ?1}}")
    List<User> findUsersCreatedBetween(LocalDateTime start, LocalDateTime end);

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);

    long countByGender(Gender gender);
}
```

## 13.3 MinIO集成

### 13.3.1 依赖配置

```xml
<dependency>
    <groupId>io.minio</groupId>
    <artifactId>minio</artifactId>
    <version>8.5.7</version>
</dependency>
```

### 13.3.2 MinIO配置

```yaml
minio:
  endpoint: http://localhost:9000
  access-key: minioadmin
  secret-key: minioadmin
  bucket-name: demo-bucket
```

### 13.3.3 MinIO配置类

```java
@Configuration
public class MinioConfig {

    @Value("${minio.endpoint}")
    private String endpoint;

    @Value("${minio.access-key}")
    private String accessKey;

    @Value("${minio.secret-key}")
    private String secretKey;

    @Bean
    public MinioClient minioClient() {
        return MinioClient.builder()
            .endpoint(endpoint)
            .credentials(accessKey, secretKey)
            .build();
    }
}
```

### 13.3.4 文件服务

```java
@Service
@RequiredArgsConstructor
public class MinioService {

    @Value("${minio.bucket-name}")
    private String bucketName;

    private final MinioClient minioClient;

    public String uploadFile(MultipartFile file) throws Exception {
        String filename = UUID.randomUUID() + "-" + file.getOriginalFilename();

        minioClient.putObject(
            PutObjectArgs.builder()
                .bucket(bucketName)
                .object(filename)
                .stream(file.getInputStream(), file.getSize(), -1)
                .contentType(file.getContentType())
                .build()
        );

        return getFileUrl(filename);
    }

    public InputStream downloadFile(String filename) throws Exception {
        return minioClient.getObject(
            GetObjectArgs.builder()
                .bucket(bucketName)
                .object(filename)
                .build()
        );
    }

    public void deleteFile(String filename) throws Exception {
        minioClient.removeObject(
            RemoveObjectArgs.builder()
                .bucket(bucketName)
                .object(filename)
                .build()
        );
    }

    public String getFileUrl(String filename) {
        return minioClient.getPresignedObjectUrl(
            GetPresignedObjectUrlArgs.builder()
                .method(Method.GET)
                .bucket(bucketName)
                .object(filename)
                .expiry(60 * 60)
                .build()
        );
    }
}
```

## 13.4 OSS集成

### 13.4.1 依赖配置

```xml
<dependency>
    <groupId>com.aliyun.oss</groupId>
    <artifactId>aliyun-sdk-oss</artifactId>
    <version>3.17.4</version>
</dependency>
```

### 13.4.2 OSS配置

```yaml
aliyun:
  oss:
    endpoint: oss-cn-hangzhou.aliyuncs.com
    access-key-id: your-access-key-id
    access-key-secret: your-access-key-secret
    bucket-name: your-bucket-name
```

### 13.4.3 OSS配置类

```java
@Configuration
public class OssConfig {

    @Value("${aliyun.oss.endpoint}")
    private String endpoint;

    @Value("${aliyun.oss.access-key-id}")
    private String accessKeyId;

    @Value("${aliyun.oss.access-key-secret}")
    private String accessKeySecret;

    @Value("${aliyun.oss.bucket-name}")
    private String bucketName;

    @Bean
    public OSS ossClient() {
        return new OSSClientBuilder().build(endpoint, accessKeyId, accessKeySecret);
    }
}
```

### 13.4.4 OSS服务

```java
@Service
@RequiredArgsConstructor
public class OssService {

    @Value("${aliyun.oss.bucket-name}")
    private String bucketName;

    private final OSS ossClient;

    public String uploadFile(MultipartFile file) throws Exception {
        String filename = UUID.randomUUID() + "-" + file.getOriginalFilename();

        ossClient.putObject(
            bucketName,
            filename,
            file.getInputStream(),
            new ObjectMetadata()
        );

        return getFileUrl(filename);
    }

    public InputStream downloadFile(String filename) {
        return ossClient.getObject(bucketName, filename).getObjectContent();
    }

    public void deleteFile(String filename) {
        ossClient.deleteObject(bucketName, filename);
    }

    public String getFileUrl(String filename) {
        Date expiration = new Date(System.currentTimeMillis() + 3600 * 1000);
        URL url = ossClient.generatePresignedUrl(bucketName, filename, expiration);
        return url.toString();
    }
}
```

## 13.5 定时任务

### 13.5.1 定时任务配置

```java
@Configuration
@EnableScheduling
public class SchedulingConfig {

    @Bean
    public TaskScheduler taskScheduler() {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(10);
        scheduler.setThreadNamePrefix("scheduled-");
        scheduler.setWaitForTasksToCompleteOnShutdown(true);
        scheduler.setAwaitTerminationSeconds(60);
        return scheduler;
    }
}
```

### 13.5.2 定时任务实现

```java
@Service
public class ScheduledTaskService {

    @Autowired
    private UserService userService;

    @Scheduled(cron = "0 0 2 * * ?")
    public void cleanupExpiredUsers() {
        System.out.println("清理过期用户");
        userService.cleanupExpiredUsers();
    }

    @Scheduled(fixedRate = 60000)
    public void syncUserData() {
        System.out.println("同步用户数据");
        userService.syncUserData();
    }

    @Scheduled(fixedDelay = 300000)
    public void generateReport() {
        System.out.println("生成报表");
        userService.generateReport();
    }

    @Scheduled(initialDelay = 5000, fixedRate = 10000)
    public void healthCheck() {
        System.out.println("健康检查");
    }
}
```

### 13.5.3 动态定时任务

```java
@Service
public class DynamicScheduledTaskService {

    private final TaskScheduler taskScheduler;
    private final Map<String, ScheduledFuture<?>> scheduledTasks = new ConcurrentHashMap<>();

    public DynamicScheduledTaskService(TaskScheduler taskScheduler) {
        this.taskScheduler = taskScheduler;
    }

    public void addTask(String taskId, Runnable task, String cronExpression) {
        if (scheduledTasks.containsKey(taskId)) {
            removeTask(taskId);
        }

        CronTrigger trigger = new CronTrigger(cronExpression);
        ScheduledFuture<?> future = taskScheduler.schedule(task, trigger);
        scheduledTasks.put(taskId, future);
    }

    public void removeTask(String taskId) {
        ScheduledFuture<?> future = scheduledTasks.get(taskId);
        if (future != null) {
            future.cancel(false);
            scheduledTasks.remove(taskId);
        }
    }

    public void removeAllTasks() {
        scheduledTasks.values().forEach(future -> future.cancel(false));
        scheduledTasks.clear();
    }
}
```

## 13.6 邮件发送

### 13.6.1 邮件配置

```yaml
spring:
  mail:
    host: smtp.qq.com
    port: 587
    username: your-email@qq.com
    password: your-password
    protocol: smtp
    default-encoding: UTF-8
    properties:
      mail:
        smtp:
          auth: true
          starttls:
            enable: true
            required: true
          ssl:
            trust: smtp.qq.com
```

### 13.6.2 邮件服务

```java
@Service
public class EmailService {

    @Autowired
    private JavaMailSender mailSender;

    @Autowired
    private TemplateEngine templateEngine;

    public void sendSimpleEmail(String to, String subject, String text) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(to);
        message.setSubject(subject);
        message.setText(text);
        mailSender.send(message);
    }

    public void sendHtmlEmail(String to, String subject, String htmlContent) {
        MimeMessage message = mailSender.createMimeMessage();
        try {
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            helper.setTo(to);
            helper.setSubject(subject);
            helper.setText(htmlContent, true);
            mailSender.send(message);
        } catch (MessagingException e) {
            throw new RuntimeException("发送邮件失败", e);
        }
    }

    public void sendTemplateEmail(String to, String subject, String templateName, Map<String, Object> model) {
        Context context = new Context();
        context.setVariables(model);

        String htmlContent = templateEngine.process(templateName, context);
        sendHtmlEmail(to, subject, htmlContent);
    }

    public void sendAttachmentEmail(String to, String subject, String text, String filename, InputStream inputStream) {
        MimeMessage message = mailSender.createMimeMessage();
        try {
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            helper.setTo(to);
            helper.setSubject(subject);
            helper.setText(text, true);
            helper.addAttachment(filename, new InputStreamSource() {
                @Override
                public InputStream getInputStream() {
                    return inputStream;
                }

                @Override
                public String getFilename() {
                    return filename;
                }
            });
            mailSender.send(message);
        } catch (MessagingException e) {
            throw new RuntimeException("发送邮件失败", e);
        }
    }
}
```

## 13.7 短信发送

### 13.7.1 阿里云短信配置

```yaml
aliyun:
  sms:
    access-key-id: your-access-key-id
    access-key-secret: your-access-key-secret
    sign-name: your-sign-name
    template-code: your-template-code
```

### 13.7.2 短信服务

```java
@Service
public class SmsService {

    @Value("${aliyun.sms.access-key-id}")
    private String accessKeyId;

    @Value("${aliyun.sms.access-key-secret}")
    private String accessKeySecret;

    @Value("${aliyun.sms.sign-name}")
    private String signName;

    @Value("${aliyun.sms.template-code}")
    private String templateCode;

    public void sendSms(String phoneNumber, String code) {
        DefaultProfile profile = DefaultProfile.getProfile(
            "cn-hangzhou", accessKeyId, accessKeySecret);
        IAcsClient client = new DefaultAcsClient(profile);

        SendSmsRequest request = new SendSmsRequest();
        request.setPhoneNumbers(phoneNumber);
        request.setSignName(signName);
        request.setTemplateCode(templateCode);
        request.setTemplateParam("{\"code\":\"" + code + "\"}");

        try {
            SendSmsResponse response = client.getAcsResponse(request);
            System.out.println("短信发送成功：" + response.getCode());
        } catch (ServerException e) {
            e.printStackTrace();
        } catch (ClientException e) {
            e.printStackTrace();
        }
    }
}
```

## 13.8 互联网大厂真实项目代码示例

### 13.8.1 阿里巴巴Elasticsearch

```java
package com.alibaba.search;

import org.springframework.data.elasticsearch.annotations.Document;
import org.springframework.data.elasticsearch.annotations.Field;
import org.springframework.data.elasticsearch.annotations.FieldType;
import org.springframework.data.elasticsearch.annotations.Id;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;

@Document(indexName = "products")
public class ProductDocument {

    @Id
    private String id;

    @Field(type = FieldType.Text, analyzer = "ik_max_word")
    private String name;

    @Field(type = FieldType.Keyword)
    private String category;

    @Field(type = FieldType.Double)
    private Double price;
}

public interface ProductSearchRepository extends ElasticsearchRepository<ProductDocument, String> {

    List<ProductDocument> findByNameContaining(String name);

    List<ProductDocument> findByCategory(String category);
}
```

### 13.8.2 腾讯云MongoDB

```java
package com.tencent.cloud.document;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.DBRef;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.List;

@Document(collection = "users")
public class UserDocument {

    @Id
    private String id;

    private String username;

    private String email;

    private LocalDateTime createdAt;

    @DBRef
    private List<OrderDocument> orders;
}

@Document(collection = "orders")
public class OrderDocument {

    @Id
    private String id;

    private String userId;

    private Double totalAmount;

    private LocalDateTime createdAt;
}
```

### 13.8.3 美团MinIO

```java
package com.meituan.storage;

import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
public class MinioStorageService {

    @Value("${minio.endpoint}")
    private String endpoint;

    @Value("${minio.access-key}")
    private String accessKey;

    @Value("${minio.secret-key}")
    private String secretKey;

    @Value("${minio.bucket-name}")
    private String bucketName;

    public String uploadFile(MultipartFile file) throws Exception {
        MinioClient minioClient = MinioClient.builder()
            .endpoint(endpoint)
            .credentials(accessKey, secretKey)
            .build();

        String filename = System.currentTimeMillis() + "-" + file.getOriginalFilename();

        minioClient.putObject(
            PutObjectArgs.builder()
                .bucket(bucketName)
                .object(filename)
                .stream(file.getInputStream(), file.getSize(), -1)
                .contentType(file.getContentType())
                .build()
        );

        return getFileUrl(filename);
    }

    private String getFileUrl(String filename) {
        return endpoint + "/" + bucketName + "/" + filename;
    }
}
```

### 13.8.4 字节跳动定时任务

```java
package com.bytedance.schedule;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Service
public class DataSyncTask {

    @Scheduled(cron = "0 0 2 * * ?")
    public void syncUserData() {
        System.out.println("同步用户数据");
    }

    @Scheduled(fixedRate = 60000)
    public void syncOrderData() {
        System.out.println("同步订单数据");
    }

    @Scheduled(initialDelay = 5000, fixedDelay = 300000)
    public void syncProductData() {
        System.out.println("同步商品数据");
    }
}
```

### 13.8.5 京东健康邮件服务

```java
package com.jd.health.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    @Autowired
    private JavaMailSender mailSender;

    public void sendSimpleEmail(String to, String subject, String text) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(to);
        message.setSubject(subject);
        message.setText(text);
        mailSender.send(message);
    }

    public void sendVerificationEmail(String to, String code) {
        String subject = "邮箱验证";
        String text = "您的验证码是：" + code;
        sendSimpleEmail(to, subject, text);
    }
}
```

### 13.8.6 拼多多短信服务

```java
package com.pdd.sms;

import com.aliyuncs.DefaultAcsClient;
import com.aliyuncs.IAcsClient;
import com.aliyuncs.dysmsapi.model.v20170525.SendSmsRequest;
import com.aliyuncs.dysmsapi.model.v20170525.SendSmsResponse;
import com.aliyuncs.exceptions.ClientException;
import com.aliyuncs.exceptions.ServerException;
import com.aliyuncs.profile.DefaultProfile;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class SmsService {

    @Value("${aliyun.sms.access-key-id}")
    private String accessKeyId;

    @Value("${aliyun.sms.access-key-secret}")
    private String accessKeySecret;

    @Value("${aliyun.sms.sign-name}")
    private String signName;

    @Value("${aliyun.sms.template-code}")
    private String templateCode;

    public void sendSms(String phoneNumber, String code) {
        DefaultProfile profile = DefaultProfile.getProfile(
            "cn-hangzhou", accessKeyId, accessKeySecret);
        IAcsClient client = new DefaultAcsClient(profile);

        SendSmsRequest request = new SendSmsRequest();
        request.setPhoneNumbers(phoneNumber);
        request.setSignName(signName);
        request.setTemplateCode(templateCode);
        request.setTemplateParam("{\"code\":\"" + code + "\"}");

        try {
            SendSmsResponse response = client.getAcsResponse(request);
            System.out.println("短信发送成功：" + response.getCode());
        } catch (ServerException e) {
            e.printStackTrace();
        } catch (ClientException e) {
            e.printStackTrace();
        }
    }
}
```

## 13.9 最佳实践

1. **合理选择中间件**：根据业务需求选择合适的中间件
2. **配置优化**：优化中间件配置提升性能
3. **异常处理**：完善的异常处理机制
4. **监控告警**：监控中间件运行状态
5. **安全配置**：合理配置访问权限
6. **备份恢复**：建立备份和恢复机制

## 13.10 小结

本章介绍了Spring Boot常用中间件集成的核心内容，包括：

- Elasticsearch集成
- MongoDB集成
- MinIO集成
- OSS集成
- 定时任务
- 邮件发送
- 短信发送

通过本章学习，你应该能够：

- 集成Elasticsearch进行全文搜索
- 使用MongoDB进行文档存储
- 集成MinIO和OSS进行文件存储
- 实现定时任务
- 发送邮件和短信

下一章将介绍Spring Boot的测试。
