# 文件名称: sidebar_api.py
# 完整路径: backend/api/sidebar_api.py

from flask import Blueprint, jsonify

sidebar_api = Blueprint('sidebar_api', __name__)

# 假设菜单数据存储在配置中或数据库中
menu_data = [
    {
        "title": "首页",
        "link": "#",
        "icon": "bi-house-door",
        "sub_menu": []
    },
    {
        "title": "数据管理",
        "link": "#",
        "icon": "bi-folder",
        "sub_menu": [
            {"title": "数据导入", "link": "#import", "icon": "bi-upload"},
            {"title": "数据修改", "link": "#modify", "icon": "bi-pencil"}
        ]
    },
    {
        "title": "数据查询",
        "link": "#",
        "icon": "bi-search",
        "sub_menu": []
    },
    {
        "title": "统计分析",
        "link": "#",
        "icon": "bi-bar-chart-line",
        "sub_menu": [
            {"title": "视力分布", "link": "#vision-distribution", "icon": "bi-pie-chart"},
            {"title": "视力变化", "link": "#vision-change", "icon": "bi-arrow-up-down"}
        ]
    },
    {
        "title": "系统管理",
        "link": "#",
        "icon": "bi-gear",
        "sub_menu": []
    }
]
