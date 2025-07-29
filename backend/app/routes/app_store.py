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
import yaml
from string import Template
from datetime import datetime

app_store_bp = Blueprint('app_store', __name__, url_prefix='/api/app-store')

@app_store_bp.route('/templates', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_app_templates():
    """获取应用模板列表"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        category = request.args.get('category', '')
        status = request.args.get('status', 'active')
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 构建查询条件
        conditions = ["status = %s"]
        params = [status]
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        # 查询模板
        cursor.execute(f"""
            SELECT id, name, description, category, version, logo_url, tags, 
                   ports, volumes, env_vars, is_system, created_at, updated_at
            FROM app_templates 
            WHERE {where_clause}
            ORDER BY is_system DESC, category, name
        """, params)
        
        templates = cursor.fetchall()
        
        # 查询分类
        cursor.execute("SELECT id, name FROM app_categories ORDER BY sort_order")
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 处理JSON字段
        for template in templates:
            template['tags'] = json.loads(template['tags']) if template['tags'] else []
            template['ports'] = json.loads(template['ports']) if template['ports'] else []
            template['volumes'] = json.loads(template['volumes']) if template['volumes'] else []
            template['env_vars'] = json.loads(template['env_vars']) if template['env_vars'] else {}
        
        return jsonify({
            'success': True,
            'data': {
                'templates': templates,
                'categories': categories,
                'total': len(templates)
            }
        })
        
    except Exception as e:
        logger.error(f"获取应用模板失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取应用模板失败: {str(e)}'
        }), 500

@app_store_bp.route('/templates', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def create_app_template():
    """创建应用模板"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['id', 'name', 'description', 'category']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': '缺少必要的字段'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查ID是否已存在
        cursor.execute("SELECT id FROM app_templates WHERE id = %s", (data['id'],))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': '应用ID已存在'
            }), 400
        
        # 插入模板
        cursor.execute("""
            INSERT INTO app_templates (
                id, name, description, category, version, logo_url, tags,
                deploy_type, compose_template, services, ports, volumes, env_vars,
                status, created_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            data['id'],
            data['name'],
            data['description'],
            data['category'],
            data.get('version', 'latest'),
            data.get('logo_url'),
            json.dumps(data.get('tags', [])),
            data.get('deploy_type', 'docker_compose'),
            data.get('compose_template'),
            json.dumps(data.get('services', {})),
            json.dumps(data.get('ports', [])),
            json.dumps(data.get('volumes', [])),
            json.dumps(data.get('env_vars', {})),
            data.get('status', 'active'),
            data.get('created_by')  # 从token中获取
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '应用模板创建成功'
        })
        
    except Exception as e:
        logger.error(f"创建应用模板失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建应用模板失败: {str(e)}'
        }), 500

@app_store_bp.route('/templates/<template_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
@token_required
def update_app_template(template_id):
    """更新应用模板"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查模板是否存在和是否为系统预设
        cursor.execute("SELECT id, is_system FROM app_templates WHERE id = %s", (template_id,))
        template_info = cursor.fetchone()
        if not template_info:
            return jsonify({
                'success': False,
                'message': '应用模板不存在'
            }), 404
        
        # 现在允许修改所有应用模板，包括系统预设
        
        # 更新模板
        update_fields = []
        params = []
        
        updatable_fields = {
            'name': 'name',
            'description': 'description',
            'category': 'category',
            'version': 'version',
            'logo_url': 'logo_url',
            'tags': 'tags',
            'deploy_type': 'deploy_type',
            'compose_template': 'compose_template',
            'services': 'services',
            'ports': 'ports',
            'volumes': 'volumes',
            'env_vars': 'env_vars',
            'status': 'status'
        }
        
        for field, db_field in updatable_fields.items():
            if field in data:
                update_fields.append(f"{db_field} = %s")
                if field in ['tags', 'services', 'ports', 'volumes', 'env_vars']:
                    params.append(json.dumps(data[field]))
                else:
                    params.append(data[field])
        
        if update_fields:
            params.append(template_id)
            cursor.execute(f"""
                UPDATE app_templates 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, params)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '应用模板更新成功'
        })
        
    except Exception as e:
        logger.error(f"更新应用模板失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新应用模板失败: {str(e)}'
        }), 500

@app_store_bp.route('/templates/<template_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@token_required
def delete_app_template(template_id):
    """删除应用模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否有实例使用该模板
        cursor.execute("SELECT COUNT(*) FROM app_instances WHERE template_id = %s", (template_id,))
        instance_count = cursor.fetchone()[0]
        
        if instance_count > 0:
            return jsonify({
                'success': False,
                'message': f'该模板有 {instance_count} 个正在使用的实例，无法删除'
            }), 400
        
        # 删除模板
        cursor.execute("DELETE FROM app_templates WHERE id = %s", (template_id,))
        
        if cursor.rowcount == 0:
            return jsonify({
                'success': False,
                'message': '应用模板不存在'
            }), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '应用模板删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除应用模板失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除应用模板失败: {str(e)}'
        }), 500

