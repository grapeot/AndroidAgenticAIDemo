#!/bin/bash

# AI Chat System 后端启动脚本
# 启动 FastAPI 服务器，端口 8081，支持热重载

echo "🚀 启动 AI Chat System 后端服务器..."
echo "端口: 8081"
echo "热重载: 已启用"
echo "按 Ctrl+C 停止服务器"
echo "=" * 50

# 检查是否在项目根目录
if [ ! -f "backend/main.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "当前目录应包含 backend/main.py 文件"
    exit 1
fi

# 检查依赖是否安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  警告: FastAPI 未安装，正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动服务器
echo "✅ 启动 FastAPI 服务器..."
uvicorn backend.main:app --host 0.0.0.0 --port 8081 --reload