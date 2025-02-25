#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: import_api.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\api\import_api.py
功能说明:
    1. 导入 Excel/CSV 数据，校验必填字段，不合格行记录到失败表；
    2. 对已存在（education_id 相同）的数据行，采用“部分更新”逻辑：
       - 如果数据库中某字段已有值，则不覆盖；
       - 如果数据库中该字段为 None，而上传数据有值，则填充；
       - 若发现想覆盖已有字段 => 标记整行失败。
    3. 最终只将真正插入/更新成功的行计为 success，缺少必填字段或试图覆盖已有字段的行计为失败。
    4. 失败记录表仅包含出错行，并在“错误信息”列标红提示；同时对于解析到的具体字段，还能高亮对应单元格。
    5. 解决 “NAN/INF not supported in write_number()” 报错：在写出前替换 NaN/inf。
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

# 临时上传文件保存目录（仅存储上传处理过程中的文件）
TEMP_UPLOAD_DIR = os.path.join(os.getcwd(), "temp_uploads")
if not os.path.exists(TEMP_UPLOAD_DIR):
    os.makedirs(TEMP_UPLOAD_DIR)

# 失败记录文件保存目录（生成后可下载）
FAILURE_UPLOAD_DIR = os.path.join(os.getcwd(), "frontend", "static", "uploads")
if not os.path.exists(FAILURE_UPLOAD_DIR):
    os.makedirs(FAILURE_UPLOAD_DIR)

# 必填字段
REQUIRED_FIELDS = [
    "教育ID号", "学校", "年级", "班级", "姓名", "性别", "年龄",
    "右眼-裸眼视力", "左眼-裸眼视力"
]

import_api = Blueprint("import_api", __name__)


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许上传"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_required_fields(row: dict, row_index: int) -> (bool, list):
    """
    检查当前行是否缺少必填字段，或者裸眼视力超出范围。
    返回 (is_valid, errors_list)
    """
    errors = []
    # 检查必填字段是否缺失
    for field in REQUIRED_FIELDS:
        if pd.isna(row.get(field, None)):
            errors.append(f"第{row_index + 2}行: 缺失必填字段 '{field}'")

    # 检查裸眼视力范围
    for field in ["右眼-裸眼视力", "左眼-裸眼视力"]:
        if not pd.isna(row.get(field, None)):
            try:
                val = float(row[field])
                if val < 0.1 or val > 5.0:
                    errors.append(
                        f"第{row_index+2}行: '{field}' 值 {val} 不在(0.1~5.0)"
                    )
            except ValueError:
                errors.append(f"第{row_index+2}行: '{field}' 格式错误")

    return (len(errors) == 0, errors)


def partial_update_student(
    student_obj: Student, row: dict, row_index: int, errors: list
) -> bool:
    """
    对已存在的 student_obj 进行“部分更新”：
      - 如果数据库中某字段已有值 => 不允许覆盖 => 标记失败
      - 如果是 None，则用 row 中的值填充
      - row 中若为 NaN/None，则跳过
    返回值:
      True  => 部分更新成功
      False => 出现覆盖或其他错误 => 视为整行失败
    """

    # 示例字段 1: “右眼-裸眼视力”
    val_right = row.get("右眼-裸眼视力", None)
    if not pd.isna(val_right):
        try:
            float_val = float(val_right)
            if student_obj.vision_right is not None:
                # 数据库已有值 => 不允许覆盖
                errors.append(
                    f"第{row_index+2}行: 不允许覆盖已有字段 '右眼-裸眼视力'"
                )
                return False
            else:
                student_obj.vision_right = float_val
        except ValueError:
            errors.append(
                f"第{row_index+2}行: '右眼-裸眼视力' 数据格式错误"
            )
            return False

    # 示例字段 2: “左眼-裸眼视力”
    val_left = row.get("左眼-裸眼视力", None)
    if not pd.isna(val_left):
        try:
            float_val = float(val_left)
            if student_obj.vision_left is not None:
                errors.append(
                    f"第{row_index+2}行: 不允许覆盖已有字段 '左眼-裸眼视力'"
                )
                return False
            else:
                student_obj.vision_left = float_val
        except ValueError:
            errors.append(
                f"第{row_index+2}行: '左眼-裸眼视力' 数据格式错误"
            )
            return False

    # 示例字段 3: “姓名”
    val_name = row.get("姓名", None)
    if not pd.isna(val_name):
        if student_obj.name is not None:
            errors.append(
                f"第{row_index+2}行: 不允许覆盖已有字段 '姓名'"
            )
            return False
        else:
            student_obj.name = str(val_name).strip()

    # 你可按需继续添加更多字段的 partial update 逻辑

    return True


