/*
文件名称: chart.js
完整存储路径: frontend/static/js/chart.js
功能说明:
    本文件用于图表展示页面的前端交互逻辑，主要功能包括：
      1. 收集图表展示页面的查询条件，包括固定查询字段、统计时间、报表名称、查询模式、组合查询条件及图表类型选择值，
         构造统一的 URL 查询参数。
      2. 调用后端 /api/analysis/chart 接口获取数据，并根据返回的数据使用 Chart.js 渲染图表。
      3. 针对饼图类型，通过动态添加自定义 CSS 类（.pie-chart）确保饼图以固定正方形居中显示，保证完整的圆形效果。
      4. 绑定导出图表、查询、图表类型切换、跳转到统计报表页面及查询区域取消按钮的事件处理，确保各交互功能正常工作。
使用说明:
    - 页面中需包含 id 为 "analysisChart" 的 <canvas> 元素用于图表渲染。
    - 页面必须引入共享的组合查询模块（comboQuery_report.js），保证查询条件一致。
    - 依赖 Chart.js 库，请确保页面中已正确加载 Chart.js。
    - 当图表类型为饼图时，需要在外部 CSS 文件中定义 .pie-chart 类，例如：
         .pie-chart {
             width: 400px !important;
             height: 400px !important;
             display: block;
             margin: 0 auto;
         }
*/

