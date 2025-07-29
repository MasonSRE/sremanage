from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required
import pymysql
from app.utils.logger import logger
from flask_cors import cross_origin

hosts_unified_bp = Blueprint('hosts_unified', __name__, url_prefix='/api')

@hosts_unified_bp.route('/hosts-all', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_all_hosts():
    """获取所有主机列表（包含手动添加的主机和阿里云ECS）"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        all_hosts = []
        
        # 1. 获取手动添加的主机
        cursor.execute("""
            SELECT id, hostname, ip, system_type, status, protocol, 
                   port, username, description, 
                   DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                   'manual' as source_type
            FROM hosts
            ORDER BY created_at DESC
        """)
        manual_hosts = cursor.fetchall()
        
        for host in manual_hosts:
            all_hosts.append({
                'id': f"manual_{host['id']}",  # 添加前缀区分来源
                'hostname': host['hostname'],
                'ip': host['ip'],
                'system_type': host['system_type'],
                'status': host['status'],
                'protocol': host['protocol'],
                'port': host['port'],
                'username': host['username'],
                'description': host['description'],
                'created_at': host['created_at'],
                'source_type': 'manual',
                'original_id': host['id']  # 保留原始ID用于安装软件时使用
            })
        
        # 2. 获取阿里云ECS实例
        try:
            cursor.execute("""
                SELECT instance_id, instance_name, hostname, status, instance_type, 
                       public_ip, private_ip, region, zone, os_type, cpu, memory,
                       DATE_FORMAT(last_sync_time, '%Y-%m-%d %H:%i:%s') as last_sync_time
                FROM aliyun_ecs_cache 
                ORDER BY last_sync_time DESC
            """)
            aliyun_hosts = cursor.fetchall()
            
            for host in aliyun_hosts:
                # 判断使用哪个IP
                ip = host['public_ip'] if host['public_ip'] else host['private_ip']
                
                # 映射阿里云状态到标准状态
                status = 'running' if host['status'] == 'Running' else 'stopped'
                
                # 映射系统类型
                system_type = 'Linux'
                if host['os_type']:
                    if 'windows' in host['os_type'].lower():
                        system_type = 'Windows'
                    elif any(os in host['os_type'].lower() for os in ['linux', 'centos', 'ubuntu']):
                        system_type = 'Linux'
                    else:
                        system_type = 'Other'
                
                all_hosts.append({
                    'id': f"aliyun_{host['instance_id']}",  # 添加前缀区分来源
                    'hostname': host['instance_name'],
                    'ip': ip,
                    'system_type': system_type,
                    'status': status,
                    'protocol': 'SSH' if system_type == 'Linux' else 'RDP',
                    'port': 22 if system_type == 'Linux' else 3389,
                    'username': 'root' if system_type == 'Linux' else 'administrator',
                    'description': f"阿里云ECS - {host['region']} - {host['instance_type']} - {host['cpu']}核{host['memory']}MB",
                    'created_at': host['last_sync_time'],
                    'source_type': 'aliyun',
                    'original_id': host['instance_id']  # 保留原始ID
                })
        except Exception as e:
            logger.warning(f"获取阿里云ECS失败: {str(e)}")
            # 如果阿里云数据获取失败，继续返回手动主机
        
        cursor.close()
        conn.close()
        
        # 按创建时间倒序排列
        all_hosts.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return jsonify({
            'success': True, 
            'data': all_hosts,
            'total': len(all_hosts),
            'manual_count': len(manual_hosts),
            'aliyun_count': len(all_hosts) - len(manual_hosts)
        })
        
    except Exception as e:
        logger.error(f"获取所有主机列表失败: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'获取主机列表失败: {str(e)}'
        }), 500

@hosts_unified_bp.route('/hosts-all-test', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_all_hosts_test():
    """获取所有主机列表（测试接口，不需要认证）"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        all_hosts = []
        
        # 1. 获取手动添加的主机
        cursor.execute("""
            SELECT id, hostname, ip, system_type, status, protocol, 
                   port, username, description, 
                   DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                   'manual' as source_type
            FROM hosts
            ORDER BY created_at DESC
        """)
        manual_hosts = cursor.fetchall()
        
        for host in manual_hosts:
            all_hosts.append({
                'id': f"manual_{host['id']}",  # 添加前缀区分来源
                'hostname': host['hostname'],
                'ip': host['ip'],
                'system_type': host['system_type'],
                'status': host['status'],
                'protocol': host['protocol'],
                'port': host['port'],
                'username': host['username'],
                'description': host['description'],
                'created_at': host['created_at'],
                'source_type': 'manual',
                'original_id': host['id']  # 保留原始ID用于安装软件时使用
            })
        
        # 2. 获取阿里云ECS实例
        try:
            cursor.execute("""
                SELECT instance_id, instance_name, hostname, status, instance_type, 
                       public_ip, private_ip, region, zone, os_type, cpu, memory,
                       DATE_FORMAT(last_sync_time, '%Y-%m-%d %H:%i:%s') as last_sync_time
                FROM aliyun_ecs_cache 
                ORDER BY last_sync_time DESC
            """)
            aliyun_hosts = cursor.fetchall()
            
            for host in aliyun_hosts:
                # 判断使用哪个IP
                ip = host['public_ip'] if host['public_ip'] else host['private_ip']
                
                # 映射阿里云状态到标准状态
                status = 'running' if host['status'] == 'Running' else 'stopped'
                
                # 映射系统类型
                system_type = 'Linux'
                if host['os_type']:
                    if 'windows' in host['os_type'].lower():
                        system_type = 'Windows'
                    elif any(os in host['os_type'].lower() for os in ['linux', 'centos', 'ubuntu']):
                        system_type = 'Linux'
                    else:
                        system_type = 'Other'
                
                all_hosts.append({
                    'id': f"aliyun_{host['instance_id']}",  # 添加前缀区分来源
                    'hostname': host['instance_name'],
                    'ip': ip,
                    'system_type': system_type,
                    'status': status,
                    'protocol': 'SSH' if system_type == 'Linux' else 'RDP',
                    'port': 22 if system_type == 'Linux' else 3389,
                    'username': 'root' if system_type == 'Linux' else 'administrator',
                    'description': f"阿里云ECS - {host['region']} - {host['instance_type']} - {host['cpu']}核{host['memory']}MB",
                    'created_at': host['last_sync_time'],
                    'source_type': 'aliyun',
                    'original_id': host['instance_id']  # 保留原始ID
                })
        except Exception as e:
            logger.warning(f"获取阿里云ECS失败: {str(e)}")
            # 如果阿里云数据获取失败，继续返回手动主机
        
        cursor.close()
        conn.close()
        
        # 按创建时间倒序排列
        all_hosts.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return jsonify({
            'success': True, 
            'data': all_hosts,
            'total': len(all_hosts),
            'manual_count': len(manual_hosts),
            'aliyun_count': len(all_hosts) - len(manual_hosts),
            'debug': {
                'message': '测试接口，无需认证',
                'manual_hosts_sample': manual_hosts[:2] if manual_hosts else [],
                'aliyun_hosts_sample': aliyun_hosts[:2] if aliyun_hosts else []
            }
        })
        
    except Exception as e:
        logger.error(f"获取所有主机列表失败: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'获取主机列表失败: {str(e)}'
        }), 500