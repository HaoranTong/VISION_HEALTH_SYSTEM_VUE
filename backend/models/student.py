#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: student.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\models\student.py
功能说明:
    定义 Student 模型，用于存储学生的基本信息（不随时间变化的数据字段）。
    保存字段包括：
      - education_id: 教育ID号（唯一标识，原始导入数据，不可重复）
      - school: 学校名称
      - class_name: 学生所在班级
      - name: 学生姓名
      - gender: 学生性别（男/女）
      - birthday: 出生日期（格式：YYYY-MM-DD）
      - phone: 学生联系电话
      - id_card: 身份证号码
      - region: 学生所在区域/行政区划
      - contact_address: 学生详细联系地址
      - parent_name: 法定监护人姓名
      - parent_phone: 法定监护人联系电话
使用方法:
    使用 SQLAlchemy ORM 对学生数据进行 CRUD 操作。
"""

from backend.infrastructure.database import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    # 基本信息字段（不随时间变化）
    education_id = db.Column(db.String(20), nullable=True, comment="教育ID号")
    school = db.Column(db.String(50), nullable=True, comment="学校名称")
    class_name = db.Column(db.String(10), nullable=True, comment="班级")
    name = db.Column(db.String(50), nullable=True, comment="学生姓名")
    gender = db.Column(db.String(10), nullable=True, comment="学生性别")
    birthday = db.Column(db.Date, nullable=True, comment="出生日期")
    phone = db.Column(db.String(15), nullable=True, comment="联系电话")
    id_card = db.Column(db.String(18), nullable=True, comment="身份证号码")
    region = db.Column(db.String(50), nullable=True, comment="所在区域/行政区划")
    contact_address = db.Column(
        db.String(100), nullable=True, comment="详细联系地址")
    parent_name = db.Column(db.String(50), nullable=True, comment="家长姓名")
    parent_phone = db.Column(db.String(15), nullable=True, comment="家长电话")

    def to_dict(self):
        """
        将学生基本信息转换为字典格式，便于 JSON 序列化
        """
        return {
            "id": self.id,
            "education_id": self.education_id,
            "school": self.school,
            "class_name": self.class_name,
            "name": self.name,
            "gender": self.gender,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "phone": self.phone,
            "id_card": self.id_card,
            "region": self.region,
            "contact_address": self.contact_address,
            "parent_name": self.parent_name,
            "parent_phone": self.parent_phone,
        }
