#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: clear_db.py
完整存储路径: Projects/VISION_HEALTH_SYSTEM_VUE/clear_db.py
功能介绍:
    清空数据库中学生表（students）和学生扩展信息表（student_extensions）的数据，
    用于测试前的清理工作。
使用方法:
    在项目根目录下运行：python clear_db.py
"""

from app import app  # 从项目根目录下导入 Flask 应用实例
from backend.infrastructure.database import db
from backend.models.student import Student
from backend.models.student_extension import StudentExtension

with app.app_context():
    # 清空扩展信息表
    db.session.query(StudentExtension).delete()
    # 清空学生表
    db.session.query(Student).delete()
    db.session.commit()
    print("学生表和学生扩展信息表数据已清空。")
