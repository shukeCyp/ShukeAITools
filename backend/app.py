#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request
from flask_cors import CORS
import time
import threading
from datetime import datetime

# 导入核心模块
from backend.core.database import init_database
from backend.core.middleware import before_request, after_request
from backend.core.global_task_manager import global_task_manager
from backend.models.models import JimengAccount, JimengText2ImgTask
from backend.utils.config_util import ConfigUtil

# 导入路由蓝图
from backend.api.v1.common_routes import common_bp
from backend.api.v1.accounts_routes import jimeng_accounts_bp
from backend.api.v1.text2img_routes import jimeng_text2img_bp
from backend.api.v1.config_routes import config_bp
from backend.api.v1.task_manager_routes import task_manager_bp

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 注册中间件
app.before_request(before_request)
app.after_request(after_request)

# 初始化数据库
init_database()

# 初始化默认配置
ConfigUtil.init_default_configs()

# 注册蓝图路由
app.register_blueprint(common_bp)
app.register_blueprint(jimeng_accounts_bp)
app.register_blueprint(jimeng_text2img_bp)
app.register_blueprint(config_bp)
app.register_blueprint(task_manager_bp)

# 启动全局任务管理器
global_task_manager.start()
print("全局任务管理器已启动")

if __name__ == '__main__':
    print("🚀 舒克AI工具集后端服务启动中...")
    print("✅ 数据库连接成功")
    print("🌐 API服务运行在: http://localhost:8888")
    print("📋 可用路由:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print("  {} [{}]".format(rule.rule, methods))
    app.run(debug=False, host='0.0.0.0', port=8888)