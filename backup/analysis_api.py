#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: analysis_api.py
完整存储路径: backend/api/analysis_api.py

功能说明:
    提供统计分析相关的 API 接口，包括固定模板查询（template1=按年龄段, template2=按性别）
    和自由组合查询（advanced_conditions）。在自由组合查询中，前端可指定三种角色:
      - role="metric": 统计指标
      - role="group":  分组字段
      - role="filter": 普通过滤条件
    如果 role=""，则后端会将其视为普通过滤条件(filter)进行处理。

    关键点修复:
      1. 对于同一字段的多条 "metric" 条件，采用精确匹配并用 IN(...) 进行 OR 合并，避免多次 AND 导致 0 行或重复计数。
      2. 避免使用 like 进行精确匹配场景；如需精确匹配，用 col == value 或 col.in_([...])。
      3. 在构造查询时，选取 StudentExtension 作为主表，并 join Student 仅获取分组或其他必要字段；通过 distinct(StudentExtension.id)
         确保每条记录只计数一次。
      4. 保持原有固定模板查询的逻辑不被破坏；若 advanced_conditions 存在，则忽略 template。
      5. 若 role="" 则默认视为 "filter" 处理，使用 operator 对应的方式（==、!=、like 等）进行普通过滤。

使用方法:
    GET 参数:
      - stat_time: 数据年份(若空则默认为当前年份)
      - school: 学校(精确匹配, 可按需求改为模糊)
      - template: "template1"(按年龄段)或"template2"(按性别), 若 advanced_conditions 不为空则忽略 template
      - advanced_conditions: JSON 数组字符串, 每项包含:
          {
            "role": "metric"/"group"/"filter" (或空),
            "field": "xxx",
            "operator": "like"/"="/"!=" 等,
            "value": "xxx"
          }
      - page, per_page: 分页参数
    返回:
      JSON 格式, 包含:
        {
          "tableName": "...",
          "header": [...],
          "rows": [...],
          "total": ...
        }
