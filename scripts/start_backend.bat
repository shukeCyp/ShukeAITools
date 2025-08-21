@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title ShukeAI Tools - Backend Service

echo ShukeAI Tools - Backend Service Startup Script (Windows)
echo ==========================================

:: 切换到项目根目录
cd ..
cd backend

"uv.exe" venv .venv -p 3.13.2
call .venv\Scripts\activate.bat

"uv.exe" pip install -r requirements.txt --upgrade
"uv.exe" run playwright install chromium
"uv.exe" run python app.py