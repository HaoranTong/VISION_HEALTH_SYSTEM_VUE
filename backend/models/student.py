#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: student.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\models\student.py
功能说明:
    定义 Student 模型，用于存储学生的基本信息及部分扩展信息。
    字段与导入数据表列对应，主要字段包括：
      - education_id: 教育ID号（唯一，原 full_edu_id 改为 education_id）
      - school: 学校名称
      - school_code: 学校代码（后台录入或自动映射）
      - school_id: 学校ID（由系统管理员维护）
      - grade: 年级
      - class_name: 班级
      - name: 学生姓名
      - gender: 学生性别
      - age: 学生年龄
      - birthday: 出生日期
      - id_card: 身份证号码
      - phone: 联系电话
      - parent_name: 家长姓名
      - parent_phone: 家长电话
      - vision_left: 左眼裸眼视力
      - vision_right: 右眼裸眼视力
      - vision_left_corrected: 左眼矫正视力
      - vision_right_corrected: 右眼矫正视力
      - myopia_level: 近视等级
使用方法:
    使用 SQLAlchemy ORM 对学生数据进行 CRUD 操作。
"""

from backend.infrastructure.database import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    # 使用 education_id 替换原 full_edu_id
    education_id = db.Column(db.String(20), nullable=True, comment="教育ID号")
    school = db.Column(db.String(50), nullable=True, comment="学校名称")
    school_code = db.Column(db.String(10), nullable=True, comment="学校代码")
    school_id = db.Column(db.String(20), nullable=True,
                          comment="学校ID，由系统管理员维护")
    grade = db.Column(db.String(10), nullable=True, comment="年级")
    class_name = db.Column(db.String(10), nullable=True, comment="班级")
    name = db.Column(db.String(50), nullable=True, comment="学生姓名")
    gender = db.Column(db.String(10), nullable=True, comment="学生性别")
    age = db.Column(db.Integer, nullable=True, comment="学生年龄")
    birthday = db.Column(db.Date, nullable=True, comment="出生日期")
    id_card = db.Column(db.String(18), nullable=True, comment="身份证号码")
    phone = db.Column(db.String(15), nullable=True, comment="联系电话")
    parent_name = db.Column(db.String(50), nullable=True, comment="家长姓名")
    parent_phone = db.Column(db.String(15), nullable=True, comment="家长电话")
    vision_left = db.Column(db.Float, nullable=True, comment="左眼裸眼视力")
    vision_right = db.Column(db.Float, nullable=True, comment="右眼裸眼视力")
    vision_left_corrected = db.Column(
        db.Float, nullable=True, comment="左眼矫正视力")
    vision_right_corrected = db.Column(
        db.Float, nullable=True, comment="右眼矫正视力")
    myopia_level = db.Column(db.String(10), nullable=True, comment="近视等级")

    def to_dict(self):
        return {
            "id": self.id,
            "education_id": self.education_id,
            "school": self.school,
            "school_code": self.school_code,
            "school_id": self.school_id,
            "grade": self.grade,
            "class_name": self.class_name,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "id_card": self.id_card,
            "phone": self.phone,
            "parent_name": self.parent_name,
            "parent_phone": self.parent_phone,
            "vision_left": self.vision_left,
            "vision_right": self.vision_right,
            "vision_left_corrected": self.vision_left_corrected,
            "vision_right_corrected": self.vision_right_corrected,
            "myopia_level": self.myopia_level,
        }
