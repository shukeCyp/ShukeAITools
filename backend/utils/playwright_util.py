# -*- coding: utf-8 -*-
"""
Playwright工具模块
用于检查和安装Playwright浏览器
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path


def is_playwright_installed():
    """检查Playwright是否已安装"""
    try:
        # 检查playwright包是否已安装
        spec = importlib.util.find_spec("playwright")
        if spec is None:
            print("Playwright包未安装")
            return False
        
        # 简单检查：尝试启动一个浏览器实例
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                # 尝试启动浏览器，如果成功则说明已安装
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("Playwright已正确安装并可以启动浏览器")
                return True
        except Exception as e:
            # 如果启动失败，可能是浏览器未安装
            error_msg = str(e).lower()
            if "executable doesn't exist" in error_msg or "browser executable" in error_msg:
                print("Playwright浏览器未安装")
                return False
            else:
                print(f"检查Playwright时出错: {e}")
                return False
            
    except ImportError:
        print("Playwright包未安装")
        return False
    except Exception as e:
        print(f"检查Playwright安装状态时出错: {e}")
        return False


def install_playwright():
    """安装Playwright浏览器"""
    try:
        print("开始安装Playwright浏览器...")
        
        # 首先确保playwright包已安装
        try:
            import playwright
            print("Playwright包已安装")
        except ImportError:
            print("Playwright包未安装，请先运行: pip install playwright")
            return False
        
        # 安装浏览器
        cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("Playwright浏览器安装成功!")
            print("安装输出:", result.stdout)
            return True
        else:
            print(f"Playwright浏览器安装失败，返回码: {result.returncode}")
            print("错误输出:", result.stderr)
            print("标准输出:", result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("Playwright安装超时（5分钟）")
        return False
    except Exception as e:
        print(f"安装Playwright时出错: {e}")
        return False


def ensure_playwright_installed():
    """确保Playwright已安装，如果没有则自动安装"""
    print("检查Playwright安装状态...")
    
    if is_playwright_installed():
        print("Playwright已正确安装")
        return True
    
    print("Playwright未安装或不完整，开始自动安装...")
    
    # 尝试安装
    max_retries = 2
    for attempt in range(max_retries):
        if attempt > 0:
            print(f"第 {attempt + 1} 次尝试安装Playwright...")
        
        if install_playwright():
            # 安装成功后再次检查
            if is_playwright_installed():
                print("Playwright安装并验证成功!")
                return True
            else:
                print("Playwright安装完成但验证失败")
        
        if attempt < max_retries - 1:
            print("安装失败，1秒后重试...")
            import time
            time.sleep(1)
    
    print("Playwright安装失败，请手动执行: python -m playwright install chromium")
    return False


def get_playwright_info():
    """获取Playwright安装信息"""
    info = {
        "installed": False,
        "version": None,
        "browser_path": None,
        "driver_path": None
    }
    
    try:
        # 获取版本信息
        import playwright
        info["version"] = playwright.__version__
        
        # 检查是否已安装
        info["installed"] = is_playwright_installed()
        
        # 如果已安装，尝试获取更多信息
        if info["installed"]:
            try:
                from playwright._impl._driver import compute_driver_executable
                info["driver_path"] = str(compute_driver_executable())
            except:
                pass
            
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    # 安全地获取浏览器路径
                    browser_path = getattr(p.chromium, 'executable_path', None)
                    if browser_path:
                        info["browser_path"] = str(browser_path)
            except:
                pass
                
    except Exception as e:
        print(f"获取Playwright信息时出错: {e}")
    
    return info


if __name__ == "__main__":
    # 测试功能
    print("=== Playwright安装检查 ===")
    info = get_playwright_info()
    print(f"安装状态: {info['installed']}")
    print(f"版本: {info['version']}")
    print(f"驱动路径: {info['driver_path']}")
    print(f"浏览器路径: {info['browser_path']}")
    
    if not info['installed']:
        print("\n=== 开始安装Playwright ===")
        ensure_playwright_installed() 