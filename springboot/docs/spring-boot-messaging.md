# Spring Boot 消息队列

Spring Boot 提供了对多种消息队列的支持，包括 RabbitMQ、Apache Kafka、ActiveMQ 等。本章将详细介绍如何在 Spring Boot 应用中使用消息队列。

## RabbitMQ 集成

### 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

### RabbitMQ 配置

```java
@Configuration
@EnableRabbit
public class RabbitConfig {
    
    // 队列名称
    public static final String USER_QUEUE = "user.queue";
    public static final String USER_EXCHANGE = "user.exchange";
    public static final String USER_ROUTING_KEY = "user.routing.key";
    
    // 创建队列
    @Bean
    public Queue userQueue() {
        return QueueBuilder.durable(USER_QUEUE).build();
    }
    
    // 创建交换机
    @Bean
    public TopicExchange userExchange() {
        return new TopicExchange(USER_EXCHANGE);
    }
    
    // 绑定队列到交换机
    @Bean
    public Binding userBinding(Queue userQueue, TopicExchange userExchange) {
        return BindingBuilder.bind(userQueue)
            .to(userExchange)
            .with(USER_ROUTING_KEY);
    }
    
    // 消息转换器
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }
    
    // RabbitMQ 连接工厂配置
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(jsonMessageConverter());
        return template;
    }
}
```

### 发送消息

```java
@Service
public class RabbitMQProducer {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    public void sendUserMessage(User user) {
        // 发送消息到队列
        rabbitTemplate.convertAndSend(RabbitConfig.USER_EXCHANGE, 
            RabbitConfig.USER_ROUTING_KEY, user);
    }
    
    public void sendUserMessageWithProperties(User user) {
        // 创建消息属性
        MessageProperties properties = new MessageProperties();
        properties.setHeader("type", "user_created");
        properties.setTimestamp(new Date());
        
        // 创建消息
        Message message = MessageBuilder
            .withBody(JsonUtils.toJson(user).getBytes())
            .andProperties(properties)
            .build();
        
        // 发送消息
        rabbitTemplate.send(RabbitConfig.USER_EXCHANGE, 
            RabbitConfig.USER_ROUTING_KEY, message);
    }
    
    // 异步发送并处理响应
    public CompletableFuture<String> sendAsyncUserMessage(User user) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                rabbitTemplate.convertAndSend(RabbitConfig.USER_EXCHANGE, 
                    RabbitConfig.USER_ROUTING_KEY, user);
                return "Message sent successfully";
            } catch (Exception e) {
                return "Error sending message: " + e.getMessage();
            }
        });
    }
}
```

### 接收消息

```java
@Component
public class RabbitMQConsumer {
    
    private static final Logger logger = LoggerFactory.getLogger(RabbitMQConsumer.class);
    
    @RabbitListener(queues = RabbitConfig.USER_QUEUE)
    public void receiveUserMessage(User user) {
        logger.info("Received user: {}", user.getUsername());
        // 处理用户消息
        processUser(user);
    }
    
    // 带异常处理的消息接收
    @RabbitListener(queues = RabbitConfig.USER_QUEUE)
    public void receiveUserMessageWithErrorHandling(User user, Channel channel, 
                                                  org.springframework.amqp.core.Message message) {
        try {
            logger.info("Processing user: {}", user.getUsername());
            processUser(user);
            
            // 手动确认消息
            channel.basicAck(message.getMessageProperties().getDeliveryTag(), false);
        } catch (Exception e) {
            logger.error("Error processing message", e);
            try {
                // 拒绝消息并重新入队
                channel.basicNack(message.getMessageProperties().getDeliveryTag(), 
                    false, true);
            } catch (IOException ioException) {
                logger.error("Error rejecting message", ioException);
            }
        }
    }
    
    // 接收带消息头的信息
    @RabbitListener(queues = RabbitConfig.USER_QUEUE)
    public void receiveUserMessageWithHeaders(@Payload User user, 
                                           @Header("type") String messageType,
                                           @Header(MessageProperties.CONSUMER_QUEUE) String queue) {
        logger.info("Received message of type: {} from queue: {}", messageType, queue);
        processUser(user);
    }
    
    private void processUser(User user) {
        // 实际的业务处理逻辑
        logger.info("Processing user: {} with email: {}", user.getUsername(), user.getEmail());
    }
}
```

