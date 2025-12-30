# 第8章：Spring Boot消息队列（RabbitMQ/Kafka）

## 8.1 消息队列概述

### 8.1.1 为什么需要消息队列

- **异步处理**：提升系统响应速度
- **削峰填谷**：平滑流量高峰
- **解耦系统**：降低系统耦合度
- **可靠传输**：保证消息可靠送达

### 8.1.2 常见消息队列对比

| 特性 | RabbitMQ | Kafka | RocketMQ |
|------|----------|-------|----------|
| 吞吐量 | 中等 | 高 | 高 |
| 延迟 | 低 | 中 | 低 |
| 可靠性 | 高 | 高 | 高 |
| 复杂度 | 中 | 高 | 中 |
| 适用场景 | 业务消息 | 日志、流数据 | 业务消息 |

## 8.2 RabbitMQ集成

### 8.2.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

### 8.2.2 RabbitMQ配置

```yaml
spring:
  rabbitmq:
    host: localhost
    port: 5672
    username: guest
    password: guest
    virtual-host: /
    connection-timeout: 15000
    publisher-confirm-type: correlated
    publisher-returns: true
    listener:
      simple:
        acknowledge-mode: manual
        concurrency: 5
        max-concurrency: 10
        prefetch: 1
        default-requeue-rejected: false
```

### 8.2.3 RabbitMQ配置类

```java
@Configuration
public class RabbitMQConfig {

    public static final String EXCHANGE_NAME = "spring-boot-exchange";
    public static final String QUEUE_NAME = "spring-boot-queue";
    public static final String ROUTING_KEY = "spring-boot.routing.key";

    @Bean
    public Queue queue() {
        return QueueBuilder.durable(QUEUE_NAME)
            .withArgument("x-max-length", 10000)
            .withArgument("x-message-ttl", 60000)
            .build();
    }

    @Bean
    public TopicExchange exchange() {
        return new TopicExchange(EXCHANGE_NAME, true, false);
    }

    @Bean
    public Binding binding(Queue queue, TopicExchange exchange) {
        return BindingBuilder.bind(queue)
            .to(exchange)
            .with(ROUTING_KEY);
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setConfirmCallback((correlationData, ack, cause) -> {
            if (ack) {
                System.out.println("消息发送成功");
            } else {
                System.out.println("消息发送失败: " + cause);
            }
        });

        rabbitTemplate.setReturnsCallback(returned -> {
            System.out.println("消息未路由到队列: " + returned.getMessage());
        });

        rabbitTemplate.setMessageConverter(new Jackson2JsonMessageConverter());
        return rabbitTemplate;
    }

    @Bean
    public Jackson2JsonMessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();
    }
}
```

### 8.2.4 消息生产者

```java
@Service
@RequiredArgsConstructor
public class MessageProducer {

    private final RabbitTemplate rabbitTemplate;

    public void sendMessage(String message) {
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.EXCHANGE_NAME,
            RabbitMQConfig.ROUTING_KEY,
            message
        );
    }

    public void sendObjectMessage(Object message) {
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.EXCHANGE_NAME,
            RabbitMQConfig.ROUTING_KEY,
            message
        );
    }

    public void sendMessageWithDelay(String message, long delayMillis) {
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.EXCHANGE_NAME,
            RabbitMQConfig.ROUTING_KEY,
            message,
            msg -> {
                msg.getMessageProperties().setDelay((int) delayMillis);
                return msg;
            }
        );
    }

    public void sendMessageWithCorrelationId(String message, String correlationId) {
        CorrelationData correlationData = new CorrelationData(correlationId);
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.EXCHANGE_NAME,
            RabbitMQConfig.ROUTING_KEY,
            message,
            correlationData
        );
    }
}
```

### 8.2.5 消息消费者

```java
@Component
@Slf4j
public class MessageConsumer {

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void receiveMessage(String message) {
        log.info("接收到消息: {}", message);
    }

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void receiveObjectMessage(User user) {
        log.info("接收到用户消息: {}", user);
    }

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void receiveMessageManualAck(Message message, Channel channel) throws IOException {
        long deliveryTag = message.getMessageProperties().getDeliveryTag();
        try {
            String msg = new String(message.getBody());
            log.info("接收到消息: {}", msg);

            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            log.error("消息处理失败", e);
            channel.basicNack(deliveryTag, false, true);
        }
    }

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME, containerFactory = "rabbitListenerContainerFactory")
    public void receiveMessageWithRetry(String message) {
        log.info("接收到消息: {}", message);
    }
}
```

### 8.2.6 死信队列配置

