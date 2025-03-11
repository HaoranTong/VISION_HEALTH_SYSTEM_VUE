#!/usr/bin/env node
/**
 * 文件名称: comboQuery_report.js
 * 完整存储路径: frontend/static/js/comboQuery_report.js
 * 功能说明:
 *   专用于报表页面的组合查询模块。基于原有 comboQuery.js 扩展，
 *   在每条条件行最左侧增加了一个下拉选择框，用于选择该条件的角色（"统计指标"、"分组"、"筛选"）。
 *   其它功能（添加条件、删除条件、收集条件、清除条件）与原模块基本一致。
 * 使用说明:
 *   1. 页面中必须存在条件容器（id="advancedQueryContainer"）和隐藏输入框（id="comboConditions"）。
 *   2. 操作按钮的 ID 分别为 "addConditionBtn"、"clearConditionsBtn"。
 *   3. 报表页面使用的查询按钮 ID 为 "reportSearchBtn"，本模块将绑定该按钮的点击事件，
 *      更新隐藏输入框中的组合查询条件，并调用全局函数 fetchData() 进行查询。
 */

"use strict";

// 额外角色选项
const roleOptions = [
  { value: "metric", label: "统计指标" },
  { value: "group", label: "分组" },
  { value: "filter", label: "筛选" }
];

const comboQueryConfig = {
  "data_year": { label: "数据年份", type: "dropdown", options: ["2023", "2024", "2025", "2026", "2027", "2028"] },
  "education_id": { label: "教育ID号", type: "text" },
  "school": { label: "学校", type: "dropdown", options: ["华兴小学", "苏宁红军小学", "师大附小清华小学"] },
  "grade": { label: "年级", type: "dropdown", options: ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级", "七年级", "八年级", "九年级"] },
  "class_name": { label: "班级", type: "dropdown", options: (function () { let arr = []; for (let i = 1; i <= 15; i++) { arr.push(i + "班"); } return arr; })() },
  "name": { label: "姓名", type: "text" },
  "gender": { label: "性别", type: "dropdown", options: ["男", "女"] },
  "age": { label: "年龄", type: "number_range" },
  "vision_level": { label: "视力等级", type: "dropdown", options: ["临床前期近视", "轻度近视", "中度近视"] },
  "interv_vision_level": { label: "干预后视力等级", type: "dropdown", options: ["临床前期近视", "轻度近视", "中度近视"] }
  // 可继续添加其他字段...
};

/**
 * 初始化组合查询模块，绑定按钮事件
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
  // 修改：绑定报表页面的查询按钮 reportSearchBtn
  const reportSearchBtn = document.getElementById('reportSearchBtn');
  if (reportSearchBtn) {
    reportSearchBtn.addEventListener('click', function () {
      console.log("组合查询模块：查询按钮点击事件触发");
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
    });
  }
}

/**
 * 动态添加一条条件行，增加左侧角色下拉框
 */
function addConditionRow() {
  const conditionRow = document.createElement('div');
  conditionRow.className = 'condition-row row g-1 mb-1';

  // 第一列：角色下拉框（占2列）
  const roleDiv = document.createElement('div');
  roleDiv.className = 'col-md-2';
  const roleSelect = document.createElement('select');
  roleSelect.className = 'form-select form-select-sm condition-role';
  const defaultRoleOption = document.createElement('option');
  defaultRoleOption.value = '';
  defaultRoleOption.textContent = '选择角色';
  roleSelect.appendChild(defaultRoleOption);
  roleOptions.forEach(item => {
    const option = document.createElement('option');
    option.value = item.value;
    option.textContent = item.label;
    roleSelect.appendChild(option);
  });
  roleDiv.appendChild(roleSelect);

  // 第二列：字段下拉框（占4列）
  const fieldDiv = document.createElement('div');
  fieldDiv.className = 'col-md-4';
  const fieldSelect = document.createElement('select');
  fieldSelect.className = 'form-select form-select-sm condition-field';
  const defaultFieldOption = document.createElement('option');
  defaultFieldOption.value = '';
  defaultFieldOption.textContent = '选择字段';
  fieldSelect.appendChild(defaultFieldOption);
  Object.keys(comboQueryConfig).forEach(key => {
    const option = document.createElement('option');
    option.value = key;
    option.textContent = comboQueryConfig[key].label || key;
    fieldSelect.appendChild(option);
  });
  fieldDiv.appendChild(fieldSelect);

  // 第三列：运算符下拉框（占3列）
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

  // 第四列：值输入区域（占3列）
  const valueDiv = document.createElement('div');
  valueDiv.className = 'col-md-3';
  let valueInput = document.createElement('input');
  valueInput.type = 'text';
  valueInput.className = 'form-control form-control-sm condition-value';
  valueInput.placeholder = '输入查询值';
  valueDiv.appendChild(valueInput);

  // 第五列：删除按钮（占1列）
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

  conditionRow.appendChild(roleDiv);
  conditionRow.appendChild(fieldDiv);
  conditionRow.appendChild(operatorDiv);
  conditionRow.appendChild(valueDiv);
  conditionRow.appendChild(deleteDiv);

  fieldSelect.addEventListener('change', function () {
    const selectedField = fieldSelect.value;
    valueDiv.innerHTML = "";
    if (!selectedField) {
      valueInput = document.createElement('input');
      valueInput.type = 'text';
      valueInput.className = 'form-control form-control-sm condition-value';
      valueInput.placeholder = '输入查询值';
      valueDiv.appendChild(valueInput);
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

  const container = document.getElementById('advancedQueryContainer');
  container.appendChild(conditionRow);
}

function getComboConditions() {
  const conditionRows = document.querySelectorAll('.condition-row');
  const conditions = [];
  conditionRows.forEach(row => {
    const roleEl = row.querySelector('.condition-role');
    const fieldEl = row.querySelector('.condition-field');
    const operatorEl = row.querySelector('.condition-operator');
    let value;
    const role = roleEl ? roleEl.value.trim() : '';
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
    conditions.push({ role: role, field: field, operator: operator, value: value });
  });
  return conditions;
}

function clearConditions() {
  const container = document.getElementById('advancedQueryContainer');
  container.innerHTML = '';
}

document.addEventListener('DOMContentLoaded', function () {
  initComboQuery();
});
