# 第4章：Spring Boot数据访问

## 4.1 Spring Data JPA

### 4.1.1 依赖配置

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

<dependency>
    <groupId>com.zaxxer</groupId>
    <artifactId>HikariCP</artifactId>
</dependency>
```

### 4.1.2 数据源配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20
      idle-timeout: 30000
      max-lifetime: 1800000
      connection-timeout: 30000
      connection-test-query: SELECT 1

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQL8Dialect
        format_sql: true
        use_sql_comments: true
    open-in-view: false
```

### 4.1.3 实体类定义

```java
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_username", columnList = "username"),
    @Index(name = "idx_email", columnList = "email")
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false, length = 100)
    private String password;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(name = "phone_number", length = 20)
    private String phoneNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Gender gender;

    @Column(name = "birth_date")
    @Temporal(TemporalType.DATE)
    private Date birthDate;

    @Column(name = "created_at", nullable = false, updatable = false)
    @CreationTimestamp
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    @UpdateTimestamp
    private LocalDateTime updatedAt;

    @Version
    private Integer version;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Order> orders;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles;

    @ElementCollection(fetch = FetchType.LAZY)
    @CollectionTable(name = "user_addresses", joinColumns = @JoinColumn(name = "user_id"))
    private List<Address> addresses;

    public enum Gender {
        MALE, FEMALE, OTHER
    }

    @Embeddable
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Address {
        private String province;
        private String city;
        private String district;
        private String detail;
    }
}
```

### 4.1.4 Repository接口

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long>, JpaSpecificationExecutor<User> {

    Optional<User> findByUsername(String username);

    Optional<User> findByEmail(String email);

    List<User> findByGender(Gender gender);

    Page<User> findByGender(Gender gender, Pageable pageable);

    @Query("SELECT u FROM User u WHERE u.username LIKE %:keyword% OR u.email LIKE %:keyword%")
    Page<User> searchUsers(@Param("keyword") String keyword, Pageable pageable);

    @Query(value = "SELECT * FROM users WHERE created_at >= :startDate", nativeQuery = true)
    List<User> findUsersCreatedAfter(@Param("startDate") LocalDateTime startDate);

    @Modifying
    @Query("UPDATE User u SET u.password = :password WHERE u.id = :id")
    int updatePassword(@Param("id") Long id, @Param("password") String password);

    @Modifying
    @Query("DELETE FROM User u WHERE u.createdAt < :date")
    int deleteUsersCreatedBefore(@Param("date") LocalDateTime date);

    @Query("SELECT u FROM User u JOIN u.roles r WHERE r.name = :roleName")
    List<User> findByRoleName(@Param("roleName") String roleName);

    List<User> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);

    List<User> findByUsernameContainingIgnoreCase(String keyword);

    @Query("SELECT new com.example.dto.UserDTO(u.id, u.username, u.email) FROM User u")
    List<UserDTO> findAllUserDTOs();

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);

    long countByGender(Gender gender);
}
```

### 4.1.5 自定义Repository实现

```java
public interface UserRepositoryCustom {
    List<User> findUsersByComplexConditions(String keyword, Gender gender, LocalDateTime startDate, LocalDateTime endDate);
}

@Repository
public class UserRepositoryImpl implements UserRepositoryCustom {

    @PersistenceContext
    private EntityManager entityManager;

    @Override
    public List<User> findUsersByComplexConditions(String keyword, Gender gender,
                                                   LocalDateTime startDate, LocalDateTime endDate) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> user = query.from(User.class);

        List<Predicate> predicates = new ArrayList<>();

        if (StringUtils.hasText(keyword)) {
            predicates.add(cb.or(
                cb.like(user.get("username"), "%" + keyword + "%"),
                cb.like(user.get("email"), "%" + keyword + "%")
            ));
        }

        if (gender != null) {
            predicates.add(cb.equal(user.get("gender"), gender));
        }

        if (startDate != null) {
            predicates.add(cb.greaterThanOrEqualTo(user.get("createdAt"), startDate));
        }

