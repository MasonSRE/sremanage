from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 直接初始化 SQLAlchemy，不需要复杂的配置
db = SQLAlchemy()
cors = CORS()

def init_extensions(app):
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)
    with app.app_context():
        db.create_all() 