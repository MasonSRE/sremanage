"""
API安全增强模块
提供输入验证、安全审计、防护机制等功能
"""

import logging
import time
import hashlib
import hmac
import secrets
import re
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify, g
import ipaddress

logger = logging.getLogger(__name__)

class SecurityAuditor:
    """安全审计器"""
    
    def __init__(self):
        self._audit_logs = deque(maxlen=1000)  # 保存最近1000条审计日志
        self._security_events = defaultdict(list)
        self._suspicious_ips = defaultdict(int)
        self._failed_attempts = defaultdict(list)
        
    def log_security_event(self, event_type: str, user_id: str = None, 
                          ip_address: str = None, details: Dict[str, Any] = None):
        """
        记录安全事件
        
        Args:
            event_type: 事件类型
            user_id: 用户ID
            ip_address: IP地址
            details: 事件详情
        """
        timestamp = datetime.now()
        
        event = {
            'timestamp': timestamp,
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {},
            'severity': self._get_event_severity(event_type)
        }
        
        self._audit_logs.append(event)
        self._security_events[event_type].append(event)
        
        # 记录可疑IP
        if event_type in ['login_failed', 'api_abuse', 'sql_injection_attempt']:
            if ip_address:
                self._suspicious_ips[ip_address] += 1
        
        # 记录失败尝试
        if event_type == 'login_failed':
            key = f"{user_id or 'unknown'}_{ip_address or 'unknown'}"
            self._failed_attempts[key].append(timestamp)
            
            # 清理过期记录
            cutoff = timestamp - timedelta(hours=1)
            self._failed_attempts[key] = [
                t for t in self._failed_attempts[key] if t > cutoff
            ]
        
        # 高严重性事件立即记录
        if event['severity'] == 'high':
            logger.warning(f"高安全风险事件: {event_type} - {details}")
            
    def _get_event_severity(self, event_type: str) -> str:
        """获取事件严重性等级"""
        high_severity_events = [
            'sql_injection_attempt',
            'xss_attempt', 
            'unauthorized_access',
            'privilege_escalation',
            'data_breach_attempt'
        ]
        
        medium_severity_events = [
            'login_failed',
            'api_abuse',
            'suspicious_request',
            'invalid_token'
        ]
        
        if event_type in high_severity_events:
            return 'high'
        elif event_type in medium_severity_events:
            return 'medium'
        else:
            return 'low'
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取安全事件摘要"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = [event for event in self._audit_logs if event['timestamp'] > cutoff]
        
        # 统计事件类型
        event_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for event in recent_events:
            event_counts[event['event_type']] += 1
            severity_counts[event['severity']] += 1
        
        # 获取最可疑的IP
        top_suspicious_ips = sorted(
            self._suspicious_ips.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'summary': {
                'total_events': len(recent_events),
                'high_severity': severity_counts['high'],
                'medium_severity': severity_counts['medium'],
                'low_severity': severity_counts['low']
            },
            'event_types': dict(event_counts),
            'suspicious_ips': top_suspicious_ips,
            'recent_events': recent_events[-20:],  # 最近20个事件
            'analysis_period': f'{hours}小时'
        }
    
    def is_ip_suspicious(self, ip_address: str) -> bool:
        """检查IP是否可疑"""
        return self._suspicious_ips.get(ip_address, 0) > 10
    
    def check_brute_force_attempt(self, user_id: str, ip_address: str) -> bool:
        """检查是否存在暴力破解尝试"""
        key = f"{user_id}_{ip_address}"
        attempts = self._failed_attempts.get(key, [])
        
        # 1小时内超过5次失败尝试
        return len(attempts) > 5

# 全局安全审计器
security_auditor = SecurityAuditor()

class InputValidator:
    """输入验证器"""
    
    # 危险模式定义
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bxp_\w+|\bsp_\w+)",
        r"(char\(\d+\))",
        r"(0x[0-9a-f]+)"
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>"
    ]
    
    @classmethod
    def validate_sql_injection(cls, input_data: str) -> bool:
        """检查SQL注入"""
        if not isinstance(input_data, str):
            return False
            
        input_lower = input_data.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def validate_xss(cls, input_data: str) -> bool:
        """检查XSS攻击"""
        if not isinstance(input_data, str):
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True
                
        return False
    
    @classmethod
    def validate_ip_address(cls, ip_str: str) -> bool:
        """验证IP地址格式"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    @classmethod
    def validate_api_parameters(cls, params: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证API参数"""
        errors = defaultdict(list)
        
        for key, value in params.items():
            if isinstance(value, str):
                # 检查SQL注入
                if cls.validate_sql_injection(value):
                    errors['sql_injection'].append(key)
                
                # 检查XSS
                if cls.validate_xss(value):
                    errors['xss_attempt'].append(key)
                
                # 检查过长输入
                if len(value) > 10000:  # 10KB限制
                    errors['input_too_long'].append(key)
        
        return dict(errors)

