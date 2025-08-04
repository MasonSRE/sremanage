#!/usr/bin/env python3
"""
全面的API测试和验证脚本
用于验证前端-后端集成是否正常工作
"""
import requests
import json
import time
import subprocess
import sys
from urllib.parse import urljoin

FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:5001"

class APITester:
    def __init__(self):
        self.results = []
        self.errors = []
    
    def test_backend_direct(self):
        """测试后端直接访问"""
        print("\n🔍 测试后端直接访问...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/api/settings/jenkins", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 后端直接访问成功: {len(data.get('data', []))} 个实例")
                self.results.append("后端直接访问: 成功")
                return True
            else:
                print(f"❌ 后端直接访问失败: HTTP {response.status_code}")
                self.errors.append(f"后端直接访问失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 后端直接访问异常: {e}")
            self.errors.append(f"后端直接访问异常: {e}")
            return False
    
    def test_frontend_proxy(self):
        """测试前端代理"""
        print("\n🔍 测试前端代理...")
        
        try:
            response = requests.get(f"{FRONTEND_URL}/api/settings/jenkins", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 前端代理成功: {len(data.get('data', []))} 个实例")
                self.results.append("前端代理: 成功")
                return True
            else:
                print(f"❌ 前端代理失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")
                self.errors.append(f"前端代理失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 前端代理异常: {e}")
            self.errors.append(f"前端代理异常: {e}")
            return False
    
    def test_html_vs_json_responses(self):
        """测试各种响应类型"""
        print("\n🔍 测试响应类型...")
        
        test_endpoints = [
            "/api/settings/jenkins",
            "/api/cloud-providers", 
            "/api/cloud-providers/supported",
            "/api/invalid-endpoint"  # 这个应该返回错误
        ]
        
        for endpoint in test_endpoints:
            try:
                print(f"  测试端点: {endpoint}")
                response = requests.get(f"{FRONTEND_URL}{endpoint}", 
                                      headers={'Accept': 'application/json'}, 
                                      timeout=5)
                
                content_type = response.headers.get('content-type', '')
                is_json = 'application/json' in content_type
                
                print(f"    状态码: {response.status_code}")
                print(f"    Content-Type: {content_type}")
                print(f"    是否JSON: {is_json}")
                
                if response.text.strip().startswith('<'):
                    print(f"    ⚠️  返回了HTML响应!")
                    self.errors.append(f"{endpoint}: 返回HTML而不是JSON")
                elif is_json or response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"    ✅ 有效JSON响应")
                        self.results.append(f"{endpoint}: JSON响应正常")
                    except:
                        print(f"    ❌ JSON解析失败")
                        self.errors.append(f"{endpoint}: JSON解析失败")
                
            except Exception as e:
                print(f"    ❌ 请求异常: {e}")
                self.errors.append(f"{endpoint}: 请求异常 - {e}")
    
    def test_authentication_scenarios(self):
        """测试认证场景"""
        print("\n🔍 测试认证场景...")
        
        # 测试无认证
        try:
            response = requests.get(f"{FRONTEND_URL}/api/settings/jenkins")
            print(f"无认证请求: {response.status_code}")
            if response.text.strip().startswith('<'):
                print("⚠️  无认证返回HTML页面")
                self.errors.append("无认证时返回HTML页面而不是JSON错误")
            else:
                print("✅ 无认证返回JSON响应")
                self.results.append("无认证: JSON响应")
        except Exception as e:
            print(f"无认证请求异常: {e}")
        
        # 测试无效认证
        try:
            response = requests.get(f"{FRONTEND_URL}/api/settings/jenkins",
                                  headers={'Authorization': 'Bearer invalid-token'})
            print(f"无效认证请求: {response.status_code}")
            if response.text.strip().startswith('<'):
                print("⚠️  无效认证返回HTML页面")
                self.errors.append("无效认证时返回HTML页面而不是JSON错误")
            else:
                print("✅ 无效认证返回JSON响应")
                self.results.append("无效认证: JSON响应")
        except Exception as e:
            print(f"无效认证请求异常: {e}")
    
    def check_services_status(self):
        """检查服务状态"""
        print("\n🔍 检查服务状态...")
        
        # 检查前端服务
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                print("✅ 前端服务运行正常")
                self.results.append("前端服务: 运行正常")
            else:
                print(f"⚠️  前端服务状态异常: {response.status_code}")
        except Exception as e:
            print(f"❌ 前端服务不可访问: {e}")
            self.errors.append(f"前端服务不可访问: {e}")
        
        # 检查后端服务
        try:
            response = requests.get(f"{BACKEND_URL}/api/settings/jenkins", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务运行正常")
                self.results.append("后端服务: 运行正常")
            else:
                print(f"⚠️  后端服务状态异常: {response.status_code}")
        except Exception as e:
            print(f"❌ 后端服务不可访问: {e}")
            self.errors.append(f"后端服务不可访问: {e}")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 测试报告汇总")
        print("="*60)
        
        print(f"\n✅ 成功的测试 ({len(self.results)}):")
        for result in self.results:
            print(f"  • {result}")
        
        print(f"\n❌ 失败的测试 ({len(self.errors)}):")
        for error in self.errors:
            print(f"  • {error}")
        
        if len(self.errors) == 0:
            print("\n🎉 所有测试通过！Jenkins API问题已解决！")
            return True
        else:
            print(f"\n⚠️  发现 {len(self.errors)} 个问题需要修复")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始全面API测试...")
        
        self.check_services_status()
        self.test_backend_direct()
        self.test_frontend_proxy() 
        self.test_html_vs_json_responses()
        self.test_authentication_scenarios()
        
        return self.generate_report()

def main():
    print("🎯 Jenkins API问题全面诊断和修复验证")
    print("="*60)
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎊 修复验证完成：问题已彻底解决！")
        print("用户现在可以正常访问 http://localhost:5173/ops/jenkins")
    else:
        print("\n🔧 仍需进一步修复，请查看上述错误列表")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())