from .auth import auth_bp
from .hosts import hosts_bp  
from .settings import settings
from .aliyun import aliyun
from .terminal import terminal_bp
from .ops import bp as ops_bp
from .software import bp as software_bp
from .stats import stats_bp

def register_routes(app):
    """注册所有路由"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(hosts_bp)
    app.register_blueprint(settings)
    app.register_blueprint(aliyun)
    app.register_blueprint(terminal_bp)
    app.register_blueprint(ops_bp)
    app.register_blueprint(software_bp)
    app.register_blueprint(stats_bp) 