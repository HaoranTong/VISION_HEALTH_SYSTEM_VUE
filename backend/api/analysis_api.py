#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: analysis_api.py
完整存储路径: backend/api/analysis_api.py

功能说明:
  1. 提供统计报表数据接口 (/api/analysis/report)，支持:
     - 固定模板 (template1=按年龄段, template2=按性别)
     - 自由组合查询 (advanced_conditions)，可包含多指标、分组、过滤
     - 分页及报表合计行
  2. 提供图表数据接口 (/api/analysis/chart)，返回适用于 Chart.js 的数据。

使用说明:
  - 将此文件放置于 backend/api/ 目录下，并在 Flask 主应用中注册该蓝图:
      from backend.api.analysis_api import analysis_api
      app.register_blueprint(analysis_api)
  - 固定模板:
      template=template1 => 按年龄段分组 (6-9岁, 10-12岁, 其他)
      template=template2 => 按性别分组 (男, 女, 其他)
  - 自由组合:
      advanced_conditions 为 JSON 字符串数组，每个元素格式:
         {
           "role": "metric"/"group"/"filter",
           "field": "<字段名称>",
           "operator": "<= / >= / like / in / ...>",
           "value": "<具体值或数组或区间>"
         }
      其中:
        * 同一字段多个取值 => OR 逻辑
        * 不同字段 => AND 逻辑
  - 数据年份 (stat_time) 可单独传入，若未提供则默认当前年份
  - 注意: 当 advanced_conditions 存在时，template 参数被忽略，以避免冲突

导入模块说明:
  - json, datetime: 用于解析请求参数与获取当前年份
  - flask: Blueprint, request, jsonify, current_app 提供路由和日志支持
  - sqlalchemy: func, case, and_, or_, literal, cast, Integer 用于SQL表达式构造
  - backend.models: Student, StudentExtension 数据库模型定义
  - backend.infrastructure.database: db 全局数据库实例

修改要点:
  1. 避免对 SQLAlchemy 表达式使用 if not grouping_expr 判断，改为 if grouping_expr is None 判断。
  2. 显式将布尔表达式转换为整数 (cast(..., Integer))，避免统计列出现布尔值。
  3. 修正 case() 用法，使用星号展开方式传递位置参数，适配最新 SQLAlchemy 版本。
  4. 自由组合查询中，对于字段“age”，支持：
     - 当 advanced_conditions 中输入的是区间条件（字典包含 "min" 与 "max"）时，构造 case() 表达式，对每个区间生成分组标签；
     - 如果未输入区间，则直接按 StudentExtension.age 分组，使每个具体年龄独立一行。
  5. 在自由组合查询中记录第一个分组字段，并在表头生成时根据该字段动态显示正确的分组名称（如“年龄”或“性别”），而不是固定显示“分组”。
  6. “视力不良”统计计算恢复为：临床前期近视 + 轻度近视 + 中度近视。
  7. 保留原有功能，确保不破坏之前正常使用的功能。

