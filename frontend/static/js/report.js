#!/usr/bin/env node
/**
 * 文件名称: report.js
 * 完整存储路径: frontend/static/js/report.js
 *
 * 功能说明:
 *   1. 根据用户选择的查询模式（预设模板 / 自定义查询），收集查询参数并调用后端统计报表接口获取数据。
 *   2. 动态生成报表表头和数据行，支持分页、导出和切换到图表页面。
 *   3. 提供“取消”按钮，用于重置查询状态，清空固定查询和组合查询条件。
 *
 * 使用说明:
 *   - 在 report.html 中引入此脚本，配合 comboQuery_report.js 一同使用。
 *   - 页面必须包含以下 DOM 元素：
 *       * templateSelect (id="templateSelect")：用于选择预设模板
 *       * statTime (id="statTime")：统计时间下拉框
 *       * reportNameInput (id="reportNameInput")：自定义报表名称输入框
 *       * queryMode (id="queryMode")：查询模式切换下拉框（"template" or "custom"）
 *       * comboConditions (id="comboConditions")：隐藏输入框，存储组合查询条件 JSON
 *       * reportSearchBtn (id="reportSearchBtn")：查询按钮
 *       * exportReportBtn (id="exportReportBtn")：导出按钮
 *       * toChartBtn (id="toChartBtn")：切换到图表按钮
 *       * clearBtn (id="clearBtn")：取消（重置）按钮
 *       * reportTableHead (id="reportTableHead") / reportTableBody (id="reportTableBody")：表头和表体容器
 *       * pagination (id="pagination")：分页控件容器
 *
 * 注意:
 *   - 修改过程中必须保持原有功能不破坏，所有代码均符合最新标准并附有详细注释。
 *   - 在点击“查询”按钮后，若为自定义查询模式，则需先将 getComboConditions() 的结果写入 comboConditions，
 *     再调用 fetchReportData()，确保后端能获取 advanced_conditions。
 */

