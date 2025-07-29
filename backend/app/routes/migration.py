from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required
import paramiko
import pymysql
from app.utils.logger import logger
from flask_cors import cross_origin
import json
import uuid
import subprocess
import re
from datetime import datetime

migration_bp = Blueprint('migration', __name__, url_prefix='/api/migration')

@migration_bp.route('/detect-legacy-apps', methods=['GET'])
@cross_origin(supports_credentials=True)
@token_required
def detect_legacy_apps():
    """检测旧系统的应用实例"""
    try:
        # 获取所有主机
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取手动添加的主机
        cursor.execute("""
            SELECT id, hostname, ip, username, password, port
            FROM hosts
        """)
        hosts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        legacy_apps = []
        
        for host in hosts:
            try:
                # 连接主机检测容器
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                ssh.connect(
                    hostname=host['ip'],
                    port=host['port'],
                    username=host['username'],
                    password=host['password']
                )
                
                # 检测sremanage容器
                stdin, stdout, stderr = ssh.exec_command(
                    "docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' | grep sremanage"
                )
                
                output = stdout.read().decode().strip()
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        if not line.strip():
                            continue
                        
                        parts = [p.strip() for p in line.split('\t')]
                        if len(parts) >= 4:
                            container_name = parts[0]
                            image = parts[1]
                            status = parts[2]
                            ports = parts[3]
                            
                            # 解析容器名称
                            if '_' in container_name:
                                name_parts = container_name.split('_')
                                if len(name_parts) >= 3 and name_parts[0] == 'sremanage':
                                    app_type = name_parts[1]
                                    instance_id = name_parts[2] if len(name_parts) > 2 else str(uuid.uuid4())[:8]
                                    
                                    legacy_apps.append({
                                        'container_name': container_name,
                                        'app_type': app_type,
                                        'instance_id': instance_id,
                                        'image': image,
                                        'status': 'running' if 'Up' in status else 'stopped',
                                        'ports': ports,
                                        'host_id': f"manual_{host['id']}",
                                        'hostname': host['hostname'],
                                        'host_ip': host['ip']
                                    })
                
                ssh.close()
                
            except Exception as e:
                logger.warning(f"检测主机 {host['hostname']} 失败: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'data': legacy_apps
        })
        
    except Exception as e:
        logger.error(f"检测旧应用失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'检测失败: {str(e)}'
        }), 500

