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

    # Phase 5 生产优化配置
    PERFORMANCE_MONITOR_ENABLED = os.getenv('PERFORMANCE_MONITOR_ENABLED', 'true').lower() == 'true'
    DATABASE_POOL_SIZE = int(os.getenv('DATABASE_POOL_SIZE', '20'))
    DATABASE_POOL_TIMEOUT = int(os.getenv('DATABASE_POOL_TIMEOUT', '30'))
    CACHE_DEFAULT_TTL = int(os.getenv('CACHE_DEFAULT_TTL', '300'))
    
    # 安全配置
    ENCRYPTION_MASTER_KEY = os.getenv('ENCRYPTION_MASTER_KEY')
    SECURITY_AUDIT_ENABLED = os.getenv('SECURITY_AUDIT_ENABLED', 'true').lower() == 'true'
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    IP_BLOCK_DURATION = int(os.getenv('IP_BLOCK_DURATION', '3600'))
    
    # 限流配置
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    
    # 容错配置
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv('CIRCUIT_BREAKER_THRESHOLD', '5'))
    CIRCUIT_BREAKER_TIMEOUT = int(os.getenv('CIRCUIT_BREAKER_TIMEOUT', '60'))
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    
    # Redis配置（可选）
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_CACHE_ENABLED = os.getenv('REDIS_CACHE_ENABLED', 'false').lower() == 'true'

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保日志目录存在
        os.makedirs('logs', exist_ok=True)
        os.makedirs('logs/phase5', exist_ok=True)
        os.makedirs('cache/performance', exist_ok=True)
        os.makedirs('cache/security', exist_ok=True)
        
        # 生成加密密钥（如果不存在）
        if not app.config.get('ENCRYPTION_MASTER_KEY'):
            from cryptography.fernet import Fernet
            key = Fernet.generate_key().decode()
            app.config['ENCRYPTION_MASTER_KEY'] = key
            # 写入到.env文件
            try:
                with open('.env', 'a') as f:
                    f.write(f'\nENCRYPTION_MASTER_KEY={key}\n')
            except:
                pass
        
        # 初始化Phase 5组件
        try:
            Config.init_phase5_components(app)
        except Exception as e:
            print(f"⚠️ Phase 5组件初始化警告: {e}")
    
    @staticmethod
    def init_phase5_components(app):
        """初始化Phase 5组件"""
        # 初始化性能监控
        if app.config.get('PERFORMANCE_MONITOR_ENABLED', True):
            from app.utils.performance import performance_monitor
            app.performance_monitor = performance_monitor
            
        # 初始化安全审计
        if app.config.get('SECURITY_AUDIT_ENABLED', True):
            from app.utils.security_enhancement import security_auditor
            app.security_auditor = security_auditor
            
        # 初始化权限管理
        from app.utils.permission_control import permission_manager
        app.permission_manager = permission_manager
        
        # 初始化错误处理
        from app.utils.error_handling import error_handler
        app.error_handler = error_handler
        
        # 初始化弹性组件
        from app.utils.retry_fallback import retry_manager, fallback_manager
        app.retry_manager = retry_manager
        app.fallback_manager = fallback_manager
        
        print("✅ Phase 5 组件初始化完成") 