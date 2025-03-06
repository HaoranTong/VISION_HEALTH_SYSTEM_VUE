#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: check_db_format.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\check_db_format.py
功能说明:
    独立的脚本，用于查询数据库中 StudentExtension 表中的部分记录，
    并以 JSON 格式输出，方便检查导入数据时各字段是否经过正确转换。
使用说明:
    1. 确保项目虚拟环境已激活，并安装所有依赖。
    2. 在命令行中执行该脚本，例如在 PowerShell 中运行：
         python check_db_format.py
    3. 脚本会输出部分 StudentExtension 记录的 JSON 数据到控制台，
       您可以检查各字段数据格式是否符合预期。
"""

import json
from backend.infrastructure.database import db
from backend.models.student_extension import StudentExtension
from app import create_app  # 使用项目中已有的 Flask 应用工厂


def main():
    app = create_app()
    with app.app_context():
        # 查询 StudentExtension 表中的前 10 条记录
        records = StudentExtension.query.limit(10).all()
        # 将记录转换为字典列表
        result = [record.to_dict() for record in records]
        # 输出为格式化的 JSON 字符串
        print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()
