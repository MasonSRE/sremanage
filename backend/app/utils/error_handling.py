"""
异常处理机制模块
提供全局异常处理、错误分类、恢复机制、异常监控等功能
"""

import logging
import traceback
import json
import time
from typing import Dict, List, Any, Optional, Callable, Type
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
from flask import request, jsonify, g, current_app
import threading

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ErrorCategory(Enum):
    """错误分类"""
    VALIDATION = "validation"          # 输入验证错误
    AUTHENTICATION = "authentication"  # 认证错误
    AUTHORIZATION = "authorization"    # 授权错误
    DATABASE = "database"             # 数据库错误
    NETWORK = "network"               # 网络错误
    EXTERNAL_API = "external_api"     # 外部API错误
    SYSTEM = "system"                 # 系统错误
    BUSINESS = "business"             # 业务逻辑错误
    UNKNOWN = "unknown"               # 未知错误

class ErrorCode:
    """标准化错误代码"""
    
    # 验证错误 (1000-1999)
    INVALID_INPUT = 1001
    MISSING_PARAMETER = 1002
    INVALID_FORMAT = 1003
    DATA_VALIDATION_FAILED = 1004
    
    # 认证错误 (2000-2999)
    AUTHENTICATION_FAILED = 2001
    TOKEN_EXPIRED = 2002
    TOKEN_INVALID = 2003
    CREDENTIALS_INVALID = 2004
    
    # 授权错误 (3000-3999)
    PERMISSION_DENIED = 3001
    ROLE_REQUIRED = 3002
    RESOURCE_ACCESS_DENIED = 3003
    
    # 数据库错误 (4000-4999)
    DATABASE_CONNECTION_FAILED = 4001
    QUERY_EXECUTION_FAILED = 4002
    DATA_INTEGRITY_ERROR = 4003
    TRANSACTION_FAILED = 4004
    
    # 网络错误 (5000-5999)
    NETWORK_TIMEOUT = 5001
    CONNECTION_REFUSED = 5002
    DNS_RESOLUTION_FAILED = 5003
    
    # 外部API错误 (6000-6999)
    EXTERNAL_API_UNAVAILABLE = 6001
    EXTERNAL_API_RATE_LIMITED = 6002
    EXTERNAL_API_ERROR = 6003
    
    # 系统错误 (7000-7999)
    INTERNAL_SERVER_ERROR = 7001
    SERVICE_UNAVAILABLE = 7002
    RESOURCE_EXHAUSTED = 7003
    MEMORY_ERROR = 7004
    
    # 业务错误 (8000-8999)
    BUSINESS_RULE_VIOLATION = 8001
    RESOURCE_NOT_FOUND = 8002
    OPERATION_NOT_ALLOWED = 8003
    STATE_CONFLICT = 8004

