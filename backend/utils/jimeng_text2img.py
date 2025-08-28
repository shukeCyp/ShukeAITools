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

async def text2image(prompt, username, password, model="Image 3.1", aspect_ratio="1:1", quality="1K", headless=False, cookies=None):
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
        cookies: 登录后的cookies
    返回:
        dict: {
            "code": 200/601/602/603/604,
            "data": 图片URL列表或None,
            "message": 状态信息
        }
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
        # 初始化浏览器
        print(f"{Fore.YELLOW}正在启动浏览器...{Style.RESET_ALL}")
        config = get_browser_config()
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(**config)
        
        if cookies:
            # 处理cookies字符串格式
            # 将cookies字符串转换为字典列表格式
            cookie_pairs = cookies.split('; ')
            cookie_list = []
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    cookie_list.append({
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': '.capcut.com',
                        'path': '/'
                    })
            cookies = cookie_list
            
            await context.add_cookies(cookies)
            page = await context.new_page()
            print(f"{Fore.GREEN}已加载cookies{Style.RESET_ALL}")
        else: 
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
                return {
                    "code": 602,
                    "data": None,
                    "message": "登录失败，无法找到登录节点或页面跳转异常"
                }
            
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
        
        # 重试机制，最多尝试3次
        max_retries = 3
        ratio_selected = False
        
        for attempt in range(max_retries):
            try:
                print(f"{Fore.YELLOW}第 {attempt + 1} 次尝试选择比例...{Style.RESET_ALL}")
                
                # 点击比例选择按钮
                await page.click('button.lv-btn.lv-btn-secondary.lv-btn-size-default.lv-btn-shape-square:has([class*="button-text-"])')
                await asyncio.sleep(1)
                
                # 定义比例选项的映射（从比例值到索引位置）
                ratio_index_map = {
                    "21:9": 0,
                    "16:9": 1,
                    "3:2": 2,
                    "4:3": 3,
                    "1:1": 4,
                    "3:4": 5,
                    "2:3": 6,
                    "9:16": 7
                }
                
                # 获取对应比例的索引
                if aspect_ratio in ratio_index_map:
                    ratio_index = ratio_index_map[aspect_ratio]
                    # 在弹出的比例选择框中选择对应位置的比例选项
                    await page.click(f'div.lv-radio-group.radio-group-ME1Gqz label.lv-radio:nth-child({ratio_index + 1})')
                    await asyncio.sleep(1)
                else:
                    # 如果找不到对应的比例，抛出异常
                    raise Exception(f"不支持的比例: {aspect_ratio}")

                # 关闭选择
                await page.click('button.lv-btn.lv-btn-secondary.lv-btn-size-default.lv-btn-shape-square:has([class*="button-text-"])')
                await asyncio.sleep(1)
                
                # 检查是否选择成功 - 查找按钮中是否包含目标比例
                button_element = await page.query_selector('button.lv-btn.lv-btn-secondary.lv-btn-size-default.lv-btn-shape-square:has([class*="button-text-"])')
                if button_element:
                    button_text = await button_element.text_content()
                    if aspect_ratio in button_text:
                        print(f"{Fore.GREEN}比例选择成功: {aspect_ratio}{Style.RESET_ALL}")
                        ratio_selected = True
                        break
                    else:
                        print(f"{Fore.YELLOW}比例选择失败，当前显示: {button_text}，期望: {aspect_ratio}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}未找到比例按钮元素{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.YELLOW}第 {attempt + 1} 次选择比例时出错: {str(e)}{Style.RESET_ALL}")
                
            await asyncio.sleep(1)
        
        # 如果3次尝试都失败，返回错误
        if not ratio_selected:
            print(f"{Fore.RED}比例选择失败，已尝试 {max_retries} 次{Style.RESET_ALL}")
            return {
                "code": 602,
                "data": None,
                "message": f"比例选择失败，已尝试 {max_retries} 次"
            }
        

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
            return {
                "code": 603,
                "data": None,
                "message": "任务ID等待超时"
            }
            
        # 等待图片生成完成
        print(f"{Fore.YELLOW}已获取任务ID，等待图片生成完成...{Style.RESET_ALL}")
        max_wait_time = 3600
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
            return {
                "code": 200,
                "data": image_urls,
                "message": "图片生成成功"
            }
        else:
            print(f"{Fore.YELLOW}等待超时或未能获取图片URL，已等待 {time.time() - start_time:.1f} 秒{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}任务ID: {task_id or '未获取'}{Style.RESET_ALL}")
            return {
                "code": 604,
                "data": None,
                "message": "等待超时或未能获取图片URL"
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
        print(f"{Fore.RED}生成图片时出错: {error_msg}{Style.RESET_ALL}")
        
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
        prompt = "一只可爱的猫咪在阳光下玩耍"
        model = "Image 3.1"
        aspect_ratio = "1:1"
        quality = "1K"
        
        result = await text2image(prompt, username, password, model, aspect_ratio, quality, headless=False)
        
        if result["code"] == 200:
            print(f"{Fore.GREEN}生成成功，图片链接列表: {result['data']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}生成失败: {result['message']}{Style.RESET_ALL}")
    
    # 运行测试
    asyncio.run(test())