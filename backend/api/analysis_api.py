#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: analysis_api.py
完整路径: backend/api/analysis_api.py
功能说明:
    统计报表接口，支持固定模板 (template1/按年龄段, template2/按性别) 和自定义查询 (query_mode="custom")。
    固定模板下：
      - template1 按年龄段分组，分组名称设置为"年龄"；
      - template2 按性别分组，分组名称设置为"性别"。
    数据查询结果中，每行第一列显示分组值，中间为各统计指标的“数量”和“占比”，最后一列为统计总数。
    合计行中，“数量”列直接累加，各“占比”列按对应数量与总体统计总数计算。
修改要点:
1. 修正合计行累加逻辑：循环范围扩展到最后一列，并对“占比”列重新计算。
2. 固定模板模式下显式设置 group_title，以确保第一列名头不为空。
3. 对于自定义查询模式，如果统计指标未选择子选项则返回错误提示。
4. （本次新增）当分组字段为多选且勾选了子选项，后端需对该字段执行 col.in_(val) 过滤，仅统计用户选择的分组值。
5. （本次新增）在 FIELD_DISPLAY_MAPPING 中增加 "grade": "年级"，保证第一列显示中文“年级”。
"""

from openpyxl import Workbook
from openpyxl.styles import Alignment
from flask import send_file
import pandas as pd
from io import BytesIO
from backend.models.student_extension import StudentExtension
from backend.models.student import Student
from backend.infrastructure.database import db
from sqlalchemy import func, and_, case, literal
from flask import Blueprint, request, jsonify, current_app
import datetime
import json

analysis_api = Blueprint("analysis_api", __name__)

# 定义允许的组合查询字段列表
complete_fields = {
    "data_year", "education_id", "school", "grade", "class_name", "name", "gender", "age",
    "vision_level", "interv_vision_level", "left_eye_naked", "right_eye_naked",
    "left_eye_naked_interv", "right_eye_naked_interv", "left_naked_change", "right_naked_change",
    "left_sphere_change", "right_sphere_change", "left_cylinder_change", "right_cylinder_change",
    "left_axis_change", "right_axis_change", "left_interv_effect", "right_interv_effect",
    "left_sphere_effect", "right_sphere_effect", "left_cylinder_effect", "right_cylinder_effect",
    "left_axis_effect", "right_axis_effect", "left_eye_corrected", "right_eye_corrected",
    "left_keratometry_K1", "right_keratometry_K1", "left_keratometry_K2", "right_keratometry_K2",
    "left_axial_length", "right_axial_length"
}

# 固定模板下的统计指标配置（仅支持 "vision_level"）
FIXED_METRICS = [{
    "field": "vision_level",
    "label": "视力等级",
    "distinct_vals": ["临床前期近视", "轻度近视", "中度近视"]
}]

# 自定义查询模式下可使用的统计指标配置
METRIC_CONFIG = {
    "education_id": {
        "label": "教育ID号",
        "type": "text"
    },
    "school": {
        "label": "学校",
        "type": "multi-select",
        "options": ["华兴小学", "苏宁红军小学", "师大附小清华小学"]
    },
    "class_name": {
        "label": "班级",
        "type": "dropdown",
        "options": lambda: [f"{i}班" for i in range(1, 16)]
    },
    "name": {
        "label": "姓名",
        "type": "text"
    },
    "gender": {
        "label": "性别",
        "type": "multi-select",
        "options": ["男", "女"]
    },
    "birthday": {
        "label": "出生日期",
        "type": "text"
    },
    "phone": {
        "label": "联系电话",
        "type": "text"
    },
    "id_card": {
        "label": "身份证号码",
        "type": "text"
    },
    "region": {
        "label": "区域",
        "type": "text"
    },
    "contact_address": {
        "label": "联系地址",
        "type": "text"
    },
    "parent_name": {
        "label": "家长姓名",
        "type": "text"
    },
    "parent_phone": {
        "label": "家长电话",
        "type": "text"
    },
    "data_year": {
        "label": "数据年份",
        "type": "dropdown",
        "options": ["2023", "2024", "2025", "2026", "2027", "2028"]
    },
    "grade": {
        "label": "年级",
        "type": "multi-select",
        "options": ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级", "七年级", "八年级", "九年级"]
    },
    "age": {
        "label": "年龄",
        "type": "number_range"
    },
    "height": {
        "label": "身高",
        "type": "number_range"
    },
    "weight": {
        "label": "体重",
        "type": "number_range"
    },
    "diet_preference": {
        "label": "饮食偏好",
        "type": "text"
    },
    "exercise_preference": {
        "label": "运动偏好",
        "type": "text"
    },
    "health_education": {
        "label": "健康教育",
        "type": "text"
    },
    "past_history": {
        "label": "既往史",
        "type": "text"
    },
    "family_history": {
        "label": "家族史",
        "type": "text"
    },
    "premature": {
        "label": "是否早产",
        "type": "dropdown",
        "options": ["是", "否"]
    },
    "allergy": {
        "label": "过敏史",
        "type": "text"
    },
    "right_eye_naked": {
        "label": "右眼-裸眼视力",
        "type": "number_range"
    },
    "left_eye_naked": {
        "label": "左眼-裸眼视力",
        "type": "number_range"
    },
    "right_eye_corrected": {
        "label": "右眼-矫正视力",
        "type": "number_range"
    },
    "left_eye_corrected": {
        "label": "左眼-矫正视力",
        "type": "number_range"
    },
    "right_keratometry_K1": {
        "label": "右眼-角膜曲率K1",
        "type": "number_range"
    },
    "left_keratometry_K1": {
        "label": "左眼-角膜曲率K1",
        "type": "number_range"
    },
    "right_keratometry_K2": {
        "label": "右眼-角膜曲率K2",
        "type": "number_range"
    },
    "left_keratometry_K2": {
        "label": "左眼-角膜曲率K2",
        "type": "number_range"
    },
    "right_axial_length": {
        "label": "右眼-眼轴",
        "type": "number_range"
    },
    "left_axial_length": {
        "label": "左眼-眼轴",
        "type": "number_range"
    },
    "right_sphere": {
        "label": "右眼屈光-球镜",
        "type": "number_range"
    },
    "left_sphere": {
        "label": "左眼屈光-球镜",
        "type": "number_range"
    },
    "right_cylinder": {
        "label": "右眼屈光-柱镜",
        "type": "number_range"
    },
    "left_cylinder": {
        "label": "左眼屈光-柱镜",
        "type": "number_range"
    },
    "right_axis": {
        "label": "右眼屈光-轴位",
        "type": "number_range"
    },
    "left_axis": {
        "label": "左眼屈光-轴位",
        "type": "number_range"
    },
    "right_dilated_sphere": {
        "label": "右眼散瞳-球镜",
        "type": "number_range"
    },
    "left_dilated_sphere": {
        "label": "左眼散瞳-球镜",
        "type": "number_range"
    },
    "right_dilated_cylinder": {
        "label": "右眼散瞳-柱镜",
        "type": "number_range"
    },
    "left_dilated_cylinder": {
        "label": "左眼散瞳-柱镜",
        "type": "number_range"
    },
    "right_dilated_axis": {
        "label": "右眼散瞳-轴位",
        "type": "number_range"
    },
    "left_dilated_axis": {
        "label": "左眼散瞳-轴位",
        "type": "number_range"
    },
    "vision_level": {
        "label": "视力等级",
        "type": "multi-select",
        "options": ["临床前期近视", "轻度近视", "中度近视", "假性近视", "正常"]
    },
    "right_anterior_depth": {
        "label": "右眼-前房深度",
        "type": "number_range"
    },
    "left_anterior_depth": {
        "label": "左眼-前房深度",
        "type": "number_range"
    },
    "other_info": {
        "label": "其他情况",
        "type": "text"
    },
    "eye_fatigue": {
        "label": "眼疲劳状况",
        "type": "text"
    },
    "frame_glasses": {
        "label": "框架眼镜",
        "type": "checkbox"
    },
    "contact_lenses": {
        "label": "隐形眼镜",
        "type": "checkbox"
    },
    "night_orthokeratology": {
        "label": "夜戴角膜塑型镜",
        "type": "checkbox"
    }
}


def get_column_by_field(field):
    """根据字段名获取对应的数据库列对象"""
    if hasattr(StudentExtension, field):
        return getattr(StudentExtension, field)
    if hasattr(Student, field):
        return getattr(Student, field)
    raise ValueError(f"字段 '{field}' 不存在")


def build_multi_level_header(dynamic_metrics, group_title):
    """
    构造三层表头:
    第一行: 第一列为分组字段名 (跨3行), 中间各统计指标字段名称 (每个占其选项数量*2列), 最后一列为统计总数 (跨3行).
    第二行: 每个统计指标字段下显示用户选中的子选项 (每个占2列).
    第三行: 每个子选项下固定显示 "数量" 与 "占比".
    """
    header = []

    # 第一行
    first_row = [{"text": group_title, "rowspan": 3}]  # 分组字段名
    for metric in dynamic_metrics:
        colspan = len(metric["selected"]) * 2
        first_row.append(
            {"text": metric["label"], "colspan": colspan})  # 统计指标字段名
    first_row.append({"text": "统计总数", "rowspan": 3})  # 统计总数
    header.append(first_row)

    # 第二行
    second_row = []
    for metric in dynamic_metrics:
        for sub in metric["selected"]:
            second_row.append({"text": sub, "colspan": 2})  # 统计指标子选项
    header.append(second_row)

    # 第三行
    third_row = []
    for metric in dynamic_metrics:
        for _ in metric["selected"]:
            third_row.append({"text": "数量"})  # 数量
            third_row.append({"text": "占比"})  # 占比
    header.append(third_row)

    return header


def export_to_excel(header, data_rows, file_name):
    """
    导出多层表头的 Excel 文件
    :param header: 三层表头结构
    :param data_rows: 数据行
    :param file_name: 导出文件名
    """
    wb = Workbook()
    ws = wb.active

    # 写入表头
    for row_idx, row in enumerate(header, start=1):
        for col_idx, cell in enumerate(row, start=1):
            # 设置单元格的值
            ws.cell(row=row_idx, column=col_idx, value=cell["text"])
            # 居中显示
            ws.cell(row=row_idx, column=col_idx).alignment = Alignment(
                horizontal='center', vertical='center')

    # 合并单元格
    for row_idx, row in enumerate(header, start=1):
        for col_idx, cell in enumerate(row, start=1):
            if "rowspan" in cell:  # 合并行
                ws.merge_cells(
                    start_row=row_idx,
                    end_row=row_idx + cell["rowspan"] - 1,
                    start_column=col_idx,
                    end_column=col_idx
                )
            if "colspan" in cell:  # 合并列
                ws.merge_cells(
                    start_row=row_idx,
                    end_row=row_idx,
                    start_column=col_idx,
                    end_column=col_idx + cell["colspan"] - 1
                )

    # 写入数据行
    for row_idx, row in enumerate(data_rows, start=len(header) + 1):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    # 保存文件
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


@analysis_api.route("/api/analysis/report", methods=["GET"])
def analysis_report():
    try:
        # 解析请求参数
        template = request.args.get("template", "").strip()
        advanced_str = request.args.get("advanced_conditions", "").strip()
        query_mode = request.args.get("query_mode", "template").strip()
        stat_time = request.args.get("stat_time", "").strip()
        report_name = request.args.get("report_name", "").strip()

        try:
            page = int(request.args.get("page", 1))
        except ValueError:
            page = 1
        try:
            per_page = int(request.args.get("per_page", 10))
        except ValueError:
            per_page = 10

        current_app.logger.debug(
            f"请求参数 - query_mode: '{query_mode}', template: '{template}', advanced: '{advanced_str}'"
        )

        # 构造基础查询
        query = db.session.query(StudentExtension, Student).join(
            Student, StudentExtension.student_id == Student.id
        )
        if stat_time:
            query = query.filter(StudentExtension.data_year == stat_time)
        else:
            current_year = str(datetime.datetime.now().year)
            query = query.filter(StudentExtension.data_year == current_year)
            stat_time = current_year

        # 判断分支: 固定模板 or 自定义查询
        use_fixed_template = False
        if query_mode == "template":
            if template not in ["template1", "template2"]:
                return jsonify({"error": "请选择有效的预设模板"}), 400
            use_fixed_template = True
            advanced_str = ""
            current_app.logger.debug(f"使用固定模板: {template}")
        elif query_mode == "custom":
            if not advanced_str:
                return jsonify({"error": "自定义查询模式下必须传递 advanced_conditions 参数"}), 400
        else:
            return jsonify({"error": "无效的查询模式"}), 400

        # 初始化条件列表
        grouping_cols = []
        metric_conditions = []
        filter_conditions = []
        free_group_field = None

        if not use_fixed_template:
            try:
                adv_conds = json.loads(advanced_str)
                for cond in adv_conds:
                    role = cond.get("role", "").strip().lower()
                    field = cond.get("field", "").strip()
                    op = cond.get("operator", "").strip().lower()
                    val = cond.get("value", None)
                    if not field or field not in complete_fields:
                        continue
                    col = get_column_by_field(field)
                    if role == "group":
                        if not free_group_field:
                            free_group_field = field
                        grouping_cols.append(col)
                        # 当分组字段是多选时, 同时对勾选的子选项做过滤 # <-- 新增
                        # 这样只统计用户选中的分组值
                        if isinstance(val, list) and len(val) > 0:
                            filter_conditions.append(col.in_(val))  # <-- 新增
                    elif role == "metric":
                        if not isinstance(val, list) or len(val) == 0:
                            return jsonify({"error": f"统计指标 '{field}' 未选择任何子选项"}), 400
                        metric_conditions.append({
                            "field": field,
                            "selected": val,
                            "label": METRIC_CONFIG.get(field, {}).get("label", field)
                        })
                    elif role == "filter":
                        if isinstance(val, dict) and "min" in val and "max" in val:
                            try:
                                filter_conditions.append(
                                    col >= float(val["min"]))
                                filter_conditions.append(
                                    col <= float(val["max"]))
                            except ValueError:
                                pass
                        elif isinstance(val, list) and len(val) > 0:
                            filter_conditions.append(col.in_(val))
                        else:
                            if op == "=":
                                filter_conditions.append(col == val)
                            elif op == "!=":
                                filter_conditions.append(col != val)
                            elif op == "like":
                                filter_conditions.append(col.ilike(f"%{val}%"))
                            elif op in (">", "<", ">=", "<="):
                                filter_conditions.append(getattr(col, op)(val))
            except Exception as exc:
                current_app.logger.error(f"解析高级条件失败: {str(exc)}")
                return jsonify({"error": "无效的查询条件"}), 400

        # 处理分组条件
        if not use_fixed_template:
            if grouping_cols:
                grouping_expr = grouping_cols[0]
            else:
                return jsonify({"error": "自定义查询模式下未传递分组条件"}), 400
        else:
            if template == "template1":
                grouping_expr = case(
                    (and_(StudentExtension.age >= 6,
                     StudentExtension.age <= 9), literal("6-9岁")),
                    (and_(StudentExtension.age >= 10,
                     StudentExtension.age <= 12), literal("10-12岁")),
                    else_=literal("其他")
                )
                free_group_field = "age"
            elif template == "template2":
                grouping_expr = Student.gender
                free_group_field = "gender"

        if filter_conditions:
            query = query.filter(and_(*filter_conditions))

        # 统计指标
        dynamic_metrics = []
        if use_fixed_template:
            for metric in FIXED_METRICS:
                new_metric = dict(metric)
                new_metric["selected"] = metric.get("distinct_vals", [])
                dynamic_metrics.append(new_metric)
        else:
            if len(metric_conditions) == 0:
                return jsonify({"error": "自定义查询模式下必须指定至少一个统计指标"}), 400
            dynamic_metrics = metric_conditions

        # 构造查询列: 分组表达式 + total_count + 对于每个统计指标的每个子选项
        columns = [grouping_expr.label(
            "row_name"), func.count().label("total_count")]
        for metric in dynamic_metrics:
            field = metric["field"]
            col = get_column_by_field(field)
            for sub in metric["selected"]:
                expr = func.sum(case((col == sub, 1), else_=0)
                                ).label(f"{field}_{sub}_count")
                columns.append(expr)

        try:
            query = query.group_by(grouping_expr)
            dynamic_query = query.with_entities(*columns)
            paginated = dynamic_query.paginate(
                page=page, per_page=per_page, error_out=False)
            records = paginated.items
        except Exception as exc:
            current_app.logger.error(f"数据库查询错误: {str(exc)}")
            return jsonify({"error": "数据查询失败"}), 500

        # 构造数据行
        data_rows = []
        total_counts = {}
        for rec in records:
            row = []
            row.append(rec.row_name)  # 第一列: 分组值
            total = rec.total_count
            # 动态指标部分: 依次添加每个子选项的数量和计算占比
            for metric in dynamic_metrics:
                for sub in metric["selected"]:
                    count = getattr(
                        rec, f"{metric['field']}_{sub}_count", 0) or 0
                    ratio = round(count / total * 100, 2) if total else 0
                    row.append(count)
                    row.append(ratio)
            row.append(total)  # 最后一列: 统计总数
            data_rows.append(row)
            # 累加每一行数据 (从第1列到最后一列)
            for i in range(1, len(row)):
                total_counts[i] = total_counts.get(i, 0) + row[i]

        # 构造合计行
        if data_rows:
            sum_row = ["合计"]
            num_cols = len(data_rows[0])
            grand_total = total_counts.get(num_cols - 1, 0)
            for i in range(1, num_cols):
                # 最后一列直接使用累计统计总数
                if i == num_cols - 1:
                    sum_row.append(grand_total)
                else:
                    # 对于中间列: 若该列为数量列, 则取累计数量;
                    # 若为占比列, 则重新计算: 对应数量列的累计数量除以 grand_total
                    if (i - 1) % 2 == 0:
                        sum_row.append(total_counts.get(i, 0))
                    else:
                        qty = total_counts.get(i - 1, 0)
                        ratio_val = round(
                            qty / grand_total * 100, 2) if grand_total else 0
                        sum_row.append(ratio_val)
            data_rows.append(sum_row)
        else:
            data_rows = []

        # 表头构造
        FIELD_DISPLAY_MAPPING = {
            "gender": "性别",
            "age": "年龄",
            "school": "学校",
            "grade": "年级"  # <-- 新增
        }
        group_title = free_group_field if free_group_field else ""
        if group_title in FIELD_DISPLAY_MAPPING:
            group_title = FIELD_DISPLAY_MAPPING[group_title]
        header = build_multi_level_header(dynamic_metrics, group_title)

        # 报表名称和附注
        if use_fixed_template:
            final_report_name = f"{stat_time}-学生视力统计表"
        else:
            final_report_name = report_name if report_name else "统计报表"

        filters_annotation = []
        if stat_time:
            filters_annotation.append(f"统计时间: {stat_time}")
        if not use_fixed_template and advanced_str:
            try:
                adv_conds = json.loads(advanced_str)
                for cond in adv_conds:
                    if cond.get("role", "").strip().lower() == "filter":
                        field_disp = FIELD_DISPLAY_MAPPING.get(
                            cond.get("field", "").strip(), cond.get("field", "").strip())
                        filters_annotation.append(
                            f"{field_disp}: {cond.get('value')}")
            except Exception as exc:
                current_app.logger.error(f"解析筛选附注失败: {str(exc)}")
        annotation = " ".join(filters_annotation)

        response = {
            "tableName": final_report_name,
            "filterAnnotation": annotation,
            "header": header,
            "rows": data_rows,
            "total": paginated.total
        }

        # 检查是否导出
        export_flag = request.args.get("export", "").strip().lower() == "true"

        # 如果需要导出，生成Excel文件
        if export_flag:
            try:
                # 导出多层表头的 Excel 文件
                output = export_to_excel(
                    header, data_rows, f"{final_report_name}.xlsx")
                return send_file(
                    output,
                    as_attachment=True,
                    download_name=f"{final_report_name}.xlsx",
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as exc:
                current_app.logger.error(f"导出报表失败: {str(exc)}")
                return jsonify({"error": "导出报表失败"}), 500

        return jsonify(response)
    except Exception as exc:
        current_app.logger.error(f"统计报表接口异常: {str(exc)}")
        return jsonify({"error": str(exc)}), 500