document.addEventListener("DOMContentLoaded", function () {
  "use strict";

  // 获取图表画布及图表实例变量
  const chartCanvas = document.getElementById("analysisChart");
  let analysisChart = null;

  /**
   * 获取当前图表展示页面的查询参数
   * 收集固定查询字段、统计时间、报表名称、查询模式、组合查询条件及图表类型选择值，
   * 返回一个 URLSearchParams 对象，供数据请求使用。
   *
   * @returns {URLSearchParams} 查询参数集合
   */

  function getChartQueryParams() {
    // 调用全局函数 getReportQueryParams() 获取统一的查询参数
    const params = getReportQueryParams();

    // 追加图表类型参数，因为全局函数中没有处理该参数
    const chartTypeElement = document.getElementById("chartType");
    if (chartTypeElement && chartTypeElement.value.trim() !== "") {
      // 使用 set() 确保如果已存在就覆盖
      params.set("chart_type", chartTypeElement.value.trim());
    }

    // 如果 URL 中没有 group_by 和 metric，则添加默认值（用于测试）
    if (!params.has("group_by")) {
      params.append("group_by", "school");
    }
    if (!params.has("metric")) {
      params.append("metric", "left_interv_effect");
    }

    console.log("Chart Query Params: " + params.toString());
    return params;
  }

  /**
   * 请求图表数据并渲染图表
   * 构造请求 URL 后调用后端 /api/analysis/chart 接口，
   * 获取返回数据后调用 renderChart() 进行图表渲染。
   */
  function fetchChartData() {
    const params = getChartQueryParams();
    const requestUrl = "/api/analysis/chart?" + params.toString();

    fetch(requestUrl)
      .then(function (response) {
        if (!response.ok) {
          throw new Error("网络响应错误，状态码: " + response.status);
        }
        return response.json();
      })
      .then(function (data) {
        if (data.error) {
          alert("图表数据错误: " + data.error);
          return;
        }
        renderChart(data);
      })
      .catch(function (error) {
        console.error("图表请求错误:", error);
        alert("图表请求错误，请检查控制台日志");
      });
  }

  /**
   * 使用 Chart.js 渲染图表
   * 根据返回数据和图表类型选择值，在 canvas 上创建图表实例。
   * 针对饼图类型，添加自定义 CSS 类 "pie-chart" 以保证固定正方形尺寸和居中显示。
   *
   * @param {Object} data - 后端返回的图表数据，包含 labels 与 datasets 属性
   */
  function renderChart(data) {
    const ctx = chartCanvas.getContext("2d");

    // 如果已存在图表实例，先销毁
    if (analysisChart) {
      analysisChart.destroy();
    }

    // 获取图表类型，默认为 'bar'
    const chartTypeElement = document.getElementById("chartType");
    let chartType = "bar";
    if (chartTypeElement && chartTypeElement.value.trim() !== "") {
      chartType = chartTypeElement.value.trim();
    }

    // 针对饼图，添加或移除自定义类，以保证画布为固定正方形并居中显示
    if (chartType === "pie") {
      chartCanvas.classList.add("pie-chart");
    } else {
      chartCanvas.classList.remove("pie-chart");
    }

    // Chart.js 配置选项
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.dataset.label + ": " + context.parsed.y;
            },
          },
        },
        legend: {
          position: "bottom",
          align: "center",
        },
      },
      onClick: function (event, elements) {
        // 点击数据点后，跳转到统计报表页面，传递当前查询参数及点击数据值
        if (elements && elements.length > 0) {
          const index = elements[0].index;
          const label = data.labels[index];
          const currentParams = getChartQueryParams();
          currentParams.set("group_by", "school");
          currentParams.set("filter", label);
          const reportUrl = "/report?" + currentParams.toString();
          window.location.href = reportUrl;
        }
      },
    };

    // 对于饼图，强制保持1:1的纵横比
    if (chartType === "pie") {
      options.maintainAspectRatio = true;
      options.aspectRatio = 1;
    }

    // 创建图表实例
    analysisChart = new Chart(ctx, {
      type: chartType,
      data: {
        labels: data.labels,
        datasets: data.datasets,
      },
      options: options,
    });
  }

  /**
   * 清除查询区域所有输入
   * 清空固定查询字段、统计时间、报表名称、组合查询条件以及高级查询条件区域。
   */
  function clearQueryConditions() {
    // 固定查询字段
    const fixedParams = [
      "education_id",
      "school",
      "grade",
      "class_name",
      "data_year",
      "name",
      "gender",
      "id_card",
    ];
    fixedParams.forEach(function (param) {
      const element = document.getElementById(param);
      if (element) {
        element.value = "";
      }
    });
    // 统计时间
    const statTime = document.getElementById("statTime");
    if (statTime) {
      statTime.value = "";
    }
    // 报表名称
    const reportNameInput = document.getElementById("reportNameInput");
    if (reportNameInput) {
      reportNameInput.value = "";
    }
    // 查询模式
    const queryMode = document.getElementById("queryMode");
    if (queryMode) {
      queryMode.value = "template";
    }
    // 组合查询条件隐藏框
    const comboConditions = document.getElementById("comboConditions");
    if (comboConditions) {
      comboConditions.value = "";
    }
    // 高级查询条件区域
    const advancedQueryContainer = document.getElementById(
      "advancedQueryContainer"
    );
    if (advancedQueryContainer) {
      advancedQueryContainer.innerHTML = "";
    }
  }

  /**
   * 初始化图表展示页面的交互绑定
   * 包括查询、导出、图表类型切换、跳转到统计报表页面及查询区域取消按钮等事件绑定。
   */
  function initChartPage() {
    // 查询按钮绑定
    const reportSearchBtn = document.getElementById("reportSearchBtn");
    if (reportSearchBtn) {
      reportSearchBtn.addEventListener("click", function () {
        fetchChartData();
      });
    }

    // 导出图表按钮绑定：导出当前图表为 PNG 图片
    const exportChartBtn = document.getElementById("exportChartBtn");
    if (exportChartBtn) {
      exportChartBtn.addEventListener("click", function () {
        if (analysisChart) {
          const imageUrl = analysisChart.toBase64Image();
          const link = document.createElement("a");
          link.href = imageUrl;
          link.download = "chart.png";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        } else {
          alert("请先生成图表再导出");
        }
      });
    }

    // 切换到统计报表页面按钮绑定：传递当前查询参数后跳转
    const toReportBtn = document.getElementById("toReportBtn");
    if (toReportBtn) {
      toReportBtn.addEventListener("click", function () {
        const params = getChartQueryParams();
        window.location.href = "/report?" + params.toString();
      });
    }

    // 图表类型选择下拉框绑定：切换图表类型后重新请求数据
    const chartTypeElement = document.getElementById("chartType");
    if (chartTypeElement) {
      chartTypeElement.addEventListener("change", function () {
        fetchChartData();
      });
    }

    // 绑定查询区域取消按钮：清空所有查询条件
    const clearBtn = document.getElementById("clearBtn");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        clearQueryConditions();
      });
    }

    // 页面加载时自动请求图表数据
    fetchChartData();
  }

  // 初始化图表页面交互绑定
  initChartPage();
});
