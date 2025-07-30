#!/usr/bin/env python3
"""
启动后端服务的脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    # 创建应用
    app = create_app('development')
    
    print("🚀 启动SREManage后端服务...")
    print("📡 API地址: http://localhost:5001")
    print("🔗 主机列表测试: http://localhost:5001/api/hosts-all-test")
    print("⚡ 支持热重载和调试模式")
    print("-" * 50)
    
    # 启动服务器
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )