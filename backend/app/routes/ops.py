from flask import Blueprint, request, jsonify
from app.utils.auth import login_required
from app.utils.database import get_db, get_db_connection
from app.utils.security import decrypt_sensitive_data, encrypt_sensitive_data, is_data_encrypted
from app.utils.db_context import database_connection
from app.utils.response import APIResponse, api_response
from app.utils.validation import validate_json_schema, validators, StringValidator, ListValidator
import paramiko
import concurrent.futures
import requests
from requests.auth import HTTPBasicAuth
import base64
import logging

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