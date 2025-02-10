#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: database.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM\src\context_system\infrastructure\database.py
功能介绍:
    初始化 SQLAlchemy 数据库实例，用于项目中所有数据库操作。
使用方法:
    在 Flask 应用中调用 db.init_app(app) 初始化数据库。
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
