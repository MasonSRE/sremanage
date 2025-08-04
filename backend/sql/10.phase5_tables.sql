-- Phase 5 生产优化相关数据库表
-- 创建日期: 2025-07-31

-- 性能监控表
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL COMMENT 'API端点',
    duration FLOAT NOT NULL COMMENT '响应耗时(秒)',
    status VARCHAR(50) NOT NULL DEFAULT 'success' COMMENT '请求状态',
    error_message TEXT COMMENT '错误信息',
    user_id VARCHAR(100) COMMENT '用户ID',
    ip_address VARCHAR(45) COMMENT '客户端IP',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    INDEX idx_endpoint_timestamp (endpoint, timestamp),
    INDEX idx_status (status),
    INDEX idx_user_ip (user_id, ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API性能监控表';

-- 安全审计日志表
CREATE TABLE IF NOT EXISTS security_audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL COMMENT '事件类型',
    user_id VARCHAR(100) COMMENT '用户ID',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    details JSON COMMENT '事件详情',
    severity VARCHAR(20) DEFAULT 'low' COMMENT '严重程度: low/medium/high/critical',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '事件时间',
    INDEX idx_event_type_timestamp (event_type, timestamp),
    INDEX idx_user_ip (user_id, ip_address),
    INDEX idx_severity (severity),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='安全审计日志表';

-- 用户角色权限表
CREATE TABLE IF NOT EXISTS user_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL COMMENT '用户ID',
    role_name VARCHAR(100) NOT NULL COMMENT '角色名称',
    granted_by VARCHAR(100) COMMENT '授权人',
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
    expires_at DATETIME COMMENT '过期时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    UNIQUE KEY unique_user_role (user_id, role_name),
    INDEX idx_user_id (user_id),
    INDEX idx_role_name (role_name),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色权限表';

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(255) PRIMARY KEY COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type VARCHAR(50) DEFAULT 'string' COMMENT '配置类型: string/integer/boolean/json',
    description TEXT COMMENT '配置描述',
    is_encrypted BOOLEAN DEFAULT FALSE COMMENT '是否加密存储',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_config_type (config_type),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 错误日志表
CREATE TABLE IF NOT EXISTS error_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    error_code INT NOT NULL COMMENT '错误代码',
    error_category VARCHAR(50) NOT NULL COMMENT '错误分类',
    error_message TEXT NOT NULL COMMENT '错误信息',
    error_details JSON COMMENT '错误详情',
    user_id VARCHAR(100) COMMENT '用户ID',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    request_id VARCHAR(100) COMMENT '请求ID',
    endpoint VARCHAR(255) COMMENT 'API端点',
    severity VARCHAR(20) DEFAULT 'medium' COMMENT '严重程度',
    is_resolved BOOLEAN DEFAULT FALSE COMMENT '是否已解决',
    resolved_at DATETIME COMMENT '解决时间',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发生时间',
    INDEX idx_error_code (error_code),
    INDEX idx_error_category (error_category),
    INDEX idx_severity (severity),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_endpoint (user_id, endpoint)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='错误日志表';

-- 缓存统计表
CREATE TABLE IF NOT EXISTS cache_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL COMMENT '缓存键',
    cache_type VARCHAR(50) NOT NULL COMMENT '缓存类型',
    hit_count INT DEFAULT 0 COMMENT '命中次数',
    miss_count INT DEFAULT 0 COMMENT '未命中次数',
    last_hit_at DATETIME COMMENT '最后命中时间',
    last_miss_at DATETIME COMMENT '最后未命中时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY unique_cache_key (cache_key, cache_type),
    INDEX idx_cache_type (cache_type),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='缓存统计表';

-- 初始化默认系统配置
INSERT IGNORE INTO system_config (config_key, config_value, config_type, description) VALUES
('performance_monitor_enabled', 'true', 'boolean', '性能监控开关'),
('security_audit_enabled', 'true', 'boolean', '安全审计开关'),
('cache_default_ttl', '300', 'integer', '默认缓存TTL(秒)'),
('rate_limit_requests', '100', 'integer', '速率限制-请求数'),
('rate_limit_window', '60', 'integer', '速率限制-时间窗口(秒)'),
('circuit_breaker_threshold', '5', 'integer', '熔断器失败阈值'),
('circuit_breaker_timeout', '60', 'integer', '熔断器恢复超时(秒)'),
('max_retry_attempts', '3', 'integer', '最大重试次数'),
('encryption_key_rotation_days', '90', 'integer', '密钥轮换天数'),
('audit_log_retention_days', '365', 'integer', '审计日志保留天数'),
('database_pool_size', '20', 'integer', '数据库连接池大小'),
('max_login_attempts', '5', 'integer', '最大登录尝试次数'),
('ip_block_duration', '3600', 'integer', 'IP阻止持续时间(秒)');

-- 创建性能监控视图
CREATE OR REPLACE VIEW v_performance_summary AS
SELECT 
    endpoint,
    COUNT(*) as total_requests,
    AVG(duration) as avg_duration,
    MIN(duration) as min_duration,
    MAX(duration) as max_duration,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
    (SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate,
    DATE(timestamp) as date_recorded
FROM performance_metrics 
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY endpoint, DATE(timestamp)
ORDER BY date_recorded DESC, avg_duration DESC;

-- 创建安全事件汇总视图
CREATE OR REPLACE VIEW v_security_summary AS
SELECT 
    event_type,
    severity,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as affected_users,
    COUNT(DISTINCT ip_address) as unique_ips,
    DATE(timestamp) as date_recorded,
    MAX(timestamp) as last_occurrence
FROM security_audit_log 
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY event_type, severity, DATE(timestamp)
ORDER BY date_recorded DESC, event_count DESC;

-- 创建用户权限视图
CREATE OR REPLACE VIEW v_user_permissions AS
SELECT 
    ur.user_id,
    ur.role_name,
    ur.granted_by,
    ur.granted_at,
    ur.expires_at,
    ur.is_active,
    CASE 
        WHEN ur.expires_at IS NULL THEN 'permanent'
        WHEN ur.expires_at > NOW() THEN 'active'
        ELSE 'expired'
    END as status
FROM user_roles ur
WHERE ur.is_active = TRUE
ORDER BY ur.user_id, ur.granted_at DESC;