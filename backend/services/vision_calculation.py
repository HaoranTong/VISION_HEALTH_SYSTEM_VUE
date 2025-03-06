#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: vision_calculation.py
完整存储路径: backend/services/vision_calculation.py
功能说明:
    该模块用于对学生视力数据进行统计计算，涵盖两大计算场景：
      1. 单记录内计算（同一年内计算）：
         针对单条 StudentExtension 记录，计算各项视力数据的变化值及效果标签，
         同时根据【屈光-球镜】数据及年龄判断干预前视力等级（vision_level）和干预后视力等级（interv_vision_level）。
         计算内容包括：
           - 裸眼视力变化（左右眼），变化公式：后 - 前；效果标签采用阈值0.1；
           - 球镜变化（左右眼），变化公式：后 - 前；效果标签采用阈值0.01；
           - 柱镜变化（左右眼），变化公式：后 - 前；效果标签采用阈值0.01；
           - 轴位变化（左右眼），变化公式：后 - 前；效果标签采用阈值1；
           - 干预前视力等级判断（vision_level）：基于右眼干预前球镜数据（right_sphere）、左眼干预前球镜数据（left_sphere，用于轻度判断）、年龄（age）以及右眼散瞳球镜数据（right_dilated_sphere）的判断规则如下：
                1. 假性近视：若 right_dilated_sphere 不缺失且等于 0，则判定为“假性近视”；
                2. 轻度近视：若 left_sphere 和 right_sphere 均 ≥ -3.00 且 ＜ -0.50，则判定为“轻度近视”；
                3. 中度近视：若 right_sphere ≥ -6.00 且 ＜ -3.00，则判定为“中度近视”；
                4. 临床前期近视：若不满足上述轻度和中度条件，并结合年龄判断：
                   - 如果 age 在 6 至 9 岁（含6与9），且 right_sphere ≤ 1.25，则判定为“临床前期近视”；
                   - 如果 age 在 10 至 12 岁（含10与12），且 right_sphere ≤ 0.75，则判定为“临床前期近视”；
                   - 否则判定为“正常”；
           - 干预后视力等级判断（interv_vision_level）：同上，但数据来源为干预后字段（right_sphere_interv、left_sphere_interv、right_dilated_sphere_interv）。
      2. 跨年度比较计算（实时计算，不更新数据库）：
         针对同一学生在两个不同数据年份的记录，实时计算各项指标（裸眼视力、球镜、柱镜、轴位）的跨年度变化值及效果标签。
         例如，跨年度左眼裸眼视力变化：公式为
            cross_left_naked_change = to_year_record.left_eye_naked_interv - from_year_record.left_eye_naked，
         并根据阈值 0.1 生成效果标签。
         
使用说明:
    本模块主要提供以下函数：
      - is_missing_value(value, category="default") -> bool  
            辅助函数，用于判断数据是否缺失（仅当值为 None 或 Pandas NaN 时返回 True；数值 0 为有效数据）。
      - determine_effect(change: float, type_: str) -> str  
            根据变化值和指标类型生成效果标签，返回 "上升"、"维持" 或 "下降"。
      - calculate_within_year_change(record: StudentExtension) -> dict  
            针对单条记录计算所有指定视力数据变化和效果标签，并进行视力等级判断（干预前与干预后）。
      - calculate_cross_year_change(student_id: int, from_year: str, to_year: str) -> dict  
            针对跨年度比较，实时计算同一学生在两个数据年份下各项指标的变化值及效果标签，不更新数据库。
    其他模块（如数据导入、查询、统计分析、手动重新计算等）可直接调用本模块函数实现统一计算逻辑。

备注:
    在计算过程中，如果任一需要参与计算的原始数据为空（None 或 NaN），则对应的计算结果及效果标签均返回 None。
    请确保数据录入时，相关字段（例如 age）完整；否则视力等级判断结果将返回 None。

