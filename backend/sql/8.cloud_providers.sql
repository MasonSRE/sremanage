-- 云厂商配置表
-- 替换原有的 aliyun_settings 表，支持多种云厂商配置
CREATE TABLE IF NOT EXISTS `cloud_providers` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL COMMENT '配置名称，如"生产环境阿里云"',
    `provider` varchar(50) NOT NULL COMMENT '云厂商类型: aliyun, aws, tencent, huawei, google, azure',
    `config` JSON NOT NULL COMMENT '云厂商配置信息',
    `region` varchar(50) DEFAULT NULL COMMENT '默认区域',
    `enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_provider` (`provider`),
    KEY `idx_enabled` (`enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云厂商配置表';

-- 数据迁移：将现有的阿里云配置迁移到新表
INSERT INTO `cloud_providers` (`name`, `provider`, `config`, `region`, `enabled`)
SELECT 
    '默认阿里云配置' as name,
    'aliyun' as provider,
    JSON_OBJECT(
        'access_key_id', access_key_id,
        'access_key_secret', access_key_secret
    ) as config,
    region,
    1 as enabled
FROM `aliyun_settings`
WHERE id = 1;

-- 更新实例配置表，支持多云厂商
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

-- 迁移现有的阿里云实例配置
INSERT INTO `cloud_instance_config` (`provider_id`, `instance_id`, `ssh_port`, `username`, `password`, `private_key`)
SELECT 
    (SELECT id FROM cloud_providers WHERE provider = 'aliyun' LIMIT 1) as provider_id,
    instance_id,
    ssh_port,
    username,
    password,
    private_key
FROM `aliyun_instance_config`;

-- 云厂商支持的配置字段定义表（预留，用于动态表单生成）
CREATE TABLE IF NOT EXISTS `cloud_provider_schemas` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `provider` varchar(50) NOT NULL COMMENT '云厂商类型',
    `field_name` varchar(100) NOT NULL COMMENT '字段名称',
    `field_type` varchar(50) NOT NULL COMMENT '字段类型: text, password, select, number',
    `field_label` varchar(200) NOT NULL COMMENT '字段显示名称',
    `is_required` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否必填',
    `default_value` varchar(500) DEFAULT NULL COMMENT '默认值',
    `options` JSON DEFAULT NULL COMMENT '选项列表（用于select类型）',
    `placeholder` varchar(200) DEFAULT NULL COMMENT '占位符',
    `help_text` varchar(500) DEFAULT NULL COMMENT '帮助文本',
    `sort_order` int(11) NOT NULL DEFAULT 0 COMMENT '排序顺序',
    PRIMARY KEY (`id`),
    KEY `idx_provider` (`provider`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云厂商配置字段定义表';

-- 插入常见云厂商的配置字段定义
INSERT INTO `cloud_provider_schemas` (`provider`, `field_name`, `field_type`, `field_label`, `is_required`, `placeholder`, `help_text`, `sort_order`) VALUES
-- 阿里云配置字段
('aliyun', 'access_key_id', 'text', 'Access Key ID', 1, '请输入阿里云Access Key ID', '在阿里云控制台的访问控制RAM中创建', 1),
('aliyun', 'access_key_secret', 'password', 'Access Key Secret', 1, '请输入阿里云Access Key Secret', '对应Access Key ID的密钥', 2),
('aliyun', 'default_region', 'select', '默认区域', 0, NULL, '用于API调用的默认区域', 3),

-- AWS配置字段
('aws', 'access_key_id', 'text', 'Access Key ID', 1, '请输入AWS Access Key ID', '在AWS IAM中创建访问密钥', 1),
('aws', 'secret_access_key', 'password', 'Secret Access Key', 1, '请输入AWS Secret Access Key', '对应Access Key ID的密钥', 2),
('aws', 'default_region', 'select', '默认区域', 0, 'us-east-1', '用于API调用的默认区域', 3),

-- 腾讯云配置字段
('tencent', 'secret_id', 'text', 'Secret ID', 1, '请输入腾讯云Secret ID', '在腾讯云控制台的访问管理中创建', 1),
('tencent', 'secret_key', 'password', 'Secret Key', 1, '请输入腾讯云Secret Key', '对应Secret ID的密钥', 2),
('tencent', 'default_region', 'select', '默认区域', 0, 'ap-beijing', '用于API调用的默认区域', 3),

-- 华为云配置字段
('huawei', 'access_key', 'text', 'Access Key', 1, '请输入华为云Access Key', '在华为云控制台的访问密钥中创建', 1),
('huawei', 'secret_key', 'password', 'Secret Key', 1, '请输入华为云Secret Key', '对应Access Key的密钥', 2),
('huawei', 'default_region', 'select', '默认区域', 0, 'cn-north-1', '用于API调用的默认区域', 3);

-- 插入阿里云区域选项
UPDATE `cloud_provider_schemas` SET `options` = JSON_ARRAY(
    JSON_OBJECT('value', 'cn-hangzhou', 'label', '华东1(杭州)'),
    JSON_OBJECT('value', 'cn-shanghai', 'label', '华东2(上海)'),
    JSON_OBJECT('value', 'cn-beijing', 'label', '华北2(北京)'),
    JSON_OBJECT('value', 'cn-shenzhen', 'label', '华南1(深圳)'),
    JSON_OBJECT('value', 'cn-chengdu', 'label', '西南1(成都)'),
    JSON_OBJECT('value', 'cn-hongkong', 'label', '中国香港'),
    JSON_OBJECT('value', 'ap-southeast-1', 'label', '新加坡'),
    JSON_OBJECT('value', 'us-west-1', 'label', '美国(硅谷)'),
    JSON_OBJECT('value', 'us-east-1', 'label', '美国(弗吉尼亚)')
) WHERE `provider` = 'aliyun' AND `field_name` = 'default_region';

-- 插入AWS区域选项
UPDATE `cloud_provider_schemas` SET `options` = JSON_ARRAY(
    JSON_OBJECT('value', 'us-east-1', 'label', 'US East (N. Virginia)'),
    JSON_OBJECT('value', 'us-east-2', 'label', 'US East (Ohio)'),
    JSON_OBJECT('value', 'us-west-1', 'label', 'US West (N. California)'),
    JSON_OBJECT('value', 'us-west-2', 'label', 'US West (Oregon)'),
    JSON_OBJECT('value', 'ap-east-1', 'label', 'Asia Pacific (Hong Kong)'),
    JSON_OBJECT('value', 'ap-south-1', 'label', 'Asia Pacific (Mumbai)'),
    JSON_OBJECT('value', 'ap-northeast-1', 'label', 'Asia Pacific (Tokyo)'),
    JSON_OBJECT('value', 'ap-northeast-2', 'label', 'Asia Pacific (Seoul)'),
    JSON_OBJECT('value', 'ap-southeast-1', 'label', 'Asia Pacific (Singapore)')
) WHERE `provider` = 'aws' AND `field_name` = 'default_region';

-- 插入腾讯云区域选项
UPDATE `cloud_provider_schemas` SET `options` = JSON_ARRAY(
    JSON_OBJECT('value', 'ap-beijing', 'label', '北京'),
    JSON_OBJECT('value', 'ap-shanghai', 'label', '上海'),
    JSON_OBJECT('value', 'ap-guangzhou', 'label', '广州'),
    JSON_OBJECT('value', 'ap-chengdu', 'label', '成都'),
    JSON_OBJECT('value', 'ap-hongkong', 'label', '中国香港'),
    JSON_OBJECT('value', 'ap-singapore', 'label', '新加坡'),
    JSON_OBJECT('value', 'ap-tokyo', 'label', '东京'),
    JSON_OBJECT('value', 'na-toronto', 'label', '多伦多'),
    JSON_OBJECT('value', 'na-siliconvalley', 'label', '硅谷')
) WHERE `provider` = 'tencent' AND `field_name` = 'default_region';

-- 插入华为云区域选项
UPDATE `cloud_provider_schemas` SET `options` = JSON_ARRAY(
    JSON_OBJECT('value', 'cn-north-1', 'label', '华北-北京一'),
    JSON_OBJECT('value', 'cn-north-4', 'label', '华北-北京四'),
    JSON_OBJECT('value', 'cn-east-2', 'label', '华东-上海二'),
    JSON_OBJECT('value', 'cn-east-3', 'label', '华东-上海一'),
    JSON_OBJECT('value', 'cn-south-1', 'label', '华南-广州'),
    JSON_OBJECT('value', 'cn-southwest-2', 'label', '西南-贵阳一'),
    JSON_OBJECT('value', 'ap-southeast-1', 'label', '亚太-香港'),
    JSON_OBJECT('value', 'ap-southeast-2', 'label', '亚太-曼谷'),
    JSON_OBJECT('value', 'ap-southeast-3', 'label', '亚太-新加坡')
) WHERE `provider` = 'huawei' AND `field_name` = 'default_region';