## Apache Kafka 集成

### 依赖配置

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

### Kafka 配置

```java
@Configuration
@EnableKafka
public class KafkaConfig {
    
    public static final String USER_TOPIC = "user-topic";
    public static final String USER_GROUP_ID = "user-group";
    
    @Bean
    public ProducerFactory<String, Object> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.RETRIES_CONFIG, 3);
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
        props.put(ProducerConfig.LINGER_MS_CONFIG, 1);
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 33554432);
        
        return new DefaultKafkaProducerFactory<>(props);
    }
    
    @Bean
    public KafkaTemplate<String, Object> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }
    
    @Bean
    public ConsumerFactory<String, Object> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, USER_GROUP_ID);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(JsonDeserializer.VALUE_DEFAULT_TYPE, Object.class);
        props.put(JsonDeserializer.TRUSTED_PACKAGES, "com.example.model");
        
        return new DefaultKafkaConsumerFactory<>(props);
    }
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> 
           kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, Object> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        factory.setConcurrency(3); // 设置并发消费者数量
        factory.getContainerProperties().setPollTimeout(3000);
        return factory;
    }
}
```

### Kafka 生产者

```java
@Service
public class KafkaProducer {
    
    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;
    
    public void sendUserEvent(User user) {
        // 创建消息
        UserEvent event = new UserEvent();
        event.setUserId(user.getId());
        event.setUsername(user.getUsername());
        event.setAction("USER_CREATED");
        event.setTimestamp(new Date());
        
        // 发送消息
        kafkaTemplate.send(KafkaConfig.USER_TOPIC, user.getId().toString(), event);
    }
    
    public CompletableFuture<SendResult<String, Object>> sendUserEventAsync(User user) {
        UserEvent event = new UserEvent();
        event.setUserId(user.getId());
        event.setUsername(user.getUsername());
        event.setAction("USER_UPDATED");
        event.setTimestamp(new Date());
        
        ProducerRecord<String, Object> record = new ProducerRecord<>(
            KafkaConfig.USER_TOPIC, user.getId().toString(), event);
        
        return kafkaTemplate.send(record)
            .addCallback(
                result -> System.out.println("Sent message=[" + event + 
                    "] with offset=[" + result.getRecordMetadata().offset() + "]"),
                failure -> System.out.println("Unable to send message=[" + 
                    event + "] due to : " + failure.getMessage())
            );
    }
    
    // 发送带自定义头的消息
    public void sendUserEventWithHeaders(User user) {
        UserEvent event = new UserEvent();
        event.setUserId(user.getId());
        event.setUsername(user.getUsername());
        event.setAction("USER_DELETED");
        event.setTimestamp(new Date());
        
        // 创建消息头
        Headers headers = new RecordHeaders();
        headers.add("event-type", "user-operation".getBytes());
        headers.add("source", "user-service".getBytes());
        
        ProducerRecord<String, Object> record = new ProducerRecord<>(
            KafkaConfig.USER_TOPIC, null, user.getId().toString(), event, headers);
        
        kafkaTemplate.send(record);
    }
}
```

### Kafka 消费者

