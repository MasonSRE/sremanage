from flask import Flask, jsonify, session, request
from flask_cors import CORS
from app.extensions import db
from app.config import config
from app.utils.logger import get_logger
from app.routes.hosts import hosts_bp
from datetime import timedelta
from app.routes.terminal import terminal_bp, sock
from flask_sock import Sock
from app.routes.settings import settings
from app.routes import software
from app.utils.database import init_app as init_db
from app.routes import ops
from app.routes.aliyun import aliyun
from app.routes.cloud_providers import cloud_providers
from app.routes.stats import stats_bp
from app.routes.hosts_unified import hosts_unified_bp
from app.routes.docker_apps import docker_apps_bp
from app.routes.app_store import app_store_bp
from app.routes.migration import migration_bp
from app.routes.site_monitoring import site_monitoring_bp
from app.routes.simple_deploy import simple_deploy_bp

logger = get_logger(__name__)

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 设置 session 密钥
    app.secret_key = app.config['SECRET_KEY']
    
    # 设置 session 配置
    app.config.update(
        SESSION_COOKIE_SAMESITE=None,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_PATH='/',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SESSION_REFRESH_EACH_REQUEST=True,
        SESSION_COOKIE_DOMAIN=None
    )
    
    # CORS配置需要支持WebSocket
    CORS(app, 
        origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "Accept"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type"],
        resources={
            r"/api/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]},
            r"/api/terminal": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}
        }
    )
    
    # 初始化扩展
    db.init_app(app)
    
    # 初始化数据库
    init_db(app)
    
    # 注册蓝图
    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(hosts_bp, url_prefix='/api')
    sock.init_app(app)
    app.register_blueprint(terminal_bp)
    app.register_blueprint(settings)
    app.register_blueprint(software.bp)
    app.register_blueprint(ops.bp)
    app.register_blueprint(aliyun)
    app.register_blueprint(cloud_providers)
    app.register_blueprint(stats_bp)
    app.register_blueprint(hosts_unified_bp)
    app.register_blueprint(docker_apps_bp)
    app.register_blueprint(app_store_bp)
    app.register_blueprint(migration_bp)
    app.register_blueprint(site_monitoring_bp)
    app.register_blueprint(simple_deploy_bp)
    
    # 添加错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        logger.error(f"404 Error: {error}")
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Error: {error}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    return app 