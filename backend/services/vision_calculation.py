#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: vision_calculation.py
完整存储路径: backend/services/vision_calculation.py
功能说明:
    该模块用于对学生视力数据进行统计计算，涵盖两大计算场景：
      1. 单记录内计算（同一年内计算）：
         针对单条 StudentExtension 记录，计算各项视力数据的变化值及效果标签，
         同时根据【屈光-球镜】数据及年龄判断干预前视力等级 (vision_level) 和干预后视力等级 (interv_vision_level)。
         计算内容包括：
           - 裸眼视力变化：
             * 左眼：left_naked_change = left_eye_naked_interv - left_eye_naked, 标签存入 left_interv_effect（阈值 0.1）
             * 右眼：right_naked_change = right_eye_naked_interv - right_eye_naked, 标签存入 right_interv_effect（阈值 0.1）
           - 球镜变化：
             * 左眼：left_sphere_change = left_sphere_interv - left_sphere, 标签存入 left_sphere_effect（阈值 0.01）
             * 右眼：right_sphere_change = right_sphere_interv - right_sphere, 标签存入 right_sphere_effect（阈值 0.01）
           - 柱镜变化：
             * 左眼：left_cylinder_change = left_cylinder_interv - left_cylinder, 标签存入 left_cylinder_effect（阈值 0.01）
             * 右眼：right_cylinder_change = right_cylinder_interv - right_cylinder, 标签存入 right_cylinder_effect（阈值 0.01）
           - 轴位变化：
             * 左眼：left_axis_change = left_axis_interv - left_axis, 标签存入 left_axis_effect（阈值 1）
             * 右眼：right_axis_change = right_axis_interv - right_axis, 标签存入 right_axis_effect（阈值 1）
           - 干预前视力等级判断（vision_level）：
             根据【屈光-球镜】数据及年龄判断，数据来源：
                * 右眼球镜：right_sphere
                * 左眼球镜：left_sphere（仅用于轻度判断）
                * 年龄：age
                * 右眼散瞳球镜：right_dilated_sphere
             判断规则：
                a. 若 right_dilated_sphere 存在且等于 0，则判定为“假性近视”
                b. 轻度近视：当 left_sphere 和 right_sphere 均 ≥ -3.00 且 ＜ -0.50 时
                c. 中度近视：当 right_sphere ≥ -6.00 且 ＜ -3.00 时
                d. 临床前期近视：在不满足轻度或中度条件下，结合年龄判断：
                   - 如果 age 在 6 至 9 岁（含6与9），且 right_sphere ≤ 1.25，则为“临床前期近视”
                   - 如果 age 在 10 至 12 岁（含10与12），且 right_sphere ≤ 0.75，则为“临床前期近视”
                e. 否则判定为“正常”
           - 干预后视力等级判断 (interv_vision_level)：
             同上，但数据来源为干预后字段：right_sphere_interv, left_sphere_interv, right_dilated_sphere_interv, age
      2. 跨年度比较计算（实时计算，不更新数据库）：
         针对同一学生在两个不同数据年份的记录，实时计算各项指标的跨年度变化值及效果标签，
         计算内容包括裸眼、球镜、柱镜、轴位的变化，公式均为：
           cross_XXX_change = to_year_record.XXX_interv - from_year_record.XXX
         并生成效果标签（同各自阈值，裸眼：0.1，球镜、柱镜：0.01，轴位：1）。
         返回的结果以字典形式提供，各项键名为：
           cross_left_naked_change, cross_left_naked_effect,
           cross_right_naked_change, cross_right_naked_effect,
           cross_left_sphere_change, cross_left_sphere_effect,
           cross_right_sphere_change, cross_right_sphere_effect,
           cross_left_cylinder_change, cross_left_cylinder_effect,
           cross_right_cylinder_change, cross_right_cylinder_effect,
           cross_left_axis_change, cross_left_axis_effect,
           cross_right_axis_change, cross_right_axis_effect.
使用说明:
    其他模块（如数据导入、查询、统计分析、手动重新计算）可直接调用本模块函数实现统一的视力数据计算逻辑。
