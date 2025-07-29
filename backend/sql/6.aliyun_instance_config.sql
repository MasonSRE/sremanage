-- 云实例连接配置表（替换原aliyun_instance_config表）
-- 用于存储各云厂商实例的SSH连接配置信息
CREATE TABLE IF NOT EXISTS `cloud_instance_config` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `provider_id` int(11) NOT NULL COMMENT '云厂商配置ID',
    `instance_id` varchar(100) NOT NULL COMMENT '实例ID',
    `instance_name` varchar(200) DEFAULT NULL COMMENT '实例名称',
    `ssh_port` int(11) NOT NULL DEFAULT 22 COMMENT 'SSH端口',
    `username` varchar(50) NOT NULL DEFAULT 'root' COMMENT '用户名',
    `password` varchar(255) DEFAULT NULL COMMENT '密码',
    `private_key` text DEFAULT NULL COMMENT '私钥',
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_provider_instance` (`provider_id`, `instance_id`),
    KEY `idx_provider_id` (`provider_id`),
    CONSTRAINT `fk_cloud_instance_provider` FOREIGN KEY (`provider_id`) REFERENCES `cloud_providers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云实例连接配置表';

-- 兼容性：保留aliyun_instance_config表结构，但标记为已弃用
-- CREATE TABLE IF NOT EXISTS `aliyun_instance_config` (
--   `id` int(11) NOT NULL AUTO_INCREMENT,
--   `instance_id` varchar(50) NOT NULL COMMENT '阿里云实例ID',
--   `ssh_port` int(11) NOT NULL DEFAULT 22 COMMENT 'SSH端口',
--   `username` varchar(50) NOT NULL DEFAULT 'root' COMMENT '用户名',
--   `password` varchar(255) DEFAULT NULL COMMENT '密码',
--   `private_key` text DEFAULT NULL COMMENT '私钥(预留)',
--   `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--   PRIMARY KEY (`id`),
--   UNIQUE KEY `unique_instance` (`instance_id`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='已弃用，请使用cloud_instance_config表';

-- 注意：此表初始化时为空
-- 当用户首次同步阿里云ECS实例并编辑连接配置时，系统会自动创建相应记录