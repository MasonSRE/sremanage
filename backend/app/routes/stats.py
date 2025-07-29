from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required
import pymysql
from app.utils.logger import logger
from flask_cors import cross_origin
from datetime import datetime, timedelta
import json
import os
import re
from collections import defaultdict

stats_bp = Blueprint('stats', __name__, url_prefix='/api')

def extract_login_stats_from_logs(days):
    """从应用日志中提取登录统计数据"""
    login_stats = defaultdict(int)
    
    try:
        # 查找日志文件
        log_files = []
        possible_log_paths = [
            'logs/app.log',
            'app.log', 
            '../logs/app.log',
            'backend.log',
            '../backend.log'
        ]
        
        # 找到存在的日志文件
        for log_path in possible_log_paths:
            if os.path.exists(log_path):
                log_files.append(log_path)
        
        if not log_files:
            logger.warning("未找到日志文件")
            return login_stats
        
        # 编译正则表达式匹配登录成功的日志
        # 匹配格式: 2025-07-03 15:50:40,460 - app.services.auth - INFO - [auth.py:49] - 登录成功，用户: admin
        login_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})\s+[\d:,]+.*登录成功.*用户:\s*(\w+)')
        
        # 计算日期范围
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 读取日志文件
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        match = login_pattern.search(line)
                        if match:
                            date_str = match.group(1)
                            username = match.group(2)
                            
                            # 解析日期
                            try:
                                log_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                                
                                # 检查是否在统计范围内
                                if start_date <= log_date <= end_date:
                                    login_stats[date_str] += 1
                                    
                            except ValueError:
                                continue
                                
            except Exception as e:
                logger.error(f"读取日志文件失败 {log_file}: {str(e)}")
                continue
        
        logger.info(f"从日志中提取到登录统计: {dict(login_stats)}")
        return login_stats
        
    except Exception as e:
        logger.error(f"提取登录统计失败: {str(e)}")
        return login_stats

