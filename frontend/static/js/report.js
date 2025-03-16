document.addEventListener('DOMContentLoaded', function () {
  const validParams = ['education_id', 'school', 'grade', 'class_name', 'name', 'gender', 'id_card'];
  let currentPage = 1;
  const perPage = 10;
  let latestReportData = null;
  let isLoading = false;

  function showLoading() {
    isLoading = true;
    document.getElementById('loading').style.display = 'block';
  }

  function hideLoading() {
    isLoading = false;
    document.getElementById('loading').style.display = 'none';
  }

  function getReportQueryParams() {
    const params = new URLSearchParams();
    validParams.forEach(param => {
      const el = document.getElementById(param);
      if (el && el.value.trim()) {
        params.append(param, el.value.trim());
      }
    });
    const statTimeEl = document.getElementById('statTime');
    if (statTimeEl && statTimeEl.value.trim()) {
      params.append('stat_time', statTimeEl.value.trim());
    }
    // 明确传递查询模式
    const queryModeEl = document.getElementById('queryMode');
    if (queryModeEl) {
      params.append('query_mode', queryModeEl.value.trim());
    }
    if (queryModeEl.value.trim() === "template") {
      const templateSelect = document.getElementById('templateSelect');
      if (templateSelect.value) {
        params.append('template', templateSelect.value);
      }
    } else {
      // 自定义查询模式，从组合查询模块获取条件
      if (typeof getComboConditions === 'function') {
        const comboConds = getComboConditions();
        if (comboConds && comboConds.length > 0) {
          params.append('advanced_conditions', JSON.stringify(comboConds));
        }
      }
    }
    const reportNameInput = document.getElementById('reportNameInput');
    if (reportNameInput && reportNameInput.value.trim()) {
      params.append('report_name', reportNameInput.value.trim());
    }
    return params;
  }

  function renderReportHeader(data) {
    const theadEl = document.getElementById('reportTableHead');
    theadEl.innerHTML = '';
    data.header.forEach(headerRow => {
      const tr = document.createElement('tr');
      headerRow.forEach(cell => {
        const th = document.createElement('th');
        th.textContent = cell.text;
        th.colSpan = cell.colspan || 1;
        th.rowSpan = cell.rowspan || 1;
        th.style.cssText = 'text-align: center; vertical-align: middle;';
        tr.appendChild(th);
      });
      theadEl.appendChild(tr);
    });
  }

  function renderReportTable(data) {
    const tbodyEl = document.getElementById('reportTableBody');
    tbodyEl.innerHTML = '';
    data.rows.forEach(rowArray => {
      const tr = document.createElement('tr');
      rowArray.forEach((cellValue, idx) => {
        const td = document.createElement('td');
        if (idx === 0 || idx === rowArray.length - 1) {
          td.textContent = cellValue;
        } else {
          if ((idx - 1) % 2 === 0) {
            td.textContent = cellValue;
          } else {
            td.textContent = `${cellValue}%`;
          }
        }
        td.style.textAlign = 'center';
        tr.appendChild(td);
      });
      tbodyEl.appendChild(tr);
    });
  }

  function renderReportPagination(total) {
    const paginationEl = document.getElementById('pagination');
    paginationEl.innerHTML = '';
    const totalPages = Math.ceil(total / perPage);
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement('li');
      li.className = `page-item ${i === currentPage ? 'active' : ''}`;
      li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
      li.addEventListener('click', function (e) {
        e.preventDefault();
        currentPage = i;
        fetchReportData();
      });
      paginationEl.appendChild(li);
    }
  }

  function fetchReportData() {
    if (isLoading) return;
    showLoading();
    const params = getReportQueryParams();
    params.append('page', currentPage);
    params.append('per_page', perPage);
    fetch(`/api/analysis/report?${params.toString()}`)
      .then(response => {
        if (!response.ok) throw new Error(`HTTP错误 ${response.status}`);
        return response.json();
      })
      .then(data => {
        if (data.error) throw new Error(data.error);
        latestReportData = data;
        document.getElementById('reportTitle').textContent = data.tableName;
        document.getElementById('reportTimeAnnotation').textContent = data.filterAnnotation;
        renderReportHeader(data);
        renderReportTable(data);
        renderReportPagination(data.total || data.total);
      })
      .catch(error => {
        console.error('请求失败:', error);
        alert(`查询失败: ${error.message}`);
      })
      .finally(() => hideLoading());
  }

  const reportSearchBtn = document.getElementById('reportSearchBtn');
  if (reportSearchBtn) {
    reportSearchBtn.addEventListener('click', () => {
      currentPage = 1;
      fetchReportData();
    });
  }

  const clearBtn = document.getElementById('clearBtn');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      validParams.forEach(param => {
        const el = document.getElementById(param);
        if (el) el.value = '';
      });
      document.getElementById('statTime').value = '';
      document.getElementById('reportNameInput').value = '';
      document.getElementById('comboConditions').value = '';
      document.getElementById('advancedQueryContainer').innerHTML = '';
      document.getElementById('queryMode').value = 'template';
      document.getElementById('templateSelect').disabled = false;
      document.getElementById('templateSelect').value = '';
      document.getElementById('reportTitle').textContent = '';
      document.getElementById('reportTimeAnnotation').textContent = '';
      document.getElementById('reportTableHead').innerHTML = '';
      document.getElementById('reportTableBody').innerHTML = '';
      document.getElementById('pagination').innerHTML = '';
    });
  }

  const templateSelect = document.getElementById('templateSelect');
  if (templateSelect) {
    templateSelect.addEventListener('change', function () {
      if (document.getElementById('queryMode').value === "template" && templateSelect.value) {
        currentPage = 1;
        fetchReportData();
      }
    });
  }

  const queryModeEl = document.getElementById('queryMode');
  if (queryModeEl) {
    queryModeEl.addEventListener('change', function () {
      if (queryModeEl.value === "template") {
        document.getElementById('comboConditions').value = '';
        document.getElementById('templateSelect').disabled = false;
      } else {
        document.getElementById('templateSelect').disabled = true;
        document.getElementById('templateSelect').value = '';
      }
    });
  }
// 导出报表函数
  function exportReport() {
  console.log('导出报表按钮被点击'); // 添加调试信息
  if (!latestReportData) {
    alert('请先查询数据再导出');
    return;
  }

  // 获取当前查询条件
  const params = getReportQueryParams();
  params.append('export', 'true'); // 添加导出标志

  // 构造导出请求URL
  const exportUrl = `/api/analysis/report?${params.toString()}`;

  // 触发文件下载
  window.location.href = exportUrl;
}

// 绑定导出按钮点击事件
const exportReportBtn = document.getElementById('exportReportBtn');
if (exportReportBtn) {
  exportReportBtn.addEventListener('click', exportReport);
}

});
