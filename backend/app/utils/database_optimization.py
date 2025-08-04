"""
数据库查询优化工具模块
提供连接池管理、查询优化、慢查询监控等功能
"""

import logging
import time
import threading
import functools
from typing import Dict, Any, Optional, List, Tuple
from contextlib import contextmanager
from collections import defaultdict, deque
try:
    import mysql.connector
    from mysql.connector import pooling
    HAS_MYSQL_CONNECTOR = True
except ImportError:
    # 如果没有mysql-connector-python，使用PyMySQL
    import pymysql
    import threading
    HAS_MYSQL_CONNECTOR = False
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DatabaseQueryOptimizer:
    """数据库查询优化器"""
    
    def __init__(self):
        self._slow_queries = deque(maxlen=100)  # 保存最近100个慢查询
        self._query_stats = defaultdict(list)  # 查询统计
        self._lock = threading.Lock()
        
    def record_query(self, query: str, duration: float, params: tuple = None, error: str = None):
        """
        记录查询性能
        
        Args:
            query: SQL查询语句
            duration: 执行时间(秒)
            params: 查询参数
            error: 错误信息
        """
        with self._lock:
            timestamp = datetime.now()
            
            # 简化查询语句用于统计(移除参数值)
            simplified_query = self._simplify_query(query)
            
            query_record = {
                'query': simplified_query,
                'original_query': query,
                'duration': duration,
                'timestamp': timestamp,
                'params': str(params) if params else None,
                'error': error,
                'status': 'error' if error else 'success'
            }
            
            # 记录查询统计
            self._query_stats[simplified_query].append(query_record)
            
            # 只保留最近1小时的数据
            cutoff_time = timestamp - timedelta(hours=1)
            self._query_stats[simplified_query] = [
                record for record in self._query_stats[simplified_query]
                if record['timestamp'] > cutoff_time
            ]
            
            # 记录慢查询 (>1秒)
            if duration > 1.0:
                self._slow_queries.append(query_record)
                logger.warning(f"慢查询检测: {simplified_query} 耗时 {duration:.3f}秒")
    
    def _simplify_query(self, query: str) -> str:
        """简化查询语句，用于统计分析"""
        import re
        
        # 移除多余空格和换行
        simplified = re.sub(r'\s+', ' ', query.strip())
        
        # 将参数占位符标准化
        simplified = re.sub(r'%s|%\(\w+\)s|\?', '?', simplified)
        
        # 将数字字面量替换为占位符
        simplified = re.sub(r'\b\d+\b', '?', simplified)
        
        # 将字符串字面量替换为占位符
        simplified = re.sub(r"'[^']*'", "'?'", simplified)
        simplified = re.sub(r'"[^"]*"', '"?"', simplified)
        
        return simplified.lower()
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取慢查询列表"""
        with self._lock:
            return list(self._slow_queries)[-limit:]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """获取查询统计信息"""
        with self._lock:
            stats = {}
            total_queries = 0
            total_duration = 0
            error_count = 0
            
            for query, records in self._query_stats.items():
                if not records:
                    continue
                
                query_count = len(records)
                durations = [r['duration'] for r in records]
                errors = [r for r in records if r['status'] == 'error']
                
                total_queries += query_count
                total_duration += sum(durations)
                error_count += len(errors)
                
                stats[query] = {
                    'count': query_count,
                    'avg_duration': round(sum(durations) / query_count, 3),
                    'max_duration': round(max(durations), 3),
                    'min_duration': round(min(durations), 3),
                    'error_count': len(errors),
                    'success_rate': round((query_count - len(errors)) / query_count * 100, 2)
                }
            
            return {
                'query_details': stats,
                'overall': {
                    'total_queries': total_queries,
                    'total_duration': round(total_duration, 3),
                    'avg_duration': round(total_duration / total_queries, 3) if total_queries > 0 else 0,
                    'error_count': error_count,
                    'error_rate': round(error_count / total_queries * 100, 2) if total_queries > 0 else 0,
                    'slow_queries_count': len(self._slow_queries)
                }
            }
    
    def get_optimization_suggestions(self) -> List[str]:
        """获取查询优化建议"""
        suggestions = []
        stats = self.get_query_stats()
        
        # 检查慢查询
        slow_count = stats['overall']['slow_queries_count']
        if slow_count > 10:
            suggestions.append(f'检测到{slow_count}个慢查询，建议优化查询语句或添加索引')
        
        # 检查错误率
        error_rate = stats['overall']['error_rate']
        if error_rate > 5:
            suggestions.append(f'数据库错误率较高({error_rate}%)，建议检查查询语句和数据库连接')
        
        # 检查高频查询
        for query, details in stats['query_details'].items():
            if details['count'] > 50 and details['avg_duration'] > 0.5:
                suggestions.append(f'高频慢查询检测: {query[:50]}... 建议添加缓存或优化查询')
        
        if not suggestions:
            suggestions.append('数据库查询性能良好')
        
        return suggestions

# 全局查询优化器实例
db_optimizer = DatabaseQueryOptimizer()

def monitor_query(query_name: str = None):
    """
    查询监控装饰器
    
    Args:
        query_name: 查询名称，用于标识
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            name = query_name or func.__name__
            error_msg = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = str(e)
                logger.error(f"数据库查询失败 {name}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                
                # 尝试从参数中提取查询语句
                query_sql = None
                if args:
                    for arg in args:
                        if isinstance(arg, str) and ('SELECT' in arg.upper() or 'INSERT' in arg.upper() or 'UPDATE' in arg.upper()):
                            query_sql = arg
                            break
                
                if query_sql:
                    db_optimizer.record_query(query_sql, duration, error=error_msg)
                else:
                    # 如果没有找到SQL语句，使用函数名记录
                    db_optimizer.record_query(f"FUNCTION:{name}", duration, error=error_msg)
        
        return wrapper
    return decorator

class OptimizedConnectionPool:
    """优化的数据库连接池"""
    
    def __init__(self, **config):
        """
        初始化连接池
        
        Args:
            **config: 数据库连接配置
        """
        self.config = config
        self._pool = None
        
        if HAS_MYSQL_CONNECTOR:
            # 使用mysql-connector-python的连接池
            pool_config = {
                'pool_name': 'sremanage_pool',
                'pool_size': 10,  # 连接池大小
                'pool_reset_session': True,
                'autocommit': True,
                **config
            }
            
            try:
                self._pool = pooling.MySQLConnectionPool(**pool_config)
                logger.info(f"mysql-connector连接池创建成功: {pool_config['pool_name']}")
            except Exception as e:
                logger.error(f"创建mysql-connector连接池失败: {e}")
                raise
        else:
            # 使用PyMySQL时，我们创建一个简单的连接池
            logger.info("使用PyMySQL创建简单连接池")
            self._connections = []
            self._used_connections = set()
            self._lock = threading.Lock()
            self.pool_size = config.get('pool_size', 10)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            if HAS_MYSQL_CONNECTOR and self._pool:
                connection = self._pool.get_connection()
            else:
                # 使用PyMySQL创建连接
                connection = pymysql.connect(**self.config)
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = True) -> Any:
        """
        执行数据库查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_one: 是否只获取一行结果
            fetch_all: 是否获取所有结果
            
        Returns:
            查询结果
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params)
                
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
                
                # 记录查询性能
                duration = time.time() - start_time
                db_optimizer.record_query(query, duration, params)
                
                return result
                
        except Exception as e:
            duration = time.time() - start_time
            db_optimizer.record_query(query, duration, params, str(e))
            raise
    
    def execute_transaction(self, queries: List[Tuple[str, tuple]]) -> bool:
        """
        执行事务
        
        Args:
            queries: 查询列表，每个元素为(query, params)元组
            
        Returns:
            是否执行成功
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as connection:
                connection.autocommit = False
                cursor = connection.cursor()
                
                try:
                    for query, params in queries:
                        cursor.execute(query, params)
                    
                    connection.commit()
                    
                    # 记录事务性能
                    duration = time.time() - start_time
                    transaction_query = f"TRANSACTION({len(queries)} queries)"
                    db_optimizer.record_query(transaction_query, duration)
                    
                    return True
                    
                except Exception as e:
                    connection.rollback()
                    raise
                finally:
                    connection.autocommit = True
                    
        except Exception as e:
            duration = time.time() - start_time
            transaction_query = f"TRANSACTION({len(queries)} queries)"
            db_optimizer.record_query(transaction_query, duration, error=str(e))
            logger.error(f"事务执行失败: {e}")
            return False
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        return {
            'pool_name': self._pool.pool_name,
            'pool_size': self._pool.pool_size,
            # 注意：mysql-connector-python的连接池不直接提供活跃连接数信息
            # 这里提供基本信息，实际使用时可能需要自己维护统计
        }

