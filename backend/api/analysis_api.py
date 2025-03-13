#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: analysis_api.py
完整路径: backend/api/analysis_api.py
功能说明: 
  提供统计报表和图表数据接口，支持固定模板和自由组合查询
  实现多层表头生成、多指标统计和精确合计计算
修改记录:
  2024-03-20 新增多指标三层表头支持
  2024-03-20 重构数据聚合逻辑
  2024-03-20 优化错误处理机制
"""

import json
import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import func, and_, or_, case, literal, cast, Integer
from backend.infrastructure.database import db
from backend.models.student import Student
from backend.models.student_extension import StudentExtension

analysis_api = Blueprint("analysis_api", __name__)

# 完整字段配置（保留原有字段）
complete_fields = {
    "data_year", "education_id", "school", "grade", "class_name", "name", "gender", "age",
    "vision_level", "interv_vision_level", "left_eye_naked", "right_eye_naked",
    "left_eye_naked_interv", "right_eye_naked_interv", "left_naked_change", "right_naked_change",
    "left_sphere_change", "right_sphere_change", "left_cylinder_change", "right_cylinder_change",
    "left_axis_change", "right_axis_change", "left_interv_effect", "right_interv_effect",
    "left_sphere_effect", "right_sphere_effect", "left_cylinder_effect", "right_cylinder_effect",
    "left_axis_effect", "right_axis_effect", "left_eye_corrected", "right_eye_corrected",
    "left_keratometry_K1", "right_keratometry_K1", "left_keratometry_K2", "right_keratometry_K2",
    "left_axial_length", "right_axial_length", "left_sphere", "left_cylinder", "left_axis",
    "right_sphere", "right_cylinder", "right_axis", "left_dilated_sphere", "left_dilated_cylinder",
    "left_dilated_axis", "right_dilated_sphere", "right_dilated_cylinder", "right_dilated_axis",
    "left_sphere_interv", "left_cylinder_interv", "left_axis_interv", "right_sphere_interv",
    "right_cylinder_interv", "right_axis_interv", "left_dilated_sphere_interv", "left_dilated_cylinder_interv",
    "left_dilated_axis_interv", "right_dilated_sphere_interv", "right_dilated_cylinder_interv", "right_dilated_axis_interv",
    "guasha", "aigiu", "zhongyao_xunzheng", "rejiu_training", "xuewei_tiefu", "reci_pulse", "baoguan",
    "frame_glasses", "contact_lenses", "night_orthokeratology"
}

METRIC_CONFIG = {
    "vision_level": {"label": "视力等级", "type": "dropdown"},
    "interv_vision_level": {"label": "干预后视力等级", "type": "dropdown"},
    "left_interv_effect": {"label": "左眼干预效果", "type": "multi-select"},
    "right_interv_effect": {"label": "右眼干预效果", "type": "multi-select"}
}


def get_column_by_field(field):
    """根据字段名获取对应的数据库列对象"""
    if hasattr(StudentExtension, field):
        return getattr(StudentExtension, field)
    elif hasattr(Student, field):
        return getattr(Student, field)
    raise ValueError(f"字段'{field}'不存在")


def build_multi_level_header(metrics, group_title):
    """构建三层表头结构"""
    header = []

    # 第一层：分组列 + 指标名称
    first_row = [{"text": group_title, "rowspan": 3}]
    for metric in metrics:
        colspan = len(metric["distinct_vals"]) * 2
        first_row.append({"text": metric["label"], "colspan": colspan})
    first_row.append({"text": "统计总数", "rowspan": 3})
    header.append(first_row)

    # 第二层：指标选项
    second_row = []
    for metric in metrics:
        for val in metric["distinct_vals"]:
            second_row.append({"text": val, "colspan": 2})
    header.append(second_row)

    # 第三层：数量/占比
    third_row = []
    for metric in metrics:
        for _ in metric["distinct_vals"]:
            third_row.append({"text": "数量"})
            third_row.append({"text": "占比"})
    header.append(third_row)

    return header


@analysis_api.route("/api/analysis/report", methods=["GET"])
def analysis_report():
    # 参数解析（完整保留原有逻辑）
    template = request.args.get("template", "").strip()
    advanced_str = request.args.get("advanced_conditions", "").strip()
    stat_time = request.args.get("stat_time", "").strip()
    school = request.args.get("school", "").strip()
    custom_name = request.args.get("report_name", "").strip()

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        per_page = 10

    current_app.logger.debug(
        f"请求参数 - template:{template}, advanced:{advanced_str}")

    # 基础查询构造（完整保留）
    query = db.session.query(StudentExtension, Student).join(
        Student, StudentExtension.student_id == Student.id
    )
    if stat_time:
        query = query.filter(StudentExtension.data_year == stat_time)
    else:
        current_year = str(datetime.datetime.now().year)
        query = query.filter(StudentExtension.data_year == current_year)
        stat_time = current_year
    if school:
        query = query.filter(Student.school == school)

    # 模板模式处理（完整保留）
    use_fixed_template = False
    if template in ["template1", "template2"]:
        use_fixed_template = True
        advanced_str = ""
        current_app.logger.debug(f"使用固定模板: {template}")

    # 解析组合条件（完整保留+增强）
    grouping_cols = []
    filters = []
    free_group_field = None
    metric_list = []

    if not use_fixed_template and advanced_str:
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
                elif role == "metric":
                    metric_list.append(field)
                elif role == "filter":
                    if isinstance(val, dict) and "min" in val and "max" in val:
                        try:
                            filters.append(col >= float(val["min"]))
                            filters.append(col <= float(val["max"]))
                        except ValueError:
                            pass
                    elif isinstance(val, list):
                        filters.append(col.in_(val))
                    else:
                        if op == '=':
                            filters.append(col == val)
                        elif op == '!=':
                            filters.append(col != val)
                        elif op == 'like':
                            filters.append(col.ilike(f"%{val}%"))
                        elif op in ('>', '<', '>=', '<='):
                            filters.append(getattr(col, op)(val))
        except Exception as e:
            current_app.logger.error(f"解析组合条件失败: {str(e)}")
            return jsonify({"error": "无效的查询条件"}), 400

    # 分组表达式处理（完整保留+增强）
    grouping_expr = None
    if use_fixed_template:
        if template == "template1":
            grouping_expr = case(
                (and_(StudentExtension.age >= 6,
                 StudentExtension.age <= 9), literal("6-9岁")),
                (and_(StudentExtension.age >= 10,
                 StudentExtension.age <= 12), literal("10-12岁")),
                else_=literal("其他")
            )
        elif template == "template2":
            grouping_expr = Student.gender
    else:
        if grouping_cols:
            grouping_expr = grouping_cols[0]

    if not grouping_expr:
        return jsonify({"error": "必须指定分组条件"}), 400

    if filters:
        query = query.filter(and_(*filters))

    # 动态指标处理（新增核心逻辑）
    dynamic_metrics = []
    if not use_fixed_template and metric_list:
        for field in metric_list:
            try:
                col = get_column_by_field(field)
                distinct_vals = [v[0] for v in db.session.query(
                    col).distinct().all() if v[0] is not None]
                distinct_vals.sort()

                aggregators = []
                for val in distinct_vals:
                    expr = func.sum(case([(col == val, 1)], else_=0)).label(
                        f"{field}_{val}_count")
                    aggregators.append((val, expr))

                dynamic_metrics.append({
                    "field": field,
                    "label": METRIC_CONFIG.get(field, {}).get("label", field),
                    "distinct_vals": distinct_vals,
                    "aggregators": aggregators
                })
            except Exception as e:
                current_app.logger.error(f"处理统计指标失败: {str(e)}")
                return jsonify({"error": f"无效统计指标: {field}"}), 400

    # 构建查询列（整合原有+新增）
    columns = [grouping_expr.label(
        "row_name"), func.count().label("total_count")]
    for metric in dynamic_metrics:
        for _, expr in metric["aggregators"]:
            columns.append(expr)

    # 执行查询（完整保留分页逻辑）
    try:
        query = query.group_by(grouping_expr)
        dynamic_query = query.with_entities(*columns)
        paginated = dynamic_query.paginate(
            page=page, per_page=per_page, error_out=False)
        records = paginated.items
    except Exception as e:
        current_app.logger.error(f"数据库查询错误: {str(e)}")
        return jsonify({"error": "数据查询失败"}), 500

    # 构建数据行（完整处理逻辑）
    data_rows = []
    total_counts = {}
    for rec in records:
        row = {
            "row_name": rec.row_name,
            "total_count": rec.total_count
        }

        metric_index = 2  # 前两列是分组和总数
        for metric in dynamic_metrics:
            for val in metric["distinct_vals"]:
                count = getattr(rec, f"{metric['field']}_{val}_count", 0) or 0
                ratio = (count / rec.total_count *
                         100) if rec.total_count else 0

                row[f"{metric['field']}_{val}_count"] = count
                row[f"{metric['field']}_{val}_ratio"] = round(ratio, 2)

                # 合计统计
                total_counts[f"{metric['field']}_{val}_count"] = total_counts.get(
                    f"{metric['field']}_{val}_count", 0) + count
                metric_index += 1

        data_rows.append(row)

    # 添加合计行（完整计算逻辑）
    if data_rows:
        sum_row = {
            "row_name": "合计",
            "total_count": sum(r["total_count"] for r in data_rows)
        }

        for key in total_counts:
            sum_row[key] = total_counts[key]
            ratio_key = key.replace("_count", "_ratio")
            sum_row[ratio_key] = round(
                (total_counts[key] / sum_row["total_count"] * 100), 2) if sum_row["total_count"] else 0

        data_rows.append(sum_row)

    # 构建表头（完整逻辑）
    group_title = free_group_field if free_group_field else "分组"
    if len(dynamic_metrics) > 1:
        header = build_multi_level_header(dynamic_metrics, group_title)
    elif use_fixed_template:
        header = [
            [{"text": "年龄段" if template == "template1" else "性别", "rowspan": 2}] +
            [{"text": "临床前期近视", "colspan": 2}, {"text": "轻度近视", "colspan": 2},
             {"text": "中度近视", "colspan": 2}, {"text": "统计总数", "rowspan": 2}],
            [{"text": "数量"}, {"text": "占比"}, {"text": "数量"}, {"text": "占比"},
             {"text": "数量"}, {"text": "占比"}]
        ]
    else:
        header = [
            [{"text": group_title, "rowspan": 2}] +
            [{"text": "临床前期近视", "colspan": 2}, {"text": "轻度近视", "colspan": 2},
             {"text": "中度近视", "colspan": 2}, {"text": "统计总数", "rowspan": 2}],
            [{"text": "数量"}, {"text": "占比"}, {"text": "数量"}, {"text": "占比"},
             {"text": "数量"}, {"text": "占比"}]
        ]

    return jsonify({
        "tableName": custom_name if custom_name else f"{stat_time}统计报表",
        "header": header,
        "rows": data_rows,
        "total": paginated.total
    })


@analysis_api.route("/api/analysis/chart", methods=["GET"])
def analysis_chart():
    # ... 保留原有图表接口完整代码 ...
    """
    图表数据接口:
      返回适用于 Chart.js 的数据格式。示例仅演示简单结构:
      {
        "labels": ["男", "女"],
        "datasets": [
          {
            "label": "临床前期近视(人数)",
            "data": [18, 12],
            "backgroundColor": ["rgba(75, 192, 192, 0.5)", "rgba(153, 102, 255, 0.5)"]
          }
        ]
      }
    """
    # 此处仅返回示例数据，可根据需要调整
    return jsonify({
        "labels": ["男", "女"],
        "datasets": [
            {
                "label": "临床前期近视(人数)",
                "data": [18, 12],
                "backgroundColor": [
                    "rgba(75, 192, 192, 0.5)",
                    "rgba(153, 102, 255, 0.5)"
                ]
            }
        ]
    })
