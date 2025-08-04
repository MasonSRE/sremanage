#!/bin/bash

# SRE管理系统启动脚本
# 包含Phase 5优化组件的完整部署和启动流程

set -e  # 遇到错误立即退出

echo "🎯 SRE管理系统启动脚本"
echo "包含Phase 5生产优化组件"
echo "=================================="

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python版本: $PYTHON_VERSION"

# 检查pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip未安装，请先安装pip"
    exit 1
fi

# 统一使用pip命令
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

echo "使用pip命令: $PIP_CMD"

# 检查是否首次运行
if [ ! -f ".deployed" ]; then
    echo "🚀 检测到首次运行，执行完整部署..."
    
    # 运行部署脚本
    if python3 deploy.py; then
        # 标记已部署
        touch .deployed
        echo "✅ 首次部署完成"
    else
        echo "❌ 部署失败"
        exit 1
    fi
else
    echo "✅ 系统已部署，执行快速启动..."
    
    # 快速检查关键依赖
    echo "检查关键依赖..."
    python3 -c "
import sys
try:
    import flask, pymysql, cryptography, psutil
    print('✅ 关键依赖检查通过')
except ImportError as e:
    print(f'❌ 依赖缺失: {e}')
    print('请运行: rm .deployed && ./start.sh 进行重新部署')
    sys.exit(1)
"
    
    if [ $? -ne 0 ]; then
        echo "❌ 依赖检查失败，请重新部署"
        exit 1
    fi
    
    # 确保目录存在
    echo "检查目录结构..."
    mkdir -p logs logs/phase5 cache cache/performance cache/security cache/encryption
    
    # 检查配置文件
    if [ ! -f "config.py" ]; then
        echo "❌ 配置文件config.py不存在"
        exit 1
    fi
fi

# 启动选项
echo ""
echo "请选择启动模式:"
echo "1) 开发模式 (debug=True)"
echo "2) 生产模式 (gunicorn)"
echo "3) 后台运行模式"
echo "4) 仅检查配置"

read -p "请输入选择 (1-4, 默认1): " choice
choice=${choice:-1}

case $choice in
    1)
        echo "🚀 启动开发模式..."
        echo "访问地址: http://localhost:5001"
        echo "按 Ctrl+C 停止服务"
        echo ""
        python3 run.py
        ;;
    2)
        echo "🚀 启动生产模式..."
        if ! command -v gunicorn &> /dev/null; then
            echo "安装gunicorn..."
            $PIP_CMD install gunicorn
        fi
        echo "访问地址: http://localhost:5001"
        echo "按 Ctrl+C 停止服务"
        echo ""
        gunicorn -w 4 -b 0.0.0.0:5001 --timeout 120 run:app
        ;;
    3)
        echo "🚀 启动后台运行模式..."
        if ! command -v gunicorn &> /dev/null; then
            echo "安装gunicorn..."
            $PIP_CMD install gunicorn
        fi
        
        # 停止已有进程
        pkill -f "gunicorn.*run:app" || true
        
        # 启动后台进程
        nohup gunicorn -w 4 -b 0.0.0.0:5001 --timeout 120 run:app > logs/gunicorn.log 2>&1 &
        
        sleep 2
        
        if pgrep -f "gunicorn.*run:app" > /dev/null; then
            echo "✅ 服务已在后台启动"
            echo "访问地址: http://localhost:5001"
            echo "日志文件: logs/gunicorn.log"
            echo "停止服务: pkill -f 'gunicorn.*run:app'"
        else
            echo "❌ 后台启动失败，请检查日志"
            exit 1
        fi
        ;;
    4)
        echo "🔍 检查配置..."
        python3 -c "
from config import Config;
print('数据库配置:');
print(f'  主机: {Config.DB_HOST}:{Config.DB_PORT}');
print(f'  数据库: {Config.DB_NAME}');
print(f'  用户: {Config.DB_USER}');
print('Phase 5配置:');
print(f'  性能监控: {Config.PERFORMANCE_MONITOR_ENABLED}');
print(f'  安全审计: {Config.SECURITY_AUDIT_ENABLED}');
print(f'  数据库池: {Config.DATABASE_POOL_SIZE}');
print('✅ 配置检查完成');
"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "📋 系统信息:"
echo "  配置文件: config.py"
echo "  日志目录: logs/"
echo "  缓存目录: cache/"
echo "  Phase 5: 已集成"
echo ""
echo "🎉 感谢使用SRE管理系统!"