```java
@Configuration
public class DeadLetterQueueConfig {

    public static final String DLX_EXCHANGE = "dlx.exchange";
    public static final String DLX_QUEUE = "dlx.queue";
    public static final String DLX_ROUTING_KEY = "dlx.routing.key";

    @Bean
    public Queue dlxQueue() {
        return QueueBuilder.durable(DLX_QUEUE).build();
    }

    @Bean
    public DirectExchange dlxExchange() {
        return new DirectExchange(DLX_EXCHANGE, true, false);
    }

    @Bean
    public Binding dlxBinding(Queue dlxQueue, DirectExchange dlxExchange) {
        return BindingBuilder.bind(dlxQueue).to(dlxExchange).with(DLX_ROUTING_KEY);
    }

    @Bean
    public Queue mainQueue() {
        return QueueBuilder.durable(RabbitMQConfig.QUEUE_NAME)
            .withArgument("x-dead-letter-exchange", DLX_EXCHANGE)
            .withArgument("x-dead-letter-routing-key", DLX_ROUTING_KEY)
            .withArgument("x-max-retries", 3)
            .build();
    }
}

@Component
public class DeadLetterConsumer {

    @RabbitListener(queues = DeadLetterQueueConfig.DLX_QUEUE)
    public void handleDeadLetterMessage(Message message) {
        log.info("接收到死信消息: {}", new String(message.getBody()));
    }
}
```

## 8.3 Kafka集成

### 8.3.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

### 8.3.2 Kafka配置

```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: spring-boot-group
      auto-offset-reset: earliest
      enable-auto-commit: false
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      max-poll-records: 100
      properties:
        session.timeout.ms: 30000
        max.poll.interval.ms: 300000
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
      acks: all
      retries: 3
      batch-size: 16384
      buffer-memory: 33554432
      properties:
        enable.idempotence: true
    listener:
      ack-mode: manual_immediate
      concurrency: 3
```

### 8.3.3 Kafka配置类

```java
@Configuration
public class KafkaConfig {

    @Bean
    public ProducerFactory<String, String> producerFactory(KafkaProperties properties) {
        Map<String, Object> configProps = new HashMap<>();
        configProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, properties.getBootstrapServers());
        configProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        configProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        configProps.put(ProducerConfig.ACKS_CONFIG, "all");
        configProps.put(ProducerConfig.RETRIES_CONFIG, 3);
        configProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        return new DefaultKafkaProducerFactory<>(configProps);
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplate(ProducerFactory<String, String> producerFactory) {
        return new KafkaTemplate<>(producerFactory);
    }

    @Bean
    public ConsumerFactory<String, String> consumerFactory(KafkaProperties properties) {
        Map<String, Object> configProps = new HashMap<>();
        configProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, properties.getBootstrapServers());
        configProps.put(ConsumerConfig.GROUP_ID_CONFIG, properties.getConsumer().getGroupId());
        configProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        configProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        configProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        configProps.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        return new DefaultKafkaConsumerFactory<>(configProps);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(
            ConsumerFactory<String, String> consumerFactory) {
        ConcurrentKafkaListenerContainerFactory<String, String> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        factory.setConcurrency(3);
        return factory;
    }
}
```

### 8.3.4 Kafka生产者

```java
@Service
@RequiredArgsConstructor
public class KafkaProducer {

    private final KafkaTemplate<String, String> kafkaTemplate;

    public void sendMessage(String topic, String message) {
        kafkaTemplate.send(topic, message);
    }

    public void sendMessage(String topic, String key, String message) {
        kafkaTemplate.send(topic, key, message);
    }

    public void sendMessageAsync(String topic, String message) {
        kafkaTemplate.send(topic, message).addCallback(
            result -> System.out.println("消息发送成功"),
            failure -> System.out.println("消息发送失败: " + failure.getMessage())
        );
    }

    public void sendMessageWithHeaders(String topic, String message, Map<String, String> headers) {
        ProducerRecord<String, String> record = new ProducerRecord<>(topic, message);
        headers.forEach(record.headers()::add);
        kafkaTemplate.send(record);
    }

    public void sendObjectMessage(String topic, Object message) {
        String json = JsonUtils.toJson(message);
        kafkaTemplate.send(topic, json);
    }
}
```

### 8.3.5 Kafka消费者

```java
@Component
@Slf4j
public class KafkaConsumer {

    @KafkaListener(topics = "test-topic", groupId = "spring-boot-group")
    public void consumeMessage(String message) {
        log.info("接收到消息: {}", message);
    }

    @KafkaListener(topics = "test-topic", groupId = "spring-boot-group")
    public void consumeMessageWithHeaders(
            @Payload String message,
            @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
            @Header(KafkaHeaders.RECEIVED_PARTITION_ID) int partition,
            @Header(KafkaHeaders.OFFSET) long offset) {
        log.info("接收到消息 - Topic: {}, Partition: {}, Offset: {}, Message: {}",
            topic, partition, offset, message);
    }

    @KafkaListener(topics = "test-topic", groupId = "spring-boot-group")
    public void consumeMessageManualAck(
            @Payload String message,
            Acknowledgment acknowledgment) {
        try {
            log.info("接收到消息: {}", message);
            acknowledgment.acknowledge();
        } catch (Exception e) {
            log.error("消息处理失败", e);
        }
    }

    @KafkaListener(topics = "test-topic", groupId = "spring-boot-group")
    public void consumeObjectMessage(User user) {
        log.info("接收到用户消息: {}", user);
    }
}
```

### 8.3.6 Kafka事务

```java
@Service
@RequiredArgsConstructor
public class KafkaTransactionService {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final UserRepository userRepository;

    @Transactional
    public void sendTransactionalMessage(Long userId, String message) {
        User user = userRepository.findById(userId).orElseThrow();
        user.setStatus("PROCESSED");
        userRepository.save(user);

        kafkaTemplate.send("user-events", message);
    }

    @KafkaListener(topics = "user-events", groupId = "user-processor-group")
    @Transactional
    public void processUserEvent(String event) {
        UserEvent userEvent = JsonUtils.fromJson(event, UserEvent.class);
        User user = userRepository.findById(userEvent.getUserId()).orElseThrow();
        user.setStatus(event.getStatus());
        userRepository.save(user);
    }
}
```

## 8.4 消息可靠性保证

### 8.4.1 消息持久化

```java
@Configuration
public class ReliableRabbitMQConfig {

    @Bean
    public Queue durableQueue() {
        return QueueBuilder.durable("durable.queue")
            .build();
    }

    @Bean
    public DirectExchange durableExchange() {
        return new DirectExchange("durable.exchange", true, false);
    }

    @Bean
    public Binding durableBinding() {
        return BindingBuilder.bind(durableQueue())
            .to(durableExchange())
            .with("durable.routing.key");
    }
}
```

### 8.4.2 消息确认机制

```java
@Component
public class ReliableMessageConsumer {

    @RabbitListener(queues = "reliable.queue")
    public void handleMessage(Message message, Channel channel) throws IOException {
        long deliveryTag = message.getMessageProperties().getDeliveryTag();
        try {
            String msg = new String(message.getBody());
            processMessage(msg);
            channel.basicAck(deliveryTag, false);
        } catch (BusinessException e) {
            log.warn("业务异常，拒绝消息: {}", e.getMessage());
            channel.basicReject(deliveryTag, false);
        } catch (Exception e) {
            log.error("系统异常，重新入队", e);
            channel.basicNack(deliveryTag, false, true);
        }
    }

    private void processMessage(String message) {
    }
}
```

### 8.4.3 消息重试机制

```java
@Configuration
public class RetryConfig {

    @Bean
    public RetryTemplate retryTemplate() {
        RetryTemplate retryTemplate = new RetryTemplate();

        FixedBackOffPolicy backOffPolicy = new FixedBackOffPolicy();
        backOffPolicy.setBackOffPeriod(2000);

        SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy();
        retryPolicy.setMaxAttempts(3);

        retryTemplate.setBackOffPolicy(backOffPolicy);
        retryTemplate.setRetryPolicy(retryPolicy);

        return retryTemplate;
    }
}

@Service
@RequiredArgsConstructor
public class RetryMessageService {

    private final RetryTemplate retryTemplate;

    public void processMessageWithRetry(String message) {
        retryTemplate.execute(context -> {
            processMessage(message);
            return null;
        });
    }

    private void processMessage(String message) {
    }
}
```

## 8.5 互联网大厂真实项目代码示例

### 8.5.1 阿里巴巴RabbitMQ配置

