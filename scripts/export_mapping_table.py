#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称: export_mapping_table.py
完整存储路径: scripts/export_mapping_table.py
功能说明:
    提取我们确定的数据字段映射表中的“电子表格列名称”和“数据库字段”两列，
    并输出一个 Markdown 格式的两列表格，方便后续确认和修改。
使用说明:
    在终端中运行此脚本：
        python scripts/export_mapping_table.py
    控制台会输出 Markdown 格式的表格，您可以复制到 Markdown 编辑器中进一步修改。
"""

# 学生基本信息表映射
basic_info_mapping = [
    ("教育ID号", "education_id"),
    ("学校", "school"),
    ("班级", "class_name"),
    ("姓名", "name"),
    ("性别", "gender"),
    ("身份证号码", "id_card"),
    ("出生日期", "birthday"),
    ("联系电话", "phone"),
    ("区域", "region"),
    ("联系地址", "contact_address"),
    ("家长姓名", "parent_name"),
    ("家长电话", "parent_phone"),
]

# 学生扩展信息表映射
extension_mapping = [
    ("年级", "grade"),
    ("数据年份", "data_year"),
    ("身高", "height"),
    ("体重", "weight"),
    ("饮食偏好", "diet_preference"),
    ("运动偏好", "exercise_preference"),
    ("健康教育", "health_education"),
    ("既往史", "past_history"),
    ("家族史", "family_history"),
    ("是否早产", "premature"),
    ("过敏史", "allergy"),
    ("右眼-裸眼视力", "right_eye_naked"),
    ("左眼-裸眼视力", "left_eye_naked"),
    ("右眼-矫正视力", "right_eye_corrected"),
    ("左眼-矫正视力", "left_eye_corrected"),
    ("右眼-角膜曲率K1", "right_keratometry_K1"),
    ("左眼-角膜曲率K1", "left_keratometry_K1"),
    ("右眼-角膜曲率K2", "right_keratometry_K2"),
    ("左眼-角膜曲率K2", "left_keratometry_K2"),
    ("右眼-眼轴", "right_axial_length"),
    ("左眼-眼轴", "left_axial_length"),
    ("右眼屈光-球镜", "right_sphere"),
    ("右眼屈光-柱镜", "right_cylinder"),
    ("右眼屈光-轴位", "right_axis"),
    ("左眼屈光-球镜", "left_sphere"),
    ("左眼屈光-柱镜", "left_cylinder"),
    ("左眼屈光-轴位", "left_axis"),
    ("右眼散瞳-球镜", "right_dilated_sphere"),
    ("右眼散瞳-柱镜", "right_dilated_cylinder"),
    ("右眼散瞳-轴位", "right_dilated_axis"),
    ("左眼散瞳-球镜", "left_dilated_sphere"),
    ("左眼散瞳-柱镜", "left_dilated_cylinder"),
    ("左眼散瞳-轴位", "left_dilated_axis"),
    ("【新增】视力等级", "vision_level"),
    ("右眼-前房深度", "right_anterior_depth"),
    ("左眼-前房深度", "left_anterior_depth"),
    ("其他情况", "other_info"),
    ("眼疲劳状况", "eye_fatigue"),
    ("框架眼镜", "frame_glasses"),
    ("隐形眼镜", "contact_lenses"),
    ("夜戴角膜塑型镜", "night_orthokeratology"),
    ("刮痧", "guasha"),
    ("艾灸", "aigiu"),
    ("中药熏蒸", "zhongyao_xunzheng"),
    ("热灸训练", "rejiu_training"),
    ("穴位贴敷", "xuewei_tiefu"),
    ("热磁脉冲", "reci_pulse"),
    ("拔罐", "baoguan"),
    ("右眼-干预-裸眼视力", "right_eye_naked_interv"),
    ("左眼-干预-裸眼视力", "left_eye_naked_interv"),
    ("右眼屈光-干预-球镜", "right_sphere_interv"),
    ("右眼屈光-干预-柱镜", "right_cylinder_interv"),
    ("右眼屈光-干预-轴位", "right_axis_interv"),
    ("左眼屈光-干预-球镜", "left_sphere_interv"),
    ("左眼屈光-干预-柱镜", "left_cylinder_interv"),
    ("左眼屈光-干预-轴位", "left_axis_interv"),
    ("【新增】干预后视力等级", "interv_vision_level"),
    ("【新增】左眼裸眼视力变化", "left_naked_change"),
    ("【新增】右眼裸眼视力变化", "right_naked_change"),
    ("【新增】左眼屈光-球镜变化", "left_sphere_change"),
    ("【新增】右眼屈光-球镜变化", "right_sphere_change"),
    ("【新增】左眼屈光-柱镜变化", "left_cylinder_change"),
    ("【新增】右眼屈光-柱镜变化", "right_cylinder_change"),
    ("【新增】左眼屈光-轴位变化", "left_axis_change"),
    ("【新增】右眼屈光-轴位变化", "right_axis_change"),
    ("【新增】左眼视力干预效果", "left_interv_effect"),
    ("【新增】右眼视力干预效果", "right_interv_effect"),
    ("【新增】左眼球镜干预效果", "left_sphere_effect"),
    ("【新增】右眼球镜干预效果", "right_sphere_effect"),
    ("【新增】左眼柱镜干预效果", "left_cylinder_effect"),
    ("【新增】右眼柱镜干预效果", "right_cylinder_effect"),
    ("【新增】左眼轴位干预效果", "left_axis_effect"),
    ("【新增】右眼轴位干预效果", "right_axis_effect"),
    ("第1次干预", "interv1"),
    ("第2次干预", "interv2"),
    ("第3次干预", "interv3"),
    ("第4次干预", "interv4"),
    ("第5次干预", "interv5"),
    ("第6次干预", "interv6"),
    ("第7次干预", "interv7"),
    ("第8次干预", "interv8"),
    ("第9次干预", "interv9"),
    ("第10次干预", "interv10"),
    ("第11次干预", "interv11"),
    ("第12次干预", "interv12"),
    ("第13次干预", "interv13"),
    ("第14次干预", "interv14"),
    ("第15次干预", "interv15"),
    ("第16次干预", "interv16")
]

# 合并所有映射
all_mappings = basic_info_mapping + extension_mapping

# 生成 Markdown 表格
md_lines = []
md_lines.append("| 电子表格列名称 | 数据库字段 |")
md_lines.append("| -------------- | ---------- |")
for display_name, db_field in all_mappings:
    md_lines.append(f"| {display_name} | {db_field} |")

markdown_table = "\n".join(md_lines)
print(markdown_table)
