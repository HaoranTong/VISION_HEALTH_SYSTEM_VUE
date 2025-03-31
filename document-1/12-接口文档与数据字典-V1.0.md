下面是两个文档的第一版，分别是【接口文档】和【数据字典】。请仔细阅读，确认是否满足要求。如果有任何修改意见，请指出，我们再进一步完善。

------

# 接口文档 - Version 1.0

**文件名称：** 接口文档
 **保存路径：** 文档/接口文档.md
 **功能说明：**
 本接口文档详细描述了近视预防干预系统的各个 RESTful API 接口，包括数据导入、统计分析、数据查询、侧边栏菜单、学生录入等接口的 URL、请求方法、参数说明、响应格式及示例。
 **使用说明：**
 开发、调试、维护人员参考本文档对接前后端接口。接口文档将随着系统更新持续维护，版本迭代说明会同步更新在文档内。

------

## 1. 数据导入接口

**接口名称：** 学生数据导入接口
 **URL：** `/api/students/import`
 **请求方式：** POST
 **请求内容类型：** `multipart/form-data`

### 请求参数

- file
  - 描述：上传的 Excel (.xlsx) 或 CSV (.csv) 文件
  - 类型：文件
- data_year
  - 描述：数据年份（4位字符串，如 "2023"）
  - 类型：字符串

### 响应示例

```json
{
  "message": "上传成功"
}
```

### 接口说明

该接口负责：

- 保存上传文件到临时目录；
- 使用 Pandas 解析文件数据；
- 对每行数据进行必填字段和格式校验；
- 根据 `education_id` 与 `data_year` 的组合，判断是新增记录还是部分更新；
- 合格数据写入 `Student`（学生基本信息表）和 `StudentExtension`（学生扩展信息表）；
- 失败记录生成“上传失败记录表”并提供下载链接。

------

## 2. 统计分析接口

该模块包含统计报表数据和图表数据两个接口，均支持固定查询条件、组合查询条件、分页等功能。

### 2.1 统计报表数据接口

**接口名称：** 统计报表数据接口
 **URL：** `/api/analysis/report`
 **请求方式：** GET

### 请求参数

- stat_time

   (可选)

  - 描述：统计时间（例如 "2023"），用于过滤数据年份
  - 类型：字符串

- template

   (可选)

  - 描述：预设模版名称，如 "template1"（按年龄段）或 "template2"（按性别）。当传入时，使用固定模版逻辑；否则采用自由组合查询模式。
  - 类型：字符串

- advanced_conditions

   (可选)

  - 描述：组合查询条件，格式为 JSON 字符串，数组中每个对象包括：
    - **role**：角色（"metric"、"group"、"filter"）
    - **field**：字段名称
    - **operator**：运算符（如 "="、"in" 等）
    - **value**：查询值（对于多选为数组）
  - 类型：字符串

- page

   (可选)

  - 描述：页码，默认 1
  - 类型：整数

- per_page

   (可选)

  - 描述：每页记录数，默认 10
  - 类型：整数

### 响应示例

```json
{
  "tableName": "2023-学生视力情况统计表-预防干预前(按性别)",
  "header": [
    "性别",
    "临床前期近视(人数)",
    "临床前期近视(占比)",
    "轻度近视(人数)",
    "轻度近视(占比)",
    "中度近视(人数)",
    "中度近视(占比)",
    "视力不良(人数)",
    "视力不良(占比)",
    "统计人数"
  ],
  "rows": [
    {
      "row_name": "男",
      "pre_clinic_count": 18,
      "pre_clinic_ratio": 72.0,
      "mild_count": 7,
      "mild_ratio": 28.0,
      "moderate_count": 0,
      "moderate_ratio": 0.0,
      "bad_vision_count": 25,
      "bad_vision_ratio": 100.0,
      "total_count": 25
    },
    {
      "row_name": "女",
      "pre_clinic_count": 12,
      "pre_clinic_ratio": 48.0,
      "mild_count": 10,
      "mild_ratio": 40.0,
      "moderate_count": 3,
      "moderate_ratio": 12.0,
      "bad_vision_count": 25,
      "bad_vision_ratio": 100.0,
      "total_count": 25
    },
    {
      "row_name": "合计",
      "pre_clinic_count": 30,
      "pre_clinic_ratio": "",
      "mild_count": 17,
      "mild_ratio": "",
      "moderate_count": 3,
      "moderate_ratio": "",
      "bad_vision_count": 50,
      "bad_vision_ratio": "",
      "total_count": 50
    }
  ],
  "total": 3
}
```

