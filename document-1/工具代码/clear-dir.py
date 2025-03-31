import os
import shutil

# 根目录路径
ROOT_DIR = r"E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE"

# 需要删除的无用目录和文件
UNUSED_PATHS = [
    # 目录
    os.path.join(ROOT_DIR, "frontend", "vscode-extension"),
    os.path.join(ROOT_DIR, "frontend", "web"),
    os.path.join(ROOT_DIR, "src", "context_system"),
    # 文件
    os.path.join(ROOT_DIR, "backend", "infrastructure", "database.py"),
]

# 需要创建的目录
DIRS_TO_CREATE = [
    os.path.join(ROOT_DIR, "backend", "api"),
    os.path.join(ROOT_DIR, "backend", "models"),
]


def delete_unused():
    """删除无用目录和文件"""
    for path in UNUSED_PATHS:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
                print(f"[DELETED] 文件: {path}")
            else:
                shutil.rmtree(path)
                print(f"[DELETED] 目录: {path}")
        else:
            print(f"[SKIPPED] 路径不存在: {path}")


def create_dirs():
    """创建必要目录"""
    for dir_path in DIRS_TO_CREATE:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"[CREATED] 目录: {dir_path}")
        else:
            print(f"[SKIPPED] 目录已存在: {dir_path}")


if __name__ == "__main__":
    print("=== 开始清理与重组 ===")
    delete_unused()
    create_dirs()
    print("=== 操作完成 ===")
