"""
数据加密强化模块
提供敏感数据加密、解密、密钥管理等功能
"""

import os
import hashlib
import hmac
import base64
import secrets
import json
import functools
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or self._generate_master_key()
        self.fernet = Fernet(self.master_key.encode() if isinstance(self.master_key, str) else self.master_key)
        self.key_cache = {}
        self.salt_cache = {}
        
    def _generate_master_key(self) -> bytes:
        """生成主密钥"""
        return Fernet.generate_key()
    
    def _derive_key(self, password: str, salt: bytes = None) -> bytes:
        """从密码派生密钥"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt_sensitive_data(self, data: Union[str, Dict[str, Any]], 
                             key_id: str = None) -> Dict[str, Any]:
        """
        加密敏感数据
        
        Args:
            data: 要加密的数据
            key_id: 密钥标识
            
        Returns:
            包含加密数据和元信息的字典
        """
        try:
            # 序列化数据
            if isinstance(data, dict):
                data_str = json.dumps(data, separators=(',', ':'))
            else:
                data_str = str(data)
            
            # 生成随机盐值
            salt = os.urandom(16)
            
            # 使用主密钥加密
            encrypted_data = self.fernet.encrypt(data_str.encode())
            
            # 计算数据哈希用于完整性验证
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()
            
            # 生成加密元信息
            encryption_info = {
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'salt': base64.b64encode(salt).decode(),
                'hash': data_hash,
                'key_id': key_id or 'default',
                'algorithm': 'Fernet',
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            logger.info(f"数据加密成功，密钥ID: {key_id or 'default'}")
            return encryption_info
            
        except Exception as e:
            logger.error(f"数据加密失败: {str(e)}")
            raise
    
    def decrypt_sensitive_data(self, encryption_info: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        解密敏感数据
        
        Args:
            encryption_info: 加密信息字典
            
        Returns:
            解密后的原始数据
        """
        try:
            # 解码加密数据
            encrypted_data = base64.b64decode(encryption_info['encrypted_data'])
            
            # 解密数据
            decrypted_bytes = self.fernet.decrypt(encrypted_data)
            decrypted_str = decrypted_bytes.decode()
            
            # 验证数据完整性
            calculated_hash = hashlib.sha256(decrypted_bytes).hexdigest()
            if calculated_hash != encryption_info.get('hash'):
                raise ValueError("数据完整性验证失败")
            
            # 尝试解析JSON
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
                
        except Exception as e:
            logger.error(f"数据解密失败: {str(e)}")
            raise
    
    def encrypt_password(self, password: str) -> Dict[str, str]:
        """
        加密密码
        
        Args:
            password: 明文密码
            
        Returns:
            包含加密密码和盐值的字典
        """
        salt = os.urandom(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        return {
            'password_hash': base64.b64encode(pwdhash).decode(),
            'salt': base64.b64encode(salt).decode(),
            'algorithm': 'PBKDF2-SHA256',
            'iterations': 100000
        }
    
    def verify_password(self, password: str, password_info: Dict[str, str]) -> bool:
        """
        验证密码
        
        Args:
            password: 要验证的密码
            password_info: 存储的密码信息
            
        Returns:
            密码是否正确
        """
        try:
            stored_hash = base64.b64decode(password_info['password_hash'])
            salt = base64.b64decode(password_info['salt'])
            iterations = password_info.get('iterations', 100000)
            
            pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
            return hmac.compare_digest(stored_hash, pwdhash)
            
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False


class TokenManager:
    """安全令牌管理器"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.active_tokens = {}
        self.revoked_tokens = set()
        
    def generate_secure_token(self, user_id: str, expires_in: int = 3600, 
                            permissions: List[str] = None) -> Dict[str, Any]:
        """
        生成安全令牌
        
        Args:
            user_id: 用户ID
            expires_in: 过期时间（秒）
            permissions: 权限列表
            
        Returns:
            令牌信息
        """
        token_id = secrets.token_urlsafe(32)
        issued_at = datetime.now()
        expires_at = issued_at + timedelta(seconds=expires_in)
        
        # 令牌负载
        payload = {
            'token_id': token_id,
            'user_id': user_id,
            'issued_at': issued_at.isoformat(),
            'expires_at': expires_at.isoformat(),
            'permissions': permissions or [],
            'nonce': secrets.token_urlsafe(16)
        }
        
        # 生成签名
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # 完整令牌
        token_data = {
            'payload': base64.b64encode(payload_str.encode()).decode(),
            'signature': signature
        }
        
        # 缓存令牌
        self.active_tokens[token_id] = {
            'user_id': user_id,
            'expires_at': expires_at,
            'permissions': permissions or []
        }
        
        token = base64.b64encode(json.dumps(token_data).encode()).decode()
        
        logger.info(f"为用户 {user_id} 生成安全令牌")
        return {
            'token': token,
            'token_id': token_id,
            'expires_at': expires_at.isoformat(),
            'permissions': permissions or []
        }
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证令牌
        
        Args:
            token: 令牌字符串
            
        Returns:
            令牌信息或None
        """
        try:
            # 解码令牌
            token_data = json.loads(base64.b64decode(token))
            payload_str = base64.b64decode(token_data['payload']).decode()
            payload = json.loads(payload_str)
            
            # 检查令牌是否被撤销
            if payload['token_id'] in self.revoked_tokens:
                logger.warning(f"令牌已被撤销: {payload['token_id']}")
                return None
            
            # 验证签名
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(token_data['signature'], expected_signature):
                logger.warning("令牌签名验证失败")
                return None
            
            # 检查过期时间
            expires_at = datetime.fromisoformat(payload['expires_at'])
            if datetime.now() > expires_at:
                logger.warning(f"令牌已过期: {payload['token_id']}")
                return None
            
            logger.debug(f"令牌验证成功: {payload['token_id']}")
            return payload
            
        except Exception as e:
            logger.error(f"令牌验证失败: {str(e)}")
            return None
    
    def revoke_token(self, token_id: str):
        """撤销令牌"""
        self.revoked_tokens.add(token_id)
        if token_id in self.active_tokens:
            del self.active_tokens[token_id]
        logger.info(f"令牌已撤销: {token_id}")
    
    def cleanup_expired_tokens(self):
        """清理过期令牌"""
        now = datetime.now()
        expired_tokens = []
        
        for token_id, token_info in self.active_tokens.items():
            if now > token_info['expires_at']:
                expired_tokens.append(token_id)
        
        for token_id in expired_tokens:
            del self.active_tokens[token_id]
        
        logger.info(f"清理了 {len(expired_tokens)} 个過期令牌")


class DataMasking:
    """数据脱敏处理"""
    
    @staticmethod
    def mask_email(email: str) -> str:
        """邮箱脱敏"""
        if '@' not in email:
            return email
        
        username, domain = email.split('@', 1)
        if len(username) <= 2:
            masked_username = '*' * len(username)
        else:
            masked_username = username[:2] + '*' * (len(username) - 2)
        
        return f"{masked_username}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """手机号脱敏"""
        if len(phone) <= 7:
            return '*' * len(phone)
        
        return phone[:3] + '*' * (len(phone) - 7) + phone[-4:]
    
    @staticmethod
    def mask_ip_address(ip: str) -> str:
        """IP地址脱敏"""
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.***"
        return ip
    
    @staticmethod
    def mask_password(password: str) -> str:
        """密码脱敏"""
        return '*' * min(len(password), 8)
    
    @staticmethod
    def mask_token(token: str) -> str:
        """令牌脱敏"""
        if len(token) <= 8:
            return '*' * len(token)
        
        return token[:4] + '*' * (len(token) - 8) + token[-4:]
    
    @classmethod
    def mask_sensitive_data(cls, data: Dict[str, Any], 
                          sensitive_fields: List[str] = None) -> Dict[str, Any]:
        """
        批量脱敏敏感数据
        
        Args:
            data: 原始数据
            sensitive_fields: 敏感字段列表
            
        Returns:
            脱敏后的数据
        """
        if sensitive_fields is None:
            sensitive_fields = [
                'password', 'token', 'email', 'phone', 'mobile',
                'ip_address', 'api_key', 'secret', 'private_key'
            ]
        
        masked_data = data.copy()
        
        for field in sensitive_fields:
            if field in masked_data:
                value = str(masked_data[field])
                
                if 'email' in field.lower():
                    masked_data[field] = cls.mask_email(value)
                elif 'phone' in field.lower() or 'mobile' in field.lower():
                    masked_data[field] = cls.mask_phone(value)
                elif 'ip' in field.lower():
                    masked_data[field] = cls.mask_ip_address(value)
                elif 'password' in field.lower():
                    masked_data[field] = cls.mask_password(value)
                elif 'token' in field.lower() or 'key' in field.lower():
                    masked_data[field] = cls.mask_token(value)
                else:
                    # 通用脱敏
                    if len(value) <= 4:
                        masked_data[field] = '*' * len(value)
                    else:
                        masked_data[field] = value[:2] + '*' * (len(value) - 4) + value[-2:]
        
        return masked_data


class SSLManager:
    """SSL/TLS管理器"""
    
    @staticmethod
    def generate_rsa_keypair(key_size: int = 2048) -> Dict[str, bytes]:
        """生成RSA密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'private_key': private_pem,
            'public_key': public_pem
        }
    
    @staticmethod
    def encrypt_with_public_key(data: str, public_key_pem: bytes) -> str:
        """使用公钥加密数据"""
        public_key = serialization.load_pem_public_key(public_key_pem)
        
        encrypted = public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_with_private_key(encrypted_data: str, private_key_pem: bytes) -> str:
        """使用私钥解密数据"""
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted.decode()


