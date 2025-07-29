import jwt
from datetime import datetime, timedelta
from os import getenv
from flask import session
from app.utils.logger import get_logger
from app.models.user import User
from config import Config

logger = get_logger(__name__)

class AuthService:
    @staticmethod
    def login(data):
        try:
            username = data.get('username')
            password = data.get('password')
            
            logger.info(f"尝试登录用户: {username}")
            
            # 查找用户
            user = User.query.filter_by(username=username).first()
            
            if not user:
                logger.info(f"用户不存在: {username}")
                return {
                    'success': False,
                    'message': '用户名或密码错误'
                }
            
            # 验证密码 - 直接比较
            if user.password != password:
                logger.info(f"密码错误，用户: {username}")
                return {
                    'success': False,
                    'message': '用户名或密码错误'
                }
            
            # 生成token - 使用Config中的JWT_SECRET_KEY
            token = jwt.encode(
                {
                    'user_id': user.id,
                    'username': user.username,
                    'exp': datetime.utcnow() + timedelta(hours=24)
                },
                Config.JWT_SECRET_KEY,
                algorithm='HS256'
            )
            
            logger.info(f"登录成功，用户: {username}")
            logger.debug(f"使用的JWT_SECRET_KEY: {Config.JWT_SECRET_KEY[:5]}***")
            
            return {
                'success': True,
                'data': {
                    'token': token,
                    'username': user.username,
                    'expires': int((datetime.utcnow() + timedelta(hours=24)).timestamp())
                }
            }
            
        except Exception as e:
            logger.error(f"登录服务错误: {str(e)}")
            raise Exception('登录失败，请稍后重试')

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            logger.debug(f"Token验证成功: {payload.get('username')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            raise Exception('Token has expired')
        except jwt.InvalidTokenError:
            logger.warning("无效的Token")
            raise Exception('Invalid token') 