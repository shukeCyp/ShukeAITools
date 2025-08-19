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
    
    # 导入模型后再创建表
    from backend.models.models import Config, JimengAccount, JimengText2ImgTask
    
    with db:
        db.create_tables([Config, JimengAccount, JimengText2ImgTask])
        print("数据库初始化完成: {}".format(DATABASE_PATH))