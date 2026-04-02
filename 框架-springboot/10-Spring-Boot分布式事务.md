# 第10章：Spring Boot分布式事务

## 10.1 分布式事务概述

### 10.1.1 什么是分布式事务

分布式事务是指事务的参与者、支持事务的服务器、资源服务器以及事务管理器分别位于不同的分布式系统的不同节点之上。

### 10.1.2 分布式事务问题

- **数据一致性**：多个数据源的数据一致性
- **网络分区**：网络故障导致的事务问题
- **性能问题**：分布式事务的性能开销
- **复杂度**：实现和维护的复杂度

### 10.1.3 CAP理论

| 特性 | 说明 |
|------|------|
| C（一致性） | 所有节点在同一时间看到相同的数据 |
| A（可用性） | 每次请求都能获得响应 |
| P（分区容错性） | 系统在任意分区故障时仍能运行 |

CAP理论指出，在分布式系统中，只能同时满足CAP中的两项。

## 10.2 2PC（两阶段提交）

### 10.2.1 2PC原理

两阶段提交（Two-Phase Commit）是一种强一致性的分布式事务协议：

1. **准备阶段**：协调者询问所有参与者是否可以提交
2. **提交阶段**：根据参与者的反馈，协调者决定提交或回滚

### 10.2.2 Seata AT模式

```xml
<dependency>
    <groupId>io.seata</groupId>
    <artifactId>seata-spring-boot-starter</artifactId>
    <version>2.0.0</version>
</dependency>
```

```yaml
seata:
  enabled: true
  application-id: demo-service
  tx-service-group: my_test_tx_group
  service:
    vgroup-mapping:
      my_test_tx_group: default
    grouplist:
      default: localhost:8091
  registry:
    type: nacos
    nacos:
      server-addr: localhost:8848
      namespace: public
      group: SEATA_GROUP
      application: seata-server
  config:
    type: nacos
    nacos:
      server-addr: localhost:8848
      namespace: public
      group: SEATA_GROUP
```

### 10.2.3 Seata使用示例

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final InventoryClient inventoryClient;
    private final AccountClient accountClient;

    @GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
    public void createOrder(OrderCreateRequest request) {
        Order order = Order.builder()
            .userId(request.getUserId())
            .productId(request.getProductId())
            .quantity(request.getQuantity())
            .totalAmount(request.getTotalAmount())
            .status(OrderStatus.CREATED)
            .build();
        orderRepository.save(order);

        inventoryClient.deductStock(request.getProductId(), request.getQuantity());

        accountClient.deductBalance(request.getUserId(), request.getTotalAmount());

        order.setStatus(OrderStatus.PAID);
        orderRepository.save(order);
    }
}
```

### 10.2.4 Seata配置类

```java
@Configuration
public class SeataConfig {

    @Bean
    public GlobalTransactionScanner globalTransactionScanner() {
        return new GlobalTransactionScanner("demo-service", "my_test_tx_group");
    }

    @Bean
    public DataSourceProxy dataSourceProxy(DataSource dataSource) {
        return new DataSourceProxy(dataSource);
    }
}
```

## 10.3 TCC（Try-Confirm-Cancel）

### 10.3.1 TCC原理

TCC是一种应用层的分布式事务解决方案：

1. **Try阶段**：预留资源
2. **Confirm阶段**：确认执行
3. **Cancel阶段**：取消执行

### 10.3.2 TCC实现

```java
@LocalTCC
public interface InventoryService {

    @TwoPhaseBusinessAction(
        name = "inventoryDeduct",
        commitMethod = "confirmDeduct",
        rollbackMethod = "cancelDeduct"
    )
    boolean deduct(
            @BusinessActionContextParameter(paramName = "productId") Long productId,
            @BusinessActionContextParameter(paramName = "quantity") Integer quantity);

    boolean confirmDeduct(BusinessActionContext context);

