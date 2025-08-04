#!/usr/bin/env python3
"""
Phase 5 初始化脚本
集成到现有的初始化流程中，自动完成所有必要的设置
"""

import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

def init_phase5():
    """初始化Phase 5组件"""
    print("🚀 开始初始化Phase 5组件...")
    
    # 1. 创建必要的目录
    print("📁 创建目录结构...")
    directories = [
        'logs/phase5',
        'cache/performance', 
        'cache/security',
        'cache/encryption'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ {directory}")
    
    # 2. 初始化数据库表
    print("🗄️ 初始化数据库表...")
    try:
        from app.utils.db_context import database_connection
        
        # 读取SQL文件
        sql_file = Path(__file__).parent.parent / 'sql' / '10.phase5_tables.sql'
        if sql_file.exists():
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 执行SQL语句
            with database_connection() as db:
                with db.cursor() as cursor:
                    # 分割SQL语句并逐个执行
                    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                    for statement in statements:
                        if statement and not statement.startswith('--'):
                            try:
                                cursor.execute(statement)
                            except Exception as e:
                                if 'already exists' not in str(e).lower():
                                    print(f"  ⚠️ SQL执行警告: {e}")
                
                db.commit()
                print("  ✓ 数据库表初始化完成")
        else:
            print("  ⚠️ SQL文件不存在，跳过数据库初始化")
            
    except Exception as e:
        print(f"  ⚠️ 数据库初始化失败: {e}")
    
    # 3. 生成加密密钥
    print("🔐 配置加密密钥...")
    try:
        from cryptography.fernet import Fernet
        
        env_file = Path(__file__).parent.parent / '.env'
        env_content = ""
        
        # 读取现有.env文件
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # 检查是否已有加密密钥
        if 'ENCRYPTION_MASTER_KEY' not in env_content:
            key = Fernet.generate_key().decode()
            env_content += f"\n# Phase 5 加密配置\nENCRYPTION_MASTER_KEY={key}\n"
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print("  ✓ 生成新的加密密钥")
        else:
            print("  ✓ 加密密钥已存在")
            
    except Exception as e:
        print(f"  ⚠️ 加密密钥配置失败: {e}")
    
    # 4. 初始化默认权限
    print("👥 初始化用户权限...")
    try:
        from app.utils.permission_control import permission_manager
        
        # 为admin用户分配超级管理员权限
        admin_users = ['admin', '1']  # 常见的管理员用户ID
        
        for user_id in admin_users:
            try:
                permission_manager.assign_role_to_user(user_id, 'super_admin')
                print(f"  ✓ 为用户 {user_id} 分配超级管理员权限")
            except:
                pass  # 用户可能不存在，忽略错误
                
    except Exception as e:
        print(f"  ⚠️ 权限初始化失败: {e}")
    
    # 5. 验证组件状态
    print("🔍 验证Phase 5组件...")
    try:
        # 验证核心模块是否可以正常导入
        modules = [
            'app.utils.performance',
            'app.utils.security_enhancement', 
            'app.utils.encryption',
            'app.utils.permission_control',
            'app.utils.error_handling',
            'app.utils.retry_fallback'
        ]
        
        for module in modules:
            try:
                __import__(module)
                print(f"  ✓ {module}")
            except Exception as e:
                print(f"  ❌ {module}: {e}")
                
    except Exception as e:
        print(f"  ⚠️ 组件验证失败: {e}")
    
    print("✅ Phase 5初始化完成!")
    return True

if __name__ == "__main__":
    success = init_phase5()
    sys.exit(0 if success else 1)