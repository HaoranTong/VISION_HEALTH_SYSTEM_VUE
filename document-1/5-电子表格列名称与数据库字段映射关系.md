下面是学生基本信息表（Student 表）和扩展信息表（StudentExtension 表）的字段映射关系文档，详细说明了各字段的来源、用途和在系统中的作用。

------

# 学生基本信息表（Student 表）字段映射关系

| 模型属性                   | 来源（Excel 列名称） | 说明                                                         |
| -------------------------- | -------------------- | ------------------------------------------------------------ |
| **id**                     | ——                   | 主键，自增整数，用于唯一标识每条学生记录。                   |
| **full_edu_id**            | '教育ID号'           | 原始导入的教育ID号，非唯一，来自 Excel 的“教育ID号”。        |
| **school_code**            | ——（由系统生成）     | 根据 Excel 中“学校”字段，通过映射字典生成的学校代码（例如：001、002…）。 |
| **school_id**              | '学校'               | 保存 Excel 中“学校”的原始内容，即学校名称。                  |
| **index_id**               | ——                   | 唯一索引，由 school_code 与 full_edu_id 组合生成，用于确保唯一性。 |
| **name**                   | '姓名'               | 学生姓名。                                                   |
| **gender**                 | '性别'               | 学生性别。                                                   |
| **age**                    | '年龄'               | 学生年龄，整数。                                             |
| **birthday**               | '出生日期'           | 学生出生日期，转换为 Python date 对象。                      |
| **id_card**                | '身份证'             | 学生身份证号码，转换为字符串，避免科学计数法显示。           |
| **phone**                  | '联系电话'           | 学生联系电话，转换为字符串。                                 |
| **parent_name**            | '家长姓名'           | 法定监护人姓名。                                             |
| **parent_phone**           | '家长电话'           | 法定监护人联系电话，转换为字符串。                           |
| **grade**                  | '年级'               | 学生所在年级。                                               |
| **class_name**             | '班级'               | 学生所在班级。                                               |
| **vision_right**           | '右眼-裸眼视力'      | 右眼裸眼视力数据，浮点数。                                   |
| **vision_left**            | '左眼-裸眼视力'      | 左眼裸眼视力数据，浮点数。                                   |
| **vision_right_corrected** | '右眼-矫正视力'      | 右眼矫正视力（可选），若存在则转换为浮点数；否则为 None。    |
| **vision_left_corrected**  | '左眼-矫正视力'      | 左眼矫正视力（可选），若存在则转换为浮点数；否则为 None。    |
| **myopia_level**           | ——                   | 自动计算的近视等级，初始为空，由系统后续计算填充。           |

> **说明**：
>
> - “学校ID”字段在这里用于存储 Excel 中“学校”的内容，也就是学校名称，而“school_code”则由系统通过映射字典生成。
> - “index_id”是由学校代码和教育ID号组合而成，用于确保每个学生记录的唯一性。

------

下面是更新后的扩展字段映射关系表，增加了缺失的字段映射。请参考下面的文档和代码说明，然后更新 import_api.py 中的 EXTENDED_FIELD_MAP 部分。

------

### 更新后的扩展字段映射关系表

