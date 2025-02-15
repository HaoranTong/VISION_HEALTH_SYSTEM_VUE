#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: app.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\app.py
功能介绍:
    初始化 Flask 应用、加载配置、初始化数据库，并注册各个 API 蓝图及页面路由。
    模板文件存放在 E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\frontend\web 目录下，
    页面通过 render_template 渲染，且模板中使用 Jinja2 包含公共组件（sidebar.html、topnav.html）。
    为防止 __debugger__ 请求中传入非字符串模板名导致递归错误，重写了 jinja_env.autoescape，
    并在函数中打印传入的模板名称以便调试。
使用方法:
    启动命令: python app.py
    访问首页: http://localhost:5000/ 或 http://localhost:5000/index.html
    访问学生详情页: http://localhost:5000/student_detail.html?id=1
"""

from flask import Flask, render_template
from backend.infrastructure.database import db
from backend.api.student_api import student_api
from backend.api.query_api import query_api
from backend.api.import_api import import_api
from backend.api.analysis_api import analysis_api
from backend.api.calculation_api import calculation_api
# 如未实现 advanced_query_api 模块可暂时注释掉
# from backend.api.advanced_query_api import advanced_query_api
from config.app.config import DevelopmentConfig

# 指定模板目录为 frontend/web
app = Flask(__name__, static_folder="frontend/static",
            template_folder="frontend/web")
app.config.from_object(DevelopmentConfig)


def custom_autoescape(template_name):
    """
    自定义 autoescape 函数：
      - 如果 template_name 不是字符串，返回 False；
      - 如果模板名称中包含查询参数（例如 "?__debugger__=..."），移除查询参数；
      - 如果模板名称包含 '__debugger__'，返回 False；
      - 否则，检查是否以 ('.html', '.htm', '.xml', '.xhtml') 结尾。
    """
    print("Autoescape called with:", repr(template_name))
    if not isinstance(template_name, str):
        return False
    # 移除查询参数部分
    if "?" in template_name:
        template_name = template_name.split("?", 1)[0]
    if "__debugger__" in template_name:
        return False
    return template_name.lower().endswith(('.html', '.htm', '.xml', '.xhtml'))


app.jinja_env.autoescape = custom_autoescape

db.init_app(app)

# 注册 API 蓝图
app.register_blueprint(student_api)
app.register_blueprint(query_api)
app.register_blueprint(import_api)
app.register_blueprint(analysis_api)
app.register_blueprint(calculation_api)
# app.register_blueprint(advanced_query_api)


@app.route("/")
@app.route("/index.html")
def index():
    """
    渲染系统首页模板。
    :return: 渲染后的 index.html 页面
    """
    return render_template("index.html")


@app.route("/student_detail.html")
def student_detail():
    """
    渲染学生详情页模板。
    :return: 渲染后的 student_detail.html 页面
    """
    return render_template("student_detail.html")


if __name__ == "__main__":
    app.run(debug=True)
