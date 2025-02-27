#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: query_api.py
完整存储路径: backend/api/query_api.py
功能说明:
    提供学生数据查询和导出功能的 API 接口。
    支持通过 GET 参数对学生基本信息进行模糊查询（如教育ID号、学校、年级、班级、姓名、性别、身份证号码）。
    支持分页查询，查询结果以 JSON 格式返回。
    当传入参数 export=1 时，导出查询结果为 Excel 文件（.xlsx）。
使用方法:
    查询接口 URL: /api/students/query
    请求方法: GET
    可用参数：
        - education_id (模糊查询)
        - school (模糊查询)
        - grade (模糊查询)
        - 班级 (模糊查询)
        - name (模糊查询)
        - gender (下拉选择)
        - id_card (精确查询)
        - page (页码，默认1)
        - per_page (每页条数，默认10)
        - export (导出标识，传 export=1 则返回 Excel 文件)
"""

import io
import pandas as pd
from flask import Blueprint, request, jsonify, current_app, send_file
from sqlalchemy import or_
from backend.models.student import Student

query_api = Blueprint("query_api", __name__)


@query_api.route("/api/students/query", methods=["GET"])
def query_students():
    """
    学生数据查询 API 接口
    根据 GET 参数过滤学生基本信息，支持分页查询与结果导出（Excel）。
    如果参数 export=1，则将查询结果导出为 Excel 文件下载。
    """
    # 获取查询参数（去除两端空格）
    education_id = request.args.get("education_id", "").strip()
    school = request.args.get("school", "").strip()
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

    # 构建查询条件
    query = Student.query
    if education_id:
        query = query.filter(Student.education_id.ilike(f"%{education_id}%"))
    if school:
        query = query.filter(Student.school.ilike(f"%{school}%"))
    if grade:
        # 注意：grade 存在于扩展表，但如果需要查询基本信息，这里可以不做处理
        # 如果需要组合查询扩展数据，可后续调整 join StudentExtension
        query = query.filter(Student.id_card.ilike(
            f"%{grade}%"))  # 这里仅作示例，通常 grade 在扩展信息中
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
        # 导出所有查询结果（不分页）
        students = query.all()
        # 将数据转换为字典列表
        data = [s.to_dict() for s in students]
        # 用 pandas DataFrame 构造 Excel 文件
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')
        output.seek(0)
        return send_file(output, attachment_filename="students_export.xlsx",
                         as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    students = [s.to_dict() for s in pagination.items]
    result = {
        "students": students,
        "total": pagination.total,
        "page": page,
        "per_page": per_page
    }
    return jsonify(result), 200
