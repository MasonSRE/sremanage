#!/usr/bin/env python3
"""
Jenkins API修复验证测试脚本
测试修复后的Jenkins API端点是否正常工作
"""

import requests
import json
import time

def test_api_endpoint(url, method='GET', data=None, expected_status=200):
    """测试API端点"""
    try:
        headers = {'Content-Type': 'application/json'}
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            print(f"❌ 不支持的HTTP方法: {method}")
            return False
            
        print(f"🔍 {method} {url}")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == expected_status:
            try:
                json_data = response.json()
                print(f"   ✅ JSON响应正常")
                print(f"   响应键: {list(json_data.keys())}")
                return True
            except json.JSONDecodeError:
                print(f"   ❌ 响应不是有效的JSON")
                print(f"   响应内容: {response.text[:200]}...")
                return False
        else:
            print(f"   ❌ 状态码不匹配，期望 {expected_status}，实际 {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 连接失败 - 请确保后端服务正在运行")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ 请求超时")
        return False
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return False

def main():
    print("🎯 Jenkins API修复验证测试")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5001"
    
    # 测试用例
    test_cases = [
        # Jenkins设置API
        {
            "name": "Jenkins设置列表",
            "url": f"{base_url}/api/settings/jenkins",
            "expected_status": 200
        },
        
        # Jenkins操作API
        {
            "name": "Jenkins任务列表",
            "url": f"{base_url}/api/ops/jenkins/jobs/1",
            "expected_status": 200
        },
        
        {
            "name": "Jenkins状态",
            "url": f"{base_url}/api/ops/jenkins/status/1", 
            "expected_status": 200
        },
        
        {
            "name": "Jenkins队列",
            "url": f"{base_url}/api/ops/jenkins/queue/1",
            "expected_status": 200
        },
        
        {
            "name": "Jenkins视图列表",
            "url": f"{base_url}/api/ops/jenkins/views/1",
            "expected_status": 200
        },
        
        # 404测试
        {
            "name": "404错误处理",
            "url": f"{base_url}/api/nonexistent",
            "expected_status": 404
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}/{total_count}: {test_case['name']}")
        
        if test_api_endpoint(
            test_case['url'], 
            test_case.get('method', 'GET'),
            test_case.get('data'),
            test_case['expected_status']
        ):
            success_count += 1
            print(f"   ✅ 测试通过")
        else:
            print(f"   ❌ 测试失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！Jenkins API修复成功！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查具体问题")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)