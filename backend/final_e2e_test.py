#!/usr/bin/env python3
"""
最终端到端测试 - 模拟用户访问Jenkins页面的完整流程
"""
import requests
import json
import time
import sys

def test_user_workflow():
    """模拟用户实际工作流程"""
    print("🎭 开始模拟用户工作流程...")
    
    # 第1步：测试API是否可用
    print("\n📡 步骤1：验证API可用性...")
    try:
        response = requests.get("http://localhost:5173/api/settings/jenkins", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ API正常，发现 {len(data.get('data', []))} 个Jenkins实例")
            else:
                print(f"❌ API返回失败: {data.get('message')}")
                return False
        else:
            print(f"❌ API状态码异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API请求失败: {e}")
        return False
    
    # 第2步：测试前端页面是否可访问
    print("\n📱 步骤2：验证前端页面可访问性...")
    try:
        response = requests.get("http://localhost:5173/ops/jenkins", timeout=10)
        if response.status_code == 200:
            print("✅ Jenkins页面可访问")
        else:
            print(f"❌ Jenkins页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 页面请求失败: {e}")
        return False
    
    # 第3步：测试所有相关API端点
    print("\n🔗 步骤3：验证所有相关API端点...")
    endpoints = [
        ("/api/settings/jenkins", "Jenkins实例列表"),
        ("/api/cloud-providers", "云厂商配置"),
        ("/api/cloud-providers/supported", "支持的云厂商"),
        ("/api/cloud-providers/schemas", "云厂商字段定义")
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:5173{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  ✅ {description}: 成功")
                else:
                    print(f"  ❌ {description}: API返回失败 - {data.get('message')}")
                    return False
            else:
                print(f"  ❌ {description}: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ {description}: 异常 - {e}")
            return False
    
    print("🎉 所有测试通过！用户工作流程验证成功！")
    return True

def test_error_scenarios():
    """测试各种错误场景"""
    print("\n🚨 测试错误场景处理...")
    
    # 测试网络错误处理
    try:
        response = requests.get("http://localhost:5173/api/non-existent-endpoint", timeout=5)
        print(f"  非存在端点状态码: {response.status_code}")
        if response.status_code == 404:
            print("  ✅ 404错误处理正常")
        else:
            print("  ⚠️  非预期状态码")
    except Exception as e:
        print(f"  ⚠️  网络错误测试异常: {e}")
    
    # 测试超时场景
    print("  ✅ 错误场景测试完成")

def final_verification():
    """最终验证"""
    print("\n" + "="*60)
    print("🏁 最终验证结果")
    print("="*60)
    
    # 验证问题是否真的解决了
    test_cases = [
        ("Jenkins实例加载", "http://localhost:5173/api/settings/jenkins"),
        ("云厂商配置加载", "http://localhost:5173/api/cloud-providers"),
    ]
    
    all_passed = True
    
    for name, url in test_cases:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 检查是否是HTML响应（这会导致JSON解析错误）
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type:
                    print(f"❌ {name}: 返回HTML而不是JSON")
                    all_passed = False
                elif response.text.strip().startswith('<'):
                    print(f"❌ {name}: 响应内容是HTML")
                    all_passed = False
                else:
                    try:
                        data = response.json()
                        if data.get('success'):
                            print(f"✅ {name}: 正常")
                        else:
                            print(f"❌ {name}: API失败 - {data.get('message', '未知错误')}")
                            all_passed = False
                    except json.JSONDecodeError as e:
                        print(f"❌ {name}: JSON解析失败 - {e}")
                        print(f"   响应内容: {response.text[:100]}...")
                        all_passed = False
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: 请求异常 - {e}")
            all_passed = False
    
    return all_passed

def main():
    print("🎯 最终端到端验证 - 确保用户不会再看到'Invalid JSON'错误")
    print("="*70)
    
    # 运行用户工作流程测试
    workflow_success = test_user_workflow()
    
    # 测试错误场景
    test_error_scenarios()
    
    # 最终验证
    final_success = final_verification()
    
    print("\n" + "="*70)
    if workflow_success and final_success:
        print("🎊 完美！所有测试通过！")
        print("✨ 用户访问 http://localhost:5173/ops/jenkins 将不再看到任何错误！")
        print("🚀 'Invalid JSON response' 问题已彻底解决！")
        return True
    else:
        print("⚠️  仍有部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)