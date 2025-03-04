/*
文件名称: query.js
完整存储路径: frontend/static/js/query.js
功能说明:
    实现数据查询页面的交互逻辑，包括：
    - 采集查询条件并调用后端查询接口（/api/students/query）获取数据，
      并在表格中展示查询结果和分页信息。
    - 实现导出功能，通过调用后端导出接口（/api/students/export）下载 Excel 文件。
    - 实现清除查询条件功能和列配置控制。
使用说明:
    在 query.html 页面中通过 <script> 标签引入本脚本，确保相关 DOM 元素存在。
*/

document.addEventListener('DOMContentLoaded', function () {
  // 定义查询条件元素（按白名单获取）
  const validParams = ['education_id', 'school', 'grade', 'class_name', 'data_year', 'name', 'gender', 'id_card'];
  // 对应的输入框ID与参数名一致
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
  const resultTableBody = document.getElementById('resultTableBody');
  const pagination = document.getElementById('pagination');
  // 列配置相关
  const selectAllCheckbox = document.getElementById('selectAllColumns');
  const columnCheckboxes = document.querySelectorAll('.column-checkbox');
  // 默认每页10条数据，当前页1
  let currentPage = 1;
  let perPage = 10;

  // 渲染查询结果到表格
  function renderTable(students) {
    resultTableBody.innerHTML = '';
    students.forEach(student => {
      const tr = document.createElement('tr');
      // 创建每个单元格，根据需要显示的列（初步示例，实际列可根据列配置调整）
      tr.innerHTML = `
        <td data-column="data_year">${student.data_year || ''}</td>
        <td data-column="school">${student.school || ''}</td>
        <td data-column="grade">${student.grade || ''}</td>
        <td data-column="class_name">${student.class_name || ''}</td>
        <td data-column="name">${student.name || ''}</td>
        <td data-column="gender">${student.gender || ''}</td>
        <td data-column="left_eye_naked">${student.left_eye_naked || ''}</td>
        <td data-column="right_eye_naked">${student.right_eye_naked || ''}</td>
        <td data-column="vision_level">${student.vision_level || ''}</td>
      `;
      resultTableBody.appendChild(tr);
    });
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
        renderTable(result.students);
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
    // 调用导出接口，参数同查询
    const url = '/api/students/export?' + params.toString();
    // 直接设置 window.location.href 触发下载
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

  // 列配置处理（简单示例：根据选中状态显示/隐藏 table 中对应 data-column 的列）
  function updateTableColumns() {
    const selectedColumns = [];
    columnCheckboxes.forEach(cb => {
      if (cb.checked) selectedColumns.push(cb.value);
    });
    // 对表头与每行数据进行显示隐藏
    const allCells = document.querySelectorAll('[data-column]');
    allCells.forEach(cell => {
      if (selectedColumns.includes(cell.getAttribute('data-column'))) {
        cell.style.display = '';
      } else {
        cell.style.display = 'none';
      }
    });
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
  // 其他列配置复选框事件
  columnCheckboxes.forEach(cb => {
    cb.addEventListener('change', updateTableColumns);
  });

  // 初始加载数据
  fetchData();
});
