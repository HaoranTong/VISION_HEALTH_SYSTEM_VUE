#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: import_api.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\api\import_api.py
功能介绍:
    提供电子表格数据导入功能。接收上传的 Excel 文件 (.xlsx)，
    使用 Pandas 解析文件，对每行数据进行必填字段校验与数据转换，
    如果该行存在必填字段缺失、数据格式错误或重复记录，则将该行记录为失败，
    并在失败记录表中输出原始完整内容，对出错的字段以红字标记显示；
    否则将全部数据（包括可选字段）导入数据库。
    其中必填字段为：
      "教育ID号", "学校", "年级", "班级", "姓名", "性别", "年龄",
      "右眼-裸眼视力", "左眼-裸眼视力"
    可选字段包括："出生日期", "身份证", "家长姓名", "家长电话",
      "右眼-矫正视力", "左眼-矫正视力", "联系电话"
    学校信息：
      - 学校代码由映射字典获得，保存到 school_code 字段；
      - 学校名称保存到 school_id 字段（即原 Excel 中“学校”的内容）。
使用方法:
    API接口 URL: /api/students/import
    请求方法: POST
    请求内容类型: multipart/form-data
    参数: file (上传的 .xlsx 文件)
"""

import os
import pandas as pd
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.models.student import Student
from backend.infrastructure.database import db

# 创建 Blueprint
import_api = Blueprint("import_api", __name__)

ALLOWED_EXTENSIONS = {"xlsx"}
# 定义存储失败记录文件的目录
FAILURE_RECORDS_DIR = os.path.join(os.getcwd(), "temp_uploads")
if not os.path.exists(FAILURE_RECORDS_DIR):
    os.makedirs(FAILURE_RECORDS_DIR)


def allowed_file(filename):
    """检查文件是否为允许的扩展名"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 学校名称 -> 学校代码映射
SCHOOL_CODE_MAP = {
    "华兴小学": "001",
    "师大附小清华小学校": "002",
    "苏宁红军小学校": "003"
}


