import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
import pymysql
from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

def execute_sql_files():
    """执行 SQL 文件夹下的所有 SQL 文件"""
    app = create_app()
    
    # 获取数据库配置
    db_config = {
        'host': app.config['DB_HOST'],
        'port': int(app.config['DB_PORT']),
        'user': app.config['DB_USER'],
        'password': app.config['DB_PASSWORD'],
        'database': app.config['DB_NAME'],
    }
    
    # SQL文件目录
    sql_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql')
    
    try:
        # 连接数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 创建版本控制表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_version_control (
                file_name VARCHAR(255) PRIMARY KEY,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
        # 获取已执行的文件列表
        cursor.execute("SELECT file_name FROM db_version_control")
        executed_files = {row[0] for row in cursor.fetchall()}
        
        # 获取所有SQL文件并排序
        sql_files = sorted([f for f in os.listdir(sql_dir) if f.endswith('.sql')])
        
        for sql_file in sql_files:
            # 跳过已执行的文件
            if sql_file in executed_files:
                logger.info(f"Skipping already executed file: {sql_file}")
                continue
                
            file_path = os.path.join(sql_dir, sql_file)
            logger.info(f"Executing SQL file: {sql_file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                    # 分割SQL语句（考虑到可能有多条语句）
                    statements = sql_content.split(';')
                    
                    for statement in statements:
                        statement = statement.strip()
                        if statement:  # 忽略空语句
                            try:
                                cursor.execute(statement)
                                conn.commit()
                            except Exception as e:
                                logger.error(f"Error executing statement in {sql_file}: {e}")
                                # 如果是非关键错误（如表已存在），继续执行
                                if not str(e).startswith('(1050'): # MySQL错误码1050：表已存在
                                    raise
                
                # 记录执行成功的文件
                cursor.execute(
                    "INSERT INTO db_version_control (file_name) VALUES (%s)",
                    (sql_file,)
                )
                conn.commit()
                logger.info(f"Successfully executed {sql_file}")
                
            except Exception as e:
                logger.error(f"Error processing {sql_file}: {e}")
                raise
                
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    try:
        execute_sql_files()
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1) 