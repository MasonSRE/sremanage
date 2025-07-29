from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required
from app.utils.logger import logger
from flask_cors import cross_origin
from datetime import datetime, timezone, timedelta
import pymysql
import requests
import time
import threading
from urllib.parse import urlparse

# 中国时区
CHINA_TZ = timezone(timedelta(hours=8))

def get_local_time():
    """获取本地时间（中国时区）"""
    return datetime.now(CHINA_TZ).replace(tzinfo=None)

site_monitoring_bp = Blueprint('site_monitoring', __name__, url_prefix='/api')

@site_monitoring_bp.route('/sites', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_sites():
    """获取所有站点监控配置"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT * FROM site_monitoring 
            ORDER BY created_at DESC
        """)
        sites = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': sites
        })
        
    except Exception as e:
        logger.error(f"获取站点监控列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取站点监控列表失败: {str(e)}'
        }), 500

@site_monitoring_bp.route('/sites-test', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_sites_test():
    """获取所有站点监控配置"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT * FROM site_monitoring 
            ORDER BY created_at DESC
        """)
        sites = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': sites
        })
        
    except Exception as e:
        logger.error(f"获取站点监控列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取站点监控列表失败: {str(e)}'
        }), 500

@site_monitoring_bp.route('/sites', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def add_site():
    """添加站点监控"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('site_name'):
            return jsonify({
                'success': False,
                'message': '站点名称不能为空'
            }), 400
            
        if not data.get('site_url'):
            return jsonify({
                'success': False,
                'message': '站点URL不能为空'
            }), 400
        
        # 验证URL格式
        try:
            parsed_url = urlparse(data['site_url'])
            if not parsed_url.scheme or not parsed_url.netloc:
                return jsonify({
                    'success': False,
                    'message': 'URL格式不正确'
                }), 400
        except Exception:
            return jsonify({
                'success': False,
                'message': 'URL格式不正确'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查URL是否已存在
        cursor.execute("SELECT id FROM site_monitoring WHERE site_url = %s", (data['site_url'],))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': '该URL已存在监控列表中'
            }), 400
        
        # 插入数据
        cursor.execute("""
            INSERT INTO site_monitoring 
            (site_name, site_url, check_interval, timeout, enabled, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['site_name'],
            data['site_url'],
            data.get('check_interval', 300),
            data.get('timeout', 30),
            data.get('enabled', True),
            data.get('description', '')
        ))
        
        site_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '站点监控添加成功',
            'data': {'id': site_id}
        })
        
    except Exception as e:
        logger.error(f"添加站点监控失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'添加站点监控失败: {str(e)}'
        }), 500

@site_monitoring_bp.route('/sites/<int:site_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
@token_required
def update_site(site_id):
    """更新站点监控配置"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查站点是否存在
        cursor.execute("SELECT id FROM site_monitoring WHERE id = %s", (site_id,))
        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'message': '站点不存在'
            }), 404
        
        # 构建更新语句
        update_fields = []
        update_values = []
        
        if 'site_name' in data:
            update_fields.append('site_name = %s')
            update_values.append(data['site_name'])
        
        if 'site_url' in data:
            update_fields.append('site_url = %s')
            update_values.append(data['site_url'])
        
        if 'check_interval' in data:
            update_fields.append('check_interval = %s')
            update_values.append(data['check_interval'])
        
        if 'timeout' in data:
            update_fields.append('timeout = %s')
            update_values.append(data['timeout'])
        
        if 'enabled' in data:
            update_fields.append('enabled = %s')
            update_values.append(data['enabled'])
        
        if 'description' in data:
            update_fields.append('description = %s')
            update_values.append(data['description'])
        
        if update_fields:
            update_values.append(site_id)
            cursor.execute(f"""
                UPDATE site_monitoring 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """, update_values)
            
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '站点监控更新成功'
        })
        
    except Exception as e:
        logger.error(f"更新站点监控失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新站点监控失败: {str(e)}'
        }), 500

@site_monitoring_bp.route('/sites/<int:site_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@token_required
def delete_site(site_id):
    """删除站点监控"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查站点是否存在
        cursor.execute("SELECT id FROM site_monitoring WHERE id = %s", (site_id,))
        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'message': '站点不存在'
            }), 404
        
        # 删除站点（历史记录会因为外键级联删除）
        cursor.execute("DELETE FROM site_monitoring WHERE id = %s", (site_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '站点监控删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除站点监控失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除站点监控失败: {str(e)}'
        }), 500

