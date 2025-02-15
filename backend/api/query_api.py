#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: query_api.py
完整存储路径: backend/query_api.py
功能介绍:
    实现学生数据查询 API 接口。
    支持按照学生姓名进行模糊查询，并支持分页查询，
    返回当前页数据及总记录数，数据格式为 JSON。
使用方法:
    API接口 URL: /api/students/query
    请求方法: GET
    参数: name (模糊查询关键字), page, per_page
"""
from flask import Blueprint, request, jsonify
from backend.models.student import Student

query_api = Blueprint("query_api", __name__)


@query_api.route("/api/students/query", methods=["GET"])
def query_students():
    """
    学生数据查询 API 接口
    支持根据学生姓名进行模糊查询，并支持分页查询。
    返回查询结果和总记录数，格式为 JSON。
    """
    name = request.args.get("name", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    query = Student.query.filter(Student.name.ilike(f"%{name}%"))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    students = [student.to_dict() for student in pagination.items]
    return jsonify(
        {
            "students": students,
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
        }
    )
