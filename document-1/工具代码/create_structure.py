#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: create_structure.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM\document\create_structure.py
功能介绍:
    自动创建项目文档及代码目录结构，并生成各个包目录下的 __init__.py
    以及部分占位文件。用于在意外丢失代码文件时快速恢复项目结构。
使用方法:
    在项目根目录下运行:
        python create_structure.py
    脚本将自动创建预设的目录结构及相关初始化文件。
"""

import os

# 定义目录结构及各目录下需要创建的文件
structure = {
    ".chat/index": {"__init__.py": "# __init__.py for .chat/index\n"},
    "config/app": {
        "config.py": "# config.py placeholder\n",
        "__init__.py": "# __init__.py for config/app\n",
    },
    "config/security_rules": {
        "__init__.py": "# __init__.py for config/security_rules\n"
    },
    "docker": {},
    "docs": {
        "20250205开发计划.md": "# 20250205开发计划.md\n",
        "近视预防干预系统开发文档_v1.0.md": "# 近视预防干预系统开发文档_v1.0\n",
        "近视预防干预系统开发文档_v1.1.md": "# 近视预防干预系统开发文档_v1.1\n",
        "近视预防干预系统需求文档_v1.0.md": "# 近视预防干预系统需求文档_v1.0\n",
        "近视预防干预系统需求文档_v1.1.md": "# 近视预防干预系统需求文档_v1.1\n",
        "开发任务完成情况记录-250203.md": "# 开发任务完成情况记录-250203\n",
        "开发任务完全情况记录-250204.md": "# 开发任务完全情况记录-250204\n",
    },
    "frontend/vscode-extension/src/commands": {
        "__init__.py": "# __init__.py for frontend/vscode-extension/src/commands\n"
    },
    "frontend/vscode-extension/src/core": {
        "__init__.py": "# __init__.py for frontend/vscode-extension/src/core\n"
    },
    "frontend/vscode-extension/src/webviews/components": {
        "__init__.py": "# __init__.py for frontend/vscode-extension/src/webviews/components\n"
    },
    "frontend/web": {
        "data_entry.html": "<!-- data_entry.html placeholder -->\n",
        "data_query.html": "<!-- data_query.html placeholder -->\n",
        "query_statistics.html": "<!-- query_statistics.html placeholder -->\n",
    },
    "instance": {"app.db": ""},
    "scripts": {},
    "src/context_system/api/endpoints": {
        "__init__.py": "# __init__.py for src/context_system/api/endpoints\n",
        "analysis_api.py": "# analysis_api.py placeholder\n",
        "import_api.py": "# import_api.py placeholder\n",
        "query_api.py": "# query_api.py placeholder\n",
        "student_api.py": "# student_api.py placeholder\n",
    },
    "src/context_system/api": {
        "__init__.py": "# __init__.py for src/context_system/api\n"
    },
    "src/context_system/core/managers": {
        "__init__.py": "# __init__.py for src/context_system/core/managers\n"
    },
    "src/context_system/core/models": {
        "__init__.py": "# __init__.py for src/context_system/core/models\n",
        "models.py": "# models.py placeholder\n",
        "student.py": "# student.py placeholder\n",
    },
    "src/context_system/core/services": {
        "__init__.py": "# __init__.py for src/context_system/core/services\n"
    },
    "src/context_system/core/tasks": {
        "__init__.py": "# __init__.py for src/context_system/core/tasks\n"
    },
    "src/context_system/core": {
        "__init__.py": "# __init__.py for src/context_system/core\n"
    },
    "src/context_system": {"__init__.py": "# __init__.py for src/context_system\n"},
    "src": {"__init__.py": "# __init__.py for src\n"},
    "tests/e2e": {},
    "tests/integration": {},
    "tests/unit": {
        "test_student_api.py": "# test_student_api.py placeholder\n",
        "test_query_api.py": "# test_query_api.py placeholder\n",
        "test_import_api.py": "# test_import_api.py placeholder\n",
    },
}

root_files = {
    "app.py": (
        "#!/usr/bin/env python\n"
        "# -*- coding: utf-8 -*-\n"
        '"""\n'
        "app.py\n\n"
        "功能说明:\n"
        "    初始化 Flask 应用、加载配置、注册各 API 蓝图及静态页面路由,\n"
        "    并启动 Flask 开发服务器（调试模式）。\n"
        "使用方法:\n"
        "    启动命令: python app.py\n"
        '"""\n'
        "if __name__ == '__main__':\n"
        "    from flask import Flask\n"
        "    app = Flask(__name__)\n"
        "    app.run(debug=True)\n"
    ),
    "init_db.py": (
        "#!/usr/bin/env python\n"
        "# -*- coding: utf-8 -*-\n"
        '"""\n'
        "init_db.py\n\n"
        "功能说明:\n"
        "    初始化数据库（例如使用 SQLAlchemy 的 db.create_all()）。\n"
        "使用方法:\n"
        "    运行命令: python init_db.py\n"
        '"""\n'
        "if __name__ == '__main__':\n"
        "    print('初始化数据库...')\n"
    ),
    "README.md": (
        "# 近视预防干预系统\n\n"
        "项目说明: 本项目实现学生视力数据录入、近视筛查, 干预跟踪及统计分析等功能.\n"
    ),
    "requirements.txt": (
        "# 项目依赖库\nFlask\nFlask-SQLAlchemy\npandas\nopenpyxl\nSQLAlchemy\n...\n"
    ),
}


def create_dir_with_files(dir_path, files_dict):
    """
    在指定目录 dir_path 下创建文件列表 files_dict.
    files_dict 是一个字典, 键为文件名, 值为文件内容.
    """
    for filename, content in files_dict.items():
        file_path = os.path.join(dir_path, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"创建文件: {file_path}")
        else:
            print(f"文件已存在: {file_path}")


def create_structure():
    """
    根据预定义的目录结构和文件内容创建项目目录和初始化文件.
    若目录或文件已存在，则跳过创建。
    """
    for rel_dir, files in structure.items():
        abs_dir = os.path.join(os.getcwd(), rel_dir)
        os.makedirs(abs_dir, exist_ok=True)
        print(f"创建目录: {abs_dir}")
        if files:
            create_dir_with_files(abs_dir, files)
    for filename, content in root_files.items():
        abs_file = os.path.join(os.getcwd(), filename)
        if not os.path.exists(abs_file):
            with open(abs_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"创建根目录文件: {abs_file}")
        else:
            print(f"根目录文件已存在: {abs_file}")


if __name__ == "__main__":
    create_structure()
    print("目录结构创建完毕。")
