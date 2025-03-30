#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: import_api.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\api\import_api.py
功能说明:
    提供学生数据导入功能。支持上传 Excel (.xlsx) 和 CSV (.csv) 文件，
    使用 Pandas 解析文件，对每行数据进行必填字段校验与数据格式转换。
    合格记录写入数据库：
      - 学生基本信息保存在 Student 表（不随时间变化的字段）；
      - 随时间变化的数据保存在 StudentExtension 表，包含 data_year 字段。
    重复检测基于 education_id 与 data_year 的组合：
      - 若同一 education_id 且 data_year 相同，则执行部分更新（基本信息和扩展信息中空字段补充，不覆盖已有数据）；
      - 若同一 education_id 但 data_year 不同，则在扩展信息表中新增一条记录。
    数据导入后，会调用统计计算模块，对单条记录进行计算，
    更新扩展记录中存储的计算结果（如左眼裸眼视力变化及其标签）。
使用方法:
    API接口 URL: /api/students/import
    请求方法: POST
    请求内容类型: multipart/form-data
    参数:
      - file: 上传的 .xlsx 或 .csv 文件
      - data_year: 数据年份（由前端下拉选择，格式为4位字符串，如 "2024"）
"""
import traceback
import os
import time
from datetime import datetime

import pandas as pd
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.database import db
from backend.models.student import Student

# 导入统计计算模块（单记录内计算函数）
from backend.services.vision_calculation import calculate_within_year_change

ALLOWED_EXTENSIONS = {"xlsx", "csv"}

# 临时上传文件保存目录（用于保存上传过程中产生的临时文件）
TEMP_UPLOAD_DIR = os.path.join(os.getcwd(), "temp_uploads")
if not os.path.exists(TEMP_UPLOAD_DIR):
    os.makedirs(TEMP_UPLOAD_DIR)

# 失败记录文件保存目录（公开可下载）
FAILURE_UPLOAD_DIR = os.path.join(os.getcwd(), "frontend", "static", "uploads")
if not os.path.exists(FAILURE_UPLOAD_DIR):
    os.makedirs(FAILURE_UPLOAD_DIR)


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许上传"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_row(row, required_fields, row_index: int):
    """
    校验一行数据是否满足必填字段和基本格式要求。
    返回 (is_valid, errors_list)
    """
    errors = []
    # 必填字段：教育ID号、学校、班级、姓名、性别
    for field in required_fields:
        if pd.isna(row.get(field, None)):
            errors.append(f"第{row_index+2}行: 缺失必填字段 '{field}'")
    # 校验裸眼视力范围（右眼-裸眼视力与左眼-裸眼视力），如果提供则进行校验
    for field in ["右眼-裸眼视力", "左眼-裸眼视力"]:
        if not pd.isna(row.get(field, None)):
            try:
                value = float(row.get(field, 0))
                if value < 0.1 or value > 5.0:
                    errors.append(
                        f"第{row_index+2}行: '{field}' 值 {value} 不在合理范围(0.1-5.0)")
            except ValueError:
                errors.append(f"第{row_index+2}行: '{field}' 格式错误")
    return (len(errors) == 0, errors)


def partial_update_student(student_obj, ext_obj, row, row_index: int, errors: list) -> bool:
    """
    对已有记录进行部分更新：
      - 对基本信息（Student 表）：仅更新为空的字段，不覆盖已有数据。
      - 对扩展信息（StudentExtension 表）：仅更新为空的字段，不覆盖已有数据。
    示例中更新姓名、身份证号码、家长姓名、家长电话、联系电话、联系地址、出生日期等字段。
    返回 True 表示更新成功，否则返回 False。
    """
    # 基本信息更新
    row_val = row.get("姓名", None)
    if not pd.isna(row_val):
        if student_obj.name is None or student_obj.name.strip() == "":
            student_obj.name = str(row_val).strip()
    row_val = row.get("身份证号码", None)
    if not pd.isna(row_val):
        if student_obj.id_card is None or student_obj.id_card.strip() == "":
            student_obj.id_card = str(row_val).strip()
    row_val = row.get("家长姓名", None)
    if not pd.isna(row_val):
        if student_obj.parent_name is None or student_obj.parent_name.strip() == "":
            student_obj.parent_name = str(row_val).strip()
    row_val = row.get("家长电话", None)
    if not pd.isna(row_val):
        if student_obj.parent_phone is None or student_obj.parent_phone.strip() == "":
            student_obj.parent_phone = str(row_val).strip()
    row_val = row.get("联系电话", None)
    if not pd.isna(row_val):
        if student_obj.phone is None or student_obj.phone.strip() == "":
            student_obj.phone = str(row_val).strip()
    row_val = row.get("联系地址", None)
    if not pd.isna(row_val):
        if student_obj.contact_address is None or student_obj.contact_address.strip() == "":
            student_obj.contact_address = str(row_val).strip()
    if "出生日期" in row and not pd.isna(row["出生日期"]):
        try:
            bd = pd.to_datetime(row["出生日期"]).date()
            if student_obj.birthday is None:
                student_obj.birthday = bd
        except Exception as e:
            errors.append(f"第{row_index+2}行: '出生日期' 格式错误: {str(e)}")
            return False

    # 扩展信息更新示例（仅处理部分字段，此处可扩展）
    row_val = row.get("年级", None)
    if not pd.isna(row_val):
        if ext_obj.grade is None or ext_obj.grade.strip() == "":
            ext_obj.grade = str(row_val).strip()
    row_val = row.get("身高", None)
    if not pd.isna(row_val):
        try:
            h = float(row_val)
            if ext_obj.height is None:
                ext_obj.height = h
        except ValueError:
            errors.append(f"第{row_index+2}行: '身高' 数据格式错误")
            return False
    # ...（其它扩展字段更新逻辑）
    return True


import_api = Blueprint("import_api", __name__)


@import_api.route("/api/students/import", methods=["POST"])
def import_students():

    # ============== 这里开始替换代码 ==============
    # 基础校验（不在try块内）
    if 'file' not in request.files:
        current_app.logger.error("未找到上传文件")
        return jsonify({"error": "未找到上传文件"}), 400

    file = request.files['file']
    if file.filename == '':
        current_app.logger.error("收到空文件名")
        return jsonify({"error": "未选择文件"}), 400

    # 核心处理逻辑（用完整的try-except包裹）
    try:
        current_app.logger.debug("=== 开始处理请求 ===")
        current_app.logger.debug(f"请求表单数据: {request.form}")
        current_app.logger.debug(f"请求文件: {request.files}")

        filename = secure_filename(file.filename)
        current_app.logger.debug(f"DEBUG: 原始文件名: {file.filename}")
        current_app.logger.debug(f"DEBUG: secure_filename 后: {filename}")

        if '.' not in filename:
            current_app.logger.error("文件名缺少扩展名")
            return jsonify({"error": "文件名缺少扩展名"}), 400

        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            current_app.logger.error(f"不支持的文件扩展名 .{ext}")
            return jsonify({"error": f"不支持的文件扩展名 .{ext}"}), 400

        temp_filepath = os.path.join(
            TEMP_UPLOAD_DIR, f"upload_{int(time.time())}.{ext}")
        file.save(temp_filepath)

        current_app.logger.debug(f"文件已成功保存到: {temp_filepath}")

    except Exception as e:
        current_app.logger.error(f"文件处理异常: {str(e)}")
        if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return jsonify({"error": f"文件处理错误: {str(e)}"}), 500
    # ============== 这里结束替换代码 ==============

    """
    学生数据导入接口
    处理上传的 Excel 或 CSV 文件，解析数据，对每行数据进行必填字段校验和格式转换，
    合格记录写入基本信息表（Student）和扩展信息表（StudentExtension）。
    重复检测基于 education_id 与 data_year 的组合：
      - 若同一 education_id 且 data_year 相同，则执行部分更新（仅补充为空的字段，不覆盖已有数据）；
      - 若同一 education_id 但 data_year 不同，则在扩展信息表中新增一条记录（基本信息表不变）。
    校验失败的记录生成上传失败记录表（仅包含失败行，错误信息标红），并返回上传结果。
    """
    if "file" not in request.files:
        return jsonify({"error": "未找到上传文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "未选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件格式，请上传 .xlsx 或 .csv 文件"}), 400

    data_year = request.form.get("data_year")
    if not data_year:
        return jsonify({"error": "未提供数据年份"}), 400

    current_app.logger.debug(f"DEBUG: 原始上传文件名: {file.filename}")
    filename = secure_filename(file.filename)
    current_app.logger.debug(f"DEBUG: secure_filename 后的文件名: {filename}")
    temp_filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
    file.save(temp_filepath)

    # ============== 这里开始插入/替换代码 ==============
    # 安全处理文件名和扩展名
    filename = secure_filename(file.filename)
    current_app.logger.debug(f"DEBUG: 原始文件名: {file.filename}")
    current_app.logger.debug(f"DEBUG: secure_filename 后: {filename}")

    # 增强扩展名提取
    if '.' not in filename:
        return jsonify({"error": "文件名缺少扩展名"}), 400
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"不支持的文件扩展名 .{ext}"}), 400

    temp_filepath = os.path.join(
        TEMP_UPLOAD_DIR, f"upload_{int(time.time())}.{ext}")
    # ============== 这里结束插入代码 ==============

    try:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'xlsx':
            df = pd.read_excel(temp_filepath, dtype=str)
        elif ext == 'csv':
            df = pd.read_csv(temp_filepath, dtype=str)
        else:
            os.remove(temp_filepath)
            return jsonify({"error": "不支持的文件格式"}), 400

        df.columns = df.columns.str.strip()
        current_app.logger.debug(f"DEBUG: DataFrame 列名： {list(df.columns)}")

        # ============== 这里开始插入代码 ==============
        # 增强调试日志
        current_app.logger.debug("=== 文件解析诊断日志 ===")
        current_app.logger.debug(f"文件类型: {ext}")
        current_app.logger.debug(f"原始列名: {df.columns.tolist()}")
        current_app.logger.debug(f"总行数(解析后): {len(df)}")
        if len(df) > 0:
            current_app.logger.debug("首行数据样例:")
            for col, val in df.iloc[0].items():
                current_app.logger.debug(f"  {col}: {repr(val)}")
            current_app.logger.debug("末行数据样例:")
            for col, val in df.iloc[-1].items():
                current_app.logger.debug(f"  {col}: {repr(val)}")
        else:
            current_app.logger.warning("警告: 解析到空DataFrame")
# ============== 这里结束插入代码 ==============

        current_app.logger.debug(f"DEBUG: DataFrame 行数： {len(df)}")
        current_app.logger.debug(
            f"DEBUG: DataFrame 前5行数据： {df.head().to_string()}")

        required_fields = ["教育ID号", "学校", "班级", "姓名", "性别"]
        imported_count = 0
        error_messages = []
        failed_rows = set()

        from backend.models.student_extension import StudentExtension

        for index, row in df.iterrows():
            is_valid, errors_req = validate_row(row, required_fields, index)
            if not is_valid:
                error_messages.extend(errors_req)
                failed_rows.add(index)
                continue

            edu_id = row["教育ID号"].strip()
            existing_student = Student.query.filter_by(
                education_id=edu_id).first()
            existing_extension = None
            if existing_student:
                existing_extension = StudentExtension.query.filter_by(
                    student_id=existing_student.id, data_year=data_year).first()

            if existing_student and existing_extension:
                local_errors = []
                success_update = partial_update_student(
                    existing_student, existing_extension, row, index, local_errors)
                if not success_update:
                    error_messages.extend(local_errors)
                    failed_rows.add(index)
                else:
                    # 调用单记录计算函数更新计算字段
                    from backend.services.vision_calculation import calculate_within_year_change
                    calc_result = calculate_within_year_change(
                        existing_extension)
                    for key, value in calc_result.items():
                        setattr(existing_extension, key, value)
                    imported_count += 1
            else:
                if not existing_student:
                    try:
                        student = Student(
                            education_id=row["教育ID号"].strip(),
                            school=row["学校"].strip(),
                            class_name=row["班级"].strip(),
                            name=row["姓名"].strip(),
                            gender=row["性别"].strip(),
                            id_card=row["身份证号码"].strip() if (
                                "身份证号码" in row and not pd.isna(row["身份证号码"])) else None,
                            birthday=pd.to_datetime(row["出生日期"]).date() if (
                                "出生日期" in row and not pd.isna(row["出生日期"])) else None,
                            phone=row["联系电话"].strip() if (
                                "联系电话" in row and not pd.isna(row["联系电话"])) else None,
                            region=row["区域"].strip() if (
                                "区域" in row and not pd.isna(row["区域"])) else None,
                            contact_address=row["联系地址"].strip() if (
                                "联系地址" in row and not pd.isna(row["联系地址"])) else None,
                            parent_name=row["家长姓名"].strip() if (
                                "家长姓名" in row and not pd.isna(row["家长姓名"])) else None,
                            parent_phone=row["家长电话"].strip() if (
                                "家长电话" in row and not pd.isna(row["家长电话"])) else None
                        )
                        db.session.add(student)
                        db.session.flush()  # 获取 student.id
                    except (ValueError, SQLAlchemyError) as e:
                        error_messages.append(
                            f"第{index+2}行: 基本信息数据写入错误: {str(e)}")
                        failed_rows.add(index)
                        continue
                else:
                    student = existing_student

                # 新建扩展信息记录（StudentExtension）

                try:
                    extension = StudentExtension(
                        student_id=student.id,
                        data_year=data_year,
                        grade=row["年级"].strip() if (
                            "年级" in row and not pd.isna(row["年级"])) else None,
                        age=int(row["年龄"]) if (
                            "年龄" in row and not pd.isna(row["年龄"])) else None,
                        height=float(row["身高"]) if not pd.isna(
                            row.get("身高")) else None,
                        weight=float(row["体重"]) if not pd.isna(
                            row.get("体重")) else None,
                        diet_preference=row["饮食偏好"].strip() if (
                            "饮食偏好" in row and not pd.isna(row["饮食偏好"])) else None,
                        exercise_preference=row["运动偏好"].strip() if (
                            "运动偏好" in row and not pd.isna(row["运动偏好"])) else None,
                        health_education=row["健康教育"].strip() if (
                            "健康教育" in row and not pd.isna(row["健康教育"])) else None,
                        past_history=row["既往史"].strip() if (
                            "既往史" in row and not pd.isna(row["既往史"])) else None,
                        family_history=row["家族史"].strip() if (
                            "家族史" in row and not pd.isna(row["家族史"])) else None,
                        premature=row["是否早产"].strip() if (
                            "是否早产" in row and not pd.isna(row["是否早产"])) else None,
                        allergy=row["过敏史"].strip() if (
                            "过敏史" in row and not pd.isna(row["过敏史"])) else None,
                        frame_glasses=True if str(
                            row.get("框架眼镜", "")).strip() == "是" else False,
                        contact_lenses=True if str(
                            row.get("隐形眼镜", "")).strip() == "是" else False,
                        night_orthokeratology=True if str(
                            row.get("夜戴角膜塑型镜", "")).strip() == "是" else False,
                        guasha=True if str(
                            row.get("刮痧", "")).strip() == "是" else False,
                        aigiu=True if str(
                            row.get("艾灸", "")).strip() == "是" else False,
                        zhongyao_xunzheng=True if str(
                            row.get("中药熏蒸", "")).strip() == "是" else False,
                        rejiu_training=True if str(
                            row.get("热灸训练", "")).strip() == "是" else False,
                        xuewei_tiefu=True if str(
                            row.get("穴位贴敷", "")).strip() == "是" else False,
                        reci_pulse=True if str(
                            row.get("热磁脉冲", "")).strip() == "是" else False,
                        baoguan=True if str(
                            row.get("拔罐", "")).strip() == "是" else False,
                        vision_level=row.get(
                            "视力等级", None) and float(row["视力等级"]),
                        right_eye_naked=row.get(
                            "右眼-裸眼视力", None) and float(row["右眼-裸眼视力"]),
                        left_eye_naked=row.get(
                            "左眼-裸眼视力", None) and float(row["左眼-裸眼视力"]),
                        right_eye_corrected=row.get(
                            "右眼-矫正视力", None) and float(row["右眼-矫正视力"]),
                        left_eye_corrected=row.get(
                            "左眼-矫正视力", None) and float(row["左眼-矫正视力"]),
                        right_keratometry_K1=row.get(
                            "右眼-角膜曲率K1", None) and float(row["右眼-角膜曲率K1"]),
                        left_keratometry_K1=row.get(
                            "左眼-角膜曲率K1", None) and float(row["左眼-角膜曲率K1"]),
                        right_keratometry_K2=row.get(
                            "右眼-角膜曲率K2", None) and float(row["右眼-角膜曲率K2"]),
                        left_keratometry_K2=row.get(
                            "左眼-角膜曲率K2", None) and float(row["左眼-角膜曲率K2"]),
                        right_axial_length=row.get(
                            "右眼-眼轴", None) and float(row["右眼-眼轴"]),
                        left_axial_length=row.get(
                            "左眼-眼轴", None) and float(row["左眼-眼轴"]),
                        right_sphere=row.get(
                            "右眼屈光-球镜", None) and float(row["右眼屈光-球镜"]),
                        right_cylinder=row.get(
                            "右眼屈光-柱镜", None) and float(row["右眼屈光-柱镜"]),
                        right_axis=row.get(
                            "右眼屈光-轴位", None) and float(row["右眼屈光-轴位"]),
                        left_sphere=row.get(
                            "左眼屈光-球镜", None) and float(row["左眼屈光-球镜"]),
                        left_cylinder=row.get(
                            "左眼屈光-柱镜", None) and float(row["左眼屈光-柱镜"]),
                        left_axis=row.get(
                            "左眼屈光-轴位", None) and float(row["左眼屈光-轴位"]),
                        right_dilated_sphere=row.get(
                            "右眼散瞳-球镜", None) and float(row["右眼散瞳-球镜"]),
                        right_dilated_cylinder=row.get(
                            "右眼散瞳-柱镜", None) and float(row["右眼散瞳-柱镜"]),
                        right_dilated_axis=row.get(
                            "右眼散瞳-轴位", None) and float(row["右眼散瞳-轴位"]),
                        left_dilated_sphere=row.get(
                            "左眼散瞳-球镜", None) and float(row["左眼散瞳-球镜"]),
                        left_dilated_cylinder=row.get(
                            "左眼散瞳-柱镜", None) and float(row["左眼散瞳-柱镜"]),
                        left_dilated_axis=row.get(
                            "左眼散瞳-轴位", None) and float(row["左眼散瞳-轴位"]),
                        right_anterior_depth=row.get(
                            "右眼-前房深度", None) and float(row["右眼-前房深度"]),
                        left_anterior_depth=row.get(
                            "左眼-前房深度", None) and float(row["左眼-前房深度"]),
                        other_info=str(row["其他情况"]).strip() if (
                            "其他情况" in row and not pd.isna(row["其他情况"])) else None,
                        eye_fatigue=str(row["眼疲劳状况"]).strip() if (
                            "眼疲劳状况" in row and not pd.isna(row["眼疲劳状况"])) else None,
                        right_eye_naked_interv=row.get(
                            "右眼-干预-裸眼视力", None) and float(row["右眼-干预-裸眼视力"]),
                        left_eye_naked_interv=row.get(
                            "左眼-干预-裸眼视力", None) and float(row["左眼-干预-裸眼视力"]),
                        right_sphere_interv=row.get(
                            "右眼屈光-干预-球镜", None) and float(row["右眼屈光-干预-球镜"]),
                        right_cylinder_interv=row.get(
                            "右眼屈光-干预-柱镜", None) and float(row["右眼屈光-干预-柱镜"]),
                        right_axis_interv=row.get(
                            "右眼屈光-干预-轴位", None) and float(row["右眼屈光-干预-轴位"]),
                        left_sphere_interv=row.get(
                            "左眼屈光-干预-球镜", None) and float(row["左眼屈光-干预-球镜"]),
                        left_cylinder_interv=row.get(
                            "左眼屈光-干预-柱镜", None) and float(row["左眼屈光-干预-柱镜"]),
                        left_axis_interv=row.get(
                            "左眼屈光-干预-轴位", None) and float(row["左眼屈光-干预-轴位"]),
                        right_dilated_sphere_interv=row.get(
                            "右眼散瞳-干预-球镜", None) and float(row["右眼散瞳-干预-球镜"]),
                        right_dilated_cylinder_interv=row.get(
                            "右眼散瞳-干预-柱镜", None) and float(row["右眼散瞳-干预-柱镜"]),
                        right_dilated_axis_interv=row.get(
                            "右眼散瞳-干预-轴位", None) and float(row["右眼散瞳-干预-轴位"]),
                        left_dilated_sphere_interv=row.get(
                            "左眼散瞳-干预-球镜", None) and float(row["左眼散瞳-干预-球镜"]),
                        left_dilated_cylinder_interv=row.get(
                            "左眼散瞳-干预-柱镜", None) and float(row["左眼散瞳-干预-柱镜"]),
                        left_dilated_axis_interv=row.get(
                            "左眼散瞳-干预-轴位", None) and float(row["左眼散瞳-干预-轴位"]),
                        interv_vision_level=str(row["干预后视力等级"]).strip() if (
                            "干预后视力等级" in row and not pd.isna(row["干预后视力等级"])) else None,
                        left_naked_change=row.get(
                            "左眼裸眼视力变化", None) and float(row["左眼裸眼视力变化"]),
                        right_naked_change=row.get(
                            "右眼裸眼视力变化", None) and float(row["右眼裸眼视力变化"]),
                        left_sphere_change=row.get(
                            "左眼屈光-球镜变化", None) and float(row["左眼屈光-球镜变化"]),
                        right_sphere_change=row.get(
                            "右眼屈光-球镜变化", None) and float(row["右眼屈光-球镜变化"]),
                        left_cylinder_change=row.get(
                            "左眼屈光-柱镜变化", None) and float(row["左眼屈光-柱镜变化"]),
                        right_cylinder_change=row.get(
                            "右眼屈光-柱镜变化", None) and float(row["右眼屈光-柱镜变化"]),
                        left_axis_change=row.get(
                            "左眼屈光-轴位变化", None) and float(row["左眼屈光-轴位变化"]),
                        right_axis_change=row.get(
                            "右眼屈光-轴位变化", None) and float(row["右眼屈光-轴位变化"]),
                        left_interv_effect=str(row["左眼视力干预效果"]).strip() if (
                            "左眼视力干预效果" in row and not pd.isna(row["左眼视力干预效果"])) else None,
                        right_interv_effect=str(row["右眼视力干预效果"]).strip() if (
                            "右眼视力干预效果" in row and not pd.isna(row["右眼视力干预效果"])) else None,
                        left_sphere_effect=str(row["左眼球镜干预效果"]).strip() if (
                            "左眼球镜干预效果" in row and not pd.isna(row["左眼球镜干预效果"])) else None,
                        right_sphere_effect=str(row["右眼球镜干预效果"]).strip() if (
                            "右眼球镜干预效果" in row and not pd.isna(row["右眼球镜干预效果"])) else None,
                        left_cylinder_effect=str(row["左眼柱镜干预效果"]).strip() if (
                            "左眼柱镜干预效果" in row and not pd.isna(row["左眼柱镜干预效果"])) else None,
                        right_cylinder_effect=str(row["右眼柱镜干预效果"]).strip() if (
                            "右眼柱镜干预效果" in row and not pd.isna(row["右眼柱镜干预效果"])) else None,
                        # 干预时间记录
                        interv1=pd.to_datetime(row["第1次干预"]) if (
                            "第1次干预" in row and not pd.isna(row["第1次干预"])) else None,
                        interv2=pd.to_datetime(row["第2次干预"]) if (
                            "第2次干预" in row and not pd.isna(row["第2次干预"])) else None,
                        interv3=pd.to_datetime(row["第3次干预"]) if (
                            "第3次干预" in row and not pd.isna(row["第3次干预"])) else None,
                        interv4=pd.to_datetime(row["第4次干预"]) if (
                            "第4次干预" in row and not pd.isna(row["第4次干预"])) else None,
                        interv5=pd.to_datetime(row["第5次干预"]) if (
                            "第5次干预" in row and not pd.isna(row["第5次干预"])) else None,
                        interv6=pd.to_datetime(row["第6次干预"]) if (
                            "第6次干预" in row and not pd.isna(row["第6次干预"])) else None,
                        interv7=pd.to_datetime(row["第7次干预"]) if (
                            "第7次干预" in row and not pd.isna(row["第7次干预"])) else None,
                        interv8=pd.to_datetime(row["第8次干预"]) if (
                            "第8次干预" in row and not pd.isna(row["第8次干预"])) else None,
                        interv9=pd.to_datetime(row["第9次干预"]) if (
                            "第9次干预" in row and not pd.isna(row["第9次干预"])) else None,
                        interv10=pd.to_datetime(row["第10次干预"]) if (
                            "第10次干预" in row and not pd.isna(row["第10次干预"])) else None,
                        interv11=pd.to_datetime(row["第11次干预"]) if (
                            "第11次干预" in row and not pd.isna(row["第11次干预"])) else None,
                        interv12=pd.to_datetime(row["第12次干预"]) if (
                            "第12次干预" in row and not pd.isna(row["第12次干预"])) else None,
                        interv13=pd.to_datetime(row["第13次干预"]) if (
                            "第13次干预" in row and not pd.isna(row["第13次干预"])) else None,
                        interv14=pd.to_datetime(row["第14次干预"]) if (
                            "第14次干预" in row and not pd.isna(row["第14次干预"])) else None,
                        interv15=pd.to_datetime(row["第15次干预"]) if (
                            "第15次干预" in row and not pd.isna(row["第15次干预"])) else None,
                        interv16=pd.to_datetime(row["第16次干预"]) if (
                            "第16次干预" in row and not pd.isna(row["第16次干预"])) else None
                    )
                    # 调用单记录内计算函数对新建的扩展记录进行计算，更新计算字段
                    from backend.services.vision_calculation import calculate_within_year_change
                    calc_result = calculate_within_year_change(extension)
                    for key, value in calc_result.items():
                        setattr(extension, key, value)
                    db.session.add(extension)
                    imported_count += 1
                except (ValueError, SQLAlchemyError) as e:
                    error_messages.append(f"第{index+2}行: 扩展数据写入错误: {str(e)}")
                    failed_rows.add(index)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            os.remove(temp_filepath)
            return jsonify({"error": f"数据库提交错误: {str(e)}"}), 500

        failure_row_count = len(failed_rows)
        failures_file_url = ""
        if failure_row_count > 0:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            failures_filename = f"failures_{timestamp}_{filename}.xlsx"
            failures_file_path = os.path.join(
                FAILURE_UPLOAD_DIR, failures_filename)
            df_failed = df.loc[list(failed_rows)].copy()
            error_list = ["" for _ in range(len(df_failed))]
            for i, row_idx in enumerate(df_failed.index):
                row_tag = f"第{row_idx+2}行"
                row_errors = [msg for msg in error_messages if row_tag in msg]
                if row_errors:
                    error_list[i] = "; ".join(row_errors)
            df_failed["错误信息"] = error_list
            writer = pd.ExcelWriter(failures_file_path, engine='xlsxwriter')
            df_failed.to_excel(writer, index=False, sheet_name='Failures')
            workbook = writer.book
            worksheet = writer.sheets['Failures']
            red_format = workbook.add_format({'font_color': 'red'})
            error_col = df_failed.columns.get_loc("错误信息")
            for i in range(len(df_failed)):
                if df_failed.iloc[i, error_col]:
                    worksheet.write(
                        i+1, error_col, df_failed.iloc[i, error_col], red_format)
            writer.close()
            failures_file_url = url_for(
                'static', filename=f'uploads/{failures_filename}', _external=True)

        os.remove(temp_filepath)

        result_message = f"导入成功 {imported_count} 条记录。"
        if failure_row_count > 0:
            result_message += f" 失败 {failure_row_count} 条记录。"
            if failures_file_url:
                result_message += f" 失败记录文件下载链接: {failures_file_url}"
        return jsonify({
            "message": result_message,
            "imported_count": imported_count,
            "failures_count": failure_row_count,
            "failures_file": failures_file_url if failures_file_url else None
        }), 200

    except Exception as e:
        db.session.rollback()
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return jsonify({"error": f"文件处理错误: {str(e)}"}), 500