    boolean cancelDeduct(BusinessActionContext context);
}

@Service
public class InventoryServiceImpl implements InventoryService {

    @Autowired
    private InventoryRepository inventoryRepository;

    @Autowired
    private InventoryLogRepository inventoryLogRepository;

    @Override
    @Transactional
    public boolean deduct(Long productId, Integer quantity) {
        Inventory inventory = inventoryRepository.findByProductId(productId);
        if (inventory.getStock() < quantity) {
            throw new BusinessException("库存不足");
        }

        inventory.setStock(inventory.getStock() - quantity);
        inventoryRepository.save(inventory);

        InventoryLog log = InventoryLog.builder()
            .productId(productId)
            .quantity(quantity)
            .status(InventoryLogStatus.TRY)
            .build();
        inventoryLogRepository.save(log);

        return true;
    }

    @Override
    @Transactional
    public boolean confirmDeduct(BusinessActionContext context) {
        Long productId = context.getActionContext("productId", Long.class);
        Integer quantity = context.getActionContext("quantity", Integer.class);

        InventoryLog log = inventoryLogRepository.findByProductIdAndStatus(
            productId, InventoryLogStatus.TRY);
        if (log != null) {
            log.setStatus(InventoryLogStatus.CONFIRM);
            inventoryLogRepository.save(log);
        }

        return true;
    }

    @Override
    @Transactional
    public boolean cancelDeduct(BusinessActionContext context) {
        Long productId = context.getActionContext("productId", Long.class);
        Integer quantity = context.getActionContext("quantity", Integer.class);

        Inventory inventory = inventoryRepository.findByProductId(productId);
        inventory.setStock(inventory.getStock() + quantity);
        inventoryRepository.save(inventory);

        InventoryLog log = inventoryLogRepository.findByProductIdAndStatus(
            productId, InventoryLogStatus.TRY);
        if (log != null) {
            log.setStatus(InventoryLogStatus.CANCEL);
            inventoryLogRepository.save(log);
        }

        return true;
    }
}
```

## 10.4 Saga模式

### 10.4.1 Saga原理

Saga模式将长事务拆分为多个本地短事务，每个本地事务都有对应的补偿事务。

### 10.4.2 Seata Saga实现

```java
@Service
@RequiredArgsConstructor
public class OrderSagaService {

    private final OrderRepository orderRepository;
    private final InventoryClient inventoryClient;
    private final AccountClient accountClient;

    @SagaStart(name = "create-order-saga")
    public void createOrder(OrderCreateRequest request) {
        Order order = Order.builder()
            .userId(request.getUserId())
            .productId(request.getProductId())
            .quantity(request.getQuantity())
            .totalAmount(request.getTotalAmount())
            .status(OrderStatus.CREATED)
            .build();
        order = orderRepository.save(order);

        SagaStep inventoryStep = SagaStep.builder()
            .sagaName("create-order-saga")
            .stepName("deduct-inventory")
            .businessKey(order.getId().toString())
            .build();

        try {
            inventoryClient.deductStock(request.getProductId(), request.getQuantity());
            inventoryStep.setStatus(SagaStepStatus.SUCCESS);
        } catch (Exception e) {
            inventoryStep.setStatus(SagaStepStatus.FAILED);
            throw e;
        } finally {
            sagaStepRepository.save(inventoryStep);
        }

        SagaStep accountStep = SagaStep.builder()
            .sagaName("create-order-saga")
            .stepName("deduct-balance")
            .businessKey(order.getId().toString())
            .build();

        try {
            accountClient.deductBalance(request.getUserId(), request.getTotalAmount());
            accountStep.setStatus(SagaStepStatus.SUCCESS);
        } catch (Exception e) {
            accountStep.setStatus(SagaStepStatus.FAILED);
            compensateInventory(request.getProductId(), request.getQuantity());
            throw e;
        } finally {
            sagaStepRepository.save(accountStep);
        }

        order.setStatus(OrderStatus.PAID);
        orderRepository.save(order);
    }

