#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: student_extension.py
完整存储路径: backend/models/student_extension.py
功能说明:
    定义 StudentExtension 模型，用于存储学生扩展信息，包含随时间变化的数据字段，
    健康信息、视力数据、干预数据及计算字段。该模型支持同一学生在不同数据年份下拥有多条记录，
    但通过复合唯一约束，确保每个 student_id 与 data_year 的组合在数据库中只存在一条记录。
    新增字段包括【新增】视力等级、【新增】左眼/右眼屈光-轴位变化，以及【新增】左眼/右眼轴位干预效果，
    其他字段均严格按照数据字段映射表定义。
使用说明:
    通过 SQLAlchemy ORM 对学生扩展数据进行 CRUD 操作，各字段命名、数据类型和长度依据项目需求设计，
    并与数据导入、查询等模块保持一致。请在重建数据库时确保旧数据已清除，以便新结构正常生成。
"""

from datetime import datetime
from backend.infrastructure.database import db
from sqlalchemy import UniqueConstraint


class StudentExtension(db.Model):
    __tablename__ = "student_extensions"
    __table_args__ = (
        UniqueConstraint('student_id', 'data_year', name='uq_student_year'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        "students.id"), nullable=False, comment="关联的学生ID")
    data_year = db.Column(db.String(4), nullable=False, comment="数据年份")
    grade = db.Column(db.String(10), nullable=True, comment="学生年级（随数据年份变化）")
    height = db.Column(db.Float, nullable=True, comment="身高（单位：厘米）")
    weight = db.Column(db.Float, nullable=True, comment="体重（单位：公斤）")
    diet_preference = db.Column(db.String(50), nullable=True, comment="饮食偏好")
    exercise_preference = db.Column(
        db.String(50), nullable=True, comment="运动偏好")
    health_education = db.Column(
        db.String(200), nullable=True, comment="健康教育情况")
    past_history = db.Column(db.String(200), nullable=True, comment="既往史")
    family_history = db.Column(db.String(200), nullable=True, comment="家族史")
    premature = db.Column(db.String(10), nullable=True, comment="是否早产")
    allergy = db.Column(db.String(200), nullable=True, comment="过敏史")

    # 视力数据
    right_eye_naked = db.Column(db.Float, nullable=True, comment="右眼-裸眼视力")
    left_eye_naked = db.Column(db.Float, nullable=True, comment="左眼-裸眼视力")
    right_eye_corrected = db.Column(db.Float, nullable=True, comment="右眼-矫正视力")
    left_eye_corrected = db.Column(db.Float, nullable=True, comment="左眼-矫正视力")
    right_keratometry_K1 = db.Column(
        db.Float, nullable=True, comment="右眼-角膜曲率K1")
    left_keratometry_K1 = db.Column(
        db.Float, nullable=True, comment="左眼-角膜曲率K1")
    right_keratometry_K2 = db.Column(
        db.Float, nullable=True, comment="右眼-角膜曲率K2")
    left_keratometry_K2 = db.Column(
        db.Float, nullable=True, comment="左眼-角膜曲率K2")
    right_axial_length = db.Column(db.Float, nullable=True, comment="右眼-眼轴")
    left_axial_length = db.Column(db.Float, nullable=True, comment="左眼-眼轴")
    right_sphere = db.Column(db.Float, nullable=True, comment="右眼屈光-球镜")
    right_cylinder = db.Column(db.Float, nullable=True, comment="右眼屈光-柱镜")
    right_axis = db.Column(db.Float, nullable=True, comment="右眼屈光-轴位")
    left_sphere = db.Column(db.Float, nullable=True, comment="左眼屈光-球镜")
    left_cylinder = db.Column(db.Float, nullable=True, comment="左眼屈光-柱镜")
    left_axis = db.Column(db.Float, nullable=True, comment="左眼屈光-轴位")
    right_dilated_sphere = db.Column(
        db.Float, nullable=True, comment="右眼散瞳-球镜")
    right_dilated_cylinder = db.Column(
        db.Float, nullable=True, comment="右眼散瞳-柱镜")
    right_dilated_axis = db.Column(db.Float, nullable=True, comment="右眼散瞳-轴位")
    left_dilated_sphere = db.Column(db.Float, nullable=True, comment="左眼散瞳-球镜")
    left_dilated_cylinder = db.Column(
        db.Float, nullable=True, comment="左眼散瞳-柱镜")
    left_dilated_axis = db.Column(db.Float, nullable=True, comment="左眼散瞳-轴位")

    # 【新增】视力等级（根据分析模型判断基本视力等级）
    vision_level = db.Column(db.String(20), nullable=True, comment="【新增】视力等级")

    right_anterior_depth = db.Column(
        db.Float, nullable=True, comment="右眼-前房深度")
    left_anterior_depth = db.Column(db.Float, nullable=True, comment="左眼-前房深度")
    other_info = db.Column(db.String(200), nullable=True, comment="其他情况")
    eye_fatigue = db.Column(db.String(100), nullable=True, comment="眼疲劳状况")

    # 生活方式及治疗方法
    frame_glasses = db.Column(db.Boolean, nullable=True, comment="是否使用框架眼镜")
    contact_lenses = db.Column(db.Boolean, nullable=True, comment="是否使用隐形眼镜")
    night_orthokeratology = db.Column(
        db.Boolean, nullable=True, comment="是否使用夜戴角膜塑型镜")
    guasha = db.Column(db.Boolean, nullable=True, comment="是否进行刮痧治疗")
    aigiu = db.Column(db.Boolean, nullable=True, comment="是否进行艾灸治疗")
    zhongyao_xunzheng = db.Column(
        db.Boolean, nullable=True, comment="是否进行中药熏蒸")
    rejiu_training = db.Column(db.Boolean, nullable=True, comment="是否进行热灸训练")
    xuewei_tiefu = db.Column(db.Boolean, nullable=True, comment="是否进行穴位贴敷")
    reci_pulse = db.Column(db.Boolean, nullable=True, comment="是否使用热磁脉冲")
    baoguan = db.Column(db.Boolean, nullable=True, comment="是否进行拔罐治疗")

    # 干预后数据（直接映射）
    right_eye_naked_interv = db.Column(
        db.Float, nullable=True, comment="右眼-干预-裸眼视力")
    left_eye_naked_interv = db.Column(
        db.Float, nullable=True, comment="左眼-干预-裸眼视力")
    right_sphere_interv = db.Column(
        db.Float, nullable=True, comment="右眼屈光-干预-球镜")
    right_cylinder_interv = db.Column(
        db.Float, nullable=True, comment="右眼屈光-干预-柱镜")
    right_axis_interv = db.Column(
        db.Float, nullable=True, comment="右眼屈光-干预-轴位")
    left_sphere_interv = db.Column(
        db.Float, nullable=True, comment="左眼屈光-干预-球镜")
    left_cylinder_interv = db.Column(
        db.Float, nullable=True, comment="左眼屈光-干预-柱镜")
    left_axis_interv = db.Column(db.Float, nullable=True, comment="左眼屈光-干预-轴位")
    right_dilated_sphere_interv = db.Column(
        db.Float, nullable=True, comment="右眼散瞳-干预-球镜")
    right_dilated_cylinder_interv = db.Column(
        db.Float, nullable=True, comment="右眼散瞳-干预-柱镜")
    right_dilated_axis_interv = db.Column(
        db.Float, nullable=True, comment="右眼散瞳-干预-轴位")
    left_dilated_sphere_interv = db.Column(
        db.Float, nullable=True, comment="左眼散瞳-干预-球镜")
    left_dilated_cylinder_interv = db.Column(
        db.Float, nullable=True, comment="左眼散瞳-干预-柱镜")
    left_dilated_axis_interv = db.Column(
        db.Float, nullable=True, comment="左眼散瞳-干预-轴位")

    # 干预计算字段
    interv_vision_level = db.Column(
        db.String(20), nullable=True, comment="【新增】干预后视力等级")
    left_naked_change = db.Column(
        db.Float, nullable=True, comment="【新增】左眼裸眼视力变化")
    right_naked_change = db.Column(
        db.Float, nullable=True, comment="【新增】右眼裸眼视力变化")
    left_sphere_change = db.Column(
        db.Float, nullable=True, comment="【新增】左眼屈光-球镜变化")
    right_sphere_change = db.Column(
        db.Float, nullable=True, comment="【新增】右眼屈光-球镜变化")
    left_cylinder_change = db.Column(
        db.Float, nullable=True, comment="【新增】左眼屈光-柱镜变化")
    right_cylinder_change = db.Column(
        db.Float, nullable=True, comment="【新增】右眼屈光-柱镜变化")
    left_axis_change = db.Column(
        db.Float, nullable=True, comment="【新增】左眼屈光-轴位变化")
    right_axis_change = db.Column(
        db.Float, nullable=True, comment="【新增】右眼屈光-轴位变化")

    left_interv_effect = db.Column(
        db.String(20), nullable=True, comment="【新增】左眼视力干预效果")
    right_interv_effect = db.Column(
        db.String(20), nullable=True, comment="【新增】右眼视力干预效果")
    left_sphere_effect = db.Column(
        db.String(20), nullable=True, comment="【新增】左眼球镜干预效果")
    right_sphere_effect = db.Column(
        db.String(20), nullable=True, comment="【新增】右眼球镜干预效果")
    left_cylinder_effect = db.Column(
        db.String(20), nullable=True, comment="【新增】左眼柱镜干预效果")
    right_cylinder_effect = db.Column(
        db.String(20), nullable=True, comment="【新增】右眼柱镜干预效果")
    left_axis_effect = db.Column(
        db.String(20), nullable=True, comment="【新增】左眼轴位干预效果")
    right_axis_effect = db.Column(
        db.String(20), nullable=True, comment="【新增】右眼轴位干预效果")

    # 干预时间记录（共16次）
    interv1 = db.Column(db.DateTime, nullable=True, comment="第1次干预时间")
    interv2 = db.Column(db.DateTime, nullable=True, comment="第2次干预时间")
    interv3 = db.Column(db.DateTime, nullable=True, comment="第3次干预时间")
    interv4 = db.Column(db.DateTime, nullable=True, comment="第4次干预时间")
    interv5 = db.Column(db.DateTime, nullable=True, comment="第5次干预时间")
    interv6 = db.Column(db.DateTime, nullable=True, comment="第6次干预时间")
    interv7 = db.Column(db.DateTime, nullable=True, comment="第7次干预时间")
    interv8 = db.Column(db.DateTime, nullable=True, comment="第8次干预时间")
    interv9 = db.Column(db.DateTime, nullable=True, comment="第9次干预时间")
    interv10 = db.Column(db.DateTime, nullable=True, comment="第10次干预时间")
    interv11 = db.Column(db.DateTime, nullable=True, comment="第11次干预时间")
    interv12 = db.Column(db.DateTime, nullable=True, comment="第12次干预时间")
    interv13 = db.Column(db.DateTime, nullable=True, comment="第13次干预时间")
    interv14 = db.Column(db.DateTime, nullable=True, comment="第14次干预时间")
    interv15 = db.Column(db.DateTime, nullable=True, comment="第15次干预时间")
    interv16 = db.Column(db.DateTime, nullable=True, comment="第16次干预时间")

    def to_dict(self):
        """
        将模型转换为前端友好的字典格式，便于 JSON 序列化展示
        """
        return {
            "id": self.id,
            "student_id": self.student_id,
            "data_year": self.data_year,
            "grade": self.grade,
            "height": self.height,
            "weight": self.weight,
            "diet_preference": self.diet_preference,
            "exercise_preference": self.exercise_preference,
            "health_education": self.health_education,
            "past_history": self.past_history,
            "family_history": self.family_history,
            "premature": self.premature,
            "allergy": self.allergy,
            "right_eye_naked": self.right_eye_naked,
            "left_eye_naked": self.left_eye_naked,
            "right_eye_corrected": self.right_eye_corrected,
            "left_eye_corrected": self.left_eye_corrected,
            "right_keratometry_K1": self.right_keratometry_K1,
            "left_keratometry_K1": self.left_keratometry_K1,
            "right_keratometry_K2": self.right_keratometry_K2,
            "left_keratometry_K2": self.left_keratometry_K2,
            "right_axial_length": self.right_axial_length,
            "left_axial_length": self.left_axial_length,
            "right_sphere": self.right_sphere,
            "right_cylinder": self.right_cylinder,
            "right_axis": self.right_axis,
            "left_sphere": self.left_sphere,
            "left_cylinder": self.left_cylinder,
            "left_axis": self.left_axis,
            "right_dilated_sphere": self.right_dilated_sphere,
            "right_dilated_cylinder": self.right_dilated_cylinder,
            "right_dilated_axis": self.right_dilated_axis,
            "left_dilated_sphere": self.left_dilated_sphere,
            "left_dilated_cylinder": self.left_dilated_cylinder,
            "left_dilated_axis": self.left_dilated_axis,
            "vision_level": self.vision_level,
            "right_anterior_depth": self.right_anterior_depth,
            "left_anterior_depth": self.left_anterior_depth,
            "other_info": self.other_info,
            "eye_fatigue": self.eye_fatigue,
            "frame_glasses": self.frame_glasses,
            "contact_lenses": self.contact_lenses,
            "night_orthokeratology": self.night_orthokeratology,
            "guasha": self.guasha,
            "aigiu": self.aigiu,
            "zhongyao_xunzheng": self.zhongyao_xunzheng,
            "rejiu_training": self.rejiu_training,
            "xuewei_tiefu": self.xuewei_tiefu,
            "reci_pulse": self.reci_pulse,
            "baoguan": self.baoguan,
            "right_eye_naked_interv": self.right_eye_naked_interv,
            "left_eye_naked_interv": self.left_eye_naked_interv,
            "right_sphere_interv": self.right_sphere_interv,
            "right_cylinder_interv": self.right_cylinder_interv,
            "right_axis_interv": self.right_axis_interv,
            "left_sphere_interv": self.left_sphere_interv,
            "left_cylinder_interv": self.left_cylinder_interv,
            "left_axis_interv": self.left_axis_interv,
            "right_dilated_sphere_interv": self.right_dilated_sphere_interv,
            "right_dilated_cylinder_interv": self.right_dilated_cylinder_interv,
            "right_dilated_axis_interv": self.right_dilated_axis_interv,
            "left_dilated_sphere_interv": self.left_dilated_sphere_interv,
            "left_dilated_cylinder_interv": self.left_dilated_cylinder_interv,
            "left_dilated_axis_interv": self.left_dilated_axis_interv,
            "interv_vision_level": self.interv_vision_level,
            "left_naked_change": self.left_naked_change,
            "right_naked_change": self.right_naked_change,
            "left_sphere_change": self.left_sphere_change,
            "right_sphere_change": self.right_sphere_change,
            "left_cylinder_change": self.left_cylinder_change,
            "right_cylinder_change": self.right_cylinder_change,
            "left_axis_change": self.left_axis_change,
            "right_axis_change": self.right_axis_change,
            "left_interv_effect": self.left_interv_effect,
            "right_interv_effect": self.right_interv_effect,
            "left_sphere_effect": self.left_sphere_effect,
            "right_sphere_effect": self.right_sphere_effect,
            "left_cylinder_effect": self.left_cylinder_effect,
            "right_cylinder_effect": self.right_cylinder_effect,
            "left_axis_effect": self.left_axis_effect,
            "right_axis_effect": self.right_axis_effect,
            "interv1": self.interv1.isoformat() if self.interv1 else None,
            "interv2": self.interv2.isoformat() if self.interv2 else None,
            "interv3": self.interv3.isoformat() if self.interv3 else None,
            "interv4": self.interv4.isoformat() if self.interv4 else None,
            "interv5": self.interv5.isoformat() if self.interv5 else None,
            "interv6": self.interv6.isoformat() if self.interv6 else None,
            "interv7": self.interv7.isoformat() if self.interv7 else None,
            "interv8": self.interv8.isoformat() if self.interv8 else None,
            "interv9": self.interv9.isoformat() if self.interv9 else None,
            "interv10": self.interv10.isoformat() if self.interv10 else None,
            "interv11": self.interv11.isoformat() if self.interv11 else None,
            "interv12": self.interv12.isoformat() if self.interv12 else None,
            "interv13": self.interv13.isoformat() if self.interv13 else None,
            "interv14": self.interv14.isoformat() if self.interv14 else None,
            "interv15": self.interv15.isoformat() if self.interv15 else None,
            "interv16": self.interv16.isoformat() if self.interv16 else None
        }

    def _format_datetime(self, dt):
        """私有方法：统一处理时间格式"""
        return dt.isoformat() if dt else None

    def __repr__(self):
        return f"<StudentExtension {self.student_id} - {self.data_year}>"
