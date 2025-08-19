@echo off
chcp 65001 >nul
echo 舒克AI工具集 - 前端服务启动脚本 (Windows)
echo ==========================================

cd /d "%~dp0\..\frontend"

echo 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Node.js，请确保Node.js已安装并添加到PATH
    pause
    exit /b 1
)

echo 检查npm环境...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到npm
    pause
    exit /b 1
)

echo 检查依赖包...
if not exist "node_modules" (
    echo 正在安装前端依赖包...
    npm install
    if %errorlevel% neq 0 (
        echo 错误：前端依赖包安装失败
        pause
        exit /b 1
    )
)

echo 启动前端服务...
echo 前端地址: http://localhost:9999
echo 后端地址: http://localhost:8888
echo 按 Ctrl+C 停止服务
echo ==========================================
npm run dev

pause