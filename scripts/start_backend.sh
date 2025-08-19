#!/bin/bash

echo "舒克AI工具集 - 后端服务启动脚本 (Unix/macOS)"
echo "=========================================="

# 切换到后端目录
cd "$(dirname "$0")/../backend" || exit 1

echo "检查Python环境..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "错误：未找到Python，请确保Python已安装并添加到PATH"
    read -p "按回车键退出..."
    exit 1
fi

# 优先使用python3，如果不存在则使用python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
else
    PYTHON_CMD=python
    PIP_CMD=pip
fi

echo "使用Python命令: $PYTHON_CMD"

echo "检查依赖包..."
if ! $PYTHON_CMD -c "import flask, flask_cors, peewee, playwright, colorama, asyncio" &> /dev/null; then
    echo "正在安装依赖包..."
    $PIP_CMD install flask flask-cors peewee playwright colorama
    if [ $? -ne 0 ]; then
        echo "错误：依赖包安装失败"
        read -p "按回车键退出..."
        exit 1
    fi
fi

echo "检查Playwright浏览器..."
playwright install chromium &> /dev/null

echo "启动后端服务..."
echo "服务地址: http://localhost:8888"
echo "按 Ctrl+C 停止服务"
echo "=========================================="
$PYTHON_CMD app.py