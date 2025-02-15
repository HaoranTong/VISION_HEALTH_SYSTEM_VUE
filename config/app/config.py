#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: config.py
完整存储路径: E:\\DEV_CONTEXT\\1_Projects\\VISION_HEALTH_SYSTEM\\config\\app\\config.py
功能介绍:
    配置模块，定义开发环境下的配置参数，包括数据库 URI、
    调试模式、测试模式、密钥等设置。
使用方法:
    在 Flask 应用中通过
        app.config.from_object(DevelopmentConfig)
    加载配置参数。
"""


class DevelopmentConfig:
    """
    DevelopmentConfig 类:
        定义开发环境下的配置信息。
    Attributes:
        DEBUG (bool): 启用调试模式，默认为 True。
        TESTING (bool): 启用测试模式，默认为 False。
        SQLALCHEMY_DATABASE_URI (str): 数据库连接 URI，使用 SQLite 数据库文件。
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): 禁用对象修改追踪，默认为 False。
        SECRET_KEY (str): Flask 的密钥，用于会话加密及其他安全相关功能。
    """

    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///instance/app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"