"""

import datetime
import pandas as pd
from sqlalchemy.orm import aliased
from backend.infrastructure.database import db
from backend.models.student_extension import StudentExtension


def is_missing_value(value, category="default"):
    """
    判断给定值是否缺失。
    仅当值为 None 或 Pandas 的 NaN 时返回 True。
    注意：对于数值数据（如裸眼视力、球镜、柱镜数据等），0 是有效数据，不视为缺失。

    参数:
        value: 需要判断的值
        category (str): 分类标识（默认"defalut"），当前不对特定类别做特殊处理。

    返回:
        bool: True 如果值缺失，否则 False
    """
    return value is None or pd.isna(value)


def determine_effect(change, type_):
    """
    根据变化值和指标类型生成效果标签。

    参数:
        change (float): 计算得到的差值
        type_ (str): 指标类型，可为:
                     - "naked": 裸眼视力（阈值 0.1）
                     - "spherical": 球镜数据（阈值 0.01）
                     - "cylindrical": 柱镜数据（阈值 0.01）
                     - "axis": 轴位数据（阈值 1）

    返回:
        str: "上升"、"维持" 或 "下降"
    """
    if type_ == "naked":
        threshold = 0.1
    elif type_ in ("spherical", "cylindrical"):
        threshold = 0.01
    elif type_ == "axis":
        threshold = 1
    else:
        threshold = 0.1
    if change > threshold:
        return "上升"
    elif change < -threshold:
        return "下降"
    else:
        return "维持"


def calculate_within_year_change(record):
    """
    针对单条 StudentExtension 记录，计算视力数据的变化值及效果标签，
    并根据【屈光-球镜】数据及年龄判断干预前（vision_level）与干预后（interv_vision_level）视力等级。

    参与计算的字段及公式：
      1. 裸眼视力变化：
         - 左眼： left_naked_change = left_eye_naked_interv - left_eye_naked
           标签字段： left_interv_effect（阈值 0.1）
         - 右眼： right_naked_change = right_eye_naked_interv - right_eye_naked
           标签字段： right_interv_effect（阈值 0.1）
      2. 球镜变化：
         - 左眼： left_sphere_change = left_sphere_interv - left_sphere
           标签字段： left_sphere_effect（阈值 0.01）
         - 右眼： right_sphere_change = right_sphere_interv - right_sphere
           标签字段： right_sphere_effect（阈值 0.01）
      3. 柱镜变化：
         - 左眼： left_cylinder_change = left_cylinder_interv - left_cylinder
           标签字段： left_cylinder_effect（阈值 0.01）
         - 右眼： right_cylinder_change = right_cylinder_interv - right_cylinder
           标签字段： right_cylinder_effect（阈值 0.01）
      4. 轴位变化：
         - 左眼： left_axis_change = left_axis_interv - left_axis
           标签字段： left_axis_effect（阈值 1）
         - 右眼： right_axis_change = right_axis_interv - right_axis
           标签字段： right_axis_effect（阈值 1）
      5. 干预前视力等级判断（vision_level）：
         数据来源： right_sphere, left_sphere, age, right_dilated_sphere
         判断规则：
           - 若 right_dilated_sphere 不缺失且等于 0，则为“假性近视”
           - 轻度近视：当 left_sphere 和 right_sphere 均 ≥ -3.00 且 ＜ -0.50 时
           - 中度近视：若 right_sphere ≥ -6.00 且 ＜ -3.00
           - 临床前期近视：若不满足轻度或中度条件时，结合年龄判断：
               * 如果 age 在 6 至 9 岁（含6与9），且 right_sphere ≤ 1.25，则为“临床前期近视”
               * 如果 age 在 10 至 12 岁（含10与12），且 right_sphere ≤ 0.75，则为“临床前期近视”
           - 否则，判定为“正常”
         若参与判断的数据缺失，则结果为 None。
      6. 干预后视力等级判断（interv_vision_level）：
         同上，但数据来源为： right_sphere_interv, left_sphere_interv, age, right_dilated_sphere_interv

    返回:
      dict: 计算结果字典，键名与数据库字段名称对应。
    """
    results = {}

    # 裸眼视力变化计算 - 左眼
    if not is_missing_value(record.left_eye_naked, "naked") and not is_missing_value(record.left_eye_naked_interv, "naked"):
        change = record.left_eye_naked_interv - record.left_eye_naked
        results["left_naked_change"] = round(change, 2)
        results["left_interv_effect"] = determine_effect(change, "naked")
    else:
        results["left_naked_change"] = None
        results["left_interv_effect"] = None

    # 裸眼视力变化计算 - 右眼
    if not is_missing_value(record.right_eye_naked, "naked") and not is_missing_value(record.right_eye_naked_interv, "naked"):
        change = record.right_eye_naked_interv - record.right_eye_naked
        results["right_naked_change"] = round(change, 2)
        results["right_interv_effect"] = determine_effect(change, "naked")
    else:
        results["right_naked_change"] = None
        results["right_interv_effect"] = None

    # 球镜变化计算 - 左眼
    if not is_missing_value(record.left_sphere, "sphere") and not is_missing_value(record.left_sphere_interv, "sphere"):
        change = record.left_sphere_interv - record.left_sphere
        results["left_sphere_change"] = round(change, 2)
        results["left_sphere_effect"] = determine_effect(change, "spherical")
    else:
        results["left_sphere_change"] = None
        results["left_sphere_effect"] = None

    # 球镜变化计算 - 右眼
    if not is_missing_value(record.right_sphere, "sphere") and not is_missing_value(record.right_sphere_interv, "sphere"):
        change = record.right_sphere_interv - record.right_sphere
        results["right_sphere_change"] = round(change, 2)
        results["right_sphere_effect"] = determine_effect(change, "spherical")
    else:
        results["right_sphere_change"] = None
        results["right_sphere_effect"] = None

    # 柱镜变化计算 - 左眼
    if not is_missing_value(record.left_cylinder, "cylindrical") and not is_missing_value(record.left_cylinder_interv, "cylindrical"):
        change = record.left_cylinder_interv - record.left_cylinder
        results["left_cylinder_change"] = round(change, 2)
        results["left_cylinder_effect"] = determine_effect(
            change, "cylindrical")
    else:
        results["left_cylinder_change"] = None
        results["left_cylinder_effect"] = None

    # 柱镜变化计算 - 右眼
    if not is_missing_value(record.right_cylinder, "cylindrical") and not is_missing_value(record.right_cylinder_interv, "cylindrical"):
        change = record.right_cylinder_interv - record.right_cylinder
        results["right_cylinder_change"] = round(change, 2)
        results["right_cylinder_effect"] = determine_effect(
            change, "cylindrical")
    else:
        results["right_cylinder_change"] = None
        results["right_cylinder_effect"] = None

    # 轴位变化计算 - 左眼
    if not is_missing_value(record.left_axis, "axis") and not is_missing_value(record.left_axis_interv, "axis"):
        change = record.left_axis_interv - record.left_axis
        results["left_axis_change"] = round(change, 2)
        results["left_axis_effect"] = determine_effect(change, "axis")
    else:
        results["left_axis_change"] = None
        results["left_axis_effect"] = None

    # 轴位变化计算 - 右眼
    if not is_missing_value(record.right_axis, "axis") and not is_missing_value(record.right_axis_interv, "axis"):
        change = record.right_axis_interv - record.right_axis
        results["right_axis_change"] = round(change, 2)
        results["right_axis_effect"] = determine_effect(change, "axis")
    else:
        results["right_axis_change"] = None
        results["right_axis_effect"] = None

    # 干预前视力等级判断（vision_level）
    # 数据来源： right_sphere, left_sphere, age, right_dilated_sphere
    if (not is_missing_value(record.right_sphere, "sphere") and
        not is_missing_value(record.left_sphere, "sphere") and
            not is_missing_value(record.age)):
        # 假性近视判断：如果 right_dilated_sphere 不缺失且等于 0，则判定为“假性近视”
        if not is_missing_value(record.right_dilated_sphere) and record.right_dilated_sphere == 0:
            results["vision_level"] = "假性近视"
        # 轻度近视：左右眼同时满足： left_sphere 和 right_sphere 均 ≥ -3.00 且 ＜ -0.50
        elif record.left_sphere >= -3.00 and record.left_sphere < -0.50 and \
                record.right_sphere >= -3.00 and record.right_sphere < -0.50:
            results["vision_level"] = "轻度近视"
        # 中度近视：仅依据 right_sphere 判断： ≥ -6.00 且 ＜ -3.00
        elif record.right_sphere >= -6.00 and record.right_sphere < -3.00:
            results["vision_level"] = "中度近视"
        else:
            # 临床前期近视：仅在不满足轻度或中度条件下判断，结合年龄
            if record.age >= 6 and record.age <= 9:
                if record.right_sphere <= 1.25:
                    results["vision_level"] = "临床前期近视"
                else:
                    results["vision_level"] = "正常"
            elif record.age >= 10 and record.age <= 12:
                if record.right_sphere <= 0.75:
                    results["vision_level"] = "临床前期近视"
                else:
                    results["vision_level"] = "正常"
            else:
                results["vision_level"] = "正常"
    else:
        results["vision_level"] = None

    # 干预后视力等级判断（interv_vision_level）
    # 数据来源： right_sphere_interv, left_sphere_interv, age, right_dilated_sphere_interv
    if (not is_missing_value(record.right_sphere_interv, "sphere") and
        not is_missing_value(record.left_sphere_interv, "sphere") and
            not is_missing_value(record.age)):
        if not is_missing_value(record.right_dilated_sphere_interv) and record.right_dilated_sphere_interv == 0:
            results["interv_vision_level"] = "假性近视"
        elif record.left_sphere_interv >= -3.00 and record.left_sphere_interv < -0.50 and \
                record.right_sphere_interv >= -3.00 and record.right_sphere_interv < -0.50:
            results["interv_vision_level"] = "轻度近视"
        elif record.right_sphere_interv >= -6.00 and record.right_sphere_interv < -3.00:
            results["interv_vision_level"] = "中度近视"
        else:
            if record.age >= 6 and record.age <= 9:
                if record.right_sphere_interv <= 1.25:
                    results["interv_vision_level"] = "临床前期近视"
                else:
                    results["interv_vision_level"] = "正常"
            elif record.age >= 10 and record.age <= 12:
                if record.right_sphere_interv <= 0.75:
                    results["interv_vision_level"] = "临床前期近视"
                else:
                    results["interv_vision_level"] = "正常"
            else:
                results["interv_vision_level"] = "正常"
    else:
        results["interv_vision_level"] = None

    return results


def calculate_cross_year_change(student_id, from_year, to_year):
    """
    针对同一学生的跨年度数据进行计算，实时返回指定指标的跨年度变化及效果标签。

    实现方法：
      - 使用 SQLAlchemy 的 aliased() 为 StudentExtension 创建两个别名，分别对应 from_year 和 to_year 的记录。
      - 计算方法与单记录内计算类似，主要计算以下指标：
           * 跨年度裸眼视力变化：
                - 左眼： cross_left_naked_change = to_record.left_eye_naked_interv - from_record.left_eye_naked
                - 右眼： cross_right_naked_change = to_record.right_eye_naked_interv - from_record.right_eye_naked
           * 跨年度球镜变化：
                - 左眼： cross_left_sphere_change = to_record.left_sphere_interv - from_record.left_sphere
                - 右眼： cross_right_sphere_change = to_record.right_sphere_interv - from_record.right_sphere
           * 跨年度柱镜变化：
                - 左眼： cross_left_cylinder_change = to_record.left_cylinder_interv - from_record.left_cylinder
                - 右眼： cross_right_cylinder_change = to_record.right_cylinder_interv - from_record.right_cylinder
           * 跨年度轴位变化：
                - 左眼： cross_left_axis_change = to_record.left_axis_interv - from_record.left_axis
                - 右眼： cross_right_axis_change = to_record.right_axis_interv - from_record.right_axis
      - 对每项计算，若参与数据缺失则结果置为 None；否则计算差值并根据对应阈值生成效果标签。

    返回:
      dict: 包含各项跨年度计算结果及效果标签，键名示例：
            "cross_left_naked_change", "cross_left_naked_effect", "cross_right_sphere_change", 等
      若无对应记录，则返回空字典 {}。
    """
    results = {}
    try:
        ExtFrom = aliased(StudentExtension)
        ExtTo = aliased(StudentExtension)
        query = db.session.query(ExtFrom, ExtTo).filter(
            ExtFrom.student_id == student_id,
            ExtTo.student_id == student_id,
            ExtFrom.data_year == from_year,
            ExtTo.data_year == to_year
        )
        record_pair = query.first()
        if record_pair is None:
            return {}

        ext_from, ext_to = record_pair

        # 跨年度裸眼视力变化 - 左眼
        if (not is_missing_value(ext_from.left_eye_naked, "naked") and
                not is_missing_value(ext_to.left_eye_naked_interv, "naked")):
            change = ext_to.left_eye_naked_interv - ext_from.left_eye_naked
            results["cross_left_naked_change"] = round(change, 2)
            results["cross_left_naked_effect"] = determine_effect(
                change, "naked")
        else:
            results["cross_left_naked_change"] = None
            results["cross_left_naked_effect"] = None

        # 跨年度裸眼视力变化 - 右眼
        if (not is_missing_value(ext_from.right_eye_naked, "naked") and
                not is_missing_value(ext_to.right_eye_naked_interv, "naked")):
            change = ext_to.right_eye_naked_interv - ext_from.right_eye_naked
            results["cross_right_naked_change"] = round(change, 2)
            results["cross_right_naked_effect"] = determine_effect(
                change, "naked")
        else:
            results["cross_right_naked_change"] = None
            results["cross_right_naked_effect"] = None

        # 跨年度球镜变化 - 左眼
        if (not is_missing_value(ext_from.left_sphere, "sphere") and
                not is_missing_value(ext_to.left_sphere_interv, "sphere")):
            change = ext_to.left_sphere_interv - ext_from.left_sphere
            results["cross_left_sphere_change"] = round(change, 2)
            results["cross_left_sphere_effect"] = determine_effect(
                change, "spherical")
        else:
            results["cross_left_sphere_change"] = None
            results["cross_left_sphere_effect"] = None

        # 跨年度球镜变化 - 右眼
        if (not is_missing_value(ext_from.right_sphere, "sphere") and
                not is_missing_value(ext_to.right_sphere_interv, "sphere")):
            change = ext_to.right_sphere_interv - ext_from.right_sphere
            results["cross_right_sphere_change"] = round(change, 2)
            results["cross_right_sphere_effect"] = determine_effect(
                change, "spherical")
        else:
            results["cross_right_sphere_change"] = None
            results["cross_right_sphere_effect"] = None

        # 跨年度柱镜变化 - 左眼
        if (not is_missing_value(ext_from.left_cylinder, "cylindrical") and
                not is_missing_value(ext_to.left_cylinder_interv, "cylindrical")):
            change = ext_to.left_cylinder_interv - ext_from.left_cylinder
            results["cross_left_cylinder_change"] = round(change, 2)
            results["cross_left_cylinder_effect"] = determine_effect(
                change, "cylindrical")
        else:
            results["cross_left_cylinder_change"] = None
            results["cross_left_cylinder_effect"] = None

        # 跨年度柱镜变化 - 右眼
        if (not is_missing_value(ext_from.right_cylinder, "cylindrical") and
                not is_missing_value(ext_to.right_cylinder_interv, "cylindrical")):
            change = ext_to.right_cylinder_interv - ext_from.right_cylinder
            results["cross_right_cylinder_change"] = round(change, 2)
            results["cross_right_cylinder_effect"] = determine_effect(
                change, "cylindrical")
        else:
            results["cross_right_cylinder_change"] = None
            results["cross_right_cylinder_effect"] = None

        # 跨年度轴位变化 - 左眼
        if (not is_missing_value(ext_from.left_axis, "axis") and
                not is_missing_value(ext_to.left_axis_interv, "axis")):
            change = ext_to.left_axis_interv - ext_from.left_axis
            results["cross_left_axis_change"] = round(change, 2)
            results["cross_left_axis_effect"] = determine_effect(
                change, "axis")
        else:
            results["cross_left_axis_change"] = None
            results["cross_left_axis_effect"] = None

        # 跨年度轴位变化 - 右眼
        if (not is_missing_value(ext_from.right_axis, "axis") and
                not is_missing_value(ext_to.right_axis_interv, "axis")):
            change = ext_to.right_axis_interv - ext_from.right_axis
            results["cross_right_axis_change"] = round(change, 2)
            results["cross_right_axis_effect"] = determine_effect(
                change, "axis")
        else:
            results["cross_right_axis_change"] = None
            results["cross_right_axis_effect"] = None

    except Exception as e:
        print(f"Error in cross-year calculation: {e}")
        results = {}
    return results
