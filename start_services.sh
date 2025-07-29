#!/bin/bash

echo "🚀 启动运维管理系统..."

# 检查依赖
echo "📦 检查依赖..."
cd frontend && npm list > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "安装前端依赖..."
    npm install
fi

cd ../backend && pip3 show flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "安装后端依赖..."
    pip3 install -r requirements.txt
fi

# 启动后端服务
echo "🔧 启动后端服务..."
cd ../backend
nohup python3 run.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 启动前端服务
echo "🌐 启动前端服务..."
cd ../frontend
nohup npx vite --host 0.0.0.0 --port 5173 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"

# 等待前端启动
sleep 5

echo ""
echo "✅ 服务启动完成！"
echo "📋 访问信息："
echo "   前端地址: http://localhost:5173"
echo "   后端地址: http://localhost:5000"
echo "   默认账号: admin / 9itNKA6nVs0ZkGw321Tu"
echo ""
echo "📝 进程信息："
echo "   后端PID: $BACKEND_PID"
echo "   前端PID: $FRONTEND_PID"
echo ""
echo "🛑 停止服务命令："
echo "   kill $BACKEND_PID $FRONTEND_PID"

# 检查服务状态
echo ""
echo "🔍 检查服务状态..."
sleep 2

# 测试后端
curl -s http://localhost:5000/api/captcha > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
fi

# 测试前端
curl -s http://localhost:5173 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常，请等待1-2分钟后重试"
fi

echo ""
echo "🎯 请打开浏览器访问: http://localhost:5173"