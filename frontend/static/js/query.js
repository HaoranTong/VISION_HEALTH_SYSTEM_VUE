﻿/*
文件名称: query.js
完整存储路径: frontend/static/js/query.js
功能说明:
    实现数据查询页面的交互逻辑，动态生成表头和数据行，
    使得前端展示的列顺序与用户在列配置下拉菜单中的选择保持一致。
    该脚本会根据列配置选中的字段动态构造表头 (<thead>) 和每一行 (<tr>) 的单元格 (<td>)。
使用说明:
    在 query.html 页面中通过 <script> 标签引入本脚本，确保相关 DOM 元素存在。
*/

document.addEventListener('DOMContentLoaded', function () {
  // 定义查询条件元素（按白名单获取）
  const validParams = ['education_id', 'school', 'grade', 'class_name', 'data_year', 'name', 'gender', 'id_card'];
  function getQueryParams() {
    const params = new URLSearchParams();
    validParams.forEach(param => {
      const element = document.getElementById(param);
      if (element) {
        const value = element.value.trim();
        if (value) params.append(param, value);
      }
    });
    return params;
  }

  // 获取分页与按钮元素
  const searchBtn = document.getElementById('searchBtn');
  const exportBtn = document.getElementById('exportBtn');
  const clearBtn = document.getElementById('clearBtn');
  const pagination = document.getElementById('pagination');
  // 列配置相关
  const selectAllCheckbox = document.getElementById('selectAllColumns');
  const columnCheckboxes = document.querySelectorAll('.column-checkbox');
  // 表格头和体部分（确保 query.html 中 <thead> 添加了 id="resultTableHead"）
  const resultTableHead = document.getElementById('resultTableHead');
  const resultTableBody = document.getElementById('resultTableBody');
  // 默认每页10条数据，当前页1
  let currentPage = 1;
  let perPage = 10;
  // 全局保存最新查询数据（用于列配置更新时不必重新请求后端）
  let latestData = [];

  // 定义默认展示的列（数据库字段名）
  const defaultColumns = [
    "name",
    "gender",
    "age",
    "vision_level",
    "interv_vision_level",
    "left_eye_naked",
    "right_eye_naked",
    "left_eye_naked_interv",
    "right_eye_naked_interv",
    "left_naked_change",
    "right_naked_change"
  ];

  // 根据列配置复选框的状态按页面顺序获取选中的字段
  function getSelectedColumns() {
    let selected = [];
    columnCheckboxes.forEach(cb => {
      if (cb.checked) selected.push(cb.value);
    });
    return selected;
  }

  // 初始化复选框状态，根据 defaultColumns 设置哪些默认勾选
  function initializeColumnCheckboxes() {
    columnCheckboxes.forEach(cb => {
      if (defaultColumns.includes(cb.value)) {
        cb.checked = true;
      } else {
        cb.checked = false;
      }
    });
  }

  // 根据当前选中的列动态生成表头和数据行
  function renderTable(data) {
    const selectedColumns = getSelectedColumns();

    // 生成表头：遍历复选框顺序，只有选中的生成 <th>
    let headerHTML = '<tr>';
    columnCheckboxes.forEach(cb => {
      if (cb.checked) {
        let headerText = cb.parentElement.textContent.trim();
        headerHTML += `<th data-column="${cb.value}">${headerText}</th>`;
      }
    });
    headerHTML += '</tr>';
    resultTableHead.innerHTML = headerHTML;

    // 生成数据行：遍历查询数据，根据 selectedColumns 输出对应 <td>
    let bodyHTML = '';
    data.forEach(record => {
      bodyHTML += '<tr>';
      selectedColumns.forEach(col => {
        let cellData = record[col] !== undefined ? record[col] : '';
        bodyHTML += `<td data-column="${col}">${cellData}</td>`;
      });
      bodyHTML += '</tr>';
    });
    resultTableBody.innerHTML = bodyHTML;
  }

  // 渲染分页控件（简单示例）
  function renderPagination(total) {
    pagination.innerHTML = '';
    const totalPages = Math.ceil(total / perPage);
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement('li');
      li.className = 'page-item' + (i === currentPage ? ' active' : '');
      li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
      li.addEventListener('click', function (e) {
        e.preventDefault();
        currentPage = i;
        fetchData();
      });
      pagination.appendChild(li);
    }
  }

  // 请求查询数据接口
  function fetchData() {
    const params = getQueryParams();
    params.append('page', currentPage);
    params.append('per_page', perPage);
    fetch('/api/students/query?' + params.toString())
      .then(response => response.json())
      .then(result => {
        if (result.error) {
          alert("查询错误: " + result.error);
          return;
        }
        latestData = result.students; // 保存最新数据
        renderTable(latestData);
        renderPagination(result.total);
      })
      .catch(err => {
        console.error("查询请求错误:", err);
        alert("查询请求错误，请检查控制台");
      });
  }

  // 导出数据（调用导出接口，触发文件下载）
  function exportData() {
    const params = getQueryParams();
    let selectedColumns = getSelectedColumns();
    if (selectedColumns.length > 0) {
      params.append("columns", selectedColumns.join(","));
    }
    const url = '/api/students/export?' + params.toString();
    window.location.href = url;
  }

  // 清除查询条件
  function clearData() {
    validParams.forEach(param => {
      const element = document.getElementById(param);
      if (element) {
        element.value = '';
      }
    });
    currentPage = 1;
    fetchData();
  }

  // 列配置更新时重新渲染表头和数据行（使用保存的最新数据）
  function updateTableColumns() {
    renderTable(latestData);
  }

  // 绑定事件
  searchBtn.addEventListener('click', function () {
    currentPage = 1;
    fetchData();
  });

  exportBtn.addEventListener('click', function () {
    exportData();
  });

  clearBtn.addEventListener('click', function () {
    clearData();
  });

  // 初始化列配置：设置默认勾选状态
  initializeColumnCheckboxes();

  // 列配置全选
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', function () {
      const checkAll = selectAllCheckbox.checked;
      columnCheckboxes.forEach(cb => {
        cb.checked = checkAll;
      });
      updateTableColumns();
    });
  }
  columnCheckboxes.forEach(cb => {
    cb.addEventListener('change', updateTableColumns);
  });

  // 初始加载数据
  fetchData();
});
