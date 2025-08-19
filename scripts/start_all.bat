@echo off
chcp 65001 >nul
echo 舒克AI工具集 - 启动所有服务 (Windows)
echo =========================================

echo 正在启动后端服务...
start "舒克AI工具集 - 后端" cmd /k "cd /d "%~dp0" && start_backend.bat"

echo 等待3秒让后端服务启动...
timeout /t 3 /nobreak >nul

echo 正在启动前端服务...
start "舒克AI工具集 - 前端" cmd /k "cd /d "%~dp0" && start_frontend.bat"

echo 所有服务启动完成！
echo 前端地址: http://localhost:9999
echo 后端地址: http://localhost:8888
echo =========================================
pause