    private void compensateInventory(Long productId, Integer quantity) {
        inventoryClient.addStock(productId, quantity);
    }
}
```

## 10.5 本地消息表

### 10.5.1 本地消息表原理

本地消息表是一种基于最终一致性的分布式事务解决方案：

1. 在同一个数据库的本地事务中，同时操作业务数据和消息数据
2. 通过定时任务扫描消息表，发送消息
3. 消息消费成功后更新消息状态

### 10.5.2 本地消息表实现

```java
@Entity
@Table(name = "local_message")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LocalMessage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String topic;

    private String content;

    private MessageStatus status;

    private Integer retryCount;

    private LocalDateTime nextRetryTime;

    private LocalDateTime createdTime;

    private LocalDateTime updatedTime;

    public enum MessageStatus {
        PENDING, SENT, SUCCESS, FAILED
    }
}

@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final LocalMessageRepository localMessageRepository;
    private final RabbitTemplate rabbitTemplate;

    @Transactional
    public void createOrder(OrderCreateRequest request) {
        Order order = Order.builder()
            .userId(request.getUserId())
            .productId(request.getProductId())
            .quantity(request.getQuantity())
            .totalAmount(request.getTotalAmount())
            .status(OrderStatus.CREATED)
            .build();
        order = orderRepository.save(order);

        OrderMessage message = OrderMessage.builder()
            .orderId(order.getId())
            .userId(order.getUserId())
            .productId(order.getProductId())
            .quantity(order.getQuantity())
            .totalAmount(order.getTotalAmount())
            .build();

        LocalMessage localMessage = LocalMessage.builder()
            .topic("order.created")
            .content(JsonUtils.toJson(message))
            .status(LocalMessage.MessageStatus.PENDING)
            .retryCount(0)
            .nextRetryTime(LocalDateTime.now())
            .createdTime(LocalDateTime.now())
            .updatedTime(LocalDateTime.now())
            .build();
        localMessageRepository.save(localMessage);
    }
}

@Component
@RequiredArgsConstructor
public class MessageSender {

    private final LocalMessageRepository localMessageRepository;
    private final RabbitTemplate rabbitTemplate;

    @Scheduled(fixedRate = 5000)
    public void sendPendingMessages() {
        List<LocalMessage> messages = localMessageRepository
            .findByStatusAndNextRetryTimeBefore(
                LocalMessage.MessageStatus.PENDING,
                LocalDateTime.now()
            );

        for (LocalMessage message : messages) {
            try {
                rabbitTemplate.convertAndSend(message.getTopic(), message.getContent());
                message.setStatus(LocalMessage.MessageStatus.SENT);
                message.setUpdatedTime(LocalDateTime.now());
                localMessageRepository.save(message);
            } catch (Exception e) {
                message.setRetryCount(message.getRetryCount() + 1);
                message.setNextRetryTime(LocalDateTime.now().plusMinutes(5));
                message.setUpdatedTime(LocalDateTime.now());
                localMessageRepository.save(message);
            }
        }
    }
}
```

## 10.6 事务消息

### 10.6.1 RocketMQ事务消息

```xml
<dependency>
    <groupId>org.apache.rocketmq</groupId>
    <artifactId>rocketmq-spring-boot-starter</artifactId>
    <version>2.2.3</version>
</dependency>
```

```yaml
rocketmq:
  name-server: localhost:9876
  producer:
    group: order-producer-group
    send-message-timeout: 3000
    retry-times-when-send-failed: 2
