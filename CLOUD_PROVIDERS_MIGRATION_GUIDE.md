# 云厂商配置迁移指南

## 概述

本指南将帮助您将现有的阿里云配置迁移到新的通用云厂商配置系统。新系统支持多个云厂商，包括阿里云、AWS、腾讯云、华为云等。

## 新功能特性

- ✅ 支持多个云厂商（阿里云、AWS、腾讯云、华为云、Google Cloud、Azure）
- ✅ 统一的配置管理界面
- ✅ 动态表单生成（根据云厂商类型显示不同字段）
- ✅ 配置测试功能
- ✅ 向后兼容现有阿里云配置
- ✅ 实例配置自动迁移

## 数据库变更

### 新增表

1. **cloud_providers** - 云厂商配置主表
2. **cloud_instance_config** - 云实例连接配置表
3. **cloud_provider_schemas** - 云厂商配置字段定义表

### 保留表（向后兼容）

- `aliyun_settings` - 已标记为弃用，但保留兼容性
- `aliyun_instance_config` - 已标记为弃用，但保留兼容性

## 迁移步骤

### 1. 数据库迁移

**选项A：自动迁移（推荐）**

```bash
cd backend
python scripts/migrate_to_cloud_providers.py
```

**选项B：手动迁移**

```bash
cd backend
mysql -u root -p < sql/8.cloud_providers.sql
mysql -u root -p < sql/9.cloud_provider_schemas.sql
```

### 2. 更新代码部署

如果是重新部署，新的SQL文件已经更新：

- `sql/3.settings.sql` - 已更新为云厂商配置表
- `sql/6.aliyun_instance_config.sql` - 已更新为云实例配置表

### 3. 验证迁移

运行测试脚本验证功能：

```bash
cd backend
python test_cloud_providers.py
```

### 4. 前端更新

- 菜单项："阿里云账号" → "云厂商配置"
- 路由：`/settings/aliyun` → `/settings/cloud-providers`
- 旧路由仍然可用，但会显示弃用提示

## API变更

### 新增API

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/cloud-providers` | GET | 获取所有云厂商配置 |
| `/api/cloud-providers` | POST | 创建云厂商配置 |
| `/api/cloud-providers/{id}` | GET | 获取单个配置 |
| `/api/cloud-providers/{id}` | PUT | 更新配置 |
| `/api/cloud-providers/{id}` | DELETE | 删除配置 |
| `/api/cloud-providers/{id}/test` | POST | 测试连接 |
| `/api/cloud-providers/schemas` | GET | 获取配置字段定义 |
| `/api/cloud-providers/supported` | GET | 获取支持的云厂商 |

### 兼容性API

| 接口 | 状态 | 说明 |
|------|------|------|
| `/api/settings/aliyun` | 保留 | 向后兼容，自动映射到新系统 |

## 配置示例

### 阿里云配置

```json
{
  "name": "生产环境阿里云",
  "provider": "aliyun",
  "config": {
    "access_key_id": "your_access_key_id",
    "access_key_secret": "your_access_key_secret"
  },
  "region": "cn-hangzhou",
  "enabled": true
}
```

### AWS配置

```json
{
  "name": "开发环境AWS",
  "provider": "aws",
  "config": {
    "access_key_id": "your_aws_access_key_id",
    "secret_access_key": "your_aws_secret_access_key"
  },
  "region": "us-east-1",
  "enabled": true
}
```

### 腾讯云配置

```json
{
  "name": "测试环境腾讯云",
  "provider": "tencent",
  "config": {
    "secret_id": "your_secret_id",
    "secret_key": "your_secret_key"
  },
  "region": "ap-beijing",
  "enabled": true
}
```

## 故障排除

### 1. 迁移失败

如果自动迁移失败，请检查：

- 数据库连接是否正常
- 原有表是否存在数据
- 数据库用户是否有足够权限

### 2. 前端显示异常

如果前端界面显示异常：

- 清除浏览器缓存
- 检查后端API是否正常
- 查看浏览器控制台错误信息

### 3. API兼容性问题

如果现有功能出现问题：

- 检查新的云厂商配置是否已创建
- 确认配置状态为"启用"
- 查看后端日志文件

### 4. 实例配置丢失

如果实例SSH配置丢失：

- 检查 `cloud_instance_config` 表中的数据
- 运行迁移脚本重新迁移实例配置
- 手动重新配置SSH连接信息

## 回滚方案

如果需要回滚到旧系统：

1. 恢复前端代码：
   ```bash
   git checkout HEAD~1 frontend/src/views/settings/
   git checkout HEAD~1 frontend/src/router/index.js
   git checkout HEAD~1 frontend/src/components/Layout/MainLayout.vue
   ```

2. 恢复后端代码：
   ```bash
   git checkout HEAD~1 backend/app/routes/cloud_providers.py
   git checkout HEAD~1 backend/app/utils/cloud_providers.py
   git checkout HEAD~1 backend/app/__init__.py
   ```

3. 恢复数据库（如果需要）：
   ```sql
   -- 从备份表恢复数据
   INSERT INTO aliyun_settings SELECT * FROM aliyun_settings_backup;
   INSERT INTO aliyun_instance_config SELECT * FROM aliyun_instance_config_backup;
   ```

## 联系支持

如果在迁移过程中遇到问题，请：

1. 检查日志文件 `logs/app.log`
2. 运行测试脚本获取详细错误信息
3. 记录错误信息和复现步骤

## 版本信息

- **迁移版本**: v2.0.0
- **兼容性**: 向后兼容 v1.x
- **建议**: 建议在测试环境先行验证