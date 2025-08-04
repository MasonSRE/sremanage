"""
重试和降级策略模块
提供智能重试机制、服务降级、熔断器、故障转移等功能
"""

import logging
import time
import random
import threading
from typing import Dict, List, Any, Optional, Callable, Type, Union
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import asyncio
import inspect

logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """重试策略"""
    FIXED_DELAY = "fixed_delay"           # 固定延迟
    LINEAR_BACKOFF = "linear_backoff"     # 线性退避
    EXPONENTIAL_BACKOFF = "exponential_backoff"  # 指数退避
    RANDOM_JITTER = "random_jitter"       # 随机抖动

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"     # 关闭状态，正常工作
    OPEN = "open"         # 开启状态，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态，试探性请求

class FallbackStrategy(Enum):
    """降级策略"""
    RETURN_DEFAULT = "return_default"     # 返回默认值
    RETURN_CACHED = "return_cached"       # 返回缓存数据
    CALL_BACKUP = "call_backup"           # 调用备用服务
    RETURN_EMPTY = "return_empty"         # 返回空结果
    RAISE_EXCEPTION = "raise_exception"   # 抛出异常

class RetryConfig:
    """重试配置"""
    
    def __init__(self, 
                 max_attempts: int = 3,
                 strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 backoff_multiplier: float = 2.0,
                 jitter: bool = True,
                 retry_on: List[Type[Exception]] = None,
                 stop_on: List[Type[Exception]] = None):
        self.max_attempts = max_attempts
        self.strategy = strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.retry_on = retry_on or [Exception]
        self.stop_on = stop_on or []

class CircuitBreakerConfig:
    """熔断器配置"""
    
    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 success_threshold: int = 3,
                 timeout: float = 10.0,
                 expected_exception: Type[Exception] = Exception):
        self.failure_threshold = failure_threshold  # 失败阈值
        self.recovery_timeout = recovery_timeout    # 恢复超时
        self.success_threshold = success_threshold  # 成功阈值
        self.timeout = timeout                      # 请求超时
        self.expected_exception = expected_exception

class FallbackConfig:
    """降级配置"""
    
    def __init__(self,
                 strategy: FallbackStrategy = FallbackStrategy.RETURN_DEFAULT,
                 default_value: Any = None,
                 backup_function: Callable = None,
                 cache_key: str = None,
                 cache_ttl: int = 300):
        self.strategy = strategy
        self.default_value = default_value
        self.backup_function = backup_function
        self.cache_key = cache_key
        self.cache_ttl = cache_ttl

