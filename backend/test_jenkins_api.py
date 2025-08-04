#!/usr/bin/env python3
"""
测试Jenkins API端点，用于验证修复效果
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# 禁用所有中间件，纯粹测试API响应
app.config['TESTING'] = True

@app.route('/api/settings/jenkins', methods=['GET', 'POST'])
def jenkins_settings():
    """Jenkins设置API - 测试版本"""
    print(f"收到请求: {request.method} /api/settings/jenkins")
    
    if request.method == 'GET':
        # 模拟成功的响应（表存在且有数据的情况）
        result = {
            'success': True,
            'data': [
                {
                    'id': 1,
                    'name': '测试Jenkins实例',
                    'url': 'http://localhost:8080',
                    'username': 'admin',
                    'enabled': True
                }
            ]
        }
        
        print(f"返回数据: {result}")
        return jsonify(result)
    
    # POST 请求处理
    data = request.get_json()
    return jsonify({'success': True, 'message': 'Jenkins实例添加成功'})

@app.route('/api/test/empty-response', methods=['GET'])
def test_empty_response():
    """测试空响应的情况"""
    print("测试空响应")
    # 这将返回一个空响应，模拟原始错误
    return "", 200

@app.route('/api/test/error-response', methods=['GET'])
def test_error_response():
    """测试错误响应的情况"""
    print("测试错误响应")
    return jsonify({
        'success': False,
        'message': '模拟的数据库连接失败',
        'data': []
    }), 500

@app.route('/api/test/json-parse-error', methods=['GET'])
def test_json_parse_error():
    """测试无效JSON响应"""
    print("测试无效JSON响应")
    # 返回无效的JSON，这应该会导致前端出现JSON解析错误
    return "这不是有效的JSON", 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    print("启动Jenkins API测试服务器...")
    print("测试端点:")
    print("  - GET /api/settings/jenkins (正常响应)")
    print("  - GET /api/test/empty-response (空响应)")
    print("  - GET /api/test/error-response (错误响应)")
    print("  - GET /api/test/json-parse-error (无效JSON)")
    app.run(host='127.0.0.1', port=5003, debug=False)