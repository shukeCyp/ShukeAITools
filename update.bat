@echo off
chcp 65001 > nul
echo 正在更新代码库...

:: 检查是否存在.git目录
if not exist ".git" (
    echo.
    echo ✗ 未找到.git目录！
    echo 当前目录不是Git仓库，可能是从ZIP包下载的代码
    echo 请使用git clone命令重新获取代码，或者手动下载最新版本
    echo.
    pause
    exit /b 1
)

git pull --rebase
if %errorlevel% equ 0 (
    echo.
    echo ✓ 代码更新成功！
    echo.
) else (
    echo.
    echo ✗ 代码更新失败！
    echo 错误代码: %errorlevel%
    echo 请检查网络连接或解决冲突后重试
    echo.
)

pause
