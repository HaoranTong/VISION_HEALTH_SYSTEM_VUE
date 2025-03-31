/*
文件名称: query.js
完整存储路径: frontend/static/js/query.js
功能说明:
    实现数据查询页面的交互逻辑，支持固定查询、分页、列配置、导出、以及高级组合查询和排序功能。
    高级组合查询条件通过页面上的高级面板动态添加，并转换为 JSON 字符串提交后端。
使用说明:
    在 query.html 页面中通过 <script> 标签引入本脚本，确保相关 DOM 元素存在。
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
    // 采集高级组合查询条件（JSON字符串）
    const comboConditionsInput = document.getElementById('comboConditions');
    if (comboConditionsInput && comboConditionsInput.value.trim() !== "") {
      params.append('combo_conditions', comboConditionsInput.value.trim());
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
    "left_sphere_change", "right_sphere_change", 
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
    // 生成表头
    let headerHTML = '<tr>';
    columnCheckboxes.forEach(cb => {
      if (cb.checked) {
        let headerText = cb.parentElement.textContent.trim();
        headerHTML += `<th data-column="${cb.value}">${headerText}</th>`;
      }
    });
    headerHTML += '</tr>';
    resultTableHead.innerHTML = headerHTML;
    // 生成数据行
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

  // 绑定列配置复选框更新事件
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

  // 事件绑定
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

  // 初始加载数据
  fetchData();
});
