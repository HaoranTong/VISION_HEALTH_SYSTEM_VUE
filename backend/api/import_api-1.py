#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: import_api.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\api\import_api.py
功能说明:
    提供学生数据导入功能。支持上传 Excel (.xlsx) 和 CSV (.csv) 文件，
    使用 Pandas 解析文件，对每行数据进行必填字段校验与数据格式转换。
    符合条件的记录写入数据库；校验失败的记录将生成“上传失败记录表”，
    保留原始数据并在错误列标红显示错误原因。接口返回 JSON 格式结果，
    包含导入成功记录数、失败记录数(以行数计)及失败记录文件下载链接（若有）。
使用方法:
    API接口 URL: /api/students/import
    请求方法: POST
    请求内容类型: multipart/form-data
    参数: file (上传的 .xlsx 或 .csv 文件)
"""

import os
import logging
from datetime import datetime

import pandas as pd
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.database import db
from backend.models.student import Student

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {"xlsx", "csv"}

# 临时上传文件保存目录（用于保存上传过程中产生的临时文件）
TEMP_UPLOAD_DIR = os.path.join(os.getcwd(), "temp_uploads")
if not os.path.exists(TEMP_UPLOAD_DIR):
    os.makedirs(TEMP_UPLOAD_DIR)

# 失败记录文件保存目录（公开可下载）
FAILURE_UPLOAD_DIR = os.path.join(os.getcwd(), "frontend", "static", "uploads")
if not os.path.exists(FAILURE_UPLOAD_DIR):
    os.makedirs(FAILURE_UPLOAD_DIR)


def allowed_file(filename):
    """检查文件扩展名是否允许上传"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_row(row, required_fields, row_index):
    """
    校验一行数据是否满足必填字段和基本格式要求。
    返回 (is_valid, errors_list)
    """
    errors = []
    # 必填字段检查
    for field in required_fields:
        if pd.isna(row.get(field, None)):
            errors.append(f"第{row_index+2}行: 缺失必填字段 '{field}'")
    # 简单示例：视力范围校验（右眼和左眼裸眼视力）
    for field in ["右眼-裸眼视力", "左眼-裸眼视力"]:
        try:
            value = float(row.get(field, 0))
            if value < 0.1 or value > 5.0:
                errors.append(
                    f"第{row_index+2}行: '{field}' 值 {value} 不在合理范围(0.1-5.0)")
        except ValueError:
            errors.append(f"第{row_index+2}行: '{field}' 格式错误")
    return (len(errors) == 0, errors)


import_api = Blueprint("import_api", __name__)