备注:
    在计算过程中，若任一参与计算的原始数据为空（None 或 NaN），则对应的计算结果及效果标签返回 None，
    而不会将空值当作 0 处理。所有数值计算结果使用 round() 保留两位小数。
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
    注意：对于数值数据（例如裸眼视力、球镜、柱镜数据等），0 是有效数据，不视为缺失。

    参数:
        value: 需要判断的值
        category (str): 分类标识（默认 "default"）

    返回:
        bool: True 如果值缺失，否则 False
    """
    return value is None or pd.isna(value)


def determine_effect(change, type_):
    """
    根据变化值和指标类型生成效果标签。

    参数:
        change (float): 计算得到的差值
        type_ (str): 指标类型，可为：
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

    计算内容包括：
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
           - 若 right_dilated_sphere 存在且等于 0，则判定为“假性近视”
           - 轻度近视：当 left_sphere 和 right_sphere 均 ≥ -3.00 且 ＜ -0.50 时，判定为“轻度近视”
           - 中度近视：若 right_sphere ≥ -6.00 且 ＜ -3.00，则判定为“中度近视”
           - 临床前期近视：在不满足上述条件下，结合年龄判断：
               * 如果 age 在 6 至 9 岁（含6与9），且 right_sphere ≤ 1.25，则判定为“临床前期近视”
               * 如果 age 在 10 至 12 岁（含10与12），且 right_sphere ≤ 0.75，则判定为“临床前期近视”
               * 否则判定为“正常”
      6. 干预后视力等级判断（interv_vision_level）：
         同上，但数据来源为 right_sphere_interv, left_sphere_interv, age, right_dilated_sphere_interv

    对于每一项计算，如果任一原始数据缺失，则对应结果及标签设为 None。

    返回:
        dict: 包含所有计算结果和效果标签的字典，键名与数据库字段名称对应。
    """
    results = {}

    # 裸眼视力变化 - 左眼
    if not is_missing_value(record.left_eye_naked, "naked") and not is_missing_value(record.left_eye_naked_interv, "naked"):
        change = record.left_eye_naked_interv - record.left_eye_naked
        results["left_naked_change"] = round(change, 2)
        results["left_interv_effect"] = determine_effect(change, "naked")
    else:
        results["left_naked_change"] = None
        results["left_interv_effect"] = None

    # 裸眼视力变化 - 右眼
    if not is_missing_value(record.right_eye_naked, "naked") and not is_missing_value(record.right_eye_naked_interv, "naked"):
        change = record.right_eye_naked_interv - record.right_eye_naked
        results["right_naked_change"] = round(change, 2)
        results["right_interv_effect"] = determine_effect(change, "naked")
    else:
        results["right_naked_change"] = None
        results["right_interv_effect"] = None

    # 球镜变化 - 左眼
    if not is_missing_value(record.left_sphere, "sphere") and not is_missing_value(record.left_sphere_interv, "sphere"):
        change = record.left_sphere_interv - record.left_sphere
        results["left_sphere_change"] = round(change, 2)
        results["left_sphere_effect"] = determine_effect(change, "spherical")
    else:
        results["left_sphere_change"] = None
        results["left_sphere_effect"] = None

    # 球镜变化 - 右眼
    if not is_missing_value(record.right_sphere, "sphere") and not is_missing_value(record.right_sphere_interv, "sphere"):
        change = record.right_sphere_interv - record.right_sphere
        results["right_sphere_change"] = round(change, 2)
        results["right_sphere_effect"] = determine_effect(change, "spherical")
    else:
        results["right_sphere_change"] = None
        results["right_sphere_effect"] = None

    # 柱镜变化 - 左眼
    if not is_missing_value(record.left_cylinder, "cylindrical") and not is_missing_value(record.left_cylinder_interv, "cylindrical"):
        change = record.left_cylinder_interv - record.left_cylinder
        results["left_cylinder_change"] = round(change, 2)
        results["left_cylinder_effect"] = determine_effect(
            change, "cylindrical")
    else:
        results["left_cylinder_change"] = None
        results["left_cylinder_effect"] = None

    # 柱镜变化 - 右眼
    if not is_missing_value(record.right_cylinder, "cylindrical") and not is_missing_value(record.right_cylinder_interv, "cylindrical"):
        change = record.right_cylinder_interv - record.right_cylinder
        results["right_cylinder_change"] = round(change, 2)
        results["right_cylinder_effect"] = determine_effect(
            change, "cylindrical")
    else:
        results["right_cylinder_change"] = None
        results["right_cylinder_effect"] = None

    # 轴位变化 - 左眼
    if not is_missing_value(record.left_axis, "axis") and not is_missing_value(record.left_axis_interv, "axis"):
        change = record.left_axis_interv - record.left_axis
        results["left_axis_change"] = round(change, 2)
        results["left_axis_effect"] = determine_effect(change, "axis")
    else:
        results["left_axis_change"] = None
        results["left_axis_effect"] = None

    # 轴位变化 - 右眼
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
        # 假性近视：若 right_dilated_sphere 存在且等于 0，则判定为“假性近视”
        if not is_missing_value(record.right_dilated_sphere) and record.right_dilated_sphere == 0:
            results["vision_level"] = "假性近视"
        # 轻度近视：要求左右眼同时满足： left_sphere 和 right_sphere 均 ≥ -3.00 且 ＜ -0.50
        elif record.left_sphere >= -3.00 and record.left_sphere < -0.50 and \
                record.right_sphere >= -3.00 and record.right_sphere < -0.50:
            results["vision_level"] = "轻度近视"
        # 中度近视：仅依据 right_sphere 判断： ≥ -6.00 且 ＜ -3.00
        elif record.right_sphere >= -6.00 and record.right_sphere < -3.00:
            results["vision_level"] = "中度近视"
        else:
            # 临床前期近视：在不满足轻度或中度条件下，结合年龄判断
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
    针对同一学生在不同数据年份的记录，实时计算跨年度各项指标的变化值及效果标签，
    计算方法与单记录内计算类似，但数据分别取自 from_year 和 to_year 的记录。

    计算内容包括：
      1. 跨年度裸眼视力变化：
         - 左眼： cross_left_naked_change = to_year.left_eye_naked_interv - from_year.left_eye_naked
           标签字段： cross_left_naked_effect（阈值 0.1）
         - 右眼： cross_right_naked_change = to_year.right_eye_naked_interv - from_year.right_eye_naked
           标签字段： cross_right_naked_effect（阈值 0.1）
      2. 跨年度球镜变化：
         - 左眼： cross_left_sphere_change = to_year.left_sphere_interv - from_year.left_sphere
           标签字段： cross_left_sphere_effect（阈值 0.01）
         - 右眼： cross_right_sphere_change = to_year.right_sphere_interv - from_year.right_sphere
           标签字段： cross_right_sphere_effect（阈值 0.01）
      3. 跨年度柱镜变化：
         - 左眼： cross_left_cylinder_change = to_year.left_cylinder_interv - from_year.left_cylinder
           标签字段： cross_left_cylinder_effect（阈值 0.01）
         - 右眼： cross_right_cylinder_change = to_year.right_cylinder_interv - from_year.right_cylinder
           标签字段： cross_right_cylinder_effect（阈值 0.01）
      4. 跨年度轴位变化：
         - 左眼： cross_left_axis_change = to_year.left_axis_interv - from_year.left_axis
           标签字段： cross_left_axis_effect（阈值 1）
         - 右眼： cross_right_axis_change = to_year.right_axis_interv - from_year.right_axis
           标签字段： cross_right_axis_effect（阈值 1）

    如果任一所需数据缺失，则对应计算结果及标签返回 None。

    参数:
        student_id (int): 学生ID，对应 Student 表的主键。
        from_year (str): 起始数据年份。
        to_year (str): 目标数据年份。

    返回:
        dict: 包含所有跨年度计算结果及效果标签的字典。
              如：{
                      "cross_left_naked_change": -0.25,
                      "cross_left_naked_effect": "下降",
                      "cross_right_naked_change": 0.10,
                      "cross_right_naked_effect": "上升",
                      ... (其它指标)
                  }
              若没有对应记录，则返回空字典 {}。
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
        if not is_missing_value(ext_from.left_eye_naked, "naked") and not is_missing_value(ext_to.left_eye_naked_interv, "naked"):
            change = ext_to.left_eye_naked_interv - ext_from.left_eye_naked
            results["cross_left_naked_change"] = round(change, 2)
            results["cross_left_naked_effect"] = determine_effect(
                change, "naked")
        else:
            results["cross_left_naked_change"] = None
            results["cross_left_naked_effect"] = None

        # 跨年度裸眼视力变化 - 右眼
        if not is_missing_value(ext_from.right_eye_naked, "naked") and not is_missing_value(ext_to.right_eye_naked_interv, "naked"):
            change = ext_to.right_eye_naked_interv - ext_from.right_eye_naked
            results["cross_right_naked_change"] = round(change, 2)
            results["cross_right_naked_effect"] = determine_effect(
                change, "naked")
        else:
            results["cross_right_naked_change"] = None
            results["cross_right_naked_effect"] = None

        # 跨年度球镜变化 - 左眼
        if not is_missing_value(ext_from.left_sphere, "sphere") and not is_missing_value(ext_to.left_sphere_interv, "sphere"):
            change = ext_to.left_sphere_interv - ext_from.left_sphere
            results["cross_left_sphere_change"] = round(change, 2)
            results["cross_left_sphere_effect"] = determine_effect(
                change, "spherical")
        else:
            results["cross_left_sphere_change"] = None
            results["cross_left_sphere_effect"] = None

        # 跨年度球镜变化 - 右眼
        if not is_missing_value(ext_from.right_sphere, "sphere") and not is_missing_value(ext_to.right_sphere_interv, "sphere"):
            change = ext_to.right_sphere_interv - ext_from.right_sphere
            results["cross_right_sphere_change"] = round(change, 2)
            results["cross_right_sphere_effect"] = determine_effect(
                change, "spherical")
        else:
            results["cross_right_sphere_change"] = None
            results["cross_right_sphere_effect"] = None

        # 跨年度柱镜变化 - 左眼
        if not is_missing_value(ext_from.left_cylinder, "cylindrical") and not is_missing_value(ext_to.left_cylinder_interv, "cylindrical"):
            change = ext_to.left_cylinder_interv - ext_from.left_cylinder
            results["cross_left_cylinder_change"] = round(change, 2)
            results["cross_left_cylinder_effect"] = determine_effect(
                change, "cylindrical")
        else:
            results["cross_left_cylinder_change"] = None
            results["cross_left_cylinder_effect"] = None

        # 跨年度柱镜变化 - 右眼
        if not is_missing_value(ext_from.right_cylinder, "cylindrical") and not is_missing_value(ext_to.right_cylinder_interv, "cylindrical"):
            change = ext_to.right_cylinder_interv - ext_from.right_cylinder
            results["cross_right_cylinder_change"] = round(change, 2)
            results["cross_right_cylinder_effect"] = determine_effect(
                change, "cylindrical")
        else:
            results["cross_right_cylinder_change"] = None
            results["cross_right_cylinder_effect"] = None

        # 跨年度轴位变化 - 左眼
        if not is_missing_value(ext_from.left_axis, "axis") and not is_missing_value(ext_to.left_axis_interv, "axis"):
            change = ext_to.left_axis_interv - ext_from.left_axis
            results["cross_left_axis_change"] = round(change, 2)
            results["cross_left_axis_effect"] = determine_effect(
                change, "axis")
        else:
            results["cross_left_axis_change"] = None
            results["cross_left_axis_effect"] = None

        # 跨年度轴位变化 - 右眼
        if not is_missing_value(ext_from.right_axis, "axis") and not is_missing_value(ext_to.right_axis_interv, "axis"):
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