class CustomException(Exception):
    """自定义异常基类"""
    
    def __init__(self, message: str, error_code: int = None, 
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Dict[str, Any] = None,
                 recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ErrorCode.INTERNAL_SERVER_ERROR
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = datetime.now()
        self.request_id = getattr(g, 'request_id', None)
        self.user_id = getattr(g, 'current_user_id', None)

class ValidationError(CustomException):
    """验证错误"""
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(
            message,
            error_code=ErrorCode.DATA_VALIDATION_FAILED,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        if field:
            self.details['field'] = field

class AuthenticationError(CustomException):
    """认证错误"""
    def __init__(self, message: str = "身份验证失败", **kwargs):
        super().__init__(
            message,
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            **kwargs
        )

class AuthorizationError(CustomException):
    """授权错误"""
    def __init__(self, message: str = "权限不足", **kwargs):
        super().__init__(
            message,
            error_code=ErrorCode.PERMISSION_DENIED,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.MEDIUM,
            recoverable=False,
            **kwargs
        )

class DatabaseError(CustomException):
    """数据库错误"""
    def __init__(self, message: str, operation: str = None, **kwargs):
        super().__init__(
            message,
            error_code=ErrorCode.DATABASE_CONNECTION_FAILED,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        if operation:
            self.details['operation'] = operation

class NetworkError(CustomException):
    """网络错误"""
    def __init__(self, message: str, url: str = None, **kwargs):
        super().__init__(
            message,
            error_code=ErrorCode.NETWORK_TIMEOUT,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        if url:
            self.details['url'] = url

class ExternalAPIError(CustomException):
    """外部API错误"""
    def __init__(self, message: str, api_name: str = None, status_code: int = None, **kwargs):
        super().__init__(
            message,
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            category=ErrorCategory.EXTERNAL_API,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        if api_name:
            self.details['api_name'] = api_name
        if status_code:
            self.details['status_code'] = status_code

class BusinessLogicError(CustomException):
    """业务逻辑错误"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=ErrorCode.BUSINESS_RULE_VIOLATION,
            category=ErrorCategory.BUSINESS,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_stats = defaultdict(int)
        self.error_history = deque(maxlen=1000)
        self.recovery_strategies = {}
        self.notification_handlers = []
        self.error_patterns = defaultdict(list)
        self._lock = threading.Lock()
    
    def register_recovery_strategy(self, error_type: Type[Exception], 
                                 strategy: Callable[[Exception], Any]):
        """注册错误恢复策略"""
        self.recovery_strategies[error_type] = strategy
        logger.info(f"注册恢复策略: {error_type.__name__}")
    
    def register_notification_handler(self, handler: Callable[[CustomException], None]):
        """注册错误通知处理器"""
        self.notification_handlers.append(handler)
        logger.info("注册错误通知处理器")
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理错误"""
        with self._lock:
            # 转换为自定义异常
            if not isinstance(error, CustomException):
                error = self._convert_to_custom_exception(error)
            
            # 记录错误
            self._record_error(error, context)
            
            # 尝试恢复
            recovery_result = self._attempt_recovery(error)
            
            # 发送通知
            self._send_notifications(error)
            
            # 分析错误模式
            self._analyze_error_patterns(error)
            
            # 生成响应
            return self._generate_error_response(error, recovery_result)
    
    def _convert_to_custom_exception(self, error: Exception) -> CustomException:
        """将标准异常转换为自定义异常"""
        error_message = str(error)
        error_type = type(error).__name__
        
        # 数据库相关错误
        if any(keyword in error_message.lower() for keyword in ['mysql', 'database', 'connection', 'cursor']):
            return DatabaseError(f"数据库错误: {error_message}", 
                               details={'original_type': error_type})
        
        # 网络相关错误
        elif any(keyword in error_message.lower() for keyword in ['timeout', 'connection', 'network', 'refused']):
            return NetworkError(f"网络错误: {error_message}",
                              details={'original_type': error_type})
        
        # 权限相关错误
        elif any(keyword in error_message.lower() for keyword in ['permission', 'forbidden', 'unauthorized']):
            return AuthorizationError(f"权限错误: {error_message}",
                                    details={'original_type': error_type})
        
        # 验证相关错误
        elif any(keyword in error_message.lower() for keyword in ['validation', 'invalid', 'required']):
            return ValidationError(f"验证错误: {error_message}",
                                 details={'original_type': error_type})
        
        # 默认系统错误
        else:
            return CustomException(
                f"系统错误: {error_message}",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                details={'original_type': error_type}
            )
    
    def _record_error(self, error: CustomException, context: Dict[str, Any] = None):
        """记录错误信息"""
        error_record = {
            'timestamp': error.timestamp.isoformat(),
            'message': error.message,
            'error_code': error.error_code,
            'category': error.category.value,
            'severity': error.severity.name,
            'recoverable': error.recoverable,
            'request_id': error.request_id,
            'user_id': error.user_id,
            'details': error.details,
            'context': context or {},
            'traceback': traceback.format_exc() if current_app.debug else None
        }
        
        # 添加请求信息
        if request:
            error_record['request_info'] = {
                'method': request.method,
                'url': request.url,
                'endpoint': request.endpoint,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
        
        self.error_history.append(error_record)
        self.error_stats[error.category.value] += 1
        
        # 根据严重程度记录日志
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"严重错误: {error.message}", extra=error_record)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"高级错误: {error.message}", extra=error_record)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"中级错误: {error.message}", extra=error_record)
        else:
            logger.info(f"低级错误: {error.message}", extra=error_record)
    
    def _attempt_recovery(self, error: CustomException) -> Optional[Any]:
        """尝试错误恢复"""
        if not error.recoverable:
            return None
        
        error_type = type(error)
        strategy = self.recovery_strategies.get(error_type)
        
        if strategy:
            try:
                logger.info(f"尝试恢复错误: {error.message}")
                result = strategy(error)
                logger.info(f"错误恢复成功: {error.message}")
                return result
            except Exception as recovery_error:
                logger.error(f"错误恢复失败: {recovery_error}")
                return None
        
        return None
    
    def _send_notifications(self, error: CustomException):
        """发送错误通知"""
        for handler in self.notification_handlers:
            try:
                handler(error)
            except Exception as notification_error:
                logger.error(f"错误通知发送失败: {notification_error}")
    
    def _analyze_error_patterns(self, error: CustomException):
        """分析错误模式"""
        pattern_key = f"{error.category.value}:{error.error_code}"
        self.error_patterns[pattern_key].append({
            'timestamp': error.timestamp,
            'user_id': error.user_id,
            'details': error.details
        })
        
        # 检测频繁错误
        recent_errors = [
            e for e in self.error_patterns[pattern_key]
            if datetime.now() - e['timestamp'] < timedelta(minutes=5)
        ]
        
        if len(recent_errors) > 10:  # 5分钟内超过10次同类错误
            logger.warning(f"检测到频繁错误模式: {pattern_key}, 近5分钟内发生{len(recent_errors)}次")
    
    def _generate_error_response(self, error: CustomException, 
                               recovery_result: Any = None) -> Dict[str, Any]:
        """生成错误响应"""
        response = {
            'success': False,
            'error_code': error.error_code,
            'message': error.message,
            'category': error.category.value,
            'severity': error.severity.name,
            'recoverable': error.recoverable,
            'timestamp': error.timestamp.isoformat()
        }
        
        # 添加请求ID用于追踪
        if error.request_id:
            response['request_id'] = error.request_id
        
        # 在调试模式下添加详细信息
        if current_app.debug:
            response['details'] = error.details
            response['traceback'] = traceback.format_exc()
        
        # 添加恢复结果
        if recovery_result is not None:
            response['recovery_result'] = recovery_result
            response['recovered'] = True
        
        return response
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """获取错误统计信息"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            error for error in self.error_history
            if datetime.fromisoformat(error['timestamp']) > cutoff
        ]
        
        # 按分类统计
        category_stats = defaultdict(int)
        severity_stats = defaultdict(int)
        hourly_stats = defaultdict(int)
        
        for error in recent_errors:
            category_stats[error['category']] += 1
            severity_stats[error['severity']] += 1
            
            # 按小时统计
            hour = datetime.fromisoformat(error['timestamp']).hour
            hourly_stats[hour] += 1
        
        # 查找最频繁的错误
        error_frequency = defaultdict(int)
        for error in recent_errors:
            error_key = f"{error['category']}:{error['error_code']}"
            error_frequency[error_key] += 1
        
        top_errors = sorted(error_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_errors': len(recent_errors),
            'query_period': f'{hours}小时',
            'category_distribution': dict(category_stats),
            'severity_distribution': dict(severity_stats),
            'hourly_distribution': dict(hourly_stats),
            'top_errors': top_errors,
            'recovery_rate': self._calculate_recovery_rate(recent_errors),
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_recovery_rate(self, errors: List[Dict[str, Any]]) -> float:
        """计算恢复成功率"""
        recoverable_errors = [e for e in errors if e.get('recoverable', False)]
        if not recoverable_errors:
            return 0.0
        
        # 这里简化实现，实际应该追踪恢复结果
        return 0.7  # 假设70%的可恢复错误成功恢复
    
    def clear_old_errors(self, days: int = 7):
        """清理旧的错误记录"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with self._lock:
            # 清理错误历史
            filtered_history = deque(maxlen=1000)
            for error in self.error_history:
                if datetime.fromisoformat(error['timestamp']) > cutoff:
                    filtered_history.append(error)
            
            self.error_history = filtered_history
            
            # 清理错误模式
            for pattern_key in list(self.error_patterns.keys()):
                self.error_patterns[pattern_key] = [
                    e for e in self.error_patterns[pattern_key]
                    if datetime.now() - e['timestamp'] < timedelta(days=days)
                ]
                
                if not self.error_patterns[pattern_key]:
                    del self.error_patterns[pattern_key]
        
        logger.info(f"清理了{days}天前的错误记录")

# 全局错误处理器实例
error_handler = ErrorHandler()

# 错误处理装饰器
def handle_exceptions(recovery_strategy: Callable = None, 
                     notification: bool = True,
                     reraise: bool = False):
    """异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 添加请求ID用于追踪
                if not hasattr(g, 'request_id'):
                    g.request_id = f"req_{int(time.time())}{id(e) % 1000}"
                
                # 处理错误
                error_response = error_handler.handle_error(e, {
                    'function': func.__name__,
                    'args': str(args) if args else None,
                    'kwargs': str(kwargs) if kwargs else None
                })
                
                if reraise:
                    raise
                
                # 返回JSON错误响应
                status_code = 500
                if isinstance(e, ValidationError):
                    status_code = 400
                elif isinstance(e, AuthenticationError):
                    status_code = 401
                elif isinstance(e, AuthorizationError):
                    status_code = 403
                elif isinstance(e, BusinessLogicError):
                    status_code = 422
                
                return jsonify(error_response), status_code
        
        return wrapper
    return decorator

# 便捷装饰器
def safe_execute(reraise: bool = False):
    """安全执行装饰器"""
    return handle_exceptions(reraise=reraise)

def with_recovery(strategy: Callable):
    """带恢复策略的装饰器"""
    return handle_exceptions(recovery_strategy=strategy)

# 恢复策略函数
def retry_on_network_error(error: NetworkError, max_retries: int = 3, delay: float = 1.0):
    """网络错误重试策略"""
    def retry_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except NetworkError as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.info(f"网络错误重试 {attempt + 1}/{max_retries}: {e.message}")
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        logger.error(f"网络错误重试失败，已达到最大重试次数")
                        raise
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return retry_decorator

def fallback_on_external_api_error(fallback_value: Any = None):
    """外部API错误降级策略"""
    def fallback_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ExternalAPIError as e:
                logger.warning(f"外部API错误，使用降级方案: {e.message}")
                return fallback_value
        
        return wrapper
    return fallback_decorator

# 注册默认恢复策略
error_handler.register_recovery_strategy(
    NetworkError,
    lambda error: {"strategy": "retry", "max_retries": 3}
)

error_handler.register_recovery_strategy(
    DatabaseError,
    lambda error: {"strategy": "reconnect", "fallback": "cache"}
)

# 默认通知处理器
def default_notification_handler(error: CustomException):
    """默认错误通知处理器"""
    if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
        # 这里可以集成邮件、短信、钉钉等通知方式
        logger.critical(f"重要错误通知: {error.message} (用户: {error.user_id})")

error_handler.register_notification_handler(default_notification_handler)