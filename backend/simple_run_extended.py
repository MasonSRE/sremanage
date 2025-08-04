#!/usr/bin/env python3
"""
扩展版简化后端启动文件，包含Jenkins所有必要的API
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        raise

@app.route('/api/settings/jenkins', methods=['GET', 'POST'])
def jenkins_settings():
    """Jenkins设置API"""
    print(f"收到请求: {request.method} /api/settings/jenkins")
    
    if request.method == 'GET':
        try:
            db = get_db_connection()
            with db.cursor() as cursor:
                # 首先检查表是否存在
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'jenkins_settings'
                """)
                table_exists = cursor.fetchone()['count'] > 0
                
                if not table_exists:
                    # 表不存在，创建表
                    print("jenkins_settings表不存在，正在创建...")
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS jenkins_settings (
                            id INTEGER AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            url TEXT NOT NULL,
                            username VARCHAR(100) NOT NULL,
                            token TEXT NOT NULL,
                            enabled BOOLEAN NOT NULL DEFAULT 1,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        )
                    """)
                    db.commit()
                    print("jenkins_settings表创建成功")
                
                cursor.execute('SELECT * FROM jenkins_settings ORDER BY id')
                instances = cursor.fetchall()
            db.close()
            
            result = {
                'success': True,
                'data': [{
                    'id': instance['id'],
                    'name': instance['name'],
                    'url': instance['url'],
                    'username': instance['username'],
                    'enabled': bool(instance['enabled'])
                } for instance in instances]
            }
            
            print(f"返回数据: {result}")
            return jsonify(result)
            
        except Exception as e:
            print(f"获取Jenkins实例失败: {e}")
            return jsonify({
                'success': False,
                'message': f'获取Jenkins实例失败: {str(e)}',
                'data': []
            }), 500
    
    # POST 请求处理
    data = request.get_json()
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            # 检查表是否存在，如果不存在则创建
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'jenkins_settings'
            """)
            table_exists = cursor.fetchone()['count'] > 0
            
            if not table_exists:
                print("jenkins_settings表不存在，正在创建...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jenkins_settings (
                        id INTEGER AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        url TEXT NOT NULL,
                        username VARCHAR(100) NOT NULL,
                        token TEXT NOT NULL,
                        enabled BOOLEAN NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                db.commit()
                print("jenkins_settings表创建成功")
            
            cursor.execute(
                'INSERT INTO jenkins_settings (name, url, username, token, enabled) VALUES (%s, %s, %s, %s, %s)',
                (data['name'], data['url'], data['username'], data['token'], data.get('enabled', True))
            )
        db.commit()
        db.close()
        return jsonify({'success': True, 'message': 'Jenkins实例添加成功'})
    except Exception as e:
        print(f"添加Jenkins实例失败: {e}")
        return jsonify({
            'success': False,
            'message': f'添加Jenkins实例失败: {str(e)}'
        }), 500

@app.route('/api/settings/jenkins/<int:instance_id>', methods=['PUT', 'DELETE'])
def jenkins_instance(instance_id):
    """Jenkins实例管理API"""
    print(f"收到请求: {request.method} /api/settings/jenkins/{instance_id}")
    
    db = get_db_connection()
    
    if request.method == 'PUT':
        data = request.get_json()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    'UPDATE jenkins_settings SET name=%s, url=%s, username=%s, token=%s, enabled=%s WHERE id=%s',
                    (data['name'], data['url'], data['username'], data['token'], data.get('enabled', True), instance_id)
                )
            db.commit()
            db.close()
            return jsonify({'success': True, 'message': 'Jenkins实例更新成功'})
        except Exception as e:
            print(f"更新Jenkins实例失败: {e}")
            return jsonify({
                'success': False,
                'message': f'更新Jenkins实例失败: {str(e)}'
            }), 500
    
    elif request.method == 'DELETE':
        try:
            with db.cursor() as cursor:
                cursor.execute('DELETE FROM jenkins_settings WHERE id=%s', (instance_id,))
            db.commit()
            db.close()
            return jsonify({'success': True, 'message': 'Jenkins实例删除成功'})
        except Exception as e:
            print(f"删除Jenkins实例失败: {e}")
            return jsonify({
                'success': False,
                'message': f'删除Jenkins实例失败: {str(e)}'
            }), 500

