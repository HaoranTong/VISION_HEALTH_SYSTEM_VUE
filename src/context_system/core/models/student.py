#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: student.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM\src\context_system\core\models\student.py
功能介绍:
    定义 Student 模型，用于存储学生的基本信息。
    提供 to_dict() 方法以将模型数据转换为字典格式，便于 JSON 序列化。
使用方法:
    通过 SQLAlchemy ORM 创建、查询学生数据，
    调用 to_dict() 方法获取字典数据。
"""
from context_system.infrastructure.database import db

class Student(db.Model):
    """学生模型，用于存储学生基本信息。"""
    __tablename__ = "students"
    __table_args__ = {"extend_existing": True}  # 允许重复定义表，避免重新加载时出错
    id = db.Column(db.Integer, primary_key=True)
    full_edu_id = db.Column(db.String(20))  # 原始教育ID号，非唯一
    school_code = db.Column(db.String(6), nullable=False)  # 学校代码
    school_id = db.Column(db.String(20))  # 由系统管理员维护的学校ID
    index_id = db.Column(db.String(40), unique=True)  # 由学校ID和full_edu_id生成的唯一索引
    name = db.Column(db.String(50))  # 学生姓名
    vision_left = db.Column(db.Float, nullable=False)  # 左眼视力
    vision_right = db.Column(db.Float, nullable=False)  # 右眼视力
    myopia_level = db.Column(db.String(10))  # 近视等级，自动计算

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
            "vision_left": self.vision_left,
            "vision_right": self.vision_right,
            "myopia_level": self.myopia_level
        }
