# -*- coding: utf-8 -*-
"""
应用配置设置
"""

import os

# 数据库配置
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'shukeai_tools.db')

# Cookies目录
COOKIES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies')

# 任务处理配置
TASK_PROCESSOR_INTERVAL = 5  # 任务检查间隔（秒）
TASK_PROCESSOR_ERROR_WAIT = 10  # 错误后等待时间（秒）

# Playwright配置
PLAYWRIGHT_HEADLESS = True  # 是否无头模式运行