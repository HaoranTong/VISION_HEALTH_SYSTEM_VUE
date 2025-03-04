#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: query_api.py
完整存储路径: backend/api/query_api.py
功能说明:
    提供学生数据查询和导出功能的 API 接口。
    支持通过 GET 参数对学生基本信息及扩展信息进行查询，查询条件包括：
      - education_id（模糊查询）
      - school（模糊查询）
      - data_year（精确匹配，用于查询学生扩展信息所属年份）
      - grade（模糊查询，基于 StudentExtension.grade）
      - 班级（模糊查询）
      - name（模糊查询）
      - gender（下拉选择）
      - id_card（精确查询）
    当传入 data_year 或 grade 参数时，执行关联查询 Student 和 StudentExtension，
    返回的记录为 (Student, StudentExtension) 的元组，并通过 record_to_dict() 函数合并输出数据。
    支持分页查询，查询结果以 JSON 格式返回；
    当传入 export=1 时，将查询结果导出为 Excel 文件 (.xlsx)。
使用方法:
    1. 默认查询：GET /api/students/query
    2. 带 data_year、grade 查询：GET /api/students/query?data_year=2023&grade=三年级
    3. 导出：GET /api/students/query?export=1&data_year=2023
变更说明:
    1. 修改 send_file 调用，使用 download_name 参数（替代 attachment_filename）。
    2. 调整 record_to_dict 函数，增加对 datetime 类型数据的处理，并判断关联查询中 extension 是否为 None。
    3. 修改关联查询逻辑：当 data_year 或 grade 参数存在时均执行关联查询 StudentExtension，
       并修正了关联查询部分的缩进问题，解决了 invalid syntax 错误。
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
    """处理所有不可序列化的类型，如 datetime 类型转换为 ISO 格式字符串"""
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.isoformat()
    elif isinstance(val, (Student, StudentExtension)):
        # 如果出现模型对象，调用 to_dict()
        return val.to_dict()
    else:
        return val


def record_to_dict(record):
    """
    将查询结果记录转换为字典格式。
    处理两种情况：
      - 如果记录是元组 (Student, StudentExtension)，则分别调用 to_dict（如果存在）或使用 dict() 转换，
        并合并两个字典后返回。
      - 如果记录不是元组，则尝试调用 to_dict()，如果不存在则使用 _mapping 属性转换为字典。
    """
    def convert_dict(d):
        return {k: serialize_value(v) for k, v in d.items()}

    if isinstance(record, tuple):
        student, extension = record
        # 处理 Student 部分
        if hasattr(student, "to_dict"):
            student_data = student.to_dict()
        else:
            student_data = dict(student._mapping)
        # 处理 StudentExtension 部分（允许为空）
        extension_data = {}
        if extension is not None:
            if hasattr(extension, "to_dict"):
                extension_data = extension.to_dict()
            else:
                extension_data = dict(extension._mapping)
        combined = {**student_data, **extension_data}
        return convert_dict(combined)
    elif hasattr(record, "to_dict"):
        return convert_dict(record.to_dict())
    else:
        return convert_dict(dict(record._mapping))


@query_api.route("/api/students/query", methods=["GET"])
def query_students():
    """
    学生数据查询 API 接口
    根据 GET 参数过滤学生基本信息及扩展信息，支持分页查询与结果导出（Excel）。
    当传入 data_year 或 grade 参数时，执行关联查询 Student 和 StudentExtension。
    """
    # 获取查询参数（去除两端空格）
    education_id = request.args.get("education_id", "").strip()
    school = request.args.get("school", "").strip()
    data_year = request.args.get("data_year", "").strip()
    grade = request.args.get("grade", "").strip()
    class_name = request.args.get("班级", "").strip()
    name = request.args.get("name", "").strip()
    gender = request.args.get("gender", "").strip()
    id_card = request.args.get("id_card", "").strip()

    # 分页参数
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        per_page = 10

    # 构建查询：如果传入 data_year 或 grade，则执行关联查询以获取扩展信息
    if data_year or grade:
        # 使用外连接，确保即使扩展信息不存在也能返回学生记录
        query = db.session.query(Student, StudentExtension).outerjoin(
            StudentExtension, Student.id == StudentExtension.student_id
        )
        filters = []
        if data_year:
            filters.append(StudentExtension.data_year == data_year)
        if grade:
            filters.append(StudentExtension.grade.ilike(f"%{grade}%"))
        if filters:
            query = query.filter(and_(*filters))
    else:
        query = Student.query

    # 其他条件应用在 Student 表上
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

    # 判断是否需要导出结果
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
            # 使用 download_name 参数替换 attachment_filename
            download_name="students_export.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # 分页处理：由于关联查询返回的是列表，采用手动分页
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
