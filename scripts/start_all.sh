#!/bin/bash

echo "舒克AI工具集 - 启动所有服务 (Unix/macOS)"
echo "========================================"

# 获取脚本目录
SCRIPT_DIR="$(dirname "$0")"

echo "正在启动后端服务..."
if command -v gnome-terminal &> /dev/null; then
    # Ubuntu/Linux with gnome-terminal
    gnome-terminal --title="舒克AI工具集 - 后端" -- bash -c "cd '$SCRIPT_DIR' && ./start_backend.sh"
elif command -v osascript &> /dev/null; then
    # macOS with Terminal.app
    osascript -e "tell app \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ./start_backend.sh\""
elif command -v xterm &> /dev/null; then
    # Generic X11 terminal
    xterm -T "舒克AI工具集 - 后端" -e "cd '$SCRIPT_DIR' && ./start_backend.sh" &
else
    # 后台运行
    echo "在后台启动后端服务..."
    cd "$SCRIPT_DIR" && ./start_backend.sh &
fi

echo "等待3秒让后端服务启动..."
sleep 3

echo "正在启动前端服务..."
if command -v gnome-terminal &> /dev/null; then
    # Ubuntu/Linux with gnome-terminal
    gnome-terminal --title="舒克AI工具集 - 前端" -- bash -c "cd '$SCRIPT_DIR' && ./start_frontend.sh"
elif command -v osascript &> /dev/null; then
    # macOS with Terminal.app
    osascript -e "tell app \"Terminal\" to do script \"cd '$SCRIPT_DIR' && ./start_frontend.sh\""
elif command -v xterm &> /dev/null; then
    # Generic X11 terminal
    xterm -T "舒克AI工具集 - 前端" -e "cd '$SCRIPT_DIR' && ./start_frontend.sh" &
else
    # 后台运行
    echo "在后台启动前端服务..."
    cd "$SCRIPT_DIR" && ./start_frontend.sh &
fi

echo "所有服务启动完成！"
echo "前端地址: http://localhost:9999"
echo "后端地址: http://localhost:8888"
echo "========================================"

if command -v osascript &> /dev/null; then
    read -p "按回车键退出..."
fi