```java
@Component
public class KafkaConsumer {
    
    private static final Logger logger = LoggerFactory.getLogger(KafkaConsumer.class);
    
    @KafkaListener(topics = KafkaConfig.USER_TOPIC, groupId = KafkaConfig.USER_GROUP_ID)
    public void consumeUserEvent(UserEvent event) {
        logger.info("Consumed user event: {}", event);
        processUserEvent(event);
    }
    
    // 消费带消息头的事件
    @KafkaListener(topics = KafkaConfig.USER_TOPIC, groupId = KafkaConfig.USER_GROUP_ID)
    public void consumeUserEventWithHeaders(ConsumerRecord<String, UserEvent> record) {
        UserEvent event = record.value();
        Headers headers = record.headers();
        
        logger.info("Consumed event: {} with headers: {}", event, 
            headers.toArray().length > 0 ? Arrays.toString(headers.toArray()) : "none");
        
        processUserEvent(event);
    }
    
    // 批量消费
    @KafkaListener(topics = KafkaConfig.USER_TOPIC, groupId = KafkaConfig.USER_GROUP_ID)
    public void consumeUserEventsBatch(List<ConsumerRecord<String, UserEvent>> records) {
        logger.info("Consuming batch of {} events", records.size());
        
        for (ConsumerRecord<String, UserEvent> record : records) {
            UserEvent event = record.value();
            logger.info("Processing event: {}", event);
            processUserEvent(event);
        }
    }
    
    // 错误处理
    @KafkaListener(topics = KafkaConfig.USER_TOPIC, groupId = KafkaConfig.USER_GROUP_ID)
    public void consumeUserEventWithErrorHandling(
            ConsumerRecord<String, UserEvent> record,
            Acknowledgment acknowledgment) {
        try {
            UserEvent event = record.value();
            logger.info("Processing event: {}", event);
            processUserEvent(event);
            
            // 手动确认消息
            acknowledgment.acknowledge();
        } catch (Exception e) {
            logger.error("Error processing event: {}", record.value(), e);
            // 不确认消息，让其重新消费
        }
    }
    
    private void processUserEvent(UserEvent event) {
        switch (event.getAction()) {
            case "USER_CREATED":
                logger.info("Processing user creation: {}", event.getUsername());
                break;
            case "USER_UPDATED":
                logger.info("Processing user update: {}", event.getUsername());
                break;
            case "USER_DELETED":
                logger.info("Processing user deletion: {}", event.getUsername());
                break;
            default:
                logger.warn("Unknown action: {}", event.getAction());
        }
    }
}
```

## 消息监听器配置

### 自定义监听器容器工厂

```java
@Configuration
public class CustomKafkaListenerConfig {
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> 
           retryKafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, Object> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        
        // 设置错误处理器，包含重试逻辑
        factory.setCommonErrorHandler(new DefaultErrorHandler(
            new DeadLetterPublishingRecoverer(kafkaTemplate()),
            new FixedBackOff(1000L, 3))); // 重试3次，间隔1秒
        
        return factory;
    }
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> 
           manualAckKafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, Object> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        
        // 启用手动确认
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL);
        
        return factory;
    }
}
```

### 带重试机制的消费者

```java
@Component
public class RetryableKafkaConsumer {
    
    private static final Logger logger = LoggerFactory.getLogger(RetryableKafkaConsumer.class);
    
    @KafkaListener(
        topics = KafkaConfig.USER_TOPIC, 
        groupId = "retry-group",
        containerFactory = "retryKafkaListenerContainerFactory")
    public void consumeWithRetry(UserEvent event, Exception exception) {
        logger.info("Processing event with retry: {}", event);
        
        if (event.getUserId() == null) {
            throw new IllegalArgumentException("User ID cannot be null");
        }
        
        // 业务处理逻辑
        processUserEvent(event);
    }
    
    @KafkaListener(
        topics = KafkaConfig.USER_TOPIC, 
        groupId = "manual-ack-group",
        containerFactory = "manualAckKafkaListenerContainerFactory")
    public void consumeWithManualAck(UserEvent event, Acknowledgment acknowledgment) {
        try {
            logger.info("Processing event with manual ack: {}", event);
            processUserEvent(event);
            
            // 手动确认
            acknowledgment.acknowledge();
        } catch (Exception e) {
            logger.error("Error processing event: {}", event, e);
            // 不确认消息，将重新消费
        }
    }
    
    private void processUserEvent(UserEvent event) {
        // 模拟可能失败的业务逻辑
        if (event.getUsername() != null && event.getUsername().contains("error")) {
            throw new RuntimeException("Simulated processing error");
        }
        
        logger.info("Successfully processed event: {}", event);
    }
}
```

