from flask import Blueprint, request, jsonify
from app.utils.auth import login_required
from app.utils.database import get_db_connection
from app.utils.aliyun import get_aliyun_service
from app.utils.cloud_providers import get_aliyun_credentials, get_cloud_service_instance
import logging

logger = logging.getLogger(__name__)
aliyun = Blueprint('aliyun', __name__)

# get_aliyun_credentials 函数现在从 cloud_providers 模块导入
# 保持向后兼容性

@aliyun.route('/api/aliyun/ecs/instances', methods=['GET'])
@login_required
def get_ecs_instances():
    """获取ECS实例列表（支持缓存）"""
    db = get_db_connection()
    try:
        # 检查是否强制刷新
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        # 如果不是强制刷新，先尝试从缓存获取
        if not force_refresh:
            cached_instances = get_cached_ecs_instances(db)
            if cached_instances:
                logger.info(f"从缓存返回 {len(cached_instances)} 个ECS实例")
                return jsonify({
                    'success': True,
                    'data': cached_instances,
                    'count': len(cached_instances),
                    'from_cache': True,
                    'last_sync_time': get_last_sync_time(db, 'ecs')
                })
        
        # 检查阿里云配置
        access_key_id, access_key_secret = get_aliyun_credentials()
        if not access_key_id or not access_key_secret:
            # 即使没有配置，也尝试返回缓存数据
            cached_instances = get_cached_ecs_instances(db)
            return jsonify({
                'success': False if not cached_instances else True,
                'message': '请先配置阿里云访问凭证' if not cached_instances else '',
                'data': cached_instances or [],
                'from_cache': bool(cached_instances)
            })
        
        # 执行同步
        logger.info("开始同步ECS实例...")
        update_sync_status(db, 'ecs', 'running')
        
        aliyun_service = get_aliyun_service(access_key_id, access_key_secret)
        
        # 获取所有区域的实例
        region = request.args.get('region')
        if region:
            instances = aliyun_service.get_ecs_instances(region)
        else:
            instances = aliyun_service.get_all_regions_instances()
        
        # 更新缓存
        update_ecs_cache(db, instances)
        update_sync_status(db, 'ecs', 'completed', len(instances))
        
        logger.info(f"同步完成，共 {len(instances)} 个实例")
        
        return jsonify({
            'success': True,
            'data': instances,
            'count': len(instances),
            'from_cache': False,
            'synced_at': get_last_sync_time(db, 'ecs')
        })
        
    except Exception as e:
        logger.error(f"获取ECS实例失败: {str(e)}")
        update_sync_status(db, 'ecs', 'failed', 0, str(e))
        
        # 发生错误时尝试返回缓存数据
        try:
            cached_instances = get_cached_ecs_instances(db)
            if cached_instances:
                return jsonify({
                    'success': True,
                    'data': cached_instances,
                    'count': len(cached_instances),
                    'from_cache': True,
                    'warning': f'同步失败，返回缓存数据: {str(e)}'
                })
        except:
            pass
            
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        })
    finally:
        db.close()

def get_cached_ecs_instances(db):
    """从缓存获取ECS实例列表"""
    try:
        with db.cursor() as cursor:
            cursor.execute('''
                SELECT instance_id, instance_name, hostname, status, instance_type, 
                       image_id, public_ip, private_ip, region, zone, creation_time,
                       os_type, cpu, memory, provider, last_sync_time
                FROM aliyun_ecs_cache 
                ORDER BY last_sync_time DESC, region, instance_name
            ''')
            results = cursor.fetchall()
            
            instances = []
            for row in results:
                instances.append({
                    'id': row['instance_id'],
                    'name': row['instance_name'],
                    'hostname': row['hostname'],
                    'status': row['status'],
                    'instance_type': row['instance_type'],
                    'image_id': row['image_id'],
                    'public_ip': row['public_ip'],
                    'private_ip': row['private_ip'],
                    'region': row['region'],
                    'zone': row['zone'],
                    'creation_time': row['creation_time'],
                    'os_type': row['os_type'],
                    'cpu': row['cpu'],
                    'memory': row['memory'],
                    'provider': row['provider']
                })
            
            return instances
    except Exception as e:
        logger.error(f"获取缓存ECS实例失败: {str(e)}")
        return []

