/**
 * 文件名称: comboQuery_report.js
 * 完整存储路径: frontend/static/js/comboQuery_report.js
 *
 * 功能说明:
 *   此模块为统计报表页面专用的组合查询功能实现。
 *   主要功能包括：
 *     1. 动态添加查询条件行，支持多种控件：
 *          - "text": 文本输入框
 *          - "number_range": 数值区间查询（生成最小值和最大值两个输入框）
 *          - "dropdown"/"multi-select": 生成复选框组，每个选项前添加复选框
 *          - "checkbox": 生成单个复选框
 *     2. 组合查询字段配置与独立模块保持一致，所有字段及其二级选项真实列出：
 *          - 注意：所有字段的 key 均使用后端统一识别的英文标识，显示时使用 label 显示中文名称。
 *     3. 每个查询条件行中新增角色选择下拉框（占2列），用于指定该条件的角色：
 *          - 角色选项包括："metric"（统计指标）、"group"（分组）、"filter"（筛选）
 *     4. 提供 getComboConditions() 函数，遍历所有条件行，返回 JSON 数组，每个条件对象包含：
 *          { role: <角色>, field: <字段名>, operator: <运算符>, value: <查询值> }
 *     5. 提供 clearConditions() 函数，清除所有查询条件行。
 *
 * 使用说明:
 *   在统计报表页面 (report.html) 中，必须包含：
 *     - 条件容器 (id="advancedQueryContainer") 用于插入查询条件行
 *     - 隐藏输入框 (id="comboConditions") 用于存储查询条件 JSON 字符串
 *     - “添加条件”按钮 (id="addConditionBtn") 和 “清除条件”按钮 (id="clearConditionsBtn")
 *
 * 注意:
 *   修改过程中必须保证不破坏原有功能，并且所有代码均符合我们的代码编写与输出标准。
 */

