import re
from pathlib import Path


def clean_debug_code(file_path):
    """安全移除所有排序相关调试代码，保留业务关键日志"""
    # 定义保留的关键业务日志（白名单）
    KEEP_PATTERNS = [
        r'分页参数',
        r'报表名称',
        r'统计错误',
        r'filterAnnotation'
    ]

    # 定义需要删除的调试模式（黑名单）
    REMOVE_PATTERNS = [
        r'current_app\.logger\.\w+\(.*?(sort_priority|order_by|ORDER BY|columns|order_expr|SQL|query|dynamic_query).*?\)',
        r'print\(.*?(col|order|sort|priority|expr).*?\)',
        r'#\s*(DEBUG|TODO).*?排序',
        r'调试用临时代码'
    ]

    file = Path(file_path)
    backup = file.with_suffix('.py.bak')

    # 创建备份
    file.rename(backup)
    print(f"已创建备份文件: {backup}")

    with open(backup, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(file, 'w', encoding='utf-8') as f:
        for line in lines:
            # 保留白名单日志
            if any(re.search(p, line) for p in KEEP_PATTERNS):
                f.write(line)
                continue

            # 删除黑名单调试代码
            if any(re.search(p, line) for p in REMOVE_PATTERNS):
                print(f"已删除: {line.strip()}")
                continue

            # 保留其他代码
            f.write(line)

    print(f"清理完成，原始文件已备份，清理后文件: {file}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        clean_debug_code(sys.argv[1])
    else:
        clean_debug_code('backend/api/analysis_api.py')
