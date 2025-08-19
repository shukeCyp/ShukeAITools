@echo off
chcp 65001 >nul
echo 舒克AI工具集 - 后端服务启动脚本 (Windows)
echo ==========================================

cd /d "%~dp0\..\backend"

echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo 检查依赖包...
python -c "import flask, flask_cors, peewee, playwright, colorama, asyncio" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖包...
    pip install flask flask-cors peewee playwright colorama
    if %errorlevel% neq 0 (
        echo 错误：依赖包安装失败
        pause
        exit /b 1
    )
)

echo 检查Playwright浏览器...
playwright install chromium >nul 2>&1

echo 启动后端服务...
echo 服务地址: http://localhost:8888
echo 按 Ctrl+C 停止服务
echo ==========================================
python app.py

pause