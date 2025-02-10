#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: student_api.py
完整存储路径: src/context_system/api/endpoints/student_api.py
功能介绍:
    实现学生数据录入 API 接口。
    接收前端提交的 JSON 数据，校验必填字段，并使用 SQLAlchemy
    将数据存入数据库。如遇错误则回滚事务并返回错误信息。
使用方法:
    API接口 URL: /api/student/add
    请求方法: POST
    请求内容类型: application/json
    参数: JSON格式数据，需包含 full_edu_id, name, school_code,
           vision_left, vision_right 等必填字段。
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from src.context_system.core.models.student import Student
from src.context_system.infrastructure.database import db

student_api = Blueprint('student_api', __name__)

@student_api.route('/api/student/add', methods=['POST'])
def add_student():
    """
    学生数据录入 API 接口
    接收前端 JSON 数据，校验必填字段，并将数据存入数据库。
    返回录入成功的信息及新生成的学生ID。
    """
    data = request.get_json()
    if (not data.get("full_edu_id") or not data.get("name") or
        not data.get("school_code") or data.get("vision_left") is None or
        data.get("vision_right") is None):
        return jsonify({"error": "必填字段缺失"}), 400
    try:
        student = Student(
            full_edu_id=data["full_edu_id"],
            school_code=data["school_code"],
            name=data["name"],
            vision_left=data["vision_left"],
            vision_right=data["vision_right"],
            myopia_level=None
        )
        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "录入成功", "id": student.id}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"数据库错误: {str(e)}"}), 500

