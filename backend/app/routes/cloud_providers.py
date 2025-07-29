from flask import Blueprint, request, jsonify
from app.utils.auth import login_required
from app.utils.database import get_db_connection
import json
import logging
import pymysql

logger = logging.getLogger(__name__)

cloud_providers = Blueprint('cloud_providers', __name__)

@cloud_providers.route('/api/cloud-providers-test', methods=['GET', 'OPTIONS'])
def get_cloud_providers_test():
    """获取所有云厂商配置 - 测试接口，不需要认证"""
    if request.method == 'OPTIONS':
        return '', 200
        
    db = get_db_connection()
    try:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT id, name, provider, config, region, enabled, created_at, updated_at
            FROM cloud_providers
            ORDER BY created_at DESC
        """)
        providers = cursor.fetchall()
        
        # 隐藏敏感信息
        for provider in providers:
            config = json.loads(provider['config'])
            # 隐藏密钥信息，只显示前几位
            for key in config:
                if 'secret' in key.lower() or 'key' in key.lower():
                    if len(config[key]) > 8:
                        config[key] = config[key][:4] + '*' * 8 + config[key][-4:]
                    else:
                        config[key] = '*' * len(config[key])
            provider['config'] = config
        
        return jsonify({
            'success': True,
            'data': providers,
            'debug': {
                'message': '测试接口，无需认证',
                'count': len(providers)
            }
        })
    except Exception as e:
        logger.error(f"获取云厂商配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers', methods=['GET'])
@login_required
def get_cloud_providers():
    """获取所有云厂商配置"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, provider, config, region, enabled, created_at, updated_at
                FROM cloud_providers
                ORDER BY created_at DESC
            """)
            providers = cursor.fetchall()
            
            # 隐藏敏感信息
            for provider in providers:
                config = json.loads(provider['config'])
                # 隐藏密钥信息，只显示前几位
                for key in config:
                    if 'secret' in key.lower() or 'key' in key.lower():
                        if len(config[key]) > 8:
                            config[key] = config[key][:4] + '*' * 8 + config[key][-4:]
                        else:
                            config[key] = '*' * len(config[key])
                provider['config'] = config
            
            return jsonify({
                'success': True,
                'data': providers
            })
    except Exception as e:
        logger.error(f"获取云厂商配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers', methods=['POST'])
@login_required
def create_cloud_provider():
    """创建云厂商配置"""
    db = get_db_connection()
    data = request.get_json()
    
    try:
        # 验证必填字段
        required_fields = ['name', 'provider', 'config']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'})
        
        # 验证云厂商类型
        supported_providers = ['aliyun', 'aws', 'tencent', 'huawei', 'google', 'azure']
        if data['provider'] not in supported_providers:
            return jsonify({'success': False, 'message': f'不支持的云厂商类型: {data["provider"]}'})
        
        # 验证配置格式
        if not isinstance(data['config'], dict):
            return jsonify({'success': False, 'message': '配置信息必须是对象格式'})
        
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cloud_providers (name, provider, config, region, enabled)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                data['name'],
                data['provider'],
                json.dumps(data['config']),
                data.get('region', ''),
                data.get('enabled', True)
            ))
            
            provider_id = cursor.lastrowid
            
        db.commit()
        return jsonify({
            'success': True,
            'message': '云厂商配置创建成功',
            'data': {'id': provider_id}
        })
    except Exception as e:
        db.rollback()
        logger.error(f"创建云厂商配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers/<int:provider_id>', methods=['GET'])
@login_required
def get_cloud_provider(provider_id):
    """获取单个云厂商配置"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, provider, config, region, enabled, created_at, updated_at
                FROM cloud_providers
                WHERE id = %s
            """, (provider_id,))
            provider = cursor.fetchone()
            
            if not provider:
                return jsonify({'success': False, 'message': '云厂商配置不存在'})
            
            # 解析配置信息
            provider['config'] = json.loads(provider['config'])
            
            return jsonify({
                'success': True,
                'data': provider
            })
    except Exception as e:
        logger.error(f"获取云厂商配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers/<int:provider_id>', methods=['PUT'])
@login_required
def update_cloud_provider(provider_id):
    """更新云厂商配置"""
    db = get_db_connection()
    data = request.get_json()
    
    try:
        # 检查配置是否存在
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM cloud_providers WHERE id = %s", (provider_id,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': '云厂商配置不存在'})
            
            # 更新配置
            update_fields = []
            update_values = []
            
            if 'name' in data:
                update_fields.append('name = %s')
                update_values.append(data['name'])
            
            if 'provider' in data:
                supported_providers = ['aliyun', 'aws', 'tencent', 'huawei', 'google', 'azure']
                if data['provider'] not in supported_providers:
                    return jsonify({'success': False, 'message': f'不支持的云厂商类型: {data["provider"]}'})
                update_fields.append('provider = %s')
                update_values.append(data['provider'])
            
            if 'config' in data:
                if not isinstance(data['config'], dict):
                    return jsonify({'success': False, 'message': '配置信息必须是对象格式'})
                update_fields.append('config = %s')
                update_values.append(json.dumps(data['config']))
            
            if 'region' in data:
                update_fields.append('region = %s')
                update_values.append(data['region'])
            
            if 'enabled' in data:
                update_fields.append('enabled = %s')
                update_values.append(data['enabled'])
            
            if not update_fields:
                return jsonify({'success': False, 'message': '没有需要更新的字段'})
            
            update_values.append(provider_id)
            
            cursor.execute(f"""
                UPDATE cloud_providers 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, update_values)
            
        db.commit()
        return jsonify({'success': True, 'message': '云厂商配置更新成功'})
    except Exception as e:
        db.rollback()
        logger.error(f"更新云厂商配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers/<int:provider_id>', methods=['DELETE'])
@login_required
def delete_cloud_provider(provider_id):
    """删除云厂商配置"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # 检查是否有关联的实例配置
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM cloud_instance_config 
                WHERE provider_id = %s
            """, (provider_id,))
            
            instance_count = cursor.fetchone()['count']
            if instance_count > 0:
                return jsonify({
                    'success': False, 
                    'message': f'无法删除，该配置下还有 {instance_count} 个实例配置'
                })
            
            # 删除配置
            cursor.execute("DELETE FROM cloud_providers WHERE id = %s", (provider_id,))
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': '云厂商配置不存在'})
            
        db.commit()
        return jsonify({'success': True, 'message': '云厂商配置删除成功'})
    except Exception as e:
        db.rollback()
        logger.error(f"删除云厂商配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers/<int:provider_id>/test', methods=['POST'])
@login_required
def test_cloud_provider(provider_id):
    """测试云厂商配置连接"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT provider, config, region
                FROM cloud_providers
                WHERE id = %s
            """, (provider_id,))
            provider = cursor.fetchone()
            
            if not provider:
                return jsonify({'success': False, 'message': '云厂商配置不存在'})
            
            config = json.loads(provider['config'])
            
            # 根据不同云厂商进行连接测试
            if provider['provider'] == 'aliyun':
                from app.utils.aliyun import AliyunService
                service = AliyunService(
                    access_key_id=config.get('access_key_id'),
                    access_key_secret=config.get('access_key_secret'),
                    region=provider['region'] or 'cn-hangzhou'
                )
                # 尝试获取实例列表来测试连接
                instances = service.get_ecs_instances()
                return jsonify({
                    'success': True,
                    'message': f'连接测试成功，发现 {len(instances)} 个ECS实例'
                })
            else:
                # 其他云厂商的测试逻辑待实现
                return jsonify({
                    'success': True,
                    'message': f'{provider["provider"]} 连接测试功能待实现'
                })
                
    except Exception as e:
        logger.error(f"测试云厂商配置失败: {e}")
        return jsonify({'success': False, 'message': f'连接测试失败: {str(e)}'})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers/schemas-test', methods=['GET', 'OPTIONS'])
