#!/usr/bin/env node
/**
 * 文件名称: comboQuery.js
 * 完整存储路径: frontend/static/js/comboQuery.js
 * 功能说明:
 *   封装组合查询功能模块，提供以下功能：
 *     - 初始化组合查询区域（绑定“添加条件”、“清除条件”、“查询”按钮事件）
 *     - 动态添加查询条件行，根据配置生成相应控件：
 *         * "text": 文本输入框
 *         * "dropdown": 下拉选择框（选项由 options 数组提供）
 *         * "number_range": 生成两个输入框，用于最小值和最大值输入（区间查询）
 *         * "multi-select": 生成一组复选框（用于干预效果），选项固定为 ["上升", "维持", "下降"]
 *         * "checkbox": 直接生成单个复选框（用于那些只需选中与否的项目）
 *     - 提供接口 getComboConditions() 收集所有条件行数据，返回数组（每项对象包括 field、operator、value 等）
 *     - 提供清除所有条件行接口 clearConditions()
 *
 * 使用说明:
 *   页面中必须存在：
 *     - 条件容器（id="advancedQueryContainer"）用于动态插入条件行
 *     - 隐藏输入框（id="comboConditions"）用于存储组合查询条件的 JSON 字符串
 *     - 操作按钮，其 ID 分别为 "addConditionBtn"、"clearConditionsBtn"、"comboSearchBtn"
 *   在 DOMContentLoaded 后调用 initComboQuery() 初始化该模块。
 */

"use strict";