@app.route('/api/cloud-providers', methods=['GET'])
def cloud_providers_simple():
    """云厂商配置API - 简化版"""
    print(f"收到云厂商配置请求")
    
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            # 首先检查表是否存在
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'cloud_providers'
            """)
            table_exists = cursor.fetchone()['count'] > 0
            
            if not table_exists:
                # 表不存在，创建表
                print("cloud_providers表不存在，正在创建...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `cloud_providers` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `name` varchar(100) NOT NULL COMMENT '配置名称，如"生产环境阿里云"',
                        `provider` varchar(50) NOT NULL COMMENT '云厂商类型: aliyun, aws, tencent, huawei, google, azure',
                        `config` JSON NOT NULL COMMENT '云厂商配置信息',
                        `region` varchar(50) DEFAULT NULL COMMENT '默认区域',
                        `enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
                        `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        PRIMARY KEY (`id`),
                        KEY `idx_provider` (`provider`),
                        KEY `idx_enabled` (`enabled`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云厂商配置表'
                """)
                db.commit()
                print("cloud_providers表创建成功")
            
            cursor.execute("""
                SELECT id, name, provider, config, region, enabled, created_at, updated_at
                FROM cloud_providers
                ORDER BY created_at DESC
            """)
            providers = cursor.fetchall()
            
            result = {
                'success': True,
                'data': providers
            }
            
        db.close()
        
        print(f"返回云厂商配置数据: {len(providers)} 个配置")
        return jsonify(result)
        
    except Exception as e:
        print(f"获取云厂商配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取云厂商配置失败: {str(e)}',
            'data': []
        }), 500

@app.route('/api/cloud-providers/schemas', methods=['GET'])
def cloud_provider_schemas_simple():
    """云厂商配置字段定义API - 简化版"""
    print(f"收到云厂商字段定义请求")
    
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            # 首先检查表是否存在
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'cloud_provider_schemas'
            """)
            table_exists = cursor.fetchone()['count'] > 0
            
            if not table_exists:
                # 表不存在，创建表
                print("cloud_provider_schemas表不存在，正在创建...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `cloud_provider_schemas` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `provider` varchar(50) NOT NULL COMMENT '云厂商类型',
                        `field_name` varchar(100) NOT NULL COMMENT '字段名称',
                        `field_type` varchar(50) NOT NULL COMMENT '字段类型: text, password, select, number',
                        `field_label` varchar(200) NOT NULL COMMENT '字段显示名称',
                        `is_required` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否必填',
                        `default_value` varchar(500) DEFAULT NULL COMMENT '默认值',
                        `options` JSON DEFAULT NULL COMMENT '选项列表（用于select类型）',
                        `placeholder` varchar(200) DEFAULT NULL COMMENT '占位符',
                        `help_text` varchar(500) DEFAULT NULL COMMENT '帮助文本',
                        `sort_order` int(11) NOT NULL DEFAULT 0 COMMENT '排序顺序',
                        PRIMARY KEY (`id`),
                        KEY `idx_provider` (`provider`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云厂商配置字段定义表'
                """)
                
                # 插入基础的配置字段定义
                cursor.execute("""
                    INSERT INTO `cloud_provider_schemas` (`provider`, `field_name`, `field_type`, `field_label`, `is_required`, `placeholder`, `help_text`, `sort_order`) VALUES
                    ('aliyun', 'access_key_id', 'text', 'Access Key ID', 1, '请输入阿里云Access Key ID', '在阿里云控制台的访问控制RAM中创建', 1),
                    ('aliyun', 'access_key_secret', 'password', 'Access Key Secret', 1, '请输入阿里云Access Key Secret', '对应Access Key ID的密钥', 2),
                    ('aws', 'access_key_id', 'text', 'Access Key ID', 1, '请输入AWS Access Key ID', '在AWS IAM中创建访问密钥', 1),
                    ('aws', 'secret_access_key', 'password', 'Secret Access Key', 1, '请输入AWS Secret Access Key', '对应Access Key ID的密钥', 2),
                    ('tencent', 'secret_id', 'text', 'Secret ID', 1, '请输入腾讯云Secret ID', '在腾讯云控制台的访问管理中创建', 1),
                    ('tencent', 'secret_key', 'password', 'Secret Key', 1, '请输入腾讯云Secret Key', '对应Secret ID的密钥', 2)
                """)
                
                db.commit()
                print("cloud_provider_schemas表创建成功")
            
            cursor.execute("""
                SELECT provider, field_name, field_type, field_label, is_required, 
                       default_value, options, placeholder, help_text, sort_order
                FROM cloud_provider_schemas
                ORDER BY provider, sort_order
            """)
            schemas = cursor.fetchall()
            
            # 按云厂商分组
            result_data = {}
            for schema in schemas:
                provider = schema['provider']
                if provider not in result_data:
                    result_data[provider] = []
                
                result_data[provider].append({
                    'field_name': schema['field_name'],
                    'field_type': schema['field_type'],
                    'field_label': schema['field_label'],
                    'is_required': bool(schema['is_required']),
                    'default_value': schema['default_value'],
                    'options': None,
                    'placeholder': schema['placeholder'],
                    'help_text': schema['help_text'],
                    'sort_order': schema['sort_order']
                })
            
            result = {
                'success': True,
                'data': result_data
            }
            
        db.close()
        
        print(f"返回云厂商字段定义数据: {len(result_data)} 个厂商")
        return jsonify(result)
        
    except Exception as e:
        print(f"获取云厂商字段定义失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取云厂商字段定义失败: {str(e)}',
            'data': {}
        }), 500