document.addEventListener('DOMContentLoaded', function () {
  // 固定查询字段名称（如需要，可根据需求扩展或调整）
  const validParams = ['education_id', 'school', 'grade', 'class_name', 'name', 'gender', 'id_card'];

  // 当前分页状态
  let currentPage = 1;
  const perPage = 10;
  let latestReportData = null;

  /**
   * 获取报表查询参数
   * 1. 读取固定查询字段
   * 2. 根据 queryMode 下拉框的值，决定是使用 template 参数还是 advanced_conditions
   * 3. 若 queryMode = "template"，传 template；若 queryMode = "custom"，传 advanced_conditions
   */
  function getReportQueryParams() {
    const params = new URLSearchParams();

    // 1. 读取固定查询字段
    validParams.forEach(param => {
      const element = document.getElementById(param);
      if (element) {
        const value = element.value.trim();
        if (value) {
          params.append(param, value);
        }
      }
    });

    // 2. 读取统计时间
    const statTimeEl = document.getElementById('statTime');
    if (statTimeEl && statTimeEl.value.trim() !== "") {
      params.append('stat_time', statTimeEl.value.trim());
    }

    // 3. 根据查询模式决定传 template 还是 advanced_conditions
    const queryModeEl = document.getElementById('queryMode');
    const queryMode = queryModeEl ? queryModeEl.value.trim() : "template";

    if (queryMode === "template") {
      // 模板模式：使用模板参数，不传 advanced_conditions
      const templateSelect = document.getElementById('templateSelect');
      if (templateSelect && templateSelect.value) {
        params.append('template', templateSelect.value);
      }
    } else if (queryMode === "custom") {
      // 自定义查询模式：传 advanced_conditions
      const comboConditionsInput = document.getElementById('comboConditions');
      if (comboConditionsInput && comboConditionsInput.value.trim() !== "") {
        params.append('advanced_conditions', comboConditionsInput.value.trim());
      }
    }
    return params;
  }

  /**
   * 修改后的 renderReportHeader 函数：
   * 根据后端返回的表头数据动态生成表头HTML。
   * 若 headerData 为多层结构，需要处理 colspan/rowspan。
   * 目前示例中仅简单拼接字符串，后续可改造成更灵活的多层表头处理。
   */
  function renderReportHeader(data) {
    const theadEl = document.getElementById('reportTableHead');
    let headerHtml = "";
    const header = data.header;

    if (Array.isArray(header)) {
      for (let i = 0; i < header.length; i++) {
        headerHtml += "<tr>";
        for (let j = 0; j < header[i].length; j++) {
          let cell = header[i][j];
          if (typeof cell === "object" && cell !== null) {
            let text = cell.text || "";
            let colspan = cell.colspan ? ` colspan="${cell.colspan}"` : "";
            let rowspan = cell.rowspan ? ` rowspan="${cell.rowspan}"` : "";
            headerHtml += `<th${colspan}${rowspan}>${text}</th>`;
          } else {
            headerHtml += `<th>${cell}</th>`;
          }
        }
        headerHtml += "</tr>";
      }
      theadEl.innerHTML = headerHtml;
    } else {
      theadEl.innerHTML = `<tr><th>${header}</th></tr>`;
    }
  }

  /**
   * 渲染报表表格数据行
   * 若 data.rows 存在，则生成表格；否则清空
   */
  function renderReportTable(data) {
    const titleEl = document.getElementById('reportTitle');
    const timeAnnotationEl = document.getElementById('reportTimeAnnotation');
    const tbodyEl = document.getElementById('reportTableBody');
    if (!data) return;

    // 读取自定义报表名称
    const reportNameInput = document.getElementById('reportNameInput');
    let reportName = "";
    if (reportNameInput && reportNameInput.value.trim() !== "") {
      reportName = reportNameInput.value.trim();
    } else {
      reportName = data.tableName;
    }
    // 读取统计时间
    const statTimeEl = document.getElementById('statTime');
    let annotation = "";
    if (statTimeEl && statTimeEl.value.trim() !== "") {
      annotation = "统计时间：" + statTimeEl.value.trim();
    }
    titleEl.textContent = reportName || "";
    timeAnnotationEl.textContent = annotation;

    if (!data.rows || data.rows.length === 0) {
      tbodyEl.innerHTML = "";
      return;
    }
    let bodyHTML = "";
    data.rows.forEach(row => {
      bodyHTML += "<tr>";
      // 依次输出每列数据
      // 以下示例字段需根据后端返回的 row 对象属性进行拼接
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

  /**
   * 渲染分页控件
   */
  function renderReportPagination(total) {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl) return;
    paginationEl.innerHTML = '';
    const totalPages = Math.ceil(total / perPage);
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement('li');
      li.className = 'page-item' + (i === currentPage ? ' active' : '');
      li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
      li.addEventListener('click', function (e) {
        e.preventDefault();
        currentPage = i;
        fetchReportData();
      });
      paginationEl.appendChild(li);
    }
  }

  /**
   * 发起报表查询请求
   */
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
        // 渲染表头
        renderReportHeader(result);
        // 渲染表格
        renderReportTable(result);
        // 渲染分页
        const totalRows = (result.total !== undefined) ? result.total : (result.rows ? result.rows.length : 0);
        renderReportPagination(totalRows);
      })
      .catch(err => {
        console.error("报表查询请求错误:", err);
        alert("报表查询请求错误，请检查控制台");
      });
  }
  // 将 fetchReportData 挂载到全局 window 对象，供外部调用
  window.fetchData = fetchReportData;

  // 监听模板下拉框和查询模式下拉框的变化
  const templateSelect = document.getElementById('templateSelect');
  const queryModeEl = document.getElementById('queryMode');
  if (templateSelect) {
    templateSelect.addEventListener('change', function () {
      // 当处于模板模式且选择了模板，自动查询
      if (queryModeEl && queryModeEl.value === "template" && templateSelect.value) {
        currentPage = 1;
        fetchReportData();
      }
    });
  }
  if (queryModeEl) {
    queryModeEl.addEventListener('change', function () {
      // 切换查询模式时，禁用或启用模板下拉框
      if (queryModeEl.value === "template") {
        const comboConditionsInput = document.getElementById('comboConditions');
        if (comboConditionsInput) {
          comboConditionsInput.value = "";
        }
        if (templateSelect) {
          templateSelect.disabled = false;
        }
      } else if (queryModeEl.value === "custom") {
        if (templateSelect) {
          templateSelect.disabled = true;
          templateSelect.value = "";
        }
      }
    });
  }

  // 监听“查询”按钮
  const reportSearchBtn = document.getElementById('reportSearchBtn');
  if (reportSearchBtn) {
    reportSearchBtn.addEventListener('click', () => {
      // 先将组合查询条件写入 comboConditions
      const conditions = getComboConditions(); // 来自 comboQuery_report.js
      const comboConditionsInput = document.getElementById('comboConditions');
      if (comboConditionsInput) {
        comboConditionsInput.value = JSON.stringify(conditions);
      }
      currentPage = 1;
      fetchReportData();
    });
  }

  // 监听“导出”按钮
  const exportReportBtn = document.getElementById('exportReportBtn');
  if (exportReportBtn) {
    exportReportBtn.addEventListener('click', () => {
      const conditions = getComboConditions(); // 来自 comboQuery_report.js
      const comboConditionsInput = document.getElementById('comboConditions');
      if (comboConditionsInput) {
        comboConditionsInput.value = JSON.stringify(conditions);
      }
      const params = getReportQueryParams();
      window.location.href = '/api/analysis/export?' + params.toString();
    });
  }

  // 监听“查看图表”按钮
  const toChartBtn = document.getElementById('toChartBtn');
  if (toChartBtn) {
    toChartBtn.addEventListener('click', () => {
      window.location.href = "/chart";
    });
  }

  // 监听“取消”按钮：清空查询状态
  const clearBtn = document.getElementById('clearBtn');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      // 重置固定查询输入
      const validParams = ['education_id', 'school', 'grade', 'class_name', 'name', 'gender', 'id_card'];
      validParams.forEach(param => {
        const element = document.getElementById(param);
        if (element) element.value = "";
      });
      // 重置统计时间和报表名称
      const statTimeEl = document.getElementById('statTime');
      if (statTimeEl) statTimeEl.value = "";
      const reportNameInput = document.getElementById('reportNameInput');
      if (reportNameInput) reportNameInput.value = "";
      // 重置组合查询条件
      const comboConditionsInput = document.getElementById('comboConditions');
      if (comboConditionsInput) comboConditionsInput.value = "";
      // 清空动态生成的查询条件行
      const advancedContainer = document.getElementById('advancedQueryContainer');
      if (advancedContainer) advancedContainer.innerHTML = "";
      // 恢复查询模式为模板，并清空模板下拉
      if (queryModeEl) {
        queryModeEl.value = "template";
      }
      if (templateSelect) {
        templateSelect.disabled = false;
        templateSelect.value = "";
      }
      // 清空报表展示区
      document.getElementById('reportTitle').textContent = "";
      document.getElementById('reportTimeAnnotation').textContent = "";
      document.getElementById('reportTableHead').innerHTML = "";
      document.getElementById('reportTableBody').innerHTML = "";
      document.getElementById('pagination').innerHTML = "";
    });
  }
});
