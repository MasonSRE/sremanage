from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import datetime, timedelta
from functools import wraps
import jwt
import random
import string
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
from dotenv import load_dotenv
import logging
import configparser
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time
from config import Config
from app.routes import register_routes
from app.utils.logger import setup_logger

# 修改日志配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 加载配置文件
config = configparser.ConfigParser()
config.read('config/mysql.cnf')

# 全局变量
db = None

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 设置 session 密钥
    app.secret_key = app.config['SECRET_KEY']
    
    # 设置 session 配置
    app.config.update(
        SESSION_TYPE='filesystem',  # 使用文件系统存储session
        SESSION_FILE_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session'),
        SESSION_COOKIE_SAMESITE=None,  # 允许跨站点发送Cookie
        SESSION_COOKIE_SECURE=False,     # 在开发环境中设为False，因为可能不使用HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_PATH='/',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SESSION_REFRESH_EACH_REQUEST=True,
        SESSION_COOKIE_DOMAIN=None,
        SESSION_USE_SIGNER=True,  # 使用签名保护Cookie
        SESSION_FILE_THRESHOLD=100  # 文件数量达到100时清理旧会话
    )
    
    # 确保session目录存在
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])
    
    # CORS配置需要支持WebSocket
    CORS(app, 
        origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "Accept"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type", "Set-Cookie"],
        resources={
            r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}
        }
    )
    
    # 初始化 Session
    Session(app)
    
    # 调试路由 - 检查 cookie 状态
    @app.route('/api/debug/session', methods=['GET'])
    def debug_session():
        # 记录所有请求信息
        logger.info(f"Request cookies: {request.cookies}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Session data: {dict(session)}")
        
        # 设置一个测试值
        if 'test' not in session:
            session['test'] = f"test-{time.time()}"
            session.modified = True
        
        return jsonify({
            'cookies': {k: v for k, v in request.cookies.items()},
            'session': {k: v for k, v in session.items()},
            'headers': {k: v for k, v in request.headers.items()}
        })
    
    # 从配置文件读取数据库配置
    db_config = config['client']
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'connect_args': {
            'connect_timeout': 10
        }
    }
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-jwt-key-for-development')
    
    # 初始化 SQLAlchemy
    global db
    db = SQLAlchemy(app)
    
    # 初始化日志
    setup_logger(app)
    
    # 注册路由
    register_routes(app)
    
    # 添加错误处理
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal Server Error: {str(error)}')
        return jsonify({'error': '服务器内部错误'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f'Unhandled Exception: {str(e)}')
        return jsonify({'error': '服务器错误'}), 500
    
    # 验证token装饰器
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            logger.debug(f'Received Authorization header: {auth_header[:20] if auth_header else None}...')
            
            if not auth_header:
                logger.warning('No token provided')
                return jsonify({'error': '未提供token'}), 401
            
            try:
                if ' ' not in auth_header:
                    logger.warning('Invalid token format')
                    return jsonify({'error': '无效的token格式'}), 401
                    
                token = auth_header.split(' ')[1]
                logger.debug(f'Attempting to decode token: {token[:20]}...')
                
                data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                logger.debug(f'Token decoded successfully, payload: {data}')
                
                # 使用新的数据库连接
                session = get_db_connection()
                current_user = session.query(User).get(data['user_id'])
                
                if not current_user:
                    logger.warning(f'User not found for id: {data.get("user_id")}')
                    return jsonify({'error': '用户不存在'}), 401
                
                logger.debug(f'User found: {current_user.username}')
                return f(current_user, *args, **kwargs)
                    
            except jwt.ExpiredSignatureError as e:
                logger.warning(f'Token expired: {str(e)}')
                return jsonify({'error': '登录已过期，请重新登录'}), 401
            except jwt.InvalidTokenError as e:
                logger.warning(f'Invalid token: {str(e)}')
                return jsonify({'error': '无效的token'}), 401
            except Exception as e:
                logger.exception('Unexpected error in token validation:')
                return jsonify({'error': '服务器错误'}), 500
        
        return decorated
    
    # 路由函数
    @app.route('/api/verify-token', methods=['GET'])
    @token_required
    def verify_token(current_user):
        try:
            logger.debug(f'Verifying token for user: {current_user.username}')
            return jsonify({
                'valid': True,
                'username': current_user.username
            })
        except Exception as e:
            logger.exception('Error in verify_token:')  # 这会记录完整的堆栈跟踪
            return jsonify({'error': '服务器错误'}), 500

    @app.route('/api/logout', methods=['POST'])
    @token_required
    def logout(current_user):
        current_user.token = None
        current_user.token_expires = None
        db.session.commit()
        return jsonify({'message': '退出成功'})
    
    return app

# 用户模型 - 在应用初始化后再定义
class User(db.Model):
    __tablename__ = 'user'  # 明确指定表名
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    last_login = db.Column(db.DateTime)
    token = db.Column(db.String(500))
    token_expires = db.Column(db.DateTime)

    def __init__(self, username, password):
        self.username = username
        self.password = password

def generate_captcha():
    try:
        # 生成随机验证码
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        logger.debug(f'Generated captcha code: {code}')
        
        # 创建更大的图片
        width = 280
        height = 120
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # 添加背景干扰点
        for i in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill='lightgrey')
        
        # 添加柔和的干扰线
        for i in range(2):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill='lightgray', width=1)
        
        # 尝试加载多个字体，确保至少一个可用
        font = None
        font_size = 95
        try:
            font_names = ['arial.ttf', 'Arial.ttf', 'DejaVuSans-Bold.ttf', 'FreeSans.ttf']
            for font_name in font_names:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except:
                    continue
        except:
            pass
        
        if font is None:
            default_font = ImageFont.load_default()
            font_size = 95
            logger.warning("Using default font with size scaling")
        
        # 绘制验证码字符
        colors = ['black', 'darkblue', 'darkred', 'darkgreen']
        char_spacing = width // 5
        
        for i, char in enumerate(code):
            x = char_spacing * i + 30
            y = random.randint(10, 35)
            color = random.choice(colors)
            angle = random.randint(-5, 5)
            char_img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            
            if font:
                char_draw.text((20, 10), char, font=font, fill=color)
            else:
                char_draw.text((20, 10), char, fill=color)
                char_img = char_img.resize((100, 100), Image.LANCZOS)
            
            char_img = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            img.paste(char_img, (x, y), char_img)
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        logger.debug('Captcha image generated successfully')
        
        return code, img_str
    except Exception as e:
        logger.exception('Error generating captcha:')
        raise

def get_db_connection():
    """获取数据库连接，如果连接断开则重试"""
    max_retries = 3
    retry_delay = 1  # 秒

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
    try:
        db.create_all()
        # 检查是否存在默认用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User('admin', 'admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("Default admin user created")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

if __name__ == '__main__':
    app = create_app()  # 创建应用
    with app.app_context():
        init_db()       # 初始化数据库
    app.run(host='0.0.0.0', port=5000, debug=True)
