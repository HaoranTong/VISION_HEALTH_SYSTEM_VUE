#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: app.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM\app.py
功能介绍:
    初始化 Flask 应用、加载配置、初始化数据库，
    并注册所有 API 蓝图及静态页面路由。
    支持数据录入、查询、电子表格导入、统计分析页面及 Dashboard 页面访问。
使用方法:
    启动命令: python app.py
    可访问以下页面:
        /data_entry.html
        /data_query.html
        /data_import.html
        /statistics_analysis.html
        /dashboard.html
"""

# pylint: disable=wrong-import-position
import sys
import os
from flask import Flask, send_from_directory, render_template
from flask_migrate import Migrate  # 导入 Flask-Migrate
from context_system.api.endpoints.student_api import student_api
from context_system.api.endpoints.query_api import query_api
from context_system.api.endpoints.import_api import import_api
from context_system.api.endpoints.analysis_api import analysis_api
from context_system.infrastructure.database import db
from config.app.config import DevelopmentConfig  # pylint: disable=E0611

# 初始化 Flask 应用
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# 初始化数据库迁移
migrate = Migrate(app, db)  # 初始化 Migrate

print("SQLALCHEMY_DATABASE_URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))
db.init_app(app)

# 注册所有蓝图
app.register_blueprint(student_api)
app.register_blueprint(query_api)
app.register_blueprint(import_api)
app.register_blueprint(analysis_api)

# 路由设置
@app.route("/")
def index():
    """根路由返回欢迎信息"""
    return render_template('index.html')  # 使用模板文件返回主页

@app.route("/data_entry.html")
def data_entry():
    """返回数据录入页面的静态文件"""
    directory = os.path.join(app.root_path, "frontend", "web")
    return send_from_directory(directory, "data_entry.html")

@app.route("/data_query.html")
def data_query():
    """返回数据查询页面的静态文件"""
    directory = os.path.join(app.root_path, "frontend", "web")
    return send_from_directory(directory, "data_query.html")

@app.route("/data_import.html")
def data_import():
    """返回电子表格导入页面的静态文件"""
    directory = os.path.join(app.root_path, "frontend", "web")
    return send_from_directory(directory, "data_import.html")

@app.route("/statistics_analysis.html")
def statistics_analysis():
    """返回统计分析页面的静态文件"""
    directory = os.path.join(app.root_path, "frontend", "web")
    return send_from_directory(directory, "statistics_analysis.html")


@app.route("/dashboard.html")
def dashboard():
    """
    返回 index 页面静态文件.
    从 frontend/web/ 目录中返回 index.html 文件.
    """
    directory = os.path.join(app.root_path, "frontend", "web")
    return send_from_directory(directory, "index.html")

# 主程序
if __name__ == "__main__":
    app.run(debug=True)
