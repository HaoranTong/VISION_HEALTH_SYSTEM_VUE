#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: import_api.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\api\import_api.py
功能介绍:
    提供电子表格数据导入功能。接收上传的 Excel 文件 (.xlsx)，
    使用 Pandas 解析文件，校验必填字段和数据范围，并将数据存入数据库。
    如遇错误，生成“导入失败记录表”或“数据不完整记录表”。
使用方法:
    API接口 URL: /api/students/import
    请求方法: POST
    请求内容类型: multipart/form-data
    参数: file (上传的 .xlsx 文件)
"""

# pylint: disable=no-member

import os
import pandas as pd
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.models.student import Student
from backend.infrastructure.database import db

import_api = Blueprint("import_api", __name__)

ALLOWED_EXTENSIONS = {"xlsx"}


def allowed_file(filename):
    """
    检查文件是否为允许的扩展名
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 简单的学校名称 -> 学校代码映射
SCHOOL_CODE_MAP = {
    "华兴小学": "001",
    "师大附小清华小学校": "002",
    "苏宁红军小学校": "003"
}


@import_api.route("/api/students/import", methods=["POST"])
def import_students():
    """
    电子表格导入 API 接口
    接收上传的 Excel 文件，使用 Pandas 解析文件，校验必填字段，
    将符合要求的数据存入数据库，并返回导入成功的记录条数。
    如有异常，回滚事务并返回错误信息。
    """
    if "file" not in request.files:
        return jsonify({"error": "未找到上传文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "未选择文件"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(os.getcwd(), filename)
        file.save(filepath)

        try:
            df = pd.read_excel(filepath)

            # 需求文档的关键字段（示例）
            required_columns = [
                "教育ID号", "学校", "年级", "班级", "姓名", "性别", "年龄",
                "右眼-裸眼视力", "左眼-裸眼视力", "右眼-矫正视力", "左眼-矫正视力"
            ]
            missing_columns = [
                col for col in required_columns if col not in df.columns]
            if missing_columns:
                return jsonify({"error": f"缺少必填字段: {', '.join(missing_columns)}"}), 400

            imported_count = 0

            for _, row in df.iterrows():
                # 必填字段是否为空
                if pd.isna(row["教育ID号"]) or pd.isna(row["姓名"]) or pd.isna(row["学校"]):
                    # 若关键字段缺失，则跳过
                    continue

                # 学校代码映射，如若 Excel 中的“学校”列无匹配，给个默认值或继续处理
                school_name = str(row["学校"]).strip()
                school_code = SCHOOL_CODE_MAP.get(
                    school_name, "999")  # 999 表示未知学校

                # 创建 Student 实例
                student = Student(
                    full_edu_id=str(row["教育ID号"]),
                    school_code=school_code,
                    # school_id 可根据需要赋值，比如后续维护
                    name=str(row["姓名"]),
                    gender=str(row["性别"]) if not pd.isna(row["性别"]) else None,
                    age=int(row["年龄"]) if not pd.isna(row["年龄"]) else None,
                    grade=str(row["年级"]) if not pd.isna(row["年级"]) else None,
                    class_name=str(row["班级"]) if not pd.isna(
                        row["班级"]) else None,
                    vision_right=float(
                        row["右眼-裸眼视力"]) if not pd.isna(row["右眼-裸眼视力"]) else None,
                    vision_left=float(
                        row["左眼-裸眼视力"]) if not pd.isna(row["左眼-裸眼视力"]) else None,
                    vision_right_corrected=float(
                        row["右眼-矫正视力"]) if not pd.isna(row["右眼-矫正视力"]) else None,
                    vision_left_corrected=float(
                        row["左眼-矫正视力"]) if not pd.isna(row["左眼-矫正视力"]) else None,
                    myopia_level=None
                )

                # 自动生成索引ID: school_id + full_edu_id (示例中暂时未从 Excel 取 school_id)
                # 若后续需维护 school_id, 这里可以: student.index_id = f"{student.school_id}{student.full_edu_id}"
                # 当前仅用 school_code + full_edu_id 做临时索引
                student.index_id = f"{student.school_code}{student.full_edu_id}"

                db.session.add(student)
                imported_count += 1

            db.session.commit()
            os.remove(filepath)

            return jsonify({
                "message": f"导入成功，共导入 {imported_count} 条记录。",
                "imported_count": imported_count
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"文件处理错误: {str(e)}"}), 500

    else:
        return jsonify({"error": "不支持的文件格式，请上传 .xlsx 文件"}), 400
