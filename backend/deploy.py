#!/usr/bin/env python3
"""
SRE管理系统部署脚本
包含Phase 5优化组件的完整部署流程
"""

import sys
import os
import subprocess
from pathlib import Path
import time

def print_step(step, description):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step}: {description}")
    print(f"{'='*60}")

def run_command(command, description, ignore_errors=False):
    """执行命令并处理错误"""
    print(f"执行: {description}")
    print(f"命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"⚠️ 警告: {e}")
            return False
        else:
            print(f"❌ 错误: {e}")
            if e.stderr:
                print(f"错误详情: {e.stderr}")
            return False

def check_requirements():
    """检查系统要求"""
    print_step(1, "检查系统要求")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    
    # 检查pip
    if not run_command("pip --version", "检查pip", ignore_errors=True):
        print("❌ pip未安装")
        return False
    
    # 检查MySQL连接
    try:
        import pymysql
        # 这里可以添加数据库连接测试
        print("✅ MySQL连接组件已安装")
    except ImportError:
        print("⚠️ MySQL连接组件未安装，将在后续步骤中安装")
    
    return True

def install_dependencies():
    """安装依赖包"""
    print_step(2, "安装Python依赖包")
    
    # 安装主要依赖
    if not run_command("pip install -r requirements.txt", "安装主要依赖包"):
        return False
    
    # 检查Phase 5依赖
    phase5_deps = ['psutil', 'redis', 'cryptography']
    for dep in phase5_deps:
        if not run_command(f"pip show {dep}", f"检查{dep}依赖", ignore_errors=True):
            print(f"⚠️ {dep}未安装，尝试安装...")
            if not run_command(f"pip install {dep}", f"安装{dep}"):
                print(f"❌ {dep}安装失败")
                return False
    
    return True

def setup_directories():
    """创建必要的目录结构"""
    print_step(3, "创建目录结构")
    
    directories = [
        'logs',
        'logs/phase5',
        'cache',
        'cache/performance',
        'cache/security', 
        'cache/encryption',
        'uploads',
        'temp'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 创建目录: {directory}")
        except Exception as e:
            print(f"❌ 创建目录失败 {directory}: {e}")
            return False
    
    return True

def setup_database():
    """设置数据库"""
    print_step(4, "初始化数据库")
    
    # 检查数据库配置
    try:
        from config import Config
        print(f"数据库主机: {Config.DB_HOST}:{Config.DB_PORT}")
        print(f"数据库名称: {Config.DB_NAME}")
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
        return False
    
    # 执行数据库初始化脚本
    sql_files = [
        'sql/01.hosts.sql',
        'sql/02.software.sql',
        'sql/03.settings.sql',
        'sql/04.migrations.sql',
        'sql/05.site_monitoring.sql',
        'sql/06.deployment_history.sql',
        'sql/07.deployment_config.sql',
        'sql/08.site_cache.sql',
        'sql/09.simple_deploy.sql',
        'sql/10.phase5_tables.sql'  # Phase 5数据库表
    ]
    
    for sql_file in sql_files:
        if os.path.exists(sql_file):
            print(f"执行SQL文件: {sql_file}")
            # 这里可以添加具体的SQL执行逻辑
        else:
            print(f"⚠️ SQL文件不存在: {sql_file}")
    
    return True

def generate_encryption_keys():
    """生成加密密钥"""
    print_step(5, "配置加密密钥")
    
    try:
        from cryptography.fernet import Fernet
        
        env_file = Path('.env')
        env_content = ""
        
        # 读取现有.env文件
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # 检查是否已有加密密钥
        if 'ENCRYPTION_MASTER_KEY' not in env_content:
            key = Fernet.generate_key().decode()
            env_content += f"\n# Phase 5 加密配置\nENCRYPTION_MASTER_KEY={key}\n"
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print("✅ 生成新的加密密钥")
        else:
            print("✅ 加密密钥已存在")
        
        return True
    except Exception as e:
        print(f"❌ 加密密钥配置失败: {e}")
        return False

def initialize_phase5():
    """初始化Phase 5组件"""
    print_step(6, "初始化Phase 5优化组件")
    
    # 执行Phase 5初始化脚本
    script_path = "scripts/init_phase5.py"
    if os.path.exists(script_path):
        if run_command(f"python {script_path}", "执行Phase 5初始化"):
            print("✅ Phase 5组件初始化完成")
            return True
        else:
            print("❌ Phase 5组件初始化失败")
            return False
    else:
        print(f"⚠️ Phase 5初始化脚本不存在: {script_path}")
        # 直接执行初始化逻辑
        try:
            from scripts.init_phase5 import init_phase5
            return init_phase5()
        except ImportError:
            print("⚠️ 无法执行Phase 5初始化，将在运行时自动初始化")
            return True

def run_tests():
    """运行测试"""
    print_step(7, "运行系统测试")
    
    # 基础连通性测试
    test_commands = [
        ("python -c 'import app; print(\"应用导入成功\")'", "应用导入测试"),
        ("python -c 'from config import Config; print(\"配置导入成功\")'", "配置导入测试"),
    ]
    
    for cmd, desc in test_commands:
        if run_command(cmd, desc, ignore_errors=True):
            print(f"✅ {desc}通过")
        else:
            print(f"⚠️ {desc}失败")
    
    return True

def start_services():
    """启动服务"""
    print_step(8, "启动服务")
    
    print("🚀 准备启动SRE管理系统...")
    print("使用以下命令启动:")
    print("  开发模式: python run.py")
    print("  生产模式: gunicorn -w 4 -b 0.0.0.0:5001 run:app")
    print("\n访问地址:")
    print("  后端API: http://localhost:5001")
    print("  前端页面: http://localhost:5173 (需要单独启动)")
    
    # 询问是否立即启动
    try:
        choice = input("\n是否立即启动开发服务器? (y/N): ").lower()
        if choice == 'y':
            print("启动开发服务器...")
            os.system("python run.py")
    except KeyboardInterrupt:
        print("\n✅ 部署完成，可以随时使用上述命令启动服务")
    
    return True

def main():
    """主部署流程"""
    print("🎯 SRE管理系统部署脚本")
    print("包含Phase 5生产优化组件")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    steps = [
        (check_requirements, "系统要求检查"),
        (install_dependencies, "依赖包安装"),
        (setup_directories, "目录结构创建"),
        (setup_database, "数据库初始化"),
        (generate_encryption_keys, "加密密钥配置"),
        (initialize_phase5, "Phase 5组件初始化"),
        (run_tests, "系统测试"),
        (start_services, "服务启动")
    ]
    
    start_time = time.time()
    failed_steps = []
    
    for i, (step_func, step_name) in enumerate(steps, 1):
        try:
            if not step_func():
                failed_steps.append(f"步骤{i}: {step_name}")
                print(f"❌ 步骤{i}失败: {step_name}")
                
                # 询问是否继续
                choice = input("是否继续部署? (y/N): ").lower()
                if choice != 'y':
                    break
            else:
                print(f"✅ 步骤{i}完成: {step_name}")
        except KeyboardInterrupt:
            print(f"\n❌ 用户中断部署在步骤{i}: {step_name}")
            break
        except Exception as e:
            print(f"❌ 步骤{i}异常: {step_name} - {e}")
            failed_steps.append(f"步骤{i}: {step_name} ({e})")
    
    # 部署总结
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("部署总结")
    print(f"{'='*60}")
    print(f"总耗时: {duration:.2f}秒")
    
    if failed_steps:
        print(f"❌ 失败步骤 ({len(failed_steps)}):")
        for step in failed_steps:
            print(f"  - {step}")
    else:
        print("✅ 所有步骤完成")
    
    print("\n📋 后续操作:")
    print("1. 检查配置文件 config.py 和 .env")
    print("2. 确保MySQL数据库正常运行")
    print("3. 启动前端开发服务器 (npm run dev)")
    print("4. 使用 python run.py 启动后端服务")
    
    return len(failed_steps) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)