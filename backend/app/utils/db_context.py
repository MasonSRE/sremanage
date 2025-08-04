"""
数据库连接上下文管理器
确保数据库连接在使用后正确关闭，防止资源泄露
集成性能监控和查询优化功能
"""
import logging
import time
from contextlib import contextmanager
from app.utils.database import get_db_connection
from app.utils.database_optimization import (
    db_optimizer, 
    monitor_query,
    OptimizedConnectionPool,
    QueryBuilder,
    OptimizedQueries
)

logger = logging.getLogger(__name__)

@contextmanager
def database_connection():
    """
    数据库连接上下文管理器
    
    使用方式:
    with database_connection() as db:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            result = cursor.fetchall()
    """
    db = None
    try:
        db = get_db_connection()
        logger.debug("数据库连接已建立")
        yield db
    except Exception as e:
        logger.error(f"数据库操作失败: {e}")
        if db:
            try:
                db.rollback()
                logger.debug("数据库事务已回滚")
            except Exception as rollback_error:
                logger.error(f"数据库回滚失败: {rollback_error}")
        raise
    finally:
        if db:
            try:
                db.close()
                logger.debug("数据库连接已关闭")
            except Exception as close_error:
                logger.error(f"关闭数据库连接失败: {close_error}")

@contextmanager
def database_transaction():
    """
    数据库事务上下文管理器
    自动提交成功的事务，出错时自动回滚
    
    使用方式:
    with database_transaction() as db:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO table VALUES (...)")
            # 成功时自动提交，失败时自动回滚
    """
    db = None
    try:
        db = get_db_connection()
        logger.debug("数据库事务已开始")
        yield db
        db.commit()
        logger.debug("数据库事务已提交")
    except Exception as e:
        logger.error(f"数据库事务失败: {e}")
        if db:
            try:
                db.rollback()
                logger.debug("数据库事务已回滚")
            except Exception as rollback_error:
                logger.error(f"数据库回滚失败: {rollback_error}")
        raise
    finally:
        if db:
            try:
                db.close()
                logger.debug("数据库连接已关闭")
            except Exception as close_error:
                logger.error(f"关闭数据库连接失败: {close_error}")

class DatabaseConnectionPool:
    """
    数据库连接池管理器（为未来扩展准备）
    """
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self._connections = []
        self._used_connections = set()
    
    def get_connection(self):
        """获取数据库连接"""
        # 这里可以实现连接池逻辑
        # 目前简单返回新连接
        return get_db_connection()
    
    def return_connection(self, connection):
        """归还数据库连接"""
        try:
            if connection:
                connection.close()
        except Exception as e:
            logger.error(f"归还数据库连接失败: {e}")

# 全局连接池实例（为未来使用）
connection_pool = DatabaseConnectionPool()

@contextmanager 
def optimized_database_connection():
    """
    优化的数据库连接上下文管理器
    集成性能监控和查询优化功能
    
    使用方式:
    with optimized_database_connection() as db:
        result = db.execute_query("SELECT * FROM table WHERE id = %s", (1,))
    """
    db = None
    start_time = time.time()
    
    try:
        # 这里可以配置连接池参数，实际使用时从配置文件读取
        from app.utils.database import get_database_config
        
        try:
            config = get_database_config()
            db = OptimizedConnectionPool(**config)
            logger.debug("优化数据库连接池已建立")
        except Exception as config_error:
            logger.warning(f"创建连接池失败，使用传统连接: {config_error}")
            # 降级到传统连接方式
            db = get_db_connection()
        
        yield db
        
    except Exception as e:
        connection_time = time.time() - start_time
        db_optimizer.record_query("DATABASE_CONNECTION", connection_time, error=str(e))
        logger.error(f"优化数据库操作失败: {e}")
        raise
    finally:
        connection_time = time.time() - start_time
        db_optimizer.record_query("DATABASE_CONNECTION", connection_time)
        
        if db:
            try:
                if hasattr(db, 'close'):
                    db.close()
                logger.debug("优化数据库连接已关闭")
            except Exception as close_error:
                logger.error(f"关闭优化数据库连接失败: {close_error}")

class OptimizedQueryExecutor:
    """优化的查询执行器"""
    
    @staticmethod
    @monitor_query("jenkins_instances_query")
    def get_jenkins_instances():
        """获取Jenkins实例列表（优化版本）"""
        query, params = OptimizedQueries.get_jenkins_instances_optimized()
        
        with database_connection() as db:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    
    @staticmethod
    @monitor_query("jenkins_instance_by_id_query")
    def get_jenkins_instance_by_id(instance_id: int):
        """根据ID获取Jenkins实例（优化版本）"""
        query, params = OptimizedQueries.get_jenkins_instance_by_id_optimized(instance_id)
        
        with database_connection() as db:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
    
    @staticmethod
    @monitor_query("batch_insert_query") 
    def batch_insert(table: str, data_list: list, batch_size: int = 100):
        """批量插入数据（优化版本）"""
        if not data_list:
            return 0
        
        # 获取字段名
        fields = list(data_list[0].keys())
        field_names = ', '.join(fields)
        placeholders = ', '.join(['%s'] * len(fields))
        
        query = f"INSERT INTO {table} ({field_names}) VALUES ({placeholders})"
        
        total_inserted = 0
        with database_transaction() as db:
            with db.cursor() as cursor:
                # 分批插入
                for i in range(0, len(data_list), batch_size):
                    batch = data_list[i:i + batch_size]
                    batch_values = [tuple(item[field] for field in fields) for item in batch]
                    
                    cursor.executemany(query, batch_values)
                    total_inserted += cursor.rowcount
                    
                    logger.debug(f"批量插入 {len(batch)} 条记录到 {table}")
        
        return total_inserted
    
    @staticmethod
    @monitor_query("optimized_search_query")
    def search_with_pagination(table: str, search_term: str = None, 
                              page: int = 1, page_size: int = 20,
                              order_by: str = 'id', order_direction: str = 'DESC'):
        """带分页的搜索查询（优化版本）"""
        builder = QueryBuilder(table)
        
        # 添加搜索条件
        if search_term:
            # 这里简化处理，实际应用中需要根据具体字段调整
            builder.where("name LIKE %s OR description LIKE %s", 
                         f"%{search_term}%", f"%{search_term}%")
        
        # 添加排序和分页
        offset = (page - 1) * page_size
        builder.order_by(order_by, order_direction).limit(page_size, offset)
        
        query, params = builder.build()
        
        with database_connection() as db:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

# 全局优化查询执行器实例
optimized_executor = OptimizedQueryExecutor()

def get_database_performance_report():
    """获取数据库性能报告"""
    return {
        'query_stats': db_optimizer.get_query_stats(),
        'slow_queries': db_optimizer.get_slow_queries(),
        'optimization_suggestions': db_optimizer.get_optimization_suggestions(),
        'timestamp': time.time()
    }