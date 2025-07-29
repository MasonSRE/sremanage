"""
简化部署API路由
支持直接粘贴docker-compose.yml内容部署，集成AI助手
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import yaml
import uuid
import paramiko
import os
from app.utils.database import get_db_connection
from app.utils.auth import token_required
from app.utils.logger import logger
from app.services.ai_assistant import ai_assistant
import pymysql

simple_deploy_bp = Blueprint('simple_deploy', __name__, url_prefix='/api/simple-deploy')

@simple_deploy_bp.route('/deploy', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def deploy_compose():
    """部署docker-compose配置"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['compose_content', 'host_id', 'instance_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必要参数: {field}'
                }), 400
        
        compose_content = data['compose_content'].strip()
        host_id = data['host_id']
        instance_name = data['instance_name']
        
        # 验证docker-compose语法
        validation_result = validate_compose_syntax(compose_content)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'message': 'Docker Compose配置语法错误',
                'errors': validation_result['errors']
            }), 400
        
        # 安全检查
        security_result = check_compose_security(compose_content)
        if security_result['has_critical_risks']:
            return jsonify({
                'success': False,
                'message': '配置存在安全风险',
                'risks': security_result['risks']
            }), 400
        
        # 执行部署
        deploy_result = execute_deployment(host_id, compose_content, instance_name)
        
        if deploy_result['success']:
            # 记录部署实例
            record_deployment_instance(instance_name, host_id, compose_content, deploy_result['deploy_path'])
        
        return jsonify(deploy_result)
        
    except Exception as e:
        logger.error(f"部署失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'部署过程出错: {str(e)}'
        }), 500

@simple_deploy_bp.route('/ai/generate', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def ai_generate_compose():
    """AI生成docker-compose配置"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return jsonify({
                'success': False,
                'message': '请提供需求描述'
            }), 400
        
        # 调用AI服务生成配置
        result = ai_assistant.generate_compose(user_prompt)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI生成配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'生成配置失败: {str(e)}'
        }), 500

@simple_deploy_bp.route('/ai/generate/stream', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def ai_generate_compose_stream():
    """AI流式生成docker-compose配置"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return jsonify({
                'success': False,
                'message': '请提供需求描述'
            }), 400
        
        # 返回流式响应
        from flask import Response
        
        def generate():
            for chunk in ai_assistant.stream_generate_compose(user_prompt):
                yield chunk
        
        return Response(generate(), 
                       mimetype='text/event-stream',
                       headers={
                           'Cache-Control': 'no-cache',
                           'Connection': 'keep-alive',
                           'Access-Control-Allow-Origin': '*',
                           'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                           'Access-Control-Allow-Methods': 'POST,OPTIONS'
                       })
        
    except Exception as e:
        logger.error(f"AI流式生成配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'生成配置失败: {str(e)}'
        }), 500

@simple_deploy_bp.route('/ai/status', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def ai_status():
    """获取AI助手状态"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        'success': True,
        'ai_available': ai_assistant.is_available(),
        'model': ai_assistant.model if ai_assistant.is_available() else None,
        'message': 'AI助手已启用' if ai_assistant.is_available() else 'AI助手未配置或已禁用'
    })

@simple_deploy_bp.route('/ai/sre', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def ai_sre_assistant():
    """SRE助手AI响应"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return jsonify({
                'success': False,
                'message': '请提供问题描述'
            }), 400
        
        # 调用AI服务生成SRE响应
        result = ai_assistant.generate_sre_response(user_prompt)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"SRE AI响应失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'SRE助手响应失败: {str(e)}'
        }), 500

@simple_deploy_bp.route('/instances', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def list_instances():
    """获取已部署的实例列表"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT instance_name, host_id, deploy_path, status, created_at
            FROM simple_deploy_instances
            ORDER BY created_at DESC
        """)
        
        instances = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': instances
        })
        
    except Exception as e:
        logger.error(f"获取实例列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取实例列表失败: {str(e)}'
        }), 500