class RetryManager:
    """重试管理器"""
    
    def __init__(self):
        self.retry_stats = defaultdict(lambda: {
            'total_attempts': 0,
            'total_successes': 0,
            'total_failures': 0,
            'last_success': None,
            'last_failure': None,
            'avg_attempts': 0.0
        })
        self._lock = threading.Lock()
    
    def execute_with_retry(self, func: Callable, config: RetryConfig, *args, **kwargs) -> Any:
        """执行带重试的函数"""
        func_name = f"{func.__module__}.{func.__name__}"
        attempt = 0
        last_exception = None
        
        while attempt < config.max_attempts:
            attempt += 1
            
            try:
                # 记录尝试
                with self._lock:
                    self.retry_stats[func_name]['total_attempts'] += 1
                
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 记录成功
                with self._lock:
                    stats = self.retry_stats[func_name]
                    stats['total_successes'] += 1
                    stats['last_success'] = datetime.now()
                    stats['avg_attempts'] = (stats['avg_attempts'] * (stats['total_successes'] - 1) + attempt) / stats['total_successes']
                
                logger.info(f"重试成功: {func_name}, 尝试次数: {attempt}, 执行时间: {execution_time:.2f}s")
                return result
                
            except Exception as e:
                last_exception = e
                
                # 检查是否应该停止重试
                if any(isinstance(e, stop_ex) for stop_ex in config.stop_on):
                    logger.info(f"遇到停止异常，停止重试: {func_name}, 异常: {type(e).__name__}")
                    break
                
                # 检查是否应该重试
                if not any(isinstance(e, retry_ex) for retry_ex in config.retry_on):
                    logger.info(f"异常不在重试列表中，停止重试: {func_name}, 异常: {type(e).__name__}")
                    break
                
                # 如果还有重试机会，计算延迟时间
                if attempt < config.max_attempts:
                    delay = self._calculate_delay(config, attempt)
                    logger.warning(f"重试失败: {func_name}, 尝试次数: {attempt}/{config.max_attempts}, "
                                 f"异常: {type(e).__name__}, 延迟: {delay:.2f}s")
                    time.sleep(delay)
                else:
                    logger.error(f"重试最终失败: {func_name}, 最大尝试次数: {config.max_attempts}, "
                               f"最终异常: {type(e).__name__}")
        
        # 记录最终失败
        with self._lock:
            stats = self.retry_stats[func_name]
            stats['total_failures'] += 1
            stats['last_failure'] = datetime.now()
        
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError(f"重试失败，未知错误: {func_name}")
    
    def _calculate_delay(self, config: RetryConfig, attempt: int) -> float:
        """计算延迟时间"""
        if config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * attempt
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        elif config.strategy == RetryStrategy.RANDOM_JITTER:
            delay = config.base_delay + random.uniform(0, config.base_delay)
        else:
            delay = config.base_delay
        
        # 限制最大延迟
        delay = min(delay, config.max_delay)
        
        # 添加随机抖动
        if config.jitter and config.strategy != RetryStrategy.RANDOM_JITTER:
            jitter = delay * 0.1 * random.uniform(-1, 1)
            delay += jitter
        
        return max(0, delay)
    
    def get_retry_statistics(self) -> Dict[str, Dict[str, Any]]:
        """获取重试统计信息"""
        with self._lock:
            return dict(self.retry_stats)

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.call_count = 0
        self.call_history = deque(maxlen=100)
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数调用"""
        with self._lock:
            self.call_count += 1
            
            # 检查熔断器状态
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info(f"熔断器 {self.name} 进入半开状态")
                else:
                    self._record_call('blocked')
                    raise RuntimeError(f"熔断器 {self.name} 处于开启状态，拒绝请求")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            with self._lock:
                self._on_success(execution_time)
            
            return result
            
        except self.config.expected_exception as e:
            execution_time = time.time() - start_time
            
            with self._lock:
                self._on_failure(execution_time, e)
            
            raise
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout
    
    def _on_success(self, execution_time: float):
        """处理成功调用"""
        self.success_count += 1
        self._record_call('success', execution_time)
        
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info(f"熔断器 {self.name} 恢复到关闭状态")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0  # 重置失败计数
    
    def _on_failure(self, execution_time: float, exception: Exception):
        """处理失败调用"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self._record_call('failure', execution_time, str(exception))
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning(f"熔断器 {self.name} 从半开状态回到开启状态")
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"熔断器 {self.name} 开启，失败次数: {self.failure_count}")
    
    def _record_call(self, result: str, execution_time: float = 0, error: str = None):
        """记录调用历史"""
        self.call_history.append({
            'timestamp': datetime.now(),
            'result': result,
            'execution_time': execution_time,
            'error': error,
            'state': self.state.value
        })
    
    def get_state(self) -> Dict[str, Any]:
        """获取熔断器状态"""
        with self._lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'call_count': self.call_count,
                'last_failure_time': self.last_failure_time,
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout': self.config.recovery_timeout,
                    'success_threshold': self.config.success_threshold
                }
            }
    
    def reset(self):
        """重置熔断器"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            logger.info(f"熔断器 {self.name} 已重置")

class FallbackManager:
    """降级管理器"""
    
    def __init__(self):
        self.cache = {}
        self.fallback_stats = defaultdict(lambda: {
            'total_calls': 0,
            'fallback_calls': 0,
            'success_calls': 0,
            'last_fallback': None
        })
        self._lock = threading.Lock()
    
    def execute_with_fallback(self, func: Callable, config: FallbackConfig, *args, **kwargs) -> Any:
        """执行带降级的函数"""
        func_name = f"{func.__module__}.{func.__name__}"
        
        with self._lock:
            self.fallback_stats[func_name]['total_calls'] += 1
        
        try:
            result = func(*args, **kwargs)
            
            # 缓存成功结果
            if config.cache_key:
                self._cache_result(config.cache_key, result, config.cache_ttl)
            
            with self._lock:
                self.fallback_stats[func_name]['success_calls'] += 1
            
            return result
            
        except Exception as e:
            logger.warning(f"主函数执行失败，启用降级策略: {func_name}, 异常: {type(e).__name__}")
            
            with self._lock:
                self.fallback_stats[func_name]['fallback_calls'] += 1
                self.fallback_stats[func_name]['last_fallback'] = datetime.now()
            
            return self._execute_fallback(config, func_name, e)
    
    def _execute_fallback(self, config: FallbackConfig, func_name: str, original_exception: Exception) -> Any:
        """执行降级策略"""
        try:
            if config.strategy == FallbackStrategy.RETURN_DEFAULT:
                logger.info(f"降级策略: 返回默认值 - {func_name}")
                return config.default_value
            
            elif config.strategy == FallbackStrategy.RETURN_CACHED:
                if config.cache_key and config.cache_key in self.cache:
                    cached_data = self.cache[config.cache_key]
                    if cached_data['expires_at'] > time.time():
                        logger.info(f"降级策略: 返回缓存数据 - {func_name}")
                        return cached_data['value']
                    else:
                        # 缓存过期，移除
                        del self.cache[config.cache_key]
                
                # 缓存不可用，返回默认值
                logger.info(f"降级策略: 缓存不可用，返回默认值 - {func_name}")
                return config.default_value
            
            elif config.strategy == FallbackStrategy.CALL_BACKUP:
                if config.backup_function:
                    logger.info(f"降级策略: 调用备用函数 - {func_name}")
                    return config.backup_function()
                else:
                    logger.warning(f"降级策略: 备用函数未配置，返回默认值 - {func_name}")
                    return config.default_value
            
            elif config.strategy == FallbackStrategy.RETURN_EMPTY:
                logger.info(f"降级策略: 返回空结果 - {func_name}")
                return None
            
            elif config.strategy == FallbackStrategy.RAISE_EXCEPTION:
                logger.info(f"降级策略: 重新抛出异常 - {func_name}")
                raise original_exception
            
            else:
                logger.warning(f"未知降级策略，返回默认值 - {func_name}")
                return config.default_value
                
        except Exception as fallback_exception:
            logger.error(f"降级策略执行失败: {func_name}, 异常: {type(fallback_exception).__name__}")
            raise fallback_exception
    
    def _cache_result(self, key: str, value: Any, ttl: int):
        """缓存结果"""
        expires_at = time.time() + ttl
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'cached_at': time.time()
        }
    
    def get_fallback_statistics(self) -> Dict[str, Dict[str, Any]]:
        """获取降级统计信息"""
        with self._lock:
            return dict(self.fallback_stats)
    
    def clear_cache(self):
        """清理缓存"""
        with self._lock:
            self.cache.clear()
            logger.info("降级缓存已清理")

# 全局实例
retry_manager = RetryManager()
fallback_manager = FallbackManager()
circuit_breakers = {}

def get_circuit_breaker(name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
    """获取或创建熔断器"""
    if name not in circuit_breakers:
        if config is None:
            config = CircuitBreakerConfig()
        circuit_breakers[name] = CircuitBreaker(name, config)
    return circuit_breakers[name]

# 装饰器
def retry(config: RetryConfig = None):
    """重试装饰器"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_manager.execute_with_retry(func, config, *args, **kwargs)
        return wrapper
    return decorator

