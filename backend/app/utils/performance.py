"""
性能优化工具模块
提供API响应时间监控、缓存管理、并发控制等功能
"""

import time
import functools
import threading
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控类，用于监控API响应时间和性能指标"""
    
    def __init__(self):
        self._metrics = defaultdict(list)
        self._request_counts = defaultdict(int)
        self._error_counts = defaultdict(int)
        self._slow_queries = deque(maxlen=100)  # 保存最近100个慢查询
        self._lock = threading.Lock()
        
    def record_request(self, endpoint: str, duration: float, status: str = 'success', error: str = None):
        """
        记录请求性能指标
        
        Args:
            endpoint: API端点
            duration: 请求耗时(秒)
            status: 请求状态 ('success', 'error')
            error: 错误信息
        """
        with self._lock:
            timestamp = datetime.now()
            
            # 记录响应时间
            self._metrics[endpoint].append({
                'timestamp': timestamp,
                'duration': duration,
                'status': status,
                'error': error
            })
            
            # 只保留最近1小时的数据
            cutoff_time = timestamp - timedelta(hours=1)
            self._metrics[endpoint] = [
                m for m in self._metrics[endpoint] 
                if m['timestamp'] > cutoff_time
            ]
            
            # 记录请求计数
            self._request_counts[endpoint] += 1
            
            # 记录错误计数
            if status == 'error':
                self._error_counts[endpoint] += 1
            
            # 记录慢查询 (>3秒)
            if duration > 3.0:
                self._slow_queries.append({
                    'endpoint': endpoint,
                    'duration': duration,
                    'timestamp': timestamp,
                    'error': error
                })
    
    def get_metrics(self, endpoint: str = None) -> Dict[str, Any]:
        """
        获取性能指标
        
        Args:
            endpoint: 特定端点，None表示获取所有端点指标
            
        Returns:
            性能指标字典
        """
        with self._lock:
            if endpoint:
                return self._get_endpoint_metrics(endpoint)
            else:
                return self._get_all_metrics()
    
    def _get_endpoint_metrics(self, endpoint: str) -> Dict[str, Any]:
        """获取特定端点的性能指标"""
        metrics = self._metrics.get(endpoint, [])
        if not metrics:
            return {
                'endpoint': endpoint,
                'request_count': 0,
                'avg_duration': 0,
                'max_duration': 0,
                'min_duration': 0,
                'error_rate': 0,
                'success_rate': 100
            }
        
        durations = [m['duration'] for m in metrics]
        success_count = len([m for m in metrics if m['status'] == 'success'])
        
        return {
            'endpoint': endpoint,
            'request_count': len(metrics),
            'avg_duration': round(sum(durations) / len(durations), 3),
            'max_duration': round(max(durations), 3),
            'min_duration': round(min(durations), 3),
            'error_rate': round((len(metrics) - success_count) / len(metrics) * 100, 2),
            'success_rate': round(success_count / len(metrics) * 100, 2),
            'recent_errors': [m['error'] for m in metrics[-10:] if m['error']]
        }
    
    def _get_all_metrics(self) -> Dict[str, Any]:
        """获取所有端点的性能指标汇总"""
        all_metrics = {}
        total_requests = 0
        total_errors = 0
        all_durations = []
        
        for endpoint in self._metrics:
            endpoint_metrics = self._get_endpoint_metrics(endpoint)
            all_metrics[endpoint] = endpoint_metrics
            
            total_requests += endpoint_metrics['request_count']
            total_errors += endpoint_metrics['request_count'] * endpoint_metrics['error_rate'] / 100
            
            # 收集所有响应时间用于整体统计
            endpoint_durations = [m['duration'] for m in self._metrics[endpoint]]
            all_durations.extend(endpoint_durations)
        
        # 整体性能统计
        overall_stats = {
            'total_requests': total_requests,
            'total_errors': int(total_errors),
            'overall_error_rate': round(total_errors / total_requests * 100, 2) if total_requests > 0 else 0,
            'avg_response_time': round(sum(all_durations) / len(all_durations), 3) if all_durations else 0,
            'slow_queries_count': len(self._slow_queries),
            'slow_queries': list(self._slow_queries)[-10:]  # 最近10个慢查询
        }
        
        return {
            'overall': overall_stats,
            'endpoints': all_metrics,
            'timestamp': datetime.now().isoformat()
        }

# 全局性能监控实例
performance_monitor = PerformanceMonitor()

def monitor_performance(endpoint_name: str = None):
    """
    性能监控装饰器
    
    Args:
        endpoint_name: 端点名称，默认使用函数名
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def performance_wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or f"{func.__module__}.{func.__name__}"
            error_msg = None
            status = 'success'
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                error_msg = str(e)
                logger.error(f"API {endpoint} 执行失败: {e}")
                raise
            finally:
                duration = time.time() - start_time
                performance_monitor.record_request(endpoint, duration, status, error_msg)
                
                # 记录慢查询日志
                if duration > 3.0:
                    logger.warning(f"慢查询检测: {endpoint} 耗时 {duration:.3f}秒")
        
        return performance_wrapper
    return decorator