class APISecurityManager:
    """API安全管理器"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.api_keys = {}
        self.request_signatures = deque(maxlen=1000)
        
    def generate_api_key(self, user_id: str) -> str:
        """生成API密钥"""
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.api_keys[key_hash] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_used': None,
            'usage_count': 0
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """验证API密钥"""
        if not api_key:
            return None
            
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_info = self.api_keys.get(key_hash)
        
        if key_info:
            key_info['last_used'] = datetime.now()
            key_info['usage_count'] += 1
            return key_info['user_id']
        
        return None
    
    def generate_request_signature(self, method: str, url: str, body: str, 
                                 timestamp: str, api_key: str) -> str:
        """生成请求签名"""
        message = f"{method}|{url}|{body}|{timestamp}"
        signature = hmac.new(
            api_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def validate_request_signature(self, signature: str, method: str, url: str,
                                 body: str, timestamp: str, api_key: str) -> bool:
        """验证请求签名"""
        expected_signature = self.generate_request_signature(
            method, url, body, timestamp, api_key
        )
        
        return hmac.compare_digest(signature, expected_signature)
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """检查IP是否被阻止"""
        return ip_address in self.blocked_ips
    
    def block_ip(self, ip_address: str):
        """阻止IP地址"""
        self.blocked_ips.add(ip_address)
        security_auditor.log_security_event(
            'ip_blocked',
            ip_address=ip_address,
            details={'reason': 'suspicious_activity'}
        )

# 全局API安全管理器
api_security_manager = APISecurityManager()

def security_audit(event_type: str):
    """安全审计装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def security_audit_wrapper(*args, **kwargs):
            start_time = time.time()
            user_id = getattr(g, 'current_user_id', None)
            ip_address = request.remote_addr
            
            try:
                # 记录API调用开始
                security_auditor.log_security_event(
                    f'{event_type}_start',
                    user_id=user_id,
                    ip_address=ip_address,
                    details={
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'user_agent': request.headers.get('User-Agent')
                    }
                )
                
                result = func(*args, **kwargs)
                
                # 记录成功调用
                duration = time.time() - start_time
                security_auditor.log_security_event(
                    f'{event_type}_success',
                    user_id=user_id,
                    ip_address=ip_address,
                    details={
                        'duration': duration,
                        'endpoint': request.endpoint
                    }
                )
                
                return result
                
            except Exception as e:
                # 记录失败调用
                duration = time.time() - start_time
                security_auditor.log_security_event(
                    f'{event_type}_error',
                    user_id=user_id,
                    ip_address=ip_address,
                    details={
                        'error': str(e),
                        'duration': duration,
                        'endpoint': request.endpoint
                    }
                )
                raise
        
        return security_audit_wrapper
    return decorator

def validate_input_security():
    """输入安全验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def input_security_wrapper(*args, **kwargs):
            user_id = getattr(g, 'current_user_id', None)
            ip_address = request.remote_addr
            
            # 检查IP是否被阻止
            if api_security_manager.is_ip_blocked(ip_address):
                security_auditor.log_security_event(
                    'blocked_ip_access',
                    user_id=user_id,
                    ip_address=ip_address
                )
                return jsonify({
                    'success': False,
                    'message': '访问被拒绝',
                    'error_code': 'IP_BLOCKED'
                }), 403
            
            # 检查IP是否可疑
            if security_auditor.is_ip_suspicious(ip_address):
                security_auditor.log_security_event(
                    'suspicious_ip_access',
                    user_id=user_id,
                    ip_address=ip_address
                )
            
            # 验证请求参数
            request_data = {}
            
            if request.method == 'GET':
                request_data = request.args.to_dict()
            elif request.method in ['POST', 'PUT', 'PATCH']:
                if request.is_json:
                    request_data = request.get_json() or {}
                else:
                    request_data = request.form.to_dict()
            
            # 输入验证
            validation_errors = InputValidator.validate_api_parameters(request_data)
            
            if validation_errors:
                # 记录安全事件
                for error_type, fields in validation_errors.items():
                    security_auditor.log_security_event(
                        error_type,
                        user_id=user_id,
                        ip_address=ip_address,
                        details={
                            'fields': fields,
                            'endpoint': request.endpoint,
                            'method': request.method
                        }
                    )
                
                # SQL注入或XSS尝试，立即阻止IP
                if 'sql_injection' in validation_errors or 'xss_attempt' in validation_errors:
                    api_security_manager.block_ip(ip_address)
                    
                    return jsonify({
                        'success': False,
                        'message': '检测到恶意请求，访问已被阻止',
                        'error_code': 'MALICIOUS_REQUEST'
                    }), 400
            
            return func(*args, **kwargs)
        
        return input_security_wrapper
    return decorator

def enhanced_rate_limit(max_requests: int = 100, window_seconds: int = 60, 
                       per_user: bool = True):
    """增强的速率限制装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def enhanced_rate_limit_wrapper(*args, **kwargs):
            user_id = getattr(g, 'current_user_id', None)
            ip_address = request.remote_addr
            
            # 生成限制键
            if per_user and user_id:
                limit_key = f"user_{user_id}"
            else:
                limit_key = f"ip_{ip_address}"
            
            # 这里应该使用Redis等外部存储来实现分布式限流
            # 简化实现，使用内存存储
            from app.utils.performance import rate_limiter
            
            if not rate_limiter.is_allowed(limit_key):
                # 记录限流事件
                security_auditor.log_security_event(
                    'rate_limit_exceeded',
                    user_id=user_id,
                    ip_address=ip_address,
                    details={
                        'limit_key': limit_key,
                        'endpoint': request.endpoint
                    }
                )
                
                return jsonify({
                    'success': False,
                    'message': '请求过于频繁，请稍后重试',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }), 429
            
            return func(*args, **kwargs)
        
        return enhanced_rate_limit_wrapper
    return decorator

