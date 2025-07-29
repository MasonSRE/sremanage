import logging
import os
from logging.handlers import RotatingFileHandler

# 创建 logs 目录（如果不存在）
if not os.path.exists('logs'):
    os.makedirs('logs')

def setup_logger(name=None):
    """
    设置日志记录器
    :param name: 日志记录器名称
    :return: Logger 实例
    """
    # 创建日志记录器
    logger = logging.getLogger(name or __name__)
    
    # 如果已经设置过处理器，就不再重复设置
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # 创建文件处理器
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 设置格式化器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建一个默认的日志记录器实例
logger = setup_logger('app')

def get_logger(name=None):
    """
    获取日志记录器
    :param name: 日志记录器名称
    :return: Logger 实例
    """
    return setup_logger(name) 