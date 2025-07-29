-- 创建基础设置表
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    config JSON NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 告警设置表
CREATE TABLE IF NOT EXISTS notification_settings (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    methods JSON NOT NULL,
    levels JSON NOT NULL
);

-- 云厂商配置表（替换原aliyun_settings表）
CREATE TABLE IF NOT EXISTS cloud_providers (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '配置名称，如"生产环境阿里云"',
    provider VARCHAR(50) NOT NULL COMMENT '云厂商类型: aliyun, aws, tencent, huawei, google, azure',
    config JSON NOT NULL COMMENT '云厂商配置信息',
    region VARCHAR(50) DEFAULT NULL COMMENT '默认区域',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_provider (provider),
    KEY idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云厂商配置表';

-- 兼容性：保留aliyun_settings表结构，但标记为已弃用
-- CREATE TABLE IF NOT EXISTS aliyun_settings (
--     id INTEGER AUTO_INCREMENT PRIMARY KEY,
--     access_key_id TEXT NOT NULL,
--     access_key_secret TEXT NOT NULL,
--     region TEXT NOT NULL
-- ) COMMENT='已弃用，请使用cloud_providers表';

-- 邮箱设置表
CREATE TABLE IF NOT EXISTS mail_settings (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    smtp_server TEXT NOT NULL,
    smtp_port INTEGER NOT NULL,
    sender_email TEXT NOT NULL,
    password TEXT NOT NULL,
    use_tls BOOLEAN NOT NULL DEFAULT 1
);

-- Jenkins设置表
CREATE TABLE IF NOT EXISTS jenkins_settings (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    username VARCHAR(100) NOT NULL,
    token TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 将短信通知设置为禁用状态
INSERT INTO settings (id, type, config, enabled) 
VALUES (1, 'sms', '{"enabled": false}', FALSE)
ON DUPLICATE KEY UPDATE 
    config = VALUES(config),
    enabled = VALUES(enabled);