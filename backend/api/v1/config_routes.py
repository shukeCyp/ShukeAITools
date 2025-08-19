# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from backend.utils.config_util import ConfigUtil

# 创建蓝图
config_bp = Blueprint('config', __name__, url_prefix='/api/config')

@config_bp.route('', methods=['GET'])
def get_all_configs():
    """获取所有配置"""
    try:
        print("获取所有系统配置")
        configs = ConfigUtil.get_all_configs()
        print("成功获取配置，总数: {}".format(len(configs)))
        return jsonify({
            'success': True,
            'data': configs
        })
    except Exception as e:
        print("获取配置失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '获取配置失败: {}'.format(str(e))
        }), 500

@config_bp.route('/<key>', methods=['GET'])
def get_config(key):
    """获取指定配置"""
    try:
        print("获取配置: {}".format(key))
        value = ConfigUtil.get_config(key)
        if value is None:
            return jsonify({
                'success': False,
                'message': '配置不存在: {}'.format(key)
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'key': key,
                'value': value
            }
        })
    except Exception as e:
        print("获取配置失败: {}, 错误: {}".format(key, str(e)))
        return jsonify({
            'success': False,
            'message': '获取配置失败: {}'.format(str(e))
        }), 500

@config_bp.route('/<key>', methods=['PUT'])
def update_config(key):
    """更新指定配置"""
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要字段: value'
            }), 400
        
        value = data['value']
        description = data.get('description')
        
        print("更新配置: {} = {}".format(key, value))
        
        success = ConfigUtil.set_config(key, value, description)
        if success:
            return jsonify({
                'success': True,
                'message': '配置更新成功',
                'data': {
                    'key': key,
                    'value': str(value)
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '配置更新失败'
            }), 500
            
    except Exception as e:
        print("更新配置失败: {}, 错误: {}".format(key, str(e)))
        return jsonify({
            'success': False,
            'message': '更新配置失败: {}'.format(str(e))
        }), 500

@config_bp.route('/<key>', methods=['DELETE'])
def delete_config(key):
    """删除指定配置"""
    try:
        print("删除配置: {}".format(key))
        success = ConfigUtil.delete_config(key)
        if success:
            return jsonify({
                'success': True,
                'message': '配置删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '配置不存在或删除失败'
            }), 404
            
    except Exception as e:
        print("删除配置失败: {}, 错误: {}".format(key, str(e)))
        return jsonify({
            'success': False,
            'message': '删除配置失败: {}'.format(str(e))
        }), 500

@config_bp.route('/batch', methods=['PUT'])
def update_batch_configs():
    """批量更新配置"""
    try:
        data = request.get_json()
        if not data or 'configs' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要字段: configs'
            }), 400
        
        configs = data['configs']
        if not isinstance(configs, dict):
            return jsonify({
                'success': False,
                'message': 'configs必须是对象格式'
            }), 400
        
        print("批量更新配置，数量: {}".format(len(configs)))
        
        success_count = 0
        failed_count = 0
        
        for key, value in configs.items():
            try:
                if ConfigUtil.set_config(key, value):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print("更新配置失败: {} = {}, 错误: {}".format(key, value, str(e)))
                failed_count += 1
        
        print("批量更新完成，成功: {}, 失败: {}".format(success_count, failed_count))
        
        return jsonify({
            'success': True,
            'message': '批量更新完成，成功: {}, 失败: {}'.format(success_count, failed_count),
            'data': {
                'success_count': success_count,
                'failed_count': failed_count
            }
        })
        
    except Exception as e:
        print("批量更新配置失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '批量更新配置失败: {}'.format(str(e))
        }), 500

@config_bp.route('/init', methods=['POST'])
def init_default_configs():
    """初始化默认配置"""
    try:
        print("开始初始化默认配置")
        ConfigUtil.init_default_configs()
        return jsonify({
            'success': True,
            'message': '默认配置初始化成功'
        })
    except Exception as e:
        print("初始化默认配置失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '初始化默认配置失败: {}'.format(str(e))
        }), 500