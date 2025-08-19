# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from datetime import datetime

# 创建蓝图
common_bp = Blueprint('common', __name__, url_prefix='/api')

@common_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    print("执行健康检查")
    return jsonify({
        'success': True,
        'message': '服务正常运行',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })