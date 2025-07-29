# MySQL 8.0.30 安装测试指南

## 🎯 测试目标
使用应用商店功能在"运维管理平台测试"服务器上安装MySQL 8.0.30，密码设置为"dsg238fh8wh3f"。

## 🏗️ 系统架构确认

### 应用商店组件
- **前端界面**: Vue.js + Tailwind CSS (http://localhost:5174)
- **后端API**: Flask + SQLAlchemy (http://localhost:5000)
- **数据库**: MySQL (应用模板和实例记录)
- **部署方式**: Docker Compose (自动SSH部署)

### MySQL模板配置
```yaml
# 预配置的MySQL模板
ID: mysql
名称: MySQL
版本: 8.0 (可自定义为8.0.30)
分类: database
端口: 3306
密码: 可配置 (默认123456，可改为dsg238fh8wh3f)
```

## 📋 测试步骤

### 步骤1: 登录系统
1. 访问: http://localhost:5174
2. 使用管理员账户登录:
   - 用户名: `admin`
   - 密码: `9itNKA6nVs0ZkGw321Tu`

### 步骤2: 进入应用商店
1. 导航至: **软件管理 → 应用商店**
2. 在"数据库"分类中找到MySQL应用
3. 查看MySQL应用详情:
   - 默认版本: 8.0
   - 支持的配置参数:
     - `MYSQL_VERSION`: MySQL版本
     - `MYSQL_PORT`: 端口号  
     - `MYSQL_ROOT_PASSWORD`: Root密码

### 步骤3: 配置MySQL安装
点击MySQL应用的"立即安装"按钮，配置如下:

```
目标主机: 运维管理平台测试
实例名称: mysql-8030-test
配置参数:
  - MySQL版本: 8.0.30
  - MySQL端口: 3306
  - Root密码: dsg238fh8wh3f
```

### 步骤4: 执行安装
1. 确认配置后点击"确认安装"
2. 系统将执行以下操作:
   - SSH连接到目标服务器
   - 检查并安装Docker环境
   - 创建应用目录: `/opt/sremanage/apps/mysql_[实例ID]`
   - 生成docker-compose.yml文件
   - 启动MySQL容器

### 步骤5: 验证安装
1. 在"已安装"标签页查看MySQL实例状态
2. 点击"查看日志"按钮查看安装日志
3. SSH到服务器验证:
   ```bash
   # 查看运行的容器
   docker ps | grep mysql
   
   # 连接MySQL测试
   docker exec -it sremanage_mysql_[实例ID] mysql -u root -p
   # 输入密码: dsg238fh8wh3f
   ```

## 🔧 预期的Docker Compose配置

安装过程将生成以下配置文件:

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0.30
    container_name: sremanage_mysql_[实例ID]
    ports:
      - "3306:3306"
    volumes:
      - ./data:/var/lib/mysql
      - ./config:/etc/mysql/conf.d
    environment:
      - MYSQL_ROOT_PASSWORD=dsg238fh8wh3f
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

**.env文件**:
```env
MYSQL_VERSION=8.0.30
MYSQL_PORT=3306
MYSQL_ROOT_PASSWORD=dsg238fh8wh3f
```

## 📊 功能验证清单

- [ ] 成功登录应用商店界面
- [ ] 找到MySQL应用模板
- [ ] 选择"运维管理平台测试"服务器
- [ ] 配置MySQL 8.0.30版本
- [ ] 设置密码为"dsg238fh8wh3f"
- [ ] 安装过程无错误
- [ ] MySQL容器启动成功
- [ ] 可以使用配置的密码连接数据库
- [ ] 数据持久化目录创建正确
- [ ] 在"已安装"界面能看到实例状态

## 🔧 故障排除

### 常见问题
1. **认证失败**: 确保使用正确的管理员凭据
2. **主机连接失败**: 检查SSH连接配置
3. **Docker未安装**: 系统会自动安装Docker
4. **端口冲突**: 修改MYSQL_PORT配置
5. **权限问题**: 确保SSH用户有sudo权限

### 调试命令
```bash
# 查看应用目录
ls -la /opt/sremanage/apps/

# 查看Docker容器状态  
docker ps -a

# 查看容器日志
docker logs sremanage_mysql_[实例ID]

# 测试MySQL连接
docker exec -it sremanage_mysql_[实例ID] mysql -u root -p -e "SELECT VERSION();"
```

## 🎉 成功标志

安装成功后应该能看到:
1. ✅ MySQL 8.0.30容器正在运行
2. ✅ 使用密码"dsg238fh8wh3f"能够连接
3. ✅ 数据目录已创建并挂载
4. ✅ 在应用商店"已安装"页面显示为"运行中"
5. ✅ 可以通过Web界面管理(启动/停止/查看日志)

## 📱 Web界面操作流程

```
http://localhost:5174
    ↓
[登录] admin / 9itNKA6nVs0ZkGw321Tu
    ↓  
[软件管理] → [应用商店]
    ↓
[数据库分类] → [MySQL] → [立即安装]
    ↓
[选择主机: 运维管理平台测试]
    ↓
[配置参数]
  - MySQL版本: 8.0.30
  - MySQL端口: 3306
  - Root密码: dsg238fh8wh3f
    ↓
[确认安装] → [查看安装日志] → [验证成功]
```

这个完整的测试流程将验证你的应用商店MySQL安装功能是否正常工作。