### 接口说明

- 当固定模板参数为空时，系统采用自由组合查询模式，使用 advanced_conditions 中指定的分组字段（如 "gender"）进行分组统计。
- 每个分组的统计数据（人数和占比）均基于该分组内部数据计算；合计行为所有分组的总和。
- 注意：统计数据中的字段（如临床前期近视、轻度近视、等）均依赖于数据库中存储的字符串数据，需确保条件匹配时使用正确的运算符（建议使用 `in` 代替 `like`，但请根据实际情况调整）。

------

### 2.2 图表数据接口

**接口名称：** 图表数据接口
 **URL：** `/api/analysis/chart`
 **请求方式：** GET

### 请求参数

参数与统计报表接口相似，包括：

- **stat_time**、**advanced_conditions**、**page**、**per_page** 等。

另外可传入：

- **group_by**：指定分组字段（如 "gender"、"school" 等）
- **metric**：指定统计指标字段（如 "left_interv_effect" 等）

### 响应示例

返回数据格式适合 Chart.js 使用，如：

```json
{
  "labels": ["男", "女"],
  "datasets": [
    {
      "label": "临床前期近视(人数)",
      "data": [18, 12],
      "backgroundColor": ["rgba(75, 192, 192, 0.5)", "rgba(153, 102, 255, 0.5)"]
    }
  ]
}
```

### 接口说明

- 该接口基于组合查询条件和分组信息，返回适用于图表展示的统计数据，支持多种图表类型。

------

## 3. 数据查询接口

### 3.1 学生数据查询接口

**接口名称：** 学生数据查询接口
 **URL：** `/api/students/query`
 **请求方式：** GET

### 请求参数

- 固定查询条件：`education_id`, `school`, `class_name`, `name`, `gender`, `id_card`, `data_year`, `grade` 等。
- **advanced_conditions**：组合查询条件（JSON 字符串）。
- **page** 和 **per_page**：分页参数。

### 响应示例

```json
{
  "students": [
    {
      "id": 1,
      "education_id": "E001",
      "school": "华兴小学",
      "class_name": "1班",
      "name": "张三",
      "gender": "男",
      "birthday": "2010-05-10",
      "phone": "13800138000",
      "id_card": "123456789012345678",
      "region": "XX区",
      "contact_address": "XX街道",
      "parent_name": "张爸爸",
      "parent_phone": "13900139000",
      "grade": "一年级",
      "data_year": "2023",
      "age": 13,
      // ...其他字段
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 10
}
```

### 接口说明

- 查询时同时关联 `Student` 与 `StudentExtension` 表，支持固定和自由组合查询条件；
- 返回分页后的学生数据。

------

### 3.2 学生数据导出接口

**接口名称：** 学生数据导出接口
 **URL：** `/api/students/export`
 **请求方式：** GET

### 请求参数

- 与查询接口一致（固定查询条件、advanced_conditions、分页参数）。
- 可选参数 **columns**：指定导出的列，多个字段以逗号分隔。

### 响应说明

- 返回一个 Excel 文件供下载，其中包含符合查询条件的所有数据。

------

## 4. 侧边栏菜单接口

**接口名称：** 侧边栏菜单数据接口
 **URL：** `/api/menu`
 **请求方式：** GET

### 响应示例