```

### 10.6.2 事务消息实现

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final RocketMQTemplate rocketMQTemplate;

    public void createOrder(OrderCreateRequest request) {
        Order order = Order.builder()
            .userId(request.getUserId())
            .productId(request.getProductId())
            .quantity(request.getQuantity())
            .totalAmount(request.getTotalAmount())
            .status(OrderStatus.CREATED)
            .build();

        OrderMessage message = OrderMessage.builder()
            .orderId(order.getId())
            .userId(order.getUserId())
            .productId(order.getProductId())
            .quantity(order.getQuantity())
            .totalAmount(order.getTotalAmount())
            .build();

        rocketMQTemplate.sendMessageInTransaction(
            "order-topic",
            MessageBuilder.withPayload(message).build(),
            order
        );
    }

    @RocketMQTransactionListener
    public class OrderTransactionListenerImpl implements RocketMQLocalTransactionListener {

        @Autowired
        private OrderRepository orderRepository;

        @Override
        @Transactional
        public TransactionSendResult executeLocalTransaction(Message msg, Object arg) {
            Order order = (Order) arg;
            try {
                orderRepository.save(order);
                return TransactionSendResult.COMMIT;
            } catch (Exception e) {
                return TransactionSendResult.ROLLBACK;
            }
        }

        @Override
        public TransactionSendResult checkLocalTransaction(Message msg) {
            OrderMessage message = JsonUtils.fromJson(
                new String((byte[]) msg.getPayload()), OrderMessage.class);
            Order order = orderRepository.findById(message.getOrderId()).orElse(null);
            if (order != null) {
                return TransactionSendResult.COMMIT;
            } else {
                return TransactionSendResult.ROLLBACK;
            }
        }
    }
}
```

## 10.7 互联网大厂真实项目代码示例

### 10.7.1 阿里巴巴Seata配置

```java
package com.alibaba.seata.config;

import io.seata.rm.datasource.DataSourceProxy;
import io.seata.spring.annotation.GlobalTransactionScanner;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
public class SeataConfig {

    @Value("${seata.application-id}")
    private String applicationId;

    @Value("${seata.tx-service-group}")
    private String txServiceGroup;

    @Bean
    public GlobalTransactionScanner globalTransactionScanner() {
        return new GlobalTransactionScanner(applicationId, txServiceGroup);
    }

    @Bean
    public DataSourceProxy dataSourceProxy(DataSource dataSource) {
        return new DataSourceProxy(dataSource);
    }
}
```

### 10.7.2 腾讯云TCC实现

```java
package com.tencent.cloud.tcc;

import io.seata.rm.tcc.api.BusinessActionContext;
import io.seata.rm.tcc.api.BusinessActionContextParameter;
import io.seata.rm.tcc.api.LocalTCC;
import io.seata.rm.tcc.api.TwoPhaseBusinessAction;
import org.springframework.stereotype.Service;

@LocalTCC
public interface AccountService {

    @TwoPhaseBusinessAction(
        name = "accountDeduct",
        commitMethod = "confirmDeduct",
        rollbackMethod = "cancelDeduct"
    )
    boolean deduct(
            @BusinessActionContextParameter(paramName = "userId") Long userId,
            @BusinessActionContextParameter(paramName = "amount") BigDecimal amount);

    boolean confirmDeduct(BusinessActionContext context);

    boolean cancelDeduct(BusinessActionContext context);
}

@Service
public class AccountServiceImpl implements AccountService {

    @Override
    @Transactional
    public boolean deduct(Long userId, BigDecimal amount) {
        Account account = accountRepository.findByUserId(userId);
        if (account.getBalance().compareTo(amount) < 0) {
            throw new BusinessException("余额不足");
        }
        account.setBalance(account.getBalance().subtract(amount));
        accountRepository.save(account);

        AccountLog log = AccountLog.builder()
            .userId(userId)
            .amount(amount)
            .status(AccountLogStatus.TRY)
            .build();
        accountLogRepository.save(log);

        return true;
    }

    @Override
    @Transactional
    public boolean confirmDeduct(BusinessActionContext context) {
        Long userId = context.getActionContext("userId", Long.class);
        BigDecimal amount = context.getActionContext("amount", BigDecimal.class);

        AccountLog log = accountLogRepository.findByUserIdAndStatus(
            userId, AccountLogStatus.TRY);
        if (log != null) {
            log.setStatus(AccountLogStatus.CONFIRM);
            accountLogRepository.save(log);
        }
        return true;
    }

    @Override
    @Transactional
    public boolean cancelDeduct(BusinessActionContext context) {
        Long userId = context.getActionContext("userId", Long.class);
        BigDecimal amount = context.getActionContext("amount", BigDecimal.class);

        Account account = accountRepository.findByUserId(userId);
        account.setBalance(account.getBalance().add(amount));
        accountRepository.save(account);

        AccountLog log = accountLogRepository.findByUserIdAndStatus(
            userId, AccountLogStatus.TRY);
        if (log != null) {
            log.setStatus(AccountLogStatus.CANCEL);
            accountLogRepository.save(log);
        }
        return true;
    }
}
```

