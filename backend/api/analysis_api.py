#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: analysis_api.py
完整存储路径: backend/api/analysis_api.py
功能说明:
    统计分析模块的API接口，提供统计报表数据和图表数据。
    接收前端查询条件（包括固定模板及自由组合查询），
    基于 Student 与 StudentExtension 数据表进行多维度聚合统计计算，
    返回统计报表或图表所需的JSON数据。

    主要功能:
      1. /api/analysis/report
         - 根据模板(按年龄段/按性别)或自由组合查询条件做分组聚合，
           动态计算各项近视指标(临床前期近视、轻度近视、中度近视)及视力不良人数/占比，并附合计行。
      2. /api/analysis/chart
         - 返回适用于Chart.js的图表数据，示例按性别分组，统计某个指标人数。

使用说明:
    - 前端在 GET 参数中可传递:
       template, advanced_conditions, stat_time, school, page, per_page, report_name ...
    - 返回JSON格式，包括 tableName, header, rows, total(分页前总行数)。

导入模块说明:
    - json, datetime: 用于解析前端传递的 JSON 字符串、处理日期时间
    - flask: Blueprint, request, jsonify, current_app 用于注册路由、解析请求参数、输出 JSON、记录日志等
    - sqlalchemy: 用于构造数据库查询、进行聚合函数、条件组合等
    - db: SQLAlchemy 数据库会话对象
    - Student, StudentExtension: 学生及扩展信息模型类
    - func, and_, or_, case: SQLAlchemy 提供的聚合、逻辑运算及条件表达式构造函数

代码中主要函数:
    - analysis_report(): 处理报表查询的主接口
    - analysis_chart(): 处理图表数据查询接口

修改记录:
    - 修复了在判断 grouping_field 时的布尔判断问题，改为 “if grouping_field is None” 避免 “Boolean value of this clause is not defined” 错误。
    - 针对“case()”函数的新版本要求，修正了传入方式，避免 "ArgumentError: The 'whens' argument ..." 的错误。
    - 对自由组合查询中的“metric”条件进行了 OR 逻辑合并，对“group”条件支持多分组合并。
    - 在“年龄段”模板（template1）下，使用了 CASE WHEN + between() 将年龄归为“6-9岁”、“10-12岁”两类。
    - 确保对已有功能（按性别模板、自由组合其他字段）不造成破坏。
    - 解决了前端传入多次后仍报相同错误的问题，保持最小改动以维护已有功能。

注意:
    - 代码中包含详细注释，请勿随意删除或改动已验证的功能。
    - 若需再次修改，请谨慎评估对现有功能的影响，并在注释中标明。
    - 遵循PEP 8规范，保证整体可读性；保留原有功能逻辑，不破坏已正常运行的统计分析功能。
