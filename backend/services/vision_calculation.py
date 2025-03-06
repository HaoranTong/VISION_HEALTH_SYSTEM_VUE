#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: vision_calculation.py
完整存储路径: backend/services/vision_calculation.py
功能说明:
    该模块用于对学生视力数据进行统计计算，涵盖两大计算场景：
      1. 单记录内计算：
         针对单条 StudentExtension 记录，根据同一数据年份内的干预前后数据
         （如左眼裸眼视力与左眼干预裸眼视力、右眼裸眼视力与右眼干预裸眼视力，
         左眼/右眼球镜、柱镜、轴位数据）计算变化值，并根据预设阈值生成效果标签。
         此外，还根据【屈光-球镜】数据及年龄判断干预前视力等级（vision_level）
         和干预后视力等级（interv_vision_level），其中：
             - 轻度近视：左右眼球镜数据均满足 ≥ -3.00 且 ＜ -0.50
             - 中度近视：仅依据右眼球镜数据判断，条件： ≥ -6.00 且 ＜ -3.00
             - 临床前期近视：仅依据右眼球镜数据结合年龄判断，
               年龄6~9岁时，右眼球镜数据 ≤ 1.25；年龄10~12岁时，右眼球镜数据 ≤ 0.75
             - 假性近视：若散瞳检查后右眼球镜数据为 0，则判定为假性近视
         计算结果会直接更新到数据库对应字段中。
      2. 跨年度比较计算：
         当用户指定两个不同的数据年份时，通过 SQLAlchemy 自连接获取同一学生在不同年份的记录，
         实时计算各项指标的跨年度变化值及效果标签，计算结果直接返回，不更新数据库。

使用说明:
    主要提供以下函数：
      - is_missing(value) -> bool
           辅助函数，用于判断数据是否缺失（None 或 NaN）。
      - determine_effect(change: float, type_: str) -> str
           根据变化值和指标类型生成效果标签（"上升"、"维持" 或 "下降"）。
      - calculate_within_year_change(record: StudentExtension) -> dict
           针对单条记录进行各项计算，并返回一个字典，包含各计算结果和效果标签。
      - calculate_cross_year_change(student_id: int, from_year: str, to_year: str) -> dict
           针对跨年度比较计算，返回各项跨年度计算结果及效果标签（不更新数据库）。
其他模块（如数据导入、查询、统计分析）可直接调用本模块的函数。

备注:
    在计算过程中，如果任一需要计算的数据为空，则该计算结果及对应效果标签均设为 None，
    而不会将空值当作 0 处理，从而避免错误的计算结果。
"""

import datetime
from sqlalchemy.orm import aliased
from backend.infrastructure.database import db
from backend.models.student_extension import StudentExtension
import pandas as pd


def is_missing(value):
    """
    判断给定值是否缺失。
    同时考虑两种情况：
      - 值为 None
      - 值为 Pandas 的 NaN（使用 pd.isna 判断）
    返回:
      True 如果值缺失，否则 False
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
        threshold = 0.1  # 默认阈值

    if change > threshold:
        return "上升"
    elif change < -threshold:
        return "下降"
    else:
        return "维持"