/* ---------------------------------------------------------
   静态配置：所有字段及其查询控件类型、显示标签和选项
   type:
     - "text": 文本输入
     - "dropdown": 下拉选择框
     - "number_range": 数值区间查询（生成两个输入框）
     - "multi-select": 多选复选框
     - "checkbox": 单个复选框（用于那些只需选中与否的项目）
---------------------------------------------------------- */
const comboQueryConfig = {
  "data_year": {
    label: "数据年份",
    type: "dropdown",
    options: ["2023", "2024", "2025", "2026", "2027", "2028"]
  },
  "education_id": {
    label: "教育ID号",
    type: "text"
  },
  "school": {
    label: "学校",
    type: "dropdown",
    options: ["华兴小学", "苏宁红军小学", "师大附小清华小学"]
  },
  "grade": {
    label: "年级",
    type: "dropdown",
    options: ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级", "七年级", "八年级", "九年级"]
  },
  "class_name": {
    label: "班级",
    type: "dropdown",
    options: (function () {
      let arr = [];
      for (let i = 1; i <= 15; i++) {
        arr.push(i + "班");
      }
      return arr;
    })()
  },
  "name": {
    label: "姓名",
    type: "text"
  },
  "gender": {
    label: "性别",
    type: "dropdown",
    options: ["男", "女"]
  },
  "age": {
    label: "年龄",
    type: "number_range"
  },
  "vision_level": {
    label: "视力等级",
    type: "dropdown",
    options: ["临床前期近视", "轻度近视", "中度近视"]
  },
  "interv_vision_level": {
    label: "干预后视力等级",
    type: "dropdown",
    options: ["临床前期近视", "轻度近视", "中度近视"]
  },
  "left_eye_naked": {
    label: "左眼-裸眼视力",
    type: "number_range"
  },
  "right_eye_naked": {
    label: "右眼-裸眼视力",
    type: "number_range"
  },
  "left_eye_naked_interv": {
    label: "左眼-干预-裸眼视力",
    type: "number_range"
  },
  "right_eye_naked_interv": {
    label: "右眼-干预-裸眼视力",
    type: "number_range"
  },
  "left_naked_change": {
    label: "左眼裸眼视力变化",
    type: "number_range"
  },
  "right_naked_change": {
    label: "右眼裸眼视力变化",
    type: "number_range"
  },
  "left_sphere_change": {
    label: "左眼屈光-球镜变化",
    type: "number_range"
  },
  "right_sphere_change": {
    label: "右眼屈光-球镜变化",
    type: "number_range"
  },
  "left_cylinder_change": {
    label: "左眼屈光-柱镜变化",
    type: "number_range"
  },
  "right_cylinder_change": {
    label: "右眼屈光-柱镜变化",
    type: "number_range"
  },
  "left_axis_change": {
    label: "左眼屈光-轴位变化",
    type: "number_range"
  },
  "right_axis_change": {
    label: "右眼屈光-轴位变化",
    type: "number_range"
  },
  "left_interv_effect": {
    label: "左眼视力干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"]
  },
  "right_interv_effect": {
    label: "右眼视力干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"]
  },
  "left_sphere_effect": {
    label: "左眼球镜干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"]
  },
  "right_sphere_effect": {
    label: "右眼球镜干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"]
  },
  "left_cylinder_effect": {
    label: "左眼柱镜干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"]
  },
  "right_cylinder_effect": {
    label: "右眼柱镜干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"]
  },
  "left_axis_effect": {
    label: "左眼轴位干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"]
  },
  "right_axis_effect": {
    label: "右眼轴位干预效果",
    type: "multi-select",
    options: ["上升", "维持", "下降"]
  },
  "left_eye_corrected": {
    label: "左眼-矫正视力",
    type: "number_range"
  },
  "right_eye_corrected": {
    label: "右眼-矫正视力",
    type: "number_range"
  },
  "left_keratometry_K1": {
    label: "左眼-角膜曲率K1",
    type: "number_range"
  },
  "right_keratometry_K1": {
    label: "右眼-角膜曲率K1",
    type: "number_range"
  },
  "left_keratometry_K2": {
    label: "左眼-角膜曲率K2",
    type: "number_range"
  },
  "right_keratometry_K2": {
    label: "右眼-角膜曲率K2",
    type: "number_range"
  },
  "left_axial_length": {
    label: "左眼-眼轴",
    type: "number_range"
  },
  "right_axial_length": {
    label: "右眼-眼轴",
    type: "number_range"
  },
  "left_sphere": {
    label: "左眼屈光-球镜",
    type: "number_range"
  },
  "left_cylinder": {
    label: "左眼屈光-柱镜",
    type: "number_range"
  },
  "left_axis": {
    label: "左眼屈光-轴位",
    type: "number_range"
  },
  "right_sphere": {
    label: "右眼屈光-球镜",
    type: "number_range"
  },
  "right_cylinder": {
    label: "右眼屈光-柱镜",
    type: "number_range"
  },
  "right_axis": {
    label: "右眼屈光-轴位",
    type: "number_range"
  },
  "left_dilated_sphere": {
    label: "左眼散瞳-球镜",
    type: "number_range"
  },
  "left_dilated_cylinder": {
    label: "左眼散瞳-柱镜",
    type: "number_range"
  },
  "left_dilated_axis": {
    label: "左眼散瞳-轴位",
    type: "number_range"
  },
  "right_dilated_sphere": {
    label: "右眼散瞳-球镜",
    type: "number_range"
  },
  "right_dilated_cylinder": {
    label: "右眼散瞳-柱镜",
    type: "number_range"
  },
  "right_dilated_axis": {
    label: "右眼散瞳-轴位",
    type: "number_range"
  },
  "left_sphere_interv": {
    label: "左眼屈光-干预-球镜",
    type: "number_range"
  },
  "left_cylinder_interv": {
    label: "左眼屈光-干预-柱镜",
    type: "number_range"
  },
  "left_axis_interv": {
    label: "左眼屈光-干预-轴位",
    type: "number_range"
  },
  "right_sphere_interv": {
    label: "右眼屈光-干预-球镜",
    type: "number_range"
  },
  "right_cylinder_interv": {
    label: "右眼屈光-干预-柱镜",
    type: "number_range"
  },
  "right_axis_interv": {
    label: "右眼屈光-干预-轴位",
    type: "number_range"
  },
  "left_dilated_sphere_interv": {
    label: "左眼散瞳-干预-球镜",
    type: "number_range"
  },
  "left_dilated_cylinder_interv": {
    label: "左眼散瞳-干预-柱镜",
    type: "number_range"
  },
  "left_dilated_axis_interv": {
    label: "左眼散瞳-干预-轴位",
    type: "number_range"
  },
  "right_dilated_sphere_interv": {
    label: "右眼散瞳-干预-球镜",
    type: "number_range"
  },
  "right_dilated_cylinder_interv": {
    label: "右眼散瞳-干预-柱镜",
    type: "number_range"
  },
  "right_dilated_axis_interv": {
    label: "右眼散瞳-干预-轴位",
    type: "number_range"
  },
  // 布尔型字段：直接生成单个复选框供选择
  "guasha": {
    label: "刮痧",
    type: "checkbox"
  },
  "aigiu": {
    label: "艾灸",
    type: "checkbox"
  },
  "zhongyao_xunzheng": {
    label: "中药熏蒸",
    type: "checkbox"
  },
  "rejiu_training": {
    label: "热灸训练",
    type: "checkbox"
  },
  "xuewei_tiefu": {
    label: "穴位贴敷",
    type: "checkbox"
  },
  "reci_pulse": {
    label: "热磁脉冲",
    type: "checkbox"
  },
  "baoguan": {
    label: "拔罐",
    type: "checkbox"
  },
  "frame_glasses": {
    label: "框架眼镜",
    type: "checkbox"
  },
  "contact_lenses": {
    label: "隐形眼镜",
    type: "checkbox"
  },
  "night_orthokeratology": {
    label: "夜戴角膜塑型镜",
    type: "checkbox"
  },
  "interv1": {
    label: "第1次干预",
    type: "checkbox"
  },
  "interv2": {
    label: "第2次干预",
    type: "checkbox"
  },
  "interv3": {
    label: "第3次干预",
    type: "checkbox"
  },
  "interv4": {
    label: "第4次干预",
    type: "checkbox"
  },
  "interv5": {
    label: "第5次干预",
    type: "checkbox"
  },
  "interv6": {
    label: "第6次干预",
    type: "checkbox"
  },
  "interv7": {
    label: "第7次干预",
    type: "checkbox"
  },
  "interv8": {
    label: "第8次干预",
    type: "checkbox"
  },
  "interv9": {
    label: "第9次干预",
    type: "checkbox"
  },
  "interv10": {
    label: "第10次干预",
    type: "checkbox"
  },
  "interv11": {
    label: "第11次干预",
    type: "checkbox"
  },
  "interv12": {
    label: "第12次干预",
    type: "checkbox"
  },
  "interv13": {
    label: "第13次干预",
    type: "checkbox"
  },
  "interv14": {
    label: "第14次干预",
    type: "checkbox"
  },
  "interv15": {
    label: "第15次干预",
    type: "checkbox"
  },
  "interv16": {
    label: "第16次干预",
    type: "checkbox"
  },
  // 其他自由文本字段
  "birthday": {
    label: "出生日期",
    type: "text"
  },
  "phone": {
    label: "联系电话",
    type: "text"
  },
  "region": {
    label: "区域",
    type: "text"
  },
  "contact_address": {
    label: "联系地址",
    type: "text"
  },
  "parent_name": {
    label: "家长姓名",
    type: "text"
  },
  "parent_phone": {
    label: "家长电话",
    type: "text"
  },
  "diet_preference": {
    label: "饮食偏好",
    type: "text"
  },
  "exercise_preference": {
    label: "运动偏好",
    type: "text"
  },
  "health_education": {
    label: "健康教育",
    type: "text"
  },
  "past_history": {
    label: "既往史",
    type: "text"
  },
  "family_history": {
    label: "家族史",
    type: "text"
  },
  "premature": {
    label: "是否早产",
    type: "dropdown",
    options: ["是", "否"]
  },
  "allergy": {
    label: "过敏史",
    type: "text"
  }
};