@app.route('/api/cloud-providers/supported', methods=['GET'])
def supported_providers_simple():
    """支持的云厂商列表API - 简化版"""
    print(f"收到支持的云厂商列表请求")
    
    providers = [
        {'value': 'aliyun', 'label': '阿里云', 'icon': '🌐'},
        {'value': 'aws', 'label': 'Amazon Web Services', 'icon': '☁️'},
        {'value': 'tencent', 'label': '腾讯云', 'icon': '🐧'},
        {'value': 'huawei', 'label': '华为云', 'icon': '🌸'},
        {'value': 'google', 'label': 'Google Cloud', 'icon': '🔍'},
        {'value': 'azure', 'label': 'Microsoft Azure', 'icon': '🪟'}
    ]
    
    result = {
        'success': True,
        'data': providers
    }
    
    print(f"返回支持的云厂商列表: {len(providers)} 个厂商")
    return jsonify(result)

@app.route('/api/ops/jenkins/metrics/<int:instance_id>', methods=['GET'])
def jenkins_metrics(instance_id):
    """Jenkins性能指标API - 模拟数据"""
    print(f"收到Jenkins性能指标请求: instance_id={instance_id}")
    
    # 模拟数据
    mock_data = {
        'success': True,
        'data': {
            'overview': {
                'builds24h': 45,
                'overallSuccessRate': 87,
                'queueLength': 3,
                'averageBuildDuration': 125000,
                'performanceLevels': {
                    'excellent': 12,
                    'good': 18,
                    'fair': 8,
                    'poor': 7
                }
            },
            'systemInfo': {
                'jenkinsVersion': '2.414.1',
                'mode': 'NORMAL',
                'nodeDescription': 'Jenkins master node',
                'quietingDown': False
            },
            'recentBuilds': [
                {
                    'jobName': 'frontend-build',
                    'number': 123,
                    'status': 'success',
                    'duration': 95000,
                    'timestamp': 1627834567000,
                    'efficiency': 98
                },
                {
                    'jobName': 'backend-test',
                    'number': 67,
                    'status': 'failure',
                    'duration': 180000,
                    'timestamp': 1627834500000,
                    'efficiency': 134
                },
                {
                    'jobName': 'integration-test',
                    'number': 89,
                    'status': 'success',
                    'duration': 156000,
                    'timestamp': 1627834200000,
                    'efficiency': 112
                }
            ],
            'warnings': [
                {
                    'type': 'queue_length',
                    'level': 'warning',
                    'message': '构建队列长度较高，可能影响响应时间',
                    'suggestion': '考虑增加构建节点或优化构建脚本'
                }
            ]
        }
    }
    
    print(f"返回模拟数据: 性能指标数据已生成")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/health-check/<int:instance_id>', methods=['POST'])
