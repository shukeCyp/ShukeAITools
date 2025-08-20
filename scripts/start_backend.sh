#!/bin/bash

echo "舒克AI工具集 - 后端服务启动脚本 (Unix/macOS)"
echo "=========================================="

# 切换到项目根目录
cd "$(dirname "$0")/.." || exit 1
PROJECT_ROOT=$(pwd)
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

echo "项目根目录: $PROJECT_ROOT"

# 检查UV是否存在
UV_CMD=""
if [ -f "$SCRIPTS_DIR/uv" ]; then
    UV_CMD="$SCRIPTS_DIR/uv"
    echo "使用项目内置UV: $UV_CMD"
elif command -v uv &> /dev/null; then
    UV_CMD="uv"
    echo "使用系统UV: $UV_CMD"
else
    echo "错误：未找到UV，请确保UV已安装或使用项目内置版本"
    echo "您可以通过以下方式安装UV："
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    read -p "按回车键退出..."
    exit 1
fi

# 检查UV版本
echo "UV版本信息："
$UV_CMD self version

# 切换到后端目录
cd "$PROJECT_ROOT/backend" || exit 1
echo "当前目录: $(pwd)"

# 检查Python版本要求
echo "检查Python环境..."
if ! $UV_CMD python --version &> /dev/null; then
    echo "正在安装Python 3.11..."
    $UV_CMD python install 3.11
    if [ $? -ne 0 ]; then
        echo "错误：Python安装失败"
        read -p "按回车键退出..."
        exit 1
    fi
fi

# 创建虚拟环境
echo "创建虚拟环境..."
$UV_CMD venv

# 显示Python版本
echo "Python版本："
$UV_CMD run python --version

# 检查并安装Python依赖
echo "检查Python依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt 不存在，将使用UV安装基础依赖..."
    $UV_CMD pip install playwright peewee python-dotenv requests beautifulsoup4 python-dateutil pillow pandas flask flask-cors colorama aiohttp aiofiles
else
    echo "正在安装requirements.txt中的依赖..."
    $UV_CMD pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo "错误：Python依赖安装失败"
    read -p "按回车键退出..."
    exit 1
fi

# 安装Playwright浏览器
echo "检查Playwright浏览器..."
$UV_CMD run playwright install chromium
if [ $? -ne 0 ]; then
    echo "警告：Playwright浏览器安装失败，某些功能可能无法正常使用"
fi

echo "启动后端服务..."
echo "服务地址: http://localhost:8888"
echo "按 Ctrl+C 停止服务"
echo "=========================================="

# 使用UV运行应用
$UV_CMD run python app.py