def update_ecs_cache(db, instances):
    """更新ECS实例缓存"""
    try:
        with db.cursor() as cursor:
            # 清空现有缓存
            cursor.execute('DELETE FROM aliyun_ecs_cache')
            
            # 插入新数据
            for instance in instances:
                cursor.execute('''
                    INSERT INTO aliyun_ecs_cache 
                    (instance_id, instance_name, hostname, status, instance_type, image_id,
                     public_ip, private_ip, region, zone, creation_time, os_type, cpu, memory, provider)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    instance.get('id'),
                    instance.get('name'),
                    instance.get('hostname'),
                    instance.get('status'),
                    instance.get('instance_type'),
                    instance.get('image_id'),
                    instance.get('public_ip'),
                    instance.get('private_ip'),
                    instance.get('region'),
                    instance.get('zone'),
                    instance.get('creation_time'),
                    instance.get('os_type'),
                    instance.get('cpu'),
                    instance.get('memory'),
                    instance.get('provider', 'aliyun')
                ))
        
        db.commit()
        logger.info(f"缓存已更新，共 {len(instances)} 个实例")
        
    except Exception as e:
        logger.error(f"更新ECS缓存失败: {str(e)}")
        db.rollback()

def update_sync_status(db, sync_type, status, count=0, error_message=None):
    """更新同步状态"""
    try:
        with db.cursor() as cursor:
            cursor.execute('''
                INSERT INTO aliyun_sync_status (sync_type, sync_status, total_count, error_message)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                sync_status = VALUES(sync_status),
                total_count = VALUES(total_count),
                error_message = VALUES(error_message),
                last_sync_time = CURRENT_TIMESTAMP
            ''', (sync_type, status, count, error_message))
        
        db.commit()
        
    except Exception as e:
        logger.error(f"更新同步状态失败: {str(e)}")

def get_last_sync_time(db, sync_type):
    """获取最后同步时间"""
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT last_sync_time FROM aliyun_sync_status WHERE sync_type = %s',
                (sync_type,)
            )
            result = cursor.fetchone()
            if result:
                return result['last_sync_time'].strftime('%Y-%m-%d %H:%M:%S')
        return None
    except Exception as e:
        logger.error(f"获取同步时间失败: {str(e)}")
        return None

@aliyun.route('/api/aliyun/ecs/sync-status', methods=['GET'])
@login_required
def get_sync_status():
    """获取同步状态"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute('''
                SELECT sync_type, sync_status, total_count, last_sync_time, error_message
                FROM aliyun_sync_status 
                WHERE sync_type = 'ecs'
            ''')
            result = cursor.fetchone()
            
            if result:
                return jsonify({
                    'success': True,
                    'data': {
                        'sync_status': result['sync_status'],
                        'total_count': result['total_count'],
                        'last_sync_time': result['last_sync_time'].strftime('%Y-%m-%d %H:%M:%S') if result['last_sync_time'] else None,
                        'error_message': result['error_message']
                    }
                })
            else:
                return jsonify({
                    'success': True,
                    'data': {
                        'sync_status': 'completed',
                        'total_count': 0,
                        'last_sync_time': None,
                        'error_message': None
                    }
                })
                
    except Exception as e:
        logger.error(f"获取同步状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })
    finally:
        db.close()

@aliyun.route('/api/aliyun/domains', methods=['GET'])
@login_required
def get_domains():
    """获取域名列表"""
    try:
        access_key_id, access_key_secret = get_aliyun_credentials()
        
        if not access_key_id or not access_key_secret:
            return jsonify({
                'success': False,
                'message': '请先配置阿里云访问凭证',
                'data': []
            })
        
        aliyun_service = get_aliyun_service(access_key_id, access_key_secret)
        domains = aliyun_service.get_domains()
        
        return jsonify({
            'success': True,
            'data': domains,
            'count': len(domains)
        })
        
    except Exception as e:
        logger.error(f"获取域名列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        })

@aliyun.route('/api/aliyun/cdn/domains', methods=['GET'])
@login_required
def get_cdn_domains():
    """获取CDN域名列表"""
    try:
        access_key_id, access_key_secret = get_aliyun_credentials()
        
        if not access_key_id or not access_key_secret:
            return jsonify({
                'success': False,
                'message': '请先配置阿里云访问凭证',
                'data': []
            })
        
        aliyun_service = get_aliyun_service(access_key_id, access_key_secret)
        domains = aliyun_service.get_cdn_domains()
        
        return jsonify({
            'success': True,
            'data': domains,
            'count': len(domains)
        })
        
    except Exception as e:
        logger.error(f"获取CDN域名列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        })

@aliyun.route('/api/aliyun/cdn/refresh', methods=['POST'])
@login_required
def refresh_cdn_cache():
    """刷新CDN缓存"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({
                'success': False,
                'message': 'URLs参数不能为空'
            })
        
        access_key_id, access_key_secret = get_aliyun_credentials()
        
        if not access_key_id or not access_key_secret:
            return jsonify({
                'success': False,
                'message': '请先配置阿里云访问凭证'
            })
        
        aliyun_service = get_aliyun_service(access_key_id, access_key_secret)
        result = aliyun_service.refresh_cdn_cache(urls)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"CDN缓存刷新失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@aliyun.route('/api/aliyun/cdn/preload', methods=['POST'])
@login_required
def preload_cdn_cache():
    """CDN缓存预热"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({
                'success': False,
                'message': 'URLs参数不能为空'
            })
        
        access_key_id, access_key_secret = get_aliyun_credentials()
        
        if not access_key_id or not access_key_secret:
            return jsonify({
                'success': False,
                'message': '请先配置阿里云访问凭证'
            })
        
        aliyun_service = get_aliyun_service(access_key_id, access_key_secret)
        result = aliyun_service.preload_cdn_cache(urls)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"CDN缓存预热失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@aliyun.route('/api/aliyun/test', methods=['POST'])
@login_required
def test_credentials():
    """测试阿里云凭证"""
    try:
        access_key_id, access_key_secret = get_aliyun_credentials()
        
        if not access_key_id or not access_key_secret:
            return jsonify({
                'success': False,
                'message': '请先配置阿里云访问凭证'
            })
        
        # 通过获取ECS实例来测试凭证是否有效
        aliyun_service = get_aliyun_service(access_key_id, access_key_secret)
        aliyun_service.get_ecs_instances('cn-hangzhou')
        
        return jsonify({
            'success': True,
            'message': '阿里云凭证验证成功'
        })
        
    except Exception as e:
        logger.error(f"阿里云凭证测试失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'凭证验证失败: {str(e)}'
        })

@aliyun.route('/api/aliyun/instance/config/<instance_id>', methods=['GET', 'PUT'])
@login_required
def manage_instance_config(instance_id):
    """管理阿里云实例连接配置（向后兼容）"""
    db = get_db_connection()
    
    if request.method == 'GET':
        try:
            with db.cursor() as cursor:
                # 优先从新表获取配置
                cursor.execute("""
                    SELECT cic.ssh_port, cic.username, cic.password 
                    FROM cloud_instance_config cic
                    JOIN cloud_providers cp ON cic.provider_id = cp.id
                    WHERE cp.provider = 'aliyun' AND cic.instance_id = %s
                    ORDER BY cp.created_at ASC
                    LIMIT 1
                """, (instance_id,))
                config = cursor.fetchone()
                
                # 如果新表没有，尝试从旧表获取（兼容性）
                if not config:
                    cursor.execute(
                        'SELECT ssh_port, username, password FROM aliyun_instance_config WHERE instance_id = %s',
                        (instance_id,)
                    )
                    config = cursor.fetchone()
                
                if config:
                    return jsonify({
                        'success': True,
                        'data': {
                            'ssh_port': config['ssh_port'],
                            'username': config['username'],
                            'password': config['password'] or ''  # 不返回实际密码，只返回是否有密码
                        }
                    })
                else:
                    # 返回默认配置
                    return jsonify({
                        'success': True,
                        'data': {
                            'ssh_port': 22,
                            'username': 'root',
                            'password': ''
                        }
                    })
        except Exception as e:
            logger.error(f"获取实例配置失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            })
        finally:
            db.close()
    
    elif request.method == 'PUT':
        data = request.get_json()
        try:
            with db.cursor() as cursor:
                # 获取默认的阿里云配置ID
                cursor.execute("""
                    SELECT id FROM cloud_providers 
                    WHERE provider = 'aliyun' AND enabled = 1
                    ORDER BY created_at ASC
                    LIMIT 1
                """)
                provider = cursor.fetchone()
                
                if provider:
                    # 使用新表结构
                    cursor.execute("""
                        INSERT INTO cloud_instance_config 
                        (provider_id, instance_id, ssh_port, username, password)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            ssh_port = VALUES(ssh_port),
                            username = VALUES(username),
                            password = VALUES(password),
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        provider['id'],
                        instance_id,
                        data.get('ssh_port', 22),
                        data.get('username', 'root'),
                        data.get('password', '')
                    ))
                else:
                    # 降级到旧表（向后兼容）
                    cursor.execute(
                        '''REPLACE INTO aliyun_instance_config 
                           (instance_id, ssh_port, username, password) 
                           VALUES (%s, %s, %s, %s)''',
                        (
                            instance_id,
                            data.get('ssh_port', 22),
                            data.get('username', 'root'),
                            data.get('password', '')
                        )
                    )
            db.commit()
            
            return jsonify({
                'success': True,
                'message': '配置更新成功'
            })
            
        except Exception as e:
            logger.error(f"更新实例配置失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            })
        finally:
            db.close()

@aliyun.route('/api/aliyun/instance/config', methods=['GET'])
@login_required  
def get_all_instance_configs():
    """获取所有阿里云实例的连接配置"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT instance_id, ssh_port, username FROM aliyun_instance_config'
            )
            configs = cursor.fetchall()
            
            config_dict = {}
            for config in configs:
                config_dict[config['instance_id']] = {
                    'ssh_port': config['ssh_port'],
                    'username': config['username']
                }
            
            return jsonify({
                'success': True,
                'data': config_dict
            })
            
    except Exception as e:
        logger.error(f"获取所有实例配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {}
        })
    finally:
        db.close()