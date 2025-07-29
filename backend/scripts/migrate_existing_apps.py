#!/usr/bin/env python3
"""
迁移脚本：将现有的Docker应用实例迁移到新的应用商店系统
"""

import json
import subprocess
import re
import uuid
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_db_connection
import pymysql

def run_command(cmd):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def detect_existing_apps():
    """检测现有的sremanage容器"""
    print("🔍 检测现有的sremanage应用容器...")
    
    success, stdout, stderr = run_command("docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' | grep sremanage")
    
    if not success:
        print("❌ 未找到现有的sremanage容器")
        return []
    
    apps = []
    lines = stdout.strip().split('\n')
    
    for line in lines:
        if not line.strip():
            continue
            
        parts = line.split('\t')
        if len(parts) >= 4:
            container_name = parts[0].strip()
            image = parts[1].strip()
            status = parts[2].strip()
            ports = parts[3].strip()
            
            # 解析容器名称以提取信息
            if '_' in container_name:
                name_parts = container_name.split('_')
                if len(name_parts) >= 3 and name_parts[0] == 'sremanage':
                    app_type = name_parts[1]
                    instance_id = name_parts[2] if len(name_parts) > 2 else str(uuid.uuid4())[:8]
                    
                    apps.append({
                        'container_name': container_name,
                        'app_type': app_type,
                        'instance_id': instance_id,
                        'image': image,
                        'status': 'running' if 'Up' in status else 'stopped',
                        'ports': ports
                    })
    
    return apps

def get_app_directory(container_name):
    """获取应用的部署目录"""
    # 尝试通过docker inspect获取挂载信息
    success, stdout, stderr = run_command(f"docker inspect {container_name} --format '{{{{json .Mounts}}}}'")
    
    if success:
        try:
            mounts = json.loads(stdout.strip())
            for mount in mounts:
                if mount['Type'] == 'bind' and '/opt/sremanage/apps/' in mount['Source']:
                    return mount['Source']
        except:
            pass
    
    # 如果无法获取，使用默认路径
    return f"/opt/sremanage/apps/{container_name}"

def migrate_app_to_database(app, deploy_path):
    """将应用实例信息迁移到数据库"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 生成新的实例ID（如果需要）
        new_instance_id = app['instance_id']
        template_id = app['app_type']
        
        # 检查模板是否存在
        cursor.execute("SELECT id FROM app_templates WHERE id = %s", (template_id,))
        if not cursor.fetchone():
            print(f"⚠️  模板 {template_id} 不存在，跳过迁移")
            return False
        
        # 检查实例是否已存在
        cursor.execute("SELECT id FROM app_instances WHERE id = %s", (new_instance_id,))
        if cursor.fetchone():
            print(f"⚠️  实例 {new_instance_id} 已存在，跳过")
            return True
        
        # 解析端口映射
        port_mappings = []
        if app['ports']:
            # 简单解析端口映射，格式如: 0.0.0.0:3306->3306/tcp
            port_pattern = r'(?:[\d.]+:)?(\d+)->(\d+)/(\w+)'
            matches = re.findall(port_pattern, app['ports'])
            for match in matches:
                host_port, container_port, protocol = match
                port_mappings.append({
                    'host': int(host_port),
                    'container': int(container_port),
                    'protocol': protocol
                })
        
        # 插入实例记录
        cursor.execute("""
            INSERT INTO app_instances (
                id, template_id, instance_name, host_id, host_type,
                config, status, deploy_path, port_mappings
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            new_instance_id,
            template_id,
            f"{template_id}_{new_instance_id}",
            "manual_1",  # 默认主机，可能需要调整
            "manual",
            json.dumps({}),  # 空配置，可以后续编辑
            app['status'],
            deploy_path,
            json.dumps(port_mappings)
        ))
        
        # 记录迁移日志
        cursor.execute("""
            INSERT INTO app_instance_logs (instance_id, log_type, message, details)
            VALUES (%s, %s, %s, %s)
        """, (
            new_instance_id,
            'info',
            '从旧系统迁移的应用实例',
            json.dumps({
                'original_container': app['container_name'],
                'migration_time': datetime.now().isoformat(),
                'image': app['image']
            })
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始迁移现有应用实例到新的应用商店系统")
    print("=" * 50)
    
    # 检测现有应用
    existing_apps = detect_existing_apps()
    
    if not existing_apps:
        print("✅ 未发现需要迁移的应用实例")
        return
    
    print(f"📋 发现 {len(existing_apps)} 个现有应用实例:")
    for app in existing_apps:
        print(f"  • {app['container_name']} ({app['app_type']}) - {app['status']}")
    
    print("\n🔄 开始迁移...")
    
    migrated_count = 0
    
    for app in existing_apps:
        print(f"\n📦 迁移应用: {app['container_name']}")
        
        # 获取部署目录
        deploy_path = get_app_directory(app['container_name'])
        print(f"  📂 部署目录: {deploy_path}")
        
        # 迁移到数据库
        if migrate_app_to_database(app, deploy_path):
            print(f"  ✅ 迁移成功")
            migrated_count += 1
        else:
            print(f"  ❌ 迁移失败")
    
    print(f"\n🎉 迁移完成! 成功迁移 {migrated_count}/{len(existing_apps)} 个应用实例")
    
    if migrated_count > 0:
        print("\n📌 迁移后操作建议:")
        print("1. 在应用商店的'已安装'页面查看迁移的应用")
        print("2. 检查应用状态和配置是否正确")
        print("3. 如需修改配置，可以在'应用管理'中复制模板后重新部署")
        print("4. 旧的容器仍在运行，你可以选择保留或清理")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 迁移被用户中断")
    except Exception as e:
        print(f"\n❌ 迁移过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()