def jenkins_health_check(instance_id):
    """Jenkins健康检查API - 模拟数据"""
    print(f"收到Jenkins健康检查请求: instance_id={instance_id}")
    
    mock_data = {
        'success': True,
        'data': {
            'overall': 'healthy',
            'score': 92,
            'checks': {
                'connectivity': {
                    'status': 'healthy',
                    'message': '连接正常',
                    'responseTime': 45
                },
                'system_status': {
                    'status': 'healthy',
                    'message': '系统运行正常',
                    'responseTime': 23
                },
                'queue': {
                    'status': 'warning',
                    'message': '队列中有3个待处理任务',
                    'responseTime': 12
                },
                'recent_builds': {
                    'status': 'healthy',
                    'message': '最近构建正常',
                    'responseTime': 67
                }
            },
            'recommendations': [
                '建议关注队列中的待处理任务',
                '考虑增加构建节点以提高并发能力'
            ]
        }
    }
    
    print(f"返回健康检查数据: 健康状态良好")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/jobs/<int:instance_id>', methods=['GET'])
def jenkins_jobs(instance_id):
    """Jenkins任务列表API - 模拟数据"""
    print(f"收到Jenkins任务列表请求: instance_id={instance_id}")
    
    mock_data = {
        'success': True,
        'data': [
            {
                'name': 'frontend-build',
                'url': 'http://jenkins.example.com/job/frontend-build/',
                'buildable': True,
                'lastBuildNumber': 123,
                'lastBuildTime': 1627834567000,
                'status': 'success',
                'duration': 95000
            },
            {
                'name': 'backend-test',
                'url': 'http://jenkins.example.com/job/backend-test/',
                'buildable': True,
                'lastBuildNumber': 67,
                'lastBuildTime': 1627834500000,
                'status': 'failure',
                'duration': 180000
            },
            {
                'name': 'integration-test',
                'url': 'http://jenkins.example.com/job/integration-test/',
                'buildable': True,
                'lastBuildNumber': 89,
                'lastBuildTime': 1627834200000,
                'status': 'success',
                'duration': 156000
            },
            {
                'name': 'deploy-staging',
                'url': 'http://jenkins.example.com/job/deploy-staging/',
                'buildable': True,
                'lastBuildNumber': 45,
                'lastBuildTime': 1627833800000,
                'status': 'building',
                'duration': 0
            }
        ],
        'message': '成功获取 4 个任务'
    }
    
    print(f"返回任务列表: 4个Jenkins任务")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/status/<int:instance_id>', methods=['GET'])
def jenkins_status(instance_id):
    """Jenkins状态概览API - 模拟数据"""
    print(f"收到Jenkins状态概览请求: instance_id={instance_id}")
    
    mock_data = {
        'success': True,
        'data': {
            'totalJobs': 15,
            'queueCount': 3
        }
    }
    
    print(f"返回状态概览数据")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/queue/<int:instance_id>', methods=['GET'])
def jenkins_queue(instance_id):
    """Jenkins构建队列API - 模拟数据"""
    print(f"收到Jenkins队列请求: instance_id={instance_id}")
    
    mock_data = {
        'success': True,
        'data': [
            {
                'id': 1001,
                'jobName': 'frontend-build',
                'why': 'Waiting for next available executor',
                'inQueueSince': 1627834567000,
                'stuck': False,
                'blocked': False
            },
            {
                'id': 1002,
                'jobName': 'backend-test',
                'why': 'Waiting for upstream build to complete',
                'inQueueSince': 1627834500000,
                'stuck': False,
                'blocked': True
            },
            {
                'id': 1003,
                'jobName': 'deploy-production',
                'why': 'Waiting for manual approval',
                'inQueueSince': 1627834200000,
                'stuck': True,
                'blocked': False
            }
        ]
    }
    
    print(f"返回队列数据: 3个队列项目")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/history/<int:instance_id>', methods=['GET'])
