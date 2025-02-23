#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: student_extension.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\backend\models\student_extension.py
功能介绍: 学生扩展信息模型，包含视力检测数据及干预记录
"""

from datetime import datetime
from backend.infrastructure.database import db


class StudentExtension(db.Model):
    __tablename__ = "student_extensions"

    # 主键字段
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        "students.id"), unique=True, nullable=False)

    # 基础信息扩展
    region = db.Column(db.String(50), comment="所在区域")
    diet_preference = db.Column(db.String(100), comment="饮食偏好")

    # 视力检测数据（示例字段）
    right_keratometry_K1 = db.Column(db.Float, comment="右眼角膜曲率K1值")
    left_keratometry_K1 = db.Column(db.Float, comment="左眼角膜曲率K1值")

    # 干预时间字段（完整16个）
    intervention1 = db.Column(db.DateTime, comment="第1次干预时间")
    intervention2 = db.Column(db.DateTime, comment="第2次干预时间")
    intervention3 = db.Column(db.DateTime, comment="第3次干预时间")
    # ... 其他干预时间字段按相同格式添加

    def to_dict(self):
        """将模型转换为前端友好的字典格式"""
        return {
            "region": self.region,
            "diet_preference": self.diet_preference,
            "right_keratometry_K1": self.right_keratometry_K1,
            "left_keratometry_K1": self.left_keratometry_K1,
            "intervention1": self._format_datetime(self.intervention1),
            "intervention2": self._format_datetime(self.intervention2),
            "intervention3": self._format_datetime(self.intervention3),
            # 其他字段按相同模式添加
        }

    def _format_datetime(self, dt):
        """私有方法：统一处理时间格式"""
        return dt.isoformat() if dt else None

    def __repr__(self):
        return f"<StudentExtension {self.student_id}>"