/* --------------------------------------------------
   功能函数定义：初始化、添加条件行、获取条件、清除条件
---------------------------------------------------*/

/**
 * 初始化组合查询模块，绑定操作按钮事件
 */
function initComboQuery() {
  const addBtn = document.getElementById('addConditionBtn');
  if (addBtn) {
    addBtn.addEventListener('click', addConditionRow);
  }
  const clearBtn = document.getElementById('clearConditionsBtn');
  if (clearBtn) {
    clearBtn.addEventListener('click', clearConditions);
  }
  const comboSearchBtn = document.getElementById('comboSearchBtn');
  if (comboSearchBtn) {
    comboSearchBtn.addEventListener('click', function () {
      console.log("查询按钮点击事件已触发");
      const conditions = getComboConditions();
      const comboInput = document.getElementById('comboConditions');
      if (comboInput) {
        comboInput.value = JSON.stringify(conditions);
      }
      console.log("组合查询条件：", comboInput.value);
      if (typeof fetchData === 'function') {
        console.log("调用 fetchData() 进行查询");
        fetchData();
      } else {
        console.error("fetchData() 未定义");
      }
      // 如需要调用 Collapse API 隐藏条件区域，可在此添加代码
    });
  }
}

/**
 * 动态添加一条条件行
 * 根据选中字段的配置决定生成控件：
 *   - "text": 生成文本输入框
 *   - "dropdown": 生成下拉选择框（选项来自 options 数组）
 *   - "number_range": 生成两个输入框，用于最小值和最大值输入
 *   - "multi-select": 生成一组复选框（用于干预效果），选项来自 options 数组
 *   - "checkbox": 直接生成单个复选框
 */
