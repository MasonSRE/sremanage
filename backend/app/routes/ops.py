from flask import Blueprint, request, jsonify
from app.utils.auth import login_required
from app.utils.database import get_db, get_db_connection
import paramiko
import concurrent.futures
import requests
from requests.auth import HTTPBasicAuth
import base64

bp = Blueprint('ops', __name__, url_prefix='/api/ops')

@bp.route('/batch-command', methods=['POST'])
@login_required
def batch_command():
    """批量执行命令（需要认证）"""
    return _batch_command()

@bp.route('/batch-command-test', methods=['POST'])
def batch_command_test():
    """批量执行命令（测试版本，无需认证）"""
    return _batch_command()

def _batch_command():
    """批量执行命令"""
    data = request.get_json()
    
    if not all(key in data for key in ['hosts', 'command']):
        return jsonify({
            'success': False,
            'message': '缺少必要的字段'
        }), 400
    
    results = []
    
    def execute_command(host_id):
        db = get_db_connection()
        try:
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
                        host = {
                            'hostname': host_data['hostname'],
                            'ip': host_data['ip'],
                            'username': host_data['username'],
                            'password': host_data['password'],
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
                            password = password_result['password']
                        
                        # 如果没有找到密码，尝试从手动主机表查找
                        if not password:
                            cursor.execute("SELECT password FROM hosts WHERE ip = %s AND username = %s", (host_data['ip'], 'root'))
                            fallback_result = cursor.fetchone()
                            if fallback_result and fallback_result['password']:
                                password = fallback_result['password']
                        
                        host = {
                            'hostname': host_data['hostname'],
                            'ip': host_data['ip'],
                            'username': 'root',  # 阿里云ECS默认用户
                            'password': password or '',  # 使用查询到的密码
                            'port': 22
                        }
            
            if not host:
                return {
                    'hostname': f'Unknown Host ({host_id})',
                    'ip': 'unknown',
                    'status': 'error',
                    'output': 'Host not found'
                }
            
            try:
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
            except Exception as e:
                return {
                    'hostname': host['hostname'],
                    'ip': host['ip'],
                    'status': 'error',
                    'output': str(e)
                }
            finally:
                try:
                    ssh.close()
                except:
                    pass
        finally:
            db.close()
    
    # 使用线程池并行执行命令
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(execute_command, data['hosts']))
    
    return jsonify({
        'success': True,
        'data': results
    })

@bp.route('/jenkins/jobs/<int:instance_id>', methods=['GET'])
@login_required
def get_jenkins_jobs(instance_id):
    """获取指定Jenkins实例的任务列表"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM jenkins_settings WHERE id = %s', (instance_id,))
            instance = cursor.fetchone()
            
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 调用Jenkins API获取任务列表
        jobs_url = f"{instance['url']}/api/json?tree=jobs[name,url,buildable,lastBuild[number,timestamp,result,duration]]"
        
        response = requests.get(
            jobs_url,
            auth=HTTPBasicAuth(instance['username'], instance['token']),
            timeout=10
        )
        
        if response.status_code == 200:
            jenkins_data = response.json()
            jobs = []
            
            for job in jenkins_data.get('jobs', []):
                last_build = job.get('lastBuild', {})
                jobs.append({
                    'name': job['name'],
                    'url': job['url'],
                    'buildable': job['buildable'],
                    'lastBuildNumber': last_build.get('number', 0),
                    'lastBuildTime': last_build.get('timestamp', 0),
                    'status': last_build.get('result', 'unknown').lower() if last_build.get('result') else 'unknown',
                    'duration': last_build.get('duration', 0)
                })
            
            return jsonify({'success': True, 'data': jobs})
        else:
            return jsonify({'success': False, 'message': 'Jenkins API调用失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@bp.route('/jenkins/build/<int:instance_id>/<job_name>', methods=['POST'])
@login_required
def trigger_jenkins_build(instance_id, job_name):
    """触发Jenkins构建任务"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM jenkins_settings WHERE id = %s', (instance_id,))
            instance = cursor.fetchone()
            
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 触发构建
        build_url = f"{instance['url']}/job/{job_name}/build"
        
        response = requests.post(
            build_url,
            auth=HTTPBasicAuth(instance['username'], instance['token']),
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return jsonify({'success': True, 'message': f'任务 {job_name} 构建已触发'})
        else:
            return jsonify({'success': False, 'message': 'Jenkins构建触发失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@bp.route('/jenkins/test/<int:instance_id>', methods=['POST'])
@login_required
def test_jenkins_connection(instance_id):
    """测试Jenkins连接"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM jenkins_settings WHERE id = %s', (instance_id,))
            instance = cursor.fetchone()
            
        if not instance:
            return jsonify({'success': False, 'message': 'Jenkins实例不存在'})
        
        # 测试连接
        test_url = f"{instance['url']}/api/json"
        
        response = requests.get(
            test_url,
            auth=HTTPBasicAuth(instance['username'], instance['token']),
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Jenkins连接测试成功'})
        else:
            return jsonify({'success': False, 'message': f'Jenkins连接测试失败: HTTP {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'连接测试失败: {str(e)}'})
    finally:
        db.close() 