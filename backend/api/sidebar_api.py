#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: sidebar_api.py
完整存储路径: backend/api/sidebar_api.py
功能说明:
    提供侧边栏菜单数据 API 接口，返回 JSON 格式的菜单数据。
    修改后 "数据查询" 菜单增加二级子菜单，确保点击时展示子菜单而非直接跳转。
使用说明:
    通过 GET 请求访问 /api/menu 获取菜单数据。
"""

from flask import Blueprint, jsonify

sidebar_api = Blueprint('sidebar_api', __name__)

menu_data = [
    {
        "title": "首页",
        "link": "/",
        "icon": "bi-house-door",
        "sub_menu": []
    },
    {
        "title": "数据管理",
        "link": "#",
        "icon": "bi-folder",
        "sub_menu": [
            {"title": "数据导入", "link": "/import", "icon": "bi-upload"},
            {"title": "数据修改", "link": "modify", "icon": "bi-pencil"}
        ]
    },
    {
        "title": "数据查询",
        "link": "query",
        "icon": "bi-search",
        "sub_menu": []
    },
    {
        "title": "统计分析",
        "link": "#",
        "icon": "bi-bar-chart-line",
        "sub_menu": [
            {"title": "视力分布", "link": "#vision-distribution", "icon": "bi-pie-chart"},
            {"title": "趋势分析", "link": "#vision-change", "icon": "bi-graph-up"}
        ]
    },
    {
        "title": "系统管理",
        "link": "#",
        "icon": "bi-gear",
        "sub_menu": []
    }
]


@sidebar_api.route('/api/menu')
def get_menu():
    """
    返回侧边栏菜单 JSON 数据.
    Returns:
        JSON: 菜单数据列表.
    """
    return jsonify(menu_data)