function addConditionRow() {
  const conditionRow = document.createElement('div');
  conditionRow.className = 'condition-row row g-1 mb-1';

  // 第一列：字段下拉框（占4列）
  const fieldDiv = document.createElement('div');
  fieldDiv.className = 'col-md-4';
  const fieldSelect = document.createElement('select');
  fieldSelect.className = 'form-select form-select-sm condition-field';
  const defaultFieldOption = document.createElement('option');
  defaultFieldOption.value = '';
  defaultFieldOption.textContent = '选择字段';
  fieldSelect.appendChild(defaultFieldOption);
  // 遍历配置对象生成所有字段选项，显示 label，value 使用后端字段名
  Object.keys(comboQueryConfig).forEach(key => {
    const option = document.createElement('option');
    option.value = key;
    option.textContent = comboQueryConfig[key].label || key;
    fieldSelect.appendChild(option);
  });
  fieldDiv.appendChild(fieldSelect);

  // 第二列：运算符下拉框（占3列）
  const operatorDiv = document.createElement('div');
  operatorDiv.className = 'col-md-3';
  const operatorSelect = document.createElement('select');
  operatorSelect.className = 'form-select form-select-sm condition-operator';
    const operators = [
    { value: 'like', label: 'like' },
    { value: '=', label: '=' },
    { value: '!=', label: '!=' },
    { value: '>', label: '>' },
    { value: '<', label: '<' },
    { value: '>=', label: '>=' },
    { value: '<=', label: '<=' }
   
  ];
  operators.forEach(op => {
    const opOption = document.createElement('option');
    opOption.value = op.value;
    opOption.textContent = op.label;
    operatorSelect.appendChild(opOption);
  });
  operatorDiv.appendChild(operatorSelect);

  // 第三列：值输入区域（占4列）
  const valueDiv = document.createElement('div');
  valueDiv.className = 'col-md-4';
  // 默认生成文本输入控件
  let valueInput = document.createElement('input');
  valueInput.type = 'text';
  valueInput.className = 'form-control form-control-sm condition-value';
  valueInput.placeholder = '输入查询值';
  valueDiv.appendChild(valueInput);

  // 第四列：删除按钮（占1列）
  const deleteDiv = document.createElement('div');
  deleteDiv.className = 'col-md-1';
  const deleteBtn = document.createElement('button');
  deleteBtn.type = 'button';
  deleteBtn.className = 'btn btn-danger btn-sm condition-delete';
  deleteBtn.textContent = '×';
  deleteBtn.addEventListener('click', function () {
    conditionRow.remove();
  });
  deleteDiv.appendChild(deleteBtn);

  // 将各部分加入条件行
  conditionRow.appendChild(fieldDiv);
  conditionRow.appendChild(operatorDiv);
  conditionRow.appendChild(valueDiv);
  conditionRow.appendChild(deleteDiv);

  // 字段下拉框 change 事件：根据所选字段更新值输入区域
  fieldSelect.addEventListener('change', function () {
    const selectedField = fieldSelect.value;
    valueDiv.innerHTML = ""; // 清空当前值输入区域
    if (!selectedField) {
      // 恢复默认文本输入框
      valueInput = document.createElement('input');
      valueInput.type = 'text';
      valueInput.className = 'form-control form-control-sm condition-value';
      valueInput.placeholder = '输入查询值';
      valueDiv.appendChild(valueInput);
      const existingExtra = conditionRow.querySelector('.extra-options');
      if (existingExtra) existingExtra.remove();
      return;
    }
    const config = comboQueryConfig[selectedField];
    if (!config) {
      valueInput = document.createElement('input');
      valueInput.type = 'text';
      valueInput.className = 'form-control form-control-sm condition-value';
      valueInput.placeholder = '输入查询值';
      valueDiv.appendChild(valueInput);
      return;
    }
    switch (config.type) {
      case "text":
        valueInput = document.createElement('input');
        valueInput.type = 'text';
        valueInput.className = 'form-control form-control-sm condition-value';
        valueInput.placeholder = '输入查询值';
        valueDiv.appendChild(valueInput);
        break;
      case "number_range":
        const minInput = document.createElement('input');
        minInput.type = 'number';
        minInput.className = 'form-control form-control-sm condition-value-min';
        minInput.placeholder = '最小值';
        const maxInput = document.createElement('input');
        maxInput.type = 'number';
        maxInput.className = 'form-control form-control-sm condition-value-max';
        maxInput.placeholder = '最大值';
        const rangeDiv = document.createElement('div');
        rangeDiv.className = 'd-flex gap-1';
        rangeDiv.appendChild(minInput);
        rangeDiv.appendChild(maxInput);
        valueDiv.appendChild(rangeDiv);
        break;
      case "dropdown":
        const select = document.createElement('select');
        select.className = 'form-select form-select-sm condition-value';
        const defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = '请选择';
        select.appendChild(defaultOpt);
        config.options.forEach(opt => {
          const option = document.createElement('option');
          option.value = opt;
          option.textContent = opt;
          select.appendChild(option);
        });
        valueDiv.appendChild(select);
        break;
      case "multi-select":
        // 生成复选框组
        const multiDiv = document.createElement('div');
        multiDiv.className = 'd-flex flex-wrap gap-1';
        config.options.forEach(opt => {
          const label = document.createElement('label');
          label.className = 'form-check form-check-inline';
          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.className = 'form-check-input condition-value-multi';
          checkbox.value = opt;
          label.appendChild(checkbox);
          const span = document.createElement('span');
          span.className = 'form-check-label';
          span.textContent = opt;
          label.appendChild(span);
          multiDiv.appendChild(label);
        });
        valueDiv.appendChild(multiDiv);
        break;
      case "checkbox":
        // 生成单个复选框
        const singleCheckboxDiv = document.createElement('div');
        singleCheckboxDiv.className = 'form-check';
        const singleCheckbox = document.createElement('input');
        singleCheckbox.type = 'checkbox';
        singleCheckbox.className = 'form-check-input condition-value-checkbox';
        singleCheckboxDiv.appendChild(singleCheckbox);
        const checkboxLabel = document.createElement('label');
        checkboxLabel.className = 'form-check-label';
        checkboxLabel.textContent = '选中';
        singleCheckboxDiv.appendChild(checkboxLabel);
        valueDiv.appendChild(singleCheckboxDiv);
        break;
      default:
        valueInput = document.createElement('input');
        valueInput.type = 'text';
        valueInput.className = 'form-control form-control-sm condition-value';
        valueInput.placeholder = '输入查询值';
        valueDiv.appendChild(valueInput);
        break;
    }
  });

  // 将条件行添加到条件容器中
  const container = document.getElementById('advancedQueryContainer');
  container.appendChild(conditionRow);
}

