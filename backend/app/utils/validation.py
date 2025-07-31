"""
输入验证和参数校验工具
提供强大的数据验证功能，确保API输入的安全性和有效性
"""
import re
import ipaddress
from functools import wraps
from flask import request
from app.utils.response import APIResponse

class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, errors):
        self.errors = errors if isinstance(errors, list) else [errors]
        super().__init__("Validation failed")

class Validator:
    """数据验证器基类"""
    
    def __init__(self, required=True, allow_none=False):
        self.required = required
        self.allow_none = allow_none
        self.errors = []
    
    def validate(self, value, field_name="field"):
        """验证数据"""
        self.errors = []
        
        # 检查必填项
        if value is None or value == "":
            if self.required:
                self.errors.append(f"{field_name}是必填项")
                return False
            elif self.allow_none:
                return True
            else:
                self.errors.append(f"{field_name}不能为空")
                return False
        
        # 执行具体验证
        return self._validate_value(value, field_name)
    
    def _validate_value(self, value, field_name):
        """子类实现具体验证逻辑"""
        return True
    
    def get_errors(self):
        """获取验证错误"""
        return self.errors

class StringValidator(Validator):
    """字符串验证器"""
    
    def __init__(self, min_length=None, max_length=None, pattern=None, 
                 strip=True, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.strip = strip
    
    def _validate_value(self, value, field_name):
        # 转换为字符串并去空格
        if not isinstance(value, str):
            value = str(value)
        
        if self.strip:
            value = value.strip()
        
        # 长度验证
        if self.min_length is not None and len(value) < self.min_length:
            self.errors.append(f"{field_name}长度不能少于{self.min_length}个字符")
            return False
        
        if self.max_length is not None and len(value) > self.max_length:
            self.errors.append(f"{field_name}长度不能超过{self.max_length}个字符")
            return False
        
        # 正则验证
        if self.pattern and not self.pattern.match(value):
            self.errors.append(f"{field_name}格式不正确")
            return False
        
        return True

class IntegerValidator(Validator):
    """整数验证器"""
    
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
    
    def _validate_value(self, value, field_name):
        # 转换为整数
        try:
            if isinstance(value, str):
                value = int(value)
            elif not isinstance(value, int):
                raise ValueError()
        except ValueError:
            self.errors.append(f"{field_name}必须是整数")
            return False
        
        # 范围验证
        if self.min_value is not None and value < self.min_value:
            self.errors.append(f"{field_name}不能小于{self.min_value}")
            return False
        
        if self.max_value is not None and value > self.max_value:
            self.errors.append(f"{field_name}不能大于{self.max_value}")
            return False
        
        return True

class EmailValidator(Validator):
    """邮箱验证器"""
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def _validate_value(self, value, field_name):
        if not isinstance(value, str):
            value = str(value)
        
        if not self.EMAIL_PATTERN.match(value.strip()):
            self.errors.append(f"{field_name}邮箱格式不正确")
            return False
        
        return True

class URLValidator(Validator):
    """URL验证器"""
    
    URL_PATTERN = re.compile(
        r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.]*))?(?:#(?:[\w.]*))?)?$'
    )
    
    def _validate_value(self, value, field_name):
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        if not self.URL_PATTERN.match(value):
            self.errors.append(f"{field_name}URL格式不正确")
            return False
        
        return True

class IPValidator(Validator):
    """IP地址验证器"""
    
    def __init__(self, allow_private=True, **kwargs):
        super().__init__(**kwargs)
        self.allow_private = allow_private
    
    def _validate_value(self, value, field_name):
        if not isinstance(value, str):
            value = str(value)
        
        try:
            ip = ipaddress.ip_address(value.strip())
            
            if not self.allow_private and ip.is_private:
                self.errors.append(f"{field_name}不能使用私有IP地址")
                return False
                
        except ValueError:
            self.errors.append(f"{field_name}IP地址格式不正确")
            return False
        
        return True

class ChoiceValidator(Validator):
    """选择验证器"""
    
    def __init__(self, choices, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices
    
    def _validate_value(self, value, field_name):
        if value not in self.choices:
            self.errors.append(f"{field_name}必须是以下值之一: {', '.join(map(str, self.choices))}")
            return False
        
        return True

class DictValidator(Validator):
    """字典验证器"""
    
    def __init__(self, schema, **kwargs):
        super().__init__(**kwargs)
        self.schema = schema
    
    def _validate_value(self, value, field_name):
        if not isinstance(value, dict):
            self.errors.append(f"{field_name}必须是对象类型")
            return False
        
        # 验证字典中的每个字段
        for key, validator in self.schema.items():
            field_value = value.get(key)
            sub_field_name = f"{field_name}.{key}"
            
            if not validator.validate(field_value, sub_field_name):
                self.errors.extend(validator.get_errors())
        
        return len(self.errors) == 0

class ListValidator(Validator):
    """列表验证器"""
    
    def __init__(self, item_validator, min_length=None, max_length=None, **kwargs):
        super().__init__(**kwargs)
        self.item_validator = item_validator
        self.min_length = min_length
        self.max_length = max_length
    
    def _validate_value(self, value, field_name):
        if not isinstance(value, list):
            self.errors.append(f"{field_name}必须是数组类型")
            return False
        
        # 长度验证
        if self.min_length is not None and len(value) < self.min_length:
            self.errors.append(f"{field_name}至少需要{self.min_length}个元素")
            return False
        
        if self.max_length is not None and len(value) > self.max_length:
            self.errors.append(f"{field_name}最多只能有{self.max_length}个元素")
            return False
        
        # 验证每个元素
        for i, item in enumerate(value):
            item_field_name = f"{field_name}[{i}]"
            if not self.item_validator.validate(item, item_field_name):
                self.errors.extend(self.item_validator.get_errors())
        
        return len(self.errors) == 0

def validate_json_schema(schema):
    """
    JSON Schema验证装饰器
    
    使用方式:
    @validate_json_schema({
        'name': StringValidator(min_length=1, max_length=50),
        'email': EmailValidator(),
        'age': IntegerValidator(min_value=0, max_value=120, required=False)
    })
    def my_api():
        data = request.get_json()
        # data已经过验证
        return {"success": True}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                if data is None:
                    return APIResponse.validation_error(["请求体必须是有效的JSON"])
                
                # 验证数据
                validator = DictValidator(schema)
                if not validator.validate(data, "data"):
                    return APIResponse.validation_error(validator.get_errors())
                
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.validation_error([f"数据验证失败: {str(e)}"])
        
        return wrapper
    return decorator

def validate_query_params(schema):
    """
    查询参数验证装饰器
    
    使用方式:
    @validate_query_params({
        'page': IntegerValidator(min_value=1, required=False),
        'size': IntegerValidator(min_value=1, max_value=100, required=False)
    })
    def my_api():
        # 查询参数已经过验证
        return {"success": True}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 获取查询参数
                params = request.args.to_dict()
                
                # 验证参数
                validator = DictValidator(schema)
                if not validator.validate(params, "params"):
                    return APIResponse.validation_error(validator.get_errors())
                
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.validation_error([f"参数验证失败: {str(e)}"])
        
        return wrapper
    return decorator

# 常用验证器实例
validators = {
    'jenkins_name': StringValidator(min_length=1, max_length=100, 
                                   pattern=r'^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$'),
    'jenkins_url': URLValidator(),
    'jenkins_username': StringValidator(min_length=1, max_length=50),
    'jenkins_token': StringValidator(min_length=1, max_length=200),
    'host_ip': IPValidator(),
    'host_port': IntegerValidator(min_value=1, max_value=65535),
    'host_username': StringValidator(min_length=1, max_length=50),
    'job_name': StringValidator(min_length=1, max_length=200,
                               pattern=r'^[a-zA-Z0-9_\-./]+$'),
    'instance_id': IntegerValidator(min_value=1),
    'page': IntegerValidator(min_value=1),
    'page_size': IntegerValidator(min_value=1, max_value=100)
}