"""

import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import func, and_, case
from backend.infrastructure.database import db
from backend.models.student import Student
from backend.models.student_extension import StudentExtension

analysis_api = Blueprint("analysis_api", __name__)


def find_column(field_name):
    """
    帮助函数:
    根据字段名返回对应的 SQLAlchemy 列对象。先在 StudentExtension 中查找,
    若无则在 Student 中查找, 若都无则返回 None。
    """
    if hasattr(StudentExtension, field_name):
        return getattr(StudentExtension, field_name)
    elif hasattr(Student, field_name):
        return getattr(Student, field_name)
    return None


@analysis_api.route("/api/analysis/report", methods=["GET"])
def analysis_report():
    """
    统计报表数据接口:
      - 支持固定模板(template1=按年龄段, template2=按性别)和自由组合查询(advanced_conditions)。
      - 对于自由组合查询:
        * 同一字段的多条 metric 条件 => 使用 in_([...]) OR 合并
        * role="group" => 分组字段 => group_field
        * role="filter" => 普通过滤 => 根据 operator(=, !=, like) 等做 AND 过滤
        * role="" => 也当作 "filter"
      - 使用 StudentExtension 作为主表, join Student 以获取 gender 等字段,
        并 distinct(StudentExtension.id) 确保每条记录只统计一次。
    """
    # 1. 解析前端参数
    stat_time = request.args.get("stat_time", "").strip()
    if not stat_time:
        stat_time = str(datetime.now().year)  # 默认当前年份

    school = request.args.get("school", "").strip()
    template = request.args.get("template", "").strip()
    adv_str = request.args.get("advanced_conditions", "").strip()
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        per_page = 10

    current_app.logger.debug(
        f"[analysis_report] stat_time={stat_time}, school={school}, template={template}, "
        f"advanced_conditions={adv_str}, page={page}, per_page={per_page}"
    )

    # 2. 以 StudentExtension 为主表, join Student 获取分组/其他字段
    base_query = db.session.query(
        StudentExtension.id.label("ext_id"),
        StudentExtension.age.label("age"),
        StudentExtension.vision_level.label("vision_level"),
        StudentExtension.interv_vision_level.label("interv_vision_level"),
        Student.gender.label("gender")
    ).join(Student, StudentExtension.student_id == Student.id)

    # 数据年份过滤
    base_query = base_query.filter(StudentExtension.data_year == stat_time)

    # 如果有 school, 按需过滤(精确匹配)
    if school:
        base_query = base_query.filter(Student.school == school)

    # distinct 防止重复计数
    base_query = base_query.distinct(StudentExtension.id)

    # 3. 解析 advanced_conditions
    free_query_mode = bool(adv_str)
    group_conditions = {}   # dict[field_name -> set(values)]  分组字段
    metric_conditions = {}  # dict[field_name -> set(values)]  统计指标字段
    advanced_filters = []   # 其他过滤条件

    if free_query_mode:
        current_app.logger.debug(
            "[analysis_report] Parsing advanced_conditions...")
        try:
            conds = json.loads(adv_str)
            for c in conds:
                role = c.get("role", "").strip() or "filter"  # 若空, 当作filter
                field = c.get("field", "").strip()
                operator = c.get("operator", "").strip().lower()
                value = c.get("value", None)

                current_app.logger.debug(
                    f"    Condition => role={role}, field={field}, operator={operator}, value={value}"
                )
                if not field or not operator:
                    continue

                col = find_column(field)
                if not col:
                    current_app.logger.debug(
                        f"    - skip: field {field} not found in models.")
                    continue

                if role == "group":
                    # 分组字段 => group_conditions[field] = {val1, val2,...}
                    group_conditions.setdefault(field, set()).add(value)
                elif role == "metric":
                    # metric => 不使用like, 用精确匹配 => col.in_([...]) OR
                    metric_conditions.setdefault(field, set()).add(value)
                else:
                    # role="filter" 或 ""
                    # 走普通过滤
                    if operator == "=":
                        advanced_filters.append(col == value)
                    elif operator == "!=":
                        advanced_filters.append(col != value)
                    elif operator == "like":
                        # 仍然保留like以兼容某些模糊场景
                        advanced_filters.append(col.ilike(f"%{value}%"))
                    # 可扩展其他运算符: >, <, >=, <= 等
        except Exception as e:
            current_app.logger.error(
                f"[analysis_report] advanced_conditions parse error: {e}")

    # 合并 metric 条件 => 同一字段 => in_(...)
    for m_field, m_vals in metric_conditions.items():
        m_col = find_column(m_field)
        if not m_col:
            continue
        if len(m_vals) == 1:
            val = list(m_vals)[0]
            advanced_filters.append(m_col == val)
        else:
            advanced_filters.append(m_col.in_(list(m_vals)))

    # 若有 advanced_filters => AND 连接
    if advanced_filters:
        from sqlalchemy import and_
        current_app.logger.debug(
            f"[analysis_report] Merging {len(advanced_filters)} advanced_filters with AND.")
        base_query = base_query.filter(and_(*advanced_filters))

    # 4. 确定分组字段 group_field
    group_field = None
    if free_query_mode and group_conditions:
        # 取第一条 group 条件(仅支持单字段分组)
        for gf, gf_vals in group_conditions.items():
            gf_col = find_column(gf)
            if gf_col:
                group_field = gf_col
                base_query = base_query.filter(gf_col.in_(list(gf_vals)))
                break
        # 忽略 template
        template = ""
        current_app.logger.debug(
            "[analysis_report] free_query_mode => grouping by advanced_conditions.")
    else:
        # 若无 advanced_conditions => 看 template
        if not free_query_mode:
            if template == "template1":
                current_app.logger.debug(
                    "[analysis_report] fixed template=template1 => group by age bucket.")
                group_field = case(
                    (and_(StudentExtension.age != None, StudentExtension.age >=
                     6, StudentExtension.age <= 9), "6-9岁"),
                    (and_(StudentExtension.age != None, StudentExtension.age >=
                     10, StudentExtension.age <= 12), "10-12岁"),
                    else_="其他"
                )
            elif template == "template2":
                current_app.logger.debug(
                    "[analysis_report] fixed template=template2 => group by gender.")
                group_field = Student.gender
            else:
                current_app.logger.debug(
                    "[analysis_report] unknown template => return empty.")
                return jsonify({
                    "tableName": "统计报表(默认)",
                    "header": ["无数据"],
                    "rows": [],
                    "total": 0
                })

    if not group_field:
        current_app.logger.debug(
            "[analysis_report] no group field => return empty result.")
        return jsonify({
            "tableName": "自由组合查询统计报表",
            "header": ["无数据"],
            "rows": [],
            "total": 0
        })

    # 5. 子查询 => 保证每条记录只出现一次
    subq = base_query.subquery()
    group_col = group_field.label("row_name") if hasattr(
        group_field, "label") else group_field

    # 6. 构造聚合表达式(以 vision_level 统计 => pre_clinic, mild, moderate)
    pre_clinic_expr = func.count(case((subq.c.vision_level == "临床前期近视", 1)))
    mild_expr = func.count(case((subq.c.vision_level == "轻度近视", 1)))
    mod_expr = func.count(case((subq.c.vision_level == "中度近视", 1)))
    total_expr = func.count()
    bad_expr = pre_clinic_expr + mild_expr + mod_expr

    agg_query = db.session.query(
        group_col,
        total_expr.label("total_count"),
        pre_clinic_expr.label("pre_clinic_count"),
        mild_expr.label("mild_count"),
        mod_expr.label("moderate_count"),
        bad_expr.label("bad_vision_count")
    ).select_from(subq).group_by(group_col)

    current_app.logger.debug("[analysis_report] executing aggregator ...")
    agg_results = agg_query.all()
    current_app.logger.debug(
        f"[analysis_report] aggregator returned {len(agg_results)} rows.")

    # 7. 组装rows
    rows = []
    for r in agg_results:
        tv = r.total_count if r.total_count else 1
        row_data = {
            "row_name": r.row_name if r.row_name else "无",
            "pre_clinic_count": r.pre_clinic_count,
            "pre_clinic_ratio": round(r.pre_clinic_count / tv * 100, 2),
            "mild_count": r.mild_count,
            "mild_ratio": round(r.mild_count / tv * 100, 2),
            "moderate_count": r.moderate_count,
            "moderate_ratio": round(r.moderate_count / tv * 100, 2),
            "bad_vision_count": r.bad_vision_count,
            "bad_vision_ratio": round(r.bad_vision_count / tv * 100, 2),
            "total_count": r.total_count
        }
        rows.append(row_data)

    # 合计行
    if rows:
        sum_pre = sum(x["pre_clinic_count"] for x in rows)
        sum_mild = sum(x["mild_count"] for x in rows)
        sum_mod = sum(x["moderate_count"] for x in rows)
        sum_bad = sum(x["bad_vision_count"] for x in rows)
        sum_total = sum(x["total_count"] for x in rows)
        sum_row = {
            "row_name": "合计",
            "pre_clinic_count": sum_pre,
            "pre_clinic_ratio": round(sum_pre / sum_total * 100, 2) if sum_total else 0,
            "mild_count": sum_mild,
            "mild_ratio": round(sum_mild / sum_total * 100, 2) if sum_total else 0,
            "moderate_count": sum_mod,
            "moderate_ratio": round(sum_mod / sum_total * 100, 2) if sum_total else 0,
            "bad_vision_count": sum_bad,
            "bad_vision_ratio": round(sum_bad / sum_total * 100, 2) if sum_total else 0,
            "total_count": sum_total
        }
        rows.append(sum_row)

    total_rows = len(rows)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_rows = rows[start_idx:end_idx]

    # 8. 构造表头 => 根据 template / group_conditions 区分
    field_label_map = {
        "gender": "性别",
        "class_name": "班级",
        "vision_level": "视力等级",
        "interv_vision_level": "干预后视力等级"
    }
    default_group_title = "分组"
    if free_query_mode and group_conditions:
        for gf in group_conditions.keys():
            col = find_column(gf)
            if col and hasattr(col, "key") and col.key in field_label_map:
                default_group_title = field_label_map[col.key]
                break
    else:
        if template == "template1":
            default_group_title = "年龄段"
        elif template == "template2":
            default_group_title = "性别"

    header = [
        default_group_title,
        "临床前期近视(人数)", "临床前期近视(占比)",
        "轻度近视(人数)", "轻度近视(占比)",
        "中度近视(人数)", "中度近视(占比)",
        "视力不良(人数)", "视力不良(占比)",
        "统计人数"
    ]

    # 9. 确定表名
    if not free_query_mode:
        if template == "template1":
            table_name = f"{stat_time}-学生视力情况统计表-预防干预前(按年龄段)"
        elif template == "template2":
            table_name = f"{stat_time}-学生视力情况统计表-预防干预前(按性别)"
        else:
            table_name = "统计报表(默认)"
    else:
        table_name = "自由组合查询统计报表"

    resp = {
        "tableName": table_name,
        "header": header,
        "rows": paginated_rows,
        "total": total_rows
    }
    current_app.logger.debug(f"[analysis_report] Final response => {resp}")
    return jsonify(resp)


@analysis_api.route("/api/analysis/chart", methods=["GET"])
def analysis_chart():
    """
    图表数据接口(示例):
      根据 advanced_conditions 返回静态示例数据。
      真实逻辑可根据聚合查询结果生成图表数据。
    """
    adv_str = request.args.get("advanced_conditions", "").strip()
    current_app.logger.debug(f"[analysis_chart] advanced_conditions={adv_str}")
    if adv_str:
        data = {
            "labels": ["过滤后-男", "过滤后-女"],
            "datasets": [
                {
                    "label": "人数",
                    "data": [60, 80],
                    "backgroundColor": ["rgba(75,192,192,0.6)", "rgba(255,99,132,0.6)"]
                }
            ]
        }
    else:
        data = {
            "labels": ["男", "女"],
            "datasets": [
                {
                    "label": "人数",
                    "data": [120, 130],
                    "backgroundColor": ["rgba(75,192,192,0.6)", "rgba(255,99,132,0.6)"]
                }
            ]
        }
    return jsonify(data)
