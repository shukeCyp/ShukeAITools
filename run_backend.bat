@echo off
chcp 65001 > nul
echo 正在启动后端服务...

:: 检查是否存在后端目录
if not exist "backend" (
    echo.
    echo ✗ 未找到backend目录！
    echo 请确保在项目根目录下运行此脚本
    echo.
    pause
    exit /b 1
)

:: 检查是否安装了Python
python -V > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ✗ 未检测到Python！
    echo 请先安装Python后再运行此脚本
    echo 下载地址: https://www.python.org/
    echo.
    pause
    exit /b 1
)

:: 进入后端目录
cd backend

:: 检查是否存在requirements.txt
if not exist "requirements.txt" (
    echo.
    echo ✗ 未找到requirements.txt文件！
    echo 请确保在项目根目录下运行此脚本
    echo.
    pause
    exit /b 1
)

:: 安装Python依赖
echo.
echo 正在安装Python依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ✗ 依赖安装失败！
    echo 请检查网络连接后重试
    echo.
    pause
    exit /b 1
)

:: 安装Playwright浏览器
echo.
echo 正在安装Playwright浏览器...
playwright install
if %errorlevel% neq 0 (
    echo.
    echo ✗ Playwright安装失败！
    echo 请检查网络连接后重试
    echo.
    pause
    exit /b 1
)

:: 启动后端服务
echo.
echo ✓ 正在启动后端服务器...
echo 服务器将在 http://localhost:8888 启动
echo 按 Ctrl+C 可以停止服务器
echo.

python app.py

pause