# 创建通用查询构建器
class QueryBuilder:
    """SQL查询构建器，帮助构建优化的查询"""
    
    def __init__(self, table: str):
        self.table = table
        self._select_fields = ['*']
        self._where_conditions = []
        self._join_clauses = []
        self._order_by = []
        self._limit_clause = None
        self._group_by = []
        self._having_conditions = []
    
    def select(self, *fields: str) -> 'QueryBuilder':
        """选择字段"""
        self._select_fields = list(fields) if fields else ['*']
        return self
    
    def where(self, condition: str, *params) -> 'QueryBuilder':
        """添加WHERE条件"""
        self._where_conditions.append((condition, params))
        return self
    
    def join(self, table: str, condition: str, join_type: str = 'INNER') -> 'QueryBuilder':
        """添加JOIN"""
        self._join_clauses.append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def order_by(self, field: str, direction: str = 'ASC') -> 'QueryBuilder':
        """添加排序"""
        self._order_by.append(f"{field} {direction}")
        return self
    
    def limit(self, count: int, offset: int = 0) -> 'QueryBuilder':
        """添加限制"""
        if offset > 0:
            self._limit_clause = f"LIMIT {offset}, {count}"
        else:
            self._limit_clause = f"LIMIT {count}"
        return self
    
    def group_by(self, *fields: str) -> 'QueryBuilder':
        """添加分组"""
        self._group_by.extend(fields)
        return self
    
    def having(self, condition: str) -> 'QueryBuilder':
        """添加HAVING条件"""
        self._having_conditions.append(condition)
        return self
    
    def build(self) -> Tuple[str, tuple]:
        """构建查询语句"""
        # 构建SELECT部分
        query_parts = [f"SELECT {', '.join(self._select_fields)}"]
        query_parts.append(f"FROM {self.table}")
        
        # 构建JOIN部分
        if self._join_clauses:
            query_parts.extend(self._join_clauses)
        
        # 构建WHERE部分
        params = []
        if self._where_conditions:
            where_parts = []
            for condition, condition_params in self._where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query_parts.append(f"WHERE {' AND '.join(where_parts)}")
        
        # 构建GROUP BY部分
        if self._group_by:
            query_parts.append(f"GROUP BY {', '.join(self._group_by)}")
        
        # 构建HAVING部分
        if self._having_conditions:
            query_parts.append(f"HAVING {' AND '.join(self._having_conditions)}")
        
        # 构建ORDER BY部分
        if self._order_by:
            query_parts.append(f"ORDER BY {', '.join(self._order_by)}")
        
        # 构建LIMIT部分
        if self._limit_clause:
            query_parts.append(self._limit_clause)
        
        return ' '.join(query_parts), tuple(params)

