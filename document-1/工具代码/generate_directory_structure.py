import os

def generate_markdown_tree(directory):
 ""
    生成指定目录的树状结构，并以 Markdown 格式返回。
    """
markdown_tree = ''
for root, dirs, files in os.walk(directory):
# 计算当前目录的层级
level = root.replace(directory, '').count(os.sep)
indent = ' ' * 4 * level
markdown_tree += f"{indent}- **{os.path.basename(root)}/**\n"
subindent = ' ' * 4 * (level + 1)
for file in files:
markdown_tree += f"{subindent}- {file}\n"
return markdown_tree

def save_markdown_tree(directory, output_file):
"""
    将目录树以 Markdown 格式保存到指定文件。
    """
markdown_tree = generate_markdown_tree(directory)
with open(output_file, 'w', encoding='utf-8') as f:
f.write(markdown_tree)

if __name__ == '__main__':
current_directory = os.getcwd()  # 获取当前工作目录
output_filename = 'directory_structure.md'
save_markdown_tree(current_directory, output_filename)
print(f"目录结构已保存为 {output_filename}")
