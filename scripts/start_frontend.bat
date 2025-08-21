@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title 舒克AI工具集 - 前端服务

echo 舒克AI工具集 - 前端服务启动脚本 (Windows)
echo ==========================================

:: 切换到项目根目录
cd ..
cd frontend

npm run dev

pause