#!/bin/bash

echo "舒克AI工具集 - 前端服务启动脚本 (Unix/macOS)"
echo "=========================================="

# 切换到项目根目录
cd "$(dirname "$0")/.." || exit 1
PROJECT_ROOT=$(pwd)

echo "项目根目录: $PROJECT_ROOT"

# 切换到前端目录
cd "$PROJECT_ROOT/frontend" || exit 1
echo "当前目录: $(pwd)"

echo "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js"
    echo "📦 检测到Node.js安装包: $PROJECT_ROOT/scripts/node-v22.18.0-x86.msi"
    echo ""
    echo "请选择安装方式："
    echo "1. 在线下载安装 (推荐)"
    echo "2. 退出"
    echo ""
    read -p "请输入选择 (1-2): " choice
    
    case $choice in
        1)
            echo "🌐 正在打开Node.js官网..."
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                echo "📋 请下载macOS版本的Node.js"
                open "https://nodejs.org/"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Linux
                echo "📋 Linux系统建议使用包管理器安装："
                echo "Ubuntu/Debian: sudo apt install nodejs npm"
                echo "CentOS/RHEL: sudo yum install nodejs npm"
                echo "或从官网下载: https://nodejs.org/"
                if command -v xdg-open &> /dev/null; then
                    xdg-open "https://nodejs.org/"
                fi
            else
                # 其他系统
                echo "📋 请访问官网下载适合您系统的版本"
                if command -v open &> /dev/null; then
                    open "https://nodejs.org/"
                elif command -v xdg-open &> /dev/null; then
                    xdg-open "https://nodejs.org/"
                else
                    echo "请手动访问: https://nodejs.org/"
                fi
            fi
            echo "⚠️  安装完成后，请重新运行此脚本"
            ;;
        2)
            echo "退出安装"
            exit 0
            ;;
        *)
            echo "无效选择，退出"
            exit 1
            ;;
    esac
    
    echo ""
    echo "安装完成后，请重新运行此脚本"
    read -p "按回车键退出..."
    exit 1
fi

# 显示Node.js版本
echo "Node.js版本："
node --version

# 检查包管理器，优先使用pnpm，其次npm
PKG_MANAGER=""
if command -v pnpm &> /dev/null; then
    PKG_MANAGER="pnpm"
    echo "使用包管理器: pnpm"
elif command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
    echo "使用包管理器: npm"
else
    echo "错误：未找到npm或pnpm包管理器"
    read -p "按回车键退出..."
    exit 1
fi

# 检查依赖包
echo "检查前端依赖..."
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ] && [ ! -f "pnpm-lock.yaml" ]; then
    echo "正在安装前端依赖包..."
    if [ "$PKG_MANAGER" = "pnpm" ]; then
        pnpm install
    else
        npm install
    fi
    
    if [ $? -ne 0 ]; then
        echo "错误：前端依赖包安装失败"
        read -p "按回车键退出..."
        exit 1
    fi
    echo "依赖安装完成"
else
    echo "依赖已存在，跳过安装"
fi

echo "启动前端开发服务器..."
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:8888"
echo "按 Ctrl+C 停止服务"
echo "=========================================="

# 使用对应的包管理器启动
if [ "$PKG_MANAGER" = "pnpm" ]; then
    pnpm run dev
else
    npm run dev
fi