from flask import Blueprint, request, jsonify
from typing import Dict, Any, List, Optional
from app.utils.auth import login_required
from app.utils.database import get_db, get_db_connection
from app.utils.security import decrypt_sensitive_data, encrypt_sensitive_data, is_data_encrypted
from app.utils.db_context import database_connection
from app.utils.response import APIResponse, api_response
from app.utils.validation import validate_json_schema, validators, StringValidator, ListValidator
from app.utils.performance import (
    monitor_performance, 
    cached, 
    rate_limit, 
    performance_monitor,
    simple_cache,
    rate_limiter
)
from app.utils.security_enhancement import (
    security_audit,
    validate_input_security,
    enhanced_rate_limit,
    security_auditor,
    api_security_manager,
    SecurityHealthChecker
)
from app.utils.encryption import (
    encryption_manager,
    token_manager,
    data_masking,
    encrypt_sensitive_response,
    mask_sensitive_logs
)
from app.utils.permission_control import (
    permission_manager,
    require_permission,
    require_admin,
    require_write,
    require_read,
    require_super_admin,
    check_user_permission,
    get_current_user_permissions,
    ResourceType,
    PermissionLevel,
    Permission,
    Role
)
from app.utils.error_handling import (
    error_handler,
    handle_exceptions,
    safe_execute,
    with_recovery,
    retry_on_network_error,
    fallback_on_external_api_error,
    CustomException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    NetworkError,
    ExternalAPIError,
    BusinessLogicError,
    ErrorSeverity,
    ErrorCategory
)
from app.utils.retry_fallback import (
    retry_manager,
    fallback_manager,
    circuit_breakers,
    get_circuit_breaker,
    retry,
    circuit_breaker,
    fallback,
    resilience,
    get_resilience_status,
    reset_all_circuit_breakers,
    cleanup_old_statistics,
    RetryConfig,
    CircuitBreakerConfig,
    FallbackConfig,
    RetryStrategy,
    CircuitState,
    FallbackStrategy,
    PresetConfigs
)
import paramiko
import concurrent.futures
import requests
from requests.auth import HTTPBasicAuth
import base64
import logging
import time
import re
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

bp = Blueprint('ops', __name__, url_prefix='/api/ops')

def get_jenkins_instance_with_decrypted_token(instance_id):
    """
    获取Jenkins实例并解密token
    
    Args:
        instance_id: Jenkins实例ID
        
    Returns:
        tuple: (instance_dict, decrypted_token) 或 (None, None) 如果实例不存在
    """
    try:
        with database_connection() as db:
            with db.cursor() as cursor:
                cursor.execute('SELECT * FROM jenkins_settings WHERE id = %s', (instance_id,))
                instance = cursor.fetchone()
                
            if not instance:
                logger.warning(f"Jenkins实例 {instance_id} 不存在")
                return None, None
            
            # 解密Jenkins token
            jenkins_token = instance['token']
            if jenkins_token:
                try:
                    jenkins_token = decrypt_sensitive_data(jenkins_token)
                    logger.debug(f"成功解密Jenkins实例 {instance_id} 的token")
                except Exception as e:
                    logger.error(f"解密Jenkins实例 {instance_id} token失败: {e}")
                    # 降级到明文token，保持向后兼容
            
            return instance, jenkins_token
            
    except Exception as e:
        logger.error(f"获取Jenkins实例 {instance_id} 失败: {e}")
        return None, None

@bp.route('/batch-command', methods=['POST'])
@login_required
@validate_json_schema({
    'hosts': ListValidator(
        StringValidator(min_length=1, max_length=100),
        min_length=1,
        max_length=50
    ),
    'command': StringValidator(min_length=1, max_length=1000)
})
@api_response
def batch_command():
    """批量执行命令（需要认证）"""
    return _batch_command()

@bp.route('/batch-command-test', methods=['POST'])
@validate_json_schema({
    'hosts': ListValidator(
        StringValidator(min_length=1, max_length=100),
        min_length=1,
        max_length=10  # 测试版本限制更少主机
    ),
    'command': StringValidator(min_length=1, max_length=500)  # 测试版本限制命令长度
})
@api_response
def batch_command_test():
    """批量执行命令（测试版本，无需认证）"""
    return _batch_command()

def _batch_command():
    """批量执行命令"""
    data = request.get_json()
    
    results = []
    
    def execute_command(host_id):
        try:
            with database_connection() as db:
                with db.cursor() as cursor:
                    # 解析主机ID并获取主机信息
                    host = None
                    
                    if host_id.startswith('manual_'):
                        # 手动添加的主机
                        original_id = int(host_id.replace('manual_', ''))
                        cursor.execute(
                            "SELECT hostname, ip, username, password, port FROM hosts WHERE id = %s",
                            (original_id,)
                        )
                        host_data = cursor.fetchone()
                        if host_data:
                            # 解密密码
                            decrypted_password = None
                            if host_data['password']:
                                try:
                                    decrypted_password = decrypt_sensitive_data(host_data['password'])
                                    logger.debug(f"成功解密手动主机 {original_id} 的密码")
                                except Exception as e:
                                    logger.error(f"解密手动主机密码失败: {e}")
                                    decrypted_password = host_data['password']  # 降级到明文
                            
                            host = {
                                'hostname': host_data['hostname'],
                                'ip': host_data['ip'],
                                'username': host_data['username'],
                                'password': decrypted_password,
                                'port': host_data.get('port', 22)
                            }
                    elif host_id.startswith('aliyun_'):
                        # 阿里云ECS实例
                        original_id = host_id.replace('aliyun_', '')
                        cursor.execute(
                            "SELECT instance_name as hostname, COALESCE(public_ip, private_ip) as ip FROM aliyun_ecs_cache WHERE instance_id = %s",
                            (original_id,)
                        )
                        host_data = cursor.fetchone()
                        if host_data:
                            # 获取阿里云实例的密码
                            password = None
                            cursor.execute("SELECT password FROM aliyun_instance_config WHERE instance_id = %s", (original_id,))
                            password_result = cursor.fetchone()
                            if password_result and password_result['password']:
                                # 解密密码
                                try:
                                    password = decrypt_sensitive_data(password_result['password'])
                                    logger.debug(f"成功解密阿里云实例 {original_id} 的密码")
                                except Exception as e:
                                    logger.error(f"解密阿里云实例密码失败: {e}")
                                    password = password_result['password']  # 降级到明文
                            
                            # 如果没有找到密码，尝试从手动主机表查找
                            if not password:
                                cursor.execute("SELECT password FROM hosts WHERE ip = %s AND username = %s", (host_data['ip'], 'root'))
                                fallback_result = cursor.fetchone()
                                if fallback_result and fallback_result['password']:
                                    try:
                                        password = decrypt_sensitive_data(fallback_result['password'])
                                        logger.debug(f"成功解密手动主机密码")
                                    except Exception as e:
                                        logger.error(f"解密手动主机密码失败: {e}")
                                        password = fallback_result['password']  # 降级到明文
                            
                            host = {
                                'hostname': host_data['hostname'],
                                'ip': host_data['ip'],
                                'username': 'root',  # 阿里云ECS默认用户
                                'password': password or '',  # 使用解密后的密码
                                'port': 22
                            }
                
                if not host:
                    return {
                        'hostname': f'Unknown Host ({host_id})',
                        'ip': 'unknown',
                        'status': 'error',
                        'output': 'Host not found'
                    }
                
                # 检查是否有密码
                if not host.get('password'):
                    return {
                        'hostname': host['hostname'],
                        'ip': host['ip'],
                        'status': 'error',
                        'output': 'Authentication failed: 请先配置主机登录密码'
                    }
                
                # 创建SSH客户端
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                try:
                    # 统一使用密码认证（与终端连接方式一致）
                    ssh.connect(
                        hostname=host['ip'],
                        username=host['username'],
                        password=host['password'],
                        timeout=10
                    )
                    
                    # 执行命令
                    stdin, stdout, stderr = ssh.exec_command(data['command'])
                    output = stdout.read().decode().strip()
                    error = stderr.read().decode().strip()
                    
                    # 处理输出显示
                    if error:
                        display_output = error
                        status = 'error'
                    elif output:
                        display_output = output
                        status = 'success'
                    else:
                        # 命令成功执行但无输出时，显示友好提示
                        display_output = '执行成功'
                        status = 'success'
                    
                    return {
                        'hostname': host['hostname'],
                        'ip': host['ip'],
                        'status': status,
                        'output': display_output
                    }
                except Exception as ssh_e:
                    return {
                        'hostname': host['hostname'],
                        'ip': host['ip'],
                        'status': 'error',
                        'output': str(ssh_e)
                    }
                finally:
                    try:
                        ssh.close()
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"执行命令时发生异常: {e}")
            return {
                'hostname': f'Error Host ({host_id})',
                'ip': 'unknown',
                'status': 'error',
                'output': f'执行失败: {str(e)}'
            }
    
    # 使用线程池并行执行命令
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(execute_command, data['hosts']))
    
    # 统计执行结果
    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = len(results) - success_count
    
    message = f"批量命令执行完成: 成功 {success_count} 个，失败 {error_count} 个"
    
    return APIResponse.success(
        data={
            'results': results,
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': error_count,
                'command': data['command']
            }
        },
        message=message
    )

@bp.route('/jenkins/jobs/<int:instance_id>', methods=['GET'])
@login_required
@monitor_performance('jenkins_jobs_list')
@cached(ttl=120, key_prefix='jobs_')  # 缓存2分钟，任务列表变化相对频繁
@rate_limit(max_requests=60, window_seconds=60)  # 每分钟最多60次请求，这是高频API
@api_response
def get_jenkins_jobs(instance_id):
    """获取指定Jenkins实例的任务列表"""
    instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
    if not instance:
        return APIResponse.not_found('Jenkins实例不存在', 'jenkins_instance')
    
    # 调用Jenkins API获取任务列表
    jobs_url = f"{instance['url']}/api/json?tree=jobs[name,url,buildable,lastBuild[number,timestamp,result,duration]]"
    
    try:
        response = requests.get(
            jobs_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=10
        )
        
        if response.status_code == 200:
            jenkins_data = response.json()
            jobs = []
            
            for job in jenkins_data.get('jobs', []):
                last_build = job.get('lastBuild') or {}
                jobs.append({
                    'name': job['name'],
                    'url': job['url'],
                    'buildable': job['buildable'],
                    'lastBuildNumber': last_build.get('number', 0),
                    'lastBuildTime': last_build.get('timestamp', 0),
                    'status': last_build.get('result', 'unknown').lower() if last_build.get('result') else 'unknown',
                    'duration': last_build.get('duration', 0)
                })
            
            return APIResponse.success(jobs, f"成功获取 {len(jobs)} 个任务")
        else:
            return APIResponse.error(
                f"Jenkins API调用失败: HTTP {response.status_code}",
                code=502,
                error_code="JENKINS_API_ERROR"
            )
            
    except requests.exceptions.Timeout:
        return APIResponse.error("Jenkins连接超时", code=504, error_code="JENKINS_TIMEOUT")
    except requests.exceptions.ConnectionError:
        return APIResponse.error("无法连接到Jenkins服务器", code=503, error_code="JENKINS_CONNECTION_ERROR")

@bp.route('/jenkins/build/<int:instance_id>/<job_name>', methods=['POST'])
@login_required
@api_response
def trigger_jenkins_build(instance_id, job_name):
    """触发Jenkins构建任务"""
    # 参数验证
    if not job_name.strip():
        return APIResponse.validation_error(["任务名称不能为空"])
    
    instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
    if not instance:
        return APIResponse.not_found('Jenkins实例不存在', 'jenkins_instance')
    
    # 获取请求参数
    data = request.get_json() or {}
    parameters = data.get('parameters', {})
    
    try:
        # 确定构建URL和参数
        if parameters:
            # 参数化构建
            build_url = f"{instance['url']}/job/{job_name}/buildWithParameters"
            response = requests.post(
                build_url,
                data=parameters,
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=10
            )
        else:
            # 普通构建
            build_url = f"{instance['url']}/job/{job_name}/build"
            response = requests.post(
                build_url,
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=10
            )
        
        if response.status_code in [200, 201]:
            # 获取队列位置信息
            queue_location = response.headers.get('Location')
            return APIResponse.success(
                data={
                    'jobName': job_name,
                    'queueLocation': queue_location,
                    'buildTriggered': True
                },
                message=f'任务 {job_name} 构建已触发'
            )
        elif response.status_code == 404:
            return APIResponse.not_found(f'Jenkins任务 {job_name} 不存在', 'jenkins_job')
        elif response.status_code == 403:
            return APIResponse.forbidden('没有权限触发此任务')
        else:
            return APIResponse.error(
                f'Jenkins构建触发失败: HTTP {response.status_code}',
                code=502,
                error_code="BUILD_TRIGGER_FAILED"
            )
            
    except requests.exceptions.Timeout:
        return APIResponse.error("Jenkins连接超时", code=504, error_code="JENKINS_TIMEOUT")
    except requests.exceptions.ConnectionError:
        return APIResponse.error("无法连接到Jenkins服务器", code=503, error_code="JENKINS_CONNECTION_ERROR")

