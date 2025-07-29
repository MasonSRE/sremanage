# 🚀 简化部署功能完整指南

## 概述

简化部署功能让您可以直接粘贴 docker-compose.yml 配置来部署应用，同时集成了AI助手来帮助生成配置。

## ✅ 功能验证状态

| 组件 | 状态 | 说明 |
|------|------|------|
| 后端API | ✅ 正常 | 路由已注册，认证正常 |
| 前端界面 | ✅ 正常 | 运行在 http://localhost:5173 |
| 配置验证 | ✅ 正常 | 语法和安全检查功能正常 |
| AI助手 | ⚠️ 需配置 | 需要在.env中配置API密钥 |

## 🎯 MySQL 8.0.30 部署示例

### 方式1: 直接粘贴配置

访问: http://localhost:5173/software/simple-deploy

粘贴以下配置：

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0.30
    container_name: mysql-prod
    environment:
      - MYSQL_ROOT_PASSWORD=dsg238fh8wh3f
      - TZ=Asia/Shanghai
    ports:
      - "3306:3306"
    volumes:
      - ./data:/var/lib/mysql
      - ./config:/etc/mysql/conf.d
    restart: unless-stopped
```

### 方式2: 使用AI助手（需配置）

1. 配置AI服务（见下方配置说明）
2. 点击"🤖 AI助手"按钮
3. 输入："我要安装MySQL 8.0.30，密码是dsg238fh8wh3f"
4. AI自动生成配置

## 🤖 AI助手配置

### 在 backend/.env 中添加配置：

```bash
# AI助手配置
AI_ENABLED=true
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=your_openai_api_key_here
AI_MODEL=gpt-3.5-turbo
```

### 支持的AI服务：

#### OpenAI 官方
```bash
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=sk-xxx
AI_MODEL=gpt-3.5-turbo
```

#### Claude (如果有OpenAI兼容接口)
```bash
AI_BASE_URL=https://api.anthropic.com/v1
AI_API_KEY=sk-ant-xxx
AI_MODEL=claude-3-sonnet
```

#### 本地模型 (如 Ollama)
```bash
AI_BASE_URL=http://localhost:11434/v1
AI_API_KEY=dummy
AI_MODEL=llama2
```

#### 其他兼容OpenAI格式的服务
```bash
AI_BASE_URL=https://your-service.com/v1
AI_API_KEY=your_key
AI_MODEL=your_model
```

## 📋 部署步骤

### 1. 基本信息
- **实例名称**: mysql-prod （自定义名称）
- **目标服务器**: 选择"运维管理平台测试"

### 2. 配置编辑
- 直接粘贴或编辑 docker-compose.yml 内容
- 系统会实时验证语法
- 检查安全风险

### 3. 执行部署
- 点击"🚀 开始部署"
- 系统自动执行：
  - SSH连接到目标服务器
  - 创建部署目录
  - 写入配置文件
  - 启动Docker容器

### 4. 管理实例
- 在右侧面板查看已部署实例
- 支持启动/停止/删除操作
- 查看实例状态和创建时间

## 🛠️ 技术特性

### 安全检查
- 检测特权模式 (privileged: true)
- 检查危险的卷挂载
- 验证端口配置
- 阻止不安全的网络模式

### 语法验证
- YAML格式验证
- Docker Compose结构检查
- 必要字段验证
- 实时错误提示

### 备用机制
- AI不可用时使用预设模板
- 支持MySQL、Redis、Nginx等常用应用
- 关键词智能匹配

## 🎪 使用演示

### AI对话示例：

```
用户: "我要安装MySQL 8.0.30，密码是dsg238fh8wh3f"

AI: "好的！为你生成MySQL配置：

version: '3.8'
services:
  mysql:
    image: mysql:8.0.30
    container_name: mysql-prod
    environment:
      - MYSQL_ROOT_PASSWORD=dsg238fh8wh3f
      - TZ=Asia/Shanghai
    ports:
      - "3306:3306"
    volumes:
      - ./data:/var/lib/mysql
    restart: unless-stopped

[✅ 使用这个配置]"
```

### 快速部署按钮：
- 🔵 MySQL数据库
- 🔴 Redis缓存  
- 🟢 Nginx服务器

## 🔧 故障排除

### 常见问题

1. **部署失败**
   - 检查目标服务器Docker状态
   - 验证SSH连接配置
   - 确认端口不冲突

2. **AI助手不可用**
   - 检查.env配置
   - 验证API密钥有效性
   - 检查网络连接

3. **配置验证失败**
   - 检查YAML语法
   - 确保包含必要字段
   - 避免安全风险配置

### 调试命令

```bash
# 检查容器状态
docker ps | grep mysql

# 查看容器日志
docker logs mysql-prod

# 测试连接
docker exec -it mysql-prod mysql -u root -p
```

## 📊 API接口

### 主要端点

- `POST /api/simple-deploy/deploy` - 部署应用
- `POST /api/simple-deploy/ai/generate` - AI生成配置
- `GET /api/simple-deploy/ai/status` - AI状态
- `GET /api/simple-deploy/instances` - 实例列表
- `POST /api/simple-deploy/instances/{name}/start` - 启动实例
- `POST /api/simple-deploy/instances/{name}/stop` - 停止实例
- `DELETE /api/simple-deploy/instances/{name}/remove` - 删除实例

## 🎉 完成！

现在您可以访问 http://localhost:5173/software/simple-deploy 开始使用简化部署功能了！

这个功能大大简化了应用部署流程，从复杂的模板变量配置变成了简单的"粘贴配置，一键部署"。