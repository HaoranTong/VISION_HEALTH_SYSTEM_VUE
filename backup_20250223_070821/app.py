# 文件名称：app.py
# 完整路径：E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\app.py
# 功能说明：Flask应用主入口，包含数据库初始化、路由定义和菜单API
# 使用说明：直接运行或通过run.ps1启动

import os
from datetime import datetime
from flask import Flask, render_template, jsonify
from backend.infrastructure.database import db


def create_app():
    # 初始化Flask应用
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'frontend/templates'),
                static_folder=os.path.join(base_dir, 'frontend/static'))

    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "instance/app.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # 初始化数据库表
    with app.app_context():
        try:
            from backend.models.student import Student
            db.create_all()
        except Exception as e:
            print(f"数据库初始化错误: {str(e)}")

    # ================= 路由定义 =================
    @app.route('/')
    def index():
        stats = {"total_students": 0,
                 "current_time": datetime.now().strftime('%Y-%m-%d %H:%M')}
        try:
            from backend.models.student import Student
            stats["total_students"] = db.session.query(Student).count()
        except Exception as e:
            print(f"数据库查询错误: {str(e)}")
        return render_template('index.html', **stats)

    @app.route('/api/menu')
    def get_menu():
        return jsonify([
            {"title": "首页", "link": "/", "icon": "bi-house-door", "sub_menu": []},
            {"title": "数据管理", "link": "#", "icon": "bi-folder", "sub_menu": [
                {"title": "数据导入", "link": "/import", "icon": "bi-upload"},
                {"title": "数据修改", "link": "/modify", "icon": "bi-pencil"}
            ]},
            {"title": "数据查询", "link": "/query",
                "icon": "bi-search", "sub_menu": []},
            {"title": "统计分析", "link": "#", "icon": "bi-bar-chart-line", "sub_menu": [
                {"title": "视力分布", "link": "/analysis/vision", "icon": "bi-pie-chart"},
                {"title": "趋势分析", "link": "/analysis/trend", "icon": "bi-graph-up"}
            ]},
            {"title": "系统管理", "link": "#", "icon": "bi-gear", "sub_menu": [
                {"title": "用户管理", "link": "/admin/users", "icon": "bi-people"},
                {"title": "日志审计", "link": "/admin/logs", "icon": "bi-journal-text"}
            ]}
        ])

    return app


if __name__ == '__main__':
    create_app().run(debug=False)
