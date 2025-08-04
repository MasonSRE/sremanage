#!/usr/bin/env python3
"""
全面测试Jenkins和云厂商API，验证"Empty response"问题已解决
"""
import requests
import json
import time

API_BASE = "http://127.0.0.1:5001"

def test_api_endpoint(endpoint, description):
    """测试单个API端点"""
    print(f"\n🧪 测试: {description}")
    print(f"📡 端点: {endpoint}")
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        print(f"📊 HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ 响应格式: 有效JSON")
                print(f"📦 数据结构: {type(data)}")
                
                if 'success' in data:
                    print(f"🎯 Success字段: {data['success']}")
                    if data['success']:
                        print(f"📋 数据条目: {len(data.get('data', []))} 项")
                        print(f"🎉 测试结果: 通过 ✅")
                        return True
                    else:
                        print(f"❌ API返回失败: {data.get('message', '未知错误')}")
                        return False
                else:
                    print(f"⚠️  响应缺少success字段")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"🔤 原始响应: {response.text[:200]}...")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"🔤 错误内容: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败: 无法连接到 {API_BASE}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def main():
    print("🚀 开始全面测试 - 验证'Empty response'问题已解决")
    print("=" * 60)
    
    # 等待服务启动
    print("\n⏳ 等待服务启动...")
    time.sleep(2)
    
    # 测试用例
    test_cases = [
        ("/api/settings/jenkins", "Jenkins实例配置API"),
        ("/api/cloud-providers", "云厂商配置API"),
        ("/api/cloud-providers/schemas", "云厂商字段定义API"),
        ("/api/cloud-providers/supported", "支持的云厂商列表API"),
    ]
    
    results = []
    
    for endpoint, description in test_cases:
        result = test_api_endpoint(endpoint, description)
        results.append((description, result))
        time.sleep(1)  # 避免请求过快
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for description, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{description}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！'Empty response'问题已完全解决！")
        print("✨ 用户现在可以正常加载Jenkins实例和云厂商配置了。")
    else:
        print(f"\n⚠️  仍有 {failed} 个测试失败，需要进一步修复。")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)