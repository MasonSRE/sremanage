#!/usr/bin/env python3
"""
测试云厂商配置API端点，用于验证修复效果
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# 禁用所有中间件，纯粹测试API响应
app.config['TESTING'] = True

@app.route('/api/cloud-providers', methods=['GET'])
def cloud_providers():
    """云厂商配置API - 测试版本"""
    print(f"收到云厂商配置请求")
    
    # 模拟成功的响应（表存在且有数据的情况）
    result = {
        'success': True,
        'data': [
            {
                'id': 1,
                'name': '测试阿里云配置',
                'provider': 'aliyun',
                'config': {
                    'access_key_id': 'LTAI****',
                    'access_key_secret': '****'
                },
                'region': 'cn-hangzhou',
                'enabled': True,
                'created_at': '2025-01-01 00:00:00',
                'updated_at': '2025-01-01 00:00:00'
            }
        ]
    }
    
    print(f"返回云厂商配置数据: {result}")
    return jsonify(result)

@app.route('/api/cloud-providers/schemas', methods=['GET'])
def cloud_provider_schemas():
    """云厂商配置字段定义API - 测试版本"""
    print(f"收到云厂商字段定义请求")
    
    result = {
        'success': True,
        'data': {
            'aliyun': [
                {
                    'field_name': 'access_key_id',
                    'field_type': 'text',
                    'field_label': 'Access Key ID',
                    'is_required': True,
                    'placeholder': '请输入阿里云Access Key ID',
                    'help_text': '在阿里云控制台的访问控制RAM中创建'
                },
                {
                    'field_name': 'access_key_secret',
                    'field_type': 'password',
                    'field_label': 'Access Key Secret',
                    'is_required': True,
                    'placeholder': '请输入阿里云Access Key Secret',
                    'help_text': '对应Access Key ID的密钥'
                }
            ]
        }
    }
    
    print(f"返回云厂商字段定义数据: {result}")
    return jsonify(result)

@app.route('/api/cloud-providers/supported', methods=['GET'])
def supported_providers():
    """支持的云厂商列表API - 测试版本"""
    print(f"收到支持的云厂商列表请求")
    
    result = {
        'success': True,
        'data': [
            {'value': 'aliyun', 'label': '阿里云', 'icon': '🌐'},
            {'value': 'aws', 'label': 'Amazon Web Services', 'icon': '☁️'},
            {'value': 'tencent', 'label': '腾讯云', 'icon': '🐧'},
            {'value': 'huawei', 'label': '华为云', 'icon': '🌸'},
            {'value': 'google', 'label': 'Google Cloud', 'icon': '🔍'},
            {'value': 'azure', 'label': 'Microsoft Azure', 'icon': '🪟'}
        ]
    }
    
    print(f"返回支持的云厂商列表: {result}")
    return jsonify(result)

@app.route('/api/test/empty-cloud-response', methods=['GET'])
def test_empty_cloud_response():
    """测试云厂商空响应的情况"""
    print("测试云厂商空响应")
    # 这将返回一个空响应，模拟原始错误
    return "", 200

@app.route('/api/test/cloud-error-response', methods=['GET'])
def test_cloud_error_response():
    """测试云厂商错误响应的情况"""
    print("测试云厂商错误响应")
    return jsonify({
        'success': False,
        'message': '模拟的云厂商数据库连接失败',
        'data': []
    }), 500

if __name__ == '__main__':
    print("启动云厂商配置API测试服务器...")
    print("测试端点:")
    print("  - GET /api/cloud-providers (正常响应)")
    print("  - GET /api/cloud-providers/schemas (字段定义)")
    print("  - GET /api/cloud-providers/supported (支持的厂商)")
    print("  - GET /api/test/empty-cloud-response (空响应)")
    print("  - GET /api/test/cloud-error-response (错误响应)")
    app.run(host='127.0.0.1', port=5004, debug=False)