        if (endDate != null) {
            predicates.add(cb.lessThanOrEqualTo(user.get("createdAt"), endDate));
        }

        query.where(predicates.toArray(new Predicate[0]));
        query.orderBy(cb.desc(user.get("createdAt")));

        return entityManager.createQuery(query).getResultList();
    }
}

public interface UserRepository extends JpaRepository<User, Long>, JpaSpecificationExecutor<User>, UserRepositoryCustom {
}
```

### 4.1.6 Specification动态查询

```java
@Service
public class UserQueryService {

    @Autowired
    private UserRepository userRepository;

    public Page<User> searchUsers(UserQuery query, Pageable pageable) {
        Specification<User> spec = (root, criteriaQuery, criteriaBuilder) -> {
            List<Predicate> predicates = new ArrayList<>();

            if (StringUtils.hasText(query.getKeyword())) {
                predicates.add(criteriaBuilder.or(
                    criteriaBuilder.like(root.get("username"), "%" + query.getKeyword() + "%"),
                    criteriaBuilder.like(root.get("email"), "%" + query.getKeyword() + "%")
                ));
            }

            if (query.getGender() != null) {
                predicates.add(criteriaBuilder.equal(root.get("gender"), query.getGender()));
            }

            if (query.getStartDate() != null) {
                predicates.add(criteriaBuilder.greaterThanOrEqualTo(
                    root.get("createdAt"), query.getStartDate()));
            }

            if (query.getEndDate() != null) {
                predicates.add(criteriaBuilder.lessThanOrEqualTo(
                    root.get("createdAt"), query.getEndDate()));
            }

            return criteriaBuilder.and(predicates.toArray(new Predicate[0]));
        };

        return userRepository.findAll(spec, pageable);
    }
}
```

## 4.2 MyBatis集成

### 4.2.1 依赖配置

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.3</version>
</dependency>

<dependency>
    <groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper-spring-boot-starter</artifactId>
    <version>2.1.0</version>
</dependency>
```

### 4.2.2 MyBatis配置

```yaml
mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.example.entity
  configuration:
    map-underscore-to-camel-case: true
    cache-enabled: true
    lazy-loading-enabled: true
    aggressive-lazy-loading: false
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl

pagehelper:
  helper-dialect: mysql
  reasonable: true
  support-methods-arguments: true
  params: count=countSql
```

### 4.2.3 Mapper接口

```java
@Mapper
public interface UserMapper {

    User findById(Long id);

    User findByUsername(String username);

    List<User> findAll();

    List<User> findByCondition(@Param("condition") UserQuery condition);

    int insert(User user);

    int update(User user);

    int deleteById(Long id);

    int batchInsert(@Param("users") List<User> users);

    List<User> selectByPage(@Param("offset") int offset, @Param("limit") int limit);

    int countByCondition(@Param("condition") UserQuery condition);
}
```

