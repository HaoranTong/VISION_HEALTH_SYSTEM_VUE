#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: reset_db.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\reset_db.py
功能说明:
    删除并重建数据库中的所有表（数据将全部丢失）。
使用方法:
    在命令行中运行: python reset_db.py
"""

from app import create_app
from backend.infrastructure.database import db
from backend.models import student  # 已经导入
from backend.models import student_extension  # 确保扩展表模型被加载


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset and recreated.")