def jenkins_history(instance_id):
    """Jenkins构建历史API - 模拟数据"""
    print(f"收到Jenkins构建历史请求: instance_id={instance_id}")
    
    mock_data = {
        'success': True,
        'data': [
            {
                'id': 'frontend-build-123',
                'jobName': 'frontend-build',
                'number': 123,
                'status': 'success',
                'startTime': 1627834567000,
                'duration': 95000,
                'triggeredBy': 'admin'
            },
            {
                'id': 'backend-test-67',
                'jobName': 'backend-test',
                'number': 67,
                'status': 'failure',
                'startTime': 1627834500000,
                'duration': 180000,
                'triggeredBy': 'webhook'
            },
            {
                'id': 'integration-test-89',
                'jobName': 'integration-test',
                'number': 89,
                'status': 'success',
                'startTime': 1627834200000,
                'duration': 156000,
                'triggeredBy': 'scheduler'
            }
        ]
    }
    
    print(f"返回构建历史: 3条记录")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/test/<int:instance_id>', methods=['POST'])
def jenkins_test(instance_id):
    """Jenkins连接测试API"""
    print(f"收到Jenkins连接测试请求: instance_id={instance_id}")
    
    # 模拟连接测试成功
    mock_data = {
        'success': True,
        'message': 'Jenkins连接测试成功'
    }
    
    print(f"返回连接测试结果: 成功")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/trends/<int:instance_id>', methods=['GET'])
def jenkins_trends(instance_id):
    """Jenkins构建趋势数据API - 模拟数据"""
    print(f"收到Jenkins构建趋势请求: instance_id={instance_id}")
    
    # 获取查询参数
    days = request.args.get('days', 7, type=int)
    interval = request.args.get('interval', 'daily')
    
    print(f"查询参数: days={days}, interval={interval}")
    
    # 模拟趋势数据
    import time
    import random
    
    current_time = int(time.time() * 1000)
    day_ms = 24 * 60 * 60 * 1000
    
    trends = []
    for i in range(days):
        day_start = current_time - (i * day_ms)
        total_builds = random.randint(5, 25)
        success_builds = random.randint(int(total_builds * 0.6), int(total_builds * 0.95))
        failure_builds = total_builds - success_builds
        building_builds = random.randint(0, 2)
        
        trends.append({
            'time': time.strftime('%Y-%m-%d', time.localtime(day_start / 1000)),
            'timestamp': day_start,
            'total': total_builds,
            'success': success_builds,
            'failure': failure_builds,
            'building': building_builds,
            'successRate': round((success_builds / total_builds) * 100, 1) if total_builds > 0 else 0,
            'averageDuration': random.randint(60000, 300000)  # 1-5分钟
        })
    
    # 反转列表使时间从旧到新排列
    trends.reverse()
    
    # 计算汇总统计
    total_builds = sum(t['total'] for t in trends)
    total_success = sum(t['success'] for t in trends)
    
    summary = {
        'totalPeriods': len(trends),
        'overallSuccessRate': round((total_success / total_builds) * 100, 1) if total_builds > 0 else 0,
        'averageBuildsPerPeriod': round(total_builds / len(trends), 1) if trends else 0,
        'totalBuilds': total_builds,
        'totalSuccess': total_success,
        'totalFailure': sum(t['failure'] for t in trends),
        'averageDuration': sum(t['averageDuration'] for t in trends) // len(trends) if trends else 0
    }
    
    mock_data = {
        'success': True,
        'data': {
            'trends': trends,
            'summary': summary,
            'period': {
                'days': days,
                'interval': interval,
                'startTime': trends[0]['timestamp'] if trends else current_time,
                'endTime': trends[-1]['timestamp'] if trends else current_time
            }
        }
    }
    
    print(f"返回趋势数据: {len(trends)}天的数据，总构建数{total_builds}")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/analytics/<int:instance_id>', methods=['GET'])