```java
package com.alibaba.mq.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    public static final String ORDER_EXCHANGE = "order.exchange";
    public static final String ORDER_QUEUE = "order.queue";
    public static final String ORDER_ROUTING_KEY = "order.routing.key";

    public static final String PAYMENT_EXCHANGE = "payment.exchange";
    public static final String PAYMENT_QUEUE = "payment.queue";
    public static final String PAYMENT_ROUTING_KEY = "payment.routing.key";

    @Bean
    public Queue orderQueue() {
        return QueueBuilder.durable(ORDER_QUEUE)
            .withArgument("x-max-length", 100000)
            .withArgument("x-message-ttl", 86400000)
            .build();
    }

    @Bean
    public TopicExchange orderExchange() {
        return new TopicExchange(ORDER_EXCHANGE, true, false);
    }

    @Bean
    public Binding orderBinding() {
        return BindingBuilder.bind(orderQueue())
            .to(orderExchange())
            .with(ORDER_ROUTING_KEY);
    }

    @Bean
    public Queue paymentQueue() {
        return QueueBuilder.durable(PAYMENT_QUEUE)
            .withArgument("x-max-length", 100000)
            .withArgument("x-message-ttl", 86400000)
            .build();
    }

    @Bean
    public TopicExchange paymentExchange() {
        return new TopicExchange(PAYMENT_EXCHANGE, true, false);
    }

    @Bean
    public Binding paymentBinding() {
        return BindingBuilder.bind(paymentQueue())
            .to(paymentExchange())
            .with(PAYMENT_ROUTING_KEY);
    }

    @Bean
    public MessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(messageConverter());
        rabbitTemplate.setConfirmCallback((correlationData, ack, cause) -> {
            if (ack) {
                System.out.println("消息发送成功");
            } else {
                System.out.println("消息发送失败: " + cause);
            }
        });
        rabbitTemplate.setReturnsCallback(returned -> {
            System.out.println("消息未路由到队列");
        });
        return rabbitTemplate;
    }
}
```

### 8.5.2 腾讯云Kafka配置

```java
package com.tencent.cloud.kafka.config;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.*;
import org.springframework.kafka.listener.ContainerProperties;

import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableKafka
public class KafkaConfig {

    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;

    @Bean
    public ProducerFactory<String, String> producerFactory() {
        Map<String, Object> configProps = new HashMap<>();
        configProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        configProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        configProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        configProps.put(ProducerConfig.ACKS_CONFIG, "all");
        configProps.put(ProducerConfig.RETRIES_CONFIG, 3);
        configProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        configProps.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
        configProps.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 33554432);
        configProps.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "snappy");
        return new DefaultKafkaProducerFactory<>(configProps);
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }

    @Bean
    public ConsumerFactory<String, String> consumerFactory() {
        Map<String, Object> configProps = new HashMap<>();
        configProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        configProps.put(ConsumerConfig.GROUP_ID_CONFIG, "tencent-cloud-group");
        configProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        configProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        configProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        configProps.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        configProps.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 100);
        configProps.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 30000);
        configProps.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 300000);
        return new DefaultKafkaConsumerFactory<>(configProps);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, String> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        factory.setConcurrency(5);
        return factory;
    }
}
```

### 8.5.3 美团消息生产者

```java
package com.meituan.mq.producer;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.connection.CorrelationData;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Slf4j
@Component
public class OrderMessageProducer {

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    public void sendOrderCreated(OrderMessage message) {
        try {
            String json = objectMapper.writeValueAsString(message);
            CorrelationData correlationData = new CorrelationData(UUID.randomUUID().toString());

            rabbitTemplate.convertAndSend(
                "order.exchange",
                "order.created",
                json,
                correlationData
            );

            log.info("订单创建消息发送成功: {}", message.getOrderId());
        } catch (Exception e) {
            log.error("订单创建消息发送失败", e);
        }
    }

    public void sendOrderPaid(OrderMessage message) {
        try {
            String json = objectMapper.writeValueAsString(message);
            CorrelationData correlationData = new CorrelationData(UUID.randomUUID().toString());

            rabbitTemplate.convertAndSend(
                "order.exchange",
                "order.paid",
                json,
                correlationData
            );

            log.info("订单支付消息发送成功: {}", message.getOrderId());
        } catch (Exception e) {
            log.error("订单支付消息发送失败", e);
        }
    }

    public void sendOrderCancelled(OrderMessage message) {
        try {
            String json = objectMapper.writeValueAsString(message);
            CorrelationData correlationData = new CorrelationData(UUID.randomUUID().toString());

            rabbitTemplate.convertAndSend(
                "order.exchange",
                "order.cancelled",
                json,
                correlationData
            );

            log.info("订单取消消息发送成功: {}", message.getOrderId());
        } catch (Exception e) {
            log.error("订单取消消息发送失败", e);
        }
    }
}
```

### 8.5.4 字节跳动消息消费者