### 10.7.3 美团本地消息表

```java
package com.meituan.transaction;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private LocalMessageRepository localMessageRepository;

    @Autowired
    private MessageSender messageSender;

    @Transactional
    public void createOrder(OrderCreateRequest request) {
        Order order = Order.builder()
            .userId(request.getUserId())
            .productId(request.getProductId())
            .quantity(request.getQuantity())
            .totalAmount(request.getTotalAmount())
            .status(OrderStatus.CREATED)
            .build();
        order = orderRepository.save(order);

        OrderMessage message = OrderMessage.builder()
            .orderId(order.getId())
            .userId(order.getUserId())
            .productId(order.getProductId())
            .quantity(order.getQuantity())
            .totalAmount(order.getTotalAmount())
            .build();

        LocalMessage localMessage = LocalMessage.builder()
            .topic("order.created")
            .content(JsonUtils.toJson(message))
            .status(LocalMessage.MessageStatus.PENDING)
            .retryCount(0)
            .nextRetryTime(LocalDateTime.now())
            .createdTime(LocalDateTime.now())
            .updatedTime(LocalDateTime.now())
            .build();
        localMessageRepository.save(localMessage);
    }
}
```

### 10.7.4 字节跳动Saga模式

```java
package com.bytedance.saga;

import io.seata.spring.annotation.GlobalTransactional;
import org.springframework.stereotype.Service;

@Service
public class OrderSagaService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private InventoryClient inventoryClient;

    @Autowired
    private AccountClient accountClient;

    @GlobalTransactional(name = "create-order-saga", rollbackFor = Exception.class)
    public void createOrder(OrderCreateRequest request) {
        Order order = Order.builder()
            .userId(request.getUserId())
            .productId(request.getProductId())
            .quantity(request.getQuantity())
            .totalAmount(request.getTotalAmount())
            .status(OrderStatus.CREATED)
            .build();
        order = orderRepository.save(order);

        SagaStep inventoryStep = SagaStep.builder()
            .sagaName("create-order-saga")
            .stepName("deduct-inventory")
            .businessKey(order.getId().toString())
            .status(SagaStepStatus.SUCCESS)
            .build();
        sagaStepRepository.save(inventoryStep);

        inventoryClient.deductStock(request.getProductId(), request.getQuantity());

        SagaStep accountStep = SagaStep.builder()
            .sagaName("create-order-saga")
            .stepName("deduct-balance")
            .businessKey(order.getId().toString())
            .status(SagaStepStatus.SUCCESS)
            .build();
        sagaStepRepository.save(accountStep);

        accountClient.deductBalance(request.getUserId(), request.getTotalAmount());

        order.setStatus(OrderStatus.PAID);
        orderRepository.save(order);
    }
}
```

### 10.7.5 京东健康事务消息

