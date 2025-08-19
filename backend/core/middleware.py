# -*- coding: utf-8 -*-
"""
中间件模块
"""

import time
from flask import request

def before_request():
    """记录请求开始时间的中间件"""
    request.start_time = time.time()

def after_request(response):
    """记录API响应的中间件"""
    if hasattr(request, 'start_time'):
        response_time = round((time.time() - request.start_time) * 1000, 2)
        print("API响应 - {} {}, 状态码: {}, 响应时间: {}ms".format(
            request.method, request.url, response.status_code, response_time))
    return response