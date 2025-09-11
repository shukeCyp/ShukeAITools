# -*- coding: utf-8 -*-
"""
配置管理工具类
"""
from backend.models.models import Config
from datetime import datetime
import json

class ConfigUtil:
    """配置工具类"""
    
    # 默认配置
    DEFAULT_CONFIGS = {
        'automation_max_threads': {
            'value': '3',
            'description': '自动化任务最大线程数'
        },
        'hide_window': {
            'value': 'false',
            'description': '是否隐藏浏览器窗口'
        },
        'auto_retry_enabled': {
            'value': 'false',
            'description': '是否启用自动重试功能，只会重试因为网络问题导致的失败任务'
        }
    }
    
    @classmethod
    def init_default_configs(cls):
        """初始化默认配置"""
        print("初始化默认配置...")
        for key, config in cls.DEFAULT_CONFIGS.items():
            try:
                # 检查是否已存在
                existing = Config.get(Config.key == key)
                print("配置已存在: {} = {}".format(key, existing.value))
            except Config.DoesNotExist:
                # 不存在则创建
                Config.create(
                    key=key,
                    value=config['value'],
                    description=config['description']
                )
                print("创建默认配置: {} = {}".format(key, config['value']))
    
    @classmethod
    def get_config(cls, key, default_value=None):
        """获取配置值"""
        try:
            config = Config.get(Config.key == key)
            return config.value
        except Config.DoesNotExist:
            print("配置不存在: {}, 返回默认值: {}".format(key, default_value))
            return default_value
    
    @classmethod
    def set_config(cls, key, value, description=None):
        """设置配置值"""
        try:
            config = Config.get(Config.key == key)
            config.value = str(value)
            config.updated_at = datetime.now()
            if description:
                config.description = description
            config.save()
            print("更新配置: {} = {}".format(key, value))
            return True
        except Config.DoesNotExist:
            # 配置不存在则创建
            Config.create(
                key=key,
                value=str(value),
                description=description or ''
            )
            print("创建配置: {} = {}".format(key, value))
            return True
        except Exception as e:
            print("设置配置失败: {} = {}, 错误: {}".format(key, value, str(e)))
            return False
    
    @classmethod
    def get_config_bool(cls, key, default_value=False):
        """获取布尔类型配置"""
        value = cls.get_config(key, str(default_value).lower())
        return value.lower() in ['true', '1', 'yes', 'on']
    
    @classmethod
    def get_config_int(cls, key, default_value=0):
        """获取整数类型配置"""
        try:
            value = cls.get_config(key, str(default_value))
            return int(value)
        except (ValueError, TypeError):
            print("配置值转换为整数失败: {} = {}, 返回默认值: {}".format(key, value, default_value))
            return default_value
    
    @classmethod
    def get_all_configs(cls):
        """获取所有配置"""
        try:
            configs = {}
            for config in Config.select():
                configs[config.key] = {
                    'value': config.value,
                    'description': config.description,
                    'created_at': config.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': config.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            return configs
        except Exception as e:
            print("获取所有配置失败: {}".format(str(e)))
            return {}
    
    @classmethod
    def delete_config(cls, key):
        """删除配置"""
        try:
            config = Config.get(Config.key == key)
            config.delete_instance()
            print("删除配置: {}".format(key))
            return True
        except Config.DoesNotExist:
            print("配置不存在，无需删除: {}".format(key))
            return False
        except Exception as e:
            print("删除配置失败: {}, 错误: {}".format(key, str(e)))
            return False

# 便捷方法
def get_automation_max_threads():
    """获取自动化最大线程数"""
    return ConfigUtil.get_config_int('automation_max_threads', 3)

def set_automation_max_threads(value):
    """设置自动化最大线程数"""
    return ConfigUtil.set_config('automation_max_threads', value)

def get_hide_window():
    """获取是否隐藏窗口"""
    return ConfigUtil.get_config_bool('hide_window', False)

def set_hide_window(value):
    """设置是否隐藏窗口"""
    return ConfigUtil.set_config('hide_window', value)

def get_auto_retry_enabled():
    """获取是否启用自动重试"""
    return ConfigUtil.get_config_bool('auto_retry_enabled', False)

def set_auto_retry_enabled(value):
    """设置是否启用自动重试"""
    return ConfigUtil.set_config('auto_retry_enabled', value)