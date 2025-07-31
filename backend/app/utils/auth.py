from functools import wraps
from flask import request, jsonify
import jwt
from os import getenv
from app.utils.logger import get_logger
from datetime import datetime, timedelta
from config import Config

logger = get_logger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 对于 OPTIONS 请求，直接放行
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'success': False, 'message': 'Token is missing'}), 401
                
            token = auth_header.split(' ')[1]
            jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

    return decorated 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 临时跳过认证用于测试
        return f(*args, **kwargs)
        
        token = None
        
        # 从请求头中获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': '无效的认证头部'}), 401
                
        if not token:
            return jsonify({'message': '缺少认证token'}), 401
            
        try:
            # 验证token
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            
            # 检查token是否过期
            exp = datetime.fromtimestamp(data['exp'])
            if datetime.utcnow() > exp:
                return jsonify({'message': 'token已过期'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的token'}), 401
            
        return f(*args, **kwargs)
        
    return decorated_function

def generate_token(user_id, username):
    """生成JWT token"""
    exp = datetime.utcnow() + timedelta(hours=24)  # token有效期24小时
    
    token = jwt.encode(
        {
            'user_id': user_id,
            'username': username,
            'exp': exp
        },
        Config.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    
    return token, exp 