def require_api_key():
    """API密钥验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def api_key_wrapper(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            ip_address = request.remote_addr
            
            if not api_key:
                security_auditor.log_security_event(
                    'missing_api_key',
                    ip_address=ip_address,
                    details={'endpoint': request.endpoint}
                )
                return jsonify({
                    'success': False,
                    'message': '缺少API密钥',
                    'error_code': 'MISSING_API_KEY'
                }), 401
            
            user_id = api_security_manager.validate_api_key(api_key)
            if not user_id:
                security_auditor.log_security_event(
                    'invalid_api_key',
                    ip_address=ip_address,
                    details={'endpoint': request.endpoint}
                )
                return jsonify({
                    'success': False,
                    'message': '无效的API密钥',
                    'error_code': 'INVALID_API_KEY'
                }), 401
            
            # 设置当前用户
            g.current_user_id = user_id
            
            return func(*args, **kwargs)
        
        return api_key_wrapper
    return decorator

class SecurityHealthChecker:
    """安全健康检查器"""
    
    @staticmethod
    def check_security_status() -> Dict[str, Any]:
        """检查系统安全状态"""
        summary = security_auditor.get_security_summary(24)
        
        # 安全等级评估
        security_level = 'normal'
        warnings = []
        
        if summary['summary']['high_severity'] > 0:
            security_level = 'critical'
            warnings.append(f"检测到 {summary['summary']['high_severity']} 个高风险安全事件")
        
        if summary['summary']['medium_severity'] > 20:
            if security_level != 'critical':
                security_level = 'warning'
            warnings.append(f"检测到 {summary['summary']['medium_severity']} 个中风险安全事件")
        
        # 检查可疑IP
        suspicious_count = len([ip for ip, count in summary['suspicious_ips'] if count > 5])
        if suspicious_count > 0:
            if security_level == 'normal':
                security_level = 'warning'
            warnings.append(f"发现 {suspicious_count} 个可疑IP地址")
        
        return {
            'security_level': security_level,
            'warnings': warnings,
            'summary': summary,
            'recommendations': SecurityHealthChecker._generate_security_recommendations(summary)
        }
    
    @staticmethod
    def _generate_security_recommendations(summary: Dict[str, Any]) -> List[str]:
        """生成安全建议"""
        recommendations = []
        
        if summary['summary']['high_severity'] > 0:
            recommendations.append('立即检查高风险安全事件，采取紧急防护措施')
        
        if summary['summary']['medium_severity'] > 10:
            recommendations.append('关注中风险安全事件，加强监控和防护')
        
        if len(summary['suspicious_ips']) > 5:
            recommendations.append('考虑增强IP白名单机制，限制可疑IP访问')
        
        event_types = summary['event_types']
        if event_types.get('login_failed', 0) > 50:
            recommendations.append('登录失败次数较多，建议增强身份验证机制')
        
        if event_types.get('api_abuse', 0) > 20:
            recommendations.append('API滥用检测较多，建议调整速率限制策略')
        
        if not recommendations:
            recommendations.append('系统安全状态良好，继续保持监控')
        
        return recommendations