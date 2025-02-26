#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: calculation_api.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\api\calculation_api.py
功能介绍:
    提供手动触发计算扩展字段数据的 API 接口。该接口根据指定学生的基本数据和扩展数据，
    计算干预相关的计算字段（例如裸眼视力变化、干预后视力等级、干预效果等），
    并更新到 StudentExtension 表中，便于用户在数据修改或补充后随时重新计算更新相关字段。
使用方法:
    API接口 URL: /api/students/calculate/<student_id>
    请求方法: POST
    参数:
      student_id - 学生在 Student 表中的主键
"""

import warnings
from flask import Blueprint, jsonify

# 导入项目内部模块（先导入第三方，再导入内部模块）
from backend.infrastructure.database import db
from backend.models.student import Student
from backend.models.student_extension import StudentExtension

warnings.filterwarnings("ignore")

calculation_api = Blueprint("calculation_api", __name__)


def calculate_interv_effects(student_id):
    """
    根据指定学生的现有数据计算干预相关的扩展字段，并更新 StudentExtension 记录。

    示例计算逻辑（需根据实际业务规则调整）：
      - 计算裸眼视力变化：如果学生模型中包含干预后裸眼视力数据（例如 vision_left_post、vision_right_post），
        则计算裸眼视力变化 = 干预后裸眼视力 - 干预前裸眼视力。
      - 根据裸眼视力变化判断干预效果（例如“上升”、“维持”、“下降”）。

    参数:
      student_id (int): 学生在 Student 表中的主键

    返回:
      tuple(bool, str): 计算成功返回 (True, "成功消息")，失败返回 (False, 错误消息)
    """
    student = Student.query.get(student_id)
    extension = StudentExtension.query.filter_by(student_id=student_id).first()
    if not student or not extension:
        return False, "学生或扩展记录不存在。"
    try:
        # 示例计算裸眼视力变化，假设学生中有 vision_left_post 与 vision_right_post 字段
        if hasattr(student, 'vision_left_post') and student.vision_left_post is not None:
            extension.left_naked_vision_change = (
                student.vision_left_post - student.vision_left
            )
        if hasattr(student, 'vision_right_post') and student.vision_right_post is not None:
            extension.right_naked_vision_change = (
                student.vision_right_post - student.vision_right
            )

        # 根据裸眼视力变化判断干预效果（示例逻辑，请根据需求调整）
        def determine_effect(change):
            if change is None:
                return None
            if change > 0.1:
                return "上升"
            elif change < -0.1:
                return "下降"
            else:
                return "维持"

        extension.left_interv_effect = determine_effect(
            extension.left_naked_vision_change
        )
        extension.right_interv_effect = determine_effect(
            extension.right_naked_vision_change
        )

        # 此处可添加其他计算逻辑，如计算干预后视力等级、球镜变化等

        # pylint: disable=no-member
        db.session.commit()
        return True, "计算更新成功。"
    except Exception as e:  # pylint: disable=broad-exception-caught
        # pylint: disable=no-member
        db.session.rollback()
        return False, str(e)


@calculation_api.route("/api/students/calculate/<int:student_id>", methods=["POST"])
def calculate_for_student(student_id):
    """
    手动触发指定学生扩展字段数据计算的 API 接口。

    请求示例：
      POST /api/students/calculate/1

    返回:
      JSON 格式结果，包含成功或错误消息。
    """
    success, msg = calculate_interv_effects(student_id)
    if success:
        return jsonify({"message": msg}), 200
    else:
        return jsonify({"error": msg}), 500
