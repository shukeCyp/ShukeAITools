# -*- coding: utf-8 -*-
"""
数据库核心模块
"""

import os
import time
from datetime import datetime
from peewee import *

from backend.config.settings import DATABASE_PATH, DATABASE_DIR

# 初始化数据库连接，增加超时和重试配置
db = SqliteDatabase(
    DATABASE_PATH,
    timeout=30,  # 30秒超时
    pragmas={
        'journal_mode': 'wal',  # 使用WAL模式减少锁定
        'cache_size': -1024 * 64,  # 64MB缓存
        'synchronous': 1,  # 正常同步模式
        'foreign_keys': 1,
        'busy_timeout': 30000,  # 30秒忙等待超时
    }
)

def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        print("创建数据库目录: {}".format(DATABASE_DIR))
    
    # 导入模型
    from backend.models.models import Config, JimengAccount, JimengText2ImgTask, JimengImg2ImgTask, JimengImg2VideoTask, JimengDigitalHumanTask, JimengTaskRecord, QingyingAccount, QingyingImage2VideoTask
    
    # 定义所有模型类
    models = [Config, JimengAccount, JimengText2ImgTask, JimengImg2ImgTask, JimengImg2VideoTask, JimengDigitalHumanTask, JimengTaskRecord, QingyingAccount, QingyingImage2VideoTask]
    
    max_retries = 3
    retry_delay = 1  # 秒
    
    for attempt in range(max_retries):
        try:
            with db:
                # 检查并创建缺失的表
                created_tables = []
                for model in models:
                    table_name = model._meta.table_name
                    if not db.table_exists(table_name):
                        # 使用safe=True避免表已存在时的错误
                        model.create_table(safe=True)
                        created_tables.append(table_name)
                        print(f"创建缺失的表: {table_name}")
                    else:
                        print(f"表已存在: {table_name}")
                
                if created_tables:
                    print(f"成功创建 {len(created_tables)} 个缺失的表: {', '.join(created_tables)}")
                else:
                    print("所有表都已存在，无需创建")
                
                print("数据库初始化完成: {}".format(DATABASE_PATH))
                return  # 成功完成，退出重试循环
                
        except OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                print(f"数据库被锁定，第 {attempt + 1} 次重试，等待 {retry_delay} 秒...")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
                continue
            else:
                print(f"数据库初始化失败: {e}")
                raise
        except Exception as e:
            print(f"数据库初始化出现意外错误: {e}")
            if attempt < max_retries - 1:
                print(f"第 {attempt + 1} 次重试，等待 {retry_delay} 秒...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                raise