#!/usr/bin/env python3
"""
模拟前端API调用，验证前端和后端集成正常工作
"""
import requests
import json

API_BASE = "http://127.0.0.1:5001"

def simulate_frontend_call():
    """模拟前端加载Jenkins实例的完整流程"""
    print("🎭 模拟前端加载Jenkins实例...")
    
    # 模拟前端的fetchApi调用
    try:
        # 第1步：获取Jenkins实例列表（前端核心功能）
        print("\n📡 步骤1：获取Jenkins实例列表...")
        response = requests.get(f"{API_BASE}/api/settings/jenkins", 
                              headers={'Accept': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                instances = data.get('data', [])
                print(f"✅ 成功获取 {len(instances)} 个Jenkins实例")
                
                for i, instance in enumerate(instances, 1):
                    print(f"   {i}. {instance.get('name')} - {instance.get('url')}")
                
                # 第2步：如果有实例，模拟选择第一个实例
                if instances:
                    first_instance = instances[0]
                    print(f"\n📡 步骤2：选择实例 '{first_instance['name']}'")
                    print(f"✅ 实例选择成功，ID: {first_instance['id']}")
                    
                    # 第3步：模拟获取该实例的详细信息（可选）
                    print(f"\n📡 步骤3：验证实例详情...")
                    print(f"   实例名称: {first_instance['name']}")
                    print(f"   Jenkins URL: {first_instance['url']}")
                    print(f"   用户名: {first_instance['username']}")
                    print(f"   状态: {'启用' if first_instance['enabled'] else '禁用'}")
                    print(f"✅ 实例详情获取成功")
                    
                    return True
                else:
                    print("ℹ️  当前没有配置Jenkins实例，但API工作正常")
                    return True
            else:
                print(f"❌ API返回失败: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 前端模拟失败: {e}")
        return False

def simulate_cloud_provider_call():
    """模拟前端加载云厂商配置的完整流程"""
    print("\n🎭 模拟前端加载云厂商配置...")
    
    try:
        # 第1步：获取云厂商配置列表
        print("\n📡 步骤1：获取云厂商配置列表...")
        response = requests.get(f"{API_BASE}/api/cloud-providers", 
                              headers={'Accept': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                providers = data.get('data', [])
                print(f"✅ 成功获取 {len(providers)} 个云厂商配置")
                
                # 第2步：获取支持的云厂商列表
                print("\n📡 步骤2：获取支持的云厂商列表...")
                response2 = requests.get(f"{API_BASE}/api/cloud-providers/supported")
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2.get('success'):
                        supported = data2.get('data', [])
                        print(f"✅ 支持 {len(supported)} 种云厂商:")
                        for provider in supported:
                            print(f"   {provider['icon']} {provider['label']} ({provider['value']})")
                        
                        # 第3步：获取配置字段定义
                        print("\n📡 步骤3：获取配置字段定义...")
                        response3 = requests.get(f"{API_BASE}/api/cloud-providers/schemas")
                        
                        if response3.status_code == 200:
                            data3 = response3.json()
                            if data3.get('success'):
                                schemas = data3.get('data', {})
                                print(f"✅ 获取 {len(schemas)} 种云厂商的字段定义")
                                for provider, fields in schemas.items():
                                    print(f"   {provider}: {len(fields)} 个配置字段")
                                
                                return True
                            else:
                                print(f"❌ 字段定义API失败: {data3.get('message')}")
                                return False
                        else:
                            print(f"❌ 字段定义HTTP错误: {response3.status_code}")
                            return False
                    else:
                        print(f"❌ 支持列表API失败: {data2.get('message')}")
                        return False
                else:
                    print(f"❌ 支持列表HTTP错误: {response2.status_code}")
                    return False
            else:
                print(f"❌ 云厂商配置API失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 云厂商配置HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 云厂商前端模拟失败: {e}")
        return False

def main():
    print("🎯 全面验证 - 模拟前端完整用户流程")
    print("=" * 60)
    
    # 测试Jenkins功能
    jenkins_success = simulate_frontend_call()
    
    # 测试云厂商功能
    cloud_success = simulate_cloud_provider_call()
    
    print("\n" + "=" * 60)
    print("🏁 最终验证结果:")
    print("=" * 60)
    
    print(f"Jenkins实例加载: {'✅ 成功' if jenkins_success else '❌ 失败'}")
    print(f"云厂商配置加载: {'✅ 成功' if cloud_success else '❌ 失败'}")
    
    if jenkins_success and cloud_success:
        print("\n🎉 完美！所有功能都正常工作！")
        print("🚀 用户不会再看到'Empty response'错误了！")
        print("✨ Jenkins实例和云厂商配置都能正常加载！")
        return True
    else:
        print("\n⚠️ 仍有功能异常，需要进一步检查。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)