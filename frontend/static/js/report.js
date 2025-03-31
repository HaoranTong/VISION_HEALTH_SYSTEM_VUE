/**
 * 文件名称: report.js
 * 完整存储路径: frontend/static/js/report.js
 * 功能说明:
 *   此文件用于统计报表页面的查询、表头渲染、数据行渲染、分页生成以及报表导出功能。
 *   修改内容包括：
 *     - 在查询前增加参数验证，确保至少选择一个分组和一个统计指标，
 *       同时对支持二级选项或需要输入的字段进行有效性检查，并弹出提示。
 *     - 对查询参数的收集、分页、报表导出等功能保持原有逻辑。
 * 使用说明:
 *   页面通过该脚本收集用户查询条件，调用 /api/analysis/report 接口获取统计数据，
 *   并动态生成报表表头和数据表格。支持分页、导出报表以及查询模式（预设模板与自定义查询）的切换。
 */

// import { getReportQueryParams } from './comboQuery_report.js';

document.addEventListener("DOMContentLoaded", function () {
  const validParams = [
    "education_id",
    "school",
    "grade",
    "class_name",
    "name",
    "gender",
    "id_card",
  ];
  let currentPage = 1;
  const perPage = 10;
  let latestReportData = null;
  let isLoading = false;

  function showLoading() {
    isLoading = true;
    document.getElementById("loading").style.display = "block";
  }

  function hideLoading() {
    isLoading = false;
    document.getElementById("loading").style.display = "none";
  }

  /**
   * 获取报表查询的 URL 参数
   */
  // ----------------------
  // 以下为原 report.js 中的 getReportQueryParams() 定义，现已移动到 comboQuery_report.js 模块中，所以此处删除或注释掉
  /*
  function getReportQueryParams() {
    const params = new URLSearchParams();
    validParams.forEach((param) => {
      const el = document.getElementById(param);
      if (el && el.value.trim()) {
        params.append(param, el.value.trim());
      }
    });
    const statTimeEl = document.getElementById("statTime");
    if (statTimeEl && statTimeEl.value.trim()) {
      params.append("stat_time", statTimeEl.value.trim());
    }
    // 明确传递查询模式
    const queryModeEl = document.getElementById("queryMode");
    if (queryModeEl) {
      params.append("query_mode", queryModeEl.value.trim());
    }
    if (queryModeEl.value.trim() === "template") {
      const templateSelect = document.getElementById("templateSelect");
      if (templateSelect.value) {
        params.append("template", templateSelect.value);
      }
    } else {
      // 自定义查询模式，从组合查询模块获取条件
      if (typeof getComboConditions === "function") {
        const comboConds = getComboConditions();
        if (comboConds && comboConds.length > 0) {
          // === 插入开始：干预方式字段映射 ===
          comboConds.forEach((cond) => {
            if (cond.field === "intervention_methods") {
              // 将中文标签映射回字段名
              cond.value = cond.value.map((v) => {
                const field = Object.keys(
                  comboQueryConfig.intervention_methods.labels
                ).find(
                  (key) =>
                    comboQueryConfig.intervention_methods.labels[key] === v
                );
                return field || v;
              });
            }
          });
          // === 插入结束 ===
          params.append("advanced_conditions", JSON.stringify(comboConds));
        }
      }
    }
    const reportNameInput = document.getElementById("reportNameInput");
    if (reportNameInput && reportNameInput.value.trim()) {
      params.append("report_name", reportNameInput.value.trim());
    }
    return params;
  }
  */

  /**
   * 验证统计报表查询的必选参数：
   * 1. 当查询模式为“预设模板”时，必须选择一个有效的模板；
   * 2. 当查询模式为“自定义查询”时，隐藏输入框 comboConditions 中必须包含至少一个分组条件和至少一个统计指标条件，
   *    且每个条件的 field、operator 和 value 必须非空。
   * 返回：
   *   true：验证通过； false：验证失败，并弹出相应提示信息。
   */
  function validateReportParams() {
    const queryModeEl = document.getElementById("queryMode");
    if (!queryModeEl) {
      alert("查询模式未设置，请检查页面布局");
      return false;
    }
    const mode = queryModeEl.value.trim();
    if (mode === "template") {
      // 预设模板模式：模板下拉框必须选择有效值
      const templateSelect = document.getElementById("templateSelect");
      if (!templateSelect || !templateSelect.value) {
        alert("请选择有效的预设模板");
        return false;
      }
    } else if (mode === "custom") {
      // 自定义查询模式：必须有 advanced_conditions 参数
      const comboConditionsInput = document.getElementById("comboConditions");
      if (!comboConditionsInput) {
        alert("组合查询条件未找到，请检查页面布局");
        return false;
      }
      let conditions = [];
      try {
        if (comboConditionsInput.value.trim() !== "") {
          conditions = JSON.parse(comboConditionsInput.value.trim());
        }
      } catch (e) {
        alert("组合查询条件格式错误");
        return false;
      }
      let hasGroup = false;
      let hasMetric = false;
      // 遍历每个条件，检查字段、运算符、值是否有效
      for (const cond of conditions) {
        if (
          !cond.field ||
          !cond.operator ||
          cond.value === null ||
          cond.value === "" ||
          (Array.isArray(cond.value) && cond.value.length === 0)
        ) {
          alert("请选择二级选项或填写数值或文本");
          return false;
        }
        const role = cond.role ? cond.role.toLowerCase() : "";
        if (role === "group") {
          hasGroup = true;
        }
        if (role === "metric") {
          hasMetric = true;
        }
      }
      if (!hasGroup || !hasMetric) {
        alert("请选择统计指标或分组");
        return false;
      }
    } else {
      alert("无效的查询模式");
      return false;
    }
    return true;
  }

  function renderReportHeader(data) {
    const theadEl = document.getElementById("reportTableHead");
    theadEl.innerHTML = "";
    data.header.forEach((headerRow) => {
      const tr = document.createElement("tr");
      headerRow.forEach((cell) => {
        const th = document.createElement("th");
        th.textContent = cell.text;
        th.colSpan = cell.colspan || 1;
        th.rowSpan = cell.rowspan || 1;
        th.style.cssText = "text-align: center; vertical-align: middle;";
        tr.appendChild(th);
      });
      theadEl.appendChild(tr);
    });
  }

  function renderReportTable(data) {
    const tbodyEl = document.getElementById("reportTableBody");
    tbodyEl.innerHTML = "";
    data.rows.forEach((rowArray) => {
      const tr = document.createElement("tr");
      rowArray.forEach((cellValue, idx) => {
        const td = document.createElement("td");
        if (idx === 0 || idx === rowArray.length - 1) {
          td.textContent = cellValue;
        } else {
          if ((idx - 1) % 2 === 0) {
            td.textContent = cellValue;
          } else {
            td.textContent = `${cellValue}%`;
          }
        }
        td.style.textAlign = "center";
        tr.appendChild(td);
      });
      tbodyEl.appendChild(tr);
    });
  }

  function renderReportPagination(total) {
    const paginationEl = document.getElementById("pagination");
    paginationEl.innerHTML = "";
    const totalPages = Math.ceil(total / perPage);
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement("li");
      li.className = `page-item ${i === currentPage ? "active" : ""}`;
      li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
      li.addEventListener("click", function (e) {
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
    params.append("page", currentPage);
    params.append("per_page", perPage);
    fetch(`/api/analysis/report?${params.toString()}`)
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP错误 ${response.status}`);
        return response.json();
      })
      .then((data) => {
        if (data.error) throw new Error(data.error);
        latestReportData = data;

        const fieldNameMap = {
          vision_level: "视力等级",
          intervention_methods: "干预方式",
          gender: "性别",
          age: "年龄",
          school: "学校",
          grade: "年级",
          data_year: "数据年份",
          interv_vision_level: "干预后视力等级",
          left_eye_naked: "左眼裸眼视力",
          right_eye_naked: "右眼裸眼视力",
          left_eye_naked_interv: "左眼干预后裸眼视力",
          right_eye_naked_interv: "右眼干预后裸眼视力",
          guasha: "刮痧",
          aigiu: "艾灸",
          zhongyao_xunzheng: "中药熏蒸",
          rejiu_training: "热灸训练",
          xuewei_tiefu: "穴位贴敷",
          reci_pulse: "热磁脉冲",
          baoguan: "拔罐",
          frame_glasses: "框架眼镜",
          contact_lenses: "隐形眼镜",
          night_orthokeratology: "夜戴角膜塑型镜",
        };

        document.getElementById("reportTitle").textContent = data.tableName;
        document.getElementById("reportTimeAnnotation").textContent =
          data.filterAnnotation;
        renderReportHeader(data);
        renderReportTable(data);
        renderReportPagination(data.total || data.total);
      })
      .catch((error) => {
        console.error("请求失败:", error);
        alert(`查询失败: ${error.message}`);
      })
      .finally(() => hideLoading());
  }

  // 绑定查询按钮事件：在点击前先验证参数
  const reportSearchBtn = document.getElementById("reportSearchBtn");
  if (reportSearchBtn) {
    reportSearchBtn.addEventListener("click", () => {
      // 注释掉验证逻辑后测试，请确保后续恢复验证逻辑
      // if (!validateReportParams()) {
      //   return; // 验证失败则停止查询
      // }
      currentPage = 1;
      fetchReportData();
    });
  }

  const clearBtn = document.getElementById("clearBtn");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      validParams.forEach((param) => {
        const el = document.getElementById(param);
        if (el) el.value = "";
      });
      document.getElementById("statTime").value = "";
      document.getElementById("reportNameInput").value = "";
      document.getElementById("comboConditions").value = "";
      document.getElementById("advancedQueryContainer").innerHTML = "";
      document.getElementById("queryMode").value = "template";
      document.getElementById("templateSelect").disabled = false;
      document.getElementById("templateSelect").value = "";
      document.getElementById("reportTitle").textContent = "";
      document.getElementById("reportTimeAnnotation").textContent = "";
      document.getElementById("reportTableHead").innerHTML = "";
      document.getElementById("reportTableBody").innerHTML = "";
      document.getElementById("pagination").innerHTML = "";
    });
  }

  const templateSelect = document.getElementById("templateSelect");
  if (templateSelect) {
    templateSelect.addEventListener("change", function () {
      if (
        document.getElementById("queryMode").value === "template" &&
        templateSelect.value
      ) {
        currentPage = 1;
        fetchReportData();
      }
    });
  }

  const queryModeEl = document.getElementById("queryMode");
  if (queryModeEl) {
    queryModeEl.addEventListener("change", function () {
      if (queryModeEl.value === "template") {
        document.getElementById("comboConditions").value = "";
        document.getElementById("templateSelect").disabled = false;
      } else {
        document.getElementById("templateSelect").disabled = true;
        document.getElementById("templateSelect").value = "";
      }
    });
  }

  // 导出报表函数（已实现导出功能，但格式问题需后续优化）
  function exportReport() {
    console.log("导出报表按钮被点击");
    if (!latestReportData) {
      alert("请先查询数据再导出");
      return;
    }
    const params = getReportQueryParams();
    params.append("export", "true");
    const exportUrl = `/api/analysis/report?${params.toString()}`;
    window.location.href = exportUrl;
  }

  const exportReportBtn = document.getElementById("exportReportBtn");
  if (exportReportBtn) {
    exportReportBtn.addEventListener("click", exportReport);
  }

  // 在 DOMContentLoaded 事件内添加以下代码
  const toChartBtn = document.getElementById("toChartBtn");
  if (toChartBtn) {
    toChartBtn.addEventListener("click", () => {
      const params = getReportQueryParams();
      params.delete("page");
      params.delete("per_page");
      window.location.href = `/chart?${params.toString()}`;
    });
  }
});