def get_cloud_provider_schemas_test():
    """获取云厂商配置字段定义 - 测试接口，不需要认证"""
    if request.method == 'OPTIONS':
        return '', 200
        
    db = get_db_connection()
    try:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT provider, field_name, field_type, field_label, is_required, 
                   default_value, options, placeholder, help_text, sort_order
            FROM cloud_provider_schemas
            ORDER BY provider, sort_order
        """)
        schemas = cursor.fetchall()
        
        # 按云厂商分组
        result = {}
        for schema in schemas:
            provider = schema['provider']
            if provider not in result:
                result[provider] = []
            
            # 解析JSON字段
            options = None
            if schema['options']:
                try:
                    options = json.loads(schema['options'])
                except:
                    pass
            
            result[provider].append({
                'field_name': schema['field_name'],
                'field_type': schema['field_type'],
                'field_label': schema['field_label'],
                'is_required': bool(schema['is_required']),
                'default_value': schema['default_value'],
                'options': options,
                'placeholder': schema['placeholder'],
                'help_text': schema['help_text'],
                'sort_order': schema['sort_order']
            })
        
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'data': result,
            'debug': {
                'message': '测试接口，无需认证',
                'providers': list(result.keys()),
                'field_count': len(schemas)
            }
        })
    except Exception as e:
        logger.error(f"获取云厂商配置字段定义失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers/schemas', methods=['GET'])
@login_required
def get_cloud_provider_schemas():
    """获取云厂商配置字段定义"""
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT provider, field_name, field_type, field_label, is_required, 
                       default_value, options, placeholder, help_text, sort_order
                FROM cloud_provider_schemas
                ORDER BY provider, sort_order
            """)
            schemas = cursor.fetchall()
            
            # 按云厂商分组
            result = {}
            for schema in schemas:
                provider = schema['provider']
                if provider not in result:
                    result[provider] = []
                
                # 解析JSON字段
                options = None
                if schema['options']:
                    try:
                        options = json.loads(schema['options'])
                    except:
                        pass
                
                result[provider].append({
                    'field_name': schema['field_name'],
                    'field_type': schema['field_type'],
                    'field_label': schema['field_label'],
                    'is_required': bool(schema['is_required']),
                    'default_value': schema['default_value'],
                    'options': options,
                    'placeholder': schema['placeholder'],
                    'help_text': schema['help_text'],
                    'sort_order': schema['sort_order']
                })
            
            return jsonify({
                'success': True,
                'data': result
            })
    except Exception as e:
        logger.error(f"获取云厂商配置字段定义失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@cloud_providers.route('/api/cloud-providers/supported-test', methods=['GET', 'OPTIONS'])
def get_supported_providers_test():
    """获取支持的云厂商列表 - 测试接口，不需要认证"""
    if request.method == 'OPTIONS':
        return '', 200
        
    providers = [
        {'value': 'aliyun', 'label': '阿里云', 'icon': '🌐'},
        {'value': 'aws', 'label': 'Amazon Web Services', 'icon': '☁️'},
        {'value': 'tencent', 'label': '腾讯云', 'icon': '🐧'},
        {'value': 'huawei', 'label': '华为云', 'icon': '🌸'},
        {'value': 'google', 'label': 'Google Cloud', 'icon': '🔍'},
        {'value': 'azure', 'label': 'Microsoft Azure', 'icon': '🪟'}
    ]
    
    return jsonify({
        'success': True,
        'data': providers,
        'debug': {
            'message': '测试接口，无需认证',
            'count': len(providers)
        }
    })

@cloud_providers.route('/api/cloud-providers/supported', methods=['GET'])
@login_required
def get_supported_providers():
    """获取支持的云厂商列表"""
    providers = [
        {'value': 'aliyun', 'label': '阿里云', 'icon': '🌐'},
        {'value': 'aws', 'label': 'Amazon Web Services', 'icon': '☁️'},
        {'value': 'tencent', 'label': '腾讯云', 'icon': '🐧'},
        {'value': 'huawei', 'label': '华为云', 'icon': '🌸'},
        {'value': 'google', 'label': 'Google Cloud', 'icon': '🔍'},
        {'value': 'azure', 'label': 'Microsoft Azure', 'icon': '🪟'}
    ]
    
    return jsonify({
        'success': True,
        'data': providers
    })

# 兼容性路由 - 保持向后兼容
@cloud_providers.route('/api/settings/aliyun', methods=['GET', 'POST'])
@login_required
def aliyun_settings_compatibility():
    """阿里云设置兼容性接口"""
    db = get_db_connection()
    
    if request.method == 'GET':
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    SELECT config, region FROM cloud_providers 
                    WHERE provider = 'aliyun' 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """)
                provider = cursor.fetchone()
                
                if not provider:
                    return jsonify({
                        'success': True,
                        'data': {
                            'accessKeyId': '',
                            'accessKeySecret': ''
                        }
                    })
                
                config = json.loads(provider['config'])
                return jsonify({
                    'success': True,
                    'data': {
                        'accessKeyId': config.get('access_key_id', ''),
                        'accessKeySecret': ''  # 不返回密钥
                    }
                })
        except Exception as e:
            logger.error(f"获取阿里云设置失败: {e}")
            return jsonify({'success': False, 'message': str(e)})
        finally:
            db.close()
    
    else:  # POST
        data = request.get_json()
        try:
            with db.cursor() as cursor:
                # 更新现有的阿里云配置或创建新的
                cursor.execute("""
                    SELECT id FROM cloud_providers 
                    WHERE provider = 'aliyun' 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """)
                provider = cursor.fetchone()
                
                config_data = {
                    'access_key_id': data.get('accessKeyId', ''),
                    'access_key_secret': data.get('accessKeySecret', '')
                }
                
                if provider:
                    # 更新现有配置
                    cursor.execute("""
                        UPDATE cloud_providers 
                        SET config = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (json.dumps(config_data), provider['id']))
                else:
                    # 创建新配置
                    cursor.execute("""
                        INSERT INTO cloud_providers (name, provider, config, region, enabled)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        '默认阿里云配置',
                        'aliyun',
                        json.dumps(config_data),
                        'cn-hangzhou',
                        True
                    ))
                
            db.commit()
            return jsonify({'success': True, 'message': '保存成功'})
        except Exception as e:
            db.rollback()
            logger.error(f"保存阿里云设置失败: {e}")
            return jsonify({'success': False, 'message': str(e)})
        finally:
            db.close()