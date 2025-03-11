/**
 * 文件名称: report.js
 * 完整存储路径: frontend/static/js/report.js
 * 功能说明:
 *   实现统计报表页面的前端交互逻辑，包括：
 *     1. 收集固定查询字段、组合查询条件、模板选择、统计时间以及报表名称（用户可修改）；
 *     2. 当检测到自由组合查询条件不为空时，自动清除模板选择（不传 template 参数）；
 *     3. 调用后端统计报表接口获取数据，并动态生成两行表头和报表数据；
 *     4. 在报表标题行中，左侧显示报表名称（用户自定义或系统默认），右侧显示附注“统计时间：<stat_time>”，字体与报表一致且右对齐；
 *     5. 支持分页、导出、切换到图表页面和统一“取消”按钮，恢复页面初始状态。
 */

document.addEventListener('DOMContentLoaded', function () {
  const validParams = ['education_id', 'school', 'grade', 'class_name', 'name', 'gender', 'id_card'];

  function getReportQueryParams() {
    const params = new URLSearchParams();
    validParams.forEach(param => {
      const element = document.getElementById(param);
      if (element) {
        const value = element.value.trim();
        if (value) params.append(param, value);
      }
    });
    // 统计时间下拉框
    const statTimeEl = document.getElementById('statTime');
    if (statTimeEl && statTimeEl.value.trim() !== "") {
      params.append('stat_time', statTimeEl.value.trim());
    }
    // 读取组合查询条件
    const comboConditionsInput = document.getElementById('comboConditions');
    const advancedConditions = comboConditionsInput && comboConditionsInput.value.trim();
    if (advancedConditions) {
      params.append('advanced_conditions', advancedConditions);
      // 如果存在自由组合查询条件，则不传模板参数
    } else {
      const templateSelect = document.getElementById('templateSelect');
      if (templateSelect && templateSelect.value) {
        params.append('template', templateSelect.value);
      }
    }
    return params;
  }

  let currentPage = 1;
  const perPage = 10;
  let latestReportData = null;

  function renderReportHeader(data) {
    const theadEl = document.getElementById('reportTableHead');
    const templateSelect = document.getElementById('templateSelect');
    let groupTitle = "分组";
    if (templateSelect) {
      if (templateSelect.value === "template1") {
        groupTitle = "年龄段";
      } else if (templateSelect.value === "template2") {
        groupTitle = "性别";
      }
    }
    const header = data.header;
    if (!header || header.length < 10) {
      let headerHTML = "<tr>";
      (header || []).forEach(col => {
        headerHTML += `<th>${col}</th>`;
      });
      headerHTML += "</tr>";
      theadEl.innerHTML = headerHTML;
      return;
    }
    // 使用 groupTitle 替换第一列标题
    let row1 = "<tr>";
    row1 += `<th colspan="1">${groupTitle}</th>`;
    const groups = [
      header[1].replace("(人数)", "").trim(),
      header[3].replace("(人数)", "").trim(),
      header[5].replace("(人数)", "").trim(),
      header[7].replace("(人数)", "").trim()
    ];
    groups.forEach(g => {
      row1 += `<th colspan="2">${g}</th>`;
    });
    row1 += `<th colspan="1">${header[9]}</th>`;
    row1 += "</tr>";

    let row2 = "<tr>";
    row2 += `<th></th>`;
    for (let i = 0; i < 4; i++) {
      row2 += `<th>人数</th><th>占比</th>`;
    }
    row2 += `<th></th>`;
    row2 += "</tr>";

    theadEl.innerHTML = row1 + row2;
  }

  function renderReportTable(data) {
    const titleContainer = document.getElementById('reportTitleContainer');
    const titleEl = document.getElementById('reportTitle');
    const timeAnnotationEl = document.getElementById('reportTimeAnnotation');
    const tbodyEl = document.getElementById('reportTableBody');
    if (!data) return;
    // 获取用户自定义报表名称，如果为空则使用后端返回的名称
    const reportNameInput = document.getElementById('reportNameInput');
    let reportName = "";
    if (reportNameInput && reportNameInput.value.trim() !== "") {
      reportName = reportNameInput.value.trim();
    } else {
      reportName = data.tableName;
    }
    // 统计时间附注
    const statTimeEl = document.getElementById('statTime');
    let annotation = "";
    if (statTimeEl && statTimeEl.value.trim() !== "") {
      annotation = "统计时间：" + statTimeEl.value.trim();
    }
    // 设置标题区域：左侧显示报表名称（居中可通过CSS调整），右侧显示附注（右对齐）
    titleEl.textContent = reportName;
    timeAnnotationEl.textContent = annotation;

    if (!data.rows || data.rows.length === 0) {
      tbodyEl.innerHTML = "";
      return;
    }
    let bodyHTML = "";
    data.rows.forEach(row => {
      bodyHTML += "<tr>";
      bodyHTML += `<td>${row.row_name || ""}</td>`;
      bodyHTML += `<td>${row.pre_clinic_count || 0}</td>`;
      bodyHTML += `<td>${(typeof row.pre_clinic_ratio === "number") ? row.pre_clinic_ratio.toFixed(2) + "%" : row.pre_clinic_ratio}</td>`;
      bodyHTML += `<td>${row.mild_count || 0}</td>`;
      bodyHTML += `<td>${(typeof row.mild_ratio === "number") ? row.mild_ratio.toFixed(2) + "%" : row.mild_ratio}</td>`;
      bodyHTML += `<td>${row.moderate_count || 0}</td>`;
      bodyHTML += `<td>${(typeof row.moderate_ratio === "number") ? row.moderate_ratio.toFixed(2) + "%" : row.moderate_ratio}</td>`;
      bodyHTML += `<td>${row.bad_vision_count || 0}</td>`;
      bodyHTML += `<td>${(typeof row.bad_vision_ratio === "number") ? row.bad_vision_ratio.toFixed(2) + "%" : row.bad_vision_ratio}</td>`;
      bodyHTML += `<td>${row.total_count || 0}</td>`;
      bodyHTML += "</tr>";
    });
    tbodyEl.innerHTML = bodyHTML;
  }

  function renderReportPagination(total) {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl) return;
    paginationEl.innerHTML = '';
    const totalPages = Math.ceil(total / perPage);
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement('li');
      li.className = 'page-item' + (i === currentPage ? ' active' : '');
      li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
      li.addEventListener('click', (e) => {
        e.preventDefault();
        currentPage = i;
        fetchReportData();
      });
      paginationEl.appendChild(li);
    }
  }

  function fetchReportData() {
    const params = getReportQueryParams();
    params.append('page', currentPage);
    params.append('per_page', perPage);
    fetch('/api/analysis/report?' + params.toString())
      .then(res => res.json())
      .then(result => {
        if (result.error) {
          alert("报表查询错误: " + result.error);
          return;
        }
        latestReportData = result;
        renderReportHeader(result);
        renderReportTable(result);
        const totalRows = result.total !== undefined ? result.total : (result.rows ? result.rows.length : 0);
        renderReportPagination(totalRows);
      })
      .catch(err => {
        console.error("报表查询请求错误:", err);
        alert("报表查询请求错误，请检查控制台");
      });
  }
  window.fetchData = fetchReportData;

  // 模板下拉框 change 事件：自动查询或清空报表
  const templateSelect = document.getElementById('templateSelect');
  if (templateSelect) {
    templateSelect.addEventListener('change', function () {
      if (templateSelect.value) {
        currentPage = 1;
        fetchReportData();
      } else {
        // 选择取消时清空报表区域
        document.getElementById('reportTitle').textContent = "";
        document.getElementById('reportTimeAnnotation').textContent = "";
        document.getElementById('reportTableHead').innerHTML = "";
        document.getElementById('reportTableBody').innerHTML = "";
        document.getElementById('pagination').innerHTML = "";
      }
    });
  }

  // 查询按钮事件
  const reportSearchBtn = document.getElementById('reportSearchBtn');
  if (reportSearchBtn) {
    reportSearchBtn.addEventListener('click', () => {
      currentPage = 1;
      fetchReportData();
    });
  }
  // 导出按钮事件
  const exportReportBtn = document.getElementById('exportReportBtn');
  if (exportReportBtn) {
    exportReportBtn.addEventListener('click', () => {
      const params = getReportQueryParams();
      window.location.href = '/api/analysis/export?' + params.toString();
    });
  }
  // 切换到图表页面按钮
  const toChartBtn = document.getElementById('toChartBtn');
  if (toChartBtn) {
    toChartBtn.addEventListener('click', () => {
      window.location.href = "/chart";
    });
  }
  // 统一取消按钮：清除所有固定查询条件、组合查询条件、模板、统计时间和报表显示
  const clearBtn = document.getElementById('clearBtn');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      validParams.forEach(param => {
        const element = document.getElementById(param);
        if (element) element.value = "";
      });
      const comboConditionsInput = document.getElementById('comboConditions');
      if (comboConditionsInput) comboConditionsInput.value = "";
      const advancedContainer = document.getElementById('advancedQueryContainer');
      if (advancedContainer) advancedContainer.innerHTML = "";
      const templateSelect = document.getElementById('templateSelect');
      if (templateSelect) templateSelect.value = "";
      const statTimeEl = document.getElementById('statTime');
      if (statTimeEl) statTimeEl.value = "";
      const reportNameInput = document.getElementById('reportNameInput');
      if (reportNameInput) reportNameInput.value = "";
      document.getElementById('reportTitle').textContent = "";
      document.getElementById('reportTimeAnnotation').textContent = "";
      document.getElementById('reportTableHead').innerHTML = "";
      document.getElementById('reportTableBody').innerHTML = "";
      document.getElementById('pagination').innerHTML = "";
    });
  }
  // 页面初始保持空白，不自动查询
});
