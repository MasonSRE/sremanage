-- 站点监控表结构

-- 设置字符集确保中文字符正确处理
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

-- 站点监控配置表
CREATE TABLE IF NOT EXISTS site_monitoring (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_name VARCHAR(255) NOT NULL COMMENT '站点名称',
    site_url VARCHAR(500) NOT NULL COMMENT '站点URL',
    check_interval INT DEFAULT 300 COMMENT '检查间隔（秒）',
    timeout INT DEFAULT 30 COMMENT '超时时间（秒）',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用监控',
    status VARCHAR(20) DEFAULT 'unknown' COMMENT '当前状态：online, offline, unknown',
    last_check_time DATETIME COMMENT '最后检查时间',
    last_response_time INT COMMENT '最后响应时间（毫秒）',
    failure_count INT DEFAULT 0 COMMENT '连续失败次数',
    description TEXT COMMENT '描述信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_site_url (site_url),
    INDEX idx_status (status),
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站点监控配置表';

-- 站点监控历史记录表
CREATE TABLE IF NOT EXISTS site_monitoring_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL COMMENT '站点ID',
    check_time DATETIME NOT NULL COMMENT '检查时间',
    status VARCHAR(20) NOT NULL COMMENT '状态：online, offline, timeout, error',
    response_time INT COMMENT '响应时间（毫秒）',
    http_code INT COMMENT 'HTTP状态码',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES site_monitoring(id) ON DELETE CASCADE,
    INDEX idx_site_id (site_id),
    INDEX idx_check_time (check_time),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站点监控历史记录表';

-- 插入示例数据
INSERT INTO site_monitoring (site_name, site_url, check_interval, timeout, enabled, status, description) 
VALUES 
('示例站点', 'https://example.com', 300, 30, 1, 'unknown', '示例站点监控'),
('百度', 'https://www.baidu.com', 300, 30, 1, 'unknown', '百度搜索引擎'),
('Google', 'https://www.google.com', 300, 30, 1, 'unknown', 'Google搜索引擎')
ON DUPLICATE KEY UPDATE 
    site_name = VALUES(site_name),
    site_url = VALUES(site_url),
    check_interval = VALUES(check_interval),
    timeout = VALUES(timeout),
    enabled = VALUES(enabled),
    description = VALUES(description);