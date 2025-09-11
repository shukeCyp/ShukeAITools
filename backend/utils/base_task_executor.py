"""
任务执行基类 - 提供通用的浏览器自动化功能
"""

import asyncio
import time
import traceback
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from playwright.async_api import async_playwright
from colorama import Fore, Style, init

# 初始化colorama
init()

class ErrorCode(Enum):
    """错误代码枚举 - 简化为4大类型"""
    SUCCESS = 200
    
    # 类型1: 网页加载超时，节点找不到 (600-699)
    WEB_INTERACTION_FAILED = 600
    
    # 类型2: 生成未获取到taskID (700-799) 
    TASK_ID_NOT_OBTAINED = 700
    
    # 类型3: 生成失败(任务查询完成，但是没有url) (800-899)
    GENERATION_FAILED = 800
    
    # 类型4: 其他类型失败 (900-999)
    OTHER_ERROR = 900

@dataclass
class TaskResult:
    """任务执行结果数据类"""
    code: int
    data: Optional[Any]
    message: str
    error_details: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    cookies: Optional[str] = None

class TaskLogger:
    """结构化日志记录器"""
    
    @staticmethod
    def info(message: str, **kwargs):
        extra_info = f" | {kwargs}" if kwargs else ""
        print(f"{Fore.GREEN}[INFO] {message}{extra_info}{Style.RESET_ALL}")
    
    @staticmethod
    def warning(message: str, **kwargs):
        extra_info = f" | {kwargs}" if kwargs else ""
        print(f"{Fore.YELLOW}[WARN] {message}{extra_info}{Style.RESET_ALL}")
    
    @staticmethod
    def error(message: str, **kwargs):
        extra_info = f" | {kwargs}" if kwargs else ""
        print(f"{Fore.RED}[ERROR] {message}{extra_info}{Style.RESET_ALL}")
    
    @staticmethod
    def debug(message: str, **kwargs):
        extra_info = f" | {kwargs}" if kwargs else ""
        print(f"{Fore.CYAN}[DEBUG] {message}{extra_info}{Style.RESET_ALL}")

class BaseTaskExecutor(ABC):
    """任务执行基类"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.logger = TaskLogger()
    
    def get_browser_config(self) -> Dict[str, Any]:
        """获取浏览器配置"""
        self.logger.info("使用默认浏览器配置")
        
        config = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "device_scale_factor": 1.0,
            "locale": "en-US",
            "timezone_id": "America/New_York"
        }
        
        self.logger.info("浏览器配置已设置")
        return config
    
    async def init_browser(self, cookies: Optional[str] = None) -> TaskResult:
        """初始化浏览器"""
        try:
            self.logger.info("正在启动浏览器")
            config = self.get_browser_config()
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(**config)
            
            # 如果提供了cookies，则添加到浏览器上下文中
            if cookies:
                await self.hook_cookies(cookies)
                self.logger.info("已加载cookies")
            
            self.page = await self.context.new_page()
            
            self.logger.info("浏览器启动成功")
            return TaskResult(code=ErrorCode.SUCCESS.value, data=None, message="浏览器启动成功")
            
        except Exception as e:
            self.logger.error("浏览器启动失败", error=str(e))
            return TaskResult(
                code=ErrorCode.OTHER_ERROR.value,
                data=None,
                message="浏览器启动失败",
                error_details={"error": str(e), "traceback": traceback.format_exc()}
            )
    
    async def hook_cookies(self, cookies: str):
        """设置cookies到浏览器上下文"""
        try:
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
            
            await self.context.add_cookies(cookie_list)
            self.logger.info("Cookies设置成功")
            
        except Exception as e:
            self.logger.error("设置cookies时出错", error=str(e))
    
    async def get_cookies(self) -> Optional[str]:
        """获取当前页面的cookies"""
        try:
            if self.context:
                cookies = await self.context.cookies()
                # 将Cookie转换为字符串格式
                cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                self.logger.debug("获取到cookies", count=len(cookies))
                return cookie_string
            else:
                self.logger.warning("无法获取cookies：浏览器上下文不存在")
                return None
        except Exception as e:
            self.logger.error("获取cookies时出错", error=str(e))
            return None
    async def close_browser(self):
        """关闭浏览器"""
        try:
            if self.browser:
                await self.browser.close()
                self.logger.info("浏览器已关闭")
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            self.logger.error("关闭浏览器时出错", error=str(e))
    
    @abstractmethod
    async def execute(self, **kwargs) -> TaskResult:
        """执行任务的抽象方法，子类必须实现"""
        pass