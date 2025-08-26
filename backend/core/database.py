# -*- coding: utf-8 -*-
"""
数据库核心模块
"""

import os
from datetime import datetime
from peewee import *

from backend.config.settings import DATABASE_PATH, DATABASE_DIR

# 初始化数据库
db = SqliteDatabase(DATABASE_PATH)

def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        print("创建数据库目录: {}".format(DATABASE_DIR))
    
    # 导入模型
    from backend.models.models import Config, JimengAccount, JimengText2ImgTask, JimengImg2VideoTask, JimengDigitalHumanTask
    
    # 定义所有模型类
    models = [Config, JimengAccount, JimengText2ImgTask, JimengImg2VideoTask, JimengDigitalHumanTask]
    
    with db:
        # 检查并创建缺失的表
        created_tables = []
        for model in models:
            table_name = model._meta.table_name
            if not db.table_exists(table_name):
                db.create_tables([model])
                created_tables.append(table_name)
                print(f"创建缺失的表: {table_name}")
            else:
                print(f"表已存在: {table_name}")
        
        if created_tables:
            print(f"成功创建 {len(created_tables)} 个缺失的表: {', '.join(created_tables)}")
        else:
            print("所有表都已存在，无需创建")
        
        print("数据库初始化完成: {}".format(DATABASE_PATH))