"""
安全工具类 - 提供密码加密/解密功能
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class PasswordManager:
    """密码管理器 - 提供安全的密码加密和解密功能"""
    
    def __init__(self, master_key=None):
        """
        初始化密码管理器
        
        Args:
            master_key: 主密钥，如果不提供则从环境变量或配置文件读取
        """
        self.master_key = master_key or self._get_master_key()
        self.cipher_suite = self._create_cipher_suite()
    
    def _get_master_key(self):
        """获取主密钥"""
        # 优先从环境变量获取
        master_key = os.environ.get('SREMANAGE_MASTER_KEY')
        if master_key:
            return master_key.encode()
        
        # 从配置文件获取或生成新的密钥
        key_file = os.path.join(os.path.dirname(__file__), '..', '..', '.secret_key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # 生成新的密钥并保存
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # 设置文件权限为只有所有者可读
            os.chmod(key_file, 0o600)
            logger.warning(f"生成新的主密钥并保存到 {key_file}")
            return key
    
    def _create_cipher_suite(self):
        """创建加密套件"""
        try:
            # 如果master_key已经是Fernet格式的密钥，直接使用
            if len(self.master_key) == 44:  # Fernet密钥长度
                return Fernet(self.master_key)
            
            # 否则使用PBKDF2派生Fernet密钥
            salt = b'sremanage_salt'  # 在生产环境中应该使用随机salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
            return Fernet(key)
        except Exception as e:
            logger.error(f"创建加密套件失败: {e}")
            # 作为备用方案，生成新的密钥
            key = Fernet.generate_key()
            return Fernet(key)
    
    def encrypt_password(self, password):
        """
        加密密码
        
        Args:
            password: 明文密码
            
        Returns:
            加密后的密码（base64编码的字符串）
        """
        if not password:
            return None
        
        try:
            encrypted_bytes = self.cipher_suite.encrypt(password.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"密码加密失败: {e}")
            raise Exception("密码加密失败")
    
    def decrypt_password(self, encrypted_password):
        """
        解密密码
        
        Args:
            encrypted_password: 加密的密码（base64编码的字符串）
            
        Returns:
            明文密码
        """
        if not encrypted_password:
            return None
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode('utf-8'))
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"密码解密失败: {e}")
            # 如果解密失败，可能是旧的明文密码，直接返回
            logger.warning("解密失败，可能是明文密码，建议重新加密存储")
            return encrypted_password
    
    def is_encrypted(self, password):
        """
        检查密码是否已加密
        
        Args:
            password: 待检查的密码
            
        Returns:
            True if encrypted, False if plaintext
        """
        if not password:
            return False
        
        try:
            # 尝试解密，如果成功说明是加密的
            encrypted_bytes = base64.urlsafe_b64decode(password.encode('utf-8'))
            self.cipher_suite.decrypt(encrypted_bytes)
            return True
        except:
            # 解密失败，可能是明文
            return False

# 全局密码管理器实例
password_manager = PasswordManager()

def encrypt_sensitive_data(data):
    """加密敏感数据的便捷函数"""
    return password_manager.encrypt_password(data)

def decrypt_sensitive_data(encrypted_data):
    """解密敏感数据的便捷函数"""
    return password_manager.decrypt_password(encrypted_data)

def is_data_encrypted(data):
    """检查数据是否已加密的便捷函数"""
    return password_manager.is_encrypted(data)