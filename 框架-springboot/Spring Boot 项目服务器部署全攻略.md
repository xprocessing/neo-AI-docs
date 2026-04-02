# Spring Boot 项目服务器部署全攻略

Spring Boot 项目部署到服务器是开发的核心收尾环节，我会为你提供 **3 种主流部署方式**（覆盖新手友好、生产级稳定、容器化高效），从环境准备到实操步骤全程拆解，适配不同服务器场景（Linux 为主）。

### 前置准备

1. **服务器环境**：Linux 服务器（CentOS/Ubuntu），已安装对应版本的 **JDK**（需和项目开发时的 Java 版本一致，如 JDK 17）；

2. **项目打包**：本地用 Maven/Gradle 打包成 **可执行 JAR 包**（Spring Boot 推荐）：

    ```Bash
    
    # Maven 打包（跳过测试）
    mvn clean package -DskipTests
    # 打包后文件路径：target/xxx-0.0.1-SNAPSHOT.jar
    ```

3. **文件传输**：用 `scp` 或 FinalShell/Xftp 等工具，将 JAR 包上传到服务器（如 `/usr/local/project/` 目录）。

---

## 方式 1：手动启动（新手入门，快速验证）

适合调试/临时部署，缺点是终端关闭后进程会终止。

### 1. 启动项目

```Bash

# 进入 JAR 包目录
cd /usr/local/project/
# 启动 Spring Boot 项目
java -jar xxx-0.0.1-SNAPSHOT.jar
```

### 2. 后台启动（避免终端关闭终止）

```Bash

# 后台启动，日志输出到 app.log
nohup java -jar xxx-0.0.1-SNAPSHOT.jar > app.log 2>&1 &
```

### 3. 停止项目

```Bash

# 查找进程 ID
ps -ef | grep java | grep xxx-0.0.1-SNAPSHOT.jar
# 杀死进程（替换为实际 PID）
kill -9 12345
```

---

## 方式 2：系统服务部署（生产级稳定，推荐）

将 Spring Boot 注册为 Linux 系统服务，支持开机自启、统一管理，是企业生产环境的主流方式。

### 1. 创建系统服务文件

```Bash

# 编辑服务配置文件（命名为 springboot-app.service）
vim /etc/systemd/system/springboot-app.service
```

### 2. 写入配置内容（按需修改）

```TOML

[Unit]
Description=Spring Boot Application
After=network.target

[Service]
# 执行用户（推荐用非 root 用户，如 appuser）
User=root
# JAR 包路径
ExecStart=/usr/bin/java -jar /usr/local/project/xxx-0.0.1-SNAPSHOT.jar
# 进程崩溃自动重启
Restart=always
# 日志输出目录（需提前创建）
StandardOutput=append:/usr/local/project/logs/app.log
StandardError=append:/usr/local/project/logs/error.log

[Install]
WantedBy=multi-user.target
```

### 3. 配置生效并启动服务

```Bash

# 重新加载系统服务配置
systemctl daemon-reload

# 启动服务
systemctl start springboot-app

# 设置开机自启
systemctl enable springboot-app

# 查看服务状态
systemctl status springboot-app

# 停止/重启服务
systemctl stop springboot-app
systemctl restart springboot-app
```

---

## 方式 3：Docker 容器化部署（高效运维，适合集群）

将项目打包为 Docker 镜像，跨环境一致运行，适合多服务器/集群部署。

### 1. 本地编写 Dockerfile

在项目根目录创建 `Dockerfile`（无需手动打包 JAR，Docker 自动构建）：

```Dockerfile

# 基础镜像（JDK 17）
FROM openjdk:17-jdk-slim

# 作者信息
MAINTAINER yourname <your@email.com>

# 挂载日志目录
VOLUME /tmp

# 复制本地 JAR 包到容器（target 为打包目录）
COPY target/xxx-0.0.1-SNAPSHOT.jar app.jar

# 暴露项目端口（和 application.yml 中 server.port 一致）
EXPOSE 8080

# 启动命令
ENTRYPOINT ["java","-jar","/app.jar"]
```

### 2. 构建 Docker 镜像

```Bash

# 本地构建镜像（tag 格式：名称:版本）
docker build -t springboot-app:1.0 .

# 将镜像上传到服务器（或直接在服务器构建）
# 方式 1：推送到镜像仓库（如 Docker Hub），服务器拉取
# 方式 2：保存镜像为 tar 包，上传到服务器后加载
docker save -o springboot-app.tar springboot-app:1.0
scp springboot-app.tar root@服务器IP:/usr/local/project/
# 服务器加载镜像
docker load -i springboot-app.tar
```

### 3. 服务器启动容器

```Bash

# 启动容器（端口映射：主机8080 → 容器8080）
docker run -d --name springboot-app -p 8080:8080 springboot-app:1.0

# 查看容器日志
docker logs -f springboot-app

# 停止/重启容器
docker stop springboot-app
docker restart springboot-app
```

---

## 关键补充：部署优化

### 1. 配置文件外置（避免改代码重新打包）

```Bash

# 启动时指定外部配置文件
java -jar xxx.jar --spring.config.location=/usr/local/project/application.yml
# Docker 启动时挂载配置文件
docker run -d -p 8080:8080 -v /usr/local/project/application.yml:/application.yml springboot-app:1.0
```

### 2. JVM 参数优化（提升性能）

```Bash

# 启动时添加 JVM 参数（调整内存）
java -Xms512m -Xmx1024m -jar xxx.jar
# 解释：-Xms 初始内存，-Xmx 最大内存
```

### 3. 端口放行（服务器防火墙）

```Bash

# CentOS 放行 8080 端口
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --reload

# Ubuntu 放行端口
ufw allow 8080/tcp
```

---

### 总结

1. **快速验证**：用 `nohup java -jar` 手动启动，适合调试；

2. **生产环境**：优先注册为 Linux 系统服务，支持开机自启、进程守护；

3. **高效运维**：Docker 容器化部署，跨环境一致，适合集群/多版本管理。

核心要点：确保服务器 JDK 版本和项目一致，打包为可执行 JAR 包，根据场景选择部署方式，记得放行端口和优化 JVM 参数。

如果需要具体的 **Nginx 反向代理配置**（将 80/443 端口映射到 Spring Boot 项目），或 **CI/CD 自动部署脚本**（Jenkins 一键部署），我可以补充完整步骤。
> （注：文档部分内容可能由 AI 生成）