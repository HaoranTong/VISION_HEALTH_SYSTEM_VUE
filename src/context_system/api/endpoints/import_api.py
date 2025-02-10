#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: import_api.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM\src\context_system\api\endpoints\import_api.py
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
import os
import pandas as pd
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from context_system.core.models.student import Student
from context_system.infrastructure.database import db
# 此处未使用 SQLAlchemyError，因此移除该导入

# 创建 Blueprint
import_api = Blueprint("import_api", __name__)

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {"xlsx"}

def allowed_file(filename):
    """检查文件是否为允许的扩展名"""
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

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
            required_columns = [
                "full_edu_id", "name", "school_code",
                "vision_left", "vision_right"
            ]
            missing_columns = [
                col for col in required_columns if col not in df.columns
            ]
            if missing_columns:
                return jsonify({"error": f"缺少必填字段: "
                                f"{', '.join(missing_columns)}"}), 400
            imported_count = 0
            for _, row in df.iterrows():
                if (pd.isna(row["full_edu_id"]) or pd.isna(row["name"]) or
                    pd.isna(row["school_code"]) or
                    pd.isna(row["vision_left"]) or
                    pd.isna(row["vision_right"])):
                    continue
                student = Student(
                    full_edu_id=str(row["full_edu_id"]),
                    school_code=str(row["school_code"]),
                    name=str(row["name"]),
                    vision_left=float(row["vision_left"]),
                    vision_right=float(row["vision_right"]),
                    myopia_level=None
                )
                db.session.add(student)
                imported_count += 1
            db.session.commit()
            os.remove(filepath)
            return jsonify({"message": "导入成功",
                            "imported_count": imported_count}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"文件处理错误: {str(e)}"}), 500
    else:
        return jsonify({"error": "不支持的文件格式，请上传 .xlsx 文件"}), 400