@migration_bp.route('/migrate-legacy-app', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def migrate_legacy_app():
    """迁移单个旧应用到新系统"""
    try:
        data = request.get_json()
        
        required_fields = ['container_name', 'app_type', 'instance_id', 'host_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': '缺少必要的字段'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查模板是否存在
        cursor.execute("SELECT id FROM app_templates WHERE id = %s", (data['app_type'],))
        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'message': f'应用模板 {data["app_type"]} 不存在'
            }), 404
        
        # 检查实例是否已存在
        cursor.execute("SELECT id FROM app_instances WHERE id = %s", (data['instance_id'],))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': '该实例已经迁移过了'
            }), 400
        
        # 获取应用部署路径
        deploy_path = _get_app_deploy_path(data, cursor)
        
        # 解析端口映射
        port_mappings = _parse_port_mappings(data.get('ports', ''))
        
        # 插入实例记录
        cursor.execute("""
            INSERT INTO app_instances (
                id, template_id, instance_name, host_id, host_type,
                config, status, deploy_path, port_mappings
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['instance_id'],
            data['app_type'],
            f"{data['app_type']}_{data['instance_id']}",
            data['host_id'],
            'manual' if data['host_id'].startswith('manual_') else 'aliyun',
            json.dumps({}),  # 空配置，用户可以后续编辑
            data.get('status', 'running'),
            deploy_path,
            json.dumps(port_mappings)
        ))
        
        # 记录迁移日志
        cursor.execute("""
            INSERT INTO app_instance_logs (instance_id, log_type, message, details)
            VALUES (%s, %s, %s, %s)
        """, (
            data['instance_id'],
            'info',
            '从旧系统迁移的应用实例',
            json.dumps({
                'original_container': data['container_name'],
                'migration_time': datetime.now().isoformat(),
                'image': data.get('image', ''),
                'migrated_by': 'system'  # 可以从token获取用户信息
            })
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'应用 {data["container_name"]} 迁移成功',
            'data': {
                'instance_id': data['instance_id'],
                'deploy_path': deploy_path
            }
        })
        
    except Exception as e:
        logger.error(f"迁移应用失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'迁移失败: {str(e)}'
        }), 500

@migration_bp.route('/batch-migrate', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def batch_migrate_legacy_apps():
    """批量迁移旧应用"""
    try:
        data = request.get_json()
        apps_to_migrate = data.get('apps', [])
        
        if not apps_to_migrate:
            return jsonify({
                'success': False,
                'message': '没有指定要迁移的应用'
            }), 400
        
        results = []
        success_count = 0
        
        for app in apps_to_migrate:
            try:
                # 调用单个迁移逻辑
                result = _migrate_single_app(app)
                results.append({
                    'container_name': app.get('container_name', ''),
                    'success': result['success'],
                    'message': result['message']
                })
                
                if result['success']:
                    success_count += 1
                    
            except Exception as e:
                results.append({
                    'container_name': app.get('container_name', ''),
                    'success': False,
                    'message': f'迁移失败: {str(e)}'
                })
        
        return jsonify({
            'success': True,
            'message': f'批量迁移完成，成功: {success_count}/{len(apps_to_migrate)}',
            'data': {
                'total': len(apps_to_migrate),
                'success': success_count,
                'failed': len(apps_to_migrate) - success_count,
                'results': results
            }
        })
        
    except Exception as e:
        logger.error(f"批量迁移失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量迁移失败: {str(e)}'
        }), 500

def _get_app_deploy_path(app_data, cursor):
    """获取应用部署路径"""
    # 尝试从容器中获取挂载信息，如果失败则使用默认路径
    default_path = f"/opt/sremanage/apps/{app_data['app_type']}_{app_data['instance_id']}"
    
    try:
        # 这里可以添加更复杂的逻辑来检测实际部署路径
        # 现在先使用默认路径
        return default_path
    except:
        return default_path

def _parse_port_mappings(ports_string):
    """解析端口映射字符串"""
    port_mappings = []
    
    if not ports_string:
        return port_mappings
    
    # 解析端口映射，格式如: 0.0.0.0:3306->3306/tcp, :::3306->3306/tcp
    port_pattern = r'(?:[\d.:]+:)?(\d+)->(\d+)/(\w+)'
    matches = re.findall(port_pattern, ports_string)
    
    for match in matches:
        host_port, container_port, protocol = match
        port_mappings.append({
            'name': f'{protocol.upper()}_Port',
            'host': int(host_port),
            'container': int(container_port),
            'protocol': protocol.lower()
        })
    
    return port_mappings

def _migrate_single_app(app_data):
    """迁移单个应用的内部逻辑"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查模板是否存在
        cursor.execute("SELECT id FROM app_templates WHERE id = %s", (app_data['app_type'],))
        if not cursor.fetchone():
            return {
                'success': False,
                'message': f'应用模板 {app_data["app_type"]} 不存在'
            }
        
        # 检查实例是否已存在
        cursor.execute("SELECT id FROM app_instances WHERE id = %s", (app_data['instance_id'],))
        if cursor.fetchone():
            return {
                'success': False,
                'message': '该实例已经迁移过了'
            }
        
        # 获取应用部署路径
        deploy_path = _get_app_deploy_path(app_data, cursor)
        
        # 解析端口映射
        port_mappings = _parse_port_mappings(app_data.get('ports', ''))
        
        # 插入实例记录
        cursor.execute("""
            INSERT INTO app_instances (
                id, template_id, instance_name, host_id, host_type,
                config, status, deploy_path, port_mappings
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            app_data['instance_id'],
            app_data['app_type'],
            f"{app_data['app_type']}_{app_data['instance_id']}",
            app_data['host_id'],
            'manual' if app_data['host_id'].startswith('manual_') else 'aliyun',
            json.dumps({}),
            app_data.get('status', 'running'),
            deploy_path,
            json.dumps(port_mappings)
        ))
        
        # 记录迁移日志
        cursor.execute("""
            INSERT INTO app_instance_logs (instance_id, log_type, message, details)
            VALUES (%s, %s, %s, %s)
        """, (
            app_data['instance_id'],
            'info',
            '从旧系统迁移的应用实例',
            json.dumps({
                'original_container': app_data['container_name'],
                'migration_time': datetime.now().isoformat(),
                'image': app_data.get('image', ''),
                'migrated_by': 'system'
            })
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': f'应用 {app_data["container_name"]} 迁移成功'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'迁移失败: {str(e)}'
        }