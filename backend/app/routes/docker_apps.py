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
import os

docker_apps_bp = Blueprint('docker_apps', __name__, url_prefix='/api')

# 应用商店数据现在从数据库读取

@docker_apps_bp.route('/docker-apps', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_docker_apps():
    """获取Docker应用商店列表 - 从数据库读取"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        category = request.args.get('category', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 构建查询条件
        conditions = ["status = 'active'"]
        params = []
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        # 查询模板
        cursor.execute(f"""
            SELECT id, name, description, category, version, tags, 
                   ports, volumes, env_vars
            FROM app_templates 
            WHERE {where_clause}
            ORDER BY category, name
        """, params)
        
        templates = cursor.fetchall()
        
        # 查询分类
        cursor.execute("SELECT DISTINCT category FROM app_templates WHERE status = 'active'")
        categories = [row['category'] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        # 处理JSON字段，转换为旧格式兼容
        apps = []
        for template in templates:
            app = {
                'id': template['id'],
                'name': template['name'],
                'description': template['description'],
                'category': template['category'],
                'version': template['version'],
                'tags': json.loads(template['tags']) if template['tags'] else [],
                'ports': json.loads(template['ports']) if template['ports'] else [],
                'volumes': json.loads(template['volumes']) if template['volumes'] else [],
                'env_vars': json.loads(template['env_vars']) if template['env_vars'] else {}
            }
            apps.append(app)
        
        return jsonify({
            'success': True,
            'data': {
                'apps': apps,
                'categories': categories,
                'total': len(apps)
            }
        })
        
    except Exception as e:
        logger.error(f"获取Docker应用列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取应用列表失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps-test', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_docker_apps_test():
    """获取Docker应用商店列表 - 测试接口，不需要认证，从数据库读取"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        category = request.args.get('category', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 构建查询条件
        conditions = ["status = 'active'"]
        params = []
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        # 查询模板
        cursor.execute(f"""
            SELECT id, name, description, category, version, tags, 
                   ports, volumes, env_vars
            FROM app_templates 
            WHERE {where_clause}
            ORDER BY category, name
        """, params)
        
        templates = cursor.fetchall()
        
        # 查询分类
        cursor.execute("SELECT DISTINCT category FROM app_templates WHERE status = 'active'")
        categories = [row['category'] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        # 处理JSON字段，转换为旧格式兼容
        apps = []
        for template in templates:
            app = {
                'id': template['id'],
                'name': template['name'],
                'description': template['description'],
                'category': template['category'],
                'version': template['version'],
                'tags': json.loads(template['tags']) if template['tags'] else [],
                'ports': json.loads(template['ports']) if template['ports'] else [],
                'volumes': json.loads(template['volumes']) if template['volumes'] else [],
                'env_vars': json.loads(template['env_vars']) if template['env_vars'] else {}
            }
            apps.append(app)
        
        return jsonify({
            'success': True,
            'data': {
                'apps': apps,
                'categories': categories,
                'total': len(apps)
            },
            'debug': {
                'message': '测试接口，无需认证',
                'app_count': len(apps),
                'category_count': len(categories)
            }
        })
        
    except Exception as e:
        logger.error(f"获取Docker应用列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取应用列表失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps/<app_id>/install-test', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def install_docker_app_test(app_id):
    """安装Docker应用 - 测试接口，不需要认证"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        host_id = data.get('host_id')
        config = data.get('config', {})
        
        if not host_id:
            return jsonify({
                'success': False,
                'message': '请选择目标主机'
            }), 400
        
        # 从数据库获取应用模板信息
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT id, name, description, category, version, tags, 
                   ports, volumes, env_vars, compose_template
            FROM app_templates 
            WHERE id = %s AND status = 'active'
        """, (app_id,))
        
        template = cursor.fetchone()
        if not template:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': '应用不存在'
            }), 404
        
        # 转换为旧格式兼容
        app_info = {
            'id': template['id'],
            'name': template['name'],
            'description': template['description'],
            'category': template['category'],
            'version': template['version'],
            'tags': json.loads(template['tags']) if template['tags'] else [],
            'ports': json.loads(template['ports']) if template['ports'] else [],
            'volumes': json.loads(template['volumes']) if template['volumes'] else [],
            'env_vars': json.loads(template['env_vars']) if template['env_vars'] else {}
        }
        
        # 解析主机ID
        if host_id.startswith('manual_'):
            host_type = 'manual'
            original_id = int(host_id.replace('manual_', ''))
        elif host_id.startswith('aliyun_'):
            host_type = 'aliyun'
            original_id = host_id.replace('aliyun_', '')
        else:
            return jsonify({
                'success': False,
                'message': '无效的主机ID'
            }), 400
        
        # 获取主机连接信息
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if host_type == 'manual':
            cursor.execute("""
                SELECT hostname, ip, username, password, port, protocol
                FROM hosts WHERE id = %s
            """, (original_id,))
        else:
            cursor.execute("""
                SELECT instance_name as hostname, 
                       COALESCE(public_ip, private_ip) as ip,
                       'root' as username,
                       '' as password,
                       22 as port,
                       'SSH' as protocol
                FROM aliyun_ecs_cache WHERE instance_id = %s
            """, (original_id,))
        
        host_info = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not host_info:
            return jsonify({
                'success': False,
                'message': '主机不存在'
            }), 404
        
        # 生成实例ID
        instance_id = str(uuid.uuid4())[:8]
        
        # 对于测试，我们先返回成功信息，不实际执行安装
        return jsonify({
            'success': True,
            'message': f'{app_info["name"]} 测试安装成功',
            'data': {
                'instance_id': instance_id,
                'app_id': app_id,
                'host': host_info['hostname'],
                'host_ip': host_info['ip'],
                'config': config,
                'test_mode': True,
                'docker_compose': template['compose_template'] or '',  # 使用数据库中的模板
                'env_file': _generate_env_file(app_info, config)
            }
        })
        
    except Exception as e:
        logger.error(f"测试安装Docker应用失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'测试安装失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps/<app_id>/install', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def install_docker_app(app_id):
    """安装Docker应用"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        host_id = data.get('host_id')
        config = data.get('config', {})
        
        if not host_id:
            return jsonify({
                'success': False,
                'message': '请选择目标主机'
            }), 400
        
        # 从数据库获取应用模板信息
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT id, name, description, category, version, tags, 
                   ports, volumes, env_vars, compose_template
            FROM app_templates 
            WHERE id = %s AND status = 'active'
        """, (app_id,))
        
        template = cursor.fetchone()
        if not template:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': '应用不存在'
            }), 404
        
        # 转换为旧格式兼容
        app_info = {
            'id': template['id'],
            'name': template['name'],
            'description': template['description'],
            'category': template['category'],
            'version': template['version'],
            'tags': json.loads(template['tags']) if template['tags'] else [],
            'ports': json.loads(template['ports']) if template['ports'] else [],
            'volumes': json.loads(template['volumes']) if template['volumes'] else [],
            'env_vars': json.loads(template['env_vars']) if template['env_vars'] else {}
        }
        
        # 解析主机ID
        if host_id.startswith('manual_'):
            host_type = 'manual'
            original_id = int(host_id.replace('manual_', ''))
        elif host_id.startswith('aliyun_'):
            host_type = 'aliyun'
            original_id = host_id.replace('aliyun_', '')
        else:
            return jsonify({
                'success': False,
                'message': '无效的主机ID'
            }), 400
        
        # 获取主机连接信息（复用之前的连接）
        
        if host_type == 'manual':
            cursor.execute("""
                SELECT hostname, ip, username, password, port, protocol
                FROM hosts WHERE id = %s
            """, (original_id,))
        else:
            cursor.execute("""
                SELECT instance_name as hostname, 
                       COALESCE(public_ip, private_ip) as ip,
                       'root' as username,
                       '' as password,
                       22 as port,
                       'SSH' as protocol
                FROM aliyun_ecs_cache WHERE instance_id = %s
            """, (original_id,))
        
        host_info = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not host_info:
            return jsonify({
                'success': False,
                'message': '主机不存在'
            }), 404
        
        # 生成实例ID
        instance_id = str(uuid.uuid4())[:8]
        
        # 执行安装
        result = _install_app_on_host(host_info, app_id, app_info, instance_id, config)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"安装Docker应用失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'安装失败: {str(e)}'
        }), 500