```java
package com.bytedance.mq.consumer;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Slf4j
@Component
public class OrderMessageConsumer {

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private OrderService orderService;

    @RabbitListener(queues = "order.created.queue")
    public void handleOrderCreated(Message message) throws IOException {
        try {
            OrderMessage orderMessage = objectMapper.readValue(
                message.getBody(), OrderMessage.class);

            orderService.processOrderCreated(orderMessage);

            log.info("订单创建消息处理成功: {}", orderMessage.getOrderId());
        } catch (Exception e) {
            log.error("订单创建消息处理失败", e);
        }
    }

    @RabbitListener(queues = "order.paid.queue")
    public void handleOrderPaid(Message message) throws IOException {
        try {
            OrderMessage orderMessage = objectMapper.readValue(
                message.getBody(), OrderMessage.class);

            orderService.processOrderPaid(orderMessage);

            log.info("订单支付消息处理成功: {}", orderMessage.getOrderId());
        } catch (Exception e) {
            log.error("订单支付消息处理失败", e);
        }
    }

    @RabbitListener(queues = "order.cancelled.queue")
    public void handleOrderCancelled(Message message) throws IOException {
        try {
            OrderMessage orderMessage = objectMapper.readValue(
                message.getBody(), OrderMessage.class);

            orderService.processOrderCancelled(orderMessage);

            log.info("订单取消消息处理成功: {}", orderMessage.getOrderId());
        } catch (Exception e) {
            log.error("订单取消消息处理失败", e);
        }
    }
}
```

### 8.5.5 京东健康Kafka生产者

```java
package com.jd.health.kafka.producer;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Component;
import org.springframework.util.concurrent.ListenableFuture;
import org.springframework.util.concurrent.ListenableFutureCallback;

@Slf4j
@Component
public class PatientEventProducer {

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    public void sendPatientCreated(PatientEvent event) {
        try {
            String json = objectMapper.writeValueAsString(event);
            ListenableFuture<SendResult<String, String>> future =
                kafkaTemplate.send("patient-events", event.getPatientId(), json);

            future.addCallback(new ListenableFutureCallback<SendResult<String, String>>() {
                @Override
                public void onSuccess(SendResult<String, String> result) {
                    log.info("患者创建事件发送成功: {}", event.getPatientId());
                }

                @Override
                public void onFailure(Throwable ex) {
                    log.error("患者创建事件发送失败", ex);
                }
            });
        } catch (Exception e) {
            log.error("患者创建事件序列化失败", e);
        }
    }

    public void sendPatientUpdated(PatientEvent event) {
        try {
            String json = objectMapper.writeValueAsString(event);
            kafkaTemplate.send("patient-events", event.getPatientId(), json);
            log.info("患者更新事件发送成功: {}", event.getPatientId());
        } catch (Exception e) {
            log.error("患者更新事件发送失败", e);
        }
    }
}
```

### 8.5.6 拼多多Kafka消费者

```java
package com.pdd.kafka.consumer;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class ProductEventConsumer {

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ProductService productService;

    @KafkaListener(
        topics = "product-events",
        groupId = "product-processor-group",
        concurrency = "3"
    )
    public void handleProductEvent(
            ConsumerRecord<String, String> record,
            Acknowledgment acknowledgment) {
        try {
            String value = record.value();
            ProductEvent event = objectMapper.readValue(value, ProductEvent.class);

            switch (event.getEventType()) {
                case "PRODUCT_CREATED":
                    productService.handleProductCreated(event);
                    break;
                case "PRODUCT_UPDATED":
                    productService.handleProductUpdated(event);
                    break;
                case "PRODUCT_DELETED":
                    productService.handleProductDeleted(event);
                    break;
                default:
                    log.warn("未知的事件类型: {}", event.getEventType());
            }

            acknowledgment.acknowledge();
            log.info("产品事件处理成功: {}", event.getProductId());
        } catch (Exception e) {
            log.error("产品事件处理失败", e);
        }
    }
}
```

## 8.6 最佳实践

1. **消息持久化**：确保消息不丢失
2. **消息确认**：使用手动确认机制
3. **死信队列**：处理失败消息
4. **幂等性**：保证消息重复消费的正确性
5. **监控告警**：监控消息队列状态
6. **限流保护**：防止消息堆积

## 8.7 小结

本章介绍了Spring Boot消息队列的核心内容，包括：

- RabbitMQ集成与配置
- Kafka集成与配置
- 消息生产者与消费者
- 消息可靠性保证
- 死信队列处理

通过本章学习，你应该能够：

- 集成RabbitMQ和Kafka
- 实现消息的发送和接收
- 保证消息的可靠性
- 处理死信消息
- 实现消息重试机制

下一章将介绍Spring Boot的微服务架构。
