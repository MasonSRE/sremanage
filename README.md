# SREManage - 运维管理系统

一个基于 Vue.js + Flask 的运维管理系统，包含主机管理、批量命令、Web终端、监控等功能。

## 快速开始

### 1. 环境要求
- Python 3.8+
- Node.js 16+
- Docker (用于MySQL)

### 2. 数据库设置
```bash
# 启动MySQL容器
docker run --name sremanage-mysql \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=ops_management \
  -p 3306:3306 -d mysql:8.0

# 等待容器启动，然后执行SQL文件
docker exec -i sremanage-mysql mysql -uroot -pyour_password ops_management < backend/sql/1.user.sql
docker exec -i sremanage-mysql mysql -uroot -pyour_password ops_management < backend/sql/2.hosts.sql
docker exec -i sremanage-mysql mysql -uroot -pyour_password ops_management < backend/sql/3.settings.sql
```

### 3. 后端配置
```bash
cd backend

# 创建环境配置文件
cp .env.example .env

# 编辑.env文件，设置数据库密码等配置
vim .env

# 安装依赖
pip3 install -r requirements.txt

# 启动后端
python3 run.py
```

### 4. 前端配置
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 访问系统
- 前端地址: http://localhost:5173
- 后端API: http://localhost:5002
- 默认账号: admin / 9itNKA6nVs0ZkGw321Tu

## 环境变量说明

参考 `backend/.env.example` 文件中的配置项说明。

## 功能特性

- 🖥️ 主机管理与监控
- 📋 批量命令执行
- 🖥️ Web SSH终端
- 📊 运维数据统计
- 🤖 AI运维助手
- ⚙️ 系统设置管理

## 技术栈

- **前端**: Vue 3 + Vite + Tailwind CSS
- **后端**: Flask + SQLAlchemy + PyMySQL
- **数据库**: MySQL 8.0
- **终端**: xterm.js + WebSocket
EOF < /dev/null