@import_api.route("/api/students/import", methods=["POST"])
def import_students():
    """
    学生数据导入接口
    处理上传的 Excel 或 CSV 文件，解析数据，对每行数据进行必填字段和格式校验，
    合格记录导入 Student 表（可根据需要扩展到 StudentExtension），
    校验失败记录生成上传失败记录表，并返回上传结果。
    """
    if "file" not in request.files:
        return jsonify({"error": "未找到上传文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "未选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件格式，请上传 .xlsx 或 .csv 文件"}), 400

    # 调试输出文件名
    current_app.logger.debug(f"DEBUG: 原始上传文件名: {file.filename}")
    filename = secure_filename(file.filename)
    current_app.logger.debug(f"DEBUG: secure_filename 后的文件名: {filename}")
    temp_filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
    file.save(temp_filepath)

    try:
        # 根据扩展名使用 read_excel 或 read_csv 解析数据
        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'xlsx':
            df = pd.read_excel(temp_filepath, dtype=str)
        elif ext == 'csv':
            df = pd.read_csv(temp_filepath, dtype=str)
        else:
            os.remove(temp_filepath)
            return jsonify({"error": "不支持的文件格式"}), 400

        # 清洗列名，去除首尾空格及所有空白字符
        df.columns = df.columns.str.strip()

        current_app.logger.debug(f"DEBUG: DataFrame 列名： {list(df.columns)}")
        current_app.logger.debug(f"DEBUG: DataFrame 行数： {len(df)}")
        current_app.logger.debug(
            f"DEBUG: DataFrame 前5行数据： {df.head().to_string()}")

        # 定义必填字段（Excel/CSV 列名）
        required_fields = ["教育ID号", "学校", "年级", "班级", "姓名", "性别",
                           "年龄", "右眼-裸眼视力", "左眼-裸眼视力"]

        imported_count = 0
        # error_messages 原先存放所有错误文本，现在仍保留，但不再用它的长度作为失败数
        error_messages = []

        # 新增：用于记录失败行的下标集合
        failed_rows = set()

        for index, row in df.iterrows():
            is_valid, errors = validate_row(row, required_fields, index)
            if not is_valid:
                error_messages.extend(errors)
                failed_rows.add(index)  # 标记此行失败
                continue
            try:
                # 注意：此处字段名称须与 Student 模型保持一致
                student = Student(
                    education_id=row["教育ID号"].strip(),
                    school=row["学校"].strip(),
                    school_code="",  # 后台维护或自动映射
                    grade=row["年级"].strip(),
                    class_name=row["班级"].strip(),
                    name=row["姓名"].strip(),
                    gender=row["性别"].strip(),
                    age=int(row["年龄"].strip()) if not pd.isna(
                        row["年龄"]) else None,
                    birthday=pd.to_datetime(row["出生日期"]).date() if (
                        "出生日期" in row and not pd.isna(row["出生日期"])) else None,
                    phone=row["联系电话"].strip() if (
                        "联系电话" in row and not pd.isna(row["联系电话"])) else None,
                    id_card=row["身份证"].strip() if (
                        "身份证" in row and not pd.isna(row["身份证"])) else None,
                    parent_name=row["家长姓名"].strip() if (
                        "家长姓名" in row and not pd.isna(row["家长姓名"])) else None,
                    parent_phone=row["家长电话"].strip() if (
                        "家长电话" in row and not pd.isna(row["家长电话"])) else None,
                    vision_right=float(row["右眼-裸眼视力"]),
                    vision_left=float(row["左眼-裸眼视力"]),
                    vision_right_corrected=float(
                        row["右眼-矫正视力"]) if ("右眼-矫正视力" in row and not pd.isna(row["右眼-矫正视力"])) else None,
                    vision_left_corrected=float(
                        row["左眼-矫正视力"]) if ("左眼-矫正视力" in row and not pd.isna(row["左眼-矫正视力"])) else None,
                    myopia_level=None  # 后续可自动计算
                )
                db.session.add(student)
                imported_count += 1
            except (ValueError, SQLAlchemyError) as e:
                # 写入数据库时出错，也算失败
                error_messages.append(f"第{index+2}行: 数据写入错误: {str(e)}")
                failed_rows.add(index)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            os.remove(temp_filepath)
            return jsonify({"error": f"数据库提交错误: {str(e)}"}), 500

        # 注意，这里 failures_count 不再是 error_messages 的长度，而是 failed_rows 的大小
        failure_row_count = len(failed_rows)

        # 如果存在错误记录，生成上传失败记录表
        failures_file_url = ""
        if failure_row_count > 0:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            # 给文件名加个随机后缀，避免重名覆盖
            failures_filename = f"failures_{timestamp}_{filename}.xlsx"
            failures_file_path = os.path.join(
                FAILURE_UPLOAD_DIR, failures_filename)

            # 使用 XlsxWriter 写入 Excel 失败记录
            writer = pd.ExcelWriter(failures_file_path, engine='xlsxwriter')
            df_errors = df.copy()

            # 新增：给每行的“错误信息”列
            error_list = ["" for _ in range(len(df_errors))]

            # 逐条错误日志里解析行号，并把错误追加到 error_list[row_num]
            for err in error_messages:
                print("DEBUG ERROR:", err)
                row_num = None
                try:
                    if "行" in err:
                        # 例如 "第5行: 缺失必填字段..."
                        left_part = err.split("行")[0].replace("第", "")  # "5"
                        row_num = int(left_part) - 2
                except Exception:
                    pass

                if row_num is not None and 0 <= row_num < len(df_errors):
                    if error_list[row_num]:
                        error_list[row_num] += "; " + err
                    else:
                        error_list[row_num] = err

            df_errors["错误信息"] = error_list
            df_errors.to_excel(writer, index=False, sheet_name='Failures')

            workbook = writer.book
            worksheet = writer.sheets['Failures']
            red_format = workbook.add_format({'font_color': 'red'})
            error_col = df_errors.columns.get_loc("错误信息")

            # 给有错误的单元格标红
            for row_idx in range(1, len(df_errors) + 1):
                if df_errors.iloc[row_idx-1, error_col]:
                    worksheet.write(row_idx, error_col,
                                    df_errors.iloc[row_idx-1, error_col], red_format)
            writer.close()

            # 构造下载 URL，使用静态资源方式
            failures_file_url = url_for('static',
                                        filename=f'uploads/{failures_filename}',
                                        _external=True)

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
