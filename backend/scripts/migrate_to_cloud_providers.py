#!/usr/bin/env python3
"""
数据库迁移脚本：将阿里云设置迁移到云厂商配置
"""

import sys
import os
import pymysql
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_db_connection

def backup_current_tables(db):
    """备份现有表数据"""
    backup_queries = [
        "CREATE TABLE IF NOT EXISTS aliyun_settings_backup AS SELECT * FROM aliyun_settings",
        "CREATE TABLE IF NOT EXISTS aliyun_instance_config_backup AS SELECT * FROM aliyun_instance_config"
    ]
    
    with db.cursor() as cursor:
        for query in backup_queries:
            try:
                cursor.execute(query)
                print(f"✓ 备份表: {query.split('AS')[0].split('_backup')[0]}")
            except Exception as e:
                print(f"✗ 备份失败: {e}")
                return False
    
    db.commit()
    return True

def check_table_exists(db, table_name):
    """检查表是否存在"""
    with db.cursor() as cursor:
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = '{table_name}'
        """)
        result = cursor.fetchone()
        return result['count'] > 0

def create_new_tables(db):
    """创建新的表结构"""
    
    # 读取SQL文件
    sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', '8.cloud_providers.sql')
    
    if not os.path.exists(sql_file):
        print(f"✗ SQL文件不存在: {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割SQL语句
    sql_statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        line = line.strip()
        if line.startswith('--') or not line:
            continue
        
        current_statement += line + '\n'
        
        if line.endswith(';'):
            sql_statements.append(current_statement.strip())
            current_statement = ""
    
    # 执行SQL语句
    with db.cursor() as cursor:
        for i, statement in enumerate(sql_statements):
            try:
                # 跳过数据迁移语句，我们稍后手动处理
                if 'INSERT INTO' in statement and 'cloud_providers' in statement:
                    continue
                if 'INSERT INTO' in statement and 'cloud_instance_config' in statement:
                    continue
                
                cursor.execute(statement)
                print(f"✓ 执行SQL语句 {i+1}/{len(sql_statements)}")
            except Exception as e:
                print(f"✗ SQL执行失败: {e}")
                print(f"语句: {statement[:100]}...")
                return False
    
    db.commit()
    return True

def migrate_aliyun_settings(db):
    """迁移阿里云设置"""
    
    # 检查是否有现有的阿里云设置
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM aliyun_settings WHERE id = 1")
        aliyun_setting = cursor.fetchone()
        
        if not aliyun_setting:
            print("ℹ 没有找到现有的阿里云设置，跳过迁移")
            return True
        
        # 检查是否已经迁移过
        cursor.execute("SELECT COUNT(*) as count FROM cloud_providers WHERE provider = 'aliyun'")
        existing_count = cursor.fetchone()['count']
        
        if existing_count > 0:
            print("ℹ 阿里云配置已经存在，跳过迁移")
            return True
        
        # 迁移阿里云设置
        config_data = {
            'access_key_id': aliyun_setting['access_key_id'],
            'access_key_secret': aliyun_setting['access_key_secret']
        }
        
        cursor.execute("""
            INSERT INTO cloud_providers (name, provider, config, region, enabled)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            '默认阿里云配置',
            'aliyun',
            json.dumps(config_data),
            aliyun_setting.get('region', 'cn-hangzhou'),
            1
        ))
        
        provider_id = cursor.lastrowid
        print(f"✓ 迁移阿里云设置，新ID: {provider_id}")
        
        # 迁移实例配置
        cursor.execute("SELECT * FROM aliyun_instance_config")
        instance_configs = cursor.fetchall()
        
        for config in instance_configs:
            cursor.execute("""
                INSERT INTO cloud_instance_config (provider_id, instance_id, ssh_port, username, password, private_key)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                provider_id,
                config['instance_id'],
                config['ssh_port'],
                config['username'],
                config['password'],
                config['private_key']
            ))
        
        print(f"✓ 迁移 {len(instance_configs)} 个实例配置")
    
    db.commit()
    return True

def verify_migration(db):
    """验证迁移结果"""
    
    with db.cursor() as cursor:
        # 检查云厂商配置表
        cursor.execute("SELECT COUNT(*) as count FROM cloud_providers")
        provider_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM cloud_instance_config")
        instance_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM cloud_provider_schemas")
        schema_count = cursor.fetchone()['count']
        
        print(f"✓ 验证结果:")
        print(f"  - 云厂商配置数量: {provider_count}")
        print(f"  - 实例配置数量: {instance_count}")
        print(f"  - 配置模式数量: {schema_count}")
        
        # 检查阿里云配置是否正确迁移
        cursor.execute("SELECT * FROM cloud_providers WHERE provider = 'aliyun'")
        aliyun_providers = cursor.fetchall()
        
        for provider in aliyun_providers:
            config = json.loads(provider['config'])
            print(f"  - 阿里云配置 '{provider['name']}': {list(config.keys())}")
        
        return provider_count > 0

def main():
    """主函数"""
    
    print("开始数据库迁移...")
    print("=" * 50)
    
    try:
        # 连接数据库
        db = get_db_connection()
        print("✓ 数据库连接成功")
        
        # 备份现有表
        print("\n1. 备份现有表...")
        if not backup_current_tables(db):
            print("✗ 备份失败，停止迁移")
            return False
        
        # 创建新表
        print("\n2. 创建新表结构...")
        if not create_new_tables(db):
            print("✗ 创建新表失败，停止迁移")
            return False
        
        # 迁移数据
        print("\n3. 迁移现有数据...")
        if not migrate_aliyun_settings(db):
            print("✗ 数据迁移失败，停止迁移")
            return False
        
        # 验证迁移
        print("\n4. 验证迁移结果...")
        if not verify_migration(db):
            print("✗ 迁移验证失败")
            return False
        
        print("\n" + "=" * 50)
        print("✓ 数据库迁移完成！")
        print("\n注意事项：")
        print("- 原有表已备份为 *_backup 表")
        print("- 新的云厂商配置表已创建")
        print("- 阿里云配置已迁移到新表")
        print("- 请测试新功能后再删除备份表")
        
        return True
        
    except Exception as e:
        print(f"✗ 迁移过程中发生错误: {e}")
        return False
    
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)