### 4.2.4 Mapper XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.UserMapper">

    <resultMap id="BaseResultMap" type="com.example.entity.User">
        <id column="id" property="id" jdbcType="BIGINT"/>
        <result column="username" property="username" jdbcType="VARCHAR"/>
        <result column="password" property="password" jdbcType="VARCHAR"/>
        <result column="email" property="email" jdbcType="VARCHAR"/>
        <result column="phone_number" property="phoneNumber" jdbcType="VARCHAR"/>
        <result column="gender" property="gender" jdbcType="VARCHAR"/>
        <result column="birth_date" property="birthDate" jdbcType="DATE"/>
        <result column="created_at" property="createdAt" jdbcType="TIMESTAMP"/>
        <result column="updated_at" property="updatedAt" jdbcType="TIMESTAMP"/>
        <result column="version" property="version" jdbcType="INTEGER"/>
    </resultMap>

    <sql id="Base_Column_List">
        id, username, password, email, phone_number, gender, birth_date,
        created_at, updated_at, version
    </sql>

    <select id="findById" resultMap="BaseResultMap">
        SELECT
        <include refid="Base_Column_List"/>
        FROM users
        WHERE id = #{id}
    </select>

    <select id="findByUsername" resultMap="BaseResultMap">
        SELECT
        <include refid="Base_Column_List"/>
        FROM users
        WHERE username = #{username}
    </select>

    <select id="findAll" resultMap="BaseResultMap">
        SELECT
        <include refid="Base_Column_List"/>
        FROM users
        ORDER BY created_at DESC
    </select>

    <select id="findByCondition" resultMap="BaseResultMap">
        SELECT
        <include refid="Base_Column_List"/>
        FROM users
        <where>
            <if test="condition.keyword != null and condition.keyword != ''">
                AND (username LIKE CONCAT('%', #{condition.keyword}, '%')
                OR email LIKE CONCAT('%', #{condition.keyword}, '%'))
            </if>
            <if test="condition.gender != null">
                AND gender = #{condition.gender}
            </if>
            <if test="condition.startDate != null">
                AND created_at &gt;= #{condition.startDate}
            </if>
            <if test="condition.endDate != null">
                AND created_at &lt;= #{condition.endDate}
            </if>
        </where>
        ORDER BY created_at DESC
    </select>

    <insert id="insert" parameterType="com.example.entity.User" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO users (username, password, email, phone_number, gender, birth_date, created_at)
        VALUES (#{username}, #{password}, #{email}, #{phoneNumber}, #{gender}, #{birthDate}, NOW())
    </insert>

    <update id="update" parameterType="com.example.entity.User">
        UPDATE users
        <set>
            <if test="username != null">username = #{username},</if>
            <if test="password != null">password = #{password},</if>
            <if test="email != null">email = #{email},</if>
            <if test="phoneNumber != null">phone_number = #{phoneNumber},</if>
            <if test="gender != null">gender = #{gender},</if>
            <if test="birthDate != null">birth_date = #{birthDate},</if>
            updated_at = NOW(),
            version = version + 1
        </set>
        WHERE id = #{id}
    </update>

    <delete id="deleteById">
        DELETE FROM users WHERE id = #{id}
    </delete>

    <insert id="batchInsert" parameterType="java.util.List" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO users (username, password, email, phone_number, gender, birth_date, created_at)
        VALUES
        <foreach collection="users" item="user" separator=",">
            (#{user.username}, #{user.password}, #{user.email}, #{user.phoneNumber},
             #{user.gender}, #{user.birthDate}, NOW())
        </foreach>
    </insert>

    <select id="selectByPage" resultMap="BaseResultMap">
        SELECT
        <include refid="Base_Column_List"/>
        FROM users
        ORDER BY created_at DESC
        LIMIT #{offset}, #{limit}
    </select>

    <select id="countByCondition" resultType="int">
        SELECT COUNT(*)
        FROM users
        <where>
            <if test="condition.keyword != null and condition.keyword != ''">
                AND (username LIKE CONCAT('%', #{condition.keyword}, '%')
                OR email LIKE CONCAT('%', #{condition.keyword}, '%'))
            </if>
            <if test="condition.gender != null">
                AND gender = #{condition.gender}
            </if>
            <if test="condition.startDate != null">
                AND created_at &gt;= #{condition.startDate}
            </if>
            <if test="condition.endDate != null">
                AND created_at &lt;= #{condition.endDate}
            </if>
        </where>
    </select>

</mapper>
```

### 4.2.5 动态SQL

```xml
<select id="dynamicQuery" resultMap="BaseResultMap">
    SELECT
    <include refid="Base_Column_List"/>
    FROM users
    <where>
        <choose>
            <when test="type == 'username'">
                AND username = #{value}
            </when>
            <when test="type == 'email'">
                AND email = #{value}
            </when>
            <otherwise>
                AND (username = #{value} OR email = #{value})
            </otherwise>
        </choose>
        <trim prefix="AND" prefixOverrides="OR">
            <if test="status != null">
                OR status = #{status}
            </if>
            <if test="active != null">
                OR active = #{active}
            </if>
        </trim>
    </where>
</select>

<update id="dynamicUpdate">
    UPDATE users
    <set>
        <if test="username != null">username = #{username},</if>
        <if test="password != null">password = #{password},</if>
        <if test="email != null">email = #{email},</if>
        <if test="phoneNumber != null">phone_number = #{phoneNumber},</if>
        updated_at = NOW()
    </set>
    WHERE id = #{id}
</update>

<select id="forEachExample" resultMap="BaseResultMap">
    SELECT
    <include refid="Base_Column_List"/>
    FROM users
    WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>
```

## 4.3 多数据源配置

### 4.3.1 JPA多数据源

```java
@Configuration
public class PrimaryDataSourceConfig {

    @Primary
    @Bean(name = "primaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Primary
    @Bean(name = "primaryEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean primaryEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("primaryDataSource") DataSource dataSource) {
        return builder
            .dataSource(dataSource)
            .packages("com.example.entity.primary")
            .persistenceUnit("primary")
            .build();
    }

    @Primary
    @Bean(name = "primaryTransactionManager")
    public PlatformTransactionManager primaryTransactionManager(
            @Qualifier("primaryEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }
}

@Configuration
public class SecondaryDataSourceConfig {

    @Bean(name = "secondaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.secondary")
    public DataSource secondaryDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean(name = "secondaryEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean secondaryEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("secondaryDataSource") DataSource dataSource) {
        return builder
            .dataSource(dataSource)
            .packages("com.example.entity.secondary")
            .persistenceUnit("secondary")
            .build();
    }

    @Bean(name = "secondaryTransactionManager")
    public PlatformTransactionManager secondaryTransactionManager(
            @Qualifier("secondaryEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }
}
```

### 4.3.2 MyBatis多数据源

```java
@Configuration
@MapperScan(basePackages = "com.example.mapper.primary",
           sqlSessionFactoryRef = "primarySqlSessionFactory")
public class PrimaryMyBatisConfig {

    @Primary
    @Bean(name = "primaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Primary
    @Bean(name = "primarySqlSessionFactory")
    public SqlSessionFactory primarySqlSessionFactory(
            @Qualifier("primaryDataSource") DataSource dataSource) throws Exception {
        SqlSessionFactoryBean bean = new SqlSessionFactoryBean();
        bean.setDataSource(dataSource);
        bean.setMapperLocations(new PathMatchingResourcePatternResolver()
            .getResources("classpath:mapper/primary/*.xml"));
        return bean.getObject();
    }

    @Primary
    @Bean(name = "primarySqlSessionTemplate")
    public SqlSessionTemplate primarySqlSessionTemplate(
            @Qualifier("primarySqlSessionFactory") SqlSessionFactory sqlSessionFactory) {
        return new SqlSessionTemplate(sqlSessionFactory);
    }
}

@Configuration
@MapperScan(basePackages = "com.example.mapper.secondary",
           sqlSessionFactoryRef = "secondarySqlSessionFactory")
public class SecondaryMyBatisConfig {

    @Bean(name = "secondaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.secondary")
    public DataSource secondaryDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean(name = "secondarySqlSessionFactory")
    public SqlSessionFactory secondarySqlSessionFactory(
            @Qualifier("secondaryDataSource") DataSource dataSource) throws Exception {
        SqlSessionFactoryBean bean = new SqlSessionFactoryBean();
        bean.setDataSource(dataSource);
        bean.setMapperLocations(new PathMatchingResourcePatternResolver()
            .getResources("classpath:mapper/secondary/*.xml"));
        return bean.getObject();
    }

    @Bean(name = "secondarySqlSessionTemplate")
    public SqlSessionTemplate secondarySqlSessionTemplate(
            @Qualifier("secondarySqlSessionFactory") SqlSessionFactory sqlSessionFactory) {
        return new SqlSessionTemplate(sqlSessionFactory);
    }
}
```

## 4.4 互联网大厂真实项目代码示例

### 4.4.1 阿里巴巴JPA配置

```java
package com.alibaba.common.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.transaction.PlatformTransactionManager;

import javax.persistence.EntityManagerFactory;
import javax.sql.DataSource;
import java.util.Properties;

@Configuration
@EnableJpaRepositories(basePackages = "com.alibaba.repository")
@EnableJpaAuditing
public class JpaConfig {

    @Primary
    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.hikari")
    public DataSource dataSource() {
        return new HikariDataSource();
    }

    @Primary
    @Bean
    public LocalContainerEntityManagerFactoryBean entityManagerFactory(DataSource dataSource) {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(dataSource);
        em.setPackagesToScan("com.alibaba.entity");
        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        em.setJpaProperties(hibernateProperties());
        return em;
    }

    private Properties hibernateProperties() {
        Properties properties = new Properties();
        properties.setProperty("hibernate.hbm2ddl.auto", "none");
        properties.setProperty("hibernate.dialect", "org.hibernate.dialect.MySQL8Dialect");
        properties.setProperty("hibernate.show_sql", "false");
        properties.setProperty("hibernate.format_sql", "false");
        properties.setProperty("hibernate.jdbc.batch_size", "50");
        properties.setProperty("hibernate.order_inserts", "true");
        properties.setProperty("hibernate.order_updates", "true");
        properties.setProperty("hibernate.jdbc.fetch_size", "100");
        return properties;
    }

    @Primary
    @Bean
    public PlatformTransactionManager transactionManager(EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }
}
```

### 4.4.2 腾讯云MyBatis配置

```java
package com.tencent.cloud.mybatis;

import com.github.pagehelper.PageInterceptor;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.PlatformTransactionManager;

import javax.sql.DataSource;
import java.util.Properties;

@Configuration
@MapperScan("com.tencent.cloud.mapper")
public class MyBatisConfig {

    @Bean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        SqlSessionFactoryBean bean = new SqlSessionFactoryBean();
        bean.setDataSource(dataSource);
        bean.setTypeAliasesPackage("com.tencent.cloud.entity");
        bean.setMapperLocations(new PathMatchingResourcePatternResolver()
            .getResources("classpath:mapper/*.xml"));

        PageInterceptor pageInterceptor = new PageInterceptor();
        Properties properties = new Properties();
        properties.setProperty("helperDialect", "mysql");
        properties.setProperty("reasonable", "true");
        properties.setProperty("supportMethodsArguments", "true");
        pageInterceptor.setProperties(properties);

        org.apache.ibatis.session.Configuration configuration = new org.apache.ibatis.session.Configuration();
        configuration.setMapUnderscoreToCamelCase(true);
        configuration.setCacheEnabled(true);
        configuration.setLazyLoadingEnabled(true);
        configuration.setAggressiveLazyLoading(false);
        configuration.setDefaultExecutorType(org.apache.ibatis.session.ExecutorType.REUSE);
        bean.setConfiguration(configuration);

        return bean.getObject();
    }

    @Bean
    public PlatformTransactionManager transactionManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

### 4.4.3 美团动态数据源

```java
package com.meituan.datasource;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;

import javax.sql.DataSource;
import java.util.HashMap;
import java.util.Map;

public class DynamicDataSource extends AbstractRoutingDataSource {

    private static final ThreadLocal<String> CONTEXT_HOLDER = new ThreadLocal<>();

    public static void setDataSource(String dataSourceKey) {
        CONTEXT_HOLDER.set(dataSourceKey);
    }

    public static String getDataSource() {
        return CONTEXT_HOLDER.get();
    }

    public static void clearDataSource() {
        CONTEXT_HOLDER.remove();
    }

    @Override
    protected Object determineCurrentLookupKey() {
        return getDataSource();
    }

    public static DataSource createDataSource(String url, String username, String password) {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(url);
        dataSource.setUsername(username);
        dataSource.setPassword(password);
        dataSource.setMinimumIdle(5);
        dataSource.setMaximumPoolSize(20);
        dataSource.setConnectionTimeout(30000);
        dataSource.setIdleTimeout(600000);
        dataSource.setMaxLifetime(1800000);
        return dataSource;
    }

    public static DataSource createDynamicDataSource(DataSource masterDataSource,
                                                     DataSource slaveDataSource) {
        Map<Object, Object> targetDataSources = new HashMap<>();
        targetDataSources.put("master", masterDataSource);
        targetDataSources.put("slave", slaveDataSource);

        DynamicDataSource dynamicDataSource = new DynamicDataSource();
        dynamicDataSource.setDefaultTargetDataSource(masterDataSource);
        dynamicDataSource.setTargetDataSources(targetDataSources);
        return dynamicDataSource;
    }
}
```

### 4.4.4 字节跳动读写分离

```java
package com.bytedance.datasource;

import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class DataSourceAspect {

    @Before("@annotation(com.bytedance.annotation.ReadOnly)")
    public void setReadDataSource() {
        DynamicDataSource.setDataSource("slave");
    }

    @Before("@annotation(com.bytedance.annotation.WriteOnly)")
    public void setWriteDataSource() {
        DynamicDataSource.setDataSource("master");
    }

    @Before("execution(* com.bytedance.service.*.save*(..)) || " +
            "execution(* com.bytedance.service.*.update*(..)) || " +
            "execution(* com.bytedance.service.*.delete*(..))")
    public void setWriteDataSourceForWriteOperations() {
        DynamicDataSource.setDataSource("master");
    }

    @Before("execution(* com.bytedance.service.*.get*(..)) || " +
            "execution(* com.bytedance.service.*.find*(..)) || " +
            "execution(* com.bytedance.service.*.query*(..)) || " +
            "execution(* com.bytedance.service.*.select*(..))")
    public void setReadDataSourceForReadOperations() {
        DynamicDataSource.setDataSource("slave");
    }
}
```

### 4.4.5 京东健康批量操作

```java
package com.jd.health.repository;

import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import javax.sql.DataSource;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.List;

@Repository
public class BatchOperationRepository {

    private final JdbcTemplate jdbcTemplate;

    public BatchOperationRepository(DataSource dataSource) {
        this.jdbcTemplate = new JdbcTemplate(dataSource);
    }

    public int[] batchInsertUsers(List<User> users) {
        String sql = "INSERT INTO users (username, email, phone_number, gender, created_at) " +
                     "VALUES (?, ?, ?, ?, NOW())";

        return jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                User user = users.get(i);
                ps.setString(1, user.getUsername());
                ps.setString(2, user.getEmail());
                ps.setString(3, user.getPhoneNumber());
                ps.setString(4, user.getGender().name());
            }

            @Override
            public int getBatchSize() {
                return users.size();
            }
        });
    }

    public int[] batchUpdateUsers(List<User> users) {
        String sql = "UPDATE users SET email = ?, phone_number = ?, gender = ?, updated_at = NOW() " +
                     "WHERE id = ?";

        return jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                User user = users.get(i);
                ps.setString(1, user.getEmail());
                ps.setString(2, user.getPhoneNumber());
                ps.setString(3, user.getGender().name());
                ps.setLong(4, user.getId());
            }

            @Override
            public int getBatchSize() {
                return users.size();
            }
        });
    }
}
```

### 4.4.6 拼多多复杂查询

```java
package com.pdd.repository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Repository
public class ComplexQueryRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private NamedParameterJdbcTemplate namedParameterJdbcTemplate;

    public List<Order> findOrdersByComplexConditions(OrderQuery query) {
        StringBuilder sql = new StringBuilder();
        sql.append("SELECT o.* FROM orders o ");
        sql.append("LEFT JOIN users u ON o.user_id = u.id ");
        sql.append("LEFT JOIN order_items oi ON o.id = oi.order_id ");
        sql.append("WHERE 1=1 ");

        Map<String, Object> params = new HashMap<>();

        if (query.getUserId() != null) {
            sql.append("AND o.user_id = :userId ");
            params.put("userId", query.getUserId());
        }

        if (query.getStatus() != null) {
            sql.append("AND o.status = :status ");
            params.put("status", query.getStatus());
        }

        if (query.getStartDate() != null) {
            sql.append("AND o.created_at >= :startDate ");
            params.put("startDate", query.getStartDate());
        }

        if (query.getEndDate() != null) {
            sql.append("AND o.created_at <= :endDate ");
            params.put("endDate", query.getEndDate());
        }

        if (query.getMinAmount() != null) {
            sql.append("AND o.total_amount >= :minAmount ");
            params.put("minAmount", query.getMinAmount());
        }

        if (query.getMaxAmount() != null) {
            sql.append("AND o.total_amount <= :maxAmount ");
            params.put("maxAmount", query.getMaxAmount());
        }

        if (query.getKeyword() != null && !query.getKeyword().isEmpty()) {
            sql.append("AND (o.order_no LIKE :keyword OR u.username LIKE :keyword) ");
            params.put("keyword", "%" + query.getKeyword() + "%");
        }

        sql.append("GROUP BY o.id ");
        sql.append("ORDER BY o.created_at DESC ");

        if (query.getPageSize() > 0) {
            sql.append("LIMIT :limit OFFSET :offset ");
            params.put("limit", query.getPageSize());
            params.put("offset", (query.getPageNum() - 1) * query.getPageSize());
        }

        return namedParameterJdbcTemplate.query(sql.toString(), params,
            new BeanPropertyRowMapper<>(Order.class));
    }

    public OrderStatistics getOrderStatistics(OrderQuery query) {
        StringBuilder sql = new StringBuilder();
        sql.append("SELECT ");
        sql.append("COUNT(*) as totalCount, ");
        sql.append("SUM(total_amount) as totalAmount, ");
        sql.append("AVG(total_amount) as avgAmount, ");
        sql.append("MAX(total_amount) as maxAmount, ");
        sql.append("MIN(total_amount) as minAmount ");
        sql.append("FROM orders ");
        sql.append("WHERE 1=1 ");

        Map<String, Object> params = new HashMap<>();

        if (query.getUserId() != null) {
            sql.append("AND user_id = :userId ");
            params.put("userId", query.getUserId());
        }

        if (query.getStatus() != null) {
            sql.append("AND status = :status ");
            params.put("status", query.getStatus());
        }

        if (query.getStartDate() != null) {
            sql.append("AND created_at >= :startDate ");
            params.put("startDate", query.getStartDate());
        }

        if (query.getEndDate() != null) {
            sql.append("AND created_at <= :endDate ");
            params.put("endDate", query.getEndDate());
        }

        return namedParameterJdbcTemplate.queryForObject(sql.toString(), params,
            (rs, rowNum) -> {
                OrderStatistics stats = new OrderStatistics();
                stats.setTotalCount(rs.getLong("totalCount"));
                stats.setTotalAmount(rs.getBigDecimal("totalAmount"));
                stats.setAvgAmount(rs.getBigDecimal("avgAmount"));
                stats.setMaxAmount(rs.getBigDecimal("maxAmount"));
                stats.setMinAmount(rs.getBigDecimal("minAmount"));
                return stats;
            });
    }
}
```

## 4.5 最佳实践

1. **合理选择ORM框架**：JPA适合简单CRUD，MyBatis适合复杂查询
2. **使用连接池**：HikariCP性能优秀
3. **读写分离**：提升数据库性能
4. **批量操作**：减少数据库交互次数
5. **索引优化**：合理创建索引提升查询性能
6. **事务管理**：正确使用@Transactional注解

## 4.6 小结

本章介绍了Spring Boot的数据访问技术，包括：

- Spring Data JPA的使用
- MyBatis的集成与配置
- 多数据源配置
- 动态查询与批量操作
- 读写分离实现

通过本章学习，你应该能够：

- 使用JPA进行数据持久化
- 使用MyBatis进行复杂查询
- 配置多数据源
- 实现读写分离
- 优化数据库操作性能

下一章将介绍Spring Boot的RESTful API开发。