# 全局实例
encryption_manager = EncryptionManager()
token_manager = TokenManager()
data_masking = DataMasking()
ssl_manager = SSLManager()

# 加密装饰器
def encrypt_sensitive_response(sensitive_fields: List[str] = None):
    """响应数据加密装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if isinstance(result, dict) and 'data' in result:
                # 对敏感字段进行加密
                if sensitive_fields:
                    for field in sensitive_fields:
                        if field in result['data']:
                            encrypted_info = encryption_manager.encrypt_sensitive_data(
                                result['data'][field]
                            )
                            result['data'][f'{field}_encrypted'] = encrypted_info
                            # 可选择是否删除原始字段
                            # del result['data'][field]
            
            return result
        return wrapper
    return decorator

def mask_sensitive_logs():
    """日志脱敏装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # 脱敏异常信息中的敏感数据
                error_str = str(e)
                
                # 脱敏常见的敏感信息
                import re
                
                # 脱敏密码
                error_str = re.sub(r'password[\'\":\s]*[\'\"]\S+[\'\"]\s*', 'password: "***"', error_str, flags=re.IGNORECASE)
                
                # 脱敏令牌
                error_str = re.sub(r'token[\'\":\s]*[\'\"]\S+[\'\"]\s*', 'token: "***"', error_str, flags=re.IGNORECASE)
                
                logger.error(f"处理请求时发生错误: {error_str}")
                raise
        return wrapper
    return decorator