// 组合查询字段配置对象，所有 key 均使用后端统一英文标识，显示时使用 label 显示中文名称
const comboQueryConfig = {
  data_year: {
    label: "数据年份",
    type: "dropdown",
    options: ["2023", "2024", "2025", "2026", "2027", "2028"],
  },
  education_id: {
    label: "教育ID号",
    type: "text",
  },
  school: {
    label: "学校",
    type: "multi-select",
    options: ["华兴小学", "苏宁红军小学校", "师大附小清华小学"],
  },
  grade: {
    label: "年级",
    type: "multi-select",
    options: [
      "一年级",
      "二年级",
      "三年级",
      "四年级",
      "5年级",
      "六年级",
      "七年级",
      "八年级",
      "九年级",
    ],
  },
  class_name: {
    label: "班级",
    type: "dropdown",
    options: (function () {
      let arr = [];
      for (let i = 1; i <= 15; i++) {
        arr.push(i + "班");
      }
      return arr;
    })(),
  },
  name: {
    label: "姓名",
    type: "text",
  },
  gender: {
    label: "性别",
    type: "multi-select",
    options: ["男", "女"],
  },
  age: {
    label: "年龄",
    type: "number_range",
  },
  vision_level: {
    label: "视力等级",
    type: "multi-select",
    options: ["临床前期近视", "轻度近视", "中度近视"],
  },
  interv_vision_level: {
    label: "干预后视力等级",
    type: "multi-select",
    options: ["临床前期近视", "轻度近视", "中度近视"],
  },
  left_eye_naked: {
    label: "左眼-裸眼视力",
    type: "number_range",
  },
  right_eye_naked: {
    label: "右眼-裸眼视力",
    type: "number_range",
  },
  left_eye_naked_interv: {
    label: "左眼-干预-裸眼视力",
    type: "number_range",
  },
  right_eye_naked_interv: {
    label: "右眼-干预-裸眼视力",
    type: "number_range",
  },
  left_naked_change: {
    label: "左眼裸眼视力变化",
    type: "number_range",
  },
  right_naked_change: {
    label: "右眼裸眼视力变化",
    type: "number_range",
  },
  left_sphere: {
    label: "左眼屈光-球镜",
    type: "number_range",
  },
  right_sphere: {
    label: "右眼屈光-球镜",
    type: "number_range",
  },
  left_sphere_interv: {
    label: "左眼屈光-干预-球镜",
    type: "number_range",
  },
  right_sphere_interv: {
    label: "右眼屈光-干预-球镜",
    type: "number_range",
  },
  left_sphere_change: {
    label: "左眼屈光-球镜变化",
    type: "number_range",
  },
  right_sphere_change: {
    label: "右眼屈光-球镜变化",
    type: "number_range",
  },
  left_cylinder: {
    label: "左眼屈光-柱镜",
    type: "number_range",
  },
  right_cylinder: {
    label: "右眼屈光-柱镜",
    type: "number_range",
  },
  left_cylinder_interv: {
    label: "左眼屈光-干预-柱镜",
    type: "number_range",
  },
  right_cylinder_interv: {
    label: "右眼屈光-干预-柱镜",
    type: "number_range",
  },
  left_cylinder_change: {
    label: "左眼屈光-柱镜变化",
    type: "number_range",
  },
  right_cylinder_change: {
    label: "右眼屈光-柱镜变化",
    type: "number_range",
  },
  left_axis: {
    label: "左眼屈光-轴位",
    type: "number_range",
  },
  right_axis: {
    label: "右眼屈光-轴位",
    type: "number_range",
  },
  left_axis_interv: {
    label: "左眼屈光-干预-轴位",
    type: "number_range",
  },
  right_axis_interv: {
    label: "右眼屈光-干预-轴位",
    type: "number_range",
  },
  left_axis_change: {
    label: "左眼屈光-轴位变化",
    type: "number_range",
  },
  right_axis_change: {
    label: "右眼屈光-轴位变化",
    type: "number_range",
  },
  left_interv_effect: {
    label: "左眼视力干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"],
  },
  right_interv_effect: {
    label: "右眼视力干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"],
  },
  left_sphere_effect: {
    label: "左眼球镜干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"],
  },
  right_sphere_effect: {
    label: "右眼球镜干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"],
  },
  left_cylinder_effect: {
    label: "左眼柱镜干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"],
  },
  right_cylinder_effect: {
    label: "右眼柱镜干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"],
  },
  left_axis_effect: {
    label: "左眼轴位干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"],
  },
  right_axis_effect: {
    label: "右眼轴位干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"],
  },
  guasha: {
    label: "刮痧",
    type: "multi-select",
    options: ["是", "否"],
  },
  aigiu: {
    label: "艾灸",
    type: "multi-select",
    options: ["是", "否"],
  },
  zhongyao_xunzheng: {
    label: "中药熏蒸",
    type: "multi-select",
    options: ["是", "否"],
  },
  rejiu_training: {
    label: "热灸训练",
    type: "multi-select",
    options: ["是", "否"],
  },
  xuewei_tiefu: {
    label: "穴位贴敷",
    type: "multi-select",
    options: ["是", "否"],
  },
  reci_pulse: {
    label: "热磁脉冲",
    type: "multi-select",
    options: ["是", "否"],
  },
  baoguan: {
    label: "拔罐",
    type: "multi-select",
    options: ["是", "否"],
  },
  frame_glasses: {
    label: "框架眼镜",
    type: "multi-select",
    options: ["是", "否"],
  },
  contact_lenses: {
    label: "隐形眼镜",
    type: "multi-select",
    options: ["是", "否"],
  },
  night_orthokeratology: {
    label: "夜戴角膜塑型镜",
    type: "multi-select",
    options: ["是", "否"],
  },
};

const BOOLEAN_FIELDS = ['guasha', '刮痧'];  // 根据实际布尔字段列表修改


// 固定角色选项，用于每个查询条件行中的角色选择下拉框
const roleOptions = [
  { value: "metric", label: "统计指标" },
  { value: "group", label: "分组" },
  { value: "filter", label: "筛选" },
];

/**
 * 初始化组合查询模块，绑定“添加条件”和“清除条件”按钮事件
 */
function initComboQuery() {
  const addBtn = document.getElementById("addConditionBtn");
  if (addBtn) {
    addBtn.addEventListener("click", addConditionRow);
  }
  const clearBtn = document.getElementById("clearConditionsBtn");
  if (clearBtn) {
    clearBtn.addEventListener("click", clearConditions);
  }
}

/**
 * 动态添加一条查询条件行
 * 每行包括：
 *  - 角色选择下拉框（占2列）：选择“统计指标”、“分组”或“筛选”
 *  - 字段下拉框（占3列）：基于 comboQueryConfig 生成所有字段选项
 *  - 运算符下拉框（占2列）：固定选项
 *  - 值输入区域（占3列）：根据字段类型生成对应控件：
 *       * "text": 文本输入框
 *       * "number_range": 生成最小值和最大值输入框
 *       * "dropdown"/"multi-select": 生成复选框组（每个选项前添加复选框）
 *       * "checkbox": 生成单个复选框
 *  - 删除按钮（占2列）：删除当前条件行
 */