def jenkins_analytics(instance_id):
    """Jenkins构建分析数据API - 模拟数据"""
    print(f"收到Jenkins构建分析请求: instance_id={instance_id}")
    
    # 获取查询参数
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    import time
    import random
    
    current_time = int(time.time() * 1000)
    
    # 模拟构建记录
    builds = []
    job_names = ['frontend-build', 'backend-test', 'integration-test', 'deploy-staging', 'api-test']
    
    for i in range(limit):
        build_time = current_time - (i * random.randint(3600000, 14400000))  # 1-4小时前
        job_name = random.choice(job_names)
        status = random.choice(['success', 'failure', 'success', 'success'])  # 偏向成功
        duration = random.randint(30000, 600000)  # 30秒到10分钟
        
        builds.append({
            'id': f"{job_name}-{100 + i}",
            'jobName': job_name,
            'number': 100 + i,
            'status': status,
            'duration': duration,
            'timestamp': build_time,
            'startTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(build_time / 1000)),
            'triggeredBy': random.choice(['admin', 'webhook', 'scheduler', 'user1']),
            'branch': random.choice(['main', 'develop', 'feature/new-ui', 'hotfix/bug-123'])
        })
    
    # 计算摘要统计
    total_builds = len(builds)
    success_builds = len([b for b in builds if b['status'] == 'success'])
    failure_builds = len([b for b in builds if b['status'] == 'failure'])
    avg_duration = sum(b['duration'] for b in builds) // total_builds if total_builds > 0 else 0
    
    summary = {
        'totalBuilds': total_builds,
        'successBuilds': success_builds,
        'failureBuilds': failure_builds,
        'successRate': round((success_builds / total_builds) * 100, 1) if total_builds > 0 else 0,
        'averageDuration': avg_duration,
        'mostActiveJob': max(job_names, key=lambda x: len([b for b in builds if b['jobName'] == x])),
        'totalDuration': sum(b['duration'] for b in builds)
    }
    
    # 任务统计
    job_stats = {}
    for job_name in job_names:
        job_builds = [b for b in builds if b['jobName'] == job_name]
        if job_builds:
            job_success = len([b for b in job_builds if b['status'] == 'success'])
            job_stats[job_name] = {
                'totalBuilds': len(job_builds),
                'successBuilds': job_success,
                'failureBuilds': len(job_builds) - job_success,
                'successRate': round((job_success / len(job_builds)) * 100, 1),
                'averageDuration': sum(b['duration'] for b in job_builds) // len(job_builds),
                'lastBuildTime': max(b['timestamp'] for b in job_builds)
            }
    
    mock_data = {
        'success': True,
        'data': {
            'summary': summary,
            'jobStats': job_stats,
            'builds': builds
        }
    }
    
    print(f"返回构建分析数据: {total_builds}个构建记录，{len(job_stats)}个任务统计")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/prediction/<int:instance_id>', methods=['GET'])
def jenkins_prediction(instance_id):
    """Jenkins预测分析API - 模拟数据"""
    print(f"收到Jenkins预测分析请求: instance_id={instance_id}")
    
    import random
    import time
    
    current_time = int(time.time() * 1000)
    
    # 模拟预测数据
    predictions = {
        'buildTimePrediction': {
            'nextBuildEstimate': random.randint(180000, 480000),  # 3-8分钟
            'confidence': random.randint(75, 95),
            'factors': [
                '基于历史构建时间分析',
                '考虑当前系统负载',
                '代码变更量评估'
            ]
        },
        'failurePrediction': {
            'riskLevel': random.choice(['low', 'medium', 'high']),
            'probability': random.randint(5, 25),
            'riskFactors': [
                '最近失败率增加',
                '依赖服务不稳定',
                '测试覆盖率下降'
            ]
        },
        'resourcePrediction': {
            'peakHours': ['09:00-11:00', '14:00-16:00'],
            'recommendedExecutors': random.randint(3, 8),
            'estimatedQueueTime': random.randint(30000, 180000)
        },
        'trends': {
            'buildFrequency': 'increasing',
            'successRate': 'stable',
            'averageDuration': 'decreasing'
        }
    }
    
    mock_data = {
        'success': True,
        'data': predictions
    }
    
    print(f"返回预测分析数据")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/failure-analysis/<int:instance_id>', methods=['GET'])
