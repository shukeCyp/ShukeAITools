# -*- coding: utf-8 -*-
"""
清影平台账号登录模块 - 获取Cookie
"""

import asyncio
import time
from playwright.async_api import async_playwright
from colorama import Fore, Style, init

# 初始化colorama
init()

async def login_and_get_cookie(headless=True):
    """
    登录清影平台并获取Cookie
    
    参数:
        headless: 是否无头模式运行
        
    返回:
        dict: {
            "code": 200/601/602/603,
            "data": Cookie字符串或None,
            "message": 状态信息
        }
    """
    print(f"{Fore.GREEN}开始登录清影平台获取Cookie...{Style.RESET_ALL}")
    
    playwright = None
    browser = None
    context = None
    page = None
    
    try:
        # 初始化浏览器
        print(f"{Fore.YELLOW}正在启动浏览器...{Style.RESET_ALL}")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"{Fore.GREEN}浏览器已启动{Style.RESET_ALL}")
        
        # 设置网络监听器，监听用户信息接口
        user_info_success = False
        user_nickname = None
        user_phone = None
        
        async def check_login_response(response):
            nonlocal user_info_success, user_nickname, user_phone
            
            # 监听用户信息接口
            if "chatglm.cn/chatglm/user-api/user/info" in response.url:
                try:
                    response_data = await response.json()
                    print(f"{Fore.CYAN}监听到用户信息接口响应: {response_data}{Style.RESET_ALL}")
                    
                    if response_data.get("status") == 0 and response_data.get("message") == "success":
                        result = response_data.get("result", {})
                        user_nickname = result.get("nickname")
                        user_phone = result.get("phone")
                        
                        if user_nickname and user_phone:
                            print(f"{Fore.GREEN}用户信息获取成功！昵称: {user_nickname}, 手机: {user_phone}{Style.RESET_ALL}")
                            user_info_success = True
                        else:
                            print(f"{Fore.RED}用户信息响应缺少必要信息（昵称或手机号）{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}用户信息获取失败，状态: {response_data.get('status')}, 消息: {response_data.get('message')}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}解析用户信息响应失败: {str(e)}{Style.RESET_ALL}")
        
        # 绑定响应监听器
        page.on("response", check_login_response)
        
        # 访问清影平台
        print(f"{Fore.GREEN}开始访问清影平台...{Style.RESET_ALL}")
        
        await page.goto('https://chatglm.cn/main/alltoolsdetail?lang=zh', timeout=60000)
        await asyncio.sleep(2)
        
        # 等待用户信息获取完成或超时（最多等待5分钟）
        max_wait_time = 300  # 5分钟
        start_time = time.time()
        
        while not user_info_success and (time.time() - start_time) < max_wait_time:
            await asyncio.sleep(1)
            
            # 检查页面是否已经跳转到其他页面（可能表示登录成功）
            current_url = page.url
            if current_url != 'https://chatglm.cn/main/alltoolsdetail?lang=zh':
                print(f"{Fore.YELLOW}页面已跳转到: {current_url}{Style.RESET_ALL}")
        
        if not user_info_success:
            print(f"{Fore.RED}等待用户信息获取超时（{max_wait_time}秒），未检测到用户信息响应{Style.RESET_ALL}")
            return {
                "code": 601,
                "data": None,
                "message": f"等待用户信息获取超时（{max_wait_time}秒）"
            }
        
        # 用户信息获取成功，等待10秒后获取Cookie
        print(f"{Fore.GREEN}用户信息获取完成！昵称: {user_nickname}, 手机: {user_phone}，等待10秒后获取Cookie...{Style.RESET_ALL}")
        await asyncio.sleep(10)
        
        # 获取Cookie
        print(f"{Fore.YELLOW}正在获取Cookie...{Style.RESET_ALL}")
        cookies = await context.cookies()
        
        if cookies:
            # 将Cookie转换为字符串格式
            cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            print(f"{Fore.GREEN}Cookie获取成功！共获取到 {len(cookies)} 个Cookie{Style.RESET_ALL}")
            return {
                "code": 200,
                "data": {
                    "nickname": user_nickname,
                    "phone": user_phone,
                    "cookies": cookie_string
                },
                "message": "登录成功"
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
import json
import os

# 使用示例
if __name__ == "__main__":
    async def test():
        result = await login_and_get_cookie(headless=False)
        
        if result["code"] == 200:
            print(f"{Fore.GREEN}Cookie获取成功: {result['data'][:100] if result['data'] else '无数据'}...{Style.RESET_ALL}")
            
            # 保存Cookie到文件
            try:
                cookies_file = os.path.join(os.path.dirname(__file__), "cookies.json")
                cookie_data = {
                    "timestamp": time.time(),
                    "cookies": result['data']
                }
                
                with open(cookies_file, 'w', encoding='utf-8') as f:
                    json.dump(cookie_data, f, ensure_ascii=False, indent=2)
                
                print(f"{Fore.GREEN}Cookie已保存到文件: {cookies_file}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}保存Cookie文件失败: {str(e)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Cookie获取失败: {result['message']}{Style.RESET_ALL}")
    
    # 运行测试
    asyncio.run(test())