## 消息模型

### 用户事件模型

```java
public class UserEvent implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Long userId;
    private String username;
    private String action; // USER_CREATED, USER_UPDATED, USER_DELETED
    private Date timestamp;
    private Map<String, Object> additionalData;
    
    // constructors, getters and setters
    public UserEvent() {
        this.additionalData = new HashMap<>();
    }
    
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public Date getTimestamp() { return timestamp; }
    public void setTimestamp(Date timestamp) { this.timestamp = timestamp; }
    public Map<String, Object> getAdditionalData() { return additionalData; }
    public void setAdditionalData(Map<String, Object> additionalData) { 
        this.additionalData = additionalData; 
    }
}
```

### 消息处理器

```java
@Service
public class MessageHandler {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private NotificationService notificationService;
    
    // 处理用户创建事件
    public void handleUserCreated(UserEvent event) {
        User user = userService.findById(event.getUserId());
        if (user != null) {
            // 发送欢迎邮件
            notificationService.sendWelcomeEmail(user.getEmail(), user.getUsername());
            
            // 记录用户活动
            logUserActivity(event.getUserId(), "USER_CREATED", event.getTimestamp());
        }
    }
    
    // 处理用户更新事件
    public void handleUserUpdated(UserEvent event) {
        // 更新用户相关缓存
        userService.clearUserCache(event.getUserId());
        
        // 通知相关服务
        notificationService.notifyUserUpdated(event.getUserId());
    }
    
    // 处理用户删除事件
    public void handleUserDeleted(UserEvent event) {
        // 清理用户相关数据
        userService.cleanupUserData(event.getUserId());
        
        // 发送删除确认
        notificationService.sendDeletionConfirmation(event.getUserId());
    }
    
    private void logUserActivity(Long userId, String action, Date timestamp) {
        // 记录用户活动日志
        System.out.println("User activity - ID: " + userId + 
            ", Action: " + action + ", Time: " + timestamp);
    }
}
```

## 消息队列监控

### 消息统计服务

```java
@Component
public class MessageStatsService {
    
    private final MeterRegistry meterRegistry;
    private final Counter messageProcessedCounter;
    private final Timer messageProcessingTimer;
    
    public MessageStatsService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.messageProcessedCounter = Counter.builder("messages.processed")
            .description("Number of processed messages")
            .register(meterRegistry);
        this.messageProcessingTimer = Timer.builder("message.processing.duration")
            .description("Message processing duration")
            .register(meterRegistry);
    }
    
    public void recordMessageProcessed(String messageType) {
        messageProcessedCounter.increment(Tags.of("type", messageType));
    }
    
    public <T> T timeMessageProcessing(Supplier<T> operation) {
        return messageProcessingTimer.recordCallable(operation::get);
    }
}
```

### 带监控的消费者

```java
@Component
public class MonitoredKafkaConsumer {
    
    private static final Logger logger = LoggerFactory.getLogger(MonitoredKafkaConsumer.class);
    
    @Autowired
    private MessageStatsService messageStatsService;
    
    @KafkaListener(topics = KafkaConfig.USER_TOPIC, groupId = "monitored-group")
    public void consumeWithMetrics(UserEvent event) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            logger.info("Processing event: {}", event);
            
            // 实际业务处理
            processUserEvent(event);
            
            // 记录指标
            messageStatsService.recordMessageProcessed(event.getAction());
            
        } catch (Exception e) {
            logger.error("Error processing event: {}", event, e);
            // 可以记录错误指标
            Counter.builder("messages.errors")
                .tags("type", event.getAction())
                .register(meterRegistry)
                .increment();
            throw e;
        } finally {
            sample.stop(Timer.builder("message.processing.time")
                .tags("type", event.getAction())
                .register(meterRegistry));
        }
    }
    
    private void processUserEvent(UserEvent event) {
        // 业务逻辑处理
        logger.info("Successfully processed event: {}", event);
    }
}
```