def jenkins_failure_analysis(instance_id):
    """Jenkins失败分析API - 模拟数据"""
    print(f"收到Jenkins失败分析请求: instance_id={instance_id}")
    
    import random
    
    # 模拟失败分析数据
    failure_data = {
        'summary': {
            'totalFailures': random.randint(15, 45),
            'uniqueErrors': random.randint(5, 12),
            'mostFailedJob': 'backend-test',
            'failureRate': random.randint(8, 25)
        },
        'errorPatterns': [
            {
                'type': 'compilation_error',
                'count': random.randint(5, 15),
                'percentage': random.randint(20, 40),
                'description': '编译错误',
                'commonCauses': ['语法错误', '依赖缺失', '版本冲突']
            },
            {
                'type': 'test_failure',
                'count': random.randint(3, 10),
                'percentage': random.randint(15, 30),
                'description': '测试失败',
                'commonCauses': ['单元测试失败', '集成测试超时', '环境问题']
            },
            {
                'type': 'deployment_error',
                'count': random.randint(2, 8),
                'percentage': random.randint(10, 25),
                'description': '部署错误',
                'commonCauses': ['权限问题', '网络超时', '资源不足']
            }
        ],
        'jobFailures': {
            'backend-test': {
                'failures': random.randint(8, 20),
                'rate': random.randint(15, 35),
                'topErrors': ['测试超时', '数据库连接失败', '内存溢出']
            },
            'frontend-build': {
                'failures': random.randint(3, 12),
                'rate': random.randint(5, 20),
                'topErrors': ['编译错误', 'npm 依赖问题', '构建脚本错误']
            }
        },
        'recommendations': [
            '优化测试用例，减少执行时间',
            '增加构建环境的资源配置',
            '改进错误日志记录和监控',
            '建立构建失败自动重试机制'
        ]
    }
    
    mock_data = {
        'success': True,
        'data': failure_data
    }
    
    print(f"返回失败分析数据: {failure_data['summary']['totalFailures']}个失败记录")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/optimization-recommendations/<int:instance_id>', methods=['GET'])
def jenkins_optimization_recommendations(instance_id):
    """Jenkins优化建议API - 模拟数据"""
    print(f"收到Jenkins优化建议请求: instance_id={instance_id}")
    
    import random
    
    recommendations = {
        'performanceOptimizations': [
            {
                'category': 'build_speed',
                'title': '构建速度优化',
                'priority': 'high',
                'impact': 'medium',
                'suggestions': [
                    '启用并行构建',
                    '使用构建缓存',
                    '优化Docker镜像层'
                ],
                'estimatedImprovement': '减少30%构建时间'
            },
            {
                'category': 'resource_usage',
                'title': '资源使用优化',
                'priority': 'medium',
                'impact': 'high',
                'suggestions': [
                    '调整执行器数量',
                    '优化内存分配',
                    '清理无用的工作空间'
                ],
                'estimatedImprovement': '节省40%资源消耗'
            }
        ],
        'reliabilityImprovements': [
            {
                'category': 'stability',
                'title': '构建稳定性提升',
                'priority': 'high',
                'impact': 'high',
                'suggestions': [
                    '增加重试机制',
                    '改进错误处理',
                    '监控关键指标'
                ],
                'estimatedImprovement': '提高15%成功率'
            }
        ],
        'securityEnhancements': [
            {
                'category': 'access_control',
                'title': '访问控制增强',
                'priority': 'medium',
                'impact': 'medium',
                'suggestions': [
                    '实施基于角色的访问控制',
                    '定期审查用户权限',
                    '启用审计日志'
                ],
                'estimatedImprovement': '提高安全性'
            }
        ],
        'overallScore': random.randint(75, 90),
        'implementationPlan': {
            'immediate': ['启用构建缓存', '调整执行器配置'],
            'shortTerm': ['实施并行构建', '优化测试流程'],
            'longTerm': ['架构重构', '监控系统升级']
        }
    }
    
    mock_data = {
        'success': True,
        'data': recommendations
    }
    
    print(f"返回优化建议数据: {len(recommendations['performanceOptimizations']) + len(recommendations['reliabilityImprovements']) + len(recommendations['securityEnhancements'])}项建议")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/build/<int:instance_id>/<job_name>', methods=['POST'])
def jenkins_trigger_build(instance_id, job_name):
    """Jenkins触发构建API - 模拟数据"""
    print(f"收到Jenkins触发构建请求: instance_id={instance_id}, job_name={job_name}")
    
    import random
    
    # 模拟构建触发
    build_number = random.randint(100, 999)
    queue_location = f"http://jenkins.example.com/queue/item/{random.randint(1000, 9999)}/"
    
    mock_data = {
        'success': True,
        'data': {
            'jobName': job_name,
            'buildNumber': build_number,
            'queueLocation': queue_location,
            'buildTriggered': True,
            'estimatedStartTime': '约30秒后开始'
        },
        'message': f'任务 {job_name} 构建已触发'
    }
    
    print(f"返回构建触发结果: #{build_number}")
    return jsonify(mock_data)