class SimpleCache:
    """简单的内存缓存实现"""
    
    def __init__(self, default_ttl: int = 300):  # 默认5分钟TTL
        self._cache = {}
        self._ttl = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                return None
            
            # 检查是否过期
            if key in self._ttl and datetime.now() > self._ttl[key]:
                del self._cache[key]
                del self._ttl[key]
                return None
            
            return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """设置缓存值"""
        with self._lock:
            self._cache[key] = value
            
            # 设置过期时间
            if ttl is None:
                ttl = self._default_ttl
            
            if ttl > 0:
                self._ttl[key] = datetime.now() + timedelta(seconds=ttl)
    
    def delete(self, key: str) -> None:
        """删除缓存值"""
        with self._lock:
            self._cache.pop(key, None)
            self._ttl.pop(key, None)
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._ttl.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            current_time = datetime.now()
            active_keys = 0
            expired_keys = 0
            
            for key in self._cache:
                if key in self._ttl and current_time > self._ttl[key]:
                    expired_keys += 1
                else:
                    active_keys += 1
            
            return {
                'total_keys': len(self._cache),
                'active_keys': active_keys,
                'expired_keys': expired_keys,
                'cache_size_mb': len(str(self._cache)) / 1024 / 1024
            }

# 全局缓存实例
simple_cache = SimpleCache()

def cached(ttl: int = 300, key_prefix: str = ""):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存生存时间(秒) 
        key_prefix: 缓存键前缀
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def cached_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = simple_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            simple_cache.set(cache_key, result, ttl)
            logger.debug(f"缓存设置: {cache_key}")
            
            return result
        
        return cached_wrapper
    return decorator

class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests = defaultdict(deque)
        self._lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """
        检查是否允许请求
        
        Args:
            identifier: 请求标识符(如IP地址、用户ID等)
            
        Returns:
            True表示允许，False表示超过限制
        """
        with self._lock:
            current_time = time.time()
            window_start = current_time - self._window_seconds
            
            # 清理过期的请求记录
            requests = self._requests[identifier]
            while requests and requests[0] < window_start:
                requests.popleft()
            
            # 检查是否超过限制
            if len(requests) >= self._max_requests:
                return False
            
            # 记录当前请求
            requests.append(current_time)
            return True
    
    def get_stats(self, identifier: str) -> Dict[str, Any]:
        """获取速率限制统计"""
        with self._lock:
            current_time = time.time()
            window_start = current_time - self._window_seconds
            
            # 清理过期记录
            requests = self._requests[identifier]
            while requests and requests[0] < window_start:
                requests.popleft()
            
            return {
                'identifier': identifier,
                'current_requests': len(requests),
                'max_requests': self._max_requests,
                'window_seconds': self._window_seconds,
                'remaining_requests': max(0, self._max_requests - len(requests)),
                'reset_time': window_start + self._window_seconds
            }

# 全局限流器实例
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 100, window_seconds: int = 60, identifier_func: Callable = None):
    """
    速率限制装饰器
    
    Args:
        max_requests: 最大请求数
        window_seconds: 时间窗口(秒)
        identifier_func: 标识符提取函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def rate_limit_wrapper(*args, **kwargs):
            # 提取请求标识符
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                # 默认使用函数名作为标识符
                identifier = f"{func.__name__}_global"
            
            # 检查速率限制
            limiter = RateLimiter(max_requests, window_seconds)
            if not limiter.is_allowed(identifier):
                from flask import jsonify
                logger.warning(f"速率限制触发: {identifier} 超过 {max_requests}/{window_seconds}s 限制")
                return jsonify({
                    'success': False,
                    'message': '请求过于频繁，请稍后重试',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }), 429
            
            return func(*args, **kwargs)
        
        return rate_limit_wrapper
    return decorator