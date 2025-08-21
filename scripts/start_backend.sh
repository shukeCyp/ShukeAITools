#!/bin/bash

echo "ShukeAI Tools - Backend Service Startup Script (Unix/macOS)"
echo "=========================================="

# 切换到项目根目录
cd "$(dirname "$0")/.." || exit 1
cd backend

# 创建虚拟环境
uv venv .venv -p 3.13.2
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt --upgrade
uv run playwright install chromium
uv run python app.py