@site_monitoring_bp.route('/sites/<int:site_id>/test', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def test_site(site_id):
    """单点拨测站点"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取站点信息
        cursor.execute("SELECT * FROM site_monitoring WHERE id = %s", (site_id,))
        site = cursor.fetchone()
        
        if not site:
            return jsonify({
                'success': False,
                'message': '站点不存在'
            }), 404
        
        # 执行拨测
        test_result = perform_site_check(site)
        
        # 记录拨测历史
        cursor.execute("""
            INSERT INTO site_monitoring_history 
            (site_id, check_time, status, response_time, http_code, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            site_id,
            get_local_time(),
            test_result['status'],
            test_result['response_time'],
            test_result['http_code'],
            test_result['error_message']
        ))
        
        # 更新站点状态和响应时间
        cursor.execute("""
            UPDATE site_monitoring 
            SET status = %s, last_check_time = %s, last_response_time = %s
            WHERE id = %s
        """, (
            test_result['status'],
            get_local_time(),
            test_result['response_time'],
            site_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # 获取更新后的站点信息
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM site_monitoring WHERE id = %s", (site_id,))
        updated_site = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '拨测完成',
            'data': {
                'test_result': test_result,
                'updated_site': updated_site
            }
        })
        
    except Exception as e:
        logger.error(f"站点拨测失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'站点拨测失败: {str(e)}'
        }), 500

@site_monitoring_bp.route('/sites/<int:site_id>/history', methods=['GET'])
@cross_origin(supports_credentials=True)
@token_required
def get_site_history(site_id):
    """获取站点监控历史记录"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取历史记录
        cursor.execute("""
            SELECT * FROM site_monitoring_history 
            WHERE site_id = %s 
            ORDER BY check_time DESC 
            LIMIT %s OFFSET %s
        """, (site_id, per_page, offset))
        
        history = cursor.fetchall()
        
        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM site_monitoring_history WHERE site_id = %s", (site_id,))
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'total': total,
                'page': page,
                'per_page': per_page
            }
        })
        
    except Exception as e:
        logger.error(f"获取站点历史记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取站点历史记录失败: {str(e)}'
        }), 500

def perform_site_check(site):
    """执行站点检查"""
    try:
        start_time = time.time()
        
        # 发送HTTP请求
        response = requests.get(
            site['site_url'],
            timeout=site['timeout'],
            headers={
                'User-Agent': 'Site-Monitor/1.0'
            }
        )
        
        end_time = time.time()
        response_time = int((end_time - start_time) * 1000)  # 转换为毫秒
        
        # 判断状态
        if response.status_code == 200:
            status = 'online'
        else:
            status = 'offline'
        
        return {
            'status': status,
            'response_time': response_time,
            'http_code': response.status_code,
            'error_message': None
        }
        
    except requests.exceptions.Timeout:
        return {
            'status': 'timeout',
            'response_time': None,
            'http_code': None,
            'error_message': '请求超时'
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'offline',
            'response_time': None,
            'http_code': None,
            'error_message': '连接失败'
        }
    except Exception as e:
        return {
            'status': 'error',
            'response_time': None,
            'http_code': None,
            'error_message': str(e)
        }

@site_monitoring_bp.route('/sites/batch-test', methods=['POST'])
@cross_origin(supports_credentials=True)
@token_required
def batch_test_sites():
    """批量拨测所有启用的站点"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取所有启用的站点
        cursor.execute("SELECT * FROM site_monitoring WHERE enabled = 1")
        sites = cursor.fetchall()
        
        if not sites:
            return jsonify({
                'success': True,
                'message': '没有启用的站点需要拨测',
                'data': []
            })
        
        # 批量拨测
        results = []
        for site in sites:
            test_result = perform_site_check(site)
            test_result['site_id'] = site['id']
            test_result['site_name'] = site['site_name']
            test_result['site_url'] = site['site_url']
            
            # 记录历史
            cursor.execute("""
                INSERT INTO site_monitoring_history 
                (site_id, check_time, status, response_time, http_code, error_message)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                site['id'],
                get_local_time(),
                test_result['status'],
                test_result['response_time'],
                test_result['http_code'],
                test_result['error_message']
            ))
            
            # 更新站点状态
            cursor.execute("""
                UPDATE site_monitoring 
                SET status = %s, last_check_time = %s, last_response_time = %s
                WHERE id = %s
            """, (
                test_result['status'],
                get_local_time(),
                test_result['response_time'],
                site['id']
            ))
            
            results.append(test_result)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'批量拨测完成，共检测 {len(results)} 个站点',
            'data': results
        })
        
    except Exception as e:
        logger.error(f"批量拨测失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量拨测失败: {str(e)}'
        }), 500