/**
 * 遍历所有条件行，收集组合查询条件数据，返回数组。
 * 每个条件对象结构：
 * {
 *   field: <字段名>,
 *   operator: <运算符>,
 *   value: <查询值>  // 对于 number_range 为 {min: "", max: ""}，multi-select 为数组，checkbox 为布尔值
 * }
 */
function getComboConditions() {
  const conditionRows = document.querySelectorAll('.condition-row');
  const conditions = [];
  conditionRows.forEach(row => {
    const fieldEl = row.querySelector('.condition-field');
    const operatorEl = row.querySelector('.condition-operator');
    let value;
    const field = fieldEl ? fieldEl.value.trim() : '';
    const operator = operatorEl ? operatorEl.value.trim() : '';
    if (!field || !operator) return;
    const config = comboQueryConfig[field];
    if (config) {
      switch (config.type) {
        case "number_range":
          const minEl = row.querySelector('.condition-value-min');
          const maxEl = row.querySelector('.condition-value-max');
          value = { min: minEl ? minEl.value.trim() : "", max: maxEl ? maxEl.value.trim() : "" };
          break;
        case "multi-select":
          const checkboxes = row.querySelectorAll('.condition-value-multi');
          value = [];
          checkboxes.forEach(cb => {
            if (cb.checked) {
              value.push(cb.value);
            }
          });
          break;
        case "checkbox":
          const checkboxEl = row.querySelector('.condition-value-checkbox');
          value = checkboxEl ? checkboxEl.checked : false;
          break;
        default:
          const valEl = row.querySelector('.condition-value');
          value = valEl ? valEl.value.trim() : "";
          break;
      }
    } else {
      const valEl = row.querySelector('.condition-value');
      value = valEl ? valEl.value.trim() : "";
    }
    conditions.push({ field: field, operator: operator, value: value });
  });
  return conditions;
}