```java
package com.jd.health.transaction;

import org.apache.rocketmq.spring.annotation.RocketMQMessageListener;
import org.apache.rocketmq.spring.annotation.RocketMQTransactionListener;
import org.apache.rocketmq.spring.core.RocketMQLocalTransactionListener;
import org.apache.rocketmq.spring.core.RocketMQLocalTransactionState;
import org.apache.rocketmq.spring.core.RocketMQTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.Message;
import org.springframework.messaging.support.MessageBuilder;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

@Service
public class AppointmentService {

    @Autowired
    private RocketMQTemplate rocketMQTemplate;

    public void createAppointment(AppointmentCreateRequest request) {
        Appointment appointment = Appointment.builder()
            .patientId(request.getPatientId())
            .doctorId(request.getDoctorId())
            .appointmentTime(request.getAppointmentTime())
            .status(AppointmentStatus.PENDING)
            .build();

        AppointmentMessage message = AppointmentMessage.builder()
            .appointmentId(appointment.getId())
            .patientId(appointment.getPatientId())
            .doctorId(appointment.getDoctorId())
            .appointmentTime(appointment.getAppointmentTime())
            .build();

        rocketMQTemplate.sendMessageInTransaction(
            "appointment-topic",
            MessageBuilder.withPayload(message).build(),
            appointment
        );
    }

    @RocketMQTransactionListener
    public class AppointmentTransactionListener implements RocketMQLocalTransactionListener {

        @Autowired
        private AppointmentRepository appointmentRepository;

        @Override
        public RocketMQLocalTransactionState executeLocalTransaction(Message msg, Object arg) {
            Appointment appointment = (Appointment) arg;
            try {
                appointmentRepository.save(appointment);
                return RocketMQLocalTransactionState.COMMIT;
            } catch (Exception e) {
                return RocketMQLocalTransactionState.ROLLBACK;
            }
        }

        @Override
        public RocketMQLocalTransactionState checkLocalTransaction(Message msg) {
            AppointmentMessage message = JsonUtils.fromJson(
                new String((byte[]) msg.getPayload()), AppointmentMessage.class);
            Appointment appointment = appointmentRepository.findById(message.getAppointmentId()).orElse(null);
            if (appointment != null) {
                return RocketMQLocalTransactionState.COMMIT;
            } else {
                return RocketMQLocalTransactionState.ROLLBACK;
            }
        }
    }
}
```

### 10.7.6 拼多多分布式事务监控

```java
package com.pdd.monitor;

import io.seata.rm.tcc.api.BusinessActionContext;
import org.springframework.stereotype.Component;

@Component
public class DistributedTransactionMonitor {

    public void monitorTransaction(BusinessActionContext context) {
        String actionName = context.getActionName();
        Object businessKey = context.getActionContext("businessKey");

        System.out.println("分布式事务监控 - Action: " + actionName + ", BusinessKey: " + businessKey);
    }

    public void monitorCompensation(BusinessActionContext context) {
        String actionName = context.getActionName();
        Object businessKey = context.getActionContext("businessKey");

        System.out.println("分布式事务补偿 - Action: " + actionName + ", BusinessKey: " + businessKey);
    }
}
```

## 10.8 最佳实践

1. **选择合适方案**：根据业务场景选择分布式事务方案
2. **幂等性设计**：确保操作的幂等性
3. **补偿机制**：实现完善的补偿逻辑
4. **监控告警**：监控分布式事务状态
5. **性能优化**：减少分布式事务的使用
6. **测试验证**：充分测试各种异常场景

## 10.9 小结

本章介绍了Spring Boot分布式事务的核心内容，包括：

- 分布式事务概述
- 2PC（两阶段提交）
- TCC（Try-Confirm-Cancel）
- Saga模式
- 本地消息表
- 事务消息

通过本章学习，你应该能够：

- 理解分布式事务的原理
- 使用Seata实现分布式事务
- 实现TCC事务模式
- 使用Saga模式
- 实现本地消息表
- 使用RocketMQ事务消息

下一章将介绍Spring Boot的性能优化与监控。
