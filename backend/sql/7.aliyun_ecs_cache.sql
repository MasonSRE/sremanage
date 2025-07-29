-- 阿里云ECS实例缓存表
-- 用于持久化存储同步的ECS实例信息，避免重复手动同步
CREATE TABLE IF NOT EXISTS `aliyun_ecs_cache` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `instance_id` varchar(50) NOT NULL COMMENT '阿里云实例ID',
  `instance_name` varchar(100) NOT NULL COMMENT '实例名称',
  `hostname` varchar(100) DEFAULT NULL COMMENT '主机名',
  `status` varchar(20) NOT NULL COMMENT '实例状态',
  `instance_type` varchar(50) DEFAULT NULL COMMENT '实例规格',
  `image_id` varchar(50) DEFAULT NULL COMMENT '镜像ID',
  `public_ip` varchar(15) DEFAULT NULL COMMENT '公网IP',
  `private_ip` varchar(15) DEFAULT NULL COMMENT '私网IP',
  `region` varchar(20) NOT NULL COMMENT '所在区域',
  `zone` varchar(20) DEFAULT NULL COMMENT '可用区',
  `creation_time` varchar(30) DEFAULT NULL COMMENT '创建时间',
  `os_type` varchar(20) DEFAULT NULL COMMENT '操作系统类型',
  `cpu` int(11) DEFAULT NULL COMMENT 'CPU核数',
  `memory` int(11) DEFAULT NULL COMMENT '内存大小(MB)',
  `provider` varchar(20) NOT NULL DEFAULT 'aliyun' COMMENT '云服务商',
  `last_sync_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后同步时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_instance` (`instance_id`),
  KEY `idx_region` (`region`),
  KEY `idx_status` (`status`),
  KEY `idx_last_sync` (`last_sync_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='阿里云ECS实例缓存表';

-- 创建同步状态表
CREATE TABLE IF NOT EXISTS `aliyun_sync_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sync_type` varchar(20) NOT NULL COMMENT '同步类型(ecs,cdn,domain)',
  `last_sync_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后同步时间',
  `sync_status` enum('running','completed','failed') NOT NULL DEFAULT 'completed' COMMENT '同步状态',
  `total_count` int(11) DEFAULT 0 COMMENT '总数量',
  `error_message` text DEFAULT NULL COMMENT '错误信息',
  `sync_duration` int(11) DEFAULT NULL COMMENT '同步耗时(秒)',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_sync_type` (`sync_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='阿里云同步状态表';

-- 插入初始同步状态记录
INSERT IGNORE INTO `aliyun_sync_status` (`sync_type`, `sync_status`, `total_count`) VALUES
('ecs', 'completed', 0),
('cdn', 'completed', 0),
('domain', 'completed', 0);