def circuit_breaker(name: str = None, config: CircuitBreakerConfig = None):
    """熔断器装饰器"""
    def decorator(func: Callable) -> Callable:
        breaker_name = name or f"{func.__module__}.{func.__name__}"
        breaker = get_circuit_breaker(breaker_name, config)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator

def fallback(config: FallbackConfig = None):
    """降级装饰器"""
    if config is None:
        config = FallbackConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return fallback_manager.execute_with_fallback(func, config, *args, **kwargs)
        return wrapper
    return decorator

def resilience(retry_config: RetryConfig = None,
              circuit_config: CircuitBreakerConfig = None,
              fallback_config: FallbackConfig = None,
              circuit_name: str = None):
    """组合弹性装饰器 - 重试 + 熔断 + 降级"""
    def decorator(func: Callable) -> Callable:
        # 应用装饰器链：fallback -> circuit_breaker -> retry -> func
        decorated_func = func
        
        # 最内层：重试
        if retry_config:
            decorated_func = retry(retry_config)(decorated_func)
        
        # 中间层：熔断器
        if circuit_config:
            breaker_name = circuit_name or f"{func.__module__}.{func.__name__}"
            decorated_func = circuit_breaker(breaker_name, circuit_config)(decorated_func)
        
        # 最外层：降级
        if fallback_config:
            decorated_func = fallback(fallback_config)(decorated_func)
        
        return decorated_func
    return decorator

