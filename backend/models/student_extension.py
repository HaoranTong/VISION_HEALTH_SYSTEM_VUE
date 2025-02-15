#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: student_extension.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\models\student_extension.py
功能介绍:
    定义学生扩展信息表模型，用于存储《近视预防干预系统需求文档_v1.3》中第四部分完整数据字段表中不属于学生基本信息的扩展字段。
    本模型存储的字段包括：
      - 从电子表格导入的扩展字段：区域、饮食偏好、运动偏好、健康教育、矫正方式、
        右眼-角膜曲率K1、左眼-角膜曲率K1、右眼-角膜曲率K2、左眼-角膜曲率K2、
        右眼-眼轴、左眼-眼轴、
        右眼屈光-球镜、右眼屈光-柱镜、右眼屈光-轴位、左眼屈光-球镜、左眼屈光-柱镜、左眼屈光-轴位，
        右眼散瞳-球镜、右眼散瞳-柱镜、右眼散瞳-轴位、左眼散瞳-球镜、左眼散瞳-柱镜、左眼散瞳-轴位，
        右眼-前房深度、左眼-前房深度，
        其他情况、眼疲劳状况，
        右眼散瞳-干预-球镜、右眼散瞳-干预-柱镜、右眼散瞳-干预-轴位、左眼散瞳-干预-球镜、左眼散瞳-干预-柱镜、左眼散瞳-干预-轴位，
      - 干预时间记录：第1次干预 至 第16次干预（记录各次干预的日期时间），
      - 系统根据导入数据计算得到的新增字段（例如【新增】干预后视力等级、左眼裸眼视力变化、右眼裸眼视力变化、
        左眼屈光-球镜变化、右眼屈光-球镜变化、左眼屈光-柱镜变化、右眼屈光-柱镜变化、
        左眼视力干预效果、右眼视力干预效果、左眼球镜干预效果、右眼球镜干预效果、左眼柱镜干预效果、右眼柱镜干预效果）。
    同时，通过 student_id 与 Student 表建立一对一关系。
"""
from backend.infrastructure.database import db
import warnings
warnings.filterwarnings("ignore")


class StudentExtension(db.Model):
    __tablename__ = "student_extensions"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.id'), nullable=False, unique=True)

    # 扩展字段直接从电子表格导入的数据
    region = db.Column(db.String(50))  # 区域
    diet_preference = db.Column(db.String(100))  # 饮食偏好
    exercise_preference = db.Column(db.String(100))  # 运动偏好
    health_education = db.Column(db.String(100))  # 健康教育
    correction_method = db.Column(db.String(50))  # 矫正方式

    right_keratometry_K1 = db.Column(db.Float)  # 右眼-角膜曲率K1
    left_keratometry_K1 = db.Column(db.Float)   # 左眼-角膜曲率K1
    right_keratometry_K2 = db.Column(db.Float)  # 右眼-角膜曲率K2
    left_keratometry_K2 = db.Column(db.Float)   # 左眼-角膜曲率K2

    right_axial_length = db.Column(db.Float)    # 右眼-眼轴
    left_axial_length = db.Column(db.Float)     # 左眼-眼轴

    right_sphere = db.Column(db.Float)  # 右眼屈光-球镜
    right_cylinder = db.Column(db.Float)  # 右眼屈光-柱镜
    right_axis = db.Column(db.Float)      # 右眼屈光-轴位

    left_sphere = db.Column(db.Float)   # 左眼屈光-球镜
    left_cylinder = db.Column(db.Float)  # 左眼屈光-柱镜
    left_axis = db.Column(db.Float)     # 左眼屈光-轴位

    right_dilation_sphere = db.Column(db.Float)  # 右眼散瞳-球镜
    right_dilation_cylinder = db.Column(db.Float)  # 右眼散瞳-柱镜
    right_dilation_axis = db.Column(db.Float)      # 右眼散瞳-轴位

    left_dilation_sphere = db.Column(db.Float)   # 左眼散瞳-球镜
    left_dilation_cylinder = db.Column(db.Float)   # 左眼散瞳-柱镜
    left_dilation_axis = db.Column(db.Float)       # 左眼散瞳-轴位

    right_anterior_chamber = db.Column(db.Float)  # 右眼-前房深度
    left_anterior_chamber = db.Column(db.Float)   # 左眼-前房深度

    other_remarks = db.Column(db.String(200))  # 其他情况
    eye_fatigue = db.Column(db.String(100))      # 眼疲劳状况

    right_intervention_dilation_sphere = db.Column(db.Float)  # 右眼散瞳-干预-球镜
    right_intervention_dilation_cylinder = db.Column(db.Float)  # 右眼散瞳-干预-柱镜
    right_intervention_dilation_axis = db.Column(db.Float)      # 右眼散瞳-干预-轴位

    left_intervention_dilation_sphere = db.Column(db.Float)   # 左眼散瞳-干预-球镜
    left_intervention_dilation_cylinder = db.Column(db.Float)   # 左眼散瞳-干预-柱镜
    left_intervention_dilation_axis = db.Column(db.Float)       # 左眼散瞳-干预-轴位

    # 新增字段，由系统计算得到
    post_intervention_vision_level = db.Column(db.String(50))  # 干预后视力等级
    left_naked_vision_change = db.Column(db.Float)  # 左眼裸眼视力变化
    right_naked_vision_change = db.Column(db.Float)  # 右眼裸眼视力变化
    left_sphere_change = db.Column(db.Float)  # 左眼屈光-球镜变化
    right_sphere_change = db.Column(db.Float)  # 右眼屈光-球镜变化
    left_cylinder_change = db.Column(db.Float)  # 左眼屈光-柱镜变化
    right_cylinder_change = db.Column(db.Float)  # 右眼屈光-柱镜变化
    left_intervention_effect = db.Column(db.String(50))  # 左眼视力干预效果
    right_intervention_effect = db.Column(db.String(50))  # 右眼视力干预效果
    left_sphere_intervention_effect = db.Column(db.String(50))  # 左眼球镜干预效果
    right_sphere_intervention_effect = db.Column(db.String(50))  # 右眼球镜干预效果
    left_cylinder_intervention_effect = db.Column(db.String(50))  # 左眼柱镜干预效果
    right_cylinder_intervention_effect = db.Column(db.String(50))  # 右眼柱镜干预效果

    # 干预时间记录：记录第1次至第16次干预的日期时间
    intervention1 = db.Column(db.DateTime)
    intervention2 = db.Column(db.DateTime)
    intervention3 = db.Column(db.DateTime)
    intervention4 = db.Column(db.DateTime)
    intervention5 = db.Column(db.DateTime)
    intervention6 = db.Column(db.DateTime)
    intervention7 = db.Column(db.DateTime)
    intervention8 = db.Column(db.DateTime)
    intervention9 = db.Column(db.DateTime)
    intervention10 = db.Column(db.DateTime)
    intervention11 = db.Column(db.DateTime)
    intervention12 = db.Column(db.DateTime)
    intervention13 = db.Column(db.DateTime)
    intervention14 = db.Column(db.DateTime)
    intervention15 = db.Column(db.DateTime)
    intervention16 = db.Column(db.DateTime)

    # 建立与学生基本信息的关系（假设 Student 模型在 backend.models.student 中定义）
    student = db.relationship(
        'Student', backref=db.backref('extension', uselist=False))

    def __repr__(self):
        return f"<StudentExtension(student_id={self.student_id})>"
