# 文件名称: fix_directory.py
# 完整保存路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\fix_directory.py
"""
功能说明:
    本脚本用于自动化修复项目目录结构，支持模拟运行和实际执行两种模式
    修复内容：
    1. 补充缺失的 clean_dirs 函数定义
    2. 完善函数顺序确保调用关系正确
"""

import os
import shutil
import argparse
import sys

# 项目根目录（自动获取脚本位置）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 目录映射配置
DIRECTORY_MAP = {
    os.path.join('frontend', 'web', 'student_detail.html'):
        os.path.join('frontend', 'templates', 'student_detail.html'),
    os.path.join('frontend', 'web', 'sidebar.html'):
        os.path.join('frontend', 'templates', '_components', 'sidebar.html'),
    os.path.join('frontend', 'web', 'topnav.html'):
        os.path.join('frontend', 'templates', '_components', 'topnav.html'),
}

# 需要清理的旧目录
OBSOLETE_DIRS = [
    os.path.join('frontend', 'web'),
    os.path.join('frontend', 'src'),
    os.path.join('frontend', 'static', 'css', 'components'),
    os.path.join('frontend', 'static', 'js', 'pages')
]

# ------------------------- 功能函数定义 -------------------------


def validate_paths():
    """验证必要文件是否存在"""
    required_files = [
        os.path.join('frontend', 'web', 'student_detail.html'),
        os.path.join('frontend', 'web', 'sidebar.html'),
        os.path.join('frontend', 'web', 'topnav.html')
    ]

    missing = []
    for rel_path in required_files:
        abs_path = os.path.join(PROJECT_ROOT, rel_path)
        if not os.path.exists(abs_path):
            missing.append(rel_path)

    if missing:
        print("❌ 缺失关键文件：")
        for f in missing:
            print(f" - {f}")
        return False
    return True


def create_dirs(dry_run=True):
    """创建目标目录结构"""
    new_dirs = [
        os.path.join('frontend', 'templates', '_components'),
        os.path.join('frontend', 'static', 'css'),
        os.path.join('frontend', 'static', 'js'),
        os.path.join('frontend', 'static', 'images')
    ]

    for rel_dir in new_dirs:
        abs_dir = os.path.join(PROJECT_ROOT, rel_dir)
        if dry_run:
            print(f"[DRY RUN] 创建目录：{abs_dir}")
        else:
            os.makedirs(abs_dir, exist_ok=True)
            print(f"✅ 已创建目录：{rel_dir}")


def move_files(dry_run=True):
    """执行文件迁移操作"""
    for src_rel, dst_rel in DIRECTORY_MAP.items():
        src_abs = os.path.join(PROJECT_ROOT, src_rel)
        dst_abs = os.path.join(PROJECT_ROOT, dst_rel)

        if dry_run:
            print(f"[DRY RUN] 移动文件：{src_rel} -> {dst_rel}")
        else:
            try:
                os.makedirs(os.path.dirname(dst_abs), exist_ok=True)
                shutil.move(src_abs, dst_abs)
                print(f"✅ 已移动文件：{src_rel} -> {dst_rel}")
            except Exception as e:
                print(f"❌ 移动失败：{src_rel} | 错误：{str(e)}")


def clean_dirs(dry_run=True):
    """清理旧目录"""
    for rel_dir in OBSOLETE_DIRS:
        abs_dir = os.path.join(PROJECT_ROOT, rel_dir)
        if not os.path.exists(abs_dir):
            continue

        if dry_run:
            print(f"[DRY RUN] 删除目录：{abs_dir}")
        else:
            try:
                shutil.rmtree(abs_dir)
                print(f"✅ 已删除目录：{rel_dir}")
            except Exception as e:
                print(f"❌ 删除失败：{rel_dir} | 错误：{str(e)}")


def update_flask_config(dry_run=True):
    """更新Flask配置文件"""
    config_file = os.path.join(PROJECT_ROOT, 'app.py')
    new_config = (
        "app = Flask(\n"
        "    __name__,\n"
        "    template_folder='frontend/templates',\n"
        "    static_folder='frontend/static'\n"
        ")"
    )

    if dry_run:
        print("[DRY RUN] 将更新app.py配置")
        return

    try:
        with open(config_file, 'r+', encoding='utf-8') as f:
            content = f.read()
            new_content = content.replace(
                "template_folder='frontend/web/templates'",
                "template_folder='frontend/templates'"
            ).replace(
                "static_folder='frontend/web/static'",
                "static_folder='frontend/static'"
            )

            if new_content == content:
                new_content = content.replace(
                    "app = Flask(__name__)",
                    new_config
                )

            f.seek(0)
            f.write(new_content)
            f.truncate()
        print("✅ 已更新Flask配置")
    except Exception as e:
        print(f"❌ 配置文件更新失败：{str(e)}")

# ------------------------- 主程序 -------------------------


def main():
    parser = argparse.ArgumentParser(description='项目目录修复工具')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dry-run',
                       action='store_true',
                       help='模拟运行（默认模式）')
    group.add_argument('-e', '--execute',
                       action='store_true',
                       help='实际执行修改操作')
    args = parser.parse_args()
    dry_run = not args.execute

    print(f"\n🛠️ 当前模式: {'模拟运行' if dry_run else '实际执行'}\n")

    # 验证路径
    if not validate_paths():
        print("❌ 验证失败，请检查关键文件是否存在")
        sys.exit(1)

    # 执行操作流程
    create_dirs(dry_run)
    move_files(dry_run)
    clean_dirs(dry_run)  # 现在已正确定义
    update_flask_config(dry_run)

    if dry_run:
        print("\n⚠️ 注意：以上为模拟运行，添加 --execute 参数实际执行")


if __name__ == "__main__":
    main()
