@echo off
chcp 65001 > nul
title 舒克AI工具集 - 前端服务

echo 舒克AI工具集 - 前端服务启动脚本 (Windows)
echo ==========================================

:: 切换到项目根目录
cd /d "%~dp0\.."
set PROJECT_ROOT=%CD%

echo 项目根目录: %PROJECT_ROOT%

:: 切换到前端目录
cd /d "%PROJECT_ROOT%\frontend"
echo 当前目录: %CD%

echo 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Node.js
    echo 📦 检测到Node.js安装包: %PROJECT_ROOT%\scripts\node-v22.18.0-x86.msi
    echo.
    echo 请选择安装方式：
    echo 1. 使用本地安装包 ^(推荐^)
    echo 2. 在线下载安装
    echo 3. 退出
    echo.
    set /p choice=请输入选择 ^(1-3^): 
    
    if "%choice%"=="1" (
        echo 📂 正在打开本地安装包...
        if exist "%PROJECT_ROOT%\scripts\node-v22.18.0-x86.msi" (
            start "" "%PROJECT_ROOT%\scripts\node-v22.18.0-x86.msi"
            echo ✅ 已打开Node.js安装包
            echo 📋 请按照安装向导完成安装
            echo ⚠️  安装完成后，请重新打开命令行窗口，然后重新运行此脚本
        ) else (
            echo ❌ 未找到安装包文件: %PROJECT_ROOT%\scripts\node-v22.18.0-x86.msi
            echo 🌐 正在打开Node.js官网进行下载...
            start "" "https://nodejs.org/"
        )
    ) else if "%choice%"=="2" (
        echo 🌐 正在打开Node.js官网...
        start "" "https://nodejs.org/"
        echo 📋 请下载并安装Node.js 18或更高版本
    ) else if "%choice%"=="3" (
        echo 退出安装
        exit /b 0
    ) else (
        echo 无效选择，退出
        exit /b 1
    )
    
    echo.
    echo 安装完成后，请重新运行此脚本
    pause
    exit /b 1
)

:: 显示Node.js版本
echo Node.js版本：
node --version

:: 检查包管理器，优先使用pnpm，其次npm
set PKG_MANAGER=
pnpm --version >nul 2>&1
if %errorlevel% equ 0 (
    set PKG_MANAGER=pnpm
    echo 使用包管理器: pnpm
) else (
    npm --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PKG_MANAGER=npm
        echo 使用包管理器: npm
    ) else (
        echo 错误：未找到npm或pnpm包管理器
        pause
        exit /b 1
    )
)

:: 检查依赖包
echo 检查前端依赖...
if not exist "node_modules" (
    goto install_deps
)
if "%PKG_MANAGER%"=="pnpm" (
    if not exist "pnpm-lock.yaml" goto install_deps
) else (
    if not exist "node_modules\.package-lock.json" goto install_deps
)
echo 依赖已存在，跳过安装
goto start_server

:install_deps
echo 正在安装前端依赖包...
if "%PKG_MANAGER%"=="pnpm" (
    pnpm install
) else (
    npm install
)

if %errorlevel% neq 0 (
    echo 错误：前端依赖包安装失败
    pause
    exit /b 1
)
echo 依赖安装完成

:start_server
echo 启动前端开发服务器...
echo 前端地址: http://localhost:5173
echo 后端地址: http://localhost:8888
echo 按 Ctrl+C 停止服务
echo ==========================================

:: 使用对应的包管理器启动
if "%PKG_MANAGER%"=="pnpm" (
    pnpm run dev
) else (
    npm run dev
)

pause