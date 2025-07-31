"""
数据库连接上下文管理器
确保数据库连接在使用后正确关闭，防止资源泄露
"""
import logging
from contextlib import contextmanager
from app.utils.database import get_db_connection

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