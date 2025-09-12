@echo off
chcp 65001 > nul
echo 正在启动前端服务...

:: 检查是否存在前端目录
if not exist "frontend" (
    echo.
    echo ✗ 未找到frontend目录！
    echo 请确保在项目根目录下运行此脚本
    echo.
    pause
    exit /b 1
)

:: 进入前端目录
cd frontend

:: 检查是否安装了Node.js
node -v > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ✗ 未检测到Node.js！
    echo 请先安装Node.js后再运行此脚本
    echo 下载地址: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

:: 检查是否存在node_modules目录
if not exist "node_modules" (
    echo.
    echo 首次运行，正在安装依赖...
    npm install
    if %errorlevel% neq 0 (
        echo.
        echo ✗ 依赖安装失败！
        echo 请检查网络连接后重试
        echo.
        pause
        exit /b 1
    )
)

:: 启动开发服务器
echo.
echo ✓ 正在启动前端开发服务器...
echo 服务器将在 http://localhost:3000 启动
echo 按 Ctrl+C 可以停止服务器
echo.

npm run dev

pause