@simple_deploy_bp.route('/instances/<instance_name>/stop', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def stop_instance(instance_name):
    """停止实例"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return manage_instance(instance_name, 'stop')

@simple_deploy_bp.route('/instances/<instance_name>/start', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def start_instance(instance_name):
    """启动实例"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return manage_instance(instance_name, 'start')

@simple_deploy_bp.route('/instances/<instance_name>/remove', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def remove_instance(instance_name):
    """删除实例"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return manage_instance(instance_name, 'remove')

# 辅助函数

def validate_compose_syntax(compose_content):
    """验证docker-compose语法"""
    try:
        parsed = yaml.safe_load(compose_content)
        errors = []
        
        # 基本结构检查
        if not isinstance(parsed, dict):
            errors.append("配置必须是有效的YAML格式")
            return {'valid': False, 'errors': errors}
        
        if 'services' not in parsed:
            errors.append("缺少 'services' 配置")
        
        if 'version' not in parsed:
            errors.append("建议添加 'version' 字段")
        
        # 服务检查
        if 'services' in parsed and isinstance(parsed['services'], dict):
            for service_name, service_config in parsed['services'].items():
                if not isinstance(service_config, dict):
                    errors.append(f"服务 '{service_name}' 配置格式错误")
                    continue
                    
                if 'image' not in service_config:
                    errors.append(f"服务 '{service_name}' 缺少 'image' 配置")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
        
    except yaml.YAMLError as e:
        return {
            'valid': False,
            'errors': [f"YAML语法错误: {str(e)}"]
        }

def check_compose_security(compose_content):
    """检查docker-compose配置的安全性"""
    try:
        parsed = yaml.safe_load(compose_content)
        risks = []
        critical_risks = []
        
        for service_name, service_config in parsed.get('services', {}).items():
            if not isinstance(service_config, dict):
                continue
                
            # 检查特权模式
            if service_config.get('privileged'):
                critical_risks.append(f"服务 '{service_name}' 使用特权模式（privileged: true）")
            
            # 检查主机网络
            if service_config.get('network_mode') == 'host':
                risks.append(f"服务 '{service_name}' 使用主机网络模式")
            
            # 检查危险的卷挂载
            volumes = service_config.get('volumes', [])
            for volume in volumes:
                if isinstance(volume, str) and ':' in volume:
                    host_path = volume.split(':')[0]
                    # 检查是否挂载系统关键目录
                    dangerous_paths = ['/etc', '/usr', '/var', '/boot', '/proc', '/sys']
                    for dangerous_path in dangerous_paths:
                        if host_path.startswith(dangerous_path):
                            critical_risks.append(f"服务 '{service_name}' 挂载危险系统目录: {host_path}")
                            break
            
            # 检查端口配置
            ports = service_config.get('ports', [])
            for port in ports:
                if isinstance(port, str) and ':' in port:
                    host_port = port.split(':')[0]
                    try:
                        host_port_num = int(host_port)
                        if host_port_num < 1024:
                            risks.append(f"服务 '{service_name}' 使用特权端口: {host_port}")
                    except ValueError:
                        pass
        
        return {
            'has_risks': len(risks) > 0,
            'has_critical_risks': len(critical_risks) > 0,
            'risks': risks + critical_risks
        }
        
    except:
        return {
            'has_risks': False,
            'has_critical_risks': False,
            'risks': []
        }

def get_host_info(host_id):
    """获取主机信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if host_id.startswith('manual_'):
            original_id = int(host_id.replace('manual_', ''))
            cursor.execute("""
                SELECT hostname, ip, username, password, port
                FROM hosts WHERE id = %s
            """, (original_id,))
        elif host_id.startswith('aliyun_'):
            original_id = host_id.replace('aliyun_', '')
            cursor.execute("""
                SELECT instance_name as hostname, 
                       COALESCE(public_ip, private_ip) as ip,
                       'root' as username,
                       '' as password,
                       22 as port
                FROM aliyun_ecs_cache WHERE instance_id = %s
            """, (original_id,))
        else:
            return None
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        logger.error(f"获取主机信息失败: {str(e)}")
        return None

def execute_deployment(host_id, compose_content, instance_name):
    """执行部署"""
    try:
        # 获取主机信息
        host_info = get_host_info(host_id)
        if not host_info:
            return {
                'success': False,
                'message': '主机信息不存在'
            }
        
        # 创建SSH连接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 连接主机
        if host_info['password']:
            ssh.connect(
                hostname=host_info['ip'],
                port=host_info.get('port', 22),
                username=host_info['username'],
                password=host_info['password']
            )
        else:
            return {
                'success': False,
                'message': '主机需要配置SSH密码'
            }
        
        # 创建部署目录
        deploy_path = f'/opt/sremanage/simple/{instance_name}'
        ssh.exec_command(f'sudo mkdir -p {deploy_path}')
        
        # 写入docker-compose.yml
        stdin, stdout, stderr = ssh.exec_command(f'sudo tee {deploy_path}/docker-compose.yml > /dev/null')
        stdin.write(compose_content)
        stdin.close()
        
        # 启动服务
        stdin, stdout, stderr = ssh.exec_command(f'cd {deploy_path} && sudo docker-compose up -d')
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        
        if error and 'warning' not in error.lower() and 'pulling' not in error.lower():
            return {
                'success': False,
                'message': f'部署失败: {error}',
                'output': output
            }
        
        return {
            'success': True,
            'message': f'部署成功！实例：{instance_name}',
            'data': {
                'instance_name': instance_name,
                'deploy_path': deploy_path,
                'output': output
            },
            'deploy_path': deploy_path
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'部署过程出错: {str(e)}'
        }

def record_deployment_instance(instance_name, host_id, compose_content, deploy_path):
    """记录部署实例到数据库"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simple_deploy_instances (
                id INT AUTO_INCREMENT PRIMARY KEY,
                instance_name VARCHAR(100) UNIQUE NOT NULL,
                host_id VARCHAR(50) NOT NULL,
                compose_content TEXT NOT NULL,
                deploy_path VARCHAR(255),
                status VARCHAR(20) DEFAULT 'running',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # 插入实例记录
        cursor.execute("""
            INSERT INTO simple_deploy_instances 
            (instance_name, host_id, compose_content, deploy_path, status)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            compose_content = VALUES(compose_content),
            deploy_path = VALUES(deploy_path),
            status = 'running',
            updated_at = CURRENT_TIMESTAMP
        """, (instance_name, host_id, compose_content, deploy_path, 'running'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"记录部署实例失败: {str(e)}")

def manage_instance(instance_name, action):
    """管理实例（启动/停止/删除）"""
    try:
        # 获取实例信息
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT * FROM simple_deploy_instances WHERE instance_name = %s
        """, (instance_name,))
        
        instance = cursor.fetchone()
        if not instance:
            return jsonify({
                'success': False,
                'message': '实例不存在'
            })
        
        # 获取主机信息
        host_info = get_host_info(instance['host_id'])
        if not host_info:
            return jsonify({
                'success': False,
                'message': '主机信息不存在'
            })
        
        # SSH连接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_info['ip'],
            port=host_info.get('port', 22),
            username=host_info['username'],
            password=host_info['password']
        )
        
        deploy_path = instance['deploy_path']
        
        # 执行操作
        if action == 'start':
            cmd = f'cd {deploy_path} && sudo docker-compose start'
            new_status = 'running'
        elif action == 'stop':
            cmd = f'cd {deploy_path} && sudo docker-compose stop'
            new_status = 'stopped'
        elif action == 'remove':
            cmd = f'cd {deploy_path} && sudo docker-compose down -v && sudo rm -rf {deploy_path}'
            new_status = 'removed'
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        
        # 更新数据库状态
        if action == 'remove':
            cursor.execute("DELETE FROM simple_deploy_instances WHERE instance_name = %s", (instance_name,))
        else:
            cursor.execute("""
                UPDATE simple_deploy_instances 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE instance_name = %s
            """, (new_status, instance_name))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'实例{action}成功',
            'output': output
        })
        
    except Exception as e:
        logger.error(f"管理实例失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500