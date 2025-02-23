#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: app.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\app.py
功能说明:
    Flask 应用主入口，初始化应用、数据库、蓝图注册、日志记录和路由定义。
    提供首页和各 API 接口支持。通过脚本 run.ps1 启动服务。
使用说明:
    直接运行此文件或通过 run.ps1 脚本启动服务，确保当前工作目录为项目根目录。
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory
from backend.infrastructure.database import db
from sqlalchemy.exc import SQLAlchemyError


def create_app():
    """
    创建并配置 Flask 应用实例.

    Returns:
        Flask: 已配置的 Flask 应用实例.
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'frontend/templates'),
                static_folder=os.path.join(base_dir, 'frontend/static'))

    # 配置数据库连接
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"sqlite:///{os.path.join(base_dir, 'instance/app.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化数据库
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
        except SQLAlchemyError as e:
            app.logger.error(f"数据库初始化错误: {str(e)}")

    # 注册蓝图模块
    try:
        # pylint: disable=import-outside-toplevel
        from backend.api.analysis_api import analysis_api
        from backend.api.calculation_api import calculation_api
        from backend.api.import_api import import_api
        from backend.api.query_api import query_api
        from backend.api.sidebar_api import sidebar_api
        from backend.api.student_api import student_api

        app.register_blueprint(analysis_api)
        app.register_blueprint(calculation_api)
        app.register_blueprint(import_api)
        app.register_blueprint(query_api)
        app.register_blueprint(sidebar_api)
        app.register_blueprint(student_api)
    except Exception as e:
        app.logger.error(f"蓝图注册错误: {str(e)}")

    # 设置日志，确保捕获详细信息
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # 新增：处理 /favicon.ico 请求，确保返回正确图标
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'frontend/static'),
                                   'favicon.ico', mimetype='image/x-icon')

    # 首页路由
    @app.route('/')
    def index():
        """
        系统首页路由.

        Returns:
            HTML: 渲染后的首页模板.
        """
        stats = {
            "total_students": 0,
            "current_time": datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        try:
            from backend.models.student import Student  # pylint: disable=import-outside-toplevel
            stats["total_students"] = db.session.query(Student).count()
        except SQLAlchemyError as e:
            app.logger.error(f"数据库查询错误: {str(e)}")
        return render_template('index.html', **stats)

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=False)