```json
[
  {
    "title": "首页",
    "link": "/",
    "icon": "bi-house-door",
    "sub_menu": []
  },
  {
    "title": "数据管理",
    "link": "#",
    "icon": "bi-folder",
    "sub_menu": [
      {"title": "数据导入", "link": "/import", "icon": "bi-upload"},
      {"title": "数据修改", "link": "modify", "icon": "bi-pencil"}
    ]
  }
  // 其他菜单项……
]
```

### 接口说明

- 返回一个 JSON 数组，包含所有侧边栏菜单项及其二级菜单，用于前端动态生成侧边栏。

------

## 5. 学生数据录入接口

**接口名称：** 学生数据录入接口
 **URL：** `/api/student/add`
 **请求方式：** POST
 **请求内容类型：** application/json

### 请求参数

- 必填字段：`education_id`, `name`, `vision_left`, `vision_right` 等（根据实际需求可扩展）。
- 其他可选字段也可提供。

### 响应示例

```json
{
  "message": "录入成功",
  "id": 5
}
```

### 接口说明

- 校验请求数据中必填字段是否存在；
- 若校验通过，将数据存入 `Student` 表（部分字段）；
- 返回成功信息和新生成的学生 ID。

------

## 6. 错误处理说明

- 所有接口出错时均返回 JSON 格式的错误响应，如：

  ```json
  { "error": "具体错误信息" }
  ```

------

## 7. 版本管理

- 本接口文档为版本 1.0，后续更新将记录版本变更说明。

------

# 数据字典 - Version 1.0

**文件名称：** 数据字典
 **保存路径：** 文档/数据字典.md
 **功能说明：**
 本数据字典详细描述了近视预防干预系统的数据库模型，包括 `Student`（学生基本信息表）和 `StudentExtension`（学生扩展信息表）两个主要数据表。
 **使用说明：**
 开发、测试和维护人员参照本数据字典理解数据库中各字段的意义、数据类型和约束条件。后续数据库模型变更时，数据字典也会同步更新。

------

## 1. 表：students（学生基本信息表）

| 字段名称            | 数据类型    | 约束条件         | 说明                       |
| ------------------- | ----------- | ---------------- | -------------------------- |
| **id**              | Integer     | 主键，自增       | 学生记录唯一标识           |
| **education_id**    | String(20)  | 唯一，不允许为空 | 教育ID号，用于唯一标识学生 |
| **school**          | String(50)  | 可为空           | 学校名称                   |
| **class_name**      | String(10)  | 可为空           | 班级名称                   |
| **name**            | String(50)  | 可为空           | 学生姓名                   |
| **gender**          | String(10)  | 可为空           | 学生性别                   |
| **birthday**        | Date        | 可为空           | 出生日期                   |
| **phone**           | String(15)  | 可为空           | 联系电话                   |
| **id_card**         | String(18)  | 可为空           | 身份证号码                 |
| **region**          | String(50)  | 可为空           | 所在区域或行政区划         |
| **contact_address** | String(100) | 可为空           | 详细联系地址               |
| **parent_name**     | String(50)  | 可为空           | 家长姓名                   |
| **parent_phone**    | String(15)  | 可为空           | 家长联系电话               |

**关系：**

- 与 `StudentExtension` 表建立一对一关系（每个学生对应一条扩展信息记录）。

------

## 2. 表：student_extensions（学生扩展信息表）

