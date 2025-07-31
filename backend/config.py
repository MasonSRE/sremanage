import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'm666123')  # 从环境变量获取JWT密钥
    
    # Session配置
    SESSION_COOKIE_SECURE = False  # 如果不是HTTPS，设置为False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # CORS配置
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ['Set-Cookie']
    
    # 数据库配置 - 使用本地MySQL容器
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Uodeb2Af4AIbjGC4vWoGmJqoF2A')
    DB_NAME = os.getenv('DB_NAME', 'ops_management')
    
    # JWT配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # 跨域配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://127.0.0.1:5173,http://localhost:5173').split(',')
    
    # Cookie配置
    COOKIE_DOMAIN = os.getenv('COOKIE_DOMAIN', '127.0.0.1')

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'logs/app.log'

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保日志目录存在
        os.makedirs('logs', exist_ok=True) 