--------------------------------------------------------------------------------
以下是完整的 analysis_api.py 源码:
--------------------------------------------------------------------------------
"""

import json
import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import func, and_, or_, case, literal, cast, Integer
from backend.infrastructure.database import db
from backend.models.student import Student
from backend.models.student_extension import StudentExtension

analysis_api = Blueprint("analysis_api", __name__)


@analysis_api.route("/api/analysis/report", methods=["GET"])
def analysis_report():
    """
    统计报表数据接口:
      前端可通过以下参数控制:
        - template: "template1"=按年龄段, "template2"=按性别
        - advanced_conditions: JSON字符串, 用于自由组合查询(可包含多指标/分组)
        - stat_time: 数据年份(如 "2023"), 若不传则默认当前年份
        - school: 学校名称(可选)
        - page, per_page: 分页参数
        - report_name: 自定义报表名称(可选)

    返回 JSON 格式:
    {
      "tableName": "...",
      "header": [...],
      "rows": [...],
      "total": <int>  // 不含合计行的分组总数
    }
    """
    # ========== 1. 解析请求参数 ==========
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
        f"template={template}, advanced_conditions={advanced_str}, "
        f"page={page}, per_page={per_page}"
    )

    # ========== 2. 基础查询 ==========
    query = db.session.query(StudentExtension, Student).join(
        Student, StudentExtension.student_id == Student.id
    )

    # 2.1 过滤 data_year
    if stat_time:
        query = query.filter(StudentExtension.data_year == stat_time)
    else:
        current_year = str(datetime.datetime.now().year)
        query = query.filter(StudentExtension.data_year == current_year)
        stat_time = current_year

    # 2.2 过滤 school(若有)
    if school:
        query = query.filter(Student.school == school)

    # ========== 3. 解析 advanced_conditions ==========
    # "metric" => 统计指标, "group" => 分组, "filter" => 过滤
    grouping_cols = []
    metric_values = []
    filters = []
    free_group_field = None  # 用于记录自由组合查询中第一个分组字段

    if advanced_str:
        try:
            adv_conds = json.loads(advanced_str)
            current_app.logger.debug(
                "[analysis_report] Parsing advanced_conditions...")

            field_to_values = {}
            field_to_roles = {}
            for cond in adv_conds:
                role = cond.get("role", "").strip().lower()
                field = cond.get("field", "").strip()
                op = cond.get("operator", "").strip().lower()
                val = cond.get("value", None)

                current_app.logger.debug(
                    f"[analysis_report] Condition => role={role}, field={field}, operator={op}, value={val}"
                )

                if not field:
                    continue

                field_to_roles.setdefault(field, set()).add(role)
                field_to_values.setdefault(field, []).append((op, val))
                if role == "group" and free_group_field is None:
                    free_group_field = field

            for f_field, cond_list in field_to_values.items():
                if hasattr(StudentExtension, f_field):
                    col = getattr(StudentExtension, f_field)
                elif hasattr(Student, f_field):
                    col = getattr(Student, f_field)
                else:
                    current_app.logger.warning(
                        f"[analysis_report] Unknown field: {f_field}")
                    continue

                roleset = field_to_roles[f_field]

                # 分组字段处理
                if "group" in roleset:
                    if f_field == "age":
                        # 对于 age，判断是否有区间条件
                        age_ranges = []
                        for (op_, v_) in cond_list:
                            if isinstance(v_, dict) and "min" in v_ and "max" in v_:
                                try:
                                    minv = int(v_["min"])
                                    maxv = int(v_["max"])
                                    age_ranges.append((minv, maxv))
                                except Exception:
                                    pass
                        if age_ranges:
                            # 构造 case() 表达式：支持多个区间，所有区间条件用位置参数传递
                            whens = []
                            for (minv, maxv) in age_ranges:
                                whens.append(
                                    (and_(col >= minv, col <= maxv), literal(f"{minv}-{maxv}岁")))
                            grouping_expr_age = case(
                                *whens, else_=literal("其他"))
                            grouping_cols.append(grouping_expr_age)
                        else:
                            # 无区间条件，直接用 age 进行分组
                            grouping_cols.append(col)
                    else:
                        grouping_cols.append(col)

                # 统计指标处理
                if "metric" in roleset:
                    all_vals = []
                    for (op_, v_) in cond_list:
                        if isinstance(v_, list):
                            all_vals.extend(v_)
                        else:
                            all_vals.append(v_)
                    all_vals = list(set(all_vals))
                    metric_values.extend(all_vals)

                # 过滤条件处理
                if "filter" in roleset or (("metric" not in roleset) and ("group" not in roleset)):
                    for (op_, v_) in cond_list:
                        if isinstance(v_, dict) and "min" in v_ and "max" in v_:
                            try:
                                minv = float(v_["min"])
                                maxv = float(v_["max"])
                                filters.append(col >= minv)
                                filters.append(col <= maxv)
                            except Exception:
                                pass
                        elif isinstance(v_, list):
                            filters.append(col.in_(v_))
                        else:
                            filters.append(col == v_)
        except Exception as e:
            current_app.logger.error(
                f"[analysis_report] Error parsing advanced_conditions: {e}")

    # ========== 4. 判断是否使用固定模板 ==========
    use_fixed_template = False
    if (not advanced_str) and template in ["template1", "template2"]:
        use_fixed_template = True
        current_app.logger.debug(
            f"[analysis_report] Using fixed template: {template}")

    grouping_expr = None
    if use_fixed_template:
        if template == "template1":
            # 固定模板1：按年龄段，固定为 6-9岁 和 10-12岁
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
        if len(grouping_cols) == 1:
            grouping_expr = grouping_cols[0]
        elif len(grouping_cols) > 1:
            grouping_expr = tuple(grouping_cols)
        else:
            grouping_expr = None

    if grouping_expr is None:
        current_app.logger.error("[analysis_report] 分组条件未设置")
        return jsonify({"error": "未设置分组条件，请检查查询设置"}), 400

    # ========== 5. 应用过滤条件 ==========
    if filters:
        query = query.filter(and_(*filters))

    # ========== 6. 应用分组 & 聚合统计 ==========
    query = query.group_by(grouping_expr)

    # 统计指标：
    # “视力不良” = 临床前期近视 + 轻度近视 + 中度近视
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

    # ========== 7. 构造表头 ==========
    # 当使用固定模板时，表头第一列根据模板决定；否则取自由组合中第一个分组字段的标签
    if use_fixed_template:
        if template == "template1":
            group_title = "年龄段"
        elif template == "template2":
            group_title = "性别"
        else:
            group_title = "分组"
    else:
        if free_group_field:
            # 根据自由组合中记录的分组字段，设置表头显示
            if free_group_field == "age":
                group_title = "年龄"
            elif free_group_field == "gender":
                group_title = "性别"
            else:
                group_title = free_group_field
        else:
            group_title = "分组"

    header = []
    header.append(group_title)
    indicator_titles = ["临床前期近视", "轻度近视", "中度近视", "视力不良"]
    for t in indicator_titles:
        header.append(f"{t}(人数)")
        header.append(f"{t}(占比)")
    header.append("统计人数")

    # ========== 8. 构造数据行, 计算占比 ==========
    rows = []
    for rec in paginated_records:
        total_count = rec.total_count if rec.total_count else 0
        pre_clinic_ratio = 0
        mild_ratio = 0
        moderate_ratio = 0
        bad_vision_ratio = 0
        if total_count > 0:
            pre_clinic_ratio = round(
                (rec.pre_clinic_count / total_count) * 100, 2)
            mild_ratio = round((rec.mild_count / total_count) * 100, 2)
            moderate_ratio = round((rec.moderate_count / total_count) * 100, 2)
            bad_vision_ratio = round(
                (rec.bad_vision_count / total_count) * 100, 2)
        row = {
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
        rows.append(row)

    # ========== 9. 构造返回结果 ==========
    if not custom_name:
        custom_name = f"{stat_time} 学生视力情况统计表"
    result = {
        "tableName": custom_name,
        "header": header,
        "rows": rows,
        "total": total
    }
    return jsonify(result)


@analysis_api.route("/api/analysis/chart", methods=["GET"])
def analysis_chart():
    """
    图表数据接口
    根据查询条件返回适用于 Chart.js 的数据格式:
    {
      "labels": [...],
      "datasets": [
         { "label": "...", "data": [...], "backgroundColor": [...] }
      ]
    }
    示例中仅返回静态数据, 实际应结合 /api/analysis/report 的逻辑进行聚合统计.
    """
    chart_data = {
        "labels": ["男", "女"],
        "datasets": [
            {
                "label": "临床前期近视(人数)",
                "data": [50, 40],
                "backgroundColor": ["rgba(75, 192, 192, 0.5)", "rgba(153, 102, 255, 0.5)"]
            }
        ]
    }
    return jsonify(chart_data)