@app_store_bp.route('/install', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def install_app():
    """安装应用"""
    try:
        data = request.get_json()
        
        required_fields = ['template_id', 'host_id', 'instance_name']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': '缺少必要的字段'
            }), 400
        
        template_id = data['template_id']
        host_id = data['host_id']
        instance_name = data['instance_name']
        config = data.get('config', {})
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取模板信息
        cursor.execute("""
            SELECT * FROM app_templates WHERE id = %s AND status = 'active'
        """, (template_id,))
        template = cursor.fetchone()
        
        if not template:
            return jsonify({
                'success': False,
                'message': '应用模板不存在或已禁用'
            }), 404
        
        # 解析主机信息
        host_info = _get_host_info(cursor, host_id)
        if not host_info:
            return jsonify({
                'success': False,
                'message': '主机不存在'
            }), 404
        
        # 生成实例ID
        instance_id = str(uuid.uuid4())[:8]
        
        # 创建实例记录
        cursor.execute("""
            INSERT INTO app_instances (
                id, template_id, instance_name, host_id, host_type, 
                config, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            instance_id,
            template_id,
            instance_name,
            host_id,
            'manual' if host_id.startswith('manual_') else 'aliyun',
            json.dumps(config),
            'installing'
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # 执行安装
        result = _install_app_instance(template, host_info, instance_id, instance_name, config)
        
        # 更新实例状态
        _update_instance_status(instance_id, 'running' if result['success'] else 'failed')
        
        # 记录日志
        _log_instance_action(instance_id, 'install', result['message'], result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"安装应用失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'安装应用失败: {str(e)}'
        }), 500

@app_store_bp.route('/instances', methods=['GET'])
@cross_origin(supports_credentials=True)
@token_required
def get_app_instances():
    """获取应用实例列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT 
                i.id, i.template_id, i.instance_name, i.host_id, i.host_type,
                i.config, i.status, i.health_status, i.port_mappings,
                i.deploy_path, i.installed_at, i.updated_at,
                t.name as template_name, t.category, t.version
            FROM app_instances i
            JOIN app_templates t ON i.template_id = t.id
            ORDER BY i.installed_at DESC
        """)
        
        instances = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 处理JSON字段
        for instance in instances:
            instance['config'] = json.loads(instance['config']) if instance['config'] else {}
            instance['port_mappings'] = json.loads(instance['port_mappings']) if instance['port_mappings'] else []
        
        return jsonify({
            'success': True,
            'data': instances
        })
        
    except Exception as e:
        logger.error(f"获取应用实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取应用实例失败: {str(e)}'
        }), 500

@app_store_bp.route('/instances/<instance_id>/start', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def start_app_instance(instance_id):
    """启动应用实例"""
    try:
        result = _manage_app_instance(instance_id, 'start')
        return jsonify(result)
    except Exception as e:
        logger.error(f"启动应用实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'启动应用实例失败: {str(e)}'
        }), 500

@app_store_bp.route('/instances/<instance_id>/stop', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def stop_app_instance(instance_id):
    """停止应用实例"""
    try:
        result = _manage_app_instance(instance_id, 'stop')
        return jsonify(result)
    except Exception as e:
        logger.error(f"停止应用实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'停止应用实例失败: {str(e)}'
        }), 500

@app_store_bp.route('/instances/<instance_id>/restart', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def restart_app_instance(instance_id):
    """重启应用实例"""
    try:
        result = _manage_app_instance(instance_id, 'restart')
        return jsonify(result)
    except Exception as e:
        logger.error(f"重启应用实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'重启应用实例失败: {str(e)}'
        }), 500

@app_store_bp.route('/instances/<instance_id>/uninstall', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@token_required
def uninstall_app_instance(instance_id):
    """卸载应用实例"""
    try:
        result = _manage_app_instance(instance_id, 'uninstall')
        
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

@app_store_bp.route('/instances/<instance_id>/logs', methods=['GET'])
@cross_origin(supports_credentials=True)
@token_required
def get_instance_logs(instance_id):
    """获取实例日志"""
    try:
        log_type = request.args.get('type', '')
        limit = int(request.args.get('limit', 100))
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        conditions = ["instance_id = %s"]
        params = [instance_id]
        
        if log_type:
            conditions.append("log_type = %s")
            params.append(log_type)
        
        where_clause = " AND ".join(conditions)
        
        cursor.execute(f"""
            SELECT log_type, message, details, created_at
            FROM app_instance_logs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s
        """, params + [limit])
        
        logs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 处理JSON字段
        for log in logs:
            log['details'] = json.loads(log['details']) if log['details'] else {}
        
        return jsonify({
            'success': True,
            'data': logs
        })
        
    except Exception as e:
        logger.error(f"获取实例日志失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取实例日志失败: {str(e)}'
        }), 500

# 辅助函数

def _get_host_info(cursor, host_id):
    """获取主机信息"""
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

def _install_app_instance(template, host_info, instance_id, instance_name, config):
    """安装应用实例"""
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
            return {
                'success': False,
                'message': '主机需要配置SSH密钥或密码'
            }
        
        # 检查和安装Docker
        _ensure_docker_installed(ssh)
        
        # 创建应用目录
        app_dir = f'/opt/sremanage/apps/{template["id"]}_{instance_id}'
        ssh.exec_command(f'sudo mkdir -p {app_dir}/{{config,data,logs}}')
        
        # 生成配置文件
        compose_content = _generate_compose_content(template, instance_id, instance_name, config)
        env_content = _generate_env_content(template, config)
        
        # 写入配置文件
        _write_remote_file(ssh, f'{app_dir}/docker-compose.yml', compose_content)
        _write_remote_file(ssh, f'{app_dir}/.env', env_content)
        
        # 启动应用
        stdin, stdout, stderr = ssh.exec_command(f'cd {app_dir} && sudo docker-compose up -d')
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        
        if error and 'warning' not in error.lower():
            return {
                'success': False,
                'message': f'启动失败: {error}'
            }
        
        # 更新实例部署路径
        _update_instance_deploy_path(instance_id, app_dir)
        
        return {
            'success': True,
            'message': f'{template["name"]} 安装成功',
            'data': {
                'instance_id': instance_id,
                'deploy_path': app_dir,
                'output': output
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'安装过程中出错: {str(e)}'
        }

def _manage_app_instance(instance_id, action):
    """管理应用实例（启动/停止/重启/卸载）"""
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
        host_info = _get_host_info(cursor, instance['host_id'])
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
        deploy_path = instance['deploy_path']
        if not deploy_path:
            deploy_path = f'/opt/sremanage/apps/{instance["template_id"]}_{instance_id}'
        
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
        
        # 记录日志
        _log_instance_action(instance_id, action, f'{action}成功', {
            'output': output,
            'error': error
        })
        
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

def _ensure_docker_installed(ssh):
    """确保Docker已安装"""
    # 检查Docker是否安装
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
            ssh.exec_command(f'sudo {cmd}')
    
    # 检查docker-compose是否安装
    stdin, stdout, stderr = ssh.exec_command('which docker-compose')
    if stdout.read().decode().strip() == '':
        # 安装docker-compose
        ssh.exec_command(
            'sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose'
        )

def _generate_compose_content(template, instance_id, instance_name, config):
    """生成docker-compose内容"""
    compose_template = template['compose_template']
    
    # 准备变量替换
    variables = {
        'CONTAINER_NAME': f"sremanage_{template['id']}_{instance_id}",
        'INSTANCE_ID': instance_id,
        'INSTANCE_NAME': instance_name
    }
    
    # 添加环境变量配置
    env_vars = json.loads(template['env_vars']) if template['env_vars'] else {}
    for key, var_info in env_vars.items():
        variables[key] = config.get(key, var_info['default'])
    
    # 使用Template进行变量替换
    template_obj = Template(compose_template)
    return template_obj.safe_substitute(variables)

def _generate_env_content(template, config):
    """生成.env文件内容"""
    lines = []
    
    env_vars = json.loads(template['env_vars']) if template['env_vars'] else {}
    for key, var_info in env_vars.items():
        value = config.get(key, var_info['default'])
        lines.append(f"{key}={value}")
    
    return '\n'.join(lines)

def _write_remote_file(ssh, file_path, content):
    """写入远程文件"""
    stdin, stdout, stderr = ssh.exec_command(f'sudo tee {file_path}')
    stdin.write(content)
    stdin.flush()
    stdin.close()

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

def _update_instance_deploy_path(instance_id, deploy_path):
    """更新实例部署路径"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE app_instances 
            SET deploy_path = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (deploy_path, instance_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"更新实例部署路径失败: {str(e)}")

def _log_instance_action(instance_id, action, message, details=None):
    """记录实例操作日志"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO app_instance_logs (instance_id, log_type, message, details)
            VALUES (%s, %s, %s, %s)
        """, (instance_id, action, message, json.dumps(details) if details else None))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"记录实例日志失败: {str(e)}")