# 定义允许的组合查询字段列表
COMPLETE_FIELDS = {
    "data_year", "education_id", "school", "grade", "class_name", "name", "gender", "age",
    "vision_level", "interv_vision_level", "left_eye_naked", "right_eye_naked",
    "left_eye_naked_interv", "right_eye_naked_interv", "left_naked_change", "right_naked_change",
    "left_sphere_change", "right_sphere_change", "left_cylinder_change", "right_cylinder_change",
    "left_axis_change", "right_axis_change", "left_interv_effect", "right_interv_effect",
    "left_sphere_effect", "right_sphere_effect", "left_cylinder_effect", "right_cylinder_effect",
    "left_axis_effect", "right_axis_effect", "left_eye_corrected", "right_eye_corrected",
    "left_keratometry_K1", "right_keratometry_K1", "left_keratometry_K2", "right_keratometry_K2",
    "left_axial_length", "right_axial_length", "guasha", "aigiu", "zhongyao_xunzheng", "rejiu_training", "xuewei_tiefu",
    "reci_pulse", "baoguan", "frame_glasses", "contact_lenses", "night_orthokeratology"
}

# 定义布尔型字段
BOOLEAN_FIELDS = [
    "guasha", "aigiu", "zhongyao_xunzheng", "rejiu_training", "xuewei_tiefu",
    "reci_pulse", "baoguan", "frame_glasses", "contact_lenses", "night_orthokeratology"
]

# 定义字段名到中文标签的映射
FIELD_LABEL_MAPPING = {
    "guasha": "刮痧",
    "aigiu": "艾灸",
    "zhongyao_xunzheng": "中药熏蒸",
    "rejiu_training": "热灸训练",
    "xuewei_tiefu": "穴位贴敷",
    "reci_pulse": "热磁脉冲",
    "baoguan": "拔罐",
    "frame_glasses": "框架眼镜",
    "contact_lenses": "隐形眼镜",
    "intervention_methods": "分组",
    "night_orthokeratology": "夜戴角膜塑型镜"
}

METRIC_CONFIG = {
    "education_id": {"label": "教育ID号", "type": "text"},
    "school": {"label": "学校", "type": "multi-select", "options": ["华兴小学", "苏宁红军小学", "师大附小清华小学"]},
    "class_name": {"label": "班级", "type": "dropdown", "options": [f"{i}班" for i in range(1, 16)]},
    "name": {"label": "姓名", "type": "text"},
    "gender": {"label": "性别", "type": "multi-select", "options": ["男", "女"]},
    "age": {"label": "年龄", "type": "number_range"},
    "data_year": {"label": "数据年份", "type": "dropdown", "options": ["2023", "2024", "2025", "2026", "2027", "2028"]},
    "grade": {"label": "年级", "type": "multi-select", "options": ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级", "七年级", "八年级", "九年级"]},
    "vision_level": {"label": "视力等级", "type": "multi-select", "options": ["临床前期近视", "轻度近视", "中度近视", "假性近视", "正常"]},
    "interv_vision_level": {"label": "干预后视力等级", "type": "multi-select", "options": ["临床前期近视", "轻度近视", "中度近视", "假性近视", "正常"]},
    "left_eye_naked": {"label": "左眼-裸眼视力", "type": "number_range"},
    "right_eye_naked": {"label": "右眼-裸眼视力", "type": "number_range"},
    "left_eye_naked_interv": {"label": "左眼-干预-裸眼视力", "type": "number_range"},
    "right_eye_naked_interv": {"label": "右眼-干预-裸眼视力", "type": "number_range"},
    "left_naked_change": {"label": "左眼裸眼视力变化", "type": "number_range"},
    "right_naked_change": {"label": "右眼裸眼视力变化", "type": "number_range"},
    "left_eye_corrected": {"label": "左眼-矫正视力", "type": "number_range"},
    "right_eye_corrected": {"label": "右眼-矫正视力", "type": "number_range"},
    "left_keratometry_K1": {"label": "左眼-角膜曲率K1", "type": "number_range"},
    "right_keratometry_K1": {"label": "右眼-角膜曲率K1", "type": "number_range"},
    "left_keratometry_K2": {"label": "左眼-角膜曲率K2", "type": "number_range"},
    "right_keratometry_K2": {"label": "右眼-角膜曲率K2", "type": "number_range"},
    "left_axial_length": {"label": "左眼-眼轴", "type": "number_range"},
    "right_axial_length": {"label": "右眼-眼轴", "type": "number_range"},
    "left_sphere_change": {"label": "左眼屈光-球镜变化", "type": "number_range"},
    "right_sphere_change": {"label": "右眼屈光-球镜变化", "type": "number_range"},
    "left_cylinder_change": {"label": "左眼屈光-柱镜变化", "type": "number_range"},
    "right_cylinder_change": {"label": "右眼屈光-柱镜变化", "type": "number_range"},
    "left_axis_change": {"label": "左眼屈光-轴位变化", "type": "number_range"},
    "right_axis_change": {"label": "右眼屈光-轴位变化", "type": "number_range"},
    "left_interv_effect": {"label": "左眼视力干预效果", "type": "multi-select", "options": ["上升", "维持", "下降"]},
    "right_interv_effect": {"label": "右眼视力干预效果", "type": "multi-select", "options": ["上升", "维持", "下降"]},
    "left_sphere_effect": {"label": "左眼球镜干预效果", "type": "multi-select", "options": ["上升", "维持", "下降"]},
    "right_sphere_effect": {"label": "右眼球镜干预效果", "type": "multi-select", "options": ["上升", "维持", "下降"]},
    "left_cylinder_effect": {"label": "左眼柱镜干预效果", "type": "multi-select", "options": ["上升", "维持", "下降"]},
    "right_cylinder_effect": {"label": "右眼柱镜干预效果", "type": "multi-select", "options": ["上升", "维持", "下降"]},
    "left_axis_effect": {"label": "左眼轴位干预效果", "type": "multi-select", "options": ["上升", "维持", "下降"]},
    "right_axis_effect": {"label": "右眼轴位干预效果", "type": "multi-select", "options": ["上升", "维持", "下降"]}
}

FIXED_METRICS = [{
    "field": "vision_level",
    "label": "视力等级",
    "distinct_vals": ["临床前期近视", "轻度近视", "中度近视"]
}]
