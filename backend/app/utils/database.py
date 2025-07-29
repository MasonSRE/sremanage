from sqlalchemy import text
from app.extensions import db
from app.utils.logger import get_logger
import time
import pymysql
from os import getenv
from dotenv import load_dotenv
from app.models.user import User
import os
from flask import g
from flask import current_app

logger = get_logger(__name__)

load_dotenv()

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=os.getenv('DB_HOST'),  # 使用环境变量而不是 current_app.config
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """初始化数据库"""
    # 注册数据库连接关闭的回调函数
    app.teardown_appcontext(close_db)
    
    # 在应用上下文中初始化默认应用
    with app.app_context():
        _init_default_apps()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise

def get_db_connection_sqlalchemy():
    """获取数据库连接，如果连接断开则重试"""
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            db.session.execute(text('SELECT 1'))
            return db.session
        except Exception as e:
            logger.warning(f'Database connection attempt {attempt + 1} failed: {str(e)}')
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                db.session.rollback()
                db.session.remove()
            else:
                logger.error('All database connection attempts failed')
                raise

def init_db():
    """初始化数据库"""
    db.create_all()
    
    # 创建管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password='9itNKA6nVs0ZkGw321Tu',  # 使用新密码
            email='admin@example.com'
        )
        admin.role = 'admin'
        db.session.add(admin)
        db.session.commit()

def _init_default_apps():
    """初始化默认应用模板"""
    try:
        # 导入初始化脚本
        import subprocess
        import sys
        
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'init_default_apps.py')
        if os.path.exists(script_path):
            logger.info("正在初始化默认应用模板...")
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("默认应用模板初始化成功")
            else:
                logger.error(f"默认应用模板初始化失败: {result.stderr}")
        else:
            logger.warning(f"默认应用初始化脚本不存在: {script_path}")
    except Exception as e:
        logger.error(f"初始化默认应用时发生错误: {str(e)}")