@echo off
chcp 65001 > nul
title 舒克AI工具集 - 后端服务

echo 舒克AI工具集 - 后端服务启动脚本 (Windows)
echo ==========================================

:: 切换到项目根目录
cd /d "%~dp0\.."
set PROJECT_ROOT=%CD%
set SCRIPTS_DIR=%PROJECT_ROOT%\scripts

echo 项目根目录: %PROJECT_ROOT%

:: 使用项目内置UV
echo 使用项目内置UV: %SCRIPTS_DIR%\uv.exe

:: 检查UV版本
echo UV版本信息：
"%SCRIPTS_DIR%\uv.exe" self version

:: 切换到后端目录
cd /d "%PROJECT_ROOT%\backend"
echo 当前目录: %CD%

:: 检查Python版本要求
echo 检查Python环境...
"%SCRIPTS_DIR%\uv.exe" python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装Python 3.11...
    "%SCRIPTS_DIR%\uv.exe" python install 3.11
    if %errorlevel% neq 0 (
        echo 错误：Python安装失败
        pause
        exit /b 1
    )
)

:: 创建虚拟环境
echo 创建虚拟环境...
"%SCRIPTS_DIR%\uv.exe" venv

:: 显示Python版本
echo Python版本：
"%SCRIPTS_DIR%\uv.exe" run python --version

:: 检查并安装Python依赖
echo 检查Python依赖...
if not exist "requirements.txt" (
    echo requirements.txt 不存在，将使用UV安装基础依赖...
    "%SCRIPTS_DIR%\uv.exe" pip install playwright peewee python-dotenv requests beautifulsoup4 python-dateutil pillow pandas flask flask-cors colorama aiohttp aiofiles
) else (
    echo 正在安装requirements.txt中的依赖...
    "%SCRIPTS_DIR%\uv.exe" pip install -r requirements.txt
)

if %errorlevel% neq 0 (
    echo 错误：Python依赖安装失败
    pause
    exit /b 1
)

:: 安装Playwright浏览器
echo 检查Playwright浏览器...
"%SCRIPTS_DIR%\uv.exe" run playwright install chromium
if %errorlevel% neq 0 (
    echo 警告：Playwright浏览器安装失败，某些功能可能无法正常使用
)

echo 启动后端服务...
echo 服务地址: http://localhost:8888
echo 按 Ctrl+C 停止服务
echo ==========================================

:: 使用UV运行应用
"%SCRIPTS_DIR%\uv.exe" run python app.py

pause