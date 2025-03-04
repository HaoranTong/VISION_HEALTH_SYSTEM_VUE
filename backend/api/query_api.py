#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: query_api.py
完整存储路径: backend/api/query_api.py
功能说明：
    实现学生数据查询和导出接口。
    查询接口支持通过 GET 参数过滤数据，并返回 JSON 格式的分页结果。
    导出接口根据查询条件生成 Excel 文件供下载。
使用说明：
    查询接口 URL: /api/students/query
    导出接口 URL: /api/students/export
"""

import io
import datetime
import traceback
import pandas as pd
from flask import Blueprint, request, jsonify, send_file
from backend.models.student import Student
from backend.models.student_extension import StudentExtension
from backend.infrastructure.database import db
from sqlalchemy import and_

query_api = Blueprint("query_api", __name__)


def serialize_value(val):
    """处理日期等序列化问题"""
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.isoformat()
    return val if val is not None else ''


def record_to_dict(record):
    """
    将查询返回的记录转换为字典格式，兼容 SQLAlchemy 2.0 Row 对象
    预期 record 应为包含 (Student, StudentExtension) 的元组。
    """
    student = None
    extension = None
    try:
        # 尝试通过索引获取 ORM 对象
        student = record[0]
        extension = record[1] if len(record) > 1 else None
    except Exception:
        # 如果无法通过索引获取，则尝试使用 _mapping 属性
        if hasattr(record, "_mapping"):
            mapping = record._mapping
            student = mapping.get("Student") or mapping.get("students")
            extension = mapping.get("StudentExtension") or mapping.get(
                "student_extensions")
    student_data = student.to_dict() if (
        student and hasattr(student, "to_dict")) else {}
    extension_data = extension.to_dict() if (
        extension and hasattr(extension, "to_dict")) else {}
    combined = {**student_data, **extension_data}
    return {k: serialize_value(v) for k, v in combined.items()}


def build_query():
    """
    根据请求参数构造查询对象，返回查询和过滤条件列表。
    """
    education_id = request.args.get("education_id", "").strip()
    school = request.args.get("school", "").strip()
    data_year = request.args.get("data_year", "").strip()
    grade = request.args.get("grade", "").strip()
    class_name = request.args.get("class_name", "").strip()
    name = request.args.get("name", "").strip()
    gender = request.args.get("gender", "").strip()
    id_card = request.args.get("id_card", "").strip()

    query = db.session.query(Student, StudentExtension).outerjoin(
        StudentExtension, Student.id == StudentExtension.student_id
    )

    filters = []
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
    if data_year:
        filters.append(StudentExtension.data_year == data_year)
    if grade:
        filters.append(StudentExtension.grade.ilike(f"%{grade}%"))
    if filters:
        query = query.filter(and_(*filters))
    # 当无过滤条件时，默认只返回前10条数据
    if not any([education_id, school, data_year, grade, class_name, name, gender, id_card]):
        query = query.limit(10)
    return query


@query_api.route("/api/students/query", methods=["GET"])
def query_students():
    """
    学生数据查询接口
    返回 JSON 格式数据，包括学生记录、总记录数、当前页码和每页记录数
    """
    try:
        try:
            page = int(request.args.get("page", 1))
        except ValueError:
            page = 1
        try:
            per_page = int(request.args.get("per_page", 10))
        except ValueError:
            per_page = 10

        query = build_query()
        records = query.all()
        total = len(records)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_records = records[start:end]
        data = [record_to_dict(rec) for rec in paginated_records]

        return jsonify({
            "students": data,
            "total": total,
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        error_msg = traceback.format_exc()
        print("查询错误:", error_msg)
        return jsonify({"error": f"查询错误: {str(e)}"}), 500


@query_api.route("/api/students/export", methods=["GET"])
def export_students():
    """
    学生数据导出接口
    根据查询条件生成 Excel 文件，并通过 HTTP 返回供下载。
    如果传入参数 columns，则只导出该列配置选中的字段。
    """
    try:
        query = build_query()
        records = query.all()
        data = [record_to_dict(rec) for rec in records]
        if not data:
            return jsonify({"error": "没有符合条件的数据可导出"}), 404

        # 定义数据库字段到中文名称的映射
        COLUMN_NAME_MAPPING = {
            "education_id": "教育ID号",
            "school": "学校",
            "class_name": "班级",
            "name": "姓名",
            "gender": "性别",
            "age": "年龄",
            "id_card": "身份证号码",
            "birthday": "出生日期",
            "phone": "联系电话",
            "region": "区域",
            "contact_address": "联系地址",
            "parent_name": "家长姓名",
            "parent_phone": "家长电话",
            "data_year": "数据年份",
            "grade": "年级",
            "height": "身高",
            "weight": "体重",
            "diet_preference": "饮食偏好",
            "exercise_preference": "运动偏好",
            "health_education": "健康教育",
            "past_history": "既往史",
            "family_history": "家族史",
            "premature": "是否早产",
            "allergy": "过敏史",
            "right_eye_naked": "右眼-裸眼视力",
            "left_eye_naked": "左眼-裸眼视力",
            "right_eye_corrected": "右眼-矫正视力",
            "left_eye_corrected": "左眼-矫正视力",
            "right_keratometry_K1": "右眼-角膜曲率K1",
            "left_keratometry_K1": "左眼-角膜曲率K1",
            "right_keratometry_K2": "右眼-角膜曲率K2",
            "left_keratometry_K2": "左眼-角膜曲率K2",
            "right_axial_length": "右眼-眼轴",
            "left_axial_length": "左眼-眼轴",
            "right_sphere": "右眼屈光-球镜",
            "right_cylinder": "右眼屈光-柱镜",
            "right_axis": "右眼屈光-轴位",
            "left_sphere": "左眼屈光-球镜",
            "left_cylinder": "左眼屈光-柱镜",
            "left_axis": "左眼屈光-轴位",
            "right_dilated_sphere": "右眼散瞳-球镜",
            "right_dilated_cylinder": "右眼散瞳-柱镜",
            "right_dilated_axis": "右眼散瞳-轴位",
            "left_dilated_sphere": "左眼散瞳-球镜",
            "left_dilated_cylinder": "左眼散瞳-柱镜",
            "left_dilated_axis": "左眼散瞳-轴位",
            "vision_level": "【新增】视力等级",
            "right_anterior_depth": "右眼-前房深度",
            "left_anterior_depth": "左眼-前房深度",
            "other_info": "其他情况",
            "eye_fatigue": "眼疲劳状况",
            "frame_glasses": "框架眼镜",
            "contact_lenses": "隐形眼镜",
            "night_orthokeratology": "夜戴角膜塑型镜",
            "guasha": "刮痧",
            "aigiu": "艾灸",
            "zhongyao_xunzheng": "中药熏蒸",
            "rejiu_training": "热灸训练",
            "xuewei_tiefu": "穴位贴敷",
            "reci_pulse": "热磁脉冲",
            "baoguan": "拔罐",
            "right_eye_naked_interv": "右眼-干预-裸眼视力",
            "left_eye_naked_interv": "左眼-干预-裸眼视力",
            "right_sphere_interv": "右眼屈光-干预-球镜",
            "right_cylinder_interv": "右眼屈光-干预-柱镜",
            "right_axis_interv": "右眼屈光-干预-轴位",
            "left_sphere_interv": "左眼屈光-干预-球镜",
            "left_cylinder_interv": "左眼屈光-干预-柱镜",
            "left_axis_interv": "左眼屈光-干预-轴位",
            "right_dilated_sphere_interv": "右眼散瞳-干预-球镜",
            "right_dilated_cylinder_interv": "右眼散瞳-干预-柱镜",
            "right_dilated_axis_interv": "右眼散瞳-干预-轴位",
            "left_dilated_sphere_interv": "左眼散瞳-干预-球镜",
            "left_dilated_cylinder_interv": "左眼散瞳-干预-柱镜",
            "left_dilated_axis_interv": "左眼散瞳-干预-轴位",
            "interv_vision_level": "【新增】干预后视力等级",
            "left_naked_change": "【新增】左眼裸眼视力变化",
            "right_naked_change": "【新增】右眼裸眼视力变化",
            "left_sphere_change": "【新增】左眼屈光-球镜变化",
            "right_sphere_change": "【新增】右眼屈光-球镜变化",
            "left_cylinder_change": "【新增】左眼屈光-柱镜变化",
            "right_cylinder_change": "【新增】右眼屈光-柱镜变化",
            "left_axis_change": "【新增】左眼屈光-轴位变化",
            "right_axis_change": "【新增】右眼屈光-轴位变化",
            "left_interv_effect": "【新增】左眼视力干预效果",
            "right_interv_effect": "【新增】右眼视力干预效果",
            "left_sphere_effect": "【新增】左眼球镜干预效果",
            "right_sphere_effect": "【新增】右眼球镜干预效果",
            "left_cylinder_effect": "【新增】左眼柱镜干预效果",
            "right_cylinder_effect": "【新增】右眼柱镜干预效果",
            "left_axis_effect": "【新增】左眼轴位干预效果",
            "right_axis_effect": "【新增】右眼轴位干预效果",
            "interv1": "第1次干预",
            "interv2": "第2次干预",
            "interv3": "第3次干预",
            "interv4": "第4次干预",
            "interv5": "第5次干预",
            "interv6": "第6次干预",
            "interv7": "第7次干预",
            "interv8": "第8次干预",
            "interv9": "第9次干预",
            "interv10": "第10次干预",
            "interv11": "第11次干预",
            "interv12": "第12次干预",
            "interv13": "第13次干预",
            "interv14": "第14次干预",
            "interv15": "第15次干预",
            "interv16": "第16次干预"
        }

        df = pd.DataFrame(data)
        # 如果传入了 columns 参数，则只保留该部分列
        selected_columns = request.args.get("columns", None)
        if selected_columns:
            selected_columns = selected_columns.split(",")
            df = df[selected_columns]
        # 重命名列为中文
        df.rename(columns=COLUMN_NAME_MAPPING, inplace=True)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Students")
        output.seek(0)
        now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"students_export_{now_str}.xlsx"
        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"error": f"导出错误: {str(e)}"}), 500
