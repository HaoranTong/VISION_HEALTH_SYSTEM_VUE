/*
文件名称: query.js
完整存储路径: frontend/static/js/query.js
功能说明:
    实现数据查询页面的交互逻辑，包括固定查询、分页、列配置、导出和调用后端查询接口。
    此文件中固定查询和分页功能保持不变，不再包含组合查询的相关代码，
    组合查询功能由独立的 comboQuery.js 模块提供。
使用说明:
    在 query.html 中通过 <script> 标签引入本文件，确保 DOM 中固定查询部分正常工作。
*/

document.addEventListener('DOMContentLoaded', function () {
  // 固定查询条件（白名单）
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
    // 此处组合查询条件由 comboQuery.js 模块收集，存入隐藏输入框 comboConditions
    const comboConditionsInput = document.getElementById('comboConditions');
    if (comboConditionsInput && comboConditionsInput.value.trim() !== "") {
      params.append('advanced_conditions', comboConditionsInput.value.trim());
    }
    // 排序参数
    const sortField = document.getElementById('sortField');
    const sortOrder = document.getElementById('sortOrder');
    if (sortField && sortField.value.trim() !== "") {
      params.append('sort_field', sortField.value.trim());
    }
    if (sortOrder && sortOrder.value.trim() !== "") {
      params.append('sort_order', sortOrder.value.trim());
    }
    return params;
  }

  // 分页与按钮元素
  const searchBtn = document.getElementById('searchBtn');
  const exportBtn = document.getElementById('exportBtn');
  const clearBtn = document.getElementById('clearBtn');
  const pagination = document.getElementById('pagination');
  const resultTableHead = document.getElementById('resultTableHead');
  const resultTableBody = document.getElementById('resultTableBody');
  let currentPage = 1;
  let perPage = 10;
  let latestData = []; // 保存最新查询数据

  // 默认展示列
  const defaultColumns = [
    "school", "grade", "class_name", "name", "gender", "age",
    "vision_level", "interv_vision_level", "left_naked_change", "right_naked_change",
    "left_sphere_change", "right_sphere_change"
  ];

  // 初始化列配置复选框
  const columnCheckboxes = document.querySelectorAll('.column-checkbox');
  function initializeColumnCheckboxes() {
    columnCheckboxes.forEach(cb => {
      cb.checked = defaultColumns.includes(cb.value);
    });
  }
  initializeColumnCheckboxes();

  function getSelectedColumns() {
    let selected = [];
    columnCheckboxes.forEach(cb => {
      if (cb.checked) selected.push(cb.value);
    });
    return selected;
  }

  function renderTable(data) {
    const selectedColumns = getSelectedColumns();
    let headerHTML = '<tr>';
    columnCheckboxes.forEach(cb => {
      if (cb.checked) {
        let headerText = cb.parentElement.textContent.trim();
        headerHTML += `<th data-column="${cb.value}">${headerText}</th>`;
      }
    });
    headerHTML += '</tr>';
    resultTableHead.innerHTML = headerHTML;
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
        latestData = result.students;
        renderTable(latestData);
        renderPagination(result.total);
      })
      .catch(err => {
        console.error("查询请求错误:", err);
        alert("查询请求错误，请检查控制台");
      });
  }
  // 将 fetchData() 挂载到全局 window 对象上
window.fetchData = fetchData;

  function exportData() {
    const params = getQueryParams();
    let selectedColumns = getSelectedColumns();
    if (selectedColumns.length > 0) {
      params.append("columns", selectedColumns.join(","));
    }
    const url = '/api/students/export?' + params.toString();
    window.location.href = url;
  }

  function clearData() {
    validParams.forEach(param => {
      const element = document.getElementById(param);
      if (element) {
        element.value = '';
      }
    });
    const comboConditionsInput = document.getElementById('comboConditions');
    if (comboConditionsInput) {
      comboConditionsInput.value = '';
    }
    currentPage = 1;
    fetchData();
  }

  const selectAllCheckbox = document.getElementById('selectAllColumns');
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', function () {
      const checkAll = selectAllCheckbox.checked;
      columnCheckboxes.forEach(cb => {
        cb.checked = checkAll;
      });
      renderTable(latestData);
    });
  }
  columnCheckboxes.forEach(cb => {
    cb.addEventListener('change', function () {
      renderTable(latestData);
    });
  });

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

  fetchData();
});
