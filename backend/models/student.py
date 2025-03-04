#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: student.py
完整存储路径: backend/models/student.py
功能说明:
    定义 Student 模型，用于存储学生的基本信息（不随时间变化的数据字段）。
    主要字段包括：education_id（教育ID号，作为唯一标识，不允许为空且唯一）、school、class_name、name、gender、birthday、phone、id_card、region、contact_address、parent_name、parent_phone。
使用说明:
    通过 SQLAlchemy ORM 对学生数据进行 CRUD 操作。数据导入模块依据 education_id 判断记录存在性。
"""

from backend.infrastructure.database import db
from backend.models.student_extension import StudentExtension


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    # 教育ID号，设置为不允许为空且唯一
    education_id = db.Column(db.String(20), unique=True,
                             nullable=False, comment="教育ID号")
    school = db.Column(db.String(50), nullable=True, comment="学校名称")
    class_name = db.Column(db.String(10), nullable=True, comment="学生所在班级")
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

    # 与扩展信息表的关系，一个学生对应一条扩展记录
    extension = db.relationship(
        "StudentExtension", backref="student", uselist=False)

    def to_dict(self):
        """
        将学生基本信息转换为字典格式，便于 JSON 序列化。
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
