/**
 * 文件名称: report.js
 * 完整路径: frontend/static/js/report.js
 * 功能说明: 
 *  动态生成统计报表，支持多层表头、分页和导出
 * 修改记录:
 *  2024-03-20 新增三层表头支持
 *  2024-03-20 优化合计行显示
 */

document.addEventListener('DOMContentLoaded', function () {
    const validParams = ['education_id', 'school', 'grade', 'class_name', 'name', 'gender', 'id_card'];
    let currentPage = 1;
    const perPage = 10;
    let latestReportData = null;

    // 完整保留原有getReportQueryParams函数
    function getReportQueryParams() {
        const params = new URLSearchParams();
        validParams.forEach(param => {
            const el = document.getElementById(param);
            if (el && el.value.trim()) params.append(param, el.value.trim());
        });
        
        const statTimeEl = document.getElementById('statTime');
        if (statTimeEl && statTimeEl.value.trim()) {
            params.append('stat_time', statTimeEl.value.trim());
        }

        const queryMode = document.getElementById('queryMode').value.trim();
        if (queryMode === "template") {
            const templateSelect = document.getElementById('templateSelect');
            if (templateSelect.value) params.append('template', templateSelect.value);
        } else {
            const comboConditions = document.getElementById('comboConditions');
            if (comboConditions.value.trim()) {
                params.append('advanced_conditions', comboConditions.value.trim());
            }
        }
        return params;
    }

    // 完整重写表头渲染
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

    // 完整重写数据渲染
    function renderReportTable(data) {
        const tbodyEl = document.getElementById('reportTableBody');
        tbodyEl.innerHTML = '';
        
        data.rows.forEach(row => {
            const tr = document.createElement('tr');
            
            // 分组列
            const groupCell = document.createElement('td');
            groupCell.textContent = row.row_name;
            tr.appendChild(groupCell);
            
            // 动态指标列
            Object.keys(row).forEach(key => {
                if (key !== 'row_name' && key !== 'total_count') {
                    const td = document.createElement('td');
                    const value = row[key];
                    td.textContent = typeof value === 'number' ? 
                        (key.endsWith('_ratio') ? value.toFixed(2) + '%' : value) : 
                        value;
                    td.style.textAlign = 'center';
                    tr.appendChild(td);
                }
            });
            
            // 总数列
            const totalCell = document.createElement('td');
            totalCell.textContent = row.total_count;
            tr.appendChild(totalCell);
            
            tbodyEl.appendChild(tr);
        });
    }

    // 完整保留分页渲染
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