@bp.route('/jenkins/test/<int:instance_id>', methods=['POST'])
@login_required
def test_jenkins_connection(instance_id):
    """测试Jenkins连接"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 测试连接
        test_url = f"{instance['url']}/api/json"
        
        response = requests.get(
            test_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Jenkins连接测试成功'})
        elif response.status_code == 401:
            return jsonify({'success': False, 'message': 'Jenkins认证失败：用户名或API Token错误'})
        elif response.status_code == 403:
            return jsonify({'success': False, 'message': 'Jenkins权限不足：用户无访问权限'})
        elif response.status_code == 404:
            return jsonify({'success': False, 'message': 'Jenkins API未找到：请检查Jenkins URL是否正确'})
        elif response.status_code >= 500:
            return jsonify({'success': False, 'message': 'Jenkins服务器错误：请检查Jenkins服务状态'})
        else:
            return jsonify({'success': False, 'message': f'Jenkins连接测试失败: HTTP {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'连接测试失败: {str(e)}'})

@bp.route('/jenkins/queue/<int:instance_id>', methods=['GET'])
@login_required
def get_jenkins_queue(instance_id):
    """获取Jenkins构建队列"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取队列信息
        queue_url = f"{instance['url']}/queue/api/json"
        
        response = requests.get(
            queue_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=10
        )
        
        if response.status_code == 200:
            queue_data = response.json()
            queue_items = []
            
            for item in queue_data.get('items', []):
                task = item.get('task', {})
                queue_items.append({
                    'id': item.get('id'),
                    'jobName': task.get('name'),
                    'why': item.get('why'),
                    'inQueueSince': item.get('inQueueSince'),
                    'stuck': item.get('stuck', False),
                    'blocked': item.get('blocked', False)
                })
            
            return jsonify({'success': True, 'data': queue_items})
        else:
            return jsonify({'success': False, 'message': 'Jenkins队列API调用失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/build/<int:instance_id>/<job_name>/<int:build_number>/log', methods=['GET'])
@login_required
def get_jenkins_build_log(instance_id, job_name, build_number):
    """获取Jenkins构建日志"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取构建日志
        log_url = f"{instance['url']}/job/{job_name}/{build_number}/consoleText"
        
        response = requests.get(
            log_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=30
        )
        
        if response.status_code == 200:
            return jsonify({
                'success': True, 
                'data': {
                    'log': response.text,
                    'jobName': job_name,
                    'buildNumber': build_number
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Jenkins日志获取失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/build/<int:instance_id>/<job_name>/<int:build_number>', methods=['GET'])
@login_required
def get_jenkins_build_details(instance_id, job_name, build_number):
    """获取Jenkins构建详情"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取构建详情
        build_url = f"{instance['url']}/job/{job_name}/{build_number}/api/json"
        
        response = requests.get(
            build_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=10
        )
        
        if response.status_code == 200:
            build_data = response.json()
            return jsonify({
                'success': True, 
                'data': {
                    'number': build_data.get('number'),
                    'result': build_data.get('result'),
                    'building': build_data.get('building', False),
                    'duration': build_data.get('duration', 0),
                    'timestamp': build_data.get('timestamp', 0),
                    'description': build_data.get('description', ''),
                    'culprits': [c.get('fullName') for c in build_data.get('culprits', [])],
                    'changeSet': {
                        'items': [
                            {
                                'author': item.get('author', {}).get('fullName'),
                                'msg': item.get('msg'),
                                'commitId': item.get('commitId')
                            } for item in build_data.get('changeSet', {}).get('items', [])
                        ]
                    }
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Jenkins构建详情获取失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/batch-build/<int:instance_id>', methods=['POST'])
@login_required
def batch_jenkins_build(instance_id):
    """批量触发Jenkins构建"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        data = request.get_json()
        job_names = data.get('jobs', [])
        parameters = data.get('parameters', {})
        
        if not job_names:
            return jsonify({'success': False, 'message': '未指定构建任务'})
        
        results = []
        
        def trigger_single_build(job_name):
            try:
                if parameters:
                    build_url = f"{instance['url']}/job/{job_name}/buildWithParameters"
                    response = requests.post(
                        build_url,
                        data=parameters,
                        auth=HTTPBasicAuth(instance['username'], jenkins_token),
                        timeout=10
                    )
                else:
                    build_url = f"{instance['url']}/job/{job_name}/build"
                    response = requests.post(
                        build_url,
                        auth=HTTPBasicAuth(instance['username'], jenkins_token),
                        timeout=10
                    )
                
                if response.status_code in [200, 201]:
                    return {
                        'jobName': job_name,
                        'status': 'success',
                        'message': '构建已触发',
                        'queueLocation': response.headers.get('Location')
                    }
                else:
                    return {
                        'jobName': job_name,
                        'status': 'error',
                        'message': f'触发失败: HTTP {response.status_code}'
                    }
            except Exception as e:
                return {
                    'jobName': job_name,
                    'status': 'error',
                    'message': str(e)
                }
        
        # 使用线程池并行触发构建
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(trigger_single_build, job_names))
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return jsonify({
            'success': True,
            'message': f'批量构建完成，成功触发 {success_count}/{len(job_names)} 个任务',
            'data': results
        })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/status/<int:instance_id>', methods=['GET'])
@login_required
@monitor_performance('jenkins_status')
@cached(ttl=60, key_prefix='status_')  # 缓存1分钟，状态信息需要相对实时
@rate_limit(max_requests=120, window_seconds=60)  # 每分钟最多120次请求，状态查询很频繁
def get_jenkins_status(instance_id):
    """获取Jenkins实例状态概览"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取Jenkins基本信息
        info_url = f"{instance['url']}/api/json"
        
        response = requests.get(
            info_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=10
        )
        
        if response.status_code == 200:
            jenkins_info = response.json()
            
            # 统计作业状态
            total_jobs = len(jenkins_info.get('jobs', []))
            building_jobs = 0
            failed_jobs = 0
            success_jobs = 0
            
            for job in jenkins_info.get('jobs', []):
                last_build = job.get('lastBuild', {})
                if last_build:
                    # 需要单独查询每个job的详细信息来获取构建状态
                    pass
                    
            # 获取队列信息
            queue_url = f"{instance['url']}/queue/api/json"
            queue_response = requests.get(
                queue_url,
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=5
            )
            
            queue_count = 0
            if queue_response.status_code == 200:
                queue_data = queue_response.json()
                queue_count = len(queue_data.get('items', []))
            
            return jsonify({
                'success': True,
                'data': {
                    'totalJobs': total_jobs,
                    'queueCount': queue_count,
                    'jenkinsVersion': jenkins_info.get('version', 'unknown'),
                    'mode': jenkins_info.get('mode', 'unknown'),
                    'nodeDescription': jenkins_info.get('nodeDescription', ''),
                    'quietingDown': jenkins_info.get('quietingDown', False)
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Jenkins状态获取失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/history/<int:instance_id>', methods=['GET'])
@login_required
def get_jenkins_build_history(instance_id):
    """获取Jenkins构建历史"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取所有任务的最近构建历史
        jobs_url = f"{instance['url']}/api/json?tree=jobs[name,builds[number,timestamp,result,duration,actions[lastBuiltRevision[SHA1],causes[userId,userName]]]]"
        
        response = requests.get(
            jobs_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=30  
        )
        
        if response.status_code == 200:
            jenkins_data = response.json()
            build_history = []
            
            for job in jenkins_data.get('jobs', []):
                job_name = job['name']
                builds = job.get('builds', [])
                
                # 取每个任务的最近5次构建
                for build in builds[:5]:
                    # 获取触发者信息
                    triggered_by = 'unknown'
                    for action in build.get('actions', []):
                        if 'causes' in action:
                            for cause in action['causes']:
                                if cause.get('userName'):
                                    triggered_by = cause['userName']
                                    break
                                elif cause.get('userId'):
                                    triggered_by = cause['userId']
                                    break
                        if triggered_by != 'unknown':
                            break
                    
                    build_history.append({
                        'id': f"{job_name}-{build['number']}",
                        'jobName': job_name,
                        'number': build['number'],
                        'status': build.get('result', 'unknown').lower() if build.get('result') else 'building',
                        'triggeredBy': triggered_by,
                        'startTime': build.get('timestamp', 0),
                        'duration': build.get('duration', 0)
                    })
            
            # 按时间排序，最新的在前
            build_history.sort(key=lambda x: x['startTime'], reverse=True)
            
            # 只返回最近50条记录
            return jsonify({'success': True, 'data': build_history[:50]})
        else:
            return jsonify({'success': False, 'message': 'Jenkins API调用失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/analytics/<int:instance_id>', methods=['GET'])
@login_required
def get_jenkins_analytics(instance_id):
    """获取Jenkins构建历史统计分析"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取查询参数
        days = request.args.get('days', 7, type=int)  # 默认7天
        limit = request.args.get('limit', 100, type=int)  # 默认100条记录
        
        # 获取更详细的构建历史数据
        jobs_url = f"{instance['url']}/api/json?tree=jobs[name,builds[number,timestamp,result,duration,estimatedDuration,actions[lastBuiltRevision[SHA1],causes[userId,userName]]]]"
        
        response = requests.get(
            jobs_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=30
        )
        
        if response.status_code == 200:
            jenkins_data = response.json()
            
            # 计算时间范围
            import time
            end_time = int(time.time() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            # 收集所有构建数据
            all_builds = []
            job_stats = {}
            
            for job in jenkins_data.get('jobs', []):
                job_name = job['name']
                builds = job.get('builds', [])
                
                job_stats[job_name] = {
                    'totalBuilds': 0,
                    'successBuilds': 0,
                    'failedBuilds': 0,
                    'averageDuration': 0,
                    'totalDuration': 0
                }
                
                for build in builds:
                    build_time = build.get('timestamp', 0)
                    
                    # 只统计指定时间范围内的构建
                    if build_time >= start_time:
                        # 获取触发者信息
                        triggered_by = 'unknown'
                        for action in build.get('actions', []):
                            if 'causes' in action:
                                for cause in action['causes']:
                                    if cause.get('userName'):
                                        triggered_by = cause['userName']
                                        break
                                    elif cause.get('userId'):
                                        triggered_by = cause['userId']
                                        break
                            if triggered_by != 'unknown':
                                break
                        
                        build_status = build.get('result', 'unknown').lower() if build.get('result') else 'building'
                        build_duration = build.get('duration', 0)
                        
                        build_record = {
                            'id': f"{job_name}-{build['number']}",
                            'jobName': job_name,
                            'number': build['number'],
                            'status': build_status,
                            'triggeredBy': triggered_by,
                            'startTime': build_time,
                            'duration': build_duration,
                            'estimatedDuration': build.get('estimatedDuration', 0)
                        }
                        
                        all_builds.append(build_record)
                        
                        # 更新任务统计
                        job_stats[job_name]['totalBuilds'] += 1
                        job_stats[job_name]['totalDuration'] += build_duration
                        
                        if build_status == 'success':
                            job_stats[job_name]['successBuilds'] += 1
                        elif build_status == 'failure':
                            job_stats[job_name]['failedBuilds'] += 1
            
            # 计算平均构建时长
            for job_name, stats in job_stats.items():
                if stats['totalBuilds'] > 0:
                    stats['averageDuration'] = stats['totalDuration'] // stats['totalBuilds']
                    stats['successRate'] = round((stats['successBuilds'] / stats['totalBuilds']) * 100, 2)
                else:
                    stats['successRate'] = 0
            
            # 按时间排序，最新的在前
            all_builds.sort(key=lambda x: x['startTime'], reverse=True)
            
            # 计算总体统计
            total_builds = len(all_builds)
            success_builds = len([b for b in all_builds if b['status'] == 'success'])
            failed_builds = len([b for b in all_builds if b['status'] == 'failure'])
            building_builds = len([b for b in all_builds if b['status'] == 'building'])
            
            overall_success_rate = round((success_builds / total_builds * 100), 2) if total_builds > 0 else 0
            average_duration = sum([b['duration'] for b in all_builds]) // total_builds if total_builds > 0 else 0
            
            return jsonify({
                'success': True,
                'data': {
                    'summary': {
                        'totalBuilds': total_builds,
                        'successBuilds': success_builds,
                        'failedBuilds': failed_builds,
                        'buildingBuilds': building_builds,
                        'successRate': overall_success_rate,
                        'averageDuration': average_duration,
                        'timeRange': {
                            'days': days,
                            'startTime': start_time,
                            'endTime': end_time
                        }
                    },
                    'jobStats': job_stats,
                    'builds': all_builds[:limit]
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Jenkins API调用失败'})
            
    except Exception as e:
        logger.error(f"获取Jenkins分析数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/trends/<int:instance_id>', methods=['GET'])
@login_required  
def get_jenkins_trends(instance_id):
    """获取Jenkins构建趋势分析"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取查询参数
        days = request.args.get('days', 30, type=int)  # 默认30天
        interval = request.args.get('interval', 'daily')  # daily, hourly, weekly
        
        # 获取构建历史数据
        jobs_url = f"{instance['url']}/api/json?tree=jobs[name,builds[number,timestamp,result,duration]]"
        
        response = requests.get(
            jobs_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=30
        )
        
        if response.status_code == 200:
            jenkins_data = response.json()
            
            # 计算时间范围
            import time
            from datetime import datetime, timedelta
            
            end_time = int(time.time() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            # 收集时间段内的构建数据
            builds_by_time = {}
            duration_trends = {}
            
            # 根据interval确定时间间隔
            if interval == 'hourly':
                time_format = '%Y-%m-%d %H:00'
                interval_ms = 60 * 60 * 1000  # 1小时
            elif interval == 'weekly':
                time_format = '%Y-W%U'
                interval_ms = 7 * 24 * 60 * 60 * 1000  # 1周
            else:  # daily
                time_format = '%Y-%m-%d'
                interval_ms = 24 * 60 * 60 * 1000  # 1天
            
            for job in jenkins_data.get('jobs', []):
                builds = job.get('builds', [])
                
                for build in builds:
                    build_time = build.get('timestamp', 0)
                    
                    if build_time >= start_time:
                        # 格式化时间键
                        time_key = datetime.fromtimestamp(build_time / 1000).strftime(time_format)
                        
                        if time_key not in builds_by_time:
                            builds_by_time[time_key] = {
                                'total': 0,
                                'success': 0,
                                'failure': 0,
                                'building': 0,
                                'totalDuration': 0,
                                'builds': []
                            }
                        
                        build_status = build.get('result', 'unknown').lower() if build.get('result') else 'building'
                        build_duration = build.get('duration', 0)
                        
                        builds_by_time[time_key]['total'] += 1
                        builds_by_time[time_key]['totalDuration'] += build_duration
                        builds_by_time[time_key]['builds'].append({
                            'jobName': job['name'],
                            'number': build['number'],
                            'status': build_status,
                            'duration': build_duration,
                            'timestamp': build_time
                        })
                        
                        if build_status == 'success':
                            builds_by_time[time_key]['success'] += 1
                        elif build_status == 'failure':
                            builds_by_time[time_key]['failure'] += 1
                        elif build_status == 'building':
                            builds_by_time[time_key]['building'] += 1
            
            # 计算趋势数据
            trend_data = []
            for time_key in sorted(builds_by_time.keys()):
                stats = builds_by_time[time_key]
                avg_duration = stats['totalDuration'] // stats['total'] if stats['total'] > 0 else 0
                success_rate = round((stats['success'] / stats['total'] * 100), 2) if stats['total'] > 0 else 0
                
                trend_data.append({
                    'time': time_key,
                    'total': stats['total'],
                    'success': stats['success'],
                    'failure': stats['failure'],
                    'building': stats['building'],
                    'successRate': success_rate,
                    'averageDuration': avg_duration
                })
            
            return jsonify({
                'success': True,
                'data': {
                    'interval': interval,
                    'days': days,
                    'trends': trend_data,
                    'summary': {
                        'totalPeriods': len(trend_data),
                        'averageBuildsPerPeriod': sum([t['total'] for t in trend_data]) / len(trend_data) if trend_data else 0,
                        'overallSuccessRate': sum([t['successRate'] for t in trend_data]) / len(trend_data) if trend_data else 0
                    }
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Jenkins API调用失败'})
            
    except Exception as e:
        logger.error(f"获取Jenkins趋势数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/metrics/<int:instance_id>', methods=['GET'])
@login_required
def get_jenkins_metrics(instance_id):
    """获取Jenkins性能指标监控数据"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取查询参数
        metric_type = request.args.get('type', 'overview')  # overview, performance, health
        
        # 获取Jenkins系统信息和构建数据
        system_url = f"{instance['url']}/api/json"
        jobs_url = f"{instance['url']}/api/json?tree=jobs[name,builds[number,timestamp,result,duration,estimatedDuration]]"
        queue_url = f"{instance['url']}/queue/api/json"
        
        # 并行请求多个API
        import concurrent.futures
        
        def fetch_url(url):
            return requests.get(
                url,
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=15
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            system_future = executor.submit(fetch_url, system_url)
            jobs_future = executor.submit(fetch_url, jobs_url)
            queue_future = executor.submit(fetch_url, queue_url)
            
            system_response = system_future.result()
            jobs_response = jobs_future.result()
            queue_response = queue_future.result()
        
        if all(r.status_code == 200 for r in [system_response, jobs_response, queue_response]):
            system_data = system_response.json()
            jobs_data = jobs_response.json()
            queue_data = queue_response.json()
            
            # 计算时间范围（最近24小时）
            import time
            end_time = int(time.time() * 1000)
            start_time_24h = end_time - (24 * 60 * 60 * 1000)
            start_time_7d = end_time - (7 * 24 * 60 * 60 * 1000)
            
            # 收集性能数据
            recent_builds = []
            job_performance = {}
            
            for job in jobs_data.get('jobs', []):
                job_name = job['name']
                builds = job.get('builds', [])
                
                job_performance[job_name] = {
                    'recent24h': {'count': 0, 'success': 0, 'failure': 0, 'totalDuration': 0, 'avgDuration': 0},
                    'recent7d': {'count': 0, 'success': 0, 'failure': 0, 'totalDuration': 0, 'avgDuration': 0},
                    'efficiency': 0,  # 实际时长 vs 预计时长的比率
                    'stability': 0   # 成功率
                }
                
                for build in builds:
                    build_time = build.get('timestamp', 0)
                    build_status = build.get('result', 'unknown').lower() if build.get('result') else 'building'
                    build_duration = build.get('duration', 0)
                    estimated_duration = build.get('estimatedDuration', 0)
                    
                    # 24小时内的构建
                    if build_time >= start_time_24h:
                        job_performance[job_name]['recent24h']['count'] += 1
                        job_performance[job_name]['recent24h']['totalDuration'] += build_duration
                        
                        if build_status == 'success':
                            job_performance[job_name]['recent24h']['success'] += 1
                        elif build_status == 'failure':
                            job_performance[job_name]['recent24h']['failure'] += 1
                        
                        recent_builds.append({
                            'jobName': job_name,
                            'number': build['number'],
                            'status': build_status,
                            'duration': build_duration,
                            'estimatedDuration': estimated_duration,
                            'timestamp': build_time,
                            'efficiency': (build_duration / estimated_duration * 100) if estimated_duration > 0 else 100
                        })
                    
                    # 7天内的构建
                    if build_time >= start_time_7d:
                        job_performance[job_name]['recent7d']['count'] += 1
                        job_performance[job_name]['recent7d']['totalDuration'] += build_duration
                        
                        if build_status == 'success':
                            job_performance[job_name]['recent7d']['success'] += 1
                        elif build_status == 'failure':
                            job_performance[job_name]['recent7d']['failure'] += 1
            
            # 计算性能指标
            for job_name, perf in job_performance.items():
                # 计算平均构建时长
                for period in ['recent24h', 'recent7d']:
                    if perf[period]['count'] > 0:
                        perf[period]['avgDuration'] = perf[period]['totalDuration'] // perf[period]['count']
                        perf[period]['successRate'] = round((perf[period]['success'] / perf[period]['count']) * 100, 2)
                    else:
                        perf[period]['successRate'] = 0
                
                # 计算稳定性（7天成功率）
                perf['stability'] = perf['recent7d']['successRate']
                
                # 计算效率（实际时长 vs 预计时长）
                job_builds = [b for b in recent_builds if b['jobName'] == job_name]
                if job_builds:
                    avg_efficiency = sum([b['efficiency'] for b in job_builds]) / len(job_builds)
                    perf['efficiency'] = round(avg_efficiency, 2)
            
            # 系统性能概览
            total_jobs = len(jobs_data.get('jobs', []))
            queue_length = len(queue_data.get('items', []))
            
            # 计算24小时内的总体指标
            total_builds_24h = len(recent_builds)
            success_builds_24h = len([b for b in recent_builds if b['status'] == 'success'])
            failed_builds_24h = len([b for b in recent_builds if b['status'] == 'failure'])
            building_builds = len([b for b in recent_builds if b['status'] == 'building'])
            
            overall_success_rate = round((success_builds_24h / total_builds_24h * 100), 2) if total_builds_24h > 0 else 0
            avg_build_duration = sum([b['duration'] for b in recent_builds]) // total_builds_24h if total_builds_24h > 0 else 0
            
            # 构建性能等级分类
            performance_levels = {
                'excellent': len([j for j, p in job_performance.items() if p['stability'] >= 95 and p['efficiency'] <= 120]),
                'good': len([j for j, p in job_performance.items() if p['stability'] >= 80 and p['stability'] < 95]),
                'fair': len([j for j, p in job_performance.items() if p['stability'] >= 60 and p['stability'] < 80]),
                'poor': len([j for j, p in job_performance.items() if p['stability'] < 60])
            }
            
            # 性能预警
            warnings = []
            
            # 检查构建队列堆积
            if queue_length > 5:
                warnings.append({
                    'type': 'queue_backlog',
                    'level': 'warning',
                    'message': f'构建队列堆积严重，当前有 {queue_length} 个任务等待',
                    'suggestion': '考虑增加构建节点或优化构建效率'
                })
            
            # 检查失败率过高的任务
            high_failure_jobs = [j for j, p in job_performance.items() if p['recent24h']['count'] > 0 and p['stability'] < 50]
            if high_failure_jobs:
                warnings.append({
                    'type': 'high_failure_rate',
                    'level': 'error',
                    'message': f'发现 {len(high_failure_jobs)} 个任务失败率过高',
                    'jobs': high_failure_jobs[:5],  # 只显示前5个
                    'suggestion': '检查构建脚本和环境配置'
                })
            
            # 检查构建时长异常的任务
            slow_jobs = [j for j, p in job_performance.items() if p['efficiency'] > 200]
            if slow_jobs:
                warnings.append({
                    'type': 'slow_builds',
                    'level': 'warning', 
                    'message': f'发现 {len(slow_jobs)} 个任务构建时长异常',
                    'jobs': slow_jobs[:5],
                    'suggestion': '优化构建脚本或增加资源配置'
                })
            
            metrics_data = {
                'overview': {
                    'totalJobs': total_jobs,
                    'queueLength': queue_length,
                    'builds24h': total_builds_24h,
                    'successBuilds24h': success_builds_24h,
                    'failedBuilds24h': failed_builds_24h,
                    'buildingBuilds': building_builds,
                    'overallSuccessRate': overall_success_rate,
                    'averageBuildDuration': avg_build_duration,
                    'performanceLevels': performance_levels
                },
                'jobPerformance': job_performance,
                'recentBuilds': sorted(recent_builds, key=lambda x: x['timestamp'], reverse=True)[:20],
                'warnings': warnings,
                'systemInfo': {
                    'jenkinsVersion': system_data.get('version', 'unknown'),
                    'mode': system_data.get('mode', 'unknown'),
                    'nodeDescription': system_data.get('nodeDescription', ''),
                    'quietingDown': system_data.get('quietingDown', False)
                },
                'timestamp': end_time
            }
            
            return jsonify({
                'success': True,
                'data': metrics_data
            })
        else:
            return jsonify({'success': False, 'message': 'Jenkins API调用失败'})
            
    except Exception as e:
        logger.error(f"获取Jenkins性能指标失败: {e}")
        return jsonify({'success': False, 'message': str(e)})



@bp.route('/jenkins/health-check/<int:instance_id>', methods=['POST'])
@login_required
def jenkins_comprehensive_health_check(instance_id):
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        health_results = {
            'overall': 'unknown',
            'score': 0,
            'checks': {},
            'recommendations': [],
            'timestamp': int(time.time() * 1000)
        }
        
        # 1. 连接性检查
        try:
            start_time = time.time()
            response = requests.get(
                f"{instance['url']}/api/json",
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=10
            )
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                health_results['checks']['connectivity'] = {
                    'status': 'healthy',
                    'responseTime': response_time,
                    'message': f'连接正常，响应时间 {response_time}ms'
                }
                health_results['score'] += 25
            else:
                health_results['checks']['connectivity'] = {
                    'status': 'unhealthy',
                    'responseTime': response_time,
                    'message': f'连接异常，HTTP状态码: {response.status_code}'
                }
                health_results['recommendations'].append('检查Jenkins服务状态和网络连接')
                
        except Exception as e:
            health_results['checks']['connectivity'] = {
                'status': 'unhealthy',
                'message': f'连接失败: {str(e)}'
            }
            health_results['recommendations'].append('检查Jenkins服务器是否运行正常')
        
        # 2. 系统状态检查
        try:
            system_response = requests.get(
                f"{instance['url']}/api/json",
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=10
            )
            
            if system_response.status_code == 200:
                system_data = system_response.json()
                
                # 检查系统是否正在关闭
                quieting_down = system_data.get('quietingDown', False)
                if quieting_down:
                    health_results['checks']['system_status'] = {
                        'status': 'warning',
                        'message': 'Jenkins正在准备关闭'
                    }
                    health_results['recommendations'].append('Jenkins系统正在关闭中，避免触发新构建')
                    health_results['score'] += 15
                else:
                    health_results['checks']['system_status'] = {
                        'status': 'healthy',
                        'message': 'Jenkins系统运行正常'
                    }
                    health_results['score'] += 25
                
        except Exception as e:
            health_results['checks']['system_status'] = {
                'status': 'unhealthy',
                'message': f'无法获取系统状态: {str(e)}'
            }
        
        # 3. 构建队列检查
        try:
            queue_response = requests.get(
                f"{instance['url']}/queue/api/json",
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=10
            )
            
            if queue_response.status_code == 200:
                queue_data = queue_response.json()
                queue_length = len(queue_data.get('items', []))
                stuck_items = len([item for item in queue_data.get('items', []) if item.get('stuck', False)])
                
                if queue_length == 0:
                    health_results['checks']['queue'] = {
                        'status': 'healthy',
                        'queueLength': queue_length,
                        'message': '构建队列为空'
                    }
                    health_results['score'] += 25
                elif queue_length <= 5:
                    health_results['checks']['queue'] = {
                        'status': 'healthy',
                        'queueLength': queue_length,
                        'message': f'构建队列正常，当前 {queue_length} 个任务'
                    }
                    health_results['score'] += 20
                elif queue_length <= 10:
                    health_results['checks']['queue'] = {
                        'status': 'warning',
                        'queueLength': queue_length,
                        'message': f'构建队列较长，当前 {queue_length} 个任务'
                    }
                    health_results['recommendations'].append('监控构建队列，考虑增加构建资源')
                    health_results['score'] += 15
                else:
                    health_results['checks']['queue'] = {
                        'status': 'unhealthy',
                        'queueLength': queue_length,
                        'stuckItems': stuck_items,
                        'message': f'构建队列堆积严重，当前 {queue_length} 个任务'
                    }
                    health_results['recommendations'].append('构建队列堆积严重，需要立即处理')
                    health_results['score'] += 5
                    
        except Exception as e:
            health_results['checks']['queue'] = {
                'status': 'unhealthy',
                'message': f'无法获取队列状态: {str(e)}'
            }
        
        # 4. 最近构建状态检查
        try:
            jobs_response = requests.get(
                f"{instance['url']}/api/json?tree=jobs[name,builds[number,timestamp,result,duration]]",
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=15
            )
            
            if jobs_response.status_code == 200:
                jobs_data = jobs_response.json()
                
                # 分析最近1小时的构建
                current_time = int(time.time() * 1000)
                one_hour_ago = current_time - (60 * 60 * 1000)
                
                recent_builds = []
                for job in jobs_data.get('jobs', []):
                    for build in job.get('builds', [])[:5]:  # 只检查最近5次构建
                        if build.get('timestamp', 0) >= one_hour_ago:
                            recent_builds.append(build)
                
                if recent_builds:
                    success_count = len([b for b in recent_builds if b.get('result') == 'SUCCESS'])
                    failure_count = len([b for b in recent_builds if b.get('result') == 'FAILURE'])
                    success_rate = (success_count / len(recent_builds)) * 100
                    
                    if success_rate >= 90:
                        health_results['checks']['recent_builds'] = {
                            'status': 'healthy',
                            'successRate': round(success_rate, 2),
                            'totalBuilds': len(recent_builds),
                            'message': f'最近构建成功率良好 ({success_rate:.1f}%)'
                        }
                        health_results['score'] += 25
                    elif success_rate >= 70:
                        health_results['checks']['recent_builds'] = {
                            'status': 'warning',
                            'successRate': round(success_rate, 2),
                            'totalBuilds': len(recent_builds),
                            'message': f'最近构建成功率偏低 ({success_rate:.1f}%)'
                        }
                        health_results['recommendations'].append('关注构建失败的任务，检查相关配置')
                        health_results['score'] += 15
                    else:
                        health_results['checks']['recent_builds'] = {
                            'status': 'unhealthy',
                            'successRate': round(success_rate, 2),
                            'totalBuilds': len(recent_builds),
                            'failureCount': failure_count,
                            'message': f'最近构建成功率过低 ({success_rate:.1f}%)'
                        }
                        health_results['recommendations'].append('构建失败率过高，需要立即检查相关任务')
                        health_results['score'] += 5
                else:
                    health_results['checks']['recent_builds'] = {
                        'status': 'healthy',
                        'message': '最近1小时内无构建活动'
                    }
                    health_results['score'] += 20
                    
        except Exception as e:
            health_results['checks']['recent_builds'] = {
                'status': 'unhealthy',  
                'message': f'无法获取构建历史: {str(e)}'
            }
        
        # 确定总体健康状态
        if health_results['score'] >= 90:
            health_results['overall'] = 'healthy'
        elif health_results['score'] >= 70:
            health_results['overall'] = 'warning'
        else:
            health_results['overall'] = 'unhealthy'
        
        return jsonify({
            'success': True,
            'data': health_results
        })
        
    except Exception as e:
        logger.error(f"Jenkins健康检查失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ==================== Phase 4: 智能化升级功能 ====================

@bp.route('/jenkins/prediction/<int:instance_id>', methods=['GET'])
@login_required
@security_audit('jenkins_prediction_access')
@validate_input_security()
@monitor_performance('jenkins_prediction_analysis')
@cached(ttl=300, key_prefix='prediction_')  # 缓存5分钟
@enhanced_rate_limit(max_requests=30, window_seconds=60)  # 每分钟最多30次请求
def get_build_prediction(instance_id):
    """获取构建预测分析"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取查询参数
        job_name = request.args.get('job_name')  # 特定任务的预测，如果未指定则返回整体预测
        days = int(request.args.get('days', 30))  # 分析历史数据的天数
        
        # 获取Jenkins构建历史数据
        if job_name:
            jobs_url = f"{instance['url']}/job/{job_name}/api/json?tree=builds[number,timestamp,result,duration,estimatedDuration,executor[displayName]]"
        else:
            jobs_url = f"{instance['url']}/api/json?tree=jobs[name,builds[number,timestamp,result,duration,estimatedDuration,executor[displayName]]]"
        
        system_url = f"{instance['url']}/api/json"
        queue_url = f"{instance['url']}/queue/api/json"
        
        # 并行请求多个API
        import concurrent.futures
        import statistics
        from datetime import datetime, timedelta
        
        def fetch_url(url):
            return requests.get(
                url,
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=20
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            jobs_future = executor.submit(fetch_url, jobs_url)
            system_future = executor.submit(fetch_url, system_url)
            queue_future = executor.submit(fetch_url, queue_url)
            
            jobs_response = jobs_future.result()
            system_response = system_future.result()
            queue_response = queue_future.result()
        
        if not all(r.status_code == 200 for r in [jobs_response, system_response, queue_response]):
            return jsonify({'success': False, 'message': 'Jenkins API调用失败'})
        
        jobs_data = jobs_response.json()
        system_data = system_response.json()
        queue_data = queue_response.json()
        
        # 计算时间范围
        end_time = int(time.time() * 1000)
        start_time = end_time - (days * 24 * 60 * 60 * 1000)
        
        # 收集历史构建数据
        historical_builds = []
        
        if job_name:
            # 单个任务预测
            builds = jobs_data.get('builds', [])
            for build in builds:
                if build.get('timestamp', 0) >= start_time:
                    historical_builds.append({
                        'jobName': job_name,
                        'timestamp': build.get('timestamp', 0),
                        'result': build.get('result', 'unknown'),
                        'duration': build.get('duration', 0),
                        'estimatedDuration': build.get('estimatedDuration', 0),
                        'executor': build.get('executor', {}).get('displayName', 'unknown') if build.get('executor') else 'unknown'
                    })
        else:
            # 整体预测
            for job in jobs_data.get('jobs', []):
                job_name_current = job['name']
                builds = job.get('builds', [])
                for build in builds:
                    if build.get('timestamp', 0) >= start_time:
                        historical_builds.append({
                            'jobName': job_name_current,
                            'timestamp': build.get('timestamp', 0),
                            'result': build.get('result', 'unknown'),
                            'duration': build.get('duration', 0),
                            'estimatedDuration': build.get('estimatedDuration', 0),
                            'executor': build.get('executor', {}).get('displayName', 'unknown') if build.get('executor') else 'unknown'
                        })
        
        if not historical_builds:
            return jsonify({
                'success': True,
                'data': {
                    'prediction': {
                        'estimatedDuration': 0,
                        'successProbability': 0,
                        'optimalTime': 'unknown',
                        'resourceRequirement': {
                            'cpu': 'low',
                            'memory': 'low',
                            'disk': 'low'
                        }
                    },
                    'analysis': {
                        'historicalDataPoints': 0,
                        'analysisTimeRange': f'{days}天',
                        'confidence': 0
                    },
                    'recommendations': ['缺乏历史数据，无法进行准确预测']
                }
            })
        
        # 1. 预计构建时长分析
        successful_builds = [b for b in historical_builds if b['result'] == 'SUCCESS']
        all_durations = [b['duration'] for b in successful_builds if b['duration'] > 0]
        
        if all_durations:
            estimated_duration = int(statistics.median(all_durations))
            duration_std = statistics.stdev(all_durations) if len(all_durations) > 1 else 0
        else:
            estimated_duration = 0
            duration_std = 0
        
        # 2. 成功概率分析
        total_builds = len(historical_builds)
        successful_count = len([b for b in historical_builds if b['result'] == 'SUCCESS'])
        success_probability = round((successful_count / total_builds) * 100, 2) if total_builds > 0 else 0
        
        # 3. 最佳构建时间分析（基于历史构建时间分布）
        build_hours = {}
        for build in historical_builds:
            build_datetime = datetime.fromtimestamp(build['timestamp'] / 1000)
            hour = build_datetime.hour
            if hour not in build_hours:
                build_hours[hour] = {'total': 0, 'successful': 0}
            build_hours[hour]['total'] += 1
            if build['result'] == 'SUCCESS':
                build_hours[hour]['successful'] += 1
        
        # 找到成功率最高且构建量适中的时间段
        optimal_hours = []
        for hour, stats in build_hours.items():
            if stats['total'] >= 3:  # 至少有3次构建的时间段
                success_rate = stats['successful'] / stats['total']
                if success_rate >= 0.8:  # 成功率80%以上
                    optimal_hours.append((hour, success_rate))
        
        if optimal_hours:
            # 按成功率排序，取最佳时间
            optimal_hours.sort(key=lambda x: x[1], reverse=True)
            best_hour = optimal_hours[0][0]
            if 6 <= best_hour <= 10:
                optimal_time = f"上午 {best_hour}:00-{best_hour+1}:00"
            elif 14 <= best_hour <= 18:
                optimal_time = f"下午 {best_hour}:00-{best_hour+1}:00"
            elif 20 <= best_hour <= 23:
                optimal_time = f"晚上 {best_hour}:00-{best_hour+1}:00"
            else:
                optimal_time = f"{best_hour}:00-{best_hour+1}:00"
        else:
            optimal_time = "14:00-16:00"  # 默认下午时段
        
        # 4. 资源需求预测（基于构建时长和系统负载）
        avg_duration = estimated_duration
        queue_length = len(queue_data.get('items', []))
        
        # 根据平均构建时长预测资源需求
        if avg_duration <= 300000:  # 5分钟以内
            cpu_requirement = 'low'
            memory_requirement = 'low'
        elif avg_duration <= 900000:  # 15分钟以内
            cpu_requirement = 'medium'
            memory_requirement = 'medium'
        else:  # 15分钟以上
            cpu_requirement = 'high'
            memory_requirement = 'high'
        
        # 根据队列长度调整磁盘需求
        if queue_length <= 2:
            disk_requirement = 'low'
        elif queue_length <= 5:
            disk_requirement = 'medium'
        else:
            disk_requirement = 'high'
        
        # 5. 分析置信度计算
        confidence = min(100, (total_builds / 10) * 100) if total_builds > 0 else 0
        
        # 6. 生成建议
        recommendations = []
        
        if success_probability < 70:
            recommendations.append(f'成功率较低({success_probability}%)，建议检查最近失败的构建原因')
        
        if duration_std > avg_duration * 0.5:
            recommendations.append('构建时长波动较大，建议优化构建稳定性')
        
        if queue_length > 5:
            recommendations.append('当前队列较长，建议错峰构建或增加构建资源')
        
        if avg_duration > 1800000:  # 30分钟以上
            recommendations.append('构建时长较长，建议优化构建流程或拆分构建任务')
        
        if not recommendations:
            recommendations.append('构建状态良好，可按预测时间进行构建')
        
        return jsonify({
            'success': True,
            'data': {
                'prediction': {
                    'estimatedDuration': estimated_duration,
                    'successProbability': success_probability,
                    'optimalTime': optimal_time,
                    'resourceRequirement': {
                        'cpu': cpu_requirement,
                        'memory': memory_requirement,
                        'disk': disk_requirement
                    }
                },
                'analysis': {
                    'historicalDataPoints': total_builds,
                    'analysisTimeRange': f'{days}天',
                    'confidence': round(confidence, 1),
                    'durationVariance': round(duration_std / 1000, 1) if duration_std > 0 else 0,
                    'currentQueueLength': queue_length
                },
                'recommendations': recommendations,
                'timestamp': int(time.time() * 1000)
            }
        })
        
    except Exception as e:
        logger.error(f"构建预测分析失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/failure-analysis/<int:instance_id>', methods=['GET'])
@login_required
@security_audit('jenkins_failure_analysis_access')
@validate_input_security()
@monitor_performance('jenkins_failure_analysis')
@cached(ttl=600, key_prefix='failure_')  # 缓存10分钟，失败分析数据相对稳定
@enhanced_rate_limit(max_requests=20, window_seconds=60)  # 每分钟最多20次请求
def get_failure_analysis(instance_id):
    """获取失败模式识别和分析"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取查询参数
        job_name = request.args.get('job_name')  # 特定任务分析
        days = int(request.args.get('days', 7))  # 分析最近几天的失败构建
        limit = int(request.args.get('limit', 20))  # 最多分析的失败构建数量
        
        # 获取Jenkins失败构建数据
        if job_name:
            jobs_url = f"{instance['url']}/job/{job_name}/api/json?tree=builds[number,timestamp,result,duration,actions[causes[shortDescription]]]"
        else:
            jobs_url = f"{instance['url']}/api/json?tree=jobs[name,builds[number,timestamp,result,duration,actions[causes[shortDescription]]]]"
        
        response = requests.get(
            jobs_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=20
        )
        
        if response.status_code != 200:
            return jsonify({'success': False, 'message': 'Jenkins API调用失败'})
        
        jobs_data = response.json()
        
        # 计算时间范围
        end_time = int(time.time() * 1000)
        start_time = end_time - (days * 24 * 60 * 60 * 1000)
        
        # 收集失败构建数据
        failed_builds = []
        
        if job_name:
            # 单个任务分析
            builds = jobs_data.get('builds', [])
            for build in builds[:limit]:
                if (build.get('timestamp', 0) >= start_time and 
                    build.get('result') in ['FAILURE', 'ABORTED', 'UNSTABLE']):
                    failed_builds.append({
                        'jobName': job_name,
                        'buildNumber': build.get('number'),
                        'timestamp': build.get('timestamp', 0),
                        'result': build.get('result'),
                        'duration': build.get('duration', 0),
                        'causes': [cause.get('shortDescription', '') for action in build.get('actions', []) for cause in action.get('causes', [])]
                    })
        else:
            # 整体分析
            for job in jobs_data.get('jobs', []):
                job_name_current = job['name']
                builds = job.get('builds', [])
                for build in builds[:10]:  # 每个任务最多分析10个构建
                    if (build.get('timestamp', 0) >= start_time and 
                        build.get('result') in ['FAILURE', 'ABORTED', 'UNSTABLE'] and
                        len(failed_builds) < limit):
                        failed_builds.append({
                            'jobName': job_name_current,
                            'buildNumber': build.get('number'),
                            'timestamp': build.get('timestamp', 0),
                            'result': build.get('result'),
                            'duration': build.get('duration', 0),
                            'causes': [cause.get('shortDescription', '') for action in build.get('actions', []) for cause in action.get('causes', [])]
                        })
        
        if not failed_builds:
            return jsonify({
                'success': True,
                'data': {
                    'analysis': {
                        'totalFailures': 0,
                        'analysisTimeRange': f'{days}天',
                        'failurePatterns': [],
                        'commonCauses': []
                    },
                    'recommendations': ['近期无失败构建，系统运行稳定'],
                    'similarIssues': []
                }
            })
        
        # 获取失败构建的详细日志进行分析（并行获取）
        import concurrent.futures
        import re
        from collections import Counter
        
        def get_build_log(job_name, build_number):
            """获取构建日志"""
            try:
                log_url = f"{instance['url']}/job/{job_name}/{build_number}/consoleText"
                log_response = requests.get(
                    log_url,
                    auth=HTTPBasicAuth(instance['username'], jenkins_token),
                    timeout=10
                )
                return log_response.text if log_response.status_code == 200 else ""
            except:
                return ""
        
        # 并行获取构建日志（限制并发数避免过载）
        build_logs = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            log_futures = {
                executor.submit(get_build_log, build['jobName'], build['buildNumber']): build
                for build in failed_builds[:10]  # 最多分析10个构建的日志
            }
            
            for future in concurrent.futures.as_completed(log_futures):
                build = log_futures[future]
                try:
                    log_content = future.result()
                    if log_content:
                        build_logs[f"{build['jobName']}-{build['buildNumber']}"] = {
                            'build': build,
                            'log': log_content
                        }
                except Exception as e:
                    logger.warning(f"获取构建日志失败: {e}")
        
        # 1. 失败原因分类分析
        failure_patterns = {
            'compilation_error': {
                'name': '编译错误',
                'keywords': ['compilation failed', 'compile error', 'syntax error', 'cannot find symbol'],
                'count': 0,
                'examples': []
            },
            'test_failure': {
                'name': '测试失败',
                'keywords': ['test failed', 'assertion failed', 'junit', 'test.*error'],
                'count': 0,
                'examples': []
            },
            'dependency_error': {
                'name': '依赖错误',
                'keywords': ['dependency.*not found', 'package.*not found', 'module.*not found', 'import.*error'],
                'count': 0,
                'examples': []
            },
            'network_error': {
                'name': '网络错误',
                'keywords': ['connection.*timeout', 'network.*error', 'unable to connect', 'connection refused'],
                'count': 0,
                'examples': []
            },
            'permission_error': {
                'name': '权限错误',
                'keywords': ['permission denied', 'access denied', 'forbidden', 'unauthorized'],
                'count': 0,
                'examples': []
            },
            'resource_error': {
                'name': '资源不足',
                'keywords': ['out of memory', 'disk.*full', 'no space left', 'resource.*unavailable'],
                'count': 0,
                'examples': []
            },
            'timeout_error': {
                'name': '超时错误',
                'keywords': ['timeout', 'timed out', 'build.*timeout', 'execution.*timeout'],
                'count': 0,
                'examples': []
            },
            'other': {
                'name': '其他错误',
                'keywords': [],
                'count': 0,
                'examples': []
            }
        }
        
        # 分析日志内容
        for log_key, log_data in build_logs.items():
            log_content = log_data['log'].lower()
            build = log_data['build']
            
            pattern_matched = False
            for pattern_key, pattern_info in failure_patterns.items():
                if pattern_key == 'other':
                    continue
                
                for keyword in pattern_info['keywords']:
                    if re.search(keyword, log_content):
                        pattern_info['count'] += 1
                        if len(pattern_info['examples']) < 3:
                            pattern_info['examples'].append({
                                'jobName': build['jobName'],
                                'buildNumber': build['buildNumber'],
                                'timestamp': build['timestamp'],
                                'excerpt': _extract_error_context(log_content, keyword)
                            })
                        pattern_matched = True
                        break
                
                if pattern_matched:
                    break
            
            if not pattern_matched:
                failure_patterns['other']['count'] += 1
                if len(failure_patterns['other']['examples']) < 3:
                    failure_patterns['other']['examples'].append({
                        'jobName': build['jobName'],
                        'buildNumber': build['buildNumber'],
                        'timestamp': build['timestamp'],
                        'excerpt': log_content[:200] + '...' if len(log_content) > 200 else log_content
                    })
        
        # 2. 常见原因统计
        all_causes = []
        for build in failed_builds:
            all_causes.extend(build['causes'])
        
        cause_counter = Counter(all_causes)
        common_causes = [{'cause': cause, 'count': count} for cause, count in cause_counter.most_common(5)]
        
        # 3. 解决方案推荐
        recommendations = []
        
        # 根据失败模式生成建议
        for pattern_key, pattern_info in failure_patterns.items():
            if pattern_info['count'] > 0:
                if pattern_key == 'compilation_error':
                    recommendations.append({
                        'type': '编译错误解决方案',
                        'priority': 'high',
                        'suggestion': '检查代码语法，确保所有依赖项已正确导入，运行本地编译测试'
                    })
                elif pattern_key == 'test_failure':
                    recommendations.append({
                        'type': '测试失败解决方案',
                        'priority': 'high',
                        'suggestion': '检查测试用例逻辑，确保测试环境配置正确，更新测试数据'
                    })
                elif pattern_key == 'dependency_error':
                    recommendations.append({
                        'type': '依赖错误解决方案',
                        'priority': 'medium',
                        'suggestion': '检查依赖项版本，更新依赖管理文件，清理并重新下载依赖'
                    })
                elif pattern_key == 'network_error':
                    recommendations.append({
                        'type': '网络错误解决方案',
                        'priority': 'medium',
                        'suggestion': '检查网络连接，配置代理设置，增加重试机制'
                    })
                elif pattern_key == 'permission_error':
                    recommendations.append({
                        'type': '权限错误解决方案',
                        'priority': 'high',
                        'suggestion': '检查文件和目录权限，确保Jenkins用户有足够的访问权限'
                    })
                elif pattern_key == 'resource_error':
                    recommendations.append({
                        'type': '资源不足解决方案',
                        'priority': 'high',
                        'suggestion': '增加系统资源（内存/磁盘），优化构建过程，清理临时文件'
                    })
                elif pattern_key == 'timeout_error':
                    recommendations.append({
                        'type': '超时错误解决方案',
                        'priority': 'medium',
                        'suggestion': '增加构建超时时间，优化构建性能，分解长时间运行的任务'
                    })
        
        # 4. 相似问题检索
        similar_issues = []
        
        # 基于失败模式找出相似的历史问题
        for pattern_key, pattern_info in failure_patterns.items():
            if pattern_info['count'] > 1 and pattern_info['examples']:
                similar_issues.append({
                    'pattern': pattern_info['name'],
                    'frequency': pattern_info['count'],
                    'recentExamples': pattern_info['examples'][:2],
                    'recommendation': f'该问题在{days}天内出现{pattern_info["count"]}次，建议重点关注'
                })
        
        # 过滤空的推荐
        filtered_patterns = {k: v for k, v in failure_patterns.items() if v['count'] > 0}
        
        return jsonify({
            'success': True,
            'data': {
                'analysis': {
                    'totalFailures': len(failed_builds),
                    'analysisTimeRange': f'{days}天',
                    'failurePatterns': filtered_patterns,
                    'commonCauses': common_causes,
                    'logAnalysisCount': len(build_logs)
                },
                'recommendations': recommendations,
                'similarIssues': similar_issues,
                'timestamp': int(time.time() * 1000)
            }
        })
        
    except Exception as e:
        logger.error(f"失败模式分析失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/optimization-recommendations/<int:instance_id>', methods=['GET'])
@login_required
@monitor_performance('jenkins_optimization_recommendations')
@cached(ttl=900, key_prefix='optimization_')  # 缓存15分钟，优化建议数据更稳定
@rate_limit(max_requests=15, window_seconds=60)  # 每分钟最多15次请求
def get_optimization_recommendations(instance_id):
    """获取性能优化建议"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 获取查询参数
        days = int(request.args.get('days', 30))  # 分析历史数据的天数
        
        # 获取Jenkins系统数据和构建历史
        system_url = f"{instance['url']}/api/json"
        jobs_url = f"{instance['url']}/api/json?tree=jobs[name,builds[number,timestamp,result,duration,estimatedDuration]]"
        queue_url = f"{instance['url']}/queue/api/json"
        
        # 并行请求多个API
        import concurrent.futures
        import statistics
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        def fetch_url(url):
            return requests.get(
                url,
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=20
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            system_future = executor.submit(fetch_url, system_url)
            jobs_future = executor.submit(fetch_url, jobs_url)
            queue_future = executor.submit(fetch_url, queue_url)
            
            system_response = system_future.result()
            jobs_response = jobs_future.result()
            queue_response = queue_future.result()
        
        if not all(r.status_code == 200 for r in [system_response, jobs_response, queue_response]):
            return jsonify({'success': False, 'message': 'Jenkins API调用失败'})
        
        system_data = system_response.json()
        jobs_data = jobs_response.json()
        queue_data = queue_response.json()
        
        # 计算时间范围
        end_time = int(time.time() * 1000)
        start_time = end_time - (days * 24 * 60 * 60 * 1000)
        
        # 收集历史构建数据
        historical_builds = []
        job_build_stats = defaultdict(list)
        
        for job in jobs_data.get('jobs', []):
            job_name = job['name']
            builds = job.get('builds', [])
            
            for build in builds:
                if build.get('timestamp', 0) >= start_time:
                    build_data = {
                        'jobName': job_name,
                        'timestamp': build.get('timestamp', 0),
                        'result': build.get('result', 'unknown'),
                        'duration': build.get('duration', 0),
                        'estimatedDuration': build.get('estimatedDuration', 0)
                    }
                    historical_builds.append(build_data)
                    job_build_stats[job_name].append(build_data)
        
        if not historical_builds:
            return jsonify({
                'success': True,
                'data': {
                    'optimizations': {
                        'timeOptimization': [],
                        'parallelOptimization': [],
                        'resourceOptimization': []
                    },
                    'analysis': {
                        'analysisTimeRange': f'{days}天',
                        'totalBuilds': 0,
                        'confidence': 0
                    },
                    'recommendations': ['缺乏历史数据，无法提供优化建议']
                }
            })
        
        # 1. 构建时机优化分析
        time_analysis = defaultdict(lambda: {'builds': 0, 'total_duration': 0, 'success_count': 0, 'avg_duration': 0, 'success_rate': 0})
        
        for build in historical_builds:
            build_datetime = datetime.fromtimestamp(build['timestamp'] / 1000)
            hour = build_datetime.hour
            
            time_analysis[hour]['builds'] += 1
            time_analysis[hour]['total_duration'] += build['duration']
            if build['result'] == 'SUCCESS':
                time_analysis[hour]['success_count'] += 1
        
        # 计算每个小时的统计数据
        for hour in time_analysis:
            stats = time_analysis[hour]
            stats['avg_duration'] = stats['total_duration'] / stats['builds'] if stats['builds'] > 0 else 0
            stats['success_rate'] = (stats['success_count'] / stats['builds']) * 100 if stats['builds'] > 0 else 0
        
        # 找出最佳构建时间段
        optimal_hours = []
        for hour, stats in time_analysis.items():
            if stats['builds'] >= 3:  # 至少有3次构建的时间段
                # 综合考虑成功率和平均构建时长
                score = stats['success_rate'] * 0.7 + (100 - min(stats['avg_duration'] / 600000, 100)) * 0.3
                optimal_hours.append({
                    'hour': hour,
                    'score': score,
                    'builds': stats['builds'],
                    'success_rate': round(stats['success_rate'], 1),
                    'avg_duration': round(stats['avg_duration'] / 1000, 1)
                })
        
        optimal_hours.sort(key=lambda x: x['score'], reverse=True)
        
        time_recommendations = []
        if optimal_hours:
            best_times = optimal_hours[:3]  # 推荐前3个最佳时间段
            for time_slot in best_times:
                hour = time_slot['hour']
                if 6 <= hour <= 10:
                    period = "上午"
                elif 14 <= hour <= 18:
                    period = "下午"
                elif 20 <= hour <= 23:
                    period = "晚上"
                else:
                    period = "深夜/凌晨"
                
                time_recommendations.append({
                    'timeSlot': f"{period} {hour}:00-{hour+1}:00",
                    'score': round(time_slot['score'], 1),
                    'reason': f"成功率{time_slot['success_rate']}%，平均时长{time_slot['avg_duration']}秒",
                    'recommendation': f"建议在{period}时段进行构建，历史表现良好"
                })
        
        # 2. 并行构建建议分析
        parallel_analysis = []
        
        # 分析任务的构建时长分布
        job_durations = {}
        job_dependencies = {}
        
        for job_name, builds in job_build_stats.items():
            successful_builds = [b for b in builds if b['result'] == 'SUCCESS' and b['duration'] > 0]
            if successful_builds:
                durations = [b['duration'] for b in successful_builds]
                job_durations[job_name] = {
                    'avg_duration': statistics.mean(durations),
                    'median_duration': statistics.median(durations),
                    'std_duration': statistics.stdev(durations) if len(durations) > 1 else 0,
                    'build_count': len(successful_builds)
                }
        
        # 根据构建时长分组推荐并行策略
        short_jobs = []  # 短时间任务 (< 5分钟)
        medium_jobs = []  # 中等时间任务 (5-15分钟)
        long_jobs = []   # 长时间任务 (> 15分钟)
        
        for job_name, stats in job_durations.items():
            if stats['avg_duration'] < 300000:  # 5分钟
                short_jobs.append({'name': job_name, 'duration': stats['avg_duration']})
            elif stats['avg_duration'] < 900000:  # 15分钟
                medium_jobs.append({'name': job_name, 'duration': stats['avg_duration']})
            else:
                long_jobs.append({'name': job_name, 'duration': stats['avg_duration']})
        
        if len(short_jobs) > 3:
            parallel_analysis.append({
                'type': '短任务并行组',
                'jobs': [job['name'] for job in short_jobs[:5]],
                'recommendation': f'这{len(short_jobs)}个短时间任务可以并行执行，预计能节省60%的总时间',
                'estimated_savings': '60%'
            })
        
        if len(medium_jobs) > 2:
            parallel_analysis.append({
                'type': '中等任务并行组',
                'jobs': [job['name'] for job in medium_jobs[:3]],
                'recommendation': f'这{len(medium_jobs)}个中等时间任务可以分批并行，建议2-3个一组',
                'estimated_savings': '40%'
            })
        
        if len(long_jobs) > 0:
            parallel_analysis.append({
                'type': '长任务优化建议',
                'jobs': [job['name'] for job in long_jobs],
                'recommendation': '这些长时间任务建议单独执行，或考虑拆分为更小的子任务',
                'estimated_savings': '20%'
            })
        
        # 3. 资源配置优化分析
        resource_analysis = []
        
        # 分析构建效率（实际时长 vs 预计时长）
        efficiency_issues = []
        for job_name, builds in job_build_stats.items():
            actual_durations = []
            estimated_durations = []
            
            for build in builds:
                if build['result'] == 'SUCCESS' and build['duration'] > 0 and build['estimatedDuration'] > 0:
                    actual_durations.append(build['duration'])
                    estimated_durations.append(build['estimatedDuration'])
            
            if len(actual_durations) >= 3:
                avg_actual = statistics.mean(actual_durations)
                avg_estimated = statistics.mean(estimated_durations)
                efficiency_ratio = avg_actual / avg_estimated if avg_estimated > 0 else 1
                
                if efficiency_ratio > 1.5:  # 实际时长比预计时长长50%以上
                    efficiency_issues.append({
                        'jobName': job_name,
                        'efficiency_ratio': round(efficiency_ratio, 2),
                        'avg_actual': round(avg_actual / 1000, 1),
                        'avg_estimated': round(avg_estimated / 1000, 1)
                    })
        
        # 资源配置建议
        current_queue_length = len(queue_data.get('items', []))
        
        if efficiency_issues:
            resource_analysis.append({
                'type': '构建效率优化',
                'issues': efficiency_issues[:5],
                'recommendation': '这些任务的实际构建时间显著超过预期，建议增加构建资源或优化构建脚本'
            })
        
        if current_queue_length > 5:
            resource_analysis.append({
                'type': '构建资源扩容',
                'current_queue': current_queue_length,
                'recommendation': '当前构建队列较长，建议增加构建节点或优化资源分配'
            })
        
        # 基于历史数据的资源建议
        peak_hours = [hour for hour, stats in time_analysis.items() if stats['builds'] > statistics.mean([s['builds'] for s in time_analysis.values()])]
        if peak_hours:
            resource_analysis.append({
                'type': '峰值时段资源规划',
                'peak_hours': peak_hours,
                'recommendation': f'在{len(peak_hours)}个高峰时段({", ".join([str(h) for h in peak_hours[:5]])}点)建议预留更多构建资源'
            })
        
        # 计算分析置信度
        total_builds = len(historical_builds)
        confidence = min(100, (total_builds / 50) * 100) if total_builds > 0 else 0
        
        # 生成综合建议
        recommendations = []
        
        if time_recommendations:
            recommendations.append(f'建议在{time_recommendations[0]["timeSlot"]}进行构建，历史成功率最高')
        
        if parallel_analysis:
            total_jobs = len(short_jobs) + len(medium_jobs) + len(long_jobs)
            recommendations.append(f'发现{total_jobs}个任务可通过并行优化，预计可节省构建时间')
        
        if resource_analysis:
            recommendations.append('检测到资源配置优化机会，建议根据分析结果调整构建资源')
        
        if efficiency_issues:
            recommendations.append(f'{len(efficiency_issues)}个任务存在效率问题，建议优先处理')
        
        if not recommendations:
            recommendations.append('当前构建配置较为合理，继续监控性能指标')
        
        return jsonify({
            'success': True,
            'data': {
                'optimizations': {
                    'timeOptimization': time_recommendations,
                    'parallelOptimization': parallel_analysis,
                    'resourceOptimization': resource_analysis
                },
                'analysis': {
                    'analysisTimeRange': f'{days}天',
                    'totalBuilds': total_builds,
                    'totalJobs': len(job_build_stats),
                    'confidence': round(confidence, 1),
                    'peakHours': peak_hours[:5] if peak_hours else [],
                    'currentQueueLength': current_queue_length
                },
                'recommendations': recommendations,
                'timestamp': int(time.time() * 1000)
            }
        })
        
    except Exception as e:
        logger.error(f"性能优化建议分析失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

def _extract_error_context(log_content, keyword, context_lines=2):
    """从日志中提取错误上下文"""
    lines = log_content.split('\n')
    for i, line in enumerate(lines):
        if re.search(keyword, line.lower()):
            # 提取错误行及前后几行作为上下文
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            context = '\n'.join(lines[start:end])
            return context[:300] + '...' if len(context) > 300 else context
    return ""

# ==================== Phase 5: 性能监控和系统优化 ====================

@bp.route('/performance/metrics', methods=['GET'])
@login_required
@monitor_performance('performance_metrics')
def get_performance_metrics():
    """获取系统性能指标"""
    try:
        # 获取性能监控指标
        performance_metrics = performance_monitor.get_metrics()
        
        # 获取缓存统计
        cache_stats = simple_cache.get_stats()
        
        # 获取限流统计 (示例数据，实际环境中应该从真实的限流器获取)
        rate_limit_stats = {
            'total_requests': sum(performance_metrics.get('overall', {}).get('total_requests', 0) for _ in [1]),
            'blocked_requests': 0,  # 需要从实际的限流器获取
            'current_limits': {
                'jenkins_prediction': rate_limiter.get_stats('jenkins_prediction_global'),
                'jenkins_failure': rate_limiter.get_stats('jenkins_failure_global'),
            }
        }
        
        # 系统资源统计
        import psutil
        import os
        
        system_stats = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'process_count': len(psutil.pids()),
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
        
        return jsonify({
            'success': True,
            'data': {
                'performance': performance_metrics,
                'cache': cache_stats,
                'rate_limit': rate_limit_stats,
                'system': system_stats,
                'timestamp': int(time.time() * 1000)
            }
        })
        
    except Exception as e:
        logger.error(f"获取性能指标失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/performance/cache/clear', methods=['POST'])
@login_required
@monitor_performance('performance_cache_clear')
def clear_performance_cache():
    """清空系统缓存"""
    try:
        # 清空所有缓存
        simple_cache.clear()
        
        logger.info("系统缓存已清空")
        return jsonify({
            'success': True,
            'message': '缓存清空成功',
            'timestamp': int(time.time() * 1000)
        })
        
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/performance/health', methods=['GET'])
@login_required
@monitor_performance('performance_health_check')
def get_system_health():
    """获取系统健康状态"""
    try:
        import psutil
        
        # 检查系统资源使用情况
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 健康状态评估
        health_status = 'healthy'
        warnings = []
        
        if cpu_percent > 80:
            health_status = 'warning'
            warnings.append(f'CPU使用率过高: {cpu_percent}%')
        
        if memory.percent > 85:
            health_status = 'critical' if memory.percent > 95 else 'warning'
            warnings.append(f'内存使用率过高: {memory.percent}%')
        
        if disk.percent > 90:
            health_status = 'critical' if disk.percent > 95 else 'warning'
            warnings.append(f'磁盘使用率过高: {disk.percent}%')
        
        # 检查性能指标
        perf_metrics = performance_monitor.get_metrics()
        overall_stats = perf_metrics.get('overall', {})
        
        if overall_stats.get('overall_error_rate', 0) > 10:
            health_status = 'warning'
            warnings.append(f'API错误率过高: {overall_stats["overall_error_rate"]}%')
        
        if overall_stats.get('avg_response_time', 0) > 5:
            health_status = 'warning'
            warnings.append(f'平均响应时间过长: {overall_stats["avg_response_time"]}秒')
        
        # 获取慢查询数量
        slow_queries_count = overall_stats.get('slow_queries_count', 0)
        if slow_queries_count > 5:
            health_status = 'warning'
            warnings.append(f'慢查询过多: {slow_queries_count}个')
        
        return jsonify({
            'success': True,
            'data': {
                'status': health_status,
                'warnings': warnings,
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'error_rate': overall_stats.get('overall_error_rate', 0),
                    'avg_response_time': overall_stats.get('avg_response_time', 0),
                    'slow_queries_count': slow_queries_count
                },
                'recommendations': _generate_performance_recommendations(health_status, warnings),
                'timestamp': int(time.time() * 1000)
            }
        })
        
    except Exception as e:
        logger.error(f"获取系统健康状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

def _generate_performance_recommendations(health_status, warnings):
    """生成性能优化建议"""
    recommendations = []
    
    if health_status == 'critical':
        recommendations.append('系统资源严重不足，建议立即扩容或优化')
    elif health_status == 'warning':
        recommendations.append('系统存在性能警告，建议关注资源使用情况')
    
    for warning in warnings:
        if 'CPU' in warning:
            recommendations.append('建议优化CPU密集型操作，或增加CPU核心数')
        elif '内存' in warning:
            recommendations.append('建议优化内存使用，清理缓存或增加内存容量')
        elif '磁盘' in warning:
            recommendations.append('建议清理磁盘空间或增加存储容量')
        elif '错误率' in warning:
            recommendations.append('建议检查应用日志，修复导致错误的问题')
        elif '响应时间' in warning:
            recommendations.append('建议优化数据库查询和API响应速度')
        elif '慢查询' in warning:
            recommendations.append('建议优化数据库索引和查询语句')
    
    if not recommendations:
        recommendations.append('系统运行正常，继续保持监控')
    
    return recommendations

@bp.route('/performance/database', methods=['GET'])
@login_required
@monitor_performance('performance_database_metrics')
def get_database_performance():
    """获取数据库性能指标"""
    try:
        from app.utils.db_context import get_database_performance_report
        
        # 获取数据库性能报告
        performance_report = get_database_performance_report()
        
        return jsonify({
            'success': True,
            'data': performance_report
        })
        
    except Exception as e:
        logger.error(f"获取数据库性能指标失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/security/status', methods=['GET'])
@login_required
@security_audit('security_status_access')
@monitor_performance('security_status_check')
def get_security_status():
    """获取系统安全状态"""
    try:
        # 获取安全健康检查结果
        security_status = SecurityHealthChecker.check_security_status()
        
        # 获取最近的安全事件统计
        recent_events = security_auditor.get_security_summary(hours=1)
        
        return jsonify({
            'success': True,
            'data': {
                'security_health': security_status,
                'recent_activity': recent_events,
                'blocked_ips_count': len(api_security_manager.blocked_ips),
                'timestamp': int(time.time() * 1000)
            }
        })
        
    except Exception as e:
        logger.error(f"获取安全状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/security/events', methods=['GET'])
@login_required
@security_audit('security_events_access')
@monitor_performance('security_events_query')
def get_security_events():
    """获取安全事件列表"""
    try:
        hours = int(request.args.get('hours', 24))
        event_type = request.args.get('event_type')
        
        # 获取安全事件摘要
        events_summary = security_auditor.get_security_summary(hours)
        
        # 如果指定了事件类型，过滤事件
        if event_type:
            filtered_events = [
                event for event in events_summary['recent_events'] 
                if event['event_type'] == event_type
            ]
            events_summary['recent_events'] = filtered_events
        
        return jsonify({
            'success': True,
            'data': events_summary
        })
        
    except Exception as e:
        logger.error(f"获取安全事件失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/security/ip/unblock', methods=['POST'])
@login_required
@security_audit('security_ip_unblock')
@validate_input_security()
def unblock_ip():
    """解除IP阻止"""
    try:
        data = request.get_json()
        if not data or 'ip_address' not in data:
            return jsonify({
                'success': False,
                'message': '缺少IP地址参数'
            }), 400
        
        ip_address = data['ip_address']
        
        # 验证IP地址格式
        from app.utils.security_enhancement import InputValidator
        if not InputValidator.validate_ip_address(ip_address):
            return jsonify({
                'success': False,
                'message': '无效的IP地址格式'
            }), 400
        
        # 从阻止列表中移除IP
        if ip_address in api_security_manager.blocked_ips:
            api_security_manager.blocked_ips.remove(ip_address)
            
            # 记录解除阻止事件
            security_auditor.log_security_event(
                'ip_unblocked',
                user_id=getattr(g, 'current_user_id', None),
                ip_address=request.remote_addr,
                details={
                    'unblocked_ip': ip_address,
                    'reason': data.get('reason', 'manual_unblock')
                }
            )
            
            return jsonify({
                'success': True,
                'message': f'IP地址 {ip_address} 已解除阻止'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'IP地址未在阻止列表中'
            }), 404
            
    except Exception as e:
        logger.error(f"解除IP阻止失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# 数据加密强化API端点
@bp.route('/encryption/encrypt', methods=['POST'])
@login_required
@security_audit('data_encryption')
@validate_input_security()
@mask_sensitive_logs()
def encrypt_data():
    """加密敏感数据"""
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'message': '缺少要加密的数据'
            }), 400
        
        sensitive_data = data['data']
        key_id = data.get('key_id', 'default')
        
        # 加密数据
        encrypted_info = encryption_manager.encrypt_sensitive_data(
            sensitive_data, 
            key_id=key_id
        )
        
        # 记录加密事件
        security_auditor.log_security_event(
            'data_encrypted',
            user_id=getattr(g, 'current_user_id', None),
            ip_address=request.remote_addr,
            details={
                'key_id': key_id,
                'data_type': type(sensitive_data).__name__
            }
        )
        
        return jsonify({
            'success': True,
            'data': encrypted_info,
            'message': '数据加密成功'
        })
        
    except Exception as e:
        logger.error(f"数据加密失败: {e}")
        return jsonify({'success': False, 'message': '数据加密失败'}), 500

@bp.route('/encryption/decrypt', methods=['POST'])
@login_required
@security_audit('data_decryption')
@validate_input_security()
@mask_sensitive_logs()
def decrypt_data():
    """解密敏感数据"""
    try:
        data = request.get_json()
        if not data or 'encryption_info' not in data:
            return jsonify({
                'success': False,
                'message': '缺少加密信息'
            }), 400
        
        encryption_info = data['encryption_info']
        
        # 解密数据
        decrypted_data = encryption_manager.decrypt_sensitive_data(encryption_info)
        
        # 记录解密事件
        security_auditor.log_security_event(
            'data_decrypted',
            user_id=getattr(g, 'current_user_id', None),
            ip_address=request.remote_addr,
            details={
                'key_id': encryption_info.get('key_id', 'unknown'),
                'algorithm': encryption_info.get('algorithm', 'unknown')
            }
        )
        
        return jsonify({
            'success': True,
            'data': decrypted_data,
            'message': '数据解密成功'
        })
        
    except Exception as e:
        logger.error(f"数据解密失败: {e}")
        return jsonify({'success': False, 'message': '数据解密失败'}), 500

@bp.route('/encryption/token/generate', methods=['POST'])
@login_required
@security_audit('token_generation')
@validate_input_security()
def generate_secure_token():
    """生成安全令牌"""
    try:
        data = request.get_json() or {}
        user_id = getattr(g, 'current_user_id', None)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户身份验证失败'
            }), 401
        
        expires_in = data.get('expires_in', 3600)  # 默认1小时
        permissions = data.get('permissions', [])
        
        # 生成安全令牌
        token_info = token_manager.generate_secure_token(
            user_id=str(user_id),
            expires_in=expires_in,
            permissions=permissions
        )
        
        # 记录令牌生成事件
        security_auditor.log_security_event(
            'secure_token_generated',
            user_id=user_id,
            ip_address=request.remote_addr,
            details={
                'token_id': token_info['token_id'],
                'expires_in': expires_in,
                'permissions': permissions
            }
        )
        
        return jsonify({
            'success': True,
            'data': token_info,
            'message': '安全令牌生成成功'
        })
        
    except Exception as e:
        logger.error(f"生成安全令牌失败: {e}")
        return jsonify({'success': False, 'message': '令牌生成失败'}), 500

@bp.route('/encryption/token/validate', methods=['POST'])
@security_audit('token_validation')
@validate_input_security()
def validate_secure_token():
    """验证安全令牌"""
    try:
        data = request.get_json()
        if not data or 'token' not in data:
            return jsonify({
                'success': False,
                'message': '缺少令牌参数'
            }), 400
        
        token = data['token']
        
        # 验证令牌
        token_info = token_manager.validate_token(token)
        
        if token_info:
            # 记录令牌验证成功事件
            security_auditor.log_security_event(
                'token_validation_success',
                user_id=token_info.get('user_id'),
                ip_address=request.remote_addr,
                details={
                    'token_id': token_info.get('token_id'),
                    'permissions': token_info.get('permissions', [])
                }
            )
            
            return jsonify({
                'success': True,
                'valid': True,
                'data': {
                    'user_id': token_info['user_id'],
                    'expires_at': token_info['expires_at'],
                    'permissions': token_info.get('permissions', [])
                },
                'message': '令牌验证成功'
            })
        else:
            # 记录令牌验证失败事件
            security_auditor.log_security_event(
                'token_validation_failed',
                ip_address=request.remote_addr,
                details={'reason': 'invalid_token'}
            )
            
            return jsonify({
                'success': True,
                'valid': False,
                'message': '令牌无效或已过期'
            })
        
    except Exception as e:
        logger.error(f"验证安全令牌失败: {e}")
        return jsonify({'success': False, 'message': '令牌验证失败'}), 500

@bp.route('/encryption/token/revoke', methods=['POST'])
@login_required
@security_audit('token_revocation')
@validate_input_security()
def revoke_secure_token():
    """撤销安全令牌"""
    try:
        data = request.get_json()
        if not data or 'token_id' not in data:
            return jsonify({
                'success': False,
                'message': '缺少令牌ID参数'
            }), 400
        
        token_id = data['token_id']
        
        # 撤销令牌
        token_manager.revoke_token(token_id)
        
        # 记录令牌撤销事件
        security_auditor.log_security_event(
            'token_revoked',
            user_id=getattr(g, 'current_user_id', None),
            ip_address=request.remote_addr,
            details={
                'revoked_token_id': token_id,
                'reason': data.get('reason', 'manual_revocation')
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'令牌 {token_id} 已撤销'
        })
        
    except Exception as e:
        logger.error(f"撤销安全令牌失败: {e}")
        return jsonify({'success': False, 'message': '令牌撤销失败'}), 500

@bp.route('/encryption/mask', methods=['POST'])
@login_required
@security_audit('data_masking')
@validate_input_security()
def mask_sensitive_data():
    """脱敏敏感数据"""
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'message': '缺少要脱敏的数据'
            }), 400
        
        sensitive_data = data['data']
        sensitive_fields = data.get('sensitive_fields', None)
        
        if not isinstance(sensitive_data, dict):
            return jsonify({
                'success': False,
                'message': '数据必须是字典格式'
            }), 400
        
        # 脱敏数据
        masked_data = data_masking.mask_sensitive_data(
            sensitive_data, 
            sensitive_fields=sensitive_fields
        )
        
        # 记录脱敏事件
        security_auditor.log_security_event(
            'data_masked',
            user_id=getattr(g, 'current_user_id', None),
            ip_address=request.remote_addr,
            details={
                'field_count': len(sensitive_data),
                'masked_fields': sensitive_fields or 'auto_detected'
            }
        )
        
        return jsonify({
            'success': True,
            'data': masked_data,
            'message': '数据脱敏成功'
        })
        
    except Exception as e:
        logger.error(f"数据脱敏失败: {e}")
        return jsonify({'success': False, 'message': '数据脱敏失败'}), 500

@bp.route('/encryption/ssl/keypair', methods=['POST'])
@login_required
@security_audit('ssl_keypair_generation')
@validate_input_security()
def generate_ssl_keypair():
    """生成SSL密钥对"""
    try:
        data = request.get_json() or {}
        key_size = data.get('key_size', 2048)
        
        if key_size not in [1024, 2048, 4096]:
            return jsonify({
                'success': False,
                'message': '不支持的密钥长度'
            }), 400
        
        from app.utils.encryption import ssl_manager
        
        # 生成密钥对
        keypair = ssl_manager.generate_rsa_keypair(key_size=key_size)
        
        # 记录密钥对生成事件
        security_auditor.log_security_event(
            'ssl_keypair_generated',
            user_id=getattr(g, 'current_user_id', None),
            ip_address=request.remote_addr,
            details={
                'key_size': key_size,
                'algorithm': 'RSA'
            }
        )
        
        return jsonify({
            'success': True,
            'data': {
                'private_key': keypair['private_key'].decode(),
                'public_key': keypair['public_key'].decode(),
                'key_size': key_size
            },
            'message': 'SSL密钥对生成成功'
        })
        
    except Exception as e:
        logger.error(f"生成SSL密钥对失败: {e}")
        return jsonify({'success': False, 'message': 'SSL密钥对生成失败'}), 500

@bp.route('/encryption/status', methods=['GET'])
@login_required
@security_audit('encryption_status_check')
@validate_input_security()
def get_encryption_status():
    """获取加密系统状态"""
    try:
        # 获取令牌管理器状态
        active_tokens_count = len(token_manager.active_tokens)
        revoked_tokens_count = len(token_manager.revoked_tokens)
        
        # 清理过期令牌
        token_manager.cleanup_expired_tokens()
        
        status = {
            'encryption_manager': {
                'status': 'active',
                'algorithm': 'Fernet',
                'key_cache_size': len(encryption_manager.key_cache)
            },
            'token_manager': {
                'status': 'active',
                'active_tokens': active_tokens_count,
                'revoked_tokens': revoked_tokens_count
            },
            'data_masking': {
                'status': 'active',
                'supported_fields': [
                    'password', 'token', 'email', 'phone', 
                    'ip_address', 'api_key', 'secret'
                ]
            },
            'ssl_manager': {
                'status': 'active',
                'supported_key_sizes': [1024, 2048, 4096]
            },
            'system_info': {
                'encryption_enabled': True,
                'last_updated': datetime.now().isoformat()
            }
        }
        
        return jsonify({
            'success': True,
            'data': status,
            'message': '加密系统状态获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取加密系统状态失败: {e}")
        return jsonify({'success': False, 'message': '获取状态失败'}), 500

# 权限控制完善API端点
@bp.route('/permission/roles', methods=['GET'])
@login_required
@require_read(ResourceType.USER)
@security_audit('permission_roles_query')
@validate_input_security()
def get_all_roles():
    """获取所有角色信息"""
    try:
        roles = permission_manager.get_all_roles()
        
        return jsonify({
            'success': True,
            'data': {
                'roles': roles,
                'total_count': len(roles)
            },
            'message': '角色信息获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取角色信息失败: {e}")
        return jsonify({'success': False, 'message': '获取角色信息失败'}), 500

@bp.route('/permission/roles', methods=['POST'])
@login_required
@require_admin(ResourceType.USER)
@security_audit('permission_role_creation')
@validate_input_security()
def create_custom_role():
    """创建自定义角色"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'permissions' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: name, permissions'
            }), 400
        
        role_name = data['name']
        description = data.get('description', '')
        permissions = data['permissions']
        
        # 验证权限格式
        required_fields = ['resource_type', 'level']
        for perm in permissions:
            for field in required_fields:
                if field not in perm:
                    return jsonify({
                        'success': False,
                        'message': f'权限配置缺少字段: {field}'
                    }), 400
        
        # 创建角色
        success = permission_manager.create_custom_role(role_name, description, permissions)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'角色 {role_name} 创建成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '角色创建失败，可能已存在'
            }), 400
        
    except Exception as e:
        logger.error(f"创建自定义角色失败: {e}")
        return jsonify({'success': False, 'message': '创建角色失败'}), 500

@bp.route('/permission/users/<user_id>/roles', methods=['GET'])
@login_required
@require_read(ResourceType.USER, '<user_id>')
@security_audit('permission_user_roles_query')
@validate_input_security()
def get_user_roles(user_id):
    """获取用户角色"""
    try:
        user_permissions = permission_manager.get_user_permissions(user_id)
        
        return jsonify({
            'success': True,
            'data': user_permissions,
            'message': f'用户 {user_id} 权限信息获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取用户角色失败: {e}")
        return jsonify({'success': False, 'message': '获取用户角色失败'}), 500

@bp.route('/permission/users/<user_id>/roles', methods=['POST'])
@login_required
@require_admin(ResourceType.USER, '<user_id>')
@security_audit('permission_role_assignment')
@validate_input_security()
def assign_user_role(user_id):
    """分配用户角色"""
    try:
        data = request.get_json()
        if not data or 'role' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: role'
            }), 400
        
        role_name = data['role']
        
        success = permission_manager.assign_role_to_user(user_id, role_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'角色 {role_name} 已分配给用户 {user_id}'
            })
        else:
            return jsonify({
                'success': False,
                'message': '角色分配失败，角色不存在或用户已有该角色'
            }), 400
        
    except Exception as e:
        logger.error(f"分配用户角色失败: {e}")
        return jsonify({'success': False, 'message': '分配角色失败'}), 500

@bp.route('/permission/users/<user_id>/roles/<role_name>', methods=['DELETE'])
@login_required
@require_admin(ResourceType.USER, '<user_id>')
@security_audit('permission_role_removal')
@validate_input_security()
def remove_user_role(user_id, role_name):
    """移除用户角色"""
    try:
        success = permission_manager.remove_role_from_user(user_id, role_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'已移除用户 {user_id} 的角色 {role_name}'
            })
        else:
            return jsonify({
                'success': False,
                'message': '角色移除失败，用户可能没有该角色'
            }), 400
        
    except Exception as e:
        logger.error(f"移除用户角色失败: {e}")
        return jsonify({'success': False, 'message': '移除角色失败'}), 500

@bp.route('/permission/current-user', methods=['GET'])
@login_required
@security_audit('permission_current_user_query')
@validate_input_security()
def get_current_user_permission():
    """获取当前用户权限信息"""
    try:
        permissions = get_current_user_permissions()
        
        if not permissions:
            return jsonify({
                'success': False,
                'message': '无法获取用户权限信息'
            }), 401
        
        return jsonify({
            'success': True,
            'data': permissions,
            'message': '当前用户权限信息获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取当前用户权限失败: {e}")
        return jsonify({'success': False, 'message': '获取权限信息失败'}), 500

# 异常处理机制API端点
@bp.route('/error/statistics', methods=['GET'])
@login_required
@require_admin(ResourceType.SYSTEM)
@security_audit('error_statistics_query')
@validate_input_security()
@safe_execute()
def get_error_statistics():
    """获取错误统计信息"""
    hours = request.args.get('hours', type=int, default=24)
    
    if hours < 1 or hours > 168:  # 最多查询7天
        raise ValidationError("查询时间范围必须在1-168小时之间", field="hours")
    
    statistics = error_handler.get_error_statistics(hours)
    
    return jsonify({
        'success': True,
        'data': statistics,
        'message': '错误统计信息获取成功'
    })

@bp.route('/error/history', methods=['GET'])
@login_required
@require_admin(ResourceType.SYSTEM)
@security_audit('error_history_query')
@validate_input_security()
@safe_execute()
def get_error_history():
    """获取错误历史记录"""
    limit = request.args.get('limit', type=int, default=50)
    category = request.args.get('category', type=str)
    severity = request.args.get('severity', type=str)
    
    if limit < 1 or limit > 500:
        raise ValidationError("返回记录数量必须在1-500之间", field="limit")
    
    # 验证分类参数
    if category and category not in [c.value for c in ErrorCategory]:
        raise ValidationError(f"无效的错误分类: {category}", field="category")
    
    # 验证严重程度参数  
    if severity and severity not in [s.name for s in ErrorSeverity]:
        raise ValidationError(f"无效的错误严重程度: {severity}", field="severity")
    
    # 获取错误历史
    all_errors = list(error_handler.error_history)
    
    # 过滤条件
    filtered_errors = all_errors
    if category:
        filtered_errors = [e for e in filtered_errors if e.get('category') == category]
    if severity:
        filtered_errors = [e for e in filtered_errors if e.get('severity') == severity]
    
    # 按时间倒序排列并限制数量
    filtered_errors = sorted(filtered_errors, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    return jsonify({
        'success': True,
        'data': {
            'errors': filtered_errors,
            'total_count': len(filtered_errors),
            'filters': {
                'category': category,
                'severity': severity,
                'limit': limit
            }
        },
        'message': '错误历史记录获取成功'
    })

@bp.route('/error/patterns', methods=['GET'])
@login_required
@require_admin(ResourceType.SYSTEM)
@security_audit('error_patterns_query')
@validate_input_security()
@safe_execute()
def get_error_patterns():
    """获取错误模式分析"""
    patterns_analysis = {}
    
    for pattern_key, pattern_errors in error_handler.error_patterns.items():
        recent_errors = [
            e for e in pattern_errors
            if datetime.now() - e['timestamp'] < timedelta(hours=24)
        ]
        
        if recent_errors:
            patterns_analysis[pattern_key] = {
                'count': len(recent_errors),
                'first_occurrence': min(e['timestamp'] for e in recent_errors).isoformat(),
                'last_occurrence': max(e['timestamp'] for e in recent_errors).isoformat(),
                'affected_users': len(set(e.get('user_id') for e in recent_errors if e.get('user_id'))),
                'sample_details': recent_errors[:3]  # 样本错误详情
            }
    
    # 按发生次数排序
    sorted_patterns = sorted(
        patterns_analysis.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    
    return jsonify({
        'success': True,
        'data': {
            'patterns': dict(sorted_patterns),
            'analysis_period': '24小时',
            'total_patterns': len(sorted_patterns),
            'generated_at': datetime.now().isoformat()
        },
        'message': '错误模式分析获取成功'
    })

@bp.route('/error/test/<error_type>', methods=['POST'])
@login_required
@require_admin(ResourceType.SYSTEM)
@security_audit('error_test_trigger')
@validate_input_security()
@safe_execute()
def trigger_test_error(error_type):
    """触发测试错误（用于测试异常处理机制）"""
    
    # 只在调试模式下允许触发测试错误
    if not current_app.debug:
        raise AuthorizationError("测试错误只能在调试模式下触发")
    
    test_message = f"这是一个测试错误: {error_type}"
    
    if error_type == 'validation':
        raise ValidationError(test_message, field="test_field")
    elif error_type == 'authentication':
        raise AuthenticationError(test_message)
    elif error_type == 'authorization':
        raise AuthorizationError(test_message)
    elif error_type == 'database':
        raise DatabaseError(test_message, operation="test_operation")
    elif error_type == 'network':
        raise NetworkError(test_message, url="http://test.example.com")
    elif error_type == 'external_api':
        raise ExternalAPIError(test_message, api_name="test_api", status_code=503)
    elif error_type == 'business':
        raise BusinessLogicError(test_message)
    elif error_type == 'system':
        raise CustomException(
            test_message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH
        )
    else:
        raise ValidationError(f"不支持的测试错误类型: {error_type}", field="error_type")

@bp.route('/error/recovery/strategies', methods=['GET'])
@login_required
@require_read(ResourceType.SYSTEM)
@security_audit('error_recovery_strategies_query')
@validate_input_security()
@safe_execute()
def get_recovery_strategies():
    """获取错误恢复策略信息"""
    strategies = {}
    
    for error_type, strategy in error_handler.recovery_strategies.items():
        strategies[error_type.__name__] = {
            'error_type': error_type.__name__,
            'strategy_function': strategy.__name__ if hasattr(strategy, '__name__') else str(strategy),
            'description': f"自动恢复策略用于 {error_type.__name__} 类型错误"
        }
    
    return jsonify({
        'success': True,
        'data': {
            'strategies': strategies,
            'total_strategies': len(strategies),
            'available_error_types': [
                'NetworkError', 'DatabaseError', 'ExternalAPIError',
                'ValidationError', 'BusinessLogicError'
            ]
        },
        'message': '恢复策略信息获取成功'
    })

@bp.route('/error/cleanup', methods=['POST']) 
@login_required
@require_admin(ResourceType.SYSTEM)
@security_audit('error_cleanup')
@validate_input_security()
@safe_execute()
def cleanup_old_errors():
    """清理旧的错误记录"""
    data = request.get_json() or {}
    days = data.get('days', 7)
    
    if days < 1 or days > 30:
        raise ValidationError("清理天数必须在1-30天之间", field="days")
    
    old_count = len(error_handler.error_history)
    error_handler.clear_old_errors(days)
    new_count = len(error_handler.error_history)
    
    cleaned_count = old_count - new_count
    
    return jsonify({
        'success': True,
        'data': {
            'cleaned_errors': cleaned_count,
            'remaining_errors': new_count,
            'cleanup_days': days,
            'cleanup_time': datetime.now().isoformat()
        },
        'message': f'成功清理了{cleaned_count}条{days}天前的错误记录'
    })

@bp.route('/error/categories', methods=['GET'])
@login_required
@require_read(ResourceType.SYSTEM)  
@security_audit('error_categories_query')
@validate_input_security()
@safe_execute()
def get_error_categories():
    """获取错误分类和严重程度信息"""
    categories = []
    for category in ErrorCategory:
        categories.append({
            'value': category.value,
            'name': category.name,
            'description': _get_category_description(category)
        })
    
    severities = []
    for severity in ErrorSeverity:
        severities.append({
            'value': severity.value,
            'name': severity.name,
            'description': _get_severity_description(severity)
        })
    
    return jsonify({
        'success': True,
        'data': {
            'categories': categories,
            'severities': severities,
            'error_codes': _get_error_codes_info()
        },
        'message': '错误分类信息获取成功'
    })

@bp.route('/error/health', methods=['GET'])
@login_required
@require_read(ResourceType.SYSTEM)
@security_audit('error_health_check')
@validate_input_security()
@safe_execute()
def get_error_health_status():
    """获取错误处理系统健康状态"""
    # 计算最近1小时的错误率
    recent_errors = [
        e for e in error_handler.error_history
        if datetime.now() - datetime.fromisoformat(e['timestamp']) < timedelta(hours=1)
    ]
    
    # 分析错误严重程度分布
    severity_counts = defaultdict(int)
    for error in recent_errors:
        severity_counts[error.get('severity', 'UNKNOWN')] += 1
    
    # 计算健康评分
    health_score = _calculate_error_health_score(recent_errors, severity_counts)
    
    # 生成健康状态
    if health_score >= 90:
        health_status = 'excellent'
        health_message = '系统错误率极低，运行状态优秀'
    elif health_score >= 75:
        health_status = 'good'
        health_message = '系统错误率较低，运行状态良好'
    elif health_score >= 50:
        health_status = 'warning'
        health_message = '系统错误率偏高，需要关注'
    else:
        health_status = 'critical'
        health_message = '系统错误率很高，需要紧急处理'
    
    return jsonify({
        'success': True,
        'data': {
            'health_status': health_status,
            'health_score': health_score,
            'health_message': health_message,
            'recent_errors_count': len(recent_errors),
            'severity_distribution': dict(severity_counts),
            'recommendations': _generate_error_recommendations(recent_errors, severity_counts),
            'check_time': datetime.now().isoformat()
        },
        'message': '错误处理系统健康状态获取成功'
    })

def _get_category_description(category: ErrorCategory) -> str:
    """获取错误分类描述"""
    descriptions = {
        ErrorCategory.VALIDATION: '输入验证错误',
        ErrorCategory.AUTHENTICATION: '身份认证错误',
        ErrorCategory.AUTHORIZATION: '权限授权错误',
        ErrorCategory.DATABASE: '数据库操作错误',
        ErrorCategory.NETWORK: '网络连接错误',
        ErrorCategory.EXTERNAL_API: '外部API调用错误',
        ErrorCategory.SYSTEM: '系统内部错误',
        ErrorCategory.BUSINESS: '业务逻辑错误',
        ErrorCategory.UNKNOWN: '未知类型错误'
    }
    return descriptions.get(category, '未知分类')

def _get_severity_description(severity: ErrorSeverity) -> str:
    """获取严重程度描述"""
    descriptions = {
        ErrorSeverity.LOW: '低级错误 - 不影响核心功能',
        ErrorSeverity.MEDIUM: '中级错误 - 影响部分功能',
        ErrorSeverity.HIGH: '高级错误 - 影响核心功能',
        ErrorSeverity.CRITICAL: '严重错误 - 系统不可用'
    }
    return descriptions.get(severity, '未知严重程度')

def _get_error_codes_info() -> Dict[str, Any]:
    """获取错误代码信息"""
    from app.utils.error_handling import ErrorCode
    
    error_codes = {}
    for attr_name in dir(ErrorCode):
        if not attr_name.startswith('_'):
            code = getattr(ErrorCode, attr_name)
            if isinstance(code, int):
                error_codes[attr_name] = {
                    'code': code,
                    'name': attr_name,
                    'range': _get_error_code_range(code)
                }
    
    return error_codes

def _get_error_code_range(code: int) -> str:
    """获取错误代码范围描述"""
    if 1000 <= code < 2000:
        return '验证错误'
    elif 2000 <= code < 3000:
        return '认证错误'
    elif 3000 <= code < 4000:
        return '授权错误'
    elif 4000 <= code < 5000:
        return '数据库错误'
    elif 5000 <= code < 6000:
        return '网络错误'
    elif 6000 <= code < 7000:
        return '外部API错误'
    elif 7000 <= code < 8000:
        return '系统错误'
    elif 8000 <= code < 9000:
        return '业务错误'
    else:
        return '未知范围'

def _calculate_error_health_score(recent_errors: List[Dict], severity_counts: Dict[str, int]) -> int:
    """计算错误健康评分"""
    base_score = 100
    
    # 根据错误数量扣分
    error_count = len(recent_errors)
    if error_count > 50:
        base_score -= 30
    elif error_count > 20:
        base_score -= 20
    elif error_count > 10:
        base_score -= 10
    elif error_count > 5:
        base_score -= 5
    
    # 根据严重程度扣分
    base_score -= severity_counts.get('CRITICAL', 0) * 10
    base_score -= severity_counts.get('HIGH', 0) * 5
    base_score -= severity_counts.get('MEDIUM', 0) * 2
    base_score -= severity_counts.get('LOW', 0) * 1
    
    return max(0, min(100, base_score))

def _generate_error_recommendations(recent_errors: List[Dict], severity_counts: Dict[str, int]) -> List[str]:
    """生成错误处理建议"""
    recommendations = []
    
    if severity_counts.get('CRITICAL', 0) > 0:
        recommendations.append('立即处理严重错误，系统可能不稳定')
    
    if severity_counts.get('HIGH', 0) > 5:
        recommendations.append('关注高级错误，可能影响用户体验')
    
    if len(recent_errors) > 20:
        recommendations.append('错误频率较高，建议检查系统负载和资源使用情况')
    
    # 分析错误类型
    category_counts = defaultdict(int)
    for error in recent_errors:
        category_counts[error.get('category', 'unknown')] += 1
    
    if category_counts.get('database', 0) > category_counts.get('network', 0):
        recommendations.append('数据库错误较多，建议检查数据库连接和查询性能')
    
    if category_counts.get('network', 0) > 5:
        recommendations.append('网络错误较多，建议检查网络连接和外部服务状态')
    
    if not recommendations:
        recommendations.append('系统运行正常，继续保持监控')
    
    return recommendations

# 重试和降级策略API端点
@bp.route('/resilience/status', methods=['GET'])
@login_required
@require_read(ResourceType.SYSTEM)
@security_audit('resilience_status_query')
@validate_input_security()
@safe_execute()
def get_resilience_system_status():
    """获取弹性系统状态"""
    status = get_resilience_status()
    
    return jsonify({
        'success': True,
        'data': status,
        'message': '弹性系统状态获取成功'
    })

@bp.route('/resilience/circuit-breakers/<breaker_name>/reset', methods=['POST'])
@login_required
@require_admin(ResourceType.SYSTEM)
@security_audit('circuit_breaker_reset')
@validate_input_security()
@safe_execute()
def reset_circuit_breaker(breaker_name):
    """重置指定的熔断器"""
    if breaker_name not in circuit_breakers:
        raise ValidationError(f"熔断器 {breaker_name} 不存在", field="breaker_name")
    
    breaker = circuit_breakers[breaker_name]
    old_state = breaker.state.value
    breaker.reset()
    
    return jsonify({
        'success': True,
        'data': {
            'breaker_name': breaker_name,
            'old_state': old_state,
            'new_state': breaker.state.value,
            'reset_time': datetime.now().isoformat()
        },
        'message': f'熔断器 {breaker_name} 重置成功'
    })

@bp.route('/resilience/cleanup', methods=['POST'])
@login_required
@require_admin(ResourceType.SYSTEM)
@security_audit('resilience_cleanup')
@validate_input_security()
@safe_execute()
def cleanup_resilience_data():
    """清理弹性机制数据"""
    data = request.get_json() or {}
    days = data.get('days', 7)
    
    if days < 1 or days > 30:
        raise ValidationError("清理天数必须在1-30天之间", field="days")
    
    # 记录清理前的状态
    old_cache_size = len(fallback_manager.cache)
    old_circuit_history = sum(len(breaker.call_history) for breaker in circuit_breakers.values())
    
    # 执行清理
    cleanup_old_statistics(days)
    
    # 记录清理后的状态
    new_cache_size = len(fallback_manager.cache)
    new_circuit_history = sum(len(breaker.call_history) for breaker in circuit_breakers.values())
    
    return jsonify({
        'success': True,
        'data': {
            'cleanup_days': days,
            'cache_cleared': old_cache_size - new_cache_size,
            'history_cleared': old_circuit_history - new_circuit_history,
            'remaining_cache': new_cache_size,
            'remaining_history': new_circuit_history,
            'cleanup_time': datetime.now().isoformat()
        },
        'message': f'成功清理了{days}天前的弹性机制数据'
    })

# Jenkins视图管理API端点
@bp.route('/jenkins/views/<int:instance_id>', methods=['GET'])
@login_required
@require_read(ResourceType.JENKINS)
@security_audit('jenkins_views_query')
@validate_input_security()
@safe_execute()
def get_jenkins_views(instance_id):
    """获取Jenkins视图列表"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        # 获取Jenkins视图列表
        views_url = f"{instance['url']}/api/json?tree=views[name,url,description,jobs[name]]"
        
        response = requests.get(
            views_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            views = []
            
            for view in data.get('views', []):
                view_detail = {
                    'name': view.get('name', ''),
                    'description': view.get('description', ''),
                    'url': view.get('url', ''),
                    'jobs': []
                }
                
                # 获取视图的详细信息
                view_url = f"{instance['url']}/view/{view['name']}/api/json?tree=jobs[name,displayName,description,lastBuild[number,result,duration,timestamp]]"
                view_response = requests.get(
                    view_url,
                    auth=HTTPBasicAuth(instance['username'], jenkins_token),
                    timeout=15
                )
                
                if view_response.status_code == 200:
                    view_data = view_response.json()
                    view_detail['jobs'] = view_data.get('jobs', [])
                
                views.append(view_detail)
            
            return jsonify({
                'success': True,
                'data': {
                    'views': views,
                    'total': len(views)
                }
            })
        else:
            return jsonify({'success': False, 'message': '获取Jenkins视图失败'})
            
    except Exception as e:
        logger.error(f"获取Jenkins视图失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/views/<int:instance_id>', methods=['POST'])
@login_required
@require_write(ResourceType.JENKINS)
@security_audit('jenkins_view_create')
@validate_input_security()
@safe_execute()
def create_jenkins_view(instance_id):
    """创建新的Jenkins视图"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        data = request.get_json()
        view_name = data.get('name', '').strip()
        description = data.get('description', '')
        job_names = data.get('jobNames', [])
        
        if not view_name:
            return jsonify({'success': False, 'message': '视图名称不能为空'})
        
        # 验证视图名称格式
        if not re.match(r'^[a-zA-Z0-9_-]+$', view_name):
            return jsonify({'success': False, 'message': '视图名称只能包含字母、数字、下划线和连字符'})
        
        # 创建视图的XML配置
        view_xml = f'''<?xml version='1.1' encoding='UTF-8'?>
<listView>
    <name>{view_name}</name>
    <description>{description}</description>
    <filterExecutors>false</filterExecutors>
    <filterQueue>false</filterQueue>
    <properties class="hudson.model.View$PropertyList"/>
    <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator"/>
        <string>{'</string><string>'.join(job_names)}</string>
    </jobNames>
    <jobFilters/>
    <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastFailureColumn/>
        <hudson.views.LastDurationColumn/>
        <hudson.views.BuildButtonColumn/>
    </columns>
    <includeRegex></includeRegex>
    <recurse>false</recurse>
</listView>'''

        # 发送创建视图的请求
        create_url = f"{instance['url']}/createView"
        
        response = requests.post(
            create_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            data={'name': view_name, 'mode': 'hudson.model.ListView', 'json': view_xml},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=15
        )
        
        if response.status_code in [200, 201, 302]:  # 302 is redirect after successful creation
            return jsonify({
                'success': True,
                'data': {
                    'name': view_name,
                    'description': description,
                    'jobCount': len(job_names)
                },
                'message': f'视图 "{view_name}" 创建成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'创建视图失败: {response.status_code} - {response.text}'
            })
            
    except Exception as e:
        logger.error(f"创建Jenkins视图失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/views/<int:instance_id>/<view_name>', methods=['DELETE'])
@login_required
@require_write(ResourceType.JENKINS)
@security_audit('jenkins_view_delete')
@validate_input_security()
@safe_execute()
def delete_jenkins_view(instance_id, view_name):
    """删除Jenkins视图"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        delete_url = f"{instance['url']}/view/{view_name}/doDelete"
        
        response = requests.post(
            delete_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=15
        )
        
        if response.status_code in [200, 302, 404]:  # 404 means view might already be deleted
            return jsonify({
                'success': True,
                'message': f'视图 "{view_name}" 删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'删除视图失败: {response.status_code}'
            })
            
    except Exception as e:
        logger.error(f"删除Jenkins视图失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/views/<int:instance_id>/<view_name>/jobs', methods=['GET'])
@login_required
@require_read(ResourceType.JENKINS)
@security_audit('jenkins_view_jobs_query')
@validate_input_security()
@safe_execute()
def get_jenkins_view_jobs(instance_id, view_name):
    """获取指定视图中的任务"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        view_url = f"{instance['url']}/view/{view_name}/api/json?tree=jobs[name,displayName,description,lastBuild[number,result,duration,timestamp],color]"
        
        response = requests.get(
            view_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('jobs', []):
                last_build = job.get('lastBuild', {})
                status = 'unknown'
                
                if last_build:
                    result = last_build.get('result')
                    if result is None and last_build.get('building', False):
                        status = 'building'
                    elif result == 'SUCCESS':
                        status = 'success'
                    elif result == 'FAILURE':
                        status = 'failure'
                    elif result == 'UNSTABLE':
                        status = 'unstable'
                
                jobs.append({
                    'name': job.get('name', ''),
                    'displayName': job.get('displayName', ''),
                    'description': job.get('description', ''),
                    'status': status,
                    'lastBuildNumber': last_build.get('number', 0),
                    'lastBuildTime': last_build.get('timestamp', 0),
                    'duration': last_build.get('duration', 0),
                    'color': job.get('color', '')
                })
            
            return jsonify({
                'success': True,
                'data': {
                    'viewName': view_name,
                    'jobs': jobs,
                    'total': len(jobs)
                }
            })
        else:
            return jsonify({'success': False, 'message': '获取视图任务失败'})
            
    except Exception as e:
        logger.error(f"获取Jenkins视图任务失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/config/<int:instance_id>/<job_name>', methods=['GET'])
@login_required
@require_read(ResourceType.JENKINS)
@security_audit('jenkins_job_config_query')
@validate_input_security()
@safe_execute()
def get_jenkins_job_config(instance_id, job_name):
    """获取Jenkins任务配置"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        config_url = f"{instance['url']}/job/{job_name}/config.xml"
        
        response = requests.get(
            config_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=15
        )
        
        if response.status_code == 200:
            config_xml = response.text
            
            # 解析XML获取任务基本信息
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(config_xml)
                
                display_name = ''
                description = ''
                
                # 查找displayName
                display_name_elem = root.find('.//displayName')
                if display_name_elem is not None:
                    display_name = display_name_elem.text or ''
                
                # 查找description
                description_elem = root.find('.//description')
                if description_elem is not None:
                    description = description_elem.text or ''
                
            except Exception as parse_error:
                logger.warning(f"解析XML配置失败: {parse_error}")
                display_name = job_name
                description = ''
            
            return jsonify({
                'success': True,
                'data': {
                    'xml': config_xml,
                    'displayName': display_name,
                    'description': description
                }
            })
        elif response.status_code == 404:
            return jsonify({'success': False, 'message': '任务不存在或无法获取配置'})
        else:
            return jsonify({
                'success': False, 
                'message': f'获取任务配置失败: {response.status_code}'
            })
            
    except Exception as e:
        logger.error(f"获取Jenkins任务配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/jenkins/config/<int:instance_id>/<job_name>', methods=['POST'])
@login_required
@require_write(ResourceType.JENKINS)
@security_audit('jenkins_job_config_update')
@validate_input_security()
@safe_execute()
def update_jenkins_job_config(instance_id, job_name):
    """更新Jenkins任务配置"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        data = request.get_json()
        config_xml = data.get('config', '')
        
        if not config_xml:
            return jsonify({'success': False, 'message': '配置内容不能为空'})
        
        # 验证XML格式
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(config_xml)
        except ET.ParseError as e:
            return jsonify({'success': False, 'message': f'XML格式错误: {str(e)}'})
        
        # 更新任务配置
        config_url = f"{instance['url']}/job/{job_name}/config.xml"
        
        response = requests.post(
            config_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            data=config_xml.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            return jsonify({
                'success': True,
                'message': f'任务 "{job_name}" 配置更新成功'
            })
        elif response.status_code == 404:
            return jsonify({'success': False, 'message': '任务不存在'})
        else:
            return jsonify({
                'success': False,
                'message': f'更新任务配置失败: {response.status_code} - {response.text}'
            })
            
    except Exception as e:
        logger.error(f"更新Jenkins任务配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# 添加前端期望的路由别名
@bp.route('/jenkins/builds/history/<int:instance_id>', methods=['GET'])
@login_required
def get_jenkins_builds_history_alias(instance_id):
    """获取Jenkins构建历史 - 前端路径别名"""
    return get_jenkins_build_history(instance_id)

@bp.route('/jenkins/analytics/overview/<int:instance_id>', methods=['GET'])  
@login_required
def get_jenkins_analytics_overview_alias(instance_id):
    """获取Jenkins分析概览 - 前端路径别名"""
    return get_jenkins_analytics(instance_id)

# Jenkins 任务向导 API 端点
@bp.route('/jenkins/jobs/<int:instance_id>', methods=['POST'])
@login_required
@require_write(ResourceType.JENKINS)
@security_audit('jenkins_job_create')
@validate_input_security()
@safe_execute()
def create_jenkins_job(instance_id):
    """创建新的Jenkins任务"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        data = request.get_json()
        job_name = data.get('name', '').strip()
        job_xml = data.get('xml', '')
        job_description = data.get('description', '')
        
        if not job_name:
            return jsonify({'success': False, 'message': '任务名称不能为空'})
            
        if not job_xml:
            return jsonify({'success': False, 'message': 'XML配置不能为空'})
        
        # 验证任务名称格式
        if not re.match(r'^[a-zA-Z0-9_-]+$', job_name):
            return jsonify({'success': False, 'message': '任务名称只能包含字母、数字、连字符和下划线'})
        
        # 验证XML格式
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(job_xml)
        except ET.ParseError as e:
            return jsonify({'success': False, 'message': f'XML格式错误: {str(e)}'})
        
        # 检查任务是否已存在
        check_url = f"{instance['url']}/job/{job_name}/api/json"
        check_response = requests.get(
            check_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=10
        )
        
        if check_response.status_code == 200:
            return jsonify({'success': False, 'message': f'任务 "{job_name}" 已存在'})
        
        # 创建新任务
        create_url = f"{instance['url']}/createItem?name={job_name}"
        response = requests.post(
            create_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            data=job_xml.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            # 记录操作日志
            logger.info(f"用户创建Jenkins任务成功: 实例={instance_id}, 任务={job_name}")
            
            return jsonify({
                'success': True,
                'message': f'任务 "{job_name}" 创建成功',
                'data': {
                    'jobName': job_name,
                    'jobUrl': f"{instance['url']}/job/{job_name}"
                }
            })
        else:
            error_msg = f'创建任务失败: {response.status_code}'
            if response.text:
                error_msg += f' - {response.text[:200]}'
            return jsonify({'success': False, 'message': error_msg})
            
    except Exception as e:
        logger.error(f"创建Jenkins任务失败: {e}")
        return jsonify({'success': False, 'message': f'创建任务失败: {str(e)}'})

@bp.route('/jenkins/jobs/<int:instance_id>/<job_name>', methods=['PUT'])
@login_required
@require_write(ResourceType.JENKINS)
@security_audit('jenkins_job_update')
@validate_input_security()
@safe_execute()
def update_jenkins_job(instance_id, job_name):
    """更新Jenkins任务"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        data = request.get_json()
        job_xml = data.get('xml', '')
        
        if not job_xml:
            return jsonify({'success': False, 'message': 'XML配置不能为空'})
        
        # 验证XML格式
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(job_xml)
        except ET.ParseError as e:
            return jsonify({'success': False, 'message': f'XML格式错误: {str(e)}'})
        
        # 更新任务配置
        config_url = f"{instance['url']}/job/{job_name}/config.xml"
        response = requests.post(
            config_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            data=job_xml.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"用户更新Jenkins任务成功: 实例={instance_id}, 任务={job_name}")
            
            return jsonify({
                'success': True,
                'message': f'任务 "{job_name}" 更新成功'
            })
        elif response.status_code == 404:
            return jsonify({'success': False, 'message': '任务不存在'})
        else:
            error_msg = f'更新任务失败: {response.status_code}'
            if response.text:
                error_msg += f' - {response.text[:200]}'
            return jsonify({'success': False, 'message': error_msg})
            
    except Exception as e:
        logger.error(f"更新Jenkins任务失败: {e}")
        return jsonify({'success': False, 'message': f'更新任务失败: {str(e)}'})

@bp.route('/jenkins/templates', methods=['GET'])
@login_required
@require_read(ResourceType.JENKINS)
def get_jenkins_templates():
    """获取Jenkins任务模板"""
    try:
        templates = {
            'freestyle': [
                {
                    'id': 'basic-freestyle',
                    'name': '基础自由风格项目',
                    'description': '包含基本构建步骤的模板',
                    'category': 'basic',
                    'xml': '''<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>基础自由风格项目模板</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>echo "构建开始"
echo "这里可以添加你的构建命令"
echo "构建完成"</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>'''
                },
                {
                    'id': 'maven-freestyle',
                    'name': 'Maven项目模板',
                    'description': '适用于Maven Java项目的模板',
                    'category': 'java',
                    'xml': '''<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Maven项目构建模板</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Maven>
      <targets>clean compile test package</targets>
      <mavenName>Maven-3.8</mavenName>
      <usePrivateRepository>false</usePrivateRepository>
      <settings class="jenkins.mvn.DefaultSettingsProvider"/>
      <globalSettings class="jenkins.mvn.DefaultGlobalSettingsProvider"/>
    </hudson.tasks.Maven>
  </builders>
  <publishers>
    <hudson.tasks.junit.JUnitResultArchiver>
      <testResults>target/surefire-reports/*.xml</testResults>
      <keepLongStdio>false</keepLongStdio>
      <healthScaleFactor>1.0</healthScaleFactor>
      <allowEmptyResults>false</allowEmptyResults>
    </hudson.tasks.junit.JUnitResultArchiver>
  </publishers>
  <buildWrappers/>
</project>'''
                },
                {
                    'id': 'nodejs-freestyle',
                    'name': 'Node.js项目模板',
                    'description': '适用于Node.js项目的模板',
                    'category': 'nodejs',
                    'xml': '''<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Node.js项目构建模板</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>echo "安装Node.js依赖..."
npm install

echo "运行代码检查..."
npm run lint

echo "运行测试..."
npm test

echo "构建项目..."
npm run build

echo "构建完成！"</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>'''
                }
            ],
            'pipeline': [
                {
                    'id': 'basic-pipeline',
                    'name': '基础Pipeline',
                    'description': '包含基本阶段的Pipeline模板',
                    'category': 'basic',
                    'script': '''pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo '检出代码...'
                // checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo '构建项目...'
                // 添加你的构建命令
            }
        }
        
        stage('Test') {
            steps {
                echo '运行测试...'
                // 添加你的测试命令
            }
        }
        
        stage('Deploy') {
            when {
                branch 'master'
            }
            steps {
                echo '部署应用...'
                // 添加你的部署命令
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline执行完成'
            cleanWs()
        }
        success {
            echo 'Pipeline执行成功！'
        }
        failure {
            echo 'Pipeline执行失败！'
        }
    }
}'''
                },
                {
                    'id': 'docker-pipeline',
                    'name': 'Docker Pipeline',
                    'description': '包含Docker构建和部署的Pipeline',
                    'category': 'docker',
                    'script': '''pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'myapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
        REGISTRY = 'registry.example.com'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo '构建应用...'
                // 添加构建命令
            }
        }
        
        stage('Test') {
            steps {
                echo '运行测试...'
                // 添加测试命令
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    def image = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    echo "Docker镜像构建完成: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }
        
        stage('Docker Push') {
            when {
                anyOf {
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", 'docker-registry-credentials') {
                        def image = docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}")
                        image.push()
                        image.push("latest")
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'master'
            }
            steps {
                echo '部署到生产环境...'
                // 添加部署脚本
                sh """
                    kubectl set image deployment/myapp myapp=${REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    kubectl rollout status deployment/myapp
                """
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline执行成功！'
        }
        failure {
            echo 'Pipeline执行失败！'
            // 发送通知
        }
    }
}'''
                }
            ]
        }
        
        template_type = request.args.get('type', 'all')
        
        if template_type == 'freestyle':
            return jsonify({'success': True, 'data': templates['freestyle']})
        elif template_type == 'pipeline':
            return jsonify({'success': True, 'data': templates['pipeline']})
        else:
            return jsonify({'success': True, 'data': templates})
            
    except Exception as e:
        logger.error(f"获取Jenkins模板失败: {e}")
        return jsonify({'success': False, 'message': f'获取模板失败: {str(e)}'})

@bp.route('/jenkins/credentials/<int:instance_id>', methods=['GET'])
@login_required
@require_read(ResourceType.JENKINS)
@security_audit('jenkins_credentials_query')
def get_jenkins_credentials(instance_id):
    """获取Jenkins凭据列表"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        # 获取凭据列表
        credentials_url = f"{instance['url']}/credentials/api/json?tree=credentials[id,description]"
        
        response = requests.get(
            credentials_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=15
        )
        
        if response.status_code == 200:
            credentials_data = response.json()
            credentials = []
            
            # 处理凭据数据
            for cred in credentials_data.get('credentials', []):
                credentials.append({
                    'id': cred.get('id', ''),
                    'description': cred.get('description', cred.get('id', ''))
                })
            
            return jsonify({
                'success': True,
                'data': credentials
            })
        elif response.status_code == 404:
            # 如果凭据插件未安装，返回空列表
            return jsonify({
                'success': True,
                'data': [],
                'message': 'Jenkins凭据插件未安装或无可用凭据'
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'获取凭据列表失败: {response.status_code}'
            })
            
    except Exception as e:
        logger.error(f"获取Jenkins凭据失败: {e}")
        return jsonify({'success': False, 'message': f'获取凭据失败: {str(e)}'})

@bp.route('/jenkins/validate-config', methods=['POST'])
@login_required
@require_read(ResourceType.JENKINS)
@validate_input_security()
def validate_jenkins_config():
    """验证Jenkins配置"""
    try:
        data = request.get_json()
        config_xml = data.get('xml', '')
        config_type = data.get('type', 'freestyle')  # freestyle 或 pipeline
        
        if not config_xml:
            return jsonify({'success': False, 'message': 'XML配置不能为空'})
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # XML格式验证
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(config_xml)
        except ET.ParseError as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f'XML格式错误: {str(e)}')
            return jsonify({'success': True, 'data': validation_results})
        
        # 基础结构验证
        if config_type == 'freestyle':
            # 验证自由风格项目结构
            if root.tag != 'project':
                validation_results['errors'].append('自由风格项目根元素应为 <project>')
                validation_results['valid'] = False
            
            # 检查必要元素
            if root.find('builders') is None:
                validation_results['warnings'].append('未找到构建步骤 (<builders>)')
            else:
                builders = root.find('builders')
                if len(list(builders)) == 0:
                    validation_results['warnings'].append('构建步骤为空，建议添加构建命令')
            
            # 检查SCM配置
            scm = root.find('scm')
            if scm is not None and scm.get('class') == 'hudson.scm.NullSCM':
                validation_results['suggestions'].append('建议配置源码管理 (SCM)')
        
        elif config_type == 'pipeline':
            # 验证Pipeline脚本
            pipeline_script = data.get('script', '')
            if pipeline_script:
                # 基本Pipeline语法检查
                if 'pipeline' not in pipeline_script.lower():
                    validation_results['errors'].append('Pipeline脚本应包含 pipeline 块')
                    validation_results['valid'] = False
                
                if 'stages' not in pipeline_script.lower():
                    validation_results['warnings'].append('建议在Pipeline中定义 stages')
                
                if 'agent' not in pipeline_script.lower():
                    validation_results['warnings'].append('建议在Pipeline中指定 agent')
        
        # 安全性检查
        xml_content = config_xml.lower()
        security_warnings = []
        
        if 'password' in xml_content and 'plain' in xml_content:
            security_warnings.append('检测到明文密码，建议使用Jenkins凭据管理')
        
        if 'rm -rf' in xml_content or 'del /f' in xml_content:
            security_warnings.append('检测到危险的删除命令，请谨慎使用')
        
        if 'sudo' in xml_content:
            security_warnings.append('检测到sudo命令，确保Jenkins用户有适当权限')
        
        validation_results['warnings'].extend(security_warnings)
        
        # 性能建议
        if 'concurrent' not in xml_content:
            validation_results['suggestions'].append('考虑启用并发构建以提高效率')
        
        return jsonify({
            'success': True,
            'data': validation_results
        })
        
    except Exception as e:
        logger.error(f"验证Jenkins配置失败: {e}")
        return jsonify({'success': False, 'message': f'配置验证失败: {str(e)}'})

@bp.route('/jenkins/step-types', methods=['GET'])
@login_required
@require_read(ResourceType.JENKINS)
def get_jenkins_step_types():
    """获取可用的构建步骤类型"""
    try:
        step_types = {
            'freestyle': [
                {
                    'id': 'shell',
                    'name': 'Shell脚本',
                    'description': '执行Shell命令或脚本',
                    'icon': '🖥️',
                    'category': 'build',
                    'template': 'echo "Hello Jenkins"',
                    'params': [
                        {'name': 'script', 'type': 'textarea', 'required': True, 'label': '脚本内容'}
                    ]
                },
                {
                    'id': 'batch',
                    'name': 'Windows批处理',
                    'description': '执行Windows批处理命令',
                    'icon': '🪟',
                    'category': 'build',
                    'template': 'echo Hello Jenkins',
                    'params': [
                        {'name': 'command', 'type': 'textarea', 'required': True, 'label': '批处理命令'}
                    ]
                },
                {
                    'id': 'maven',
                    'name': 'Maven构建',
                    'description': '执行Maven构建命令',
                    'icon': '☕',
                    'category': 'build',
                    'template': 'clean compile test package',
                    'params': [
                        {'name': 'targets', 'type': 'text', 'required': True, 'label': 'Maven目标'},
                        {'name': 'pom', 'type': 'text', 'required': False, 'label': 'POM文件路径'}
                    ]
                },
                {
                    'id': 'gradle',
                    'name': 'Gradle构建',
                    'description': '执行Gradle构建任务',
                    'icon': '🐘',
                    'category': 'build',
                    'template': 'clean build test',
                    'params': [
                        {'name': 'tasks', 'type': 'text', 'required': True, 'label': 'Gradle任务'},
                        {'name': 'buildFile', 'type': 'text', 'required': False, 'label': '构建文件路径'}
                    ]
                },
                {
                    'id': 'docker',
                    'name': 'Docker操作',
                    'description': '构建、推送或运行Docker镜像',
                    'icon': '🐳',
                    'category': 'deploy',
                    'template': 'build',
                    'params': [
                        {'name': 'operation', 'type': 'select', 'required': True, 'label': '操作类型', 
                         'options': [{'value': 'build', 'label': '构建镜像'}, {'value': 'push', 'label': '推送镜像'}, {'value': 'run', 'label': '运行容器'}]},
                        {'name': 'imageName', 'type': 'text', 'required': True, 'label': '镜像名称'},
                        {'name': 'dockerfile', 'type': 'text', 'required': False, 'label': 'Dockerfile路径'}
                    ]
                },
                {
                    'id': 'ansible',
                    'name': 'Ansible部署',
                    'description': '执行Ansible playbook',
                    'icon': '🔧',
                    'category': 'deploy',
                    'template': 'site.yml',
                    'params': [
                        {'name': 'playbook', 'type': 'text', 'required': True, 'label': 'Playbook文件'},
                        {'name': 'inventory', 'type': 'text', 'required': False, 'label': '清单文件'},
                        {'name': 'extraVars', 'type': 'textarea', 'required': False, 'label': '额外变量'}
                    ]
                },
                {
                    'id': 'ssh',
                    'name': 'SSH部署',
                    'description': '通过SSH执行远程命令',
                    'icon': '🔑',
                    'category': 'deploy',
                    'template': '',
                    'params': [
                        {'name': 'host', 'type': 'text', 'required': True, 'label': '目标主机'},
                        {'name': 'username', 'type': 'text', 'required': True, 'label': '用户名'},
                        {'name': 'keyPath', 'type': 'text', 'required': False, 'label': 'SSH密钥路径'},
                        {'name': 'commands', 'type': 'textarea', 'required': True, 'label': '执行命令'}
                    ]
                },
                {
                    'id': 'email',
                    'name': '邮件通知',
                    'description': '发送构建结果邮件通知',
                    'icon': '📧',
                    'category': 'notify',
                    'template': '',
                    'params': [
                        {'name': 'recipients', 'type': 'text', 'required': True, 'label': '收件人'},
                        {'name': 'subject', 'type': 'text', 'required': False, 'label': '邮件主题'},
                        {'name': 'body', 'type': 'textarea', 'required': False, 'label': '邮件内容'}
                    ]
                },
                {
                    'id': 'slack',
                    'name': 'Slack通知',
                    'description': '发送消息到Slack频道',
                    'icon': '💬',
                    'category': 'notify',
                    'template': '',
                    'params': [
                        {'name': 'channel', 'type': 'text', 'required': True, 'label': 'Slack频道'},
                        {'name': 'message', 'type': 'textarea', 'required': True, 'label': '消息内容'},
                        {'name': 'webhookUrl', 'type': 'text', 'required': True, 'label': 'Webhook URL'}
                    ]
                },
                {
                    'id': 'junit',
                    'name': 'JUnit测试报告',
                    'description': '发布JUnit测试结果',
                    'icon': '🧪',
                    'category': 'test',
                    'template': 'target/surefire-reports/*.xml',
                    'params': [
                        {'name': 'testResults', 'type': 'text', 'required': True, 'label': '测试结果文件路径'},
                        {'name': 'allowEmptyResults', 'type': 'checkbox', 'required': False, 'label': '允许空结果'}
                    ]
                }
            ],
            'pipeline': [
                {
                    'id': 'checkout',
                    'name': '检出代码',
                    'description': '从版本控制系统检出代码',
                    'icon': '📥',
                    'category': 'source',
                    'template': 'checkout scm'
                },
                {
                    'id': 'sh',
                    'name': 'Shell命令',
                    'description': '执行Shell命令',
                    'icon': '🖥️',
                    'category': 'build',
                    'template': 'sh "echo Hello Jenkins"'
                },
                {
                    'id': 'bat',
                    'name': 'Windows命令',
                    'description': '执行Windows批处理命令',
                    'icon': '🪟',
                    'category': 'build',
                    'template': 'bat "echo Hello Jenkins"'
                },
                {
                    'id': 'script',
                    'name': 'Groovy脚本',
                    'description': '执行Groovy脚本代码',
                    'icon': '📜',
                    'category': 'build',
                    'template': 'script {\n    echo "Hello from Groovy"\n}'
                },
                {
                    'id': 'parallel',
                    'name': '并行执行',
                    'description': '并行执行多个步骤',
                    'icon': '⚡',
                    'category': 'flow',
                    'template': 'parallel {\n    stage("Task A") {\n        steps { echo "Task A" }\n    }\n    stage("Task B") {\n        steps { echo "Task B" }\n    }\n}'
                },
                {
                    'id': 'when',
                    'name': '条件执行',
                    'description': '根据条件执行步骤',
                    'icon': '❓',
                    'category': 'flow',
                    'template': 'when {\n    branch "master"\n}'
                }
            ]
        }
        
        step_category = request.args.get('category', 'all')
        project_type = request.args.get('type', 'all')
        
        if project_type == 'freestyle':
            result = step_types['freestyle']
        elif project_type == 'pipeline':
            result = step_types['pipeline']
        else:
            result = {
                'freestyle': step_types['freestyle'],
                'pipeline': step_types['pipeline']
            }
        
        if step_category != 'all' and project_type in ['freestyle', 'pipeline']:
            result = [step for step in result if step.get('category') == step_category]
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取Jenkins步骤类型失败: {e}")
        return jsonify({'success': False, 'message': f'获取步骤类型失败: {str(e)}'})

# Jenkins任务删除API
@bp.route('/jenkins/jobs/<int:instance_id>/<job_name>', methods=['DELETE'])
@login_required
@require_write(ResourceType.JENKINS)
@security_audit('jenkins_job_delete')
@safe_execute()
def delete_jenkins_job(instance_id, job_name):
    """删除Jenkins任务"""
    try:
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})

        # 删除任务
        delete_url = f"{instance['url']}/job/{job_name}/doDelete"
        response = requests.post(
            delete_url,
            auth=HTTPBasicAuth(instance['username'], jenkins_token),
            timeout=30
        )
        
        if response.status_code in [200, 302]:  # 302是重定向，表示删除成功
            logger.info(f"用户删除Jenkins任务成功: 实例={instance_id}, 任务={job_name}")
            
            return jsonify({
                'success': True,
                'message': f'任务 "{job_name}" 删除成功'
            })
        elif response.status_code == 404:
            return jsonify({'success': False, 'message': '任务不存在'})
        else:
            error_msg = f'删除任务失败: {response.status_code}'
            if response.text:
                error_msg += f' - {response.text[:200]}'
            return jsonify({'success': False, 'message': error_msg})
            
    except Exception as e:
        logger.error(f"删除Jenkins任务失败: {e}")
        return jsonify({'success': False, 'message': f'删除任务失败: {str(e)}'})

# Jenkins Pipeline语法验证API
@bp.route('/jenkins/validate-pipeline', methods=['POST'])
@login_required
@require_read(ResourceType.JENKINS)
@validate_input_security()
def validate_jenkins_pipeline():
    """验证Jenkins Pipeline语法"""
    try:
        data = request.get_json()
        pipeline_script = data.get('script', '')
        instance_id = data.get('instanceId')
        
        if not pipeline_script:
            return jsonify({'success': False, 'message': 'Pipeline脚本不能为空'})
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 基本语法检查
        if 'pipeline' not in pipeline_script.lower():
            validation_results['errors'].append('Pipeline脚本必须包含 pipeline 块')
            validation_results['valid'] = False
        
        if 'agent' not in pipeline_script.lower():
            validation_results['warnings'].append('建议指定 agent')
        
        if 'stages' not in pipeline_script.lower():
            validation_results['warnings'].append('建议定义 stages')
        
        # 括号匹配检查
        brace_count = pipeline_script.count('{') - pipeline_script.count('}')
        if brace_count != 0:
            validation_results['errors'].append(f'大括号不匹配 (差异: {brace_count})')
            validation_results['valid'] = False
        
        paren_count = pipeline_script.count('(') - pipeline_script.count(')')
        if paren_count != 0:
            validation_results['errors'].append(f'圆括号不匹配 (差异: {paren_count})')
            validation_results['valid'] = False
        
        # 如果提供了Jenkins实例ID，可以调用Jenkins API进行更严格的验证
        if instance_id and validation_results['valid']:
            try:
                instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
                if instance:
                    # 使用Jenkins的Pipeline语法验证API
                    validate_url = f"{instance['url']}/pipeline-model-converter/validate"
                    response = requests.post(
                        validate_url,
                        auth=HTTPBasicAuth(instance['username'], jenkins_token),
                        data={'jenkinsfile': pipeline_script},
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if not result.get('result', 'success') == 'success':
                            for error in result.get('errors', []):
                                validation_results['errors'].append(error.get('error', '未知错误'))
                            validation_results['valid'] = False
                    elif response.status_code == 404:
                        validation_results['warnings'].append('Jenkins实例不支持Pipeline语法验证')
            except Exception as e:
                validation_results['warnings'].append(f'无法连接到Jenkins进行语法验证: {str(e)}')
        
        return jsonify({
            'success': True,
            'data': validation_results
        })
        
    except Exception as e:
        logger.error(f"验证Jenkins Pipeline失败: {e}")
        return jsonify({'success': False, 'message': f'Pipeline验证失败: {str(e)}'})

# 导入必要的模块 (如果尚未导入)
import re

# Jenkins配置测试和验证工具API
@bp.route('/jenkins/test-config', methods=['POST'])
@login_required
@require_read(ResourceType.JENKINS)
@validate_input_security()
def test_jenkins_config():
    """测试Jenkins配置是否能正常工作"""
    try:
        data = request.get_json()
        instance_id = data.get('instanceId')
        job_name = data.get('jobName', f'test-job-{int(time.time())}')
        job_xml = data.get('xml', '')
        test_mode = data.get('testMode', 'dry_run')  # dry_run, create_test, validate_only
        
        if not instance_id:
            return jsonify({'success': False, 'message': '请选择Jenkins实例'})
            
        if not job_xml:
            return jsonify({'success': False, 'message': 'XML配置不能为空'})
        
        instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        test_results = {
            'success': True,
            'results': [],
            'warnings': [],
            'errors': []
        }
        
        # 1. XML格式验证
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(job_xml)
            test_results['results'].append({
                'test': 'XML格式验证',
                'status': 'passed',
                'message': 'XML格式正确'
            })
        except ET.ParseError as e:
            test_results['success'] = False
            test_results['errors'].append(f'XML格式错误: {str(e)}')
            test_results['results'].append({
                'test': 'XML格式验证',
                'status': 'failed',
                'message': f'XML格式错误: {str(e)}'
            })
            return jsonify({'success': True, 'data': test_results})
        
        # 2. Jenkins连接测试
        try:
            test_url = f"{instance['url']}/api/json"
            response = requests.get(
                test_url,
                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                timeout=10
            )
            
            if response.status_code == 200:
                test_results['results'].append({
                    'test': 'Jenkins连接测试',
                    'status': 'passed',
                    'message': 'Jenkins连接正常'
                })
            else:
                test_results['warnings'].append('Jenkins连接异常，可能影响任务创建')
                test_results['results'].append({
                    'test': 'Jenkins连接测试',
                    'status': 'warning',
                    'message': f'Jenkins连接异常: HTTP {response.status_code}'
                })
        except Exception as e:
            test_results['warnings'].append(f'无法连接到Jenkins: {str(e)}')
            test_results['results'].append({
                'test': 'Jenkins连接测试',
                'status': 'warning',
                'message': f'连接失败: {str(e)}'
            })
        
        # 3. 配置安全性检查
        security_issues = []
        xml_content = job_xml.lower()
        
        if 'password' in xml_content and 'plain' in xml_content:
            security_issues.append('检测到明文密码')
        
        if 'rm -rf' in xml_content or 'del /f' in xml_content:
            security_issues.append('检测到危险删除命令')
        
        if 'sudo' in xml_content:
            security_issues.append('检测到sudo命令')
        
        if security_issues:
            test_results['warnings'].extend(security_issues)
            test_results['results'].append({
                'test': '安全性检查',
                'status': 'warning',
                'message': f'发现 {len(security_issues)} 个安全问题: {", ".join(security_issues)}'
            })
        else:
            test_results['results'].append({
                'test': '安全性检查',
                'status': 'passed',
                'message': '未发现明显安全问题'
            })
        
        # 4. 配置完整性检查
        completeness_issues = []
        
        if root.find('.//scm[@class="hudson.scm.NullSCM"]') is not None:
            completeness_issues.append('未配置源码管理')
        
        builders = root.find('builders')
        if builders is None or len(list(builders)) == 0:
            completeness_issues.append('未配置构建步骤')
        
        if completeness_issues:
            test_results['warnings'].extend(completeness_issues)
            test_results['results'].append({
                'test': '配置完整性检查',
                'status': 'warning',
                'message': f'配置不完整: {", ".join(completeness_issues)}'
            })
        else:
            test_results['results'].append({
                'test': '配置完整性检查',
                'status': 'passed',
                'message': '配置完整'
            })
        
        # 5. 如果是创建测试模式，尝试创建临时任务
        if test_mode == 'create_test' and test_results['success']:
            try:
                test_job_name = f"{job_name}-test-{int(time.time())}"
                
                # 检查测试任务是否已存在
                check_url = f"{instance['url']}/job/{test_job_name}/api/json"
                check_response = requests.get(
                    check_url,
                    auth=HTTPBasicAuth(instance['username'], jenkins_token),
                    timeout=10
                )
                
                if check_response.status_code == 200:
                    test_job_name = f"{test_job_name}-{random.randint(1000, 9999)}"
                
                # 创建测试任务
                create_url = f"{instance['url']}/createItem?name={test_job_name}"
                create_response = requests.post(
                    create_url,
                    auth=HTTPBasicAuth(instance['username'], jenkins_token),
                    data=job_xml.encode('utf-8'),
                    headers={'Content-Type': 'application/xml'},
                    timeout=30
                )
                
                if create_response.status_code in [200, 201]:
                    test_results['results'].append({
                        'test': '任务创建测试',
                        'status': 'passed',
                        'message': f'测试任务 "{test_job_name}" 创建成功'
                    })
                    
                    # 立即删除测试任务
                    try:
                        delete_url = f"{instance['url']}/job/{test_job_name}/doDelete"
                        delete_response = requests.post(
                            delete_url,
                            auth=HTTPBasicAuth(instance['username'], jenkins_token),
                            timeout=30
                        )
                        
                        if delete_response.status_code in [200, 302]:
                            test_results['results'].append({
                                'test': '测试任务清理',
                                'status': 'passed',
                                'message': '测试任务已自动删除'
                            })
                        else:
                            test_results['warnings'].append(f'测试任务 "{test_job_name}" 清理失败，请手动删除')
                    except Exception as e:
                        test_results['warnings'].append(f'测试任务清理失败: {str(e)}')
                        
                else:
                    test_results['success'] = False
                    test_results['errors'].append(f'任务创建失败: {create_response.status_code}')
                    test_results['results'].append({
                        'test': '任务创建测试',
                        'status': 'failed',
                        'message': f'创建失败: HTTP {create_response.status_code}'
                    })
                    
            except Exception as e:
                test_results['success'] = False
                test_results['errors'].append(f'创建测试失败: {str(e)}')
                test_results['results'].append({
                    'test': '任务创建测试',
                    'status': 'failed',
                    'message': f'测试失败: {str(e)}'
                })
        
        # 6. 生成测试报告总结
        passed_tests = len([r for r in test_results['results'] if r['status'] == 'passed'])
        total_tests = len(test_results['results'])
        warning_count = len([r for r in test_results['results'] if r['status'] == 'warning'])
        failed_count = len([r for r in test_results['results'] if r['status'] == 'failed'])
        
        test_results['summary'] = {
            'total': total_tests,
            'passed': passed_tests,
            'warnings': warning_count,
            'failed': failed_count,
            'score': int((passed_tests / total_tests) * 100) if total_tests > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'data': test_results
        })
        
    except Exception as e:
        logger.error(f"Jenkins配置测试失败: {e}")
        return jsonify({'success': False, 'message': f'配置测试失败: {str(e)}'})

@bp.route('/jenkins/preview-xml', methods=['POST'])
@login_required
@require_read(ResourceType.JENKINS)
@validate_input_security()
def preview_jenkins_xml():
    """预览生成的Jenkins XML配置"""
    try:
        data = request.get_json()
        project_type = data.get('projectType', 'freestyle')
        job_config = data.get('jobConfig', {})
        
        if project_type == 'freestyle':
            xml_content = generate_freestyle_xml(job_config)
        elif project_type == 'pipeline':
            xml_content = generate_pipeline_xml(job_config)
        else:
            return jsonify({'success': False, 'message': '不支持的项目类型'})
        
        # 格式化XML
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            
            root = ET.fromstring(xml_content)
            rough_string = ET.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            formatted_xml = reparsed.toprettyxml(indent="  ")[23:]  # 去掉XML声明行
            
            # 添加XML声明
            formatted_xml = '<?xml version="1.1" encoding="UTF-8"?>\n' + formatted_xml
            
        except Exception:
            formatted_xml = xml_content
        
        return jsonify({
            'success': True,
            'data': {
                'xml': formatted_xml,
                'size': len(formatted_xml),
                'lines': len(formatted_xml.split('\n'))
            }
        })
        
    except Exception as e:
        logger.error(f"XML预览生成失败: {e}")
        return jsonify({'success': False, 'message': f'XML预览失败: {str(e)}'})

def generate_freestyle_xml(job_config):
    """生成Freestyle项目XML配置"""
    xml_template = '''<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>{description}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  {scm_config}
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  {triggers_config}
  <concurrentBuild>false</concurrentBuild>
  {builders_config}
  <publishers/>
  <buildWrappers/>
</project>'''
    
    # 生成SCM配置
    scm_config = '<scm class="hudson.scm.NullSCM"/>'
    scm = job_config.get('scm', {})
    if scm.get('url'):
        scm_config = f'''<scm class="hudson.plugins.git.GitSCM">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>{scm.get('url', '')}</url>
        {f'<credentialsId>{scm.get("credentials", "")}</credentialsId>' if scm.get('credentials') else ''}
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>{scm.get('branch', '*/master')}</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
  </scm>'''
    
    # 生成触发器配置
    triggers = job_config.get('triggers', {})
    triggers_config = '<triggers/>'
    if triggers.get('scm') or triggers.get('cron'):
        trigger_list = []
        if triggers.get('scm'):
            trigger_list.append(f'''<hudson.triggers.SCMTrigger>
      <spec>{triggers.get('scmSchedule', 'H/5 * * * *')}</spec>
      <ignorePostCommitHooks>false</ignorePostCommitHooks>
    </hudson.triggers.SCMTrigger>''')
        
        if triggers.get('cron'):
            trigger_list.append(f'''<hudson.triggers.TimerTrigger>
      <spec>{triggers.get('cronSchedule', '0 2 * * *')}</spec>
    </hudson.triggers.TimerTrigger>''')
        
        triggers_config = f'''<triggers>
    {chr(10).join(trigger_list)}
  </triggers>'''
    
    # 生成构建步骤配置
    build_steps = job_config.get('buildSteps', [])
    if build_steps:
        builders_list = []
        for step in build_steps:
            if step.get('type') == 'shell':
                builders_list.append(f'''<hudson.tasks.Shell>
      <command>{step.get('config', {}).get('script', '')}</command>
    </hudson.tasks.Shell>''')
            elif step.get('type') == 'maven':
                builders_list.append(f'''<hudson.tasks.Maven>
      <targets>{step.get('config', {}).get('targets', 'clean compile')}</targets>
      <mavenName>Maven-3.8</mavenName>
    </hudson.tasks.Maven>''')
        
        builders_config = f'''<builders>
    {chr(10).join(builders_list)}
  </builders>'''
    else:
        builders_config = '<builders/>'
    
    return xml_template.format(
        description=job_config.get('description', ''),
        scm_config=scm_config,
        triggers_config=triggers_config,
        builders_config=builders_config
    )

def generate_pipeline_xml(job_config):
    """生成Pipeline项目XML配置"""
    pipeline_script = job_config.get('pipelineScript', '')
    
    xml_template = '''<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <actions/>
  <description>{description}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{pipeline_script}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>'''
    
    return xml_template.format(
        description=job_config.get('description', ''),
        pipeline_script=pipeline_script.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    )

@bp.route('/jenkins/validate-job-name', methods=['POST'])
@login_required
@require_read(ResourceType.JENKINS)
@validate_input_security()
def validate_jenkins_job_name():
    """验证Jenkins任务名称是否可用"""
    try:
        data = request.get_json()
        job_name = data.get('jobName', '').strip()
        instance_id = data.get('instanceId')
        
        if not job_name:
            return jsonify({'success': False, 'message': '任务名称不能为空'})
        
        if not instance_id:
            return jsonify({'success': False, 'message': '请选择Jenkins实例'})
        
        validation_result = {
            'valid': True,
            'available': True,
            'suggestions': [],
            'errors': []
        }
        
        # 1. 名称格式验证
        if not re.match(r'^[a-zA-Z0-9_-]+$', job_name):
            validation_result['valid'] = False
            validation_result['errors'].append('任务名称只能包含字母、数字、连字符和下划线')
        
        if len(job_name) < 3:
            validation_result['valid'] = False
            validation_result['errors'].append('任务名称至少需要3个字符')
        
        if len(job_name) > 100:
            validation_result['valid'] = False
            validation_result['errors'].append('任务名称不能超过100个字符')
        
        # 2. 检查是否已存在（如果格式正确）
        if validation_result['valid']:
            try:
                instance, jenkins_token = get_jenkins_instance_with_decrypted_token(instance_id)
                if instance:
                    check_url = f"{instance['url']}/job/{job_name}/api/json"
                    response = requests.get(
                        check_url,
                        auth=HTTPBasicAuth(instance['username'], jenkins_token),
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        validation_result['available'] = False
                        validation_result['errors'].append(f'任务名称 "{job_name}" 已存在')
                        
                        # 提供替代建议
                        base_name = job_name
                        for i in range(1, 6):
                            suggested_name = f"{base_name}-{i}"
                            check_url = f"{instance['url']}/job/{suggested_name}/api/json"
                            response = requests.get(
                                check_url,
                                auth=HTTPBasicAuth(instance['username'], jenkins_token),
                                timeout=5
                            )
                            
                            if response.status_code == 404:
                                validation_result['suggestions'].append(suggested_name)
                                break
                    
            except Exception as e:
                validation_result['suggestions'].append('无法检查任务名称可用性，请手动确认')
        
        # 3. 名称建议
        if validation_result['valid'] and validation_result['available']:
            if not re.search(r'[a-z]', job_name):
                validation_result['suggestions'].append('建议在任务名称中包含小写字母以提高可读性')
            
            if len(job_name.split('-')) == 1 and len(job_name.split('_')) == 1:
                validation_result['suggestions'].append('建议使用连字符分隔词语，如: my-app-prod')
        
        return jsonify({
            'success': True,
            'data': validation_result
        })
        
    except Exception as e:
        logger.error(f"验证Jenkins任务名称失败: {e}")
        return jsonify({'success': False, 'message': f'名称验证失败: {str(e)}'})

# 导入必要的模块
import time
import random 