| Excel 列名称                               | StudentExtension 模型属性名称        | 说明                                                         |
| ------------------------------------------ | ------------------------------------ | ------------------------------------------------------------ |
| '区域'                                     | region                               | 学生所在区域                                                 |
| '饮食偏好'                                 | diet_preference                      | 学生饮食偏好                                                 |
| '运动偏好'                                 | exercise_preference                  | 学生运动偏好                                                 |
| '健康教育'                                 | health_education                     | 健康教育情况                                                 |
| '矫正方式'                                 | correction_method                    | 矫正方式信息                                                 |
| '既往史'                                   | past_history                         | 学生的既往病史（新增）                                       |
| '家族史'                                   | family_history                       | 家族病史（新增）                                             |
| '是否早产'                                 | premature_birth                      | 是否早产（新增，可存为字符串或布尔值，建议字符串）           |
| '过敏史'                                   | allergy_history                      | 过敏史（新增）                                               |
| '矫正方式类型'                             | correction_method_type               | 矫正方式类型（新增，对应Excel中的“矫正方式类型”，可能隐藏后缀） |
| '右眼-角膜曲率K1'                          | right_keratometry_K1                 | 右眼角膜曲率K1                                               |
| '左眼-角膜曲率K1'                          | left_keratometry_K1                  | 左眼角膜曲率K1                                               |
| '右眼-角膜曲率K2'                          | right_keratometry_K2                 | 右眼角膜曲率K2                                               |
| '左眼-角膜曲率K2'                          | left_keratometry_K2                  | 左眼角膜曲率K2                                               |
| '右眼-眼轴'                                | right_axial_length                   | 右眼眼轴长度                                                 |
| '左眼-眼轴'                                | left_axial_length                    | 左眼眼轴长度                                                 |
| '右眼屈光-球镜'                            | right_sphere                         | 右眼屈光-球镜                                                |
| '右眼屈光-柱镜'                            | right_cylinder                       | 右眼屈光-柱镜                                                |
| '右眼屈光-轴位'                            | right_axis                           | 右眼屈光-轴位                                                |
| '左眼屈光-球镜'                            | left_sphere                          | 左眼屈光-球镜                                                |
| '左眼屈光-柱镜'                            | left_cylinder                        | 左眼屈光-柱镜                                                |
| '左眼屈光-轴位'                            | left_axis                            | 左眼屈光-轴位                                                |
| '右眼散瞳-球镜'                            | right_dilation_sphere                | 右眼散瞳-球镜                                                |
| '右眼散瞳-柱镜'                            | right_dilation_cylinder              | 右眼散瞳-柱镜                                                |
| '右眼散瞳-轴位'                            | right_dilation_axis                  | 右眼散瞳-轴位                                                |
| '左眼散瞳-球镜'                            | left_dilation_sphere                 | 左眼散瞳-球镜                                                |
| '左眼散瞳-柱镜'                            | left_dilation_cylinder               | 左眼散瞳-柱镜                                                |
| '左眼散瞳-轴位'                            | left_dilation_axis                   | 左眼散瞳-轴位                                                |
| '右眼-前房深度'                            | right_anterior_chamber               | 右眼前房深度                                                 |
| '左眼-前房深度'                            | left_anterior_chamber                | 左眼前房深度                                                 |
| '其他情况'                                 | other_remarks                        | 其他备注信息                                                 |
| '眼疲劳状况'                               | eye_fatigue                          | 眼疲劳状况                                                   |
| '右眼散瞳-干预-球镜'                       | right_intervention_dilation_sphere   | 右眼散瞳干预-球镜                                            |
| '右眼散瞳-干预-柱镜'                       | right_intervention_dilation_cylinder | 右眼散瞳干预-柱镜                                            |
| '右眼散瞳-干预-轴位'                       | right_intervention_dilation_axis     | 右眼散瞳干预-轴位                                            |
| '左眼散瞳-干预-球镜'                       | left_intervention_dilation_sphere    | 左眼散瞳干预-球镜                                            |
| '左眼散瞳-干预-柱镜'                       | left_intervention_dilation_cylinder  | 左眼散瞳干预-柱镜                                            |
| '左眼散瞳-干预-轴位'                       | left_intervention_dilation_axis      | 左眼散瞳干预-轴位                                            |
| '第1次干预' 至 '第16次干预'                | intervention1 至 intervention16      | 每次干预记录的日期时间（存为 DateTime 类型）                 |
| 其他由系统计算得到的新增字段（初始为空）： |                                      |                                                              |
| **post_intervention_vision_level**         | ——                                   | 干预后视力等级                                               |
| **left_naked_vision_change**               | ——                                   | 左眼裸眼视力变化                                             |
| **right_naked_vision_change**              | ——                                   | 右眼裸眼视力变化                                             |
| **left_sphere_change**                     | ——                                   | 左眼屈光-球镜变化                                            |
| **right_sphere_change**                    | ——                                   | 右眼屈光-球镜变化                                            |
| **left_cylinder_change**                   | ——                                   | 左眼屈光-柱镜变化                                            |
| **right_cylinder_change**                  | ——                                   | 右眼屈光-柱镜变化                                            |
| **left_intervention_effect**               | ——                                   | 左眼干预效果                                                 |
| **right_intervention_effect**              | ——                                   | 右眼干预效果                                                 |
| **left_sphere_intervention_effect**        | ——                                   | 左眼球镜干预效果                                             |
| **right_sphere_intervention_effect**       | ——                                   | 右眼球镜干预效果                                             |
| **left_cylinder_intervention_effect**      | ——                                   | 左眼柱镜干预效果                                             |
| **right_cylinder_intervention_effect**     | ——                                   | 右眼柱镜干预效果                                             |

