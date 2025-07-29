from app.routes.settings import settings
from app.routes.aliyun import aliyun
from app.routes.hosts import hosts_bp
from app.routes.terminal import terminal_bp, sock
from app.routes import software, ops
from app.routes.simple_deploy import simple_deploy_bp
from app.routes.stats import stats_bp
from app.api.auth import auth_bp

def register_routes(app):
    """注册所有路由"""
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(hosts_bp, url_prefix='/api')
    app.register_blueprint(settings)
    app.register_blueprint(aliyun)
    app.register_blueprint(software.bp)
    app.register_blueprint(ops.bp)
    app.register_blueprint(terminal_bp)
    app.register_blueprint(simple_deploy_bp)
    app.register_blueprint(stats_bp)
    
    # 初始化WebSocket
    sock.init_app(app)