#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: analysis_api.py
完整存储路径: src/context_system/api/endpoints/analysis_api.py
功能介绍:
    提供统计分析 API 接口，用于根据数据库中学生数据生成统计数据。
    返回学生总数、平均左眼视力和平均右眼视力等指标。
使用方法:
    API接口 URL: /api/analysis/statistics
    请求方法: GET
"""
from flask import Blueprint, jsonify
from src.context_system.core.models.student import Student
from src.context_system.infrastructure.database import db
from sqlalchemy import func

# 创建 Blueprint
analysis_api = Blueprint('analysis_api', __name__)

@analysis_api.route('/api/analysis/statistics', methods=['GET'])
def statistics():
    """
    统计分析 API 接口
    返回学生总数、平均左眼视力和平均右眼视力等统计数据。
    如出现异常，返回错误信息。
    """
    try:
        total_students = Student.query.count()
        avg_vision_left = db.session.query(
            func.avg(Student.vision_left)).scalar() or 0
        avg_vision_right = db.session.query(
            func.avg(Student.vision_right)).scalar() or 0
        result = {
            "total_students": total_students,
            "average_vision_left": round(avg_vision_left, 2),
            "average_vision_right": round(avg_vision_right, 2)
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"统计分析错误: {str(e)}"}), 500

