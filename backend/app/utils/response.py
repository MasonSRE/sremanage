"""
标准API响应格式工具
统一后端API响应格式，提高前后端协作效率
"""
from flask import jsonify
import logging
import traceback
from functools import wraps

logger = logging.getLogger(__name__)

class APIResponse:
    """标准API响应格式类"""
    
    @staticmethod
    def success(data=None, message="操作成功", code=200, meta=None):
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: HTTP状态码
            meta: 元数据（分页信息等）
        """
        response = {
            "success": True,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": APIResponse._get_timestamp()
        }
        
        if meta:
            response["meta"] = meta
            
        return jsonify(response), code
    
    @staticmethod
    def error(message="操作失败", code=400, error_code=None, details=None):
        """
        错误响应
        
        Args:
            message: 错误消息
            code: HTTP状态码
            error_code: 业务错误码
            details: 详细错误信息
        """
        response = {
            "success": False,
            "code": code,
            "message": message,
            "data": None,
            "timestamp": APIResponse._get_timestamp()
        }
        
        if error_code:
            response["error_code"] = error_code
            
        if details:
            response["details"] = details
            
        return jsonify(response), code
    
    @staticmethod
    def validation_error(errors, message="参数验证失败"):
        """
        参数验证错误响应
        
        Args:
            errors: 验证错误列表
            message: 错误消息
        """
        return APIResponse.error(
            message=message,
            code=422,
            error_code="VALIDATION_ERROR",
            details=errors
        )
    
    @staticmethod
    def not_found(message="资源不存在", resource=None):
        """
        资源不存在响应
        
        Args:
            message: 错误消息
            resource: 资源类型
        """
        details = {"resource": resource} if resource else None
        return APIResponse.error(
            message=message,
            code=404,
            error_code="NOT_FOUND",
            details=details
        )
    
    @staticmethod
    def unauthorized(message="未授权访问"):
        """
        未授权响应
        
        Args:
            message: 错误消息
        """
        return APIResponse.error(
            message=message,
            code=401,
            error_code="UNAUTHORIZED"
        )
    
    @staticmethod  
    def forbidden(message="禁止访问"):
        """
        禁止访问响应
        
        Args:
            message: 错误消息
        """
        return APIResponse.error(
            message=message,
            code=403,
            error_code="FORBIDDEN"
        )
    
    @staticmethod
    def server_error(message="服务器内部错误", details=None):
        """
        服务器错误响应
        
        Args:
            message: 错误消息
            details: 错误详情（生产环境中应该隐藏）
        """
        return APIResponse.error(
            message=message,
            code=500,
            error_code="INTERNAL_ERROR",
            details=details
        )
    
    @staticmethod
    def paginated(data, total, page=1, page_size=20, message="获取成功"):
        """
        分页响应
        
        Args:
            data: 数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页大小
            message: 响应消息
        """
        total_pages = (total + page_size - 1) // page_size
        
        meta = {
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        return APIResponse.success(data=data, message=message, meta=meta)
    
    @staticmethod
    def _get_timestamp():
        """获取当前时间戳"""
        import time
        return int(time.time() * 1000)  # 毫秒时间戳

def api_response(func):
    """
    API响应装饰器 - 自动处理异常并返回标准格式
    
    使用方式:
    @api_response
    def my_api():
        return {"result": "success"}  # 自动包装为标准格式
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # 如果函数返回的是tuple (可能包含状态码)
            if isinstance(result, tuple):
                if len(result) == 2:
                    # 检查是否是Flask响应对象 (来自APIResponse.success/error)
                    from flask import Response
                    if isinstance(result[0], Response) and isinstance(result[1], int):
                        # 直接返回Flask响应
                        return result
                    elif isinstance(result[1], int):
                        # (data, status_code) 格式
                        data, status_code = result
                        return APIResponse.success(data=data, code=status_code)
                # 直接返回tuple（可能是Flask响应）
                return result
            
            # 如果函数返回的是dict
            elif isinstance(result, dict):
                # 检查是否已经是标准格式
                if "success" in result and "code" in result:
                    return jsonify(result)
                else:
                    # 包装为标准格式
                    return APIResponse.success(data=result)
            
            # 其他类型直接包装
            else:
                return APIResponse.success(data=result)
                
        except ValueError as e:
            logger.warning(f"参数验证错误: {e}")
            return APIResponse.validation_error([str(e)])
            
        except FileNotFoundError as e:
            logger.warning(f"资源不存在: {e}")
            return APIResponse.not_found(str(e))
            
        except PermissionError as e:
            logger.warning(f"权限错误: {e}")
            return APIResponse.forbidden(str(e))
            
        except Exception as e:
            logger.error(f"API异常: {e}")
            logger.error(traceback.format_exc())
            
            # 生产环境隐藏详细错误信息
            import os
            if os.environ.get('FLASK_ENV') == 'development':
                details = {
                    "error": str(e),
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            else:
                details = None
                
            return APIResponse.server_error(details=details)
    
    return wrapper

class ErrorCodes:
    """错误码常量"""
    # 通用错误
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 参数验证错误
    NOT_FOUND = "NOT_FOUND"  # 资源不存在
    UNAUTHORIZED = "UNAUTHORIZED"  # 未授权
    FORBIDDEN = "FORBIDDEN"  # 禁止访问
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 服务器内部错误
    
    # 业务错误
    JENKINS_CONNECTION_FAILED = "JENKINS_CONNECTION_FAILED"  # Jenkins连接失败
    HOST_CONNECTION_FAILED = "HOST_CONNECTION_FAILED"  # 主机连接失败
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"  # 认证失败
    BUILD_TRIGGER_FAILED = "BUILD_TRIGGER_FAILED"  # 构建触发失败
    
    # 数据错误
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"  # 资源重复
    RESOURCE_IN_USE = "RESOURCE_IN_USE"  # 资源正在使用
    DATA_INTEGRITY_ERROR = "DATA_INTEGRITY_ERROR"  # 数据完整性错误

# 便捷函数
def success_response(data=None, message="操作成功", **kwargs):
    """便捷的成功响应函数"""
    return APIResponse.success(data, message, **kwargs)

def error_response(message="操作失败", **kwargs):
    """便捷的错误响应函数"""
    return APIResponse.error(message, **kwargs)