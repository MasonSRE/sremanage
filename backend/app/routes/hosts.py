from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required
import pymysql
from app.utils.logger import logger
from flask_cors import cross_origin

hosts_bp = Blueprint('hosts', __name__, url_prefix='/api')

@hosts_bp.route('/hosts', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_hosts():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 添加日志
        logger.info("开始查询主机列表")
        
        cursor.execute("""
            SELECT id, hostname, ip, system_type, status, protocol, 
                   port, username, description, 
                   DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at
            FROM hosts
            ORDER BY created_at DESC
        """)
        
        hosts = cursor.fetchall()
        logger.info(f"查询到 {len(hosts)} 条主机记录")  # 添加日志
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'data': hosts
        })
    except Exception as e:
        logger.error(f"获取主机列表失败: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'获取主机列表失败: {str(e)}'
        }), 500

@hosts_bp.route('/hosts', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def add_host():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        logger.info(f"接收到的数据: {data}")
        
        required_fields = ['hostname', 'ip', 'system_type', 'protocol', 'port', 'username']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"缺少必填字段: {field}")
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM hosts WHERE hostname = %s", (data['hostname'],))
        if cursor.fetchone():
            logger.warning(f"主机名已存在: {data['hostname']}")
            return jsonify({'success': False, 'message': '主机名已存在'}), 400
            
        sql = """
            INSERT INTO hosts (hostname, ip, system_type, protocol, port, 
                             username, password, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            data['hostname'],
            data['ip'],
            data['system_type'],
            data['protocol'],
            data['port'],
            data['username'],
            data.get('password', ''),
            data.get('description', ''),
            'running'
        ))
        
        conn.commit()
        logger.info(f"成功添加主机: {data['hostname']}")
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': '主机添加成功'})
        
    except pymysql.err.IntegrityError as e:
        logger.error(f"数据库完整性错误: {str(e)}")
        if 'idx_hostname' in str(e):
            return jsonify({'success': False, 'message': '主机名已存在'}), 400
        return jsonify({'success': False, 'message': str(e)}), 400
        
    except Exception as e:
        logger.error(f"添加主机时发生错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@hosts_bp.route('/hosts/<int:host_id>', methods=['PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def update_host(host_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['hostname', 'ip', 'system_type', 'protocol', 'port', 'username']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field}不能为空'}), 400
        
        # 更新数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE hosts 
            SET hostname=%s, ip=%s, system_type=%s, protocol=%s, 
                port=%s, username=%s, password=%s, description=%s,
                updated_at=NOW()
            WHERE id=%s
        """
        cursor.execute(sql, (
            data['hostname'], data['ip'], data['system_type'],
            data['protocol'], data['port'], data['username'],
            data['password'], data.get('description', ''),
            host_id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': '更新成功'})
        
    except Exception as e:
        conn = get_db_connection()
        conn.rollback()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hosts WHERE id = %s', (host_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '主机不存在'}), 404
        cursor.execute("DELETE FROM hosts WHERE id = %s", (host_id,))
        conn.commit()
        cursor.close()
        conn.close()
        logger.error(f"删除主机失败: {str(e)}")
        return jsonify({'success': False, 'message': '删除主机失败'}), 500

@hosts_bp.route('/hosts/<int:host_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def delete_host(host_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hosts WHERE id = %s", (host_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '主机不存在'}), 404
        cursor.execute("DELETE FROM hosts WHERE id = %s", (host_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        conn = get_db_connection()
        conn.rollback()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hosts WHERE id = %s", (host_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '主机不存在'}), 404
        cursor.execute("DELETE FROM hosts WHERE id = %s", (host_id,))
        conn.commit()
        cursor.close()
        conn.close()
        logger.error(f"删除主机失败: {str(e)}")
        return jsonify({'success': False, 'message': '删除主机失败'}), 500

@hosts_bp.route('/hosts-debug', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def debug_hosts():
    """调试主机列表接口，不需要验证Token"""
    if request.method == 'OPTIONS':
        return '', 200
    try:
        # 添加详细的日志输出用于调试
        logger.info("=== 调试接口被访问 ===")
        logger.info(f"请求方法: {request.method}")
        logger.info(f"请求头: {dict(request.headers)}")
        logger.info(f"请求源: {request.origin if hasattr(request, 'origin') else 'Unknown'}")
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 记录环境信息
        auth_header = request.headers.get('Authorization')
        logger.info(f"Authorization头: {auth_header}")
        
        # 添加日志
        logger.info("调试：开始查询主机列表")
        
        try:
            # 获取创建主机表的SQL
            cursor.execute("SHOW CREATE TABLE hosts")
            table_info = cursor.fetchone()
            
            # 查询主机数据
            cursor.execute("""
                SELECT COUNT(*) as total FROM hosts
            """)
            count = cursor.fetchone()
            
            cursor.execute("""
                SELECT id, hostname, ip, system_type, status, protocol, 
                       port, username, description, 
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at
                FROM hosts
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            hosts = cursor.fetchall()
            
            # 查看数据库连接信息
            db_config = {}
            for key in ['host', 'user', 'database', 'port']:
                db_config[key] = conn.get_host_info() if key == 'host' else getattr(conn, key) if hasattr(conn, key) else None
            
            logger.info(f"调试查询到 {len(hosts)} 条主机记录")
            
            # 测试数据库连接是否正常
            cursor.execute("SELECT 1")
            is_connected = cursor.fetchone() is not None
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True, 
                'data': {
                    'is_connected': is_connected,
                    'hosts': hosts,
                    'count': count,
                    'table_info': table_info,
                    'db_config': db_config
                }
            })
        except Exception as db_error:
            logger.error(f"数据库操作失败: {str(db_error)}")
            return jsonify({
                'success': False, 
                'message': f'数据库操作失败: {str(db_error)}',
                'error_type': 'database_error'
            }), 500
            
    except Exception as e:
        logger.error(f"调试获取主机列表失败: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'调试获取主机列表失败: {str(e)}',
            'error_type': 'general_error'
        }), 500

@hosts_bp.route('/test-db', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://127.0.0.1:5173", "http://localhost:5173"], supports_credentials=True)
def test_db():
    """测试数据库连接的简单接口"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("开始测试数据库连接")
        # 获取连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 测试连接
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        # 测试主机表
        try:
            cursor.execute("SELECT COUNT(*) FROM hosts")
            host_count = cursor.fetchone()[0]
            has_hosts_table = True
        except Exception as e:
            logger.error(f"查询主机表失败: {str(e)}")
            has_hosts_table = False
            host_count = 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '数据库连接测试成功',
            'data': {
                'db_connected': result is not None,
                'has_hosts_table': has_hosts_table,
                'host_count': host_count
            }
        })
        
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'数据库连接测试失败: {str(e)}'
        }), 500 