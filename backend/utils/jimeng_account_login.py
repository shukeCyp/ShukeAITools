# -*- coding: utf-8 -*-
"""
即梦平台账号登录模块 - 获取Cookie
"""

import asyncio
import time
from playwright.async_api import async_playwright
from colorama import Fore, Style, init

# 初始化colorama
init()

def get_browser_config():
    """获取固定的浏览器配置"""
    print(f"{Fore.YELLOW}使用默认浏览器配置...{Style.RESET_ALL}")
    
    config = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "device_scale_factor": 1.0,
        "locale": "en-US",
        "timezone_id": "America/New_York"
    }
    
    print(f"{Fore.GREEN}浏览器配置已设置{Style.RESET_ALL}")
    
    return config

async def login_and_get_cookie(username, password, headless=True):
    """
    登录即梦平台并获取Cookie
    
    参数:
        username: 登录用户名
        password: 登录密码
        headless: 是否无头模式运行
        
    返回:
        dict: {
            "code": 200/601/602/603,
            "data": Cookie字符串或None,
            "message": 状态信息
        }
    """
    print(f"{Fore.GREEN}开始登录即梦平台获取Cookie...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}账号: {Style.RESET_ALL}{username}")
    
    playwright = None
    browser = None
    context = None
    page = None
    
    try:
        # 初始化浏览器
        print(f"{Fore.YELLOW}正在启动浏览器...{Style.RESET_ALL}")
        config = get_browser_config()
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(**config)
        page = await context.new_page()
        
        print(f"{Fore.GREEN}浏览器已启动{Style.RESET_ALL}")
        
        # 登录即梦平台
        print(f"{Fore.GREEN}开始登录即梦平台...{Style.RESET_ALL}")
        
        await page.goto('https://dreamina.capcut.com/en-us', timeout=60000)
        await asyncio.sleep(2)
        
        # 点击语言切换按钮
        print(f"{Fore.YELLOW}点击语言切换按钮...{Style.RESET_ALL}")
        await page.click('button.dreamina-header-secondary-button')
        await asyncio.sleep(1)
        
        # 点击切换为英文
        print(f"{Fore.YELLOW}切换为英文...{Style.RESET_ALL}")
        await page.click('div.language-item:has-text("English")')
        await asyncio.sleep(2)
        
        # 检查并关闭可能出现的弹窗
        try:
            print(f"{Fore.YELLOW}检查是否有弹窗需要关闭...{Style.RESET_ALL}")
            close_button = await page.query_selector('img.close-icon')
            if close_button:
                print(f"{Fore.YELLOW}关闭弹窗...{Style.RESET_ALL}")
                await close_button.click()
                await asyncio.sleep(1)
        except Exception as e:
            print(f"{Fore.YELLOW}没有发现需要关闭的弹窗: {str(e)}{Style.RESET_ALL}")
        
        # 点击登录按钮
        print(f"{Fore.YELLOW}点击登录按钮...{Style.RESET_ALL}")
        await page.click('#loginButton')
        await asyncio.sleep(2)
        
        # 等待登录页面加载
        await page.wait_for_selector('.lv-checkbox-mask', timeout=60000)
        await asyncio.sleep(2)
        
        # 勾选同意条款复选框
        print(f"{Fore.YELLOW}勾选同意条款...{Style.RESET_ALL}")
        await page.click('.lv-checkbox-mask')
        await asyncio.sleep(2)
        
        # 点击登录按钮
        await page.click('div[class^="login-button-"]:has-text("Sign in")')
        await asyncio.sleep(2)
        
        # 点击使用邮箱登录
        print(f"{Fore.YELLOW}选择邮箱登录方式...{Style.RESET_ALL}")
        await page.click('span.lv_new_third_part_sign_in_expand-label:has-text("Continue with Email")')
        await asyncio.sleep(2)
        
        # 输入账号密码
        print(f"{Fore.YELLOW}输入账号密码...{Style.RESET_ALL}")
        await page.fill('input[placeholder="Enter email"]', username)
        await asyncio.sleep(2)
        await page.fill('input[type="password"]', password)
        await asyncio.sleep(2)
        
        # 点击登录
        print(f"{Fore.YELLOW}点击登录按钮...{Style.RESET_ALL}")
        await page.click('.lv_new_sign_in_panel_wide-sign-in-button')
        await asyncio.sleep(2)
        
        # 等待登录完成
        print(f"{Fore.YELLOW}等待登录完成...{Style.RESET_ALL}")
        await page.wait_for_load_state('networkidle', timeout=60000)
        await asyncio.sleep(2)
        
        # 检查是否有确认按钮，如果有则点击
        print(f"{Fore.YELLOW}检查是否需要确认...{Style.RESET_ALL}")
        try:
            confirm_button = await page.query_selector('button:has-text("Confirm")')
            if confirm_button:
                print(f"{Fore.GREEN}检测到确认按钮，点击确认...{Style.RESET_ALL}")
                await confirm_button.click()
                await asyncio.sleep(2)
        except Exception as e:
            print(f"{Fore.YELLOW}没有确认按钮，跳过: {str(e)}{Style.RESET_ALL}")
        
        # 验证登录是否成功
        current_url = page.url
        if "dreamina.capcut.com" in current_url and "login" not in current_url:
            print(f"{Fore.GREEN}登录成功！{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}登录可能失败，当前URL: {current_url}{Style.RESET_ALL}")
            return {
                "code": 602,
                "data": None,
                "message": "登录失败，无法找到登录节点或页面跳转异常"
            }
        
        # 跳转到AI工具页面以确保完全登录
        print(f"{Fore.YELLOW}正在跳转到AI工具页面...{Style.RESET_ALL}")
        await page.goto('https://dreamina.capcut.com/ai-tool/generate')
        await page.wait_for_load_state('networkidle', timeout=60000)
        await asyncio.sleep(3)
        
        # 获取Cookie
        print(f"{Fore.YELLOW}正在获取Cookie...{Style.RESET_ALL}")
        cookies = await context.cookies()
        
        if cookies:
            # 将Cookie转换为字符串格式
            cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            print(f"{Fore.GREEN}Cookie获取成功！共获取到 {len(cookies)} 个Cookie{Style.RESET_ALL}")
            return {
                "code": 200,
                "data": cookie_string,
                "message": "Cookie获取成功"
            }
        else:
            print(f"{Fore.RED}未能获取到Cookie{Style.RESET_ALL}")
            return {
                "code": 603,
                "data": None,
                "message": "Cookie获取失败"
            }
        
    except asyncio.TimeoutError as e:
        print(f"{Fore.RED}Playwright等待超时: {str(e)}{Style.RESET_ALL}")
        return {
            "code": 601,
            "data": None,
            "message": f"Playwright等待超时: {str(e)}"
        }
    except Exception as e:
        error_msg = str(e)
        print(f"{Fore.RED}登录获取Cookie时出错: {error_msg}{Style.RESET_ALL}")
        
        # 根据错误信息判断错误类型
        if "selector" in error_msg.lower() or "element" in error_msg.lower() or "not found" in error_msg.lower():
            return {
                "code": 602,
                "data": None,
                "message": f"找不到页面节点: {error_msg}"
            }
        elif "timeout" in error_msg.lower():
            return {
                "code": 601,
                "data": None,
                "message": f"操作超时: {error_msg}"
            }
        else:
            return {
                "code": 500,
                "data": None,
                "message": f"未知错误: {error_msg}"
            }
    
    finally:
        # 关闭浏览器
        try:
            if browser:
                await browser.close()
                print(f"{Fore.GREEN}浏览器已关闭{Style.RESET_ALL}")
            if playwright:
                await playwright.stop()
        except Exception as e:
            print(f"{Fore.RED}关闭浏览器时出错: {str(e)}{Style.RESET_ALL}")

# 使用示例
if __name__ == "__main__":
    async def test():
        username = "hsabqiq2bqnr@maildrop.cc"
        password = "123456"
        
        result = await login_and_get_cookie(username, password, headless=False)
        
        if result["code"] == 200:
            print(f"{Fore.GREEN}Cookie获取成功: {result['data'][:100]}...{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Cookie获取失败: {result['message']}{Style.RESET_ALL}")
    
    # 运行测试
    asyncio.run(test())
