#!/usr/bin/env python3
"""
Jenkins API完整测试脚本
测试所有Jenkins相关的API端点，确保前后端连接正常
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5002"

def test_jenkins_settings():
    """测试Jenkins设置API"""
    print("🔧 测试 Jenkins 设置 API...")
    
    response = requests.get(f"{BASE_URL}/api/settings/jenkins")
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        if data.get('success') and data.get('data'):
            print(f"  ✅ 成功 - 找到 {len(data['data'])} 个Jenkins实例")
            return data['data']
        else:
            print("  ❌ 失败 - 数据格式不正确")
            return None
    else:
        print(f"  ❌ 失败 - HTTP {response.status_code}")
        return None

def test_jenkins_jobs(instance_id):
    """测试Jenkins任务列表API"""
    print(f"📋 测试 Jenkins 任务列表 API (实例 {instance_id})...")
    
    response = requests.get(f"{BASE_URL}/api/ops/jenkins/jobs/{instance_id}")
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ 成功 - 返回任务数据")
        return True
    else:
        print(f"  ❌ 失败 - HTTP {response.status_code}")
        if response.text:
            print(f"  错误信息: {response.text[:200]}")
        return False

def test_jenkins_builds(instance_id):
    """测试Jenkins构建历史API"""
    print(f"📊 测试 Jenkins 构建历史 API (实例 {instance_id})...")
    
    response = requests.get(f"{BASE_URL}/api/ops/jenkins/builds/history/{instance_id}")
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ 成功 - 返回构建数据")
        return True
    else:
        print(f"  ❌ 失败 - HTTP {response.status_code}")
        if response.text:
            print(f"  错误信息: {response.text[:200]}")
        return False

def test_jenkins_analytics(instance_id):
    """测试Jenkins分析API"""
    print(f"📈 测试 Jenkins 分析 API (实例 {instance_id})...")
    
    response = requests.get(f"{BASE_URL}/api/ops/jenkins/analytics/overview/{instance_id}")
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ 成功 - 返回分析数据")
        return True
    else:
        print(f"  ❌ 失败 - HTTP {response.status_code}")
        if response.text:
            print(f"  错误信息: {response.text[:200]}")
        return False

def main():
    print("🚀 开始 Jenkins API 完整测试\n")
    
    # 测试Jenkins设置
    instances = test_jenkins_settings()
    if not instances:
        print("\n❌ Jenkins设置测试失败，无法继续")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # 对每个实例测试各种API
    success_count = 0
    total_tests = 0
    
    for instance in instances:
        instance_id = instance['id']
        print(f"\n🔍 测试实例: {instance['name']} (ID: {instance_id})")
        print("-" * 30)
        
        # 测试任务列表
        total_tests += 1
        if test_jenkins_jobs(instance_id):
            success_count += 1
        
        print()
        
        # 测试构建历史
        total_tests += 1
        if test_jenkins_builds(instance_id):
            success_count += 1
        
        print()
        
        # 测试分析数据
        total_tests += 1
        if test_jenkins_analytics(instance_id):
            success_count += 1
    
    print("\n" + "="*50)
    print(f"📊 测试结果: {success_count}/{total_tests + 1} 通过")
    
    if success_count == total_tests:
        print("🎉 所有API测试均通过！Jenkins后端功能正常。")
        return True
    else:
        print("⚠️  部分API测试失败，需要检查相关实现。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)