def _install_app_on_host(host_info, app_id, app_info, instance_id, config):
    """在指定主机上安装应用"""
    try:
        # 创建SSH连接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 连接主机
        if host_info['password']:
            ssh.connect(
                hostname=host_info['ip'],
                port=host_info['port'],
                username=host_info['username'],
                password=host_info['password']
            )
        else:
            # 对于阿里云ECS，可能需要密钥连接，这里先用密码方式
            return {
                'success': False,
                'message': '阿里云ECS需要配置SSH密钥或密码'
            }
        
        # 1. 检查Docker是否安装
        stdin, stdout, stderr = ssh.exec_command('which docker')
        if stdout.read().decode().strip() == '':
            # 安装Docker
            install_commands = [
                'curl -fsSL https://get.docker.com | sh',
                'systemctl enable docker',
                'systemctl start docker',
                'usermod -aG docker $USER'
            ]
            for cmd in install_commands:
                stdin, stdout, stderr = ssh.exec_command(f'sudo {cmd}')
                stdout.read()  # 等待命令执行完成
        
        # 2. 检查docker-compose是否安装
        stdin, stdout, stderr = ssh.exec_command('which docker-compose')
        if stdout.read().decode().strip() == '':
            # 安装docker-compose
            stdin, stdout, stderr = ssh.exec_command(
                'sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose'
            )
            stdout.read()
        
        # 3. 创建应用目录
        app_dir = f'/opt/sremanage/apps/{app_id}_{instance_id}'
        ssh.exec_command(f'sudo mkdir -p {app_dir}/{{config,data,logs}}')
        
        # 4. 生成docker-compose.yml
        compose_content = _generate_docker_compose(app_id, app_info, instance_id, config)
        
        # 写入docker-compose.yml文件
        stdin, stdout, stderr = ssh.exec_command(f'sudo tee {app_dir}/docker-compose.yml')
        stdin.write(compose_content)
        stdin.flush()
        stdin.close()
        
        # 5. 生成环境变量文件
        env_content = _generate_env_file(app_info, config)
        stdin, stdout, stderr = ssh.exec_command(f'sudo tee {app_dir}/.env')
        stdin.write(env_content)
        stdin.flush()
        stdin.close()
        
        # 6. 启动应用
        stdin, stdout, stderr = ssh.exec_command(f'cd {app_dir} && sudo docker-compose up -d')
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        
        if error and 'warning' not in error.lower():
            return {
                'success': False,
                'message': f'启动失败: {error}'
            }
        
        return {
            'success': True,
            'message': f'{app_info["name"]} 安装成功',
            'data': {
                'instance_id': instance_id,
                'app_id': app_id,
                'host': host_info['hostname'],
                'output': output
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'安装过程中出错: {str(e)}'
        }

def _generate_docker_compose(app_id, app_info, instance_id, config):
    """生成docker-compose.yml内容"""
    
    if app_id == 'nginx':
        return f"""version: '3.8'
services:
  nginx:
    image: nginx:${{NGINX_VERSION:-latest}}
    container_name: sremanage_nginx_{instance_id}
    ports:
      - "${{NGINX_PORT:-8080}}:80"
    volumes:
      - ./config:/etc/nginx/conf.d:ro
      - ./data:/usr/share/nginx/html
      - ./logs:/var/log/nginx
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
"""
    
    elif app_id == 'mysql':
        return f"""version: '3.8'
services:
  mysql:
    image: mysql:${{MYSQL_VERSION:-8.0}}
    container_name: sremanage_mysql_{instance_id}
    ports:
      - "${{MYSQL_PORT:-3306}}:3306"
    volumes:
      - ./data:/var/lib/mysql
      - ./config:/etc/mysql/conf.d
      - ./logs:/var/log/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=${{MYSQL_ROOT_PASSWORD:-123456}}
      - TZ=Asia/Shanghai
    restart: unless-stopped
"""
    
    elif app_id == 'redis':
        return f"""version: '3.8'
services:
  redis:
    image: redis:${{REDIS_VERSION:-7}}
    container_name: sremanage_redis_{instance_id}
    ports:
      - "${{REDIS_PORT:-6379}}:6379"
    volumes:
      - ./data:/data
      - ./config:/usr/local/etc/redis
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
    command: redis-server --appendonly yes
"""
    
    elif app_id == 'postgresql':
        return f"""version: '3.8'
services:
  postgresql:
    image: postgres:${{POSTGRES_VERSION:-15}}
    container_name: sremanage_postgres_{instance_id}
    ports:
      - "${{POSTGRES_PORT:-5432}}:5432"
    volumes:
      - ./data:/var/lib/postgresql/data
      - ./config:/etc/postgresql
    environment:
      - POSTGRES_PASSWORD=${{POSTGRES_PASSWORD:-123456}}
      - TZ=Asia/Shanghai
    restart: unless-stopped
"""
    
    elif app_id == 'mongodb':
        return f"""version: '3.8'
services:
  mongodb:
    image: mongo:${{MONGO_VERSION:-7}}
    container_name: sremanage_mongo_{instance_id}
    ports:
      - "${{MONGO_PORT:-27017}}:27017"
    volumes:
      - ./data:/data/db
      - ./config:/data/configdb
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
"""
    
    return ""

def _generate_env_file(app_info, config):
    """生成.env文件内容"""
    lines = []
    
    for key, var_info in app_info['env_vars'].items():
        value = config.get(key, var_info['default'])
        lines.append(f"{key}={value}")
    
    return '\n'.join(lines)

@docker_apps_bp.route('/docker-apps/installed', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_installed_apps():
    """获取已安装的应用列表"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # 从新的app_instances表获取已安装应用
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT 
                i.id, i.template_id, i.instance_name, i.host_id, i.host_type,
                i.config, i.status, i.health_status, i.port_mappings,
                i.deploy_path, i.installed_at, i.updated_at,
                t.name as template_name, t.category, t.version,
                CASE 
                    WHEN i.host_type = 'manual' THEN h.hostname
                    WHEN i.host_type = 'aliyun' THEN e.instance_name
                    ELSE '未知主机'
                END as host_name
            FROM app_instances i
            JOIN app_templates t ON i.template_id = t.id
            LEFT JOIN hosts h ON i.host_type = 'manual' AND i.host_id = CONCAT('manual_', h.id)
            LEFT JOIN aliyun_ecs_cache e ON i.host_type = 'aliyun' AND i.host_id = CONCAT('aliyun_', e.instance_id)
            ORDER BY i.installed_at DESC
        """)
        
        instances = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 处理JSON字段并转换为前端期望的格式
        installed_apps = []
        for instance in instances:
            app = {
                'id': f"{instance['template_id']}_{instance['id']}",
                'instance_id': instance['id'],
                'template_id': instance['template_id'],
                'name': instance['template_name'],
                'instance_name': instance['instance_name'],
                'category': instance['category'],
                'version': instance['version'],
                'host': instance['host_name'] or '未知主机',
                'host_id': instance['host_id'],
                'status': instance['status'],
                'health_status': instance['health_status'],
                'deploy_path': instance['deploy_path'],
                'config': json.loads(instance['config']) if instance['config'] else {},
                'port_mappings': json.loads(instance['port_mappings']) if instance['port_mappings'] else [],
                'installed_at': instance['installed_at'].strftime('%Y-%m-%d %H:%M:%S') if instance['installed_at'] else '',
                'updated_at': instance['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if instance['updated_at'] else ''
            }
            installed_apps.append(app)
        
        return jsonify({
            'success': True,
            'data': installed_apps
        })
        
    except Exception as e:
        logger.error(f"获取已安装应用失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取已安装应用失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps/instances/<instance_id>/start', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def start_app_instance(instance_id):
    """启动应用实例"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        result = _manage_app_instance_action(instance_id, 'start')
        return jsonify(result)
    except Exception as e:
        logger.error(f"启动应用实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'启动应用实例失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps/instances/<instance_id>/stop', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def stop_app_instance(instance_id):
    """停止应用实例"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        result = _manage_app_instance_action(instance_id, 'stop')
        return jsonify(result)
    except Exception as e:
        logger.error(f"停止应用实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'停止应用实例失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps/instances/<instance_id>/restart', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def restart_app_instance(instance_id):
    """重启应用实例"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        result = _manage_app_instance_action(instance_id, 'restart')
        return jsonify(result)
    except Exception as e:
        logger.error(f"重启应用实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'重启应用实例失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps/instances/<instance_id>/uninstall', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def uninstall_app_instance(instance_id):
    """卸载应用实例"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        result = _manage_app_instance_action(instance_id, 'uninstall')
        
        if result['success']:
            # 删除实例记录
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM app_instances WHERE id = %s", (instance_id,))
            conn.commit()
            cursor.close()
            conn.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"卸载应用实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'卸载应用实例失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps/instances/<instance_id>/logs-test', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_instance_logs_test(instance_id):
    """获取实例日志 - 测试接口，不需要认证"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # 为演示数据提供模拟日志
        demo_logs = {
            'f4bb1412': {
                'logs': '''2025-07-04 10:30:15 [notice] 1#1: using the "epoll" event method
2025-07-04 10:30:15 [notice] 1#1: nginx/1.25.3
2025-07-04 10:30:15 [notice] 1#1: built by gcc 12.2.0 (Debian 12.2.0-14)
2025-07-04 10:30:15 [notice] 1#1: OS: Linux 5.4.0-73-generic
2025-07-04 10:30:15 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2025-07-04 10:30:15 [notice] 1#1: start worker processes
2025-07-04 10:31:20 [info] 29#29: *1 client 172.17.0.1 connected to 0.0.0.0:80
2025-07-04 10:31:20 172.17.0.1 - - [04/Jul/2025:02:31:20 +0000] "GET / HTTP/1.1" 200 615''',
                'container_name': 'sremanage_nginx_f4bb1412'
            },
            'a8c91234': {
                'logs': '''1:C 04 Jul 2025 02:30:45.123 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1:C 04 Jul 2025 02:30:45.123 # Redis version=7.0.11, bits=64, commit=00000000, modified=0, pid=1, just started
1:C 04 Jul 2025 02:30:45.123 # Configuration loaded
1:M 04 Jul 2025 02:30:45.124 * Increased maximum number of open files to 10032 (it was originally set to 1024).
1:M 04 Jul 2025 02:30:45.125 * Running mode=standalone, port=6379.
1:M 04 Jul 2025 02:30:45.126 * Ready to accept connections''',
                'container_name': 'sremanage_redis_a8c91234'
            }
        }
        
        if instance_id in demo_logs:
            return jsonify({
                'success': True,
                'data': {
                    'logs': demo_logs[instance_id]['logs'],
                    'error_logs': '',
                    'container_name': demo_logs[instance_id]['container_name']
                },
                'demo': True
            })
        else:
            return jsonify({
                'success': False,
                'message': '演示数据中不存在该实例'
            }), 404
            
    except Exception as e:
        logger.error(f"获取测试日志失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取测试日志失败: {str(e)}'
        }), 500

@docker_apps_bp.route('/docker-apps/instances/<instance_id>/logs', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_instance_logs(instance_id):
    """获取实例日志"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取实例信息
        cursor.execute("""
            SELECT i.*, t.name as template_name, t.compose_template
            FROM app_instances i
            JOIN app_templates t ON i.template_id = t.id
            WHERE i.id = %s
        """, (instance_id,))
        
        instance = cursor.fetchone()
        if not instance:
            return jsonify({
                'success': False,
                'message': '应用实例不存在'
            }), 404
        
        # 获取主机信息
        host_info = _get_host_info_by_id(cursor, instance['host_id'])
        if not host_info:
            return jsonify({
                'success': False,
                'message': '主机信息不存在'
            }), 404
        
        cursor.close()
        conn.close()
        
        # 连接主机获取日志
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=host_info['ip'],
            port=host_info['port'],
            username=host_info['username'],
            password=host_info['password']
        )
        
        # 获取容器日志
        container_name = f"sremanage_{instance['template_id']}_{instance_id}"
        stdin, stdout, stderr = ssh.exec_command(f'docker logs --tail 100 {container_name}')
        logs = stdout.read().decode()
        error_logs = stderr.read().decode()
        
        ssh.close()
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs,
                'error_logs': error_logs,
                'container_name': container_name
            }
        })
        
    except Exception as e:
        logger.error(f"获取实例日志失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取实例日志失败: {str(e)}'
        }), 500

