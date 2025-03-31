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
from backend.api.import_api import import_api
from backend.api.sidebar_api import sidebar_api
from backend.api.query_api import query_api  # 新增：引入数据查询蓝图
from backend.api.analysis_api import analysis_api


def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(
                    os.getcwd(), 'frontend', 'templates'),
                static_folder=os.path.join(os.getcwd(), 'frontend', 'static'))

    # 设置日志级别为 DEBUG
    app.logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

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

        app.register_blueprint(analysis_api)
        app.register_blueprint(import_api)
        app.register_blueprint(sidebar_api)
        app.register_blueprint(query_api)  # 新增：注册查询蓝图

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

    @app.route('/query')
    def query_page():
        return render_template('query.html')

    @app.route('/report')
    def report():
        return render_template('report.html')

    @app.route('/chart')
    def chart():
        return render_template('chart.html')

    @app.route('/api/students/import', methods=['POST'])
    def import_students():
        print("收到上传请求")  # 测试后端是否被调用
        app.logger.debug("收到上传请求")  # 使用日志记录，确保输出到终端
        return {"message": "上传成功"}, 200

    return app


application = create_app()

logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    application.run(host='0.0.0.0', port=5000, debug=True)