| 字段名称                          | 数据类型    | 约束条件                           | 说明                                            |
| --------------------------------- | ----------- | ---------------------------------- | ----------------------------------------------- |
| **id**                            | Integer     | 主键，自增                         | 扩展记录唯一标识                                |
| **student_id**                    | Integer     | 外键，关联 students.id, 不允许为空 | 关联的学生 ID                                   |
| **data_year**                     | String(4)   | 不允许为空                         | 数据年份（如 "2023"）                           |
| **grade**                         | String(10)  | 可为空                             | 学生年级                                        |
| **age**                           | Integer     | 可为空                             | 年龄                                            |
| **height**                        | Float       | 可为空                             | 身高（单位：厘米）                              |
| **weight**                        | Float       | 可为空                             | 体重（单位：公斤）                              |
| **diet_preference**               | String(50)  | 可为空                             | 饮食偏好                                        |
| **exercise_preference**           | String(50)  | 可为空                             | 运动偏好                                        |
| **health_education**              | String(200) | 可为空                             | 健康教育情况                                    |
| **past_history**                  | String(200) | 可为空                             | 既往病史                                        |
| **family_history**                | String(200) | 可为空                             | 家族病史                                        |
| **premature**                     | String(10)  | 可为空                             | 是否早产                                        |
| **allergy**                       | String(200) | 可为空                             | 过敏史                                          |
| **right_eye_naked**               | Float       | 可为空                             | 右眼裸眼视力                                    |
| **left_eye_naked**                | Float       | 可为空                             | 左眼裸眼视力                                    |
| **right_eye_corrected**           | Float       | 可为空                             | 右眼矫正视力                                    |
| **left_eye_corrected**            | Float       | 可为空                             | 左眼矫正视力                                    |
| **right_keratometry_K1**          | Float       | 可为空                             | 右眼角膜曲率K1                                  |
| **left_keratometry_K1**           | Float       | 可为空                             | 左眼角膜曲率K1                                  |
| **right_keratometry_K2**          | Float       | 可为空                             | 右眼角膜曲率K2                                  |
| **left_keratometry_K2**           | Float       | 可为空                             | 左眼角膜曲率K2                                  |
| **right_axial_length**            | Float       | 可为空                             | 右眼眼轴长度                                    |
| **left_axial_length**             | Float       | 可为空                             | 左眼眼轴长度                                    |
| **right_sphere**                  | Float       | 可为空                             | 右眼屈光-球镜                                   |
| **right_cylinder**                | Float       | 可为空                             | 右眼屈光-柱镜                                   |
| **right_axis**                    | Float       | 可为空                             | 右眼屈光-轴位                                   |
| **left_sphere**                   | Float       | 可为空                             | 左眼屈光-球镜                                   |
| **left_cylinder**                 | Float       | 可为空                             | 左眼屈光-柱镜                                   |
| **left_axis**                     | Float       | 可为空                             | 左眼屈光-轴位                                   |
| **right_dilated_sphere**          | Float       | 可为空                             | 右眼散瞳-球镜                                   |
| **right_dilated_cylinder**        | Float       | 可为空                             | 右眼散瞳-柱镜                                   |
| **right_dilated_axis**            | Float       | 可为空                             | 右眼散瞳-轴位                                   |
| **left_dilated_sphere**           | Float       | 可为空                             | 左眼散瞳-球镜                                   |
| **left_dilated_cylinder**         | Float       | 可为空                             | 左眼散瞳-柱镜                                   |
| **left_dilated_axis**             | Float       | 可为空                             | 左眼散瞳-轴位                                   |
| **vision_level**                  | String(20)  | 可为空                             | 干预前视力等级（根据右眼/左眼球镜、年龄等判断） |
| **right_anterior_depth**          | Float       | 可为空                             | 右眼前房深度                                    |
| **left_anterior_depth**           | Float       | 可为空                             | 左眼前房深度                                    |
| **other_info**                    | String(200) | 可为空                             | 其他情况说明                                    |
| **eye_fatigue**                   | String(100) | 可为空                             | 眼疲劳状况                                      |
| **frame_glasses**                 | Boolean     | 可为空                             | 是否使用框架眼镜                                |
| **contact_lenses**                | Boolean     | 可为空                             | 是否使用隐形眼镜                                |
| **night_orthokeratology**         | Boolean     | 可为空                             | 是否使用夜戴角膜塑型镜                          |
| **guasha**                        | Boolean     | 可为空                             | 是否进行刮痧治疗                                |
| **aigiu**                         | Boolean     | 可为空                             | 是否进行艾灸治疗                                |
| **zhongyao_xunzheng**             | Boolean     | 可为空                             | 是否进行中药熏蒸                                |
| **rejiu_training**                | Boolean     | 可为空                             | 是否进行热灸训练                                |
| **xuewei_tiefu**                  | Boolean     | 可为空                             | 是否进行穴位贴敷                                |
| **reci_pulse**                    | Boolean     | 可为空                             | 是否使用热磁脉冲                                |
| **baoguan**                       | Boolean     | 可为空                             | 是否进行拔罐治疗                                |
| **right_eye_naked_interv**        | Float       | 可为空                             | 干预后右眼裸眼视力                              |
| **left_eye_naked_interv**         | Float       | 可为空                             | 干预后左眼裸眼视力                              |
| **right_sphere_interv**           | Float       | 可为空                             | 干预后右眼屈光-球镜                             |
| **right_cylinder_interv**         | Float       | 可为空                             | 干预后右眼屈光-柱镜                             |
| **right_axis_interv**             | Float       | 可为空                             | 干预后右眼屈光-轴位                             |
| **left_sphere_interv**            | Float       | 可为空                             | 干预后左眼屈光-球镜                             |
| **left_cylinder_interv**          | Float       | 可为空                             | 干预后左眼屈光-柱镜                             |
| **left_axis_interv**              | Float       | 可为空                             | 干预后左眼屈光-轴位                             |
| **right_dilated_sphere_interv**   | Float       | 可为空                             | 干预后右眼散瞳-球镜                             |
| **right_dilated_cylinder_interv** | Float       | 可为空                             | 干预后右眼散瞳-柱镜                             |
| **right_dilated_axis_interv**     | Float       | 可为空                             | 干预后右眼散瞳-轴位                             |
| **left_dilated_sphere_interv**    | Float       | 可为空                             | 干预后左眼散瞳-球镜                             |
| **left_dilated_cylinder_interv**  | Float       | 可为空                             | 干预后左眼散瞳-柱镜                             |
| **left_dilated_axis_interv**      | Float       | 可为空                             | 干预后左眼散瞳-轴位                             |
| **interv_vision_level**           | String(20)  | 可为空                             | 干预后视力等级                                  |
| **left_naked_change**             | Float       | 可为空                             | 左眼裸眼视力变化                                |
| **right_naked_change**            | Float       | 可为空                             | 右眼裸眼视力变化                                |
| **left_sphere_change**            | Float       | 可为空                             | 左眼屈光-球镜变化                               |
| **right_sphere_change**           | Float       | 可为空                             | 右眼屈光-球镜变化                               |
| **left_cylinder_change**          | Float       | 可为空                             | 左眼屈光-柱镜变化                               |
| **right_cylinder_change**         | Float       | 可为空                             | 右眼屈光-柱镜变化                               |
| **left_axis_change**              | Float       | 可为空                             | 左眼屈光-轴位变化                               |
| **right_axis_change**             | Float       | 可为空                             | 右眼屈光-轴位变化                               |
| **left_interv_effect**            | String(20)  | 可为空                             | 左眼视力干预效果                                |
| **right_interv_effect**           | String(20)  | 可为空                             | 右眼视力干预效果                                |
| **left_sphere_effect**            | String(20)  | 可为空                             | 左眼球镜干预效果                                |
| **right_sphere_effect**           | String(20)  | 可为空                             | 右眼球镜干预效果                                |
| **left_cylinder_effect**          | String(20)  | 可为空                             | 左眼柱镜干预效果                                |
| **right_cylinder_effect**         | String(20)  | 可为空                             | 右眼柱镜干预效果                                |
| **left_axis_effect**              | String(20)  | 可为空                             | 左眼轴位干预效果                                |
| **right_axis_effect**             | String(20)  | 可为空                             | 右眼轴位干预效果                                |
| **interv1** 至 **interv16**       | DateTime    | 可为空                             | 第1次至第16次干预的时间记录                     |

**额外说明：**

- 表中复合唯一约束：`student_id` 与 `data_year` 的组合必须唯一，确保同一学生在同一年只有一条扩展记录。
- 本数据字典中的字段名称、数据类型及说明均与数据库模型代码一致，如有修改需同时更新此文档。

------

请确认以上两份文档是否满足您的需求，或是否需要进一步修改和补充。