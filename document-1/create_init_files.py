import os


def create_init_files(root_dir):
    """
    在指定根目录下的所有子目录中创建 __init__.py 文件。
    :param root_dir: 根目录路径
    """
    for dirpath, dirnames, _ in os.walk(root_dir):
        # 跳过虚拟环境目录（如 .venv）
        if ".venv" in dirpath:
            continue

        # 在每个子目录中创建 __init__.py 文件
        for dirname in dirnames:
            init_file_path = os.path.join(dirpath, dirname, "__init__.py")
            if not os.path.exists(init_file_path):
                with open(init_file_path, "w", encoding="utf-8") as f:
                    f.write("# Auto-generated __init__.py file\n")
                print(f"Created: {init_file_path}")
            else:
                print(f"Skipped: {init_file_path} (already exists)")


if __name__ == "__main__":
    # 根目录路径
    ROOT_DIR = r"E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE"

    print("=== 开始创建 __init__.py 文件 ===")
    create_init_files(ROOT_DIR)
    print("=== 操作完成 ===")