# 便捷配置
class PresetConfigs:
    """预设配置"""
    
    # 重试配置
    QUICK_RETRY = RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.FIXED_DELAY,
        base_delay=0.5
    )
    
    STANDARD_RETRY = RetryConfig(
        max_attempts=5,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay=1.0,
        max_delay=30.0
    )
    
    AGGRESSIVE_RETRY = RetryConfig(
        max_attempts=10,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay=0.1,
        max_delay=60.0,
        jitter=True
    )
    
    # 熔断器配置
    SENSITIVE_CIRCUIT = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30.0,
        success_threshold=2
    )
    
    STANDARD_CIRCUIT = CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60.0,
        success_threshold=3
    )
    
    TOLERANT_CIRCUIT = CircuitBreakerConfig(
        failure_threshold=10,
        recovery_timeout=120.0,
        success_threshold=5
    )
    
    # 降级配置
    DEFAULT_FALLBACK = FallbackConfig(
        strategy=FallbackStrategy.RETURN_DEFAULT,
        default_value=None
    )
    
    CACHED_FALLBACK = FallbackConfig(
        strategy=FallbackStrategy.RETURN_CACHED,
        cache_ttl=300
    )
    
    EMPTY_FALLBACK = FallbackConfig(
        strategy=FallbackStrategy.RETURN_EMPTY
    )

# 监控和管理函数
def get_resilience_status() -> Dict[str, Any]:
    """获取弹性系统状态"""
    retry_stats = retry_manager.get_retry_statistics()
    fallback_stats = fallback_manager.get_fallback_statistics()
    
    circuit_status = {}
    for name, breaker in circuit_breakers.items():
        circuit_status[name] = breaker.get_state()
    
    return {
        'retry_statistics': retry_stats,
        'fallback_statistics': fallback_stats,
        'circuit_breakers': circuit_status,
        'system_health': _calculate_system_health(retry_stats, fallback_stats, circuit_status),
        'generated_at': datetime.now().isoformat()
    }

def _calculate_system_health(retry_stats: Dict, fallback_stats: Dict, circuit_status: Dict) -> Dict[str, Any]:
    """计算系统健康度"""
    health_score = 100
    issues = []
    
    # 检查重试统计
    for func_name, stats in retry_stats.items():
        if stats['total_attempts'] > 0:
            failure_rate = stats['total_failures'] / stats['total_attempts']
            if failure_rate > 0.5:
                health_score -= 10
                issues.append(f"函数 {func_name} 失败率过高: {failure_rate:.1%}")
    
    # 检查降级统计
    for func_name, stats in fallback_stats.items():
        if stats['total_calls'] > 0:
            fallback_rate = stats['fallback_calls'] / stats['total_calls']
            if fallback_rate > 0.3:
                health_score -= 15
                issues.append(f"函数 {func_name} 降级率过高: {fallback_rate:.1%}")
    
    # 检查熔断器状态
    open_circuits = [name for name, status in circuit_status.items() if status['state'] == 'open']
    if open_circuits:
        health_score -= len(open_circuits) * 20
        issues.extend([f"熔断器 {name} 处于开启状态" for name in open_circuits])
    
    health_score = max(0, health_score)
    
    if health_score >= 90:
        health_level = 'excellent'
    elif health_score >= 75:
        health_level = 'good'
    elif health_score >= 50:
        health_level = 'warning'
    else:
        health_level = 'critical'
    
    return {
        'score': health_score,
        'level': health_level,
        'issues': issues,
        'open_circuits': len(open_circuits),
        'total_circuits': len(circuit_status)
    }

def reset_all_circuit_breakers():
    """重置所有熔断器"""
    for breaker in circuit_breakers.values():
        breaker.reset()
    logger.info(f"已重置 {len(circuit_breakers)} 个熔断器")

def cleanup_old_statistics(days: int = 7):
    """清理旧的统计数据"""
    # 清理降级缓存
    fallback_manager.clear_cache()
    
    # 清理熔断器历史
    for breaker in circuit_breakers.values():
        cutoff = datetime.now() - timedelta(days=days)
        breaker.call_history = deque([
            call for call in breaker.call_history
            if call['timestamp'] > cutoff
        ], maxlen=100)
    
    logger.info(f"已清理 {days} 天前的统计数据")