@stats_bp.route('/dashboard/stats', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_dashboard_stats():
    """获取仪表板统计数据"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 1. 主机数量 (包含手动添加的主机和云主机)
        # 手动添加的主机
        cursor.execute("SELECT COUNT(*) as count FROM hosts")
        manual_hosts_count = cursor.fetchone()['count']
        
        # 阿里云ECS实例
        try:
            cursor.execute("SELECT COUNT(*) as count FROM aliyun_ecs_cache")
            aliyun_ecs_count = cursor.fetchone()['count']
        except:
            aliyun_ecs_count = 0
        
        # 总主机数量
        hosts_count = manual_hosts_count + aliyun_ecs_count
        
        # 2. 用户数量
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = cursor.fetchone()['count']
        
        # 3. 告警数量 (目前没有alerts表，设为0)
        alerts_count = 0
        
        # 4. 资产数量 (使用主机数量作为资产数量)
        assets_count = hosts_count
        
        # 5. 在线会话数量 (目前没有sessions表，设为0) 
        sessions_count = 0
        
        # 6. 失败登录次数 (目前没有login_logs表，设为0)
        failed_logins = 0
        
        # 7. 网站监控数量
        try:
            cursor.execute("SELECT COUNT(*) as count FROM site_monitoring")
            sites_count = cursor.fetchone()['count']
        except:
            sites_count = 0
        
        # 8. 资产数据数量 (同资产数量)
        asset_data_count = assets_count
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'hosts_count': hosts_count,
                'users_count': users_count,
                'alerts_count': alerts_count,
                'assets_count': assets_count,
                'sessions_count': sessions_count,
                'failed_logins': failed_logins,
                'sites_count': sites_count,
                'asset_data_count': asset_data_count
            }
        })
        
    except Exception as e:
        logger.error(f"获取仪表板统计数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500

@stats_bp.route('/dashboard/host-types', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_host_types():
    """获取主机类型分布"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取手动添加的主机类型分布
        cursor.execute("""
            SELECT system_type, COUNT(*) as count 
            FROM hosts 
            GROUP BY system_type
        """)
        manual_host_types = cursor.fetchall()
        
        # 获取阿里云ECS的系统类型分布
        aliyun_host_types = []
        try:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN os_type LIKE '%Windows%' OR os_type LIKE '%windows%' THEN 'Windows'
                        WHEN os_type LIKE '%Linux%' OR os_type LIKE '%linux%' OR os_type LIKE '%CentOS%' OR os_type LIKE '%Ubuntu%' THEN 'Linux'
                        ELSE 'Other'
                    END as system_type,
                    COUNT(*) as count 
                FROM aliyun_ecs_cache 
                WHERE os_type IS NOT NULL AND os_type != ''
                GROUP BY 
                    CASE 
                        WHEN os_type LIKE '%Windows%' OR os_type LIKE '%windows%' THEN 'Windows'
                        WHEN os_type LIKE '%Linux%' OR os_type LIKE '%linux%' OR os_type LIKE '%CentOS%' OR os_type LIKE '%Ubuntu%' THEN 'Linux'
                        ELSE 'Other'
                    END
            """)
            aliyun_host_types = cursor.fetchall()
        except:
            aliyun_host_types = []
        
        # 合并手动主机和云主机的类型统计
        type_counts = {}
        
        # 处理手动添加的主机
        for item in manual_host_types:
            system_type = item['system_type']
            type_counts[system_type] = type_counts.get(system_type, 0) + item['count']
        
        # 处理阿里云ECS主机
        for item in aliyun_host_types:
            system_type = item['system_type']
            type_counts[system_type] = type_counts.get(system_type, 0) + item['count']
        
        # 转换为前端需要的格式
        chart_data = []
        for system_type, count in type_counts.items():
            chart_data.append({
                'name': system_type,
                'value': count
            })
        
        # 如果没有数据，返回默认数据
        if not chart_data:
            chart_data = [
                {'name': 'Linux', 'value': 0},
                {'name': 'Windows', 'value': 0}
            ]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        logger.error(f"获取主机类型分布失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取主机类型分布失败: {str(e)}'
        }), 500

@stats_bp.route('/dashboard/connectivity', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_connectivity_stats():
    """获取网站连通性占比"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 使用站点监控的真实数据
        try:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN status = 'online' THEN '正常'
                        ELSE '异常'
                    END as status_name,
                    COUNT(*) as count 
                FROM site_monitoring 
                WHERE enabled = 1
                GROUP BY 
                    CASE 
                        WHEN status = 'online' THEN '正常'
                        ELSE '异常'
                    END
            """)
            
            connectivity = cursor.fetchall()
            
            # 转换为前端需要的格式
            chart_data = []
            status_counts = {'正常': 0, '异常': 0}
            
            for item in connectivity:
                status_counts[item['status_name']] = item['count']
            
            # 添加所有状态到图表数据中
            for status_name, count in status_counts.items():
                chart_data.append({
                    'name': status_name,
                    'value': count
                })
                
            # 如果没有启用的站点，显示默认数据
            if not chart_data or sum(item['value'] for item in chart_data) == 0:
                chart_data = [
                    {'name': '正常', 'value': 0},
                    {'name': '异常', 'value': 0}
                ]
        except Exception as e:
            logger.error(f"查询站点监控数据失败: {str(e)}")
            # 如果查询失败，返回默认数据
            chart_data = [
                {'name': '正常', 'value': 0},
                {'name': '异常', 'value': 0}
            ]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        logger.error(f"获取网站连通性统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取网站连通性统计失败: {str(e)}'
        }), 500

@stats_bp.route('/dashboard/login-stats', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_login_stats():
    """获取用户登录统计数据"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        time_range = request.args.get('range', '7')  # 默认7天
        days = int(time_range)
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 从应用日志中提取登录统计数据
        labels = []
        data = []
        
        try:
            # 从日志文件中提取登录成功的记录
            login_stats = extract_login_stats_from_logs(days)
            
            for i in range(days):
                date = datetime.now() - timedelta(days=days-1-i)
                date_str = date.strftime('%Y-%m-%d')
                labels.append(date.strftime('%m-%d'))
                
                # 获取当天的登录次数
                login_count = login_stats.get(date_str, 0)
                data.append(login_count)
                
        except Exception as e:
            logger.error(f"从日志提取登录统计失败: {str(e)}")
            # 如果日志提取失败，返回空数据但保持结构
            for i in range(days):
                date = datetime.now() - timedelta(days=days-1-i)
                labels.append(date.strftime('%m-%d'))
                data.append(0)
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': '登录次数',
                'data': data,
                'borderColor': '#3B82F6',
                'tension': 0.4
            }]
        }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        logger.error(f"获取登录统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取登录统计失败: {str(e)}'
        }), 500

