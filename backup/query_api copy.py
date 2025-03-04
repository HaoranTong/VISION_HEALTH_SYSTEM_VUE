#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件功能说明：
实现学生数据查询和导出功能的API接口，支持组合查询、分页及Excel导出
包含重大逻辑修改：始终关联基本表和扩展表
"""

import io
import pandas as pd
import datetime
from flask import Blueprint, request, jsonify, send_file
from backend.models.student import Student
from backend.infrastructure.database import db
from backend.models.student_extension import StudentExtension
from sqlalchemy import and_

query_api = Blueprint("query_api", __name__)


def serialize_value(val):
    """处理不可序列化类型"""
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.isoformat()
    elif isinstance(val, (Student, StudentExtension)):
        return val.to_dict()
    else:
        return val


def record_to_dict(record):
    """将查询结果记录转换为字典格式（最小化修改版）"""
    def convert_dict(d):
        return {k: serialize_value(v) for k, v in d.items()}

    if isinstance(record, tuple):
        student, extension = record

        # 原代码结构完全保留，仅增加空值保护
        student_data = {}
        if student is not None:  # 新增空值判断
            if hasattr(student, "to_dict"):
                student_data = student.to_dict()
            else:
                student_data = dict(student._mapping)

        extension_data = {}
        if extension is not None:  # 新增空值判断
            if hasattr(extension, "to_dict"):
                extension_data = extension.to_dict()
            else:
                extension_data = dict(extension._mapping)

        # 原合并逻辑保持不变，仅增加空值替换
        combined = {**student_data, **extension_data}
        return {k: v if v is not None else '' for k, v in combined.items()}  # 新增空值处理

    # 以下代码保持原样
    elif hasattr(record, "to_dict"):
        return convert_dict(record.to_dict())
    else:
        return convert_dict(dict(record._mapping))


@query_api.route("/api/students/query", methods=["GET"])
def query_students():
    """核心查询逻辑（重大修改版本）"""
    # 获取查询参数
    education_id = request.args.get("education_id", "").strip()
    school = request.args.get("school", "").strip()
    data_year = request.args.get("data_year", "").strip()
    grade = request.args.get("grade", "").strip()
    class_name = request.args.get("班级", "").strip()
    name = request.args.get("name", "").strip()
    gender = request.args.get("gender", "").strip()
    id_card = request.args.get("id_card", "").strip()

    # 分页参数处理（保持不变）
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        per_page = 10

    # ================== 核心修改开始 ==================
    # 始终使用外连接查询（无论是否存在扩展表条件）
    query = db.session.query(Student, StudentExtension).outerjoin(
        StudentExtension, Student.id == StudentExtension.student_id
    )

    # 构建过滤条件
    filters = []

    # 基本表过滤条件
    if education_id:
        query = query.filter(Student.education_id.ilike(f"%{education_id}%"))
    if school:
        query = query.filter(Student.school.ilike(f"%{school}%"))
    if class_name:
        query = query.filter(Student.class_name.ilike(f"%{class_name}%"))
    if name:
        query = query.filter(Student.name.ilike(f"%{name}%"))
    if gender:
        query = query.filter(Student.gender == gender)
    if id_card:
        query = query.filter(Student.id_card == id_card)

    # 扩展表过滤条件
    if data_year:
        filters.append(StudentExtension.data_year == data_year)
    if grade:  # 修正字段映射
        filters.append(StudentExtension.grade.ilike(f"%{grade}%"))

    if filters:
        query = query.filter(and_(*filters))

    # 默认加载逻辑（新增）
    if not any([education_id, school, data_year, grade, class_name, name, gender, id_card]):
        query = query.limit(10)
    # ================== 核心修改结束 ==================

    # 导出处理逻辑（保持不变）
    export_flag = request.args.get("export", "0")
    if export_flag == "1":
        records = query.all()
        data = [record_to_dict(rec) for rec in records]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Students")
        output.seek(0)
        return send_file(
            output,
            download_name="students_export.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # 分页处理（保持不变）
    records = query.all()
    total = len(records)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_records = records[start:end]
    records_dict = [record_to_dict(rec) for rec in paginated_records]
    result = {
        "students": records_dict,
        "total": total,
        "page": page,
        "per_page": per_page
    }
    return jsonify(result), 200
