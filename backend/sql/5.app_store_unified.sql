-- 统一的应用商店数据库设计
-- 支持模板化配置的应用管理系统

-- 应用模板表 - 存储应用的配置模板
CREATE TABLE IF NOT EXISTS app_templates (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    version VARCHAR(20) DEFAULT 'latest',
    logo_url VARCHAR(255),
    tags JSON,
    
    -- 部署配置
    deploy_type ENUM('docker', 'docker_compose', 'script') DEFAULT 'docker_compose',
    compose_template TEXT,  -- docker-compose模板
    
    -- 服务配置
    services JSON,  -- 服务定义配置
    
    -- 端口配置
    ports JSON,  -- 端口映射配置
    
    -- 存储卷配置
    volumes JSON,  -- 存储卷配置
    
    -- 环境变量配置
    env_vars JSON,  -- 环境变量定义
    
    -- 状态和权限
    status ENUM('active', 'disabled', 'draft') DEFAULT 'active',
    is_system BOOLEAN DEFAULT FALSE,  -- 是否为系统预设
    created_by VARCHAR(50),
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 应用实例表 - 存储已安装的应用实例
CREATE TABLE IF NOT EXISTS app_instances (
    id VARCHAR(50) PRIMARY KEY,
    template_id VARCHAR(50) NOT NULL,
    instance_name VARCHAR(100) NOT NULL,
    host_id VARCHAR(50) NOT NULL,
    host_type ENUM('manual', 'aliyun') DEFAULT 'manual',
    
    -- 实例配置
    config JSON,  -- 实例特定配置
    deploy_path VARCHAR(255),  -- 部署路径
    
    -- 状态信息
    status ENUM('installing', 'running', 'stopped', 'failed', 'uninstalling') DEFAULT 'installing',
    health_status ENUM('healthy', 'unhealthy', 'unknown') DEFAULT 'unknown',
    
    -- 端口映射
    port_mappings JSON,  -- 实际端口映射
    
    -- 时间戳
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (template_id) REFERENCES app_templates(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_template_id (template_id),
    INDEX idx_host_id (host_id),
    INDEX idx_status (status)
);

-- 应用实例日志表 - 存储安装和运行日志
CREATE TABLE IF NOT EXISTS app_instance_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instance_id VARCHAR(50) NOT NULL,
    log_type ENUM('install', 'start', 'stop', 'error', 'info') DEFAULT 'info',
    message TEXT,
    details JSON,  -- 详细信息
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (instance_id) REFERENCES app_instances(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_instance_id (instance_id),
    INDEX idx_log_type (log_type),
    INDEX idx_created_at (created_at)
);

-- 应用分类表 - 管理应用分类
CREATE TABLE IF NOT EXISTS app_categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    sort_order INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入默认分类
INSERT INTO app_categories (id, name, description, icon, sort_order) VALUES
('web', 'Web服务', 'Web服务器和反向代理', 'globe', 1),
('database', '数据库', '关系型和NoSQL数据库', 'database', 2),
('cache', '缓存', '缓存和内存数据库', 'zap', 3),
('monitor', '监控', '监控和日志收集工具', 'chart-bar', 4),
('dev', '开发工具', '开发和构建工具', 'code', 5),
('other', '其他', '其他应用', 'dots-horizontal', 99);

-- 插入系统预设应用模板
INSERT INTO app_templates (id, name, description, category, version, tags, deploy_type, compose_template, services, ports, volumes, env_vars, is_system) VALUES
(
    'nginx',
    'Nginx',
    '高性能的HTTP和反向代理web服务器',
    'web',
    'latest',
    JSON_ARRAY('web', 'proxy', 'server'),
    'docker_compose',
    'version: ''3.8''\nservices:\n  nginx:\n    image: nginx:${NGINX_VERSION}\n    container_name: ${CONTAINER_NAME}\n    ports:\n      - "${NGINX_PORT}:80"\n    volumes:\n      - ./config:/etc/nginx/conf.d:ro\n      - ./data:/usr/share/nginx/html\n      - ./logs:/var/log/nginx\n    restart: unless-stopped\n    environment:\n      - TZ=Asia/Shanghai',
    JSON_OBJECT(
        'nginx', JSON_OBJECT(
            'image', 'nginx:${NGINX_VERSION}',
            'ports', JSON_ARRAY(JSON_OBJECT('host', '${NGINX_PORT}', 'container', 80)),
            'volumes', JSON_ARRAY(
                JSON_OBJECT('host', 'config', 'container', '/etc/nginx/conf.d', 'mode', 'ro'),
                JSON_OBJECT('host', 'data', 'container', '/usr/share/nginx/html'),
                JSON_OBJECT('host', 'logs', 'container', '/var/log/nginx')
            )
        )
    ),
    JSON_ARRAY(
        JSON_OBJECT('name', 'HTTP', 'host', 8080, 'container', 80, 'protocol', 'tcp')
    ),
    JSON_ARRAY(
        JSON_OBJECT('name', '配置目录', 'host', 'config', 'container', '/etc/nginx/conf.d'),
        JSON_OBJECT('name', '网站目录', 'host', 'data', 'container', '/usr/share/nginx/html'),
        JSON_OBJECT('name', '日志目录', 'host', 'logs', 'container', '/var/log/nginx')
    ),
    JSON_OBJECT(
        'NGINX_VERSION', JSON_OBJECT('default', 'latest', 'description', 'Nginx版本', 'required', false),
        'NGINX_PORT', JSON_OBJECT('default', '8080', 'description', 'HTTP端口', 'required', true)
    ),
    TRUE
),
(
    'mysql',
    'MySQL',
    '世界上最流行的开源关系型数据库',
    'database',
    '8.0',
    JSON_ARRAY('database', 'sql', 'mysql'),
    'docker_compose',
    'version: ''3.8''\nservices:\n  mysql:\n    image: mysql:${MYSQL_VERSION}\n    container_name: ${CONTAINER_NAME}\n    ports:\n      - "${MYSQL_PORT}:3306"\n    volumes:\n      - ./data:/var/lib/mysql\n      - ./config:/etc/mysql/conf.d\n    environment:\n      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}\n      - TZ=Asia/Shanghai\n    restart: unless-stopped',
    JSON_OBJECT(
        'mysql', JSON_OBJECT(
            'image', 'mysql:${MYSQL_VERSION}',
            'ports', JSON_ARRAY(JSON_OBJECT('host', '${MYSQL_PORT}', 'container', 3306)),
            'volumes', JSON_ARRAY(
                JSON_OBJECT('host', 'data', 'container', '/var/lib/mysql'),
                JSON_OBJECT('host', 'config', 'container', '/etc/mysql/conf.d')
            )
        )
    ),
    JSON_ARRAY(
        JSON_OBJECT('name', 'MySQL', 'host', 3306, 'container', 3306, 'protocol', 'tcp')
    ),
    JSON_ARRAY(
        JSON_OBJECT('name', '数据目录', 'host', 'data', 'container', '/var/lib/mysql'),
        JSON_OBJECT('name', '配置目录', 'host', 'config', 'container', '/etc/mysql/conf.d')
    ),
    JSON_OBJECT(
        'MYSQL_VERSION', JSON_OBJECT('default', '8.0', 'description', 'MySQL版本', 'required', false),
        'MYSQL_PORT', JSON_OBJECT('default', '3306', 'description', 'MySQL端口', 'required', true),
        'MYSQL_ROOT_PASSWORD', JSON_OBJECT('default', '123456', 'description', 'Root密码', 'required', true)
    ),
    TRUE
),
(
    'redis',
    'Redis',
    '内存中的数据结构存储，用作数据库、缓存和消息代理',
    'cache',
    '7',
    JSON_ARRAY('cache', 'nosql', 'redis'),
    'docker_compose',
    'version: ''3.8''\nservices:\n  redis:\n    image: redis:${REDIS_VERSION}\n    container_name: ${CONTAINER_NAME}\n    ports:\n      - "${REDIS_PORT}:6379"\n    volumes:\n      - ./data:/data\n    restart: unless-stopped\n    environment:\n      - TZ=Asia/Shanghai\n    command: redis-server --appendonly yes',
    JSON_OBJECT(
        'redis', JSON_OBJECT(
            'image', 'redis:${REDIS_VERSION}',
            'ports', JSON_ARRAY(JSON_OBJECT('host', '${REDIS_PORT}', 'container', 6379)),
            'volumes', JSON_ARRAY(
                JSON_OBJECT('host', 'data', 'container', '/data')
            )
        )
    ),
    JSON_ARRAY(
        JSON_OBJECT('name', 'Redis', 'host', 6379, 'container', 6379, 'protocol', 'tcp')
    ),
    JSON_ARRAY(
        JSON_OBJECT('name', '数据目录', 'host', 'data', 'container', '/data')
    ),
    JSON_OBJECT(
        'REDIS_VERSION', JSON_OBJECT('default', '7', 'description', 'Redis版本', 'required', false),
        'REDIS_PORT', JSON_OBJECT('default', '6379', 'description', 'Redis端口', 'required', true)
    ),
    TRUE
);