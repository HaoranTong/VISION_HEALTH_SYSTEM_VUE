#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
文件名称: adjust_directory_structure.py
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\adjust_directory_structure.py
功能介绍:
    1. 依据当前开发需求，调整文档和代码目录结构。
    2. 自动创建缺失的目录和文件，确保开发环境完整。
    3. 删除不需要的目录和文件，保持项目整洁。
使用方法:
    在项目根目录执行:
        python adjust_directory_structure.py
"""

import os
import shutil

# **项目根目录**
PROJECT_ROOT = r"E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE"

# **需要创建的目录**
REQUIRED_DIRECTORIES = [
    "backend/api",
    "backend/core",
    "backend/infrastructure",
    "backend/models",
    "backend/services",
    "backend/tests",
    "config/app",
    "config/security_rules",
    "docker",
    "docs",
    "document",
    "failures",
    "frontend/src/assets",
    "frontend/src/components",
    "frontend/src/layouts",
    "frontend/src/pages",
    "frontend/src/router",
    "frontend/src/services",
    "frontend/src/store",
    "frontend/web",
    "instance",
    "scripts",
    "src/context_system/api/endpoints",
    "src/context_system/core/managers",
    "src/context_system/core/models",
    "src/context_system/core/services",
    "src/context_system/core/tasks",
    "src/context_system/infrastructure/database",
    "tests/e2e",
    "tests/integration",
    "tests/unit",
]

# **需要创建的文件**
REQUIRED_FILES = [
    "backend/app.py",
    "backend/config.py",
    "backend/database.py",
    "backend/requirements.txt",
    "backend/run.py",
    "config/app/__init__.py",
    "config/app/config.py",
    "config/security_rules/__init__.py",
    "docs/README.md",
    "document/README.md",
    "frontend/src/router/index.js",
    "frontend/src/services/api.js",
    "frontend/src/store/index.js",
    "frontend/src/main.js",
    "frontend/src/App.vue",
    "frontend/web/index.html",
    "frontend/web/dashboard.html",
    "frontend/web/data_entry.html",
    "frontend/web/data_query.html",
    "frontend/web/query_statistics.html",
    "instance/app.db",
    "scripts/README.md",
    "src/context_system/api/endpoints/__init__.py",
    "src/context_system/api/endpoints/analysis_api.py",
    "src/context_system/api/endpoints/import_api.py",
    "src/context_system/api/endpoints/query_api.py",
    "src/context_system/api/endpoints/student_api.py",
    "src/context_system/core/__init__.py",
    "src/context_system/core/managers/__init__.py",
    "src/context_system/core/models/__init__.py",
    "src/context_system/core/models/models.py",
    "src/context_system/core/models/student.py",
    "src/context_system/core/services/__init__.py",
    "src/context_system/core/tasks/__init__.py",
    "src/context_system/infrastructure/__init__.py",
    "src/context_system/infrastructure/database/__init__.py",
    "src/context_system/infrastructure/database/database.py",
    "tests/unit/test_import_api.py",
    "tests/unit/test_query_api.py",
    "tests/unit/test_student_api.py",
    "README.md",
    "requirements.txt",
    "adjust_directory_structure.py",
]

# **需要删除的无用目录**
UNUSED_DIRECTORIES = [
    ".chat",
    ".vscode-extension",
    "backend/old",
    "frontend/old",
    "src/context_system/old",
]

# **需要删除的无用文件**
UNUSED_FILES = [
    "backend/old_config.py",
    "frontend/old_index.html",
    "src/context_system/old_models.py",
]


def create_required_directories():
    """确保所有必须的目录存在"""
    for directory in REQUIRED_DIRECTORIES:
        full_path = os.path.join(PROJECT_ROOT, directory)
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            print(f"[创建] 目录: {full_path}")


def create_required_files():
    """确保关键的 __init__.py 和配置文件存在"""
    for file_path in REQUIRED_FILES:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        parent_dir = os.path.dirname(full_path)

        # **确保目录存在**
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            print(f"[创建] 目录: {parent_dir}")

        # **创建文件**
        if not os.path.exists(full_path):
            with open(full_path, "w", encoding="utf-8") as f:
                if file_path.endswith(".py"):
                    f.write(f'""" {file_path} - 自动生成的初始化文件 """\n')
                else:
                    f.write("")
            print(f"[创建] 文件: {file_path}")


def delete_unused_directories():
    """删除不再使用的目录"""
    for directory in UNUSED_DIRECTORIES:
        full_path = os.path.join(PROJECT_ROOT, directory)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
            print(f"[删除] 目录: {full_path}")


def delete_unused_files():
    """删除不再使用的文件"""
    for file_path in UNUSED_FILES:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"[删除] 文件: {file_path}")


if __name__ == "__main__":
    print("⚙️ 开始调整目录结构...")
    create_required_directories()
    create_required_files()
    delete_unused_directories()
    delete_unused_files()
    print("✅ 目录结构调整完成！")
