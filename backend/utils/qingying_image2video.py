"""
清影平台图生视频模块
based on BaseTaskExecutor refactoring version
"""

import asyncio
import time
import json
from typing import Optional, Dict, Any
from backend.utils.base_task_executor import BaseTaskExecutor, TaskResult, ErrorCode, TaskLogger

class QingyingImage2VideoExecutor(BaseTaskExecutor):
    """清影图生视频执行器"""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.chat_id = None
        self.video_result = None
    
    async def handle_cookies(self, cookies: str):
        """处理cookies字符串格式"""
        try:
            # 将cookies字符串转换为字典列表格式
            cookie_pairs = cookies.split('; ')
            cookie_list = []
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    cookie_list.append({
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': '.chatglm.cn',
                        'path': '/'
                    })
            
            await self.context.add_cookies(cookie_list)
            self.logger.info("清影平台cookies设置成功")
            
        except Exception as e:
            self.logger.error("设置清影平台cookies时出错", error=str(e))
    
    async def navigate_to_platform(self) -> TaskResult:
        """导航到清影平台"""
        try:
            self.logger.info("开始访问清影图生视频页面")
            await self.page.goto('https://chatglm.cn/video?lang=zh', timeout=60000)
            await asyncio.sleep(2)
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message="成功访问清影平台"
            )
        except Exception as e:
            self.logger.error("访问清影平台失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"访问清影平台失败: {str(e)}"
            )
    
    async def handle_popups(self) -> TaskResult:
        """处理弹窗"""
        try:
            self.logger.info("正在检查并关闭弹窗")
            
            # 等待页面加载完成
            await asyncio.sleep(3)
            
            # 检查并关闭第一个弹窗
            try:
                popup_selector1 = 'div.new-feature-content-btn.flex.flex-x-center.flex-y-center'
                popup_element1 = await self.page.wait_for_selector(popup_selector1, timeout=5000, state='visible')
                if popup_element1:
                    await popup_element1.click()
                    self.logger.info("第一个弹窗已关闭")
                    await asyncio.sleep(2)
            except Exception as e:
                self.logger.debug("第一个弹窗未出现或已关闭", error=str(e))
            
            # 检查并关闭第二个弹窗
            try:
                popup_selector2 = 'div[data-v-3af8a7d3].btn'
                popup_element2 = await self.page.wait_for_selector(popup_selector2, timeout=5000, state='visible')
                if popup_element2:
                    await popup_element2.click()
                    self.logger.info("第二个弹窗已关闭")
                    await asyncio.sleep(2)
            except Exception as e:
                self.logger.debug("第二个弹窗未出现或已关闭", error=str(e))
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message="弹窗处理完成"
            )
        except Exception as e:
            self.logger.error("处理弹窗失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"处理弹窗失败: {str(e)}"
            )
    
    async def upload_image(self, image_path: str) -> TaskResult:
        """上传图片"""
        try:
            self.logger.info("正在上传图片", image_path=image_path)
            
            # 等待页面加载完成
            await asyncio.sleep(3)
            
            # 查找文件上传输入框
            upload_selector = 'input[type="file"][accept="image/*"]'
            await self.page.wait_for_selector(upload_selector, timeout=10000, state='attached')
            
            # 上传图片文件
            await self.page.set_input_files(upload_selector, image_path)
            self.logger.info("图片上传成功", image_path=image_path)
            await asyncio.sleep(3)
            
            # 点击上传按钮
            self.logger.info("正在点击上传按钮")
            upload_btn_selector = 'button[data-v-1507dd9a].btn_done'
            upload_btn = await self.page.wait_for_selector(upload_btn_selector, timeout=10000, state='visible')
            await upload_btn.click()
            self.logger.info("已点击上传按钮")
            await asyncio.sleep(3)
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message="图片上传成功"
            )
        except Exception as e:
            self.logger.error("上传图片失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"上传图片失败: {str(e)}"
            )
    
    async def configure_basic_params(self) -> TaskResult:
        """配置基础参数"""
        try:
            self.logger.info("正在点击基础参数")
            basic_params_selector = 'div.prompt-item'
            basic_params = await self.page.wait_for_selector(basic_params_selector, timeout=10000, state='visible')
            await basic_params.click()
            self.logger.info("已点击基础参数")
            await asyncio.sleep(2)
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message="基础参数配置完成"
            )
        except Exception as e:
            self.logger.error("配置基础参数失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"配置基础参数失败: {str(e)}"
            )
    
    async def set_generation_mode(self, generation_mode: str) -> TaskResult:
        """设置生成模式"""
        try:
            self.logger.info("正在设置生成模式", generation_mode=generation_mode)
            
            # 生成模式选项映射表，按下标对应
            generation_mode_options = {
                "speed": 0,     # 第一个选项：速度更快（默认）
                "quality": 1    # 第二个选项：质量更佳
            }
            
            if generation_mode in generation_mode_options:
                target_index = generation_mode_options[generation_mode]
                try:
                    # 先等待生成模式容器出现
                    generation_mode_container = await self.page.wait_for_selector('div.style-item:has(span.text:text("生成模式"))', timeout=10000)
                    
                    # 获取所有生成模式选项
                    generation_mode_items = await self.page.query_selector_all('div.style-item:has(span.text:text("生成模式")) .option-item')
                    
                    self.logger.debug(f"找到 {len(generation_mode_items)} 个生成模式选项")
                    
                    if len(generation_mode_items) > target_index:
                        target_item = generation_mode_items[target_index]
                        
                        # 检查目标选项是否被禁用
                        class_list = await target_item.get_attribute('class')
                        if 'disabled' in class_list:
                            self.logger.warning(f"{generation_mode}模式被禁用，无法选择")
                        else:
                            # 尝试点击目标选项
                            await target_item.click()
                            await asyncio.sleep(2)
                            
                            # 验证是否成功选中
                            updated_class = await target_item.get_attribute('class')
                            if 'selected' in updated_class:
                                self.logger.info(f"已成功设置生成模式为{generation_mode}")
                            else:
                                self.logger.warning(f"{generation_mode}模式点击后未显示为选中状态")
                    else:
                        self.logger.warning(f"生成模式选项索引{target_index}超出范围，使用默认设置")
                        
                except Exception as e:
                    self.logger.error(f"设置{generation_mode}生成模式时出错", error=str(e))
            else:
                self.logger.info("使用默认的速度更快模式")
            
            await asyncio.sleep(1)
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message=f"生成模式设置完成: {generation_mode}"
            )
        except Exception as e:
            self.logger.error("设置生成模式失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"设置生成模式失败: {str(e)}"
            )
    
    async def set_frame_rate(self, frame_rate: str) -> TaskResult:
        """设置帧率"""
        try:
            self.logger.info("正在设置视频帧率", frame_rate=f"{frame_rate}FPS")
            
            # 帧率选项映射表，按下标对应
            frame_rate_options = {
                "30": 0,    # 第一个选项：帧率30（默认）
                "60": 1     # 第二个选项：帧率60
            }
            
            if frame_rate in frame_rate_options:
                target_index = frame_rate_options[frame_rate]
                try:
                    # 先等待帧率容器出现
                    frame_rate_container = await self.page.wait_for_selector('div.style-item:has(span.text:text("视频帧率"))', timeout=10000)
                    
                    # 获取所有帧率选项
                    frame_rate_items = await self.page.query_selector_all('div.style-item:has(span.text:text("视频帧率")) .option-item')
                    
                    self.logger.debug(f"找到 {len(frame_rate_items)} 个帧率选项")
                    
                    if len(frame_rate_items) > target_index:
                        target_item = frame_rate_items[target_index]
                        
                        # 检查目标选项是否被禁用
                        class_list = await target_item.get_attribute('class')
                        if 'disabled' in class_list:
                            self.logger.warning(f"{frame_rate}FPS被禁用，无法选择")
                        else:
                            # 尝试点击目标选项
                            await target_item.click()
                            await asyncio.sleep(2)
                            
                            # 验证是否成功选中
                            updated_class = await target_item.get_attribute('class')
                            if 'selected' in updated_class:
                                self.logger.info(f"已成功设置帧率为{frame_rate}FPS")
                            else:
                                self.logger.warning(f"{frame_rate}FPS选项点击后未显示为选中状态")
                    else:
                        self.logger.warning(f"帧率选项索引{target_index}超出范围，使用默认设置")
                        
                except Exception as e:
                    self.logger.error(f"设置{frame_rate}FPS时出错", error=str(e))
            else:
                self.logger.info("使用默认的30FPS")
            
            await asyncio.sleep(1)
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message=f"帧率设置完成: {frame_rate}FPS"
            )
        except Exception as e:
            self.logger.error("设置帧率失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"设置帧率失败: {str(e)}"
            )
    
    async def set_resolution(self, resolution: str) -> TaskResult:
        """设置分辨率"""
        try:
            self.logger.info("正在设置视频分辨率", resolution=resolution)
            
            # 分辨率选项映射表，按下标对应
            resolution_options = {
                "720p": 0,  # 第一个选项：720P（默认）
                "1080p": 1,  # 第二个选项：1080P
                "4k": 2     # 第三个选项：4K
            }
            
            if resolution in resolution_options:
                target_index = resolution_options[resolution]
                try:
                    # 先等待分辨率容器出现
                    resolution_container = await self.page.wait_for_selector('div.style-item:has(span.text:text("视频分辨率"))', timeout=10000)
                    
                    # 获取所有分辨率选项
                    resolution_items = await self.page.query_selector_all('div.style-item:has(span.text:text("视频分辨率")) .option-item')
                    
                    self.logger.debug(f"找到 {len(resolution_items)} 个分辨率选项")
                    
                    if len(resolution_items) > target_index:
                        target_item = resolution_items[target_index]
                        
                        # 检查目标选项是否被禁用
                        class_list = await target_item.get_attribute('class')
                        if 'disabled' in class_list:
                            self.logger.warning(f"{resolution}选项被禁用，无法选择")
                        else:
                            # 尝试点击目标选项
                            await target_item.click()
                            await asyncio.sleep(2)
                            
                            # 验证是否成功选中
                            updated_class = await target_item.get_attribute('class')
                            if 'selected' in updated_class:
                                self.logger.info(f"已成功设置分辨率为{resolution}")
                            else:
                                self.logger.warning(f"{resolution}选项点击后未显示为选中状态")
                    else:
                        self.logger.warning(f"分辨率选项索引{target_index}超出范围，使用默认设置")
                        
                except Exception as e:
                    self.logger.error(f"设置{resolution}分辨率时出错", error=str(e))
            else:
                self.logger.info("使用默认的720P分辨率")
            
            await asyncio.sleep(1)
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message=f"分辨率设置完成: {resolution}"
            )
        except Exception as e:
            self.logger.error("设置分辨率失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"设置分辨率失败: {str(e)}"
            )
    
    async def set_duration(self, duration: str) -> TaskResult:
        """设置视频时长"""
        try:
            self.logger.info("正在设置视频时长", duration=duration)
            
            # 时长选项映射表，按下标对应
            duration_options = {
                "5s": 0,    # 第一个选项：5秒（默认）
                "10s": 1    # 第二个选项：10秒
            }
            
            if duration in duration_options:
                target_index = duration_options[duration]
                try:
                    # 先点击时长选择按钮（第二个节点）
                    self.logger.debug("正在点击时长选择按钮")
                    duration_button_selector = 'div.options div.prompt-item:nth-child(2)'
                    duration_button = await self.page.wait_for_selector(duration_button_selector, timeout=10000, state='visible')
                    await duration_button.click()
                    await asyncio.sleep(1)
                    
                    # 等待弹窗出现并获取所有时长选项
                    self.logger.debug("正在定位时长选项")
                    duration_items = await self.page.query_selector_all('div.duration-item')
                    
                    self.logger.debug(f"找到 {len(duration_items)} 个时长选项")
                    
                    if len(duration_items) > target_index:
                        target_item = duration_items[target_index]
                        
                        # 检查目标选项是否被禁用
                        class_list = await target_item.get_attribute('class')
                        if 'disabled' in class_list:
                            self.logger.warning(f"{duration}时长被禁用，无法选择")
                        else:
                            # 尝试点击目标选项
                            await target_item.click()
                            await asyncio.sleep(2)
                            
                            # 验证是否成功选中
                            updated_class = await target_item.get_attribute('class')
                            if 'selected' in updated_class or 'disabled' not in updated_class:
                                self.logger.info(f"已成功设置视频时长为{duration}")
                            else:
                                self.logger.warning(f"{duration}时长选项点击后未显示为选中状态")
                    else:
                        self.logger.warning(f"时长选项索引{target_index}超出范围，使用默认设置")
                        
                except Exception as e:
                    self.logger.error(f"设置{duration}时长时出错", error=str(e))
            else:
                self.logger.info("使用默认的5秒时长")
            
            await asyncio.sleep(1)
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message=f"时长设置完成: {duration}"
            )
        except Exception as e:
            self.logger.error("设置时长失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"设置时长失败: {str(e)}"
            )
    
    async def set_ai_audio(self, ai_audio: bool) -> TaskResult:
        """设置AI音效"""
        try:
            self.logger.info("正在设置AI音效", ai_audio='开启' if ai_audio else '关闭')
            
            try:
                # 先点击AI音效按钮来打开选项弹窗
                ai_audio_button_selector = 'div.prompt-item:has-text("AI音效")'
                ai_audio_button = await self.page.wait_for_selector(ai_audio_button_selector, timeout=10000, state='visible')
                await ai_audio_button.click()
                self.logger.debug("已点击AI音效按钮，等待选项弹窗")
                await asyncio.sleep(2)
                
                # 等待选项弹窗出现，使用更具体的选择器
                popover_selector = '.el-popper.options_popover[aria-hidden="false"]'
                await self.page.wait_for_selector(popover_selector, timeout=5000, state='visible')
                self.logger.debug("AI音效选项弹窗已出现")
                
                if ai_audio:
                    # 选择"开启"选项 - 使用更精确的选择器
                    enable_option_selector = '.el-popper.options_popover[aria-hidden="false"] .duration-item:has(.title-wrap:has-text("开启"))'
                    enable_option = await self.page.wait_for_selector(enable_option_selector, timeout=5000, state='visible')
                    await enable_option.click()
                    self.logger.info("已选择开启AI音效")
                else:
                    # 选择"关闭"选项 - 使用更精确的选择器
                    disable_option_selector = '.el-popper.options_popover[aria-hidden="false"] .duration-item:has(.title-wrap:has-text("关闭"))'
                    disable_option = await self.page.wait_for_selector(disable_option_selector, timeout=5000, state='visible')
                    await disable_option.click()
                    self.logger.info("已选择关闭AI音效")
                    
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error("设置AI音效时出错", error=str(e))
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message=f"AI音效设置完成: {'开启' if ai_audio else '关闭'}"
            )
        except Exception as e:
            self.logger.error("设置AI音效失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"设置AI音效失败: {str(e)}"
            )
    
    async def input_prompt(self, prompt: str) -> TaskResult:
        """输入提示词"""
        try:
            if prompt and prompt.strip():
                self.logger.info("开始输入提示词", prompt=prompt)
                
                # 查找提示词输入框
                prompt_textarea_selector = 'textarea.prompt.scroll-display-none[placeholder*="通过上传图片或输入描述，创造你的视频"]'
                prompt_textarea = await self.page.wait_for_selector(prompt_textarea_selector, timeout=10000, state='visible')
                
                if prompt_textarea:
                    # 清空输入框并输入提示词
                    await prompt_textarea.click()
                    await prompt_textarea.fill('')  # 清空现有内容
                    
                    # 输入提示词
                    await prompt_textarea.type(prompt, delay=50)
                    
                    self.logger.info("已成功输入提示词", prompt=prompt)
                    await asyncio.sleep(1)
                else:
                    self.logger.warning("未找到提示词输入框")
            else:
                self.logger.info("提示词为空，跳过输入提示词步骤")
            
            return TaskResult(
                code=ErrorCode.SUCCESS.value,
                data=None,
                message="提示词输入完成"
            )
        except Exception as e:
            self.logger.error("输入提示词失败", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"输入提示词失败: {str(e)}"
            )
    
    async def setup_response_listener(self):
        """设置响应监听器"""
        self.chat_id = None
        self.video_result = None
        
        async def handle_request(request):
            if 'video-api/v1/chat' in request.url and request.method == 'POST':
                self.logger.debug("检测到生成请求", url=request.url)
                
        async def handle_response(response):
            try:
                if 'video-api/v1/chat' in response.url and response.request.method == 'POST':
                    response_text = await response.text()
                    self.logger.debug("收到生成响应", response=response_text)
                    response_data = json.loads(response_text)
                    if response_data.get('status') == 0 and 'result' in response_data:
                        self.chat_id = response_data['result'].get('chat_id')
                        self.logger.info("获取到chat_id", chat_id=self.chat_id)
                
                # 监听状态更新请求
                if self.chat_id and f'video-api/v1/chat/status/{self.chat_id}' in response.url:
                    response_text = await response.text()
                    status_data = json.loads(response_text)
                    
                    if status_data.get('status') == 0 and 'result' in status_data:
                        result = status_data['result']
                        status = result.get('status')
                        plan = result.get('plan', '')
                        msg = result.get('msg', '')
                        
                        self.logger.debug("生成状态", status=status, plan=plan, msg=msg)
                        
                        if status == 'finished':
                            video_url = result.get('video_url', '')
                            if video_url:
                                self.logger.info("视频生成成功", video_url=video_url)
                                self.video_result = TaskResult(
                                    code=ErrorCode.SUCCESS.value,
                                    data={
                                        "video_url": video_url,
                                        "cover_url": result.get('cover_url', ''),
                                        "chat_id": self.chat_id,
                                        "duration": result.get('video_duration', ''),
                                        "resolution": result.get('video_resolution', ''),
                                        "fps": result.get('video_fps', ''),
                                        "containing_audio_url": result.get('containing_audio_url', '')
                                    },
                                    message="视频生成成功"
                                )
                            else:
                                self.logger.error("生成完成但未获取到视频URL")
                                self.video_result = TaskResult(
                                    code=ErrorCode.GENERATION_FAILED.value,
                                    data=None,
                                    message="生成完成但未获取到视频URL"
                                )
                        elif status == 'failed' or status == 'error':
                            self.logger.error("视频生成失败", msg=msg)
                            self.video_result = TaskResult(
                                code=ErrorCode.GENERATION_FAILED.value,
                                data=None,
                                message=f"视频生成失败: {msg}"
                            )
                            
            except Exception as e:
                self.logger.error("解析响应时出错", error=str(e))
        
        # 在浏览器上下文级别设置监听器
        self.context.on('request', handle_request)
        self.context.on('response', handle_response)
    
    async def start_generation(self) -> TaskResult:
        """开始生成视频"""
        try:
            self.logger.info("正在查找生成按钮")
            
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
                    generate_button = await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if generate_button:
                        self.logger.info("找到生成按钮", selector=selector)
                        break
                except:
                    continue
            
            if not generate_button:
                self.logger.debug("使用通用方法查找生成按钮")
                # 如果上述选择器都没找到，尝试通过文本或其他方式查找
                generate_button = await self.page.query_selector('button:has-text("生成")')
                if not generate_button:
                    generate_button = await self.page.query_selector('[role="button"]:has(svg)')
            
            if generate_button:
                # 确保按钮可点击
                await generate_button.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                
                # 点击生成按钮
                await generate_button.click()
                self.logger.info("已点击生成按钮，开始视频生成")
                
                # 等待获取chat_id
                timeout_count = 0
                while self.chat_id is None and timeout_count < 30:  # 等待30秒
                    await asyncio.sleep(1)
                    timeout_count += 1
                
                if self.chat_id is None:
                    self.logger.error("未能获取到chat_id")
                    return TaskResult(
                        code=ErrorCode.TASK_ID_NOT_OBTAINED.value,
                        data=None,
                        message="未能获取到chat_id"
                    )
                
                self.logger.info("成功获取chat_id，开始监听生成状态", chat_id=self.chat_id)
                return TaskResult(
                    code=ErrorCode.SUCCESS.value,
                    data={"chat_id": self.chat_id},
                    message="生成任务已启动"
                )
                
            else:
                self.logger.error("未找到生成按钮")
                return TaskResult(
                    code=ErrorCode.WEB_INTERACTION_FAILED.value,
                    data=None,
                    message="未找到生成按钮"
                )
                
        except Exception as e:
            self.logger.error("点击生成按钮时出错", error=str(e))
            return TaskResult(
                code=ErrorCode.WEB_INTERACTION_FAILED.value,
                data=None,
                message=f"点击生成按钮失败: {str(e)}"
            )
    
    async def wait_for_completion(self, max_wait_time: int = 3600) -> TaskResult:
        """等待生成完成"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                if self.video_result is not None:
                    return self.video_result
                
                await asyncio.sleep(1)
            
            # 超时
            self.logger.error("视频生成超时", max_wait_time=max_wait_time)
            return TaskResult(
                code=ErrorCode.OTHER_ERROR.value,
                data=None,
                message=f"视频生成超时（超过{max_wait_time}秒）"
            )
        except Exception as e:
            self.logger.error("等待生成完成时出错", error=str(e))
            return TaskResult(
                code=ErrorCode.OTHER_ERROR.value,
                data=None,
                message=f"等待生成完成失败: {str(e)}"
            )
    
    async def execute(self, image_path: str, prompt: str = "", cookies: str = "", 
                      generation_mode: str = "fast", frame_rate: str = "30", 
                      resolution: str = "720p", duration: str = "5s", 
                      ai_audio: bool = False) -> TaskResult:
        """执行清影图生视频任务"""
        start_time = time.time()
        
        try:
            self.logger.info("开始执行清影图生视频任务")
            
            # 初始化浏览器
            init_result = await self.init_browser(cookies)
            if init_result.code != ErrorCode.SUCCESS.value:
                return init_result
            
            # 设置cookies
            if cookies:
                await self.handle_cookies(cookies)
            
            # 导航到平台
            nav_result = await self.navigate_to_platform()
            if nav_result.code != ErrorCode.SUCCESS.value:
                return nav_result
            
            # 处理弹窗
            popup_result = await self.handle_popups()
            if popup_result.code != ErrorCode.SUCCESS.value:
                return popup_result
            
            # 上传图片
            upload_result = await self.upload_image(image_path)
            if upload_result.code != ErrorCode.SUCCESS.value:
                return upload_result
            
            # 配置基础参数
            params_result = await self.configure_basic_params()
            if params_result.code != ErrorCode.SUCCESS.value:
                return params_result
            
            # 设置生成模式
            mode_result = await self.set_generation_mode(generation_mode)
            if mode_result.code != ErrorCode.SUCCESS.value:
                return mode_result
            
            # 设置帧率
            frame_result = await self.set_frame_rate(frame_rate)
            if frame_result.code != ErrorCode.SUCCESS.value:
                return frame_result
            
            # 设置分辨率
            resolution_result = await self.set_resolution(resolution)
            if resolution_result.code != ErrorCode.SUCCESS.value:
                return resolution_result
            
            # 设置时长
            duration_result = await self.set_duration(duration)
            if duration_result.code != ErrorCode.SUCCESS.value:
                return duration_result
            
            # 设置AI音效
            audio_result = await self.set_ai_audio(ai_audio)
            if audio_result.code != ErrorCode.SUCCESS.value:
                return audio_result
            
            # 输入提示词
            prompt_result = await self.input_prompt(prompt)
            if prompt_result.code != ErrorCode.SUCCESS.value:
                return prompt_result
            
            # 设置响应监听器
            await self.setup_response_listener()
            
            # 开始生成
            start_result = await self.start_generation()
            if start_result.code != ErrorCode.SUCCESS.value:
                return start_result
            
            # 等待完成
            final_result = await self.wait_for_completion()
            
            # 计算执行时间
            execution_time = time.time() - start_time
            final_result.execution_time = execution_time
            
            # 获取更新后的cookies
            try:
                cookies_list = await self.context.cookies()
                cookie_strings = []
                for cookie in cookies_list:
                    cookie_strings.append(f"{cookie['name']}={cookie['value']}")
                final_result.cookies = '; '.join(cookie_strings)
            except Exception as e:
                self.logger.debug("获取cookies失败", error=str(e))
            
            return final_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error("执行清影图生视频任务失败", error=str(e), execution_time=execution_time)
            return TaskResult(
                code=ErrorCode.OTHER_ERROR.value,
                data=None,
                message=f"执行失败: {str(e)}",
                execution_time=execution_time
            )
        finally:
            await self.close_browser()


# 兼容性函数，保持与原有接口一致
async def generate_image_to_video(image_path, prompt="", cookie_string="", headless=True, 
                                  generation_mode="fast", frame_rate="30", resolution="720p", 
                                  duration="5s", ai_audio=False):
    """
    兼容性函数，保持与原有接口一致
    """
    executor = QingyingImage2VideoExecutor(headless=headless)
    
    result = await executor.execute(
        image_path=image_path,
        prompt=prompt,
        cookies=cookie_string,
        generation_mode=generation_mode,
        frame_rate=frame_rate,
        resolution=resolution,
        duration=duration,
        ai_audio=ai_audio
    )
    
    # 转换为原有格式
    return {
        "code": result.code,
        "data": result.data,
        "message": result.message
    }


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
            print("未找到cookies.json文件")
        except Exception as e:
            cookie_string = ""
            print(f"读取cookies.json时出错: {str(e)}")
        
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
            print(f"图生视频成功: {result['data']}")
        else:
            print(f"图生视频失败: {result['message']}")
    
    # 运行测试
    asyncio.run(test())