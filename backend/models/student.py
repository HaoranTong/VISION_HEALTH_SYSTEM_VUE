#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: student.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\models\student.py
功能介绍:
    定义 Student 模型，用于存储学生的基本信息及部分扩展信息。
    模型中包括从电子表格导入的字段和系统自动生成的索引字段，
    同时增加了性别、年龄、出生日期、身份证号码、联系电话、
    法定监护人姓名、法定监护人联系电话、年级、班级、矫正视力等扩展字段。
    提供 to_dict() 方法以将模型数据转换为字典格式，便于 JSON 序列化。
使用方法:
    通过 SQLAlchemy ORM 创建、查询学生数据，
    调用 to_dict() 方法获取字典数据。
"""
from datetime import date
from backend.infrastructure.database import db

# pylint: disable=no-member


class Student(db.Model):
    """学生模型，用于存储学生基本信息及扩展信息。"""
    __tablename__ = "students"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    full_edu_id = db.Column(db.String(20))  # 原始教育ID号，非唯一，由Excel导入
    school_code = db.Column(db.String(6), nullable=False)  # 学校代码
    school_id = db.Column(db.String(20))  # 由系统管理员维护的学校ID
    index_id = db.Column(db.String(40), unique=True)  # 唯一索引：学校ID + full_edu_id
    name = db.Column(db.String(50))  # 学生姓名
    gender = db.Column(db.String(10))  # 学生性别
    age = db.Column(db.Integer)  # 学生年龄
    birthday = db.Column(db.Date)  # 学生出生日期
    id_card = db.Column(db.String(18))  # 学生身份证号码
    phone = db.Column(db.String(15))  # 学生联系电话
    parent_name = db.Column(db.String(50))  # 法定监护人姓名
    parent_phone = db.Column(db.String(15))  # 法定监护人联系电话
    grade = db.Column(db.String(10))  # 学生年级
    class_name = db.Column(db.String(10))  # 班级名称
    vision_left = db.Column(db.Float, nullable=False)  # 左眼裸眼视力
    vision_right = db.Column(db.Float, nullable=False)  # 右眼裸眼视力
    vision_left_corrected = db.Column(db.Float)  # 左眼矫正视力
    vision_right_corrected = db.Column(db.Float)  # 右眼矫正视力
    myopia_level = db.Column(db.String(10))  # 自动计算的近视等级

    def to_dict(self):
        """
        将学生信息转换为字典格式，便于 JSON 序列化。
        Returns:
            dict: 包含学生所有字段的字典。
        """
        return {
            "id": self.id,
            "full_edu_id": self.full_edu_id,
            "school_code": self.school_code,
            "school_id": self.school_id,
            "index_id": self.index_id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "id_card": self.id_card,
            "phone": self.phone,
            "parent_name": self.parent_name,
            "parent_phone": self.parent_phone,
            "grade": self.grade,
            "class_name": self.class_name,
            "vision_left": self.vision_left,
            "vision_right": self.vision_right,
            "vision_left_corrected": self.vision_left_corrected,
            "vision_right_corrected": self.vision_right_corrected,
            "myopia_level": self.myopia_level,
        }
