"""
云厂商统一工具模块
提供统一的云厂商配置获取和实例管理功能
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from app.utils.database import get_db_connection

logger = logging.getLogger(__name__)

def get_cloud_provider_credentials(provider_id: int = None, provider_type: str = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    获取云厂商凭证
    
    Args:
        provider_id: 云厂商配置ID
        provider_type: 云厂商类型 (用于获取默认配置)
    
    Returns:
        tuple: (config_dict, provider_type) 或 (None, None)
    """
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            if provider_id:
                # 根据ID获取特定配置
                cursor.execute("""
                    SELECT provider, config, region, enabled 
                    FROM cloud_providers 
                    WHERE id = %s AND enabled = 1
                """, (provider_id,))
            elif provider_type:
                # 获取指定类型的默认配置（第一个启用的）
                cursor.execute("""
                    SELECT provider, config, region, enabled 
                    FROM cloud_providers 
                    WHERE provider = %s AND enabled = 1
                    ORDER BY created_at ASC
                    LIMIT 1
                """, (provider_type,))
            else:
                # 获取默认的阿里云配置（向后兼容）
                cursor.execute("""
                    SELECT provider, config, region, enabled 
                    FROM cloud_providers 
                    WHERE provider = 'aliyun' AND enabled = 1
                    ORDER BY created_at ASC
                    LIMIT 1
                """)
            
            provider = cursor.fetchone()
            
            if not provider:
                return None, None
            
            config = json.loads(provider['config'])
            return config, provider['provider']
            
    except Exception as e:
        logger.error(f"获取云厂商凭证失败: {str(e)}")
        return None, None
    finally:
        db.close()

def get_aliyun_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    获取阿里云凭证（向后兼容函数）
    
    Returns:
        tuple: (access_key_id, access_key_secret) 或 (None, None)
    """
    config, provider_type = get_cloud_provider_credentials(provider_type='aliyun')
    
    if not config or provider_type != 'aliyun':
        return None, None
    
    return config.get('access_key_id'), config.get('access_key_secret')

def get_cloud_service_instance(provider_id: int = None, provider_type: str = 'aliyun'):
    """
    获取云服务实例
    
    Args:
        provider_id: 云厂商配置ID
        provider_type: 云厂商类型
    
    Returns:
        云服务实例对象或None
    """
    config, actual_provider = get_cloud_provider_credentials(provider_id, provider_type)
    
    if not config or not actual_provider:
        raise Exception("未找到有效的云厂商配置")
    
    if actual_provider == 'aliyun':
        from app.utils.aliyun import AliyunService
        return AliyunService(
            access_key_id=config.get('access_key_id'),
            access_key_secret=config.get('access_key_secret'),
            region=config.get('default_region', 'cn-hangzhou')
        )
    elif actual_provider == 'aws':
        # TODO: 实现AWS服务
        raise Exception("AWS服务暂未实现")
    elif actual_provider == 'tencent':
        # TODO: 实现腾讯云服务
        raise Exception("腾讯云服务暂未实现")
    elif actual_provider == 'huawei':
        # TODO: 实现华为云服务
        raise Exception("华为云服务暂未实现")
    else:
        raise Exception(f"不支持的云厂商类型: {actual_provider}")

def get_cloud_providers_list() -> List[Dict]:
    """
    获取所有启用的云厂商配置列表
    
    Returns:
        list: 云厂商配置列表
    """
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, provider, region, enabled, created_at
                FROM cloud_providers
                WHERE enabled = 1
                ORDER BY provider, created_at
            """)
            providers = cursor.fetchall()
            
            return [{
                'id': p['id'],
                'name': p['name'],
                'provider': p['provider'],
                'region': p['region'],
                'enabled': bool(p['enabled']),
                'created_at': p['created_at']
            } for p in providers]
            
    except Exception as e:
        logger.error(f"获取云厂商配置列表失败: {str(e)}")
        return []
    finally:
        db.close()

def get_instance_config(provider_id: int, instance_id: str) -> Optional[Dict]:
    """
    获取实例连接配置
    
    Args:
        provider_id: 云厂商配置ID
        instance_id: 实例ID
    
    Returns:
        dict: 实例配置信息或None
    """
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM cloud_instance_config 
                WHERE provider_id = %s AND instance_id = %s
            """, (provider_id, instance_id))
            
            config = cursor.fetchone()
            return dict(config) if config else None
            
    except Exception as e:
        logger.error(f"获取实例配置失败: {str(e)}")
        return None
    finally:
        db.close()

def save_instance_config(provider_id: int, instance_id: str, config: Dict) -> bool:
    """
    保存实例连接配置
    
    Args:
        provider_id: 云厂商配置ID
        instance_id: 实例ID
        config: 配置信息
    
    Returns:
        bool: 是否保存成功
    """
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cloud_instance_config 
                (provider_id, instance_id, instance_name, ssh_port, username, password, private_key)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    instance_name = VALUES(instance_name),
                    ssh_port = VALUES(ssh_port),
                    username = VALUES(username),
                    password = VALUES(password),
                    private_key = VALUES(private_key),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                provider_id,
                instance_id,
                config.get('instance_name', ''),
                config.get('ssh_port', 22),
                config.get('username', 'root'),
                config.get('password', ''),
                config.get('private_key', '')
            ))
            
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"保存实例配置失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def get_instances_by_provider(provider_id: int) -> List[Dict]:
    """
    根据云厂商配置ID获取实例列表
    
    Args:
        provider_id: 云厂商配置ID
    
    Returns:
        list: 实例列表
    """
    try:
        # 获取云服务实例
        service = get_cloud_service_instance(provider_id=provider_id)
        
        if hasattr(service, 'get_ecs_instances'):
            # 阿里云ECS实例
            instances = service.get_ecs_instances()
        elif hasattr(service, 'get_instances'):
            # 其他云厂商的实例
            instances = service.get_instances()
        else:
            raise Exception("云服务不支持实例获取")
        
        # 为每个实例添加provider_id
        for instance in instances:
            instance['provider_id'] = provider_id
        
        return instances
        
    except Exception as e:
        logger.error(f"获取实例列表失败: {str(e)}")
        raise e

def get_all_instances() -> List[Dict]:
    """
    获取所有云厂商的实例列表
    
    Returns:
        list: 所有实例列表
    """
    all_instances = []
    providers = get_cloud_providers_list()
    
    for provider in providers:
        try:
            instances = get_instances_by_provider(provider['id'])
            
            # 为每个实例添加云厂商信息
            for instance in instances:
                instance['provider_name'] = provider['name']
                instance['provider_type'] = provider['provider']
            
            all_instances.extend(instances)
            
        except Exception as e:
            logger.warning(f"获取云厂商 {provider['name']} 的实例失败: {str(e)}")
            continue
    
    return all_instances

# 向后兼容的函数映射
def get_aliyun_service_instance():
    """向后兼容：获取阿里云服务实例"""
    return get_cloud_service_instance(provider_type='aliyun')