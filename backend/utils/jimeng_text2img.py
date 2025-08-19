"""
即梦平台自动化模块 - 文本生成图片
"""

import os
import asyncio
import time
import subprocess
import json
from playwright.async_api import async_playwright
from colorama import Fore, Style, init

# 初始化colorama
init()

async def check_playwright_browsers():
    """检查Playwright浏览器是否已安装，如果没有则安装"""
    try:
        print(f"{Fore.YELLOW}检查Playwright浏览器是否已安装...{Style.RESET_ALL}")
        result = subprocess.run(
            ["playwright", "install", "chromium"], 
            capture_output=True, 
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}Playwright浏览器已正确安装{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}正在安装Playwright浏览器...{Style.RESET_ALL}")
            subprocess.run(["playwright", "install"], check=True)
            print(f"{Fore.GREEN}Playwright浏览器安装完成{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}安装Playwright浏览器时出错: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}请手动运行: playwright install{Style.RESET_ALL}")
        return False
    
    return True
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

async def text2image(prompt, username, password, model="Image 3.1", aspect_ratio="1:1", quality="1K", headless=False):
    """
    生成文本到图片
    
    参数:
        prompt: 文本提示词
        username: 登录用户名
        password: 登录密码
        model: 使用的模型
        aspect_ratio: 图片比例（如 "1:1", "16:9", "4:3"等）
        quality: 图片清晰度
        headless: 是否无头模式运行
        
    返回:
        list: 成功时返回图片URL列表，失败时返回None
    """
    print(f"{Fore.GREEN}开始自动生成文本到图片...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}提示词: {Style.RESET_ALL}{prompt}")
    print(f"{Fore.CYAN}模型: {Style.RESET_ALL}{model}")
    print(f"{Fore.CYAN}比例: {Style.RESET_ALL}{aspect_ratio}")
    print(f"{Fore.CYAN}清晰度: {Style.RESET_ALL}{quality}")
    
    playwright = None
    browser = None
    context = None
    page = None
    
    try:
        # 检查浏览器
        if not await check_playwright_browsers():
            return None
            
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
        print(f"{Fore.CYAN}账号: {Style.RESET_ALL}{username}")
        
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
            return None
        
        # 跳转到AI工具生成页面
        print(f"{Fore.YELLOW}正在跳转到AI工具生成页面...{Style.RESET_ALL}")
        await page.goto('https://dreamina.capcut.com/ai-tool/generate')
        await page.wait_for_load_state('networkidle', timeout=60000)
        await asyncio.sleep(2)
        print(f"{Fore.GREEN}已跳转到AI工具页面{Style.RESET_ALL}")
        
        # 设置请求监听器
        task_id = None
        image_urls = []
        
        async def handle_response(response):
            nonlocal task_id, image_urls
            
            if "aigc_draft/generate" in response.url:
                try:
                    data = await response.json()
                    print(f"{Fore.GREEN}监测到生成请求响应...{Style.RESET_ALL}")
                    if data.get("ret") == "0" and "data" in data and "aigc_data" in data["data"]:
                        task_id = data["data"]["aigc_data"]["task"]["task_id"]
                        print(f"{Fore.GREEN}获取到任务ID: {task_id}{Style.RESET_ALL}")
                except:
                    pass
            
            if "/v1/get_asset_list" in response.url and task_id:
                try:
                    data = await response.json()
                    if "data" in data and "asset_list" in data["data"]:
                        asset_list = data["data"]["asset_list"]
                        for asset in asset_list:
                            if "id" in asset and asset.get("id") == task_id:
                                if "image" in asset and asset["image"].get("finish_time", 0) != 0:
                                    try:
                                        image_urls = []
                                        for i in range(4):
                                            try:
                                                url = asset["image"]["item_list"][i]["image"]["large_images"][0]["image_url"]
                                                image_urls.append(url)
                                            except (KeyError, IndexError):
                                                print(f"{Fore.YELLOW}无法获取第{i+1}张图片URL{Style.RESET_ALL}")
                                        
                                        if image_urls:
                                            print(f"{Fore.GREEN}图片生成完成! 共获取到{len(image_urls)}张图片{Style.RESET_ALL}")
                                            for i, url in enumerate(image_urls):
                                                print(f"{Fore.GREEN}图片{i+1} URL: {url}{Style.RESET_ALL}")
                                        else:
                                            print(f"{Fore.YELLOW}图片已完成但无法获取任何URL{Style.RESET_ALL}")
                                    except (KeyError, IndexError):
                                        print(f"{Fore.YELLOW}图片已完成但无法获取URL{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.YELLOW}图片生成尚未完成，继续等待...{Style.RESET_ALL}")
                except:
                    pass
        
        # 注册响应监听器
        page.on("response", handle_response)
        
        # 点击类型选择下拉框
        print(f"{Fore.YELLOW}点击类型选择下拉框...{Style.RESET_ALL}")
        await page.click('div.lv-select[role="combobox"][class*="type-select-"]')
        await asyncio.sleep(1)
        
        # 选择AI Image选项
        print(f"{Fore.YELLOW}选择AI Image选项...{Style.RESET_ALL}")
        await page.click('span.lv-select-view-value:has-text("AI Image")')
        await asyncio.sleep(2)
        
        # 输入提示词
        print(f"{Fore.YELLOW}输入提示词...{Style.RESET_ALL}")
        await page.fill('textarea.lv-textarea[placeholder="Describe the image you\'re imagining"]', prompt)
        await asyncio.sleep(2)
        
        # 选择模型
        print(f"{Fore.YELLOW}选择模型: {model}...{Style.RESET_ALL}")
        await page.click('div.lv-select[role="combobox"]:not([class*="type-select-"])')
        await asyncio.sleep(1)
        
        # 等待下拉菜单完全加载
        await page.wait_for_selector('div.lv-select-popup-inner[role="listbox"]', timeout=5000)
        await asyncio.sleep(1)
        
        # 查找并点击对应的模型选项
        try:
            option_elements = await page.query_selector_all('li[role="option"] [class*="option-label-"]')
            model_option_found = False
            
            for element in option_elements:
                text_content = await element.text_content()
                if model in text_content:
                    await element.click()
                    model_option_found = True
                    print(f"{Fore.GREEN}已选择模型: {model}{Style.RESET_ALL}")
                    break
            
            if not model_option_found:
                raise Exception("未找到模型选项")
                
        except Exception as e:
            print(f"{Fore.YELLOW}未找到指定模型 {model}，尝试通用选择方式: {str(e)}{Style.RESET_ALL}")
            await page.click(f'span[class*="select-option-label-content"]:has-text("{model}")')
        
        await asyncio.sleep(1)
        
        # 选择比例
        print(f"{Fore.YELLOW}选择比例: {aspect_ratio}...{Style.RESET_ALL}")
        await page.click('button.lv-btn.lv-btn-secondary.lv-btn-size-default.lv-btn-shape-square:has([class*="button-text-"])')
        await asyncio.sleep(1)
        
        # 在弹出的比例选择框中选择对应比例
        await page.click(f'span[class^="label-"]:has-text("{aspect_ratio}")')
        await asyncio.sleep(1)
        
        # 点击生成按钮
        print(f"{Fore.YELLOW}等待生成按钮可用并点击...{Style.RESET_ALL}")
        await page.wait_for_selector('button[class^="lv-btn lv-btn-primary"][class*="submit-button-"]:not(.lv-btn-disabled)', timeout=60000)
        await page.click('button[class^="lv-btn lv-btn-primary"][class*="submit-button-"]:not(.lv-btn-disabled)')
        print(f"{Fore.GREEN}已点击生成按钮，开始生成图片...{Style.RESET_ALL}")
        await asyncio.sleep(2)
        
        # 等待获取到任务ID
        print(f"{Fore.YELLOW}等待获取任务ID...{Style.RESET_ALL}")
        wait_task_id_time = 30
        task_id_start_time = time.time()
        
        while not task_id and time.time() - task_id_start_time < wait_task_id_time:
            elapsed = time.time() - task_id_start_time
            print(f"{Fore.YELLOW}等待任务ID中，已等待 {elapsed:.1f} 秒...{Style.RESET_ALL}")
            await asyncio.sleep(1)
        
        if not task_id:
            print(f"{Fore.RED}未能获取到任务ID，生成可能失败{Style.RESET_ALL}")
            return None
            
        # 等待图片生成完成
        print(f"{Fore.YELLOW}已获取任务ID，等待图片生成完成...{Style.RESET_ALL}")
        max_wait_time = 300
        start_time = time.time()
        
        while not image_urls and time.time() - start_time < max_wait_time:
            elapsed = time.time() - start_time
            print(f"{Fore.YELLOW}等待图片生成中，已等待 {elapsed:.1f} 秒...{Style.RESET_ALL}")
            await page.reload()
            print(f"{Fore.YELLOW}刷新页面，检查图片生成状态...{Style.RESET_ALL}")
            await asyncio.sleep(5)
        
        if image_urls:
            print(f"{Fore.GREEN}图片生成成功！总共用时 {time.time() - start_time:.1f} 秒{Style.RESET_ALL}")
            for i, url in enumerate(image_urls):
                print(f"{Fore.GREEN}图片{i+1} URL: {url}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}等待超时或未能获取图片URL，已等待 {time.time() - start_time:.1f} 秒{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}任务ID: {task_id or '未获取'}{Style.RESET_ALL}")
        
        return image_urls if image_urls else None
        
    except Exception as e:
        print(f"{Fore.RED}生成图片时出错: {str(e)}{Style.RESET_ALL}")
        return None
    
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
        prompt = "一只可爱的猫咪在阳光下玩耍"
        model = "Image 3.1"
        aspect_ratio = "1:1"
        quality = "1K"
        
        image_urls = await test2image(prompt, username, password, model, aspect_ratio, quality, headless=False)
        
        if image_urls:
            print(f"{Fore.GREEN}生成成功，图片链接列表: {image_urls}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}生成失败{Style.RESET_ALL}")
    
    # 运行测试
    asyncio.run(test())