@app.route('/api/ops/jenkins/build/<int:instance_id>/<job_name>/<int:build_number>/log', methods=['GET'])
def jenkins_build_log(instance_id, job_name, build_number):
    """Jenkins构建日志API - 模拟数据"""
    print(f"收到Jenkins构建日志请求: instance_id={instance_id}, job_name={job_name}, build_number={build_number}")
    
    # 模拟构建日志
    import time
    
    mock_log = f"""Started by user admin
Running as SYSTEM
Building in workspace /var/jenkins_home/workspace/{job_name}
[{job_name}] $ git rev-parse --resolve-git-dir /var/jenkins_home/workspace/{job_name}/.git # timeout=10
[{job_name}] $ git config remote.origin.url # timeout=10
[{job_name}] $ git config --get remote.origin.url # timeout=10
[{job_name}] $ git rev-parse --verify HEAD # timeout=10
[{job_name}] $ git config core.sparsecheckout # timeout=10
[{job_name}] $ git checkout -f HEAD
Previous HEAD position was abc1234... Update README.md
HEAD is now at def5678... Fix build configuration
[{job_name}] $ /bin/bash -xe /tmp/jenkins_build_script.sh

+ echo 'Starting build process...'
Starting build process...
+ npm install
npm WARN deprecated package@1.0.0: This package is deprecated
added 1234 packages from 567 contributors and audited 5678 packages in 45.678s

+ npm run build
> {job_name}@1.0.0 build
> webpack --mode production

Hash: 9a8b7c6d5e4f3g2h
Version: webpack 5.72.0
Time: 12345ms
Built at: {time.strftime('%Y-%m-%d %H:%M:%S')}
Asset       Size  Chunks                         Chunk Names
main.js     1.2 MB    0  [emitted]  [big]         main
index.html  0.5 kB    0  [emitted]                index

+ npm test
> {job_name}@1.0.0 test
> jest

PASS src/components/App.test.js
PASS src/utils/helpers.test.js
PASS src/services/api.test.js

Test Suites: 3 passed, 3 total
Tests:       15 passed, 15 total
Snapshots:   0 total
Time:        12.345 s
Ran all test suites.

+ echo 'Build completed successfully!'
Build completed successfully!

Finished: SUCCESS"""
    
    mock_data = {
        'success': True,
        'data': {
            'log': mock_log,
            'jobName': job_name,
            'buildNumber': build_number,
            'timestamp': int(time.time() * 1000),
            'size': len(mock_log)
        }
    }
    
    print(f"返回构建日志: {len(mock_log)} 字符")
    return jsonify(mock_data)

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'Extended simple backend is running'})

if __name__ == '__main__':
    print("启动扩展版简化后端服务...")
    print(f"数据库配置: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
    print("支持的API端点:")
    print("  - Jenkins设置: /api/settings/jenkins")
    print("  - Jenkins性能指标: /api/ops/jenkins/metrics/<id>")
    print("  - Jenkins健康检查: /api/ops/jenkins/health-check/<id>")
    print("  - Jenkins任务列表: /api/ops/jenkins/jobs/<id>")
    print("  - Jenkins状态概览: /api/ops/jenkins/status/<id>")
    print("  - Jenkins构建队列: /api/ops/jenkins/queue/<id>")
    print("  - Jenkins构建历史: /api/ops/jenkins/history/<id>")
    print("  - Jenkins构建趋势: /api/ops/jenkins/trends/<id>")
    print("  - Jenkins构建分析: /api/ops/jenkins/analytics/<id>")
    print("  - Jenkins预测分析: /api/ops/jenkins/prediction/<id>")
    print("  - Jenkins失败分析: /api/ops/jenkins/failure-analysis/<id>")
    print("  - Jenkins优化建议: /api/ops/jenkins/optimization-recommendations/<id>")
    print("  - Jenkins触发构建: /api/ops/jenkins/build/<id>/<job_name>")
    print("  - Jenkins构建日志: /api/ops/jenkins/build/<id>/<job_name>/<build_number>/log")
    print("  - Jenkins连接测试: /api/ops/jenkins/test/<id>")
    app.run(host='0.0.0.0', port=5001, debug=True)