/**
 * 清除所有条件行
 */
function clearConditions() {
  const container = document.getElementById('advancedQueryContainer');
  container.innerHTML = '';
}

/* 初始化组合查询模块 */
function initComboQuery() {
  const addBtn = document.getElementById('addConditionBtn');
  if (addBtn) {
    addBtn.addEventListener('click', addConditionRow);
  }
  const clearBtn = document.getElementById('clearConditionsBtn');
  if (clearBtn) {
    clearBtn.addEventListener('click', clearConditions);
  }
  const comboSearchBtn = document.getElementById('comboSearchBtn');
  if (comboSearchBtn) {
    comboSearchBtn.addEventListener('click', function () {
      console.log("查询按钮点击事件已触发");
      const conditions = getComboConditions();
      const comboInput = document.getElementById('comboConditions');
      if (comboInput) {
        comboInput.value = JSON.stringify(conditions);
      }
      console.log("组合查询条件：", comboInput.value);
      if (typeof fetchData === 'function') {
        console.log("调用 fetchData() 进行查询");
        fetchData();
      } else {
        console.error("fetchData() 未定义");
      }
      // 如需要调用 Collapse API 隐藏条件区域，可在此添加代码
    });
  }
}

/* DOMContentLoaded 后初始化组合查询模块 */
document.addEventListener('DOMContentLoaded', function () {
  initComboQuery();
});
