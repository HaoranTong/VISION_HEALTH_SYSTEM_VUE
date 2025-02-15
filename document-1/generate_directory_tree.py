import os


def generate_tree(directory, level=1, show_files=True, exclude_extensions=None):
    """
    生成指定目录的树状结构。

    :param directory: 要遍历的根目录路径。
    :param level: 要遍历的目录层级，默认为1。
    :param show_files: 是否显示文件，默认为True。
    :param exclude_extensions: 要排除的文件扩展名列表，默认为None。
    :return: 树状结构的字符串。
    """
    tree = ""
    if not os.path.exists(directory):
        return f"目录 {directory} 不存在。"

    if not os.path.isdir(directory):
        return f"{directory} 不是一个有效的目录。"

    # 获取目录中的所有文件和子目录
    entries = os.listdir(directory)
    entries.sort()

    for entry in entries:
        entry_path = os.path.join(directory, entry)
        if os.path.isdir(entry_path):
            # 目录
            tree += f"{'    ' * (level - 1)}├── {entry}/\n"
            if level > 1:
                tree += generate_tree(
                    entry_path, level - 1, show_files, exclude_extensions
                )
        elif os.path.isfile(entry_path) and show_files:
            # 文件
            if exclude_extensions:
                if any(entry.endswith(ext) for ext in exclude_extensions):
                    continue
            tree += f"{'    ' * (level - 1)}├── {entry}\n"

    return tree


def save_tree_to_markdown(
    directory, output_file, level=1, show_files=True, exclude_extensions=None
):
    """
    将目录树保存到Markdown文件。

    :param directory: 要遍历的根目录路径。
    :param output_file: 输出的Markdown文件路径。
    :param level: 要遍历的目录层级，默认为1。
    :param show_files: 是否显示文件，默认为True。
    :param exclude_extensions: 要排除的文件扩展名列表，默认为None。
    """
    tree = generate_tree(directory, level, show_files, exclude_extensions)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# 目录结构：{directory}\n\n")
        f.write(tree)
    print(f"目录结构已保存到 {output_file}")


if __name__ == "__main__":
    # 示例用法
    root_directory = "."  # 当前目录
    output_markdown_file = "directory_structure.md"
    depth_level = 3  # 设置查询的目录层级
    display_files = True  # 是否显示文件
    exclude_file_extensions = [".pyc", ".log"]  # 排除的文件类型

    save_tree_to_markdown(
        root_directory,
        output_markdown_file,
        depth_level,
        display_files,
        exclude_file_extensions,
    )
