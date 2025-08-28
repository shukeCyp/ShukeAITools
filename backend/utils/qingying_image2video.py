"""
清影平台图生视频模块
"""

import asyncio
import time
import requests
import json
import base64
from playwright.async_api import async_playwright
from colorama import Fore, Style, init

# 初始化colorama
init()

async def generate_image_to_video(image_path, prompt="", cookie_string="", headless=True, generation_mode="fast", frame_rate="30", resolution="720p", duration="5s", ai_audio=False):
    """
    使用清影平台生成图生视频
    
    参数:
        image_path: 输入图片路径
        prompt: 视频生成提示词
        cookie_string: Cookie字符串
        headless: 是否无头模式运行
        generation_mode: 生成模式 ("fast"速度更快 或 "quality"质量更佳)
        frame_rate: 视频帧率 ("30" 或 "60")
        resolution: 视频分辨率 ("720p", "1080p" 或 "4k")
        duration: 视频时长 ("5s" 或 "10s")
        ai_audio: AI音效 (True开启 或 False关闭)
        
    返回:
        dict: {
            "code": 200/601/602/603/500,
            "data": 视频URL或None,
            "message": 状态信息
        }
    """
    print(f"{Fore.GREEN}开始使用清影平台生成图生视频...{Style.RESET_ALL}")
    
    playwright = None
    browser = None
    context = None
    page = None
    
    try:
        # 初始化浏览器
        print(f"{Fore.YELLOW}正在启动浏览器...{Style.RESET_ALL}")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        
        # 创建浏览器上下文并设置Cookie
        context = await browser.new_context()
        if cookie_string:
            # 解析Cookie字符串并设置到上下文
            cookies = []
            for cookie_item in cookie_string.split('; '):
                if '=' in cookie_item:
                    name, value = cookie_item.split('=', 1)
                    cookies.append({
                        'name': name,
                        'value': value,
                        'domain': '.chatglm.cn',
                        'path': '/'
                    })
            await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        print(f"{Fore.GREEN}浏览器已启动{Style.RESET_ALL}")
        
        # 访问清影平台图生视频页面
        print(f"{Fore.GREEN}开始访问清影图生视频页面...{Style.RESET_ALL}")
        await page.goto('https://chatglm.cn/video?lang=zh', timeout=60000)
        await asyncio.sleep(2)
        
        # 处理弹窗
        print(f"{Fore.YELLOW}正在检查并关闭弹窗...{Style.RESET_ALL}")
        
        # 等待页面加载完成
        await asyncio.sleep(3)
        
        # 检查并关闭第一个弹窗
        try:
            popup_selector1 = 'div[data-v-0f7edd1f].new-feature-content-btn.flex.flex-x-center.flex-y-center'
            popup_element1 = await page.wait_for_selector(popup_selector1, timeout=5000, state='visible')
            if popup_element1:
                await popup_element1.click()
                print(f"{Fore.GREEN}第一个弹窗已关闭{Style.RESET_ALL}")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"{Fore.YELLOW}第一个弹窗未出现或已关闭: {str(e)}{Style.RESET_ALL}")
        
        # 检查并关闭第二个弹窗
        try:
            popup_selector2 = 'div[data-v-3af8a7d3].btn'
            popup_element2 = await page.wait_for_selector(popup_selector2, timeout=5000, state='visible')
            if popup_element2:
                await popup_element2.click()
                print(f"{Fore.GREEN}第二个弹窗已关闭{Style.RESET_ALL}")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"{Fore.YELLOW}第二个弹窗未出现或已关闭: {str(e)}{Style.RESET_ALL}")
        
        # 点击图片上传按钮
        print(f"{Fore.YELLOW}正在查找图片上传按钮...{Style.RESET_ALL}")
        
        # 等待页面加载完成
        await asyncio.sleep(3)
        
        # 查找文件上传输入框
        upload_selector = 'input[type="file"][accept="image/*"]'
        await page.wait_for_selector(upload_selector, timeout=10000, state='attached')
        
        # 上传图片文件
        await page.set_input_files(upload_selector, image_path)
        print(f"{Fore.GREEN}图片上传成功: {image_path}{Style.RESET_ALL}")
        await asyncio.sleep(3)
        
        # 点击上传按钮
        print(f"{Fore.YELLOW}正在点击上传按钮...{Style.RESET_ALL}")
        upload_btn_selector = 'button[data-v-1507dd9a].btn_done'
        upload_btn = await page.wait_for_selector(upload_btn_selector, timeout=10000, state='visible')
        await upload_btn.click()
        print(f"{Fore.GREEN}已点击上传按钮{Style.RESET_ALL}")
        await asyncio.sleep(3)
        
        # 点击基础参数
        print(f"{Fore.YELLOW}正在点击基础参数...{Style.RESET_ALL}")
        basic_params_selector = 'div.prompt-item'
        basic_params = await page.wait_for_selector(basic_params_selector, timeout=10000, state='visible')
        await basic_params.click()
        print(f"{Fore.GREEN}已点击基础参数{Style.RESET_ALL}")
        await asyncio.sleep(2)
        
        # 设置生成模式
        print(f"{Fore.YELLOW}正在设置生成模式: {generation_mode}{Style.RESET_ALL}")
        
        # 生成模式选项映射表，按下标对应
        generation_mode_options = {
            "speed": 0,     # 第一个选项：速度更快（默认）
            "quality": 1    # 第二个选项：质量更佳
        }
        
        if generation_mode in generation_mode_options:
            target_index = generation_mode_options[generation_mode]
            try:
                # 直接通过CSS选择器定位生成模式选项
                print(f"{Fore.CYAN}正在定位生成模式选项...{Style.RESET_ALL}")
                
                # 先等待生成模式容器出现
                generation_mode_container = await page.wait_for_selector('div.style-item:has(span.text:text("生成模式"))', timeout=10000)
                
                # 获取所有生成模式选项
                generation_mode_items = await page.query_selector_all('div.style-item:has(span.text:text("生成模式")) .option-item')
                
                print(f"{Fore.CYAN}找到 {len(generation_mode_items)} 个生成模式选项{Style.RESET_ALL}")
                
                # 打印每个选项的详细信息用于调试
                for i, item in enumerate(generation_mode_items):
                    try:
                        # 获取选项的文本内容和class信息
                        text_content = await item.text_content()
                        class_list = await item.get_attribute('class')
                        print(f"{Fore.CYAN}选项 {i}: 文本='{text_content}', 类名='{class_list}'{Style.RESET_ALL}")
                    except Exception as debug_e:
                        print(f"{Fore.YELLOW}获取选项 {i} 信息失败: {debug_e}{Style.RESET_ALL}")
                
                if len(generation_mode_items) > target_index:
                    target_item = generation_mode_items[target_index]
                    
                    # 检查目标选项是否被禁用
                    class_list = await target_item.get_attribute('class')
                    if 'disabled' in class_list:
                        print(f"{Fore.YELLOW}{generation_mode}模式被禁用，无法选择{Style.RESET_ALL}")
                    else:
                        # 尝试点击目标选项
                        print(f"{Fore.CYAN}正在点击{generation_mode}模式（索引{target_index}）...{Style.RESET_ALL}")
                        await target_item.click()
                        await asyncio.sleep(2)
                        
                        # 验证是否成功选中
                        updated_class = await target_item.get_attribute('class')
                        print(f"{Fore.CYAN}点击后的类名: '{updated_class}'{Style.RESET_ALL}")
                        
                        if 'selected' in updated_class:
                            print(f"{Fore.GREEN}已成功设置生成模式为{generation_mode}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{generation_mode}模式点击后未显示为选中状态{Style.RESET_ALL}")
                            
                            # 尝试检查是否有其他元素被选中
                            for i, item in enumerate(generation_mode_items):
                                item_class = await item.get_attribute('class')
                                if 'selected' in item_class:
                                    item_text = await item.text_content()
                                    print(f"{Fore.CYAN}当前选中的是选项 {i}: '{item_text}'{Style.RESET_ALL}")
                                    break
                else:
                    print(f"{Fore.YELLOW}生成模式选项索引{target_index}超出范围（共{len(generation_mode_items)}个选项），使用默认设置{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}设置{generation_mode}生成模式时出错: {str(e)}{Style.RESET_ALL}")
                
                # 添加更详细的错误调试信息
                try:
                    # 尝试获取页面上所有生成模式相关的元素
                    all_generation_mode_elements = await page.query_selector_all('*:has-text("生成模式")')
                    print(f"{Fore.CYAN}页面上找到{len(all_generation_mode_elements)}个包含'生成模式'的元素{Style.RESET_ALL}")
                    
                    # 获取页面当前的HTML结构（仅生成模式部分）
                    generation_mode_html = await page.evaluate('''() => {
                        const elements = document.querySelectorAll('*');
                        for (let el of elements) {
                            if (el.textContent && el.textContent.includes('生成模式')) {
                                return el.outerHTML;
                            }
                        }
                        return '未找到生成模式元素';
                    }''')
                    print(f"{Fore.CYAN}生成模式区域HTML结构: {generation_mode_html[:500]}...{Style.RESET_ALL}")
                    
                except Exception as debug_e:
                    print(f"{Fore.YELLOW}调试信息获取失败: {debug_e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}使用默认的速度更快模式{Style.RESET_ALL}")
        await asyncio.sleep(1)
        
        # 设置帧率
        print(f"{Fore.YELLOW}正在设置视频帧率: {frame_rate}FPS{Style.RESET_ALL}")
        
        # 帧率选项映射表，按下标对应
        frame_rate_options = {
            "30": 0,    # 第一个选项：帧率30（默认）
            "60": 1     # 第二个选项：帧率60
        }
        
        if frame_rate in frame_rate_options:
            target_index = frame_rate_options[frame_rate]
            try:
                # 直接通过CSS选择器定位帧率选项
                print(f"{Fore.CYAN}正在定位帧率选项...{Style.RESET_ALL}")
                
                # 先等待帧率容器出现
                frame_rate_container = await page.wait_for_selector('div.style-item:has(span.text:text("视频帧率"))', timeout=10000)
                
                # 获取所有帧率选项
                frame_rate_items = await page.query_selector_all('div.style-item:has(span.text:text("视频帧率")) .option-item')
                
                print(f"{Fore.CYAN}找到 {len(frame_rate_items)} 个帧率选项{Style.RESET_ALL}")
                
                # 打印每个选项的详细信息用于调试
                for i, item in enumerate(frame_rate_items):
                    try:
                        # 获取选项的文本内容和class信息
                        text_content = await item.text_content()
                        class_list = await item.get_attribute('class')
                        print(f"{Fore.CYAN}选项 {i}: 文本='{text_content}', 类名='{class_list}'{Style.RESET_ALL}")
                    except Exception as debug_e:
                        print(f"{Fore.YELLOW}获取选项 {i} 信息失败: {debug_e}{Style.RESET_ALL}")
                
                if len(frame_rate_items) > target_index:
                    target_item = frame_rate_items[target_index]
                    
                    # 检查目标选项是否被禁用
                    class_list = await target_item.get_attribute('class')
                    if 'disabled' in class_list:
                        print(f"{Fore.YELLOW}{frame_rate}FPS被禁用，无法选择{Style.RESET_ALL}")
                    else:
                        # 尝试点击目标选项
                        print(f"{Fore.CYAN}正在点击{frame_rate}FPS选项（索引{target_index}）...{Style.RESET_ALL}")
                        await target_item.click()
                        await asyncio.sleep(2)
                        
                        # 验证是否成功选中
                        updated_class = await target_item.get_attribute('class')
                        print(f"{Fore.CYAN}点击后的类名: '{updated_class}'{Style.RESET_ALL}")
                        
                        if 'selected' in updated_class:
                            print(f"{Fore.GREEN}已成功设置帧率为{frame_rate}FPS{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{frame_rate}FPS选项点击后未显示为选中状态{Style.RESET_ALL}")
                            
                            # 尝试检查是否有其他元素被选中
                            for i, item in enumerate(frame_rate_items):
                                item_class = await item.get_attribute('class')
                                if 'selected' in item_class:
                                    item_text = await item.text_content()
                                    print(f"{Fore.CYAN}当前选中的是选项 {i}: '{item_text}'{Style.RESET_ALL}")
                                    break
                else:
                    print(f"{Fore.YELLOW}帧率选项索引{target_index}超出范围（共{len(frame_rate_items)}个选项），使用默认设置{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}设置{frame_rate}FPS时出错: {str(e)}{Style.RESET_ALL}")
                
                # 添加更详细的错误调试信息
                try:
                    # 尝试获取页面上所有帧率相关的元素
                    all_frame_rate_elements = await page.query_selector_all('*:has-text("视频帧率")')
                    print(f"{Fore.CYAN}页面上找到{len(all_frame_rate_elements)}个包含'视频帧率'的元素{Style.RESET_ALL}")
                    
                    # 获取页面当前的HTML结构（仅帧率部分）
                    frame_rate_html = await page.evaluate('''() => {
                        const elements = document.querySelectorAll('*');
                        for (let el of elements) {
                            if (el.textContent && el.textContent.includes('视频帧率')) {
                                return el.outerHTML;
                            }
                        }
                        return '未找到视频帧率元素';
                    }''')
                    print(f"{Fore.CYAN}帧率区域HTML结构: {frame_rate_html[:500]}...{Style.RESET_ALL}")
                    
                except Exception as debug_e:
                    print(f"{Fore.YELLOW}调试信息获取失败: {debug_e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}使用默认的30FPS{Style.RESET_ALL}")
        await asyncio.sleep(1)
        
        # 设置分辨率
        print(f"{Fore.YELLOW}正在设置视频分辨率: {resolution}{Style.RESET_ALL}")
        
        # 分辨率选项映射表，按下标对应
        resolution_options = {
            "720p": 0,  # 第一个选项：720P（默认）
            "1080p": 1,  # 第二个选项：1080P
            "4k": 2     # 第三个选项：4K
        }
        
        if resolution in resolution_options:
            target_index = resolution_options[resolution]
            try:
                # 直接通过CSS选择器定位分辨率选项
                print(f"{Fore.CYAN}正在定位分辨率选项...{Style.RESET_ALL}")
                
                # 先等待分辨率容器出现
                resolution_container = await page.wait_for_selector('div.style-item:has(span.text:text("视频分辨率"))', timeout=10000)
                
                # 获取所有分辨率选项
                resolution_items = await page.query_selector_all('div.style-item:has(span.text:text("视频分辨率")) .option-item')
                
                print(f"{Fore.CYAN}找到 {len(resolution_items)} 个分辨率选项{Style.RESET_ALL}")
                
                # 打印每个选项的详细信息用于调试
                for i, item in enumerate(resolution_items):
                    try:
                        # 获取选项的文本内容和class信息
                        text_content = await item.text_content()
                        class_list = await item.get_attribute('class')
                        print(f"{Fore.CYAN}选项 {i}: 文本='{text_content}', 类名='{class_list}'{Style.RESET_ALL}")
                    except Exception as debug_e:
                        print(f"{Fore.YELLOW}获取选项 {i} 信息失败: {debug_e}{Style.RESET_ALL}")
                
                if len(resolution_items) > target_index:
                    target_item = resolution_items[target_index]
                    
                    # 检查目标选项是否被禁用
                    class_list = await target_item.get_attribute('class')
                    if 'disabled' in class_list:
                        print(f"{Fore.YELLOW}{resolution}选项被禁用，无法选择{Style.RESET_ALL}")
                    else:
                        # 尝试点击目标选项
                        print(f"{Fore.CYAN}正在点击{resolution}选项（索引{target_index}）...{Style.RESET_ALL}")
                        await target_item.click()
                        await asyncio.sleep(2)
                        
                        # 验证是否成功选中
                        updated_class = await target_item.get_attribute('class')
                        print(f"{Fore.CYAN}点击后的类名: '{updated_class}'{Style.RESET_ALL}")
                        
                        if 'selected' in updated_class:
                            print(f"{Fore.GREEN}已成功设置分辨率为{resolution}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{resolution}选项点击后未显示为选中状态{Style.RESET_ALL}")
                            
                            # 尝试检查是否有其他元素被选中
                            for i, item in enumerate(resolution_items):
                                item_class = await item.get_attribute('class')
                                if 'selected' in item_class:
                                    item_text = await item.text_content()
                                    print(f"{Fore.CYAN}当前选中的是选项 {i}: '{item_text}'{Style.RESET_ALL}")
                                    break
                else:
                    print(f"{Fore.YELLOW}分辨率选项索引{target_index}超出范围（共{len(resolution_items)}个选项），使用默认设置{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}设置{resolution}分辨率时出错: {str(e)}{Style.RESET_ALL}")
                
                # 添加更详细的错误调试信息
                try:
                    # 尝试获取页面上所有分辨率相关的元素
                    all_resolution_elements = await page.query_selector_all('*:has-text("视频分辨率")')
                    print(f"{Fore.CYAN}页面上找到{len(all_resolution_elements)}个包含'视频分辨率'的元素{Style.RESET_ALL}")
                    
                    # 获取页面当前的HTML结构（仅分辨率部分）
                    resolution_html = await page.evaluate('''() => {
                        const elements = document.querySelectorAll('*');
                        for (let el of elements) {
                            if (el.textContent && el.textContent.includes('视频分辨率')) {
                                return el.outerHTML;
                            }
                        }
                        return '未找到视频分辨率元素';
                    }''')
                    print(f"{Fore.CYAN}分辨率区域HTML结构: {resolution_html[:500]}...{Style.RESET_ALL}")
                    
                except Exception as debug_e:
                    print(f"{Fore.YELLOW}调试信息获取失败: {debug_e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}使用默认的720P分辨率{Style.RESET_ALL}")
        await asyncio.sleep(1)

        # 设置视频时长
        print(f"{Fore.YELLOW}正在设置视频时长: {duration}{Style.RESET_ALL}")
        
        # 时长选项映射表，按下标对应
        duration_options = {
            "5s": 0,    # 第一个选项：5秒（默认）
            "10s": 1    # 第二个选项：10秒
        }
        
        if duration in duration_options:
            target_index = duration_options[duration]
            try:
                # 先点击时长选择按钮（第二个节点）
                print(f"{Fore.CYAN}正在点击时长选择按钮...{Style.RESET_ALL}")
                duration_button_selector = 'div.options div.prompt-item:nth-child(2)'
                duration_button = await page.wait_for_selector(duration_button_selector, timeout=10000, state='visible')
                await duration_button.click()
                await asyncio.sleep(1)
                
                # 等待弹窗出现并获取所有时长选项
                print(f"{Fore.CYAN}正在定位时长选项...{Style.RESET_ALL}")
                duration_items = await page.query_selector_all('div.duration-item')
                
                print(f"{Fore.CYAN}找到 {len(duration_items)} 个时长选项{Style.RESET_ALL}")
                
                # 打印每个选项的详细信息用于调试
                for i, item in enumerate(duration_items):
                    try:
                        # 获取选项的文本内容和class信息
                        text_content = await item.text_content()
                        class_list = await item.get_attribute('class')
                        print(f"{Fore.CYAN}选项 {i}: 文本='{text_content}', 类名='{class_list}'{Style.RESET_ALL}")
                    except Exception as debug_e:
                        print(f"{Fore.YELLOW}获取选项 {i} 信息失败: {debug_e}{Style.RESET_ALL}")
                
                if len(duration_items) > target_index:
                    target_item = duration_items[target_index]
                    
                    # 检查目标选项是否被禁用
                    class_list = await target_item.get_attribute('class')
                    if 'disabled' in class_list:
                        print(f"{Fore.YELLOW}{duration}时长被禁用，无法选择{Style.RESET_ALL}")
                    else:
                        # 尝试点击目标选项
                        print(f"{Fore.CYAN}正在点击{duration}时长选项（索引{target_index}）...{Style.RESET_ALL}")
                        await target_item.click()
                        await asyncio.sleep(2)
                        
                        # 验证是否成功选中
                        updated_class = await target_item.get_attribute('class')
                        print(f"{Fore.CYAN}点击后的类名: '{updated_class}'{Style.RESET_ALL}")
                        
                        if 'selected' in updated_class or 'disabled' not in updated_class:
                            print(f"{Fore.GREEN}已成功设置视频时长为{duration}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{duration}时长选项点击后未显示为选中状态{Style.RESET_ALL}")
                            
                            # 尝试检查是否有其他元素被选中
                            for i, item in enumerate(duration_items):
                                item_class = await item.get_attribute('class')
                                if 'selected' in item_class or ('disabled' not in item_class and i == 0):
                                    item_text = await item.text_content()
                                    print(f"{Fore.CYAN}当前选中的是选项 {i}: '{item_text}'{Style.RESET_ALL}")
                                    break
                else:
                    print(f"{Fore.YELLOW}时长选项索引{target_index}超出范围（共{len(duration_items)}个选项），使用默认设置{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}设置{duration}时长时出错: {str(e)}{Style.RESET_ALL}")
                
                # 添加更详细的错误调试信息
                try:
                    # 尝试获取页面上所有时长相关的元素
                    all_duration_elements = await page.query_selector_all('*:has-text("生成时长")')
                    print(f"{Fore.CYAN}页面上找到{len(all_duration_elements)}个包含'生成时长'的元素{Style.RESET_ALL}")
                    
                    # 获取页面当前的HTML结构（仅时长部分）
                    duration_html = await page.evaluate('''() => {
                        const elements = document.querySelectorAll('*');
                        for (let el of elements) {
                            if (el.textContent && el.textContent.includes('生成时长')) {
                                return el.outerHTML;
                            }
                        }
                        return '未找到生成时长元素';
                    }''')
                    print(f"{Fore.CYAN}时长区域HTML结构: {duration_html[:500]}...{Style.RESET_ALL}")
                    
                except Exception as debug_e:
                    print(f"{Fore.YELLOW}调试信息获取失败: {debug_e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}使用默认的5秒时长{Style.RESET_ALL}")
        await asyncio.sleep(1)
        
        # 设置AI音效
        print(f"{Fore.YELLOW}正在设置AI音效: {'开启' if ai_audio else '关闭'}{Style.RESET_ALL}")
        
        try:
            # 先点击AI音效按钮来打开选项弹窗
            ai_audio_button_selector = 'div.prompt-item:has-text("AI音效")'
            ai_audio_button = await page.wait_for_selector(ai_audio_button_selector, timeout=10000, state='visible')
            await ai_audio_button.click()
            print(f"{Fore.CYAN}已点击AI音效按钮，等待选项弹窗...{Style.RESET_ALL}")
            await asyncio.sleep(2)
            
            # 等待选项弹窗出现，使用更具体的选择器
            popover_selector = '.el-popper.options_popover[aria-hidden="false"]'
            await page.wait_for_selector(popover_selector, timeout=5000, state='visible')
            print(f"{Fore.CYAN}AI音效选项弹窗已出现{Style.RESET_ALL}")
            
            if ai_audio:
                # 选择"开启"选项 - 使用更精确的选择器
                enable_option_selector = '.el-popper.options_popover[aria-hidden="false"] .duration-item:has(.title-wrap:has-text("开启"))'
                enable_option = await page.wait_for_selector(enable_option_selector, timeout=5000, state='visible')
                await enable_option.click()
                print(f"{Fore.GREEN}已选择开启AI音效{Style.RESET_ALL}")
            else:
                # 选择"关闭"选项 - 使用更精确的选择器
                disable_option_selector = '.el-popper.options_popover[aria-hidden="false"] .duration-item:has(.title-wrap:has-text("关闭"))'
                disable_option = await page.wait_for_selector(disable_option_selector, timeout=5000, state='visible')
                await disable_option.click()
                print(f"{Fore.GREEN}已选择关闭AI音效{Style.RESET_ALL}")
                
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"{Fore.RED}设置AI音效时出错: {str(e)}{Style.RESET_ALL}")
            
            # 添加调试信息
            try:
                # 检查是否能找到AI音效按钮
                ai_audio_buttons = await page.query_selector_all('*:has-text("AI音效")')
                print(f"{Fore.CYAN}页面上找到{len(ai_audio_buttons)}个包含'AI音效'的元素{Style.RESET_ALL}")
                
                # 检查所有弹窗状态
                all_popovers = await page.query_selector_all('.el-popper.options_popover')
                print(f"{Fore.CYAN}找到{len(all_popovers)}个选项弹窗{Style.RESET_ALL}")
                
                for i, popover in enumerate(all_popovers):
                    aria_hidden = await popover.get_attribute('aria-hidden')
                    print(f"{Fore.CYAN}弹窗{i}: aria-hidden='{aria_hidden}'{Style.RESET_ALL}")
                
                # 获取AI音效相关的HTML结构
                ai_audio_html = await page.evaluate('''() => {
                    const elements = document.querySelectorAll('*');
                    for (let el of elements) {
                        if (el.textContent && el.textContent.includes('AI音效')) {
                            return el.outerHTML;
                        }
                    }
                    return '未找到AI音效元素';
                }''')
                print(f"{Fore.CYAN}AI音效区域HTML结构: {ai_audio_html[:500]}...{Style.RESET_ALL}")
                
            except Exception as debug_e:
                print(f"{Fore.YELLOW}调试信息获取失败: {debug_e}{Style.RESET_ALL}")

        # 在设置完AI音效后，输入提示词
        # 检查是否需要输入提示词
        if prompt and prompt.strip():
            try:
                print(f"{Fore.CYAN}开始输入提示词...{Style.RESET_ALL}")
                
                # 查找提示词输入框
                prompt_textarea_selector = 'textarea.prompt.scroll-display-none[placeholder*="通过上传图片或输入描述，创造你的视频"]'
                prompt_textarea = await page.wait_for_selector(prompt_textarea_selector, timeout=10000, state='visible')
                
                if prompt_textarea:
                    # 清空输入框并输入提示词
                    await prompt_textarea.click()
                    await prompt_textarea.fill('')  # 清空现有内容
                    
                    # 输入提示词
                    await prompt_textarea.type(prompt, delay=50)
                    
                    print(f"{Fore.GREEN}已成功输入提示词: {prompt}{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                else:
                    print(f"{Fore.YELLOW}未找到提示词输入框{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}输入提示词时出错: {str(e)}{Style.RESET_ALL}")
                
                # 添加调试信息
                try:
                    # 查找所有textarea元素
                    all_textareas = await page.query_selector_all('textarea')
                    print(f"{Fore.CYAN}页面上找到{len(all_textareas)}个textarea元素{Style.RESET_ALL}")
                    
                    for i, textarea in enumerate(all_textareas):
                        placeholder = await textarea.get_attribute('placeholder')
                        class_name = await textarea.get_attribute('class')
                        print(f"{Fore.CYAN}Textarea {i}: placeholder='{placeholder}', class='{class_name}'{Style.RESET_ALL}")
                    
                except Exception as debug_e:
                    print(f"{Fore.YELLOW}调试信息获取失败: {debug_e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}提示词为空，跳过输入提示词步骤{Style.RESET_ALL}")
        
        # 设置网络请求监听 - 在浏览器上下文级别监听
        chat_id = None
        video_result = None
        
        async def handle_request(request):
            nonlocal chat_id
            if 'video-api/v1/chat' in request.url and request.method == 'POST':
                print(f"{Fore.CYAN}检测到生成请求: {request.url}{Style.RESET_ALL}")
                
        async def handle_response(response):
            nonlocal chat_id, video_result
            try:
                if 'video-api/v1/chat' in response.url and response.request.method == 'POST':
                    response_text = await response.text()
                    print(f"{Fore.CYAN}收到生成响应: {response_text}{Style.RESET_ALL}")
                    response_data = json.loads(response_text)
                    if response_data.get('status') == 0 and 'result' in response_data:
                        chat_id = response_data['result'].get('chat_id')
                        print(f"{Fore.GREEN}获取到chat_id: {chat_id}{Style.RESET_ALL}")
                
                # 监听状态更新请求
                if chat_id and f'video-api/v1/chat/status/{chat_id}' in response.url:
                    response_text = await response.text()
                    status_data = json.loads(response_text)
                    
                    if status_data.get('status') == 0 and 'result' in status_data:
                        result = status_data['result']
                        status = result.get('status')
                        plan = result.get('plan', '')
                        msg = result.get('msg', '')
                        
                        print(f"{Fore.CYAN}生成状态: {status}, 进度: {plan}, 消息: {msg}{Style.RESET_ALL}")
                        
                        if status == 'finished':
                            video_url = result.get('video_url', '')
                            if video_url:
                                print(f"{Fore.GREEN}视频生成成功！{Style.RESET_ALL}")
                                print(f"{Fore.GREEN}视频URL: {video_url}{Style.RESET_ALL}")
                                video_result = {
                                    "code": 200,
                                    "data": {
                                        "video_url": video_url,
                                        "cover_url": result.get('cover_url', ''),
                                        "chat_id": chat_id,
                                        "duration": result.get('video_duration', ''),
                                        "resolution": result.get('video_resolution', ''),
                                        "fps": result.get('video_fps', ''),
                                        "containing_audio_url": result.get('containing_audio_url', '')
                                    },
                                    "message": "视频生成成功"
                                }
                            else:
                                print(f"{Fore.RED}生成完成但未获取到视频URL{Style.RESET_ALL}")
                                video_result = {
                                    "code": 603,
                                    "data": None,
                                    "message": "生成完成但未获取到视频URL"
                                }
                        elif status == 'failed' or status == 'error':
                            print(f"{Fore.RED}视频生成失败: {msg}{Style.RESET_ALL}")
                            video_result = {
                                "code": 603,
                                "data": None,
                                "message": f"视频生成失败: {msg}"
                            }
                            
            except Exception as e:
                print(f"{Fore.YELLOW}解析响应时出错: {e}{Style.RESET_ALL}")
        
        # 在浏览器上下文级别设置监听器
        context.on('request', handle_request)
        context.on('response', handle_response)
        
        # 点击生成按钮开始视频生成
        try:
            print(f"{Fore.CYAN}正在查找生成按钮...{Style.RESET_ALL}")
            
            # 查找生成按钮，使用多个可能的选择器
            generate_button_selectors = [
                'div.btn-group svg[viewBox="0 0 10 10"]',  # 基于SVG的选择器
                'div.btn-group',  # 直接选择按钮组
                'button:has(svg[viewBox="0 0 10 10"])',  # 包含特定SVG的按钮
                '[class*="btn-group"]',  # 包含btn-group类的元素
                'div[data-v-2f067989].btn-group'  # 包含data-v属性的btn-group
            ]
            
            generate_button = None
            for selector in generate_button_selectors:
                try:
                    generate_button = await page.wait_for_selector(selector, timeout=5000, state='visible')
                    if generate_button:
                        print(f"{Fore.GREEN}找到生成按钮，使用选择器: {selector}{Style.RESET_ALL}")
                        break
                except:
                    continue
            
            if not generate_button:
                print(f"{Fore.YELLOW}使用通用方法查找生成按钮...{Style.RESET_ALL}")
                # 如果上述选择器都没找到，尝试通过文本或其他方式查找
                generate_button = await page.query_selector('button:has-text("生成")')
                if not generate_button:
                    generate_button = await page.query_selector('[role="button"]:has(svg)')
            
            if generate_button:
                # 确保按钮可点击
                await generate_button.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                
                # 点击生成按钮
                await generate_button.click()
                print(f"{Fore.GREEN}已点击生成按钮，开始视频生成...{Style.RESET_ALL}")
                
                # 等待获取chat_id
                timeout_count = 0
                while chat_id is None and timeout_count < 30:  # 等待30秒
                    await asyncio.sleep(1)
                    timeout_count += 1
                
                if chat_id is None:
                    print(f"{Fore.RED}未能获取到chat_id{Style.RESET_ALL}")
                    return {
                        "code": 602,
                        "data": None,
                        "message": "未能获取到chat_id"
                    }
                
                print(f"{Fore.GREEN}成功获取chat_id: {chat_id}，开始监听生成状态...{Style.RESET_ALL}")
                
                # 等待视频生成完成
                max_wait_time = 3600  # 最大等待1小时
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    if video_result is not None:
                        return video_result
                    
                    await asyncio.sleep(1)
                
                # 超时
                print(f"{Fore.RED}视频生成超时（超过{max_wait_time}秒）{Style.RESET_ALL}")
                return {
                    "code": 601,
                    "data": None,
                    "message": f"视频生成超时（超过{max_wait_time}秒）"
                }
                
            else:
                print(f"{Fore.RED}未找到生成按钮{Style.RESET_ALL}")
                
                # 调试信息：显示页面上的所有按钮
                try:
                    all_buttons = await page.query_selector_all('button, div[role="button"], [class*="btn"]')
                    print(f"{Fore.CYAN}页面上找到{len(all_buttons)}个按钮元素{Style.RESET_ALL}")
                    
                    for i, button in enumerate(all_buttons[:10]):  # 只显示前10个
                        text_content = await button.text_content()
                        class_name = await button.get_attribute('class')
                        print(f"{Fore.CYAN}按钮 {i}: text='{text_content}', class='{class_name}'{Style.RESET_ALL}")
                        
                except Exception as debug_e:
                    print(f"{Fore.YELLOW}调试信息获取失败: {debug_e}{Style.RESET_ALL}")
                
                return {
                    "code": 602,
                    "data": None,
                    "message": "未找到生成按钮"
                }
                
        except Exception as e:
            print(f"{Fore.RED}点击生成按钮时出错: {str(e)}{Style.RESET_ALL}")
            return {
                "code": 500,
                "data": None,
                "message": f"点击生成按钮失败: {str(e)}"
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
        print(f"{Fore.RED}图生视频时出错: {error_msg}{Style.RESET_ALL}")
        
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
        image_path = "/Users/chaiyapeng/Downloads/task_80_image_2.jpg"
        prompt = "生成一个美丽的风景视频"
        # 从cookies.json文件读取cookie
        try:
            with open("cookies.json", "r", encoding="utf-8") as f:
                cookie_string = f.read().strip()
        except FileNotFoundError:
            cookie_string = ""
            print(f"{Fore.YELLOW}未找到cookies.json文件{Style.RESET_ALL}")
        except Exception as e:
            cookie_string = ""
            print(f"{Fore.RED}读取cookies.json时出错: {str(e)}{Style.RESET_ALL}")
        # 调用图生视频函数，包含所有参数
        result = await generate_image_to_video(
            image_path=image_path,
            prompt=prompt,
            cookie_string=cookie_string,
            headless=False,
            generation_mode="quality",  # 生成模式：fast 或 quality
            frame_rate="60",           # 帧率：30 或 60
            resolution="1080p",        # 分辨率：720p、1080p 或 4k
            duration="10s",            # 时长：5s 或 10s
            ai_audio=True              # AI音效：True 或 False
        )
        
        if result["code"] == 200:
            print(f"{Fore.GREEN}图生视频成功: {result['data']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}图生视频失败: {result['message']}{Style.RESET_ALL}")
    
    # 运行测试
    asyncio.run(test())