@import_api.route("/api/students/import", methods=["POST"])
def import_students():
    """学生数据导入接口"""
    if "file" not in request.files:
        return jsonify({"error": "未找到上传文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "未选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件格式，请上传 .xlsx 或 .csv 文件"}), 400

    current_app.logger.debug(f"DEBUG: 原始上传文件名: {file.filename}")
    filename = secure_filename(file.filename)
    current_app.logger.debug(f"DEBUG: secure_filename 后的文件名: {filename}")
    temp_filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
    file.save(temp_filepath)

    try:
        # 解析
        ext = filename.rsplit(".", 1)[1].lower()
        if ext == "xlsx":
            df = pd.read_excel(temp_filepath, dtype=str)
        elif ext == "csv":
            df = pd.read_csv(temp_filepath, dtype=str)
        else:
            os.remove(temp_filepath)
            return jsonify({"error": "不支持的文件格式"}), 400

        # 清洗列名，去除首尾空格
        df.columns = df.columns.str.strip()

        current_app.logger.debug(
            f"DEBUG: DataFrame 列名： {list(df.columns)}"
        )
        current_app.logger.debug(
            f"DEBUG: DataFrame 行数： {len(df)}"
        )
        current_app.logger.debug(
            f"DEBUG: DataFrame 前5行数据：\n{df.head().to_string()}"
        )

        imported_count = 0
        error_messages = []
        # 用于记录“行号索引”
        failed_rows = set()

        for index, row_data in df.iterrows():
            # 1) 检查必填字段
            is_valid, req_errors = validate_required_fields(row_data, index)
            if not is_valid:
                error_messages.extend(req_errors)
                failed_rows.add(index)
                continue

            # 取出 education_id
            edu_id_val = row_data["教育ID号"]
            # 可能出现 float(例如 123.0)，所以先做 str，再 strip
            edu_id = str(edu_id_val).strip()

            # 2) 查重 => 若已存在 => partial update
            existing_student = Student.query.filter_by(
                education_id=edu_id
            ).first()
            if existing_student:
                local_errors = []
                success_update = partial_update_student(
                    existing_student, row_data, index, local_errors
                )
                if not success_update:
                    # 说明发生覆盖已有字段 或 数据格式错误
                    error_messages.extend(local_errors)
                    failed_rows.add(index)
                else:
                    # partial update 成功 => 这里算导入成功 +1
                    imported_count += 1
            else:
                # 3) 新建 Student
                try:
                    # 定义一些转换函数，安全处理 NaN
                    def safe_str(val):
                        return str(val).strip() if not pd.isna(val) else None

                    def safe_float(val):
                        return float(val) if not pd.isna(val) else None

                    def safe_int(val):
                        return int(float(val)) if not pd.isna(val) else None

                    new_student = Student(
                        education_id=safe_str(edu_id_val),
                        school=safe_str(row_data["学校"]),
                        school_code="",
                        grade=safe_str(row_data["年级"]),
                        class_name=safe_str(row_data["班级"]),
                        name=safe_str(row_data["姓名"]),
                        gender=safe_str(row_data["性别"]),
                        age=safe_int(row_data["年龄"]),
                        birthday=pd.to_datetime(row_data["出生日期"]).date()
                        if ("出生日期" in row_data and not pd.isna(row_data["出生日期"]))
                        else None,
                        phone=safe_str(row_data["联系电话"])
                        if "联系电话" in row_data else None,
                        id_card=safe_str(row_data["身份证"])
                        if "身份证" in row_data else None,
                        parent_name=safe_str(row_data["家长姓名"])
                        if "家长姓名" in row_data else None,
                        parent_phone=safe_str(row_data["家长电话"])
                        if "家长电话" in row_data else None,
                        vision_right=safe_float(row_data["右眼-裸眼视力"]),
                        vision_left=safe_float(row_data["左眼-裸眼视力"]),
                        vision_right_corrected=(
                            safe_float(row_data["右眼-矫正视力"])
                            if "右眼-矫正视力" in row_data else None
                        ),
                        vision_left_corrected=(
                            safe_float(row_data["左眼-矫正视力"])
                            if "左眼-矫正视力" in row_data else None
                        ),
                        myopia_level=None
                    )
                    db.session.add(new_student)
                    imported_count += 1
                except (ValueError, SQLAlchemyError) as e:
                    error_messages.append(
                        f"第{index+2}行: 数据写入错误: {str(e)}"
                    )
                    failed_rows.add(index)

        # 尝试提交
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            os.remove(temp_filepath)
            return jsonify({"error": f"数据库提交错误: {str(e)}"}), 500

        # 生成失败记录表
        failure_row_count = len(failed_rows)
        failures_file_url = ""

        if failure_row_count > 0:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            failures_filename = f"failures_{timestamp}_{filename}.xlsx"
            failures_file_path = os.path.join(
                FAILURE_UPLOAD_DIR, failures_filename
            )

            # 只取失败行
            df_failed = df.loc[list(failed_rows)].copy()

            # 为失败行添加“错误信息”列
            error_list = ["" for _ in range(len(df_failed))]

            # “行号 -> 出错字段列表” => 方便标红具体单元格
            row_error_fields_map = {}

            for i, row_idx in enumerate(df_failed.index):
                row_tag = f"第{row_idx+2}行"
                matching_msgs = [
                    msg for msg in error_messages if row_tag in msg
                ]
                if matching_msgs:
                    error_list[i] = "; ".join(matching_msgs)

                fields_this_row = []
                for msg in matching_msgs:
                    start_quote = msg.find("'")
                    end_quote = msg.rfind("'")
                    if start_quote != -1 and end_quote != -1 and end_quote > start_quote:
                        field_name = msg[start_quote+1:end_quote].strip()
                        fields_this_row.append(field_name)
                fields_this_row = list(set(fields_this_row))
                row_error_fields_map[row_idx] = fields_this_row

            df_failed["错误信息"] = error_list

            # ---------- 关键：替换掉 NaN/inf ----------
            # 1) 将所有 NaN 替换为空字符串:
            df_failed = df_failed.fillna("")
            # 2) 若还担心 inf/-inf，可额外处理:
            df_failed = df_failed.replace([float("inf"), float("-inf")], "")

            writer = pd.ExcelWriter(failures_file_path, engine="xlsxwriter")
            df_failed.to_excel(writer, index=False, sheet_name="Failures")

            workbook = writer.book
            worksheet = writer.sheets["Failures"]
            red_format = workbook.add_format({"font_color": "red"})

            # 获取列名列表
            failed_cols = list(df_failed.columns)
            # 标红“错误信息”列
            error_col_idx = df_failed.columns.get_loc("错误信息")
            for i in range(len(df_failed)):
                if df_failed.iloc[i, error_col_idx]:
                    worksheet.write(
                        i + 1,
                        error_col_idx,
                        df_failed.iloc[i, error_col_idx],
                        red_format
                    )

            # 对具体出错字段的单元格标红
            for i, row_idx in enumerate(df_failed.index):
                error_fields = row_error_fields_map.get(row_idx, [])
                for field in error_fields:
                    if field in failed_cols:
                        col_idx = failed_cols.index(field)
                        original_val = df_failed.iloc[i, col_idx]
                        worksheet.write(
                            i + 1,
                            col_idx,
                            original_val,
                            red_format
                        )

            writer.close()

            # 构造可下载链接
            failures_file_url = url_for(
                "static",
                filename=f"uploads/{failures_filename}",
                _external=True
            )

        # 删除临时文件
        os.remove(temp_filepath)

        # 组装返回信息
        result_message = f"导入成功 {imported_count} 条记录。"
        if failure_row_count > 0:
            result_message += f" 失败 {failure_row_count} 条记录。"
            if failures_file_url:
                result_message += f" 下载失败记录: {failures_file_url}"

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
