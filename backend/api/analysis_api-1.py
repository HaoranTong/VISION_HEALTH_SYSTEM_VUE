#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: analysis_api.py
完整存储路径: backend/api/analysis_api.py

功能说明:
  1. 提供统计报表数据接口 (/api/analysis/report)，支持固定模板（template1=按年龄段, template2=按性别）
     和自由组合查询（advanced_conditions）。
  2. 当使用自由组合查询且只存在一个统计指标 (role="metric") 时，自动检测该字段的 distinct 值，
     并为每个 distinct 值生成“数量”和“占比”两列，构造多层表头。
  3. 若存在多个统计指标，或未指定 metric，则仍旧使用示例化的“临床前期近视、轻度近视、中度近视、视力不良”列。
  4. 提供图表数据接口 (/api/analysis/chart) 返回适用于 Chart.js 的数据格式。

注意:
  1. 此示例仅演示单个统计指标的动态列生成，不支持一次选择多个指标 (需要更复杂的 pivot)。
  2. 若要支持更多高级逻辑（如三层表头、多字段并行统计），请在此基础上扩展。
"""

import json
import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import func, and_, or_, case, literal, cast, Integer
from backend.infrastructure.database import db
from backend.models.student import Student
from backend.models.student_extension import StudentExtension

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
    "left_axial_length", "right_axial_length", "left_sphere", "left_cylinder", "left_axis",
    "right_sphere", "right_cylinder", "right_axis", "left_dilated_sphere", "left_dilated_cylinder",
    "left_dilated_axis", "right_dilated_sphere", "right_dilated_cylinder", "right_dilated_axis",
    "left_sphere_interv", "left_cylinder_interv", "left_axis_interv", "right_sphere_interv",
    "right_cylinder_interv", "right_axis_interv", "left_dilated_sphere_interv", "left_dilated_cylinder_interv",
    "left_dilated_axis_interv", "right_dilated_sphere_interv", "right_dilated_cylinder_interv", "right_dilated_axis_interv",
    "guasha", "aigiu", "zhongyao_xunzheng", "rejiu_training", "xuewei_tiefu", "reci_pulse", "baoguan",
    "frame_glasses", "contact_lenses", "night_orthokeratology"
}


@analysis_api.route("/api/analysis/report", methods=["GET"])
def analysis_report():
    # 1. 解析请求参数
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
        f"[analysis_report] stat_time={stat_time}, school={school}, "
        f"template={template}, advanced={advanced_str}, page={page}, per_page={per_page}"
    )

    # 2. 构造基础查询
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

    # 3. 判断是否为固定模板模式
    use_fixed_template = False
    if template in ["template1", "template2"]:
        use_fixed_template = True
        current_app.logger.debug(
            f"[analysis_report] Using fixed template: {template}")
        advanced_str = ""  # 忽略 advanced_conditions

    grouping_cols = []
    filters = []
    free_group_field = None
    metric_list = []  # 修改: 用列表存储所有 metric 字段

    # 4. 解析自由组合查询
    if not use_fixed_template and advanced_str:
        try:
            adv_conds = json.loads(advanced_str)
            current_app.logger.debug(
                "[analysis_report] Parsing advanced_conditions...")
            for cond in adv_conds:
                role = cond.get("role", "").strip().lower()
                field = cond.get("field", "").strip()
                op = cond.get("operator", "").strip().lower()
                val = cond.get("value", None)
                current_app.logger.debug(
                    f"[analysis_report] Condition => role={role}, field={field}, operator={op}, value={val}"
                )
                if not field or field not in complete_fields:
                    current_app.logger.warning(
                        f"[analysis_report] Field '{field}' not allowed or empty, ignore."
                    )
                    continue
                if hasattr(StudentExtension, field):
                    col = getattr(StudentExtension, field)
                elif hasattr(Student, field):
                    col = getattr(Student, field)
                else:
                    current_app.logger.warning(
                        f"[analysis_report] Unknown field: {field}"
                    )
                    continue

                if role == "group":
                    if free_group_field is None:
                        free_group_field = field
                    grouping_cols.append(col)
                elif role == "metric":
                    # 收集 metric 字段
                    metric_list.append(field)
                elif role == "filter":
                    if isinstance(val, dict) and "min" in val and "max" in val:
                        try:
                            minv = float(val["min"])
                            maxv = float(val["max"])
                            filters.append(col >= minv)
                            filters.append(col <= maxv)
                        except Exception:
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
                        elif op == '>':
                            filters.append(col > val)
                        elif op == '<':
                            filters.append(col < val)
                        elif op == '>=':
                            filters.append(col >= val)
                        elif op == '<=':
                            filters.append(col <= val)
        except Exception as e:
            current_app.logger.error(
                f"[analysis_report] Error parsing advanced_conditions: {e}")

    # 5. 构造分组表达式
    grouping_expr = None
    if use_fixed_template:
        # 模板模式
        if template == "template1":
            # 按年龄段
            grouping_expr = case(
                (and_(StudentExtension.age >= 6,
                 StudentExtension.age <= 9), literal("6-9岁")),
                (and_(StudentExtension.age >= 10,
                 StudentExtension.age <= 12), literal("10-12岁")),
                else_=literal("其他")
            )
        elif template == "template2":
            # 按性别
            grouping_expr = Student.gender
    else:
        # 自由组合
        if len(grouping_cols) >= 1:
            grouping_expr = grouping_cols[0]

    if grouping_expr is None:
        current_app.logger.error("[analysis_report] 分组条件未设置")
        return jsonify({"error": "未设置分组条件，请检查查询设置"}), 400

    if filters:
        query = query.filter(and_(*filters))

    try:
        query = query.group_by(grouping_expr)
    except Exception as e:
        current_app.logger.error(f"[analysis_report] group_by error: {e}")
        return jsonify({"error": "分组条件错误，请检查查询设置"}), 400

    # ============= 6. 根据 metric_list 判断统计指标 =============
    # 场景1: use_fixed_template = True => 按“临床前期近视/轻度近视/中度近视/视力不良”方式
    # 场景2: 自由组合, 如果 metric_list 为空 => 同样用默认“临床前期近视...”做演示
    # 场景3: 自由组合, 如果 metric_list 恰好只有1个 => 动态获取 distinct 值并统计
    #  (多metric场景需要更复杂的三层表头, 此处暂不实现)
    dynamic_metrics = []  # 存放 (distinctValue, aggregator) 用于后续构造列

    use_dynamic_metric = False
    single_metric_field = None
    if not use_fixed_template:
        if len(metric_list) == 1:
            single_metric_field = metric_list[0]
            use_dynamic_metric = True
        elif len(metric_list) > 1:
            current_app.logger.warning(
                "[analysis_report] Multiple metrics not fully implemented, using default columns")

    # 场景: use_dynamic_metric = True => 构造 pivot
    if use_dynamic_metric and single_metric_field:
        # 先获取 distinct 值
        # 不能直接records，因为records是group_by后的结果
        # 需要先查询 StudentExtension 中 distinct single_metric_field
        DistinctModelCol = None
        if hasattr(StudentExtension, single_metric_field):
            DistinctModelCol = getattr(StudentExtension, single_metric_field)
        elif hasattr(Student, single_metric_field):
            DistinctModelCol = getattr(Student, single_metric_field)

        distinct_vals = [r[0] for r in db.session.query(
            DistinctModelCol).distinct() if r[0] is not None]
        distinct_vals.sort()  # 让列有序

        # 构造 case表达式 aggregator
        # aggregator_list => sum( case( col==val, 1, 0 ) )
        aggregator_list = []
        for val in distinct_vals:
            aggregator_list.append((
                val,
                func.sum(case((DistinctModelCol == val, 1), else_=0)
                         ).label(f"metric_{val}")
            ))

        # 把 aggregator_list 拼到 query
        # grouping_expr 已经 group_by => aggregator
        # 先保留 group_by expr
        columns = [grouping_expr.label(
            "row_name"), func.count().label("total_count")]
        for val, agg_col in aggregator_list:
            columns.append(agg_col)
        # 重新生成 query
        dynamic_query = query.with_entities(*columns)
        records = dynamic_query.all()
        total = len(records)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_records = records[start:end]

        # 生成表头 (2层)
        # 第一行: 分组字段 + distinct vals (colspan=2 each) + 统计总数
        # 第二行: 数量, 占比 for each distinct val
        group_title = free_group_field if free_group_field else "分组"
        first_row = []
        first_row.append({"text": group_title, "rowspan": 2})
        for val in distinct_vals:
            first_row.append({"text": str(val), "colspan": 2})
        first_row.append({"text": "统计总数", "rowspan": 2})

        second_row = []
        for _ in distinct_vals:
            second_row.append({"text": "数量"})
            second_row.append({"text": "占比"})
        header = [first_row, second_row]

        # 构造数据行
        data_rows = []
        for rec in paginated_records:
            row_name = rec[0]
            total_count = rec[1] or 0
            # rec[2], rec[3], ... => aggregator for distinct vals
            row_dict = {
                "row_name": row_name,
                "total_count": total_count
            }
            idx_base = 2  # aggregator起始index
            # 先存 aggregator 数值
            aggregator_values = rec[idx_base:]  # tuple
            # 先不填 => 由distinct_vals index
            # 先放 aggregator to row_dict
            # 例如 "metric_一年级": aggregator_values[i], ...
            # 但是前端渲染需要 { "xxx_count":, "xxx_ratio": } => 需打平
            # 这里简单存 row_dict[f"{val}_count"], row_dict[f"{val}_ratio"]
            for i, val in enumerate(distinct_vals):
                col_value = aggregator_values[i] or 0
                ratio = 0
                if total_count > 0:
                    ratio = round(col_value / total_count * 100, 2)
                row_dict[f"{val}_count"] = col_value
                row_dict[f"{val}_ratio"] = ratio

            data_rows.append(row_dict)

        # 合计行
        sum_total = sum(r["total_count"] for r in data_rows)
        sum_row = {
            "row_name": "合计",
            "total_count": sum_total
        }
        for val in distinct_vals:
            col_sum = sum(r[f"{val}_count"] for r in data_rows)
            ratio = 0
            if sum_total > 0:
                ratio = round(col_sum / sum_total * 100, 2)
            sum_row[f"{val}_count"] = col_sum
            sum_row[f"{val}_ratio"] = ratio
        data_rows.append(sum_row)

        return jsonify({
            "tableName": custom_name if custom_name else f"{stat_time} 学生视力功能统计表",
            "header": header,
            "rows": data_rows,
            "total": len(data_rows)
        })

    # ===== 否则走原有逻辑 (模板 or 默认) =====

    # 6. 统计指标计算 (示例: 临床前期近视, 轻度近视, 中度近视, 视力不良)
    pre_clinic_expr = func.sum(
        cast((StudentExtension.vision_level == "临床前期近视"), Integer))
    mild_expr = func.sum(
        cast((StudentExtension.vision_level == "轻度近视"), Integer))
    moderate_expr = func.sum(
        cast((StudentExtension.vision_level == "中度近视"), Integer))
    bad_vision_expr = pre_clinic_expr + mild_expr + moderate_expr

    aggregated_query = query.with_entities(
        grouping_expr.label("row_name"),
        pre_clinic_expr.label("pre_clinic_count"),
        mild_expr.label("mild_count"),
        moderate_expr.label("moderate_count"),
        bad_vision_expr.label("bad_vision_count"),
        func.count().label("total_count")
    )

    records = aggregated_query.all()
    total = len(records)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_records = records[start:end]

    # 7. 构造表头 (2层表头示例)
    if use_fixed_template:
        if template == "template1":
            group_title = "年龄段"
        elif template == "template2":
            group_title = "性别"
        else:
            group_title = "分组"

        flat_indicator_titles = ["临床前期近视", "轻度近视", "中度近视", "视力不良"]
        first_row = []
        first_row.append({"text": group_title, "rowspan": 2})
        for title in flat_indicator_titles:
            first_row.append({"text": title, "colspan": 2})
        first_row.append({"text": "统计总数", "rowspan": 2})
        second_row = []
        for _ in flat_indicator_titles:
            second_row.append({"text": "数量"})
            second_row.append({"text": "占比"})
        header = [first_row, second_row]
    else:
        # 无模板, 但没有metric 或 multiple metrics => 用默认
        if free_group_field == "gender":
            group_title = "性别"
        elif free_group_field == "age":
            group_title = "年龄"
        else:
            group_title = free_group_field if free_group_field else "分组"
        flat_indicator_titles = ["临床前期近视", "轻度近视", "中度近视", "视力不良"]
        first_row = []
        first_row.append({"text": group_title, "rowspan": 2})
        for title in flat_indicator_titles:
            first_row.append({"text": title, "colspan": 2})
        first_row.append({"text": "统计总数", "rowspan": 2})
        second_row = []
        for _ in flat_indicator_titles:
            second_row.append({"text": "数量"})
            second_row.append({"text": "占比"})
        header = [first_row, second_row]

    # 8. 构造数据行及计算占比
    data_rows = []
    for rec in paginated_records:
        total_count = rec.total_count or 0
        pre_clinic_ratio = 0
        mild_ratio = 0
        moderate_ratio = 0
        bad_vision_ratio = 0
        if total_count > 0:
            pre_clinic_ratio = round(
                rec.pre_clinic_count / total_count * 100, 2)
            mild_ratio = round(rec.mild_count / total_count * 100, 2)
            moderate_ratio = round(rec.moderate_count / total_count * 100, 2)
            bad_vision_ratio = round(
                (rec.bad_vision_count) / total_count * 100, 2)

        row_data = {
            "row_name": rec.row_name,
            "pre_clinic_count": rec.pre_clinic_count,
            "pre_clinic_ratio": pre_clinic_ratio,
            "mild_count": rec.mild_count,
            "mild_ratio": mild_ratio,
            "moderate_count": rec.moderate_count,
            "moderate_ratio": moderate_ratio,
            "bad_vision_count": rec.bad_vision_count,
            "bad_vision_ratio": bad_vision_ratio,
            "total_count": total_count
        }
        data_rows.append(row_data)

    # 合计行
    sum_pre = sum(r["pre_clinic_count"] for r in data_rows)
    sum_mild = sum(r["mild_count"] for r in data_rows)
    sum_moderate = sum(r["moderate_count"] for r in data_rows)
    sum_bad = sum(r["bad_vision_count"] for r in data_rows)
    sum_total = sum(r["total_count"] for r in data_rows)

    sum_pre_ratio = 0
    sum_mild_ratio = 0
    sum_moderate_ratio = 0
    sum_bad_ratio = 0
    if sum_total > 0:
        sum_pre_ratio = round(sum_pre / sum_total * 100, 2)
        sum_mild_ratio = round(sum_mild / sum_total * 100, 2)
        sum_moderate_ratio = round(sum_moderate / sum_total * 100, 2)
        sum_bad_ratio = round(sum_bad / sum_total * 100, 2)

    data_rows.append({
        "row_name": "合计",
        "pre_clinic_count": sum_pre,
        "pre_clinic_ratio": sum_pre_ratio,
        "mild_count": sum_mild,
        "mild_ratio": sum_mild_ratio,
        "moderate_count": sum_moderate,
        "moderate_ratio": sum_moderate_ratio,
        "bad_vision_count": sum_bad,
        "bad_vision_ratio": sum_bad_ratio,
        "total_count": sum_total
    })

    return jsonify({
        "tableName": custom_name if custom_name else f"{stat_time} 学生视力功能统计表",
        "header": header,
        "rows": data_rows,
        "total": len(data_rows)
    })


@analysis_api.route("/api/analysis/chart", methods=["GET"])
def analysis_chart():
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