> **备注：**
>
> - 带 “——” 的字段表示系统后续计算得到的新增字段，初始导入时为空。
> - Excel 中的“矫正方式类型”可能存在隐藏后缀（如 “矫正方式类型.1”、“矫正方式类型.2”），统一映射为模型属性 `correction_method_type`。（此处可以根据实际需求决定是否合并这些列）

------

### 回答你的问题

- **主键 (id)**：
   在 StudentExtension 表中，`id` 是该表的自增主键，用于唯一标识扩展记录。
- **外键 (student_id)**：
   `student_id` 用于连接 Student 表和 StudentExtension 表，它保存的是 Student 表中对应记录的主键（Student.id）。
- **region 字段**：
   `region` 对应 Excel 中的 “区域” 列，存储学生所在区域。

请检查以上映射关系是否与《近视预防干预系统需求文档_v1.3》的规定一致，同时确保 Excel 文件中各列名称（使用 repr() 检查）与映射关系表完全匹配。如果有需要调整的部分，请反馈具体问题。

> **备注**：
>
> - 对于标记为 “——” 的字段，这些是系统后续计算得到的新增字段，初始导入时通常为空。
>
> - 在基本信息表中，**school_id** 保存 Excel 中“学校”的内容，而 **school_code** 则是系统生成的代码；
>
> - id
>
>    和 
>
>   student_id
>
>    的区别：
>
>   - **id** 为 StudentExtension 表的自增主键；
>   - **student_id** 为外键，引用 Student 表中对应记录的 **id**，用于关联扩展信息与基本信息。

------

### 总结回答

1. **关于 student_id 和 id 的区别**
   - **id** 是扩展信息表自身的主键（自动生成的唯一标识）。
   - **student_id** 是外键，用来连接 Student 表和 StudentExtension 表，保存的是对应学生记录的主键（Student.id）。
2. **关于 region 字段**
   - **region** 对应 Excel 文件中的 “区域” 列，表示学生所在区域或行政区划。

------

请核对以上字段映射关系是否符合《近视预防干预系统需求文档_v1.3》的规定，并确认 Excel 文件中的列名称与之匹配。如果有任何不一致或疑问，请指出详细问题。

'教育ID号'
'学校'
'年级'
'班级'
'身高'
'体重'
'姓名'
'性别'
'年龄'
'出生日期'
'联系电话'
'身份证'
'区域'
'联系地址'
'家长姓名'
'家长电话'
'饮食偏好'
'运动偏好'
'健康教育'
'既往史'
'家族史'
'是否早产'
'过敏史'
'矫正方式'
'矫正方式类型'
'矫正方式类型.1'
'矫正方式类型.2'
'右眼-裸眼视力'
'左眼-裸眼视力'
'右眼-矫正视力'
'左眼-矫正视力'
'右眼-角膜曲率K1'
'左眼-角膜曲率K1'
'右眼-角膜曲率K2'
'左眼-角膜曲率K2'
'右眼-眼轴'
'左眼-眼轴'
'右眼屈光-球镜'
'右眼屈光-柱镜'
'右眼屈光-轴位'
'左眼屈光-球镜'
'左眼屈光-柱镜'
'左眼屈光-轴位'
'右眼散瞳-球镜'
'右眼散瞳-柱镜'
'右眼散瞳-轴位'
'左眼散瞳-球镜'
'左眼散瞳-柱镜'
'左眼散瞳-轴位'
'右眼-前房深度'
'左眼-前房深度'
'其他情况'
'眼疲劳状况'
'右眼-干预-裸眼视力'
'左眼-干预-裸眼视力'
'右眼屈光-干预-球镜'
'右眼屈光-干预-柱镜'
'右眼屈光-干预-轴位'
'左眼屈光-干预-球镜'
'左眼屈光-干预-柱镜'
'左眼屈光-干预-轴位'
'右眼散瞳-干预-球镜'
'右眼散瞳-干预-柱镜'
'右眼散瞳-干预-轴位'
'左眼散瞳-干预-球镜'
'左眼散瞳-干预-柱镜'
'左眼散瞳-干预-轴位'
'第1次干预'
'第2次干预'
'第3次干预'
'第4次干预'
'第5次干预'
'第6次干预'
'第7次干预'
'第8次干预'
'第9次干预'
'第10次干预'
'第11次干预'
'第12次干预'
'第13次干预'
'第14次干预'
'第15次干预'
'第16次干预'