# 常用的优化查询模板
class OptimizedQueries:
    """优化的查询模板"""
    
    @staticmethod
    def get_jenkins_instances_optimized() -> Tuple[str, tuple]:
        """获取Jenkins实例列表的优化查询"""
        query = """
        SELECT id, name, url, username, description, environment, created_at, updated_at
        FROM jenkins_settings 
        WHERE deleted_at IS NULL 
        ORDER BY environment ASC, name ASC
        """
        return query, ()
    
    @staticmethod
    def get_jenkins_instance_by_id_optimized(instance_id: int) -> Tuple[str, tuple]:
        """根据ID获取Jenkins实例的优化查询"""
        query = """
        SELECT * FROM jenkins_settings 
        WHERE id = %s AND deleted_at IS NULL
        """
        return query, (instance_id,)
    
    @staticmethod
    def get_recent_builds_optimized(instance_id: int, limit: int = 50) -> Tuple[str, tuple]:
        """获取最近构建记录的优化查询（如果有构建历史表的话）"""
        # 这里假设有一个构建历史表，实际情况需要根据表结构调整
        query = """
        SELECT job_name, build_number, status, duration, started_at, finished_at
        FROM jenkins_builds 
        WHERE jenkins_instance_id = %s 
        ORDER BY started_at DESC 
        LIMIT %s
        """
        return query, (instance_id, limit)
    
    @staticmethod
    def get_performance_metrics_optimized(hours: int = 24) -> Tuple[str, tuple]:
        """获取性能指标的优化查询（如果有性能日志表的话）"""
        query = """
        SELECT 
            endpoint,
            COUNT(*) as request_count,
            AVG(duration) as avg_duration,
            MAX(duration) as max_duration,
            MIN(duration) as min_duration,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
        FROM performance_logs 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        GROUP BY endpoint
        ORDER BY request_count DESC
        """
        return query, (hours,)