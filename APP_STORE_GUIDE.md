# 应用商店使用指南

## 🎯 重构概述

原本硬编码的应用配置现已升级为**动态模板化管理系统**，支持用户自定义添加任何Docker应用。

## 📋 功能说明

### 三个核心标签页

1. **应用商店** - 浏览和安装应用
2. **已安装** - 管理应用实例  
3. **应用管理** - 配置和管理模板（新增）

### 应用类型

- **系统预设应用**：nginx、mysql、redis、postgresql、mongodb
  - ❌ 不可编辑和删除
  - ✅ 可以复制后修改
  
- **自定义应用**：用户创建的应用模板
  - ✅ 可以编辑、复制和删除

## 🚀 如何添加新应用（以Kafka为例）

### 方法一：从零创建

1. 进入 **"应用管理"** 标签页
2. 点击 **"添加应用模板"** 
3. 填写基本信息：
   ```
   应用ID: kafka
   应用名称: Apache Kafka
   分类: 其他
   描述: 分布式流处理平台
   ```

4. 配置Docker Compose模板：
   ```yaml
   version: '3.8'
   services:
     kafka:
       image: confluentinc/cp-kafka:${KAFKA_VERSION}
       container_name: ${CONTAINER_NAME}
       ports:
         - "${KAFKA_PORT}:9092"
       environment:
         KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
         KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:${KAFKA_PORT}
         KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
       volumes:
         - ./data:/var/lib/kafka/data
       restart: unless-stopped
   ```

5. 配置环境变量：
   - `KAFKA_VERSION`: 默认值 `latest`, 描述 `Kafka版本`
   - `KAFKA_PORT`: 默认值 `9092`, 描述 `Kafka端口`

6. 配置端口映射：
   - 端口名称: `Kafka`
   - 主机端口: `9092`
   - 容器端口: `9092`
   - 协议: `TCP`

7. 点击 **"创建"** 保存

### 方法二：复制现有模板

1. 在 **"应用管理"** 中找到相似的应用（如Redis）
2. 点击 **"复制"** 按钮
3. 修改应用信息和配置
4. 点击 **"创建"** 保存

## 🔧 如何修改系统预设应用（以修改MySQL端口为例）

由于系统预设应用受到保护，需要通过复制来实现修改：

1. 在 **"应用管理"** 中找到MySQL
2. 点击 **"复制"** 按钮  
3. 修改信息：
   ```
   应用ID: mysql_custom
   应用名称: MySQL (自定义)
   ```
4. 在环境变量中修改：
   ```
   MYSQL_PORT: 默认值改为 3307
   ```
5. 在端口配置中修改：
   ```
   主机端口: 3307
   ```
6. 点击 **"创建"** 保存
7. 现在可以安装使用自定义端口的MySQL

## 📊 模板变量说明

### 系统内置变量
- `${CONTAINER_NAME}`: 自动生成的容器名称
- `${INSTANCE_ID}`: 实例唯一标识符
- `${INSTANCE_NAME}`: 用户定义的实例名称

### 自定义变量
在环境变量配置中定义的所有变量都可以在Docker Compose模板中使用。

### 使用示例
```yaml
services:
  app:
    image: myapp:${APP_VERSION}
    container_name: ${CONTAINER_NAME}
    ports:
      - "${APP_PORT}:8080"
    environment:
      - DATABASE_URL=${DB_URL}
```

## 🛠 实例管理

安装后的应用可以在 **"已安装"** 标签页中管理：

- **启动**: 启动停止的应用
- **停止**: 停止运行的应用  
- **重启**: 重启应用
- **查看日志**: 查看安装和运行日志
- **卸载**: 完全移除应用和数据

## 🔄 数据库迁移

如果需要应用新的数据库结构：

```bash
cd backend
mysql -u root -p sremanage < sql/5.app_store_unified.sql
```

## 🎉 优势总结

1. **无需修改代码**: 添加新应用只需配置，不需要重新部署
2. **灵活配置**: 支持复杂的多容器应用
3. **版本管理**: 每个应用模板都有版本控制
4. **安全保护**: 系统预设应用受到保护
5. **用户友好**: 可视化配置界面，降低使用门槛

## ❓ 常见问题

**Q: 能否修改nginx的默认端口？**
A: 复制nginx模板，修改端口配置后创建自定义版本。

**Q: 如何部署多实例？**  
A: 在安装时为每个实例设置不同的实例名称和端口。

**Q: 支持docker-compose之外的部署方式吗？**
A: 目前只支持docker-compose，未来可扩展支持Kubernetes。

**Q: 能否导入现有的docker-compose文件？**
A: 可以将现有的docker-compose内容复制到模板配置中。

---

现在你可以轻松添加Kafka或任何其他Docker应用，无需修改代码！🚀