def _manage_app_instance_action(instance_id, action):
    """管理应用实例操作"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取实例信息
        cursor.execute("""
            SELECT i.*, t.name as template_name
            FROM app_instances i
            JOIN app_templates t ON i.template_id = t.id
            WHERE i.id = %s
        """, (instance_id,))
        
        instance = cursor.fetchone()
        if not instance:
            return {
                'success': False,
                'message': '应用实例不存在'
            }
        
        # 获取主机信息
        host_info = _get_host_info_by_id(cursor, instance['host_id'])
        if not host_info:
            return {
                'success': False,
                'message': '主机信息不存在'
            }
        
        cursor.close()
        conn.close()
        
        # 创建SSH连接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=host_info['ip'],
            port=host_info['port'],
            username=host_info['username'],
            password=host_info['password']
        )
        
        # 执行操作
        deploy_path = instance['deploy_path'] or f"/opt/sremanage/apps/{instance['template_id']}_{instance_id}"
        container_name = f"sremanage_{instance['template_id']}_{instance_id}"
        
        if action == 'start':
            cmd = f'cd {deploy_path} && sudo docker-compose start'
            new_status = 'running'
        elif action == 'stop':
            cmd = f'cd {deploy_path} && sudo docker-compose stop'
            new_status = 'stopped'
        elif action == 'restart':
            cmd = f'cd {deploy_path} && sudo docker-compose restart'
            new_status = 'running'
        elif action == 'uninstall':
            cmd = f'cd {deploy_path} && sudo docker-compose down -v && sudo rm -rf {deploy_path}'
            new_status = 'uninstalled'
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        
        if error and 'warning' not in error.lower():
            return {
                'success': False,
                'message': f'{action}失败: {error}'
            }
        
        # 更新实例状态
        if action != 'uninstall':
            _update_instance_status(instance_id, new_status)
        
        return {
            'success': True,
            'message': f'{instance["template_name"]} {action}成功',
            'data': {
                'instance_id': instance_id,
                'output': output
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'{action}过程中出错: {str(e)}'
        }

def _get_host_info_by_id(cursor, host_id):
    """根据host_id获取主机信息"""
    if host_id.startswith('manual_'):
        original_id = int(host_id.replace('manual_', ''))
        cursor.execute("""
            SELECT hostname, ip, username, password, port, protocol
            FROM hosts WHERE id = %s
        """, (original_id,))
    elif host_id.startswith('aliyun_'):
        original_id = host_id.replace('aliyun_', '')
        cursor.execute("""
            SELECT instance_name as hostname, 
                   COALESCE(public_ip, private_ip) as ip,
                   'root' as username,
                   '' as password,
                   22 as port,
                   'SSH' as protocol
            FROM aliyun_ecs_cache WHERE instance_id = %s
        """, (original_id,))
    else:
        return None
    
    return cursor.fetchone()

def _update_instance_status(instance_id, status):
    """更新实例状态"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE app_instances 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (status, instance_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"更新实例状态失败: {str(e)}")