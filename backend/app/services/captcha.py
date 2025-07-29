import time
import random
import string
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 使用内存存储验证码信息
captcha_store = {}

class CaptchaService:
    @staticmethod
    def generate_captcha():
        # 从原来的 generate_captcha 函数移动验证码生成逻辑到这里
        pass 

    @staticmethod
    def save_captcha(code, expires=300):
        """
        保存验证码到存储中
        
        Args:
            code: 验证码字符串
            expires: 过期时间（秒）
            
        Returns:
            captcha_id: 验证码ID
        """
        captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        captcha_info = {
            'code': code,
            'timestamp': time.time(),
            'expires': expires
        }
        
        captcha_store[captcha_id] = captcha_info
        logger.info(f"保存验证码 {code}, ID: {captcha_id}")
        
        # 清理过期验证码
        CaptchaService.cleanup_expired()
        
        return captcha_id
    
    @staticmethod
    def validate_captcha(captcha_id, code):
        """
        验证验证码是否正确
        
        Args:
            captcha_id: 验证码ID
            code: 用户输入的验证码
            
        Returns:
            (success, message): (成功/失败, 消息)
        """
        # 获取验证码信息
        captcha_info = captcha_store.get(captcha_id)
        
        # 记录当前状态
        logger.info(f"验证码ID: {captcha_id}, 用户输入: {code}")
        logger.info(f"存储中的验证码: {captcha_info}")
        
        if not captcha_info:
            return False, '验证码已失效，请重新获取'
        
        # 检查是否过期
        if time.time() - captcha_info['timestamp'] > captcha_info['expires']:
            captcha_store.pop(captcha_id, None)
            return False, '验证码已过期，请重新获取'
        
        # 检查验证码是否匹配
        if code.upper() != captcha_info['code']:
            return False, '验证码错误'
        
        # 验证成功后，删除此验证码
        captcha_store.pop(captcha_id, None)
        return True, '验证码正确'
    
    @staticmethod
    def cleanup_expired():
        """清理过期的验证码"""
        current_time = time.time()
        expired_ids = []
        
        for captcha_id, info in captcha_store.items():
            if current_time - info['timestamp'] > info['expires']:
                expired_ids.append(captcha_id)
        
        for expired_id in expired_ids:
            captcha_store.pop(expired_id, None)
        
        if expired_ids:
            logger.info(f"已清理 {len(expired_ids)} 个过期验证码") 