"""

import json
import datetime
from flask import Blueprint, request, jsonify, current_app
from backend.infrastructure.database import db
from backend.models.student import Student
from backend.models.student_extension import StudentExtension
from sqlalchemy import func, and_, or_, case

analysis_api = Blueprint("analysis_api", __name__)


@analysis_api.route("/api/analysis/report", methods=["GET"])
def analysis_report():
    """
    统计报表数据接口:
      前端可通过以下参数控制:
        - template: 固定模板(如 "template1"=按年龄段, "template2"=按性别)
        - advanced_conditions: JSON字符串, 用于自由组合查询
        - stat_time: 数据年份(字符串), 如 "2023"
        - school: 学校名称(可选)
        - page, per_page: 分页参数
        - report_name: 自定义报表名称(可选)

    返回 JSON 格式报表:
    {
      "tableName": "...",
      "header": [... 10列 ...],
      "rows": [...],
      "total": int(分组行数含合计)
    }
    """
    # 1. 解析请求参数
    template = request.args.get("template", "").strip()
    advanced_conditions_str = request.args.get(
        "advanced_conditions", "").strip()
    stat_time = request.args.get("stat_time", "").strip()
    school = request.args.get("school", "").strip()
    custom_report_name = request.args.get("report_name", "").strip()

    # 分页
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
        f"template={template}, advanced_conditions={advanced_conditions_str}, "
        f"page={page}, per_page={per_page}"
    )

    # 2. 基础查询: 联结 StudentExtension, Student
    query = db.session.query(StudentExtension, Student).join(
        Student, StudentExtension.student_id == Student.id
    )

    # 2.1 过滤数据年份: 若 stat_time 未指定，则默认使用当前年份
    if stat_time:
        query = query.filter(StudentExtension.data_year == stat_time)
    else:
        current_year_str = str(datetime.datetime.now().year)
        query = query.filter(StudentExtension.data_year == current_year_str)
        stat_time = current_year_str

    # 2.2 过滤学校(若有)
    if school:
        query = query.filter(Student.school == school)

    # 3. 解析 advanced_conditions
    #   需要将 role=metric 的同一字段条件 OR 合并, role=group 的同一字段值 OR 合并, 并记录要分组的字段
    #   不同字段之间依然是 AND 关系
    #   例如: metric: vision_level in [临床前期近视, 轻度近视], group: gender in [男, 女]
    #   => (vision_level in (...)) AND (gender in (...))
    #   其中 vision_level in (...) 通过 or_() 实现, gender in (...) 通过 or_() 实现
    #   grouping_fields 可能有多个(若用户选了多个role=group)
    #   metric_fields 可能有多个(若用户选了多个role=metric)
    #   额外的一般 filter (role=filter), 全部 AND
    grouping_fields = []  # 用于最终 group_by
    metric_conditions_map = {}
    group_conditions_map = {}
    filter_list = []

    if advanced_conditions_str:
        try:
            conditions = json.loads(advanced_conditions_str)
            current_app.logger.debug(
                "[analysis_report] Parsing advanced_conditions...")
            for cond in conditions:
                # metric/group/filter
                role = cond.get("role", "").strip().lower()
                field = cond.get("field", "").strip()
                operator = cond.get("operator", "").strip().lower()
                value = cond.get("value", None)

                current_app.logger.debug(
                    f"  Condition => role={role}, field={field}, operator={operator}, value={value}"
                )

                # 定位字段(可能在 StudentExtension 或 Student)
                col = None
                if hasattr(StudentExtension, field):
                    col = getattr(StudentExtension, field)
                elif hasattr(Student, field):
                    col = getattr(Student, field)
                else:
                    current_app.logger.warning(
                        f"[analysis_report] Unknown field: {field}, skip it."
                    )
                    continue

                # 处理 operator, 仅做最简化的 = / in / like
                # 当 operator="like" 并出现多个值时, 视为 in_
                # 当 value 为 list 时, 也视为 in_
                # 当 value 为 dict (例如 {min: x, max: y}), 需特殊处理(例如 age between)
                # role=metric => or_ 方式聚合; role=group => or_ 方式聚合; role=filter => 直接 AND

                if isinstance(value, dict):
                    # 可能是 number_range: { "min": "6", "max": "9" }
                    if 'min' in value and 'max' in value:
                        minv = value['min']
                        maxv = value['max']
                        # 转成数字
                        try:
                            min_int = int(minv)
                            max_int = int(maxv)
                            # 若 role=group 并且 field=age => 用户想把 6-9 岁作为一个分组
                            # 但最小改动: treat it as a filter => col between min_int, max_int
                            # 后续若要将 6-9 岁显示为一行 => 需配合 case() / else
                            # 这里只保留 filter => AND col.between(...) 语义
                            filter_list.append(col.between(min_int, max_int))
                        except ValueError:
                            current_app.logger.error(
                                f"Age range parse error: min={minv}, max={maxv}"
                            )
                            continue
                    else:
                        continue
                else:
                    # 不是 dict => str or list
                    if not isinstance(value, list):
                        value_list = [value]
                    else:
                        value_list = value

                    if role == "metric":
                        if field not in metric_conditions_map:
                            metric_conditions_map[field] = set()
                        for v in value_list:
                            metric_conditions_map[field].add(v)
                    elif role == "group":
                        if field not in group_conditions_map:
                            group_conditions_map[field] = set()
                        for v in value_list:
                            group_conditions_map[field].add(v)
                    else:
                        # 当做普通 filter => col in value_list
                        if operator in ("=", "like", "==", "in"):
                            filter_list.append(col.in_(value_list))
                        else:
                            # 其它情况暂不处理
                            filter_list.append(col.in_(value_list))
        except Exception as e:
            current_app.logger.error(
                f"[analysis_report] Error parsing advanced_conditions: {e}")

    # 4. 根据 template 来判断是否固定分组
    fixed_template = None
    if (not advanced_conditions_str) and (template in ["template1", "template2"]):
        fixed_template = template
        current_app.logger.debug(
            f"[analysis_report] Using fixed template: {fixed_template}")
    else:
        current_app.logger.debug(
            "[analysis_report] No fixed template selected; using free query mode.")

    # 4.1 若是固定模板 => grouping_field 不从 advanced_conditions，而是看 template
    grouping_field = None

    if fixed_template == "template1":
        # 按年龄段 => 使用 CASE WHEN => 6-9岁, 10-12岁, else '其他'
        # 注意 case(...) 的新写法: 以一组元组形式传入
        # from sqlalchemy import case
        # case((condition, value), (condition, value), ..., else_=...)
        grouping_field = case(
            (StudentExtension.age.between(6, 9), "6-9岁"),
            (StudentExtension.age.between(10, 12), "10-12岁"),
            else_="其他"
        ).label("row_name")

    elif fixed_template == "template2":
        # 按性别
        grouping_field = Student.gender.label("row_name")

    # 4.2 若无固定模板 => 看 group_conditions_map
    #     如果 group_conditions_map 为空 => 无分组 => 直接空(或后面做1行统计)
    #     如果 group_conditions_map 有多个字段 => 只取第一个
    if not fixed_template:
        # 先把 filter_list 里 AND 条件加到 query
        if filter_list:
            query = query.filter(and_(*filter_list))

        # 处理 metric_conditions_map => 需要 or_() 进行 in_ 过滤(同字段 => in_)
        # 不同字段 => each -> AND
        for m_field, m_values in metric_conditions_map.items():
            col = None
            if hasattr(StudentExtension, m_field):
                col = getattr(StudentExtension, m_field)
            elif hasattr(Student, m_field):
                col = getattr(Student, m_field)
            if col:
                query = query.filter(col.in_(m_values))

        # 处理 group_conditions_map => 只取第一个字段做 group
        if group_conditions_map:
            group_field_name = list(group_conditions_map.keys())[0]
            group_values = group_conditions_map[group_field_name]
            col = None
            if hasattr(StudentExtension, group_field_name):
                col = getattr(StudentExtension, group_field_name)
            elif hasattr(Student, group_field_name):
                col = getattr(Student, group_field_name)
            if col:
                grouping_field = col.label("row_name")
                # group_values => or => col in group_values
                query = query.filter(col.in_(list(group_values)))
            else:
                grouping_field = None

    # 5. 若最终 grouping_field is None => 说明没有分组 => 直接返回空 or 单行统计
    #    这里按之前逻辑 => 返回空
    if grouping_field is None:
        current_app.logger.debug(
            "[analysis_report] grouping_field is None => return empty result.")
        return jsonify({
            "tableName": "自由组合查询统计报表",
            "header": ["无数据"],
            "rows": [],
            "total": 0
        })

    # 6. 确保 filter_list 也生效在固定模板下
    #    之前只在“not fixed_template”里 apply filter_list
    #    现在补一下 => minimal approach => if fixed_template => also do filter
    #    避免固定模板时, user=2023+school=XX => missing
    if fixed_template:
        if filter_list:
            query = query.filter(and_(*filter_list))
        # 同时处理 metric_conditions_map
        for m_field, m_values in metric_conditions_map.items():
            col = None
            if hasattr(StudentExtension, m_field):
                col = getattr(StudentExtension, m_field)
            elif hasattr(Student, m_field):
                col = getattr(Student, m_field)
            if col:
                query = query.filter(col.in_(m_values))

    # 7. 构造统计 CASE WHEN + SUM => 统计临床前期近视、轻度近视、中度近视、视力不良、total
    #    如果 metric_conditions_map 里包含 "vision_level" => 用 vision_level
    #    否则 => 用 interv_vision_level
    used_level_field = "interv_vision_level"
    if "vision_level" in metric_conditions_map:
        used_level_field = "vision_level"

    level_col = getattr(StudentExtension, used_level_field)

    pre_clinic_case = func.sum(
        case(
            (level_col == "临床前期近视", 1),
            else_=0
        )
    ).label("pre_clinic_count")

    mild_case = func.sum(
        case(
            (level_col == "轻度近视", 1),
            else_=0
        )
    ).label("mild_count")

    moderate_case = func.sum(
        case(
            (level_col == "中度近视", 1),
            else_=0
        )
    ).label("moderate_count")

    bad_case = func.sum(
        case(
            (level_col.in_(["临床前期近视", "轻度近视", "中度近视"]), 1),
            else_=0
        )
    ).label("bad_vision_count")

    total_case = func.count(StudentExtension.id).label("total_count")

    # 8. 构造最终分组查询
    grouped_query = query.with_entities(
        grouping_field,  # row_name
        pre_clinic_case,
        mild_case,
        moderate_case,
        bad_case,
        total_case
    ).group_by(grouping_field)

    current_app.logger.debug(
        "[analysis_report] Executing aggregation query...")
    try:
        agg_results = grouped_query.all()
    except Exception as e:
        current_app.logger.error(
            f"[analysis_report] Query execution error: {e}")
        return jsonify({"error": f"查询错误: {str(e)}"}), 500

    current_app.logger.debug(
        f"[analysis_report] Aggregation returned {len(agg_results)} rows."
    )

    # 9. 整理并计算各占比
    rows = []
    for row in agg_results:
        row_name_val = row[0] if row[0] is not None else "未知"
        pre_cnt = row[1] or 0
        mild_cnt = row[2] or 0
        mod_cnt = row[3] or 0
        bad_cnt = row[4] or 0
        total_cnt = row[5] or 0

        def local_ratio(numer, denom):
            return round(numer * 100.0 / denom, 2) if denom else 0.0

        pre_ratio = local_ratio(pre_cnt, total_cnt)
        mild_ratio = local_ratio(mild_cnt, total_cnt)
        mod_ratio = local_ratio(mod_cnt, total_cnt)
        bad_ratio = local_ratio(bad_cnt, total_cnt)

        rows.append({
            "row_name": row_name_val,
            "pre_clinic_count": pre_cnt,
            "pre_clinic_ratio": pre_ratio,
            "mild_count": mild_cnt,
            "mild_ratio": mild_ratio,
            "moderate_count": mod_cnt,
            "moderate_ratio": mod_ratio,
            "bad_vision_count": bad_cnt,
            "bad_vision_ratio": bad_ratio,
            "total_count": total_cnt
        })

    # 合计行
    sum_pre = sum(r["pre_clinic_count"] for r in rows)
    sum_mild = sum(r["mild_count"] for r in rows)
    sum_mod = sum(r["moderate_count"] for r in rows)
    sum_bad = sum(r["bad_vision_count"] for r in rows)
    sum_total = sum(r["total_count"] for r in rows)

    def global_ratio(numer, denom):
        return round(numer * 100.0 / denom, 2) if denom else 0.0

    total_row = {
        "row_name": "合计",
        "pre_clinic_count": sum_pre,
        "pre_clinic_ratio": global_ratio(sum_pre, sum_total),
        "mild_count": sum_mild,
        "mild_ratio": global_ratio(sum_mild, sum_total),
        "moderate_count": sum_mod,
        "moderate_ratio": global_ratio(sum_mod, sum_total),
        "bad_vision_count": sum_bad,
        "bad_vision_ratio": global_ratio(sum_bad, sum_total),
        "total_count": sum_total
    }
    rows.append(total_row)
    total_rows = len(rows)

    # 10. 生成表格标题
    if template in ["template1", "template2"] and (not advanced_conditions_str):
        if template == "template1":
            default_title = f"{stat_time}-学生视力情况统计表-预防干预前(按年龄段)"
        else:
            default_title = f"{stat_time}-学生视力情况统计表-预防干预前(按性别)"
    else:
        default_title = "自由组合查询统计报表"

    report_title = custom_report_name if custom_report_name else default_title

    # 11. 构造响应
    response_data = {
        "tableName": report_title,
        "header": [
            "分组",
            "临床前期近视(人数)", "临床前期近视(占比)",
            "轻度近视(人数)",   "轻度近视(占比)",
            "中度近视(人数)",   "中度近视(占比)",
            "视力不良(人数)",   "视力不良(占比)",
            "统计人数"
        ],
        "rows": rows,
        "total": total_rows
    }

    current_app.logger.debug(
        f"[analysis_report] Final response: {response_data}")
    return jsonify(response_data)


@analysis_api.route("/api/analysis/chart", methods=["GET"])
def analysis_chart():
    """
    图表数据接口:
      - template: 固定模板(可选)
      - stat_time: 数据年份(字符串)
      - school: 学校(可选)
      - 返回适用于Chart.js的数据结构, 仅做示例按性别分组统计"临床前期近视"人数

    使用示例:
      GET /api/analysis/chart?stat_time=2023&template=template2
    """
    template = request.args.get("template", "").strip()
    stat_time = request.args.get("stat_time", "").strip()
    school = request.args.get("school", "").strip()
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        per_page = 10

    current_app.logger.debug(
        f"[analysis_chart] stat_time={stat_time}, school={school}, "
        f"template={template}, page={page}, per_page={per_page}"
    )

    # 基础查询
    query = db.session.query(StudentExtension, Student).join(
        Student, StudentExtension.student_id == Student.id
    )
    if stat_time:
        query = query.filter(StudentExtension.data_year == stat_time)
    else:
        cur_yr = str(datetime.datetime.now().year)
        query = query.filter(StudentExtension.data_year == cur_yr)
        stat_time = cur_yr
    if school:
        query = query.filter(Student.school == school)

    # 示例: 统计 "临床前期近视" in interv_vision_level, 按性别分组
    pre_clinic_case = func.sum(
        case(
            (StudentExtension.interv_vision_level == "临床前期近视", 1),
            else_=0
        )
    ).label("pre_clinic_count")

    grouped_query = query.with_entities(
        Student.gender.label("row_name"),
        pre_clinic_case
    ).group_by(Student.gender)

    agg_results = grouped_query.all()
    labels = []
    data_values = []
    for res in agg_results:
        row_name = res.row_name if res.row_name else "未知"
        pre_cnt = res.pre_clinic_count or 0
        labels.append(row_name)
        data_values.append(pre_cnt)

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "临床前期近视人数",
                "data": data_values,
                "backgroundColor": [
                    "rgba(75, 192, 192, 0.5)",
                    "rgba(153, 102, 255, 0.5)",
                    "rgba(255, 159, 64, 0.5)"
                ]
            }
        ]
    }
    return jsonify(chart_data)


if __name__ == '__main__':
    """
    若需独立运行测试，可执行 python analysis_api.py
    但在实际Flask应用中, 由 create_app() 注册此蓝图后再运行.
    """
    from waitress import serve
    import sys

    print("请在完整Flask应用中使用, 或自行临时测试.")
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            pass
    print(f"Starting analysis_api alone on port {port}...")
    serve(analysis_api, host="0.0.0.0", port=port)