@import_api.route("/api/students/import", methods=["POST"])
def import_students():
    """
    电子表格导入 API 接口
    接收上传的 Excel 文件，使用 Pandas 解析文件，
    对每行数据进行必填字段校验与数据转换，
    如果该行存在必填字段缺失、数据格式错误或重复记录，则将该行记录为失败；
    否则将全部数据（包括可选字段）导入数据库。
    导入完成后，如有失败记录，导出一个 Excel 文件，
    并在出错的单元格以红字标记显示错误。
    返回 JSON 响应，包含导入成功记录数及失败记录文件下载链接（若有）。
    """
    if "file" not in request.files:
        return jsonify({"error": "未找到上传文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "未选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件格式，请上传 .xlsx 文件"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(os.getcwd(), filename)
    file.save(filepath)

    try:
        # 指定身份证、家长电话、联系电话均作为字符串读取，避免数值转换问题
        df = pd.read_excel(
            filepath, dtype={"身份证": str, "家长电话": str, "联系电话": str})

        # 统一处理“矫正方式类型”系列列（如果存在）
        cols = [col for col in df.columns if col.startswith("矫正方式类型")]
        if len(cols) > 1:
            df["矫正方式类型"] = df[cols].bfill(axis=1).iloc[:, 0]
            for col in cols:
                if col != "矫正方式类型":
                    df.drop(columns=[col], inplace=True)

        # 定义必填字段列表（只包含原来规定的必填项）
        required_columns = [
            "教育ID号", "学校", "年级", "班级", "姓名", "性别", "年龄",
            "右眼-裸眼视力", "左眼-裸眼视力"
        ]
        missing_cols = [
            col for col in required_columns if col not in df.columns]
        if missing_cols:
            failure_data = pd.DataFrame({
                "错误": [f"缺少必填字段: {', '.join(missing_cols)}"]
            })
            failure_filename = f"failure_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            failure_file_path = os.path.join(
                FAILURE_RECORDS_DIR, failure_filename)
            failure_data.to_excel(failure_file_path, index=False)
            os.remove(filepath)
            return jsonify({
                "error": f"缺少必填字段: {', '.join(missing_cols)}",
                "failures_file": failure_file_path
            }), 400

        imported_count = 0
        error_rows = []  # 记录失败行的信息

        # 遍历每一行数据进行校验与导入
        for idx, row in df.iterrows():
            error_fields = []  # 记录当前行出错的字段

            # 检查必填字段是否存在且非空
            for col in required_columns:
                if pd.isna(row[col]):
                    error_fields.append(col)

            if error_fields:
                error_rows.append({
                    "row_index": idx,
                    "row_data": row.to_dict(),
                    "error_fields": error_fields.copy()
                })
                continue

            # 转换裸眼视力数据
            try:
                vision_right = float(row["右眼-裸眼视力"])
                vision_left = float(row["左眼-裸眼视力"])
            except Exception:
                error_fields.extend(["右眼-裸眼视力", "左眼-裸眼视力"])
                error_rows.append({
                    "row_index": idx,
                    "row_data": row.to_dict(),
                    "error_fields": list(set(error_fields))
                })
                continue

            # 转换矫正视力为 optional 字段
            vision_right_corrected = None
            if "右眼-矫正视力" in df.columns and not pd.isna(row["右眼-矫正视力"]):
                try:
                    vision_right_corrected = float(row["右眼-矫正视力"])
                except Exception:
                    vision_right_corrected = None
            vision_left_corrected = None
            if "左眼-矫正视力" in df.columns and not pd.isna(row["左眼-矫正视力"]):
                try:
                    vision_left_corrected = float(row["左眼-矫正视力"])
                except Exception:
                    vision_left_corrected = None

            # 生成学校代码和获取学校名称
            school_name = str(row["学校"]).strip()
            school_code = SCHOOL_CODE_MAP.get(school_name, "999")

            # 检查重复记录：使用学校代码与教育ID号生成唯一索引
            index_id = f"{school_code}{str(row['教育ID号'])}"
            existing_student = Student.query.filter_by(
                index_id=index_id).first()
            if existing_student:
                error_fields.append("重复记录")
                error_rows.append({
                    "row_index": idx,
                    "row_data": row.to_dict(),
                    "error_fields": list(set(error_fields))
                })
                continue

            # 处理可选字段
            try:
                if "出生日期" in df.columns and not pd.isna(row["出生日期"]):
                    if isinstance(row["出生日期"], pd.Timestamp):
                        birthday_val = row["出生日期"].date()
                    else:
                        birthday_val = pd.to_datetime(row["出生日期"]).date()
                else:
                    birthday_val = None
            except Exception:
                birthday_val = None

            # 直接按字符串处理身份证、家长电话、联系电话
            id_card = row["身份证"].strip() if "身份证" in df.columns and pd.notna(
                row["身份证"]) else None
            parent_name = row["家长姓名"].strip() if "家长姓名" in df.columns and pd.notna(
                row["家长姓名"]) else None
            parent_phone = row["家长电话"].strip() if "家长电话" in df.columns and pd.notna(
                row["家长电话"]) else None
            phone_val = row["联系电话"].strip() if "联系电话" in df.columns and pd.notna(
                row["联系电话"]) else None

            # 创建 Student 实例，将必填和可选数据导入
            student = Student(
                full_edu_id=str(row["教育ID号"]),
                school_code=school_code,
                school_id=school_name,  # 将学校名称保存到 school_id 字段
                name=str(row["姓名"]),
                gender=str(row["性别"]) if not pd.isna(row["性别"]) else None,
                age=int(row["年龄"]) if not pd.isna(row["年龄"]) else None,
                grade=str(row["年级"]) if not pd.isna(row["年级"]) else None,
                class_name=str(row["班级"]) if not pd.isna(row["班级"]) else None,
                vision_right=vision_right,
                vision_left=vision_left,
                vision_right_corrected=vision_right_corrected,
                vision_left_corrected=vision_left_corrected,
                birthday=birthday_val,
                id_card=id_card,
                phone=phone_val,  # 现在将联系电话处理后导入
                parent_name=parent_name,
                parent_phone=parent_phone,
                myopia_level=None
            )
            student.index_id = index_id

            db.session.add(student)
            imported_count += 1

        db.session.commit()
        os.remove(filepath)

        # 如果有错误行，导出失败记录文件
        failures_file_link = ""
        if error_rows:
            error_data = []
            for er in error_rows:
                row_dict = er["row_data"]
                row_dict["错误字段"] = ", ".join(er["error_fields"])
                error_data.append(row_dict)
            error_df = pd.DataFrame(error_data)
            failure_filename = f"failure_records_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            failure_file_path = os.path.join(
                FAILURE_RECORDS_DIR, failure_filename)
            writer = pd.ExcelWriter(failure_file_path, engine='xlsxwriter',
                                    engine_kwargs={'options': {'nan_inf_to_errors': True}})
            error_df.to_excel(writer, sheet_name='Failures', index=False)
            workbook = writer.book
            red_format = workbook.add_format({'font_color': 'red'})
            worksheet = writer.sheets['Failures']
            # 对错误行中出错的字段单元格设置红色格式
            for i, er in enumerate(error_rows):
                for field in er["error_fields"]:
                    if field in error_df.columns:
                        col_idx = error_df.columns.get_loc(field)
                        worksheet.write(
                            i+1, col_idx, error_df.iloc[i, col_idx], red_format)
            writer.close()
            failures_file_link = failure_file_path

        return jsonify({
            "message": f"导入成功，共导入 {imported_count} 条记录。",
            "imported_count": imported_count,
            "failures_file": failures_file_link if failures_file_link else None
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"文件处理错误: {str(e)}"}), 500