@stats_bp.route('/dashboard/failed-logins', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@token_required
def get_failed_logins():
    """获取最近登录失败记录"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 目前没有login_logs表，返回空数据
        failed_logins = []
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': failed_logins
        })
        
    except Exception as e:
        logger.error(f"获取失败登录记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取失败登录记录失败: {str(e)}'
        }), 500

@stats_bp.route('/dashboard/stats-test', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_dashboard_stats_test():
    """获取仪表板统计数据 - 测试接口，不需要认证"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 1. 主机数量 (包含手动添加的主机和云主机)
        # 手动添加的主机
        cursor.execute("SELECT COUNT(*) as count FROM hosts")
        manual_hosts_count = cursor.fetchone()['count']
        
        # 阿里云ECS实例
        try:
            cursor.execute("SELECT COUNT(*) as count FROM aliyun_ecs_cache")
            aliyun_ecs_count = cursor.fetchone()['count']
        except:
            aliyun_ecs_count = 0
        
        # 总主机数量
        hosts_count = manual_hosts_count + aliyun_ecs_count
        
        # 2. 用户数量
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = cursor.fetchone()['count']
        
        # 3. 告警数量 (目前没有alerts表，设为0)
        alerts_count = 0
        
        # 4. 资产数量 (使用主机数量作为资产数量)
        assets_count = hosts_count
        
        # 5. 在线会话数量 (目前没有sessions表，设为0) 
        sessions_count = 0
        
        # 6. 失败登录次数 (目前没有login_logs表，设为0)
        failed_logins = 0
        
        # 7. 网站监控数量
        try:
            cursor.execute("SELECT COUNT(*) as count FROM site_monitoring")
            sites_count = cursor.fetchone()['count']
        except:
            sites_count = 0
        
        # 8. 资产数据数量 (同资产数量)
        asset_data_count = assets_count
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'hosts_count': hosts_count,
                'users_count': users_count,
                'alerts_count': alerts_count,
                'assets_count': assets_count,
                'sessions_count': sessions_count,
                'failed_logins': failed_logins,
                'sites_count': sites_count,
                'asset_data_count': asset_data_count
            },
            'debug': {
                'message': '测试接口，无需认证',
                'timestamp': datetime.now().isoformat(),
                'host_breakdown': {
                    'manual_hosts': manual_hosts_count,
                    'aliyun_ecs': aliyun_ecs_count,
                    'total_hosts': hosts_count
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取仪表板统计数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}',
            'debug': {
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
        }), 500

@stats_bp.route('/dashboard/host-types-test', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_host_types_test():
    """获取主机类型分布 - 测试接口，不需要认证"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取手动添加的主机类型分布
        cursor.execute("""
            SELECT system_type, COUNT(*) as count 
            FROM hosts 
            GROUP BY system_type
        """)
        manual_host_types = cursor.fetchall()
        
        # 获取阿里云ECS的系统类型分布
        aliyun_host_types = []
        try:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN os_type LIKE '%Windows%' OR os_type LIKE '%windows%' THEN 'Windows'
                        WHEN os_type LIKE '%Linux%' OR os_type LIKE '%linux%' OR os_type LIKE '%CentOS%' OR os_type LIKE '%Ubuntu%' THEN 'Linux'
                        ELSE 'Other'
                    END as system_type,
                    COUNT(*) as count 
                FROM aliyun_ecs_cache 
                WHERE os_type IS NOT NULL AND os_type != ''
                GROUP BY 
                    CASE 
                        WHEN os_type LIKE '%Windows%' OR os_type LIKE '%windows%' THEN 'Windows'
                        WHEN os_type LIKE '%Linux%' OR os_type LIKE '%linux%' OR os_type LIKE '%CentOS%' OR os_type LIKE '%Ubuntu%' THEN 'Linux'
                        ELSE 'Other'
                    END
            """)
            aliyun_host_types = cursor.fetchall()
        except:
            aliyun_host_types = []
        
        # 合并手动主机和云主机的类型统计
        type_counts = {}
        
        # 处理手动添加的主机
        for item in manual_host_types:
            system_type = item['system_type']
            type_counts[system_type] = type_counts.get(system_type, 0) + item['count']
        
        # 处理阿里云ECS主机
        for item in aliyun_host_types:
            system_type = item['system_type']
            type_counts[system_type] = type_counts.get(system_type, 0) + item['count']
        
        # 转换为前端需要的格式
        chart_data = []
        for system_type, count in type_counts.items():
            chart_data.append({
                'name': system_type,
                'value': count
            })
        
        # 如果没有数据，返回默认数据
        if not chart_data:
            chart_data = [
                {'name': 'Linux', 'value': 0},
                {'name': 'Windows', 'value': 0}
            ]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': chart_data,
            'debug': {
                'message': '测试接口，无需认证',
                'timestamp': datetime.now().isoformat(),
                'manual_hosts': manual_host_types,
                'aliyun_hosts': aliyun_host_types,
                'merged_counts': type_counts
            }
        })
        
    except Exception as e:
        logger.error(f"获取主机类型分布失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取主机类型分布失败: {str(e)}',
            'debug': {
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
        }), 500