function addConditionRow() {
  const conditionRow = document.createElement("div");
  conditionRow.className = "condition-row row g-1 mb-1";

  // 角色选择下拉框
  const roleDiv = document.createElement("div");
  roleDiv.className = "col-md-2";
  const roleSelect = document.createElement("select");
  roleSelect.className = "form-select form-select-sm condition-role";
  const defaultRoleOption = document.createElement("option");
  defaultRoleOption.value = "";
  defaultRoleOption.textContent = "选择角色";
  roleSelect.appendChild(defaultRoleOption);
  roleOptions.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    roleSelect.appendChild(option);
  });
  roleDiv.appendChild(roleSelect);

  // 字段下拉框
  const fieldDiv = document.createElement("div");
  fieldDiv.className = "col-md-3";
  const fieldSelect = document.createElement("select");
  fieldSelect.className = "form-select form-select-sm condition-field";
  const defaultFieldOption = document.createElement("option");
  defaultFieldOption.value = "";
  defaultFieldOption.textContent = "选择字段";
  fieldSelect.appendChild(defaultFieldOption);
  Object.keys(comboQueryConfig).forEach((key) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = comboQueryConfig[key].label;
    fieldSelect.appendChild(option);
  });
  fieldDiv.appendChild(fieldSelect);

  // 运算符下拉框
  const operatorDiv = document.createElement("div");
  operatorDiv.className = "col-md-2";
  const operatorSelect = document.createElement("select");
  operatorSelect.className = "form-select form-select-sm condition-operator";
  const operators = [
    { value: "like", label: "like" },
    { value: "=", label: "=" },
    { value: "!=", label: "!=" },
    { value: ">", label: ">" },
    { value: "<", label: "<" },
    { value: ">=", label: ">=" },
    { value: "<=", label: "<=" },
  ];
  operators.forEach((op) => {
    const opOption = document.createElement("option");
    opOption.value = op.value;
    opOption.textContent = op.label;
    operatorSelect.appendChild(opOption);
  });
  operatorDiv.appendChild(operatorSelect);

  // 值输入区域
  const valueDiv = document.createElement("div");
  valueDiv.className = "col-md-3";
  let valueInput = document.createElement("input");
  valueInput.type = "text";
  valueInput.className = "form-control form-control-sm condition-value";
  valueInput.placeholder = "输入查询值";
  valueDiv.appendChild(valueInput);

  // 删除按钮
  const deleteDiv = document.createElement("div");
  deleteDiv.className = "col-md-2";
  const deleteBtn = document.createElement("button");
  deleteBtn.type = "button";
  deleteBtn.className = "btn btn-danger btn-sm condition-delete";
  deleteBtn.textContent = "×";
  deleteBtn.addEventListener("click", function () {
    conditionRow.remove();
  });
  deleteDiv.appendChild(deleteBtn);

  // 拼接条件行
  conditionRow.appendChild(roleDiv);
  conditionRow.appendChild(fieldDiv);
  conditionRow.appendChild(operatorDiv);
  conditionRow.appendChild(valueDiv);
  conditionRow.appendChild(deleteDiv);

  // 根据所选字段更新值输入区域
  fieldSelect.addEventListener("change", function () {
    const selectedField = fieldSelect.value;
    valueDiv.innerHTML = "";
    if (!selectedField) {
      valueInput = document.createElement("input");
      valueInput.type = "text";
      valueInput.className = "form-control form-control-sm condition-value";
      valueInput.placeholder = "输入查询值";
      valueDiv.appendChild(valueInput);
      return;
    }
    const config = comboQueryConfig[selectedField];
    if (!config) {
      valueInput = document.createElement("input");
      valueInput.type = "text";
      valueInput.className = "form-control form-control-sm condition-value";
      valueInput.placeholder = "输入查询值";
      valueDiv.appendChild(valueInput);
      return;
    }
    switch (config.type) {
      case "text":
        valueInput = document.createElement("input");
        valueInput.type = "text";
        valueInput.className = "form-control form-control-sm condition-value";
        valueInput.placeholder = "输入查询值";
        valueDiv.appendChild(valueInput);
        break;
      case "number_range":
        const minInput = document.createElement("input");
        minInput.type = "number";
        minInput.className = "form-control form-control-sm condition-value-min";
        minInput.placeholder = "最小值";
        const maxInput = document.createElement("input");
        maxInput.type = "number";
        maxInput.className = "form-control form-control-sm condition-value-max";
        maxInput.placeholder = "最大值";
        const rangeDiv = document.createElement("div");
        rangeDiv.className = "d-flex gap-1";
        rangeDiv.appendChild(minInput);
        rangeDiv.appendChild(maxInput);
        valueDiv.appendChild(rangeDiv);
        break;
      case "dropdown":
      case "multi-select":
        const multiDiv = document.createElement("div");
        multiDiv.className = "d-flex flex-wrap gap-1";
        config.options.forEach((opt) => {
          const label = document.createElement("label");
          label.className = "form-check form-check-inline";
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.className = "form-check-input condition-value-multi";
          checkbox.value = opt;
          label.appendChild(checkbox);
          const span = document.createElement("span");
          span.className = "form-check-label";
          span.textContent = opt;
          label.appendChild(span);
          multiDiv.appendChild(label);
        });
        valueDiv.appendChild(multiDiv);
        break;
      case "checkbox":
        const singleCheckboxDiv = document.createElement("div");
        singleCheckboxDiv.className = "form-check";
        const singleCheckbox = document.createElement("input");
        singleCheckbox.type = "checkbox";
        singleCheckbox.className = "form-check-input condition-value-checkbox";
        singleCheckboxDiv.appendChild(singleCheckbox);
        const checkboxLabel = document.createElement("label");
        checkboxLabel.className = "form-check-label";
        checkboxLabel.textContent = "选中";
        singleCheckboxDiv.appendChild(checkboxLabel);
        valueDiv.appendChild(singleCheckboxDiv);
        break;
      default:
        valueInput = document.createElement("input");
        valueInput.type = "text";
        valueInput.className = "form-control form-control-sm condition-value";
        valueInput.placeholder = "输入查询值";
        valueDiv.appendChild(valueInput);
        break;
    }
  });

  const container = document.getElementById("advancedQueryContainer");
  container.appendChild(conditionRow);
}

/**
 * 遍历所有查询条件行，收集条件数据并返回数组
 * 每个条件对象格式：
 * {
 *   role: <角色> ("metric", "group", "filter"),
 *   field: <字段名>,
 *   operator: <运算符>,
 *   value: <查询值>  // "number_range" 为 {min: "", max: ""}；"multi-select" 为数组；"checkbox" 为布尔值
 * }
 */
function getComboConditions() {
  const conditionRows = document.querySelectorAll(".condition-row");
  const conditions = [];
  conditionRows.forEach((row) => {
    const roleEl = row.querySelector(".condition-role");
    const fieldEl = row.querySelector(".condition-field");
    const operatorEl = row.querySelector(".condition-operator");
    let value;
    const role = roleEl ? roleEl.value.trim() : "";
    const field = fieldEl ? fieldEl.value.trim() : "";
    const operator = operatorEl ? operatorEl.value.trim() : "";
    if (!field || !operator) return;
    const config = comboQueryConfig[field];
    // === 插入位置开始 ===
    if (BOOLEAN_FIELDS.includes(field)) {
      // 默认使用 `=` 运算符
      value = row.querySelector('.condition-value') ? row.querySelector('.condition-value').value.trim() : "";
      operator = "=";  // 设定运算符为 "="
    }
    // === 插入位置结束 ===

    // 打印调试日志，查看传递的字段、运算符和值
    console.log(`Field: ${field}, Operator: ${operator}, Value: ${value}`);

    if (config) {
      switch (config.type) {
        case "number_range":
          const minEl = row.querySelector(".condition-value-min");
          const maxEl = row.querySelector(".condition-value-max");
          value = {
            min: minEl ? minEl.value.trim() : "",
            max: maxEl ? maxEl.value.trim() : "",
          };
          break;
        case "multi-select":
          const checkboxes = row.querySelectorAll(".condition-value-multi");
          value = [];
          checkboxes.forEach((cb) => {
            // 调试输出：打印每个复选框的状态
            console.log(
              "Multi-select - value:",
              cb.value,
              "checked:",
              cb.checked
            );
            if (cb.checked) {
              value.push(cb.value);
            }
          });
          break;
        case "checkbox":
          const checkboxEl = row.querySelector(".condition-value-checkbox");
          value = checkboxEl ? checkboxEl.checked : false;
          break;
        default:
          const valEl = row.querySelector(".condition-value");
          value = valEl ? valEl.value.trim() : "";
          break;
      }
    } else {
      const valEl = row.querySelector(".condition-value");
      value = valEl ? valEl.value.trim() : "";
    }
    conditions.push({
      role: role,
      field: field,
      operator: operator,
      value: value,
    });
  });
  return conditions;
}

/**
 * 清除所有查询条件行
 */
function clearConditions() {
  const container = document.getElementById("advancedQueryContainer");
  container.innerHTML = "";
}

document.addEventListener("DOMContentLoaded", function () {
  initComboQuery();
});

window.getComboConditions = getComboConditions;
window.clearConditions = clearConditions;
