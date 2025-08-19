#!/bin/bash

echo "舒克AI工具集 - 前端服务启动脚本 (Unix/macOS)"
echo "=========================================="

# 切换到前端目录
cd "$(dirname "$0")/../frontend" || exit 1

echo "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "错误：未找到Node.js，请确保Node.js已安装并添加到PATH"
    read -p "按回车键退出..."
    exit 1
fi

echo "检查npm环境..."
if ! command -v npm &> /dev/null; then
    echo "错误：未找到npm"
    read -p "按回车键退出..."
    exit 1
fi

echo "检查依赖包..."
if [ ! -d "node_modules" ]; then
    echo "正在安装前端依赖包..."
    npm install
    if [ $? -ne 0 ]; then
        echo "错误：前端依赖包安装失败"
        read -p "按回车键退出..."
        exit 1
    fi
fi

echo "启动前端服务..."
echo "前端地址: http://localhost:9999"
echo "后端地址: http://localhost:8888"
echo "按 Ctrl+C 停止服务"
echo "=========================================="
npm run dev