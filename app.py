#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: app.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\app.py
功能说明:
    Flask 应用主入口，初始化应用、数据库、蓝图注册、日志记录和路由定义。
    提供首页、数据导入页面及各 API 接口支持。通过 run.ps1 启动服务。
使用说明:
    直接运行此文件或通过 run.ps1 脚本启动服务，确保当前工作目录为项目根目录。
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, send_from_directory
from sqlalchemy.exc import SQLAlchemyError
from backend.infrastructure.database import db


def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(
                    os.getcwd(), 'frontend', 'templates'),
                static_folder=os.path.join(os.getcwd(), 'frontend', 'static'))

    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(base_dir, 'instance', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        try:
            db.create_all()
        except SQLAlchemyError as e:
            app.logger.error(f"数据库初始化错误: {str(e)}")

    try:
        from backend.api.import_api import import_api
        from backend.api.sidebar_api import sidebar_api  # 新增注册侧边栏蓝图
        # 注册蓝图
        app.register_blueprint(import_api)
        app.register_blueprint(sidebar_api)
    except Exception as e:
        app.logger.error(f"蓝图注册错误: {str(e)}")

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'frontend', 'static'),
                                   'favicon.ico', mimetype='image/x-icon')

    @app.route('/import')
    def data_import():
        return render_template('data_import.html')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=False)