def calculate_within_year_change(record):
    """
    针对单条 StudentExtension 记录，计算视力数据的变化值及效果标签，
    并根据【屈光-球镜】数据及年龄判断干预前和干预后视力等级。

    计算内容包括：
    1. 左眼裸眼视力变化：
         left_naked_change = left_eye_naked_interv - left_eye_naked
         效果标签：阈值 0.1，保存到 left_interv_effect
    2. 右眼裸眼视力变化：
         right_naked_change = right_eye_naked_interv - right_eye_naked
         效果标签：阈值 0.1，保存到 right_interv_effect
    3. 左眼球镜变化：
         left_sphere_change = left_sphere_interv - left_sphere
         效果标签：阈值 0.01，保存到 left_sphere_effect
    4. 右眼球镜变化：
         right_sphere_change = right_sphere_interv - right_sphere
         效果标签：阈值 0.01，保存到 right_sphere_effect
    5. 左眼柱镜变化：
         left_cylinder_change = left_cylinder_interv - left_cylinder
         效果标签：阈值 0.01，保存到 left_cylinder_effect
    6. 右眼柱镜变化：
         right_cylinder_change = right_cylinder_interv - right_cylinder
         效果标签：阈值 0.01，保存到 right_cylinder_effect
    7. 左眼轴位变化：
         left_axis_change = left_axis_interv - left_axis
         效果标签：阈值 1，保存到 left_axis_effect
    8. 右眼轴位变化：
         right_axis_change = right_axis_interv - right_axis
         效果标签：阈值 1，保存到 right_axis_effect
    9. 干预前视力等级判断（vision_level）：
         根据右眼干预前球镜数据 right_sphere、左眼干预前球镜数据 left_sphere 以及年龄（age）判断：
         - 假性近视：若 right_dilated_sphere == 0，则 "假性近视"
         - 轻度近视：若 left_sphere 和 right_sphere 均 ≥ -3.00 且 ＜ -0.50，则 "轻度近视"
         - 中度近视：若 right_sphere ≥ -6.00 且 ＜ -3.00，则 "中度近视"
         - 临床前期近视：若不满足上述条件，且：
             如果 age 在 6 至 9 岁（含6与9），且 right_sphere ≤ 1.25；
             如果 age 在 10 至 12 岁（含10与12），且 right_sphere ≤ 0.75；
             则 "临床前期近视"
         - 否则，"正常"或"未分级"
    10. 干预后视力等级判断（interv_vision_level）：
         同上，但使用干预后数据：right_sphere_interv、left_sphere_interv、right_dilated_sphere_interv 以及 age

    对于每一项计算，如果参与计算的任一原始数据缺失（使用 is_missing 判断），则对应结果和标签均设为 None。
    -这里隐藏一个问题，如果年龄数据缺失，会导致视力等级判断无法进行，因此在数据录入时应确保年龄数据完整。

    返回:
        dict: 包含所有计算结果和效果标签的字典，键名与数据库字段名称对应。
    """
    results = {}

    # 计算左眼裸眼视力变化
    if not is_missing(record.left_eye_naked) and not is_missing(record.left_eye_naked_interv):
        change = record.left_eye_naked_interv - record.left_eye_naked
        results["left_naked_change"] = round(change, 2)
        results["left_interv_effect"] = determine_effect(change, "naked")
    else:
        results["left_naked_change"] = None
        results["left_interv_effect"] = None

    # 计算右眼裸眼视力变化
    if not is_missing(record.right_eye_naked) and not is_missing(record.right_eye_naked_interv):
        change = record.right_eye_naked_interv - record.right_eye_naked
        results["right_naked_change"] = round(change, 2)
        results["right_interv_effect"] = determine_effect(change, "naked")
    else:
        results["right_naked_change"] = None
        results["right_interv_effect"] = None

    # 计算左眼球镜变化
    if not is_missing(record.left_sphere) and not is_missing(record.left_sphere_interv):
        change = record.left_sphere_interv - record.left_sphere
        results["left_sphere_change"] = round(change, 2)
        results["left_sphere_effect"] = determine_effect(change, "spherical")
    else:
        results["left_sphere_change"] = None
        results["left_sphere_effect"] = None

    # 计算右眼球镜变化
    if not is_missing(record.right_sphere) and not is_missing(record.right_sphere_interv):
        change = record.right_sphere_interv - record.right_sphere
        results["right_sphere_change"] = round(change, 2)
        results["right_sphere_effect"] = determine_effect(change, "spherical")
    else:
        results["right_sphere_change"] = None
        results["right_sphere_effect"] = None

    # 计算左眼柱镜变化
    if not is_missing(record.left_cylinder) and not is_missing(record.left_cylinder_interv):
        change = record.left_cylinder_interv - record.left_cylinder
        results["left_cylinder_change"] = round(change, 2)
        results["left_cylinder_effect"] = determine_effect(
            change, "cylindrical")
    else:
        results["left_cylinder_change"] = None
        results["left_cylinder_effect"] = None

    # 计算右眼柱镜变化
    if not is_missing(record.right_cylinder) and not is_missing(record.right_cylinder_interv):
        change = record.right_cylinder_interv - record.right_cylinder
        results["right_cylinder_change"] = round(change, 2)
        results["right_cylinder_effect"] = determine_effect(
            change, "cylindrical")
    else:
        results["right_cylinder_change"] = None
        results["right_cylinder_effect"] = None

    # 计算左眼轴位变化
    if not is_missing(record.left_axis) and not is_missing(record.left_axis_interv):
        change = record.left_axis_interv - record.left_axis
        results["left_axis_change"] = round(change, 2)
        results["left_axis_effect"] = determine_effect(change, "axis")
    else:
        results["left_axis_change"] = None
        results["left_axis_effect"] = None

    # 计算右眼轴位变化
    if not is_missing(record.right_axis) and not is_missing(record.right_axis_interv):
        change = record.right_axis_interv - record.right_axis
        results["right_axis_change"] = round(change, 2)
        results["right_axis_effect"] = determine_effect(change, "axis")
    else:
        results["right_axis_change"] = None
        results["right_axis_effect"] = None

    # 干预前视力等级判断（vision_level）
    # 数据来源：right_sphere, left_sphere, age, right_dilated_sphere
    if not is_missing(record.right_sphere) and not is_missing(record.left_sphere) and not is_missing(record.age):
        # 假性近视判断（优先级最高）：如果 right_dilated_sphere == 0，则为假性近视
        if not is_missing(record.right_dilated_sphere) and record.right_dilated_sphere == 0:
            results["vision_level"] = "假性近视"
        # 轻度近视：要求左右眼同时满足：left_sphere 和 right_sphere 均 ≥ -3.00 且 ＜ -0.50
        elif record.left_sphere >= -3.00 and record.left_sphere < -0.50 and \
                record.right_sphere >= -3.00 and record.right_sphere < -0.50:
            results["vision_level"] = "轻度近视"
        # 中度近视：仅依据 right_sphere 判断，条件： right_sphere ≥ -6.00 且 ＜ -3.00
        elif record.right_sphere >= -6.00 and record.right_sphere < -3.00:
            results["vision_level"] = "中度近视"
        # 临床前期近视：前提是不满足轻度或中度条件
        else:
            # 判断年龄段
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
    # 数据来源：right_sphere_interv, left_sphere_interv, age, right_dilated_sphere_interv
    if not is_missing(record.right_sphere_interv) and not is_missing(record.left_sphere_interv) and not is_missing(record.age):
        if not is_missing(record.right_dilated_sphere_interv) and record.right_dilated_sphere_interv == 0:
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
    针对同一学生的跨年度数据进行计算，实时返回指定指标的差值及效果标签。
    实现思路：
      - 使用 SQLAlchemy 的 aliased() 创建 StudentExtension 的两个别名 ExtFrom 和 ExtTo，
        分别对应 from_year 和 to_year 的记录。
      - 仅对存在的记录进行计算，计算方法与单记录内计算类似。

    例如：跨年度左眼裸眼视力变化：
         cross_left_naked_change = to_year_record.left_eye_naked_interv - from_year_record.left_eye_naked
         并生成效果标签（阈值 0.1）。

    返回:
        dict: 包含跨年度计算结果，如：
          {
            "cross_left_naked_change": -0.25,
            "cross_left_naked_effect": "下降"
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
        # 跨年度左眼裸眼视力变化计算
        if not is_missing(ext_from.left_eye_naked) and not is_missing(ext_to.left_eye_naked_interv):
            change = ext_to.left_eye_naked_interv - ext_from.left_eye_naked
            results["cross_left_naked_change"] = round(change, 2)
            results["cross_left_naked_effect"] = determine_effect(
                change, "naked")
        else:
            results["cross_left_naked_change"] = None
            results["cross_left_naked_effect"] = None

        # 可根据需要扩展其它指标计算，例如右眼裸眼、球镜、柱镜、轴位等
    except Exception as e:
        print(f"Error in cross-year calculation: {e}")
        results = {}
    return results
