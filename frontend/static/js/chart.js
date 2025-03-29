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

/**
 * 显示全局加载状态
 */
function showLoading() {
  document.getElementById("loading").style.display = "block";
}

/**
 * 隐藏全局加载状态
 */
function hideLoading() {
  document.getElementById("loading").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
  "use strict";

  // 获取图表画布及图表实例变量
  const chartCanvas = document.getElementById("analysisChart");
  let analysisChart = null;

  /**
   * 获取当前图表展示页面的查询参数
   * 调用全局函数 getReportQueryParams() 获取统一的查询参数，并追加图表类型参数
   *
   * @returns {URLSearchParams} 查询参数集合
   */
  function getChartQueryParams() {
    const params = getReportQueryParams();
    const chartTypeElement = document.getElementById("chartType");
    if (chartTypeElement && chartTypeElement.value.trim() !== "") {
      params.set("chart_type", chartTypeElement.value.trim());
    }
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
   * 处理图表数据请求或渲染过程中发生的错误
   * @param {Error} error - 捕获的异常对象
   */
  function handleError(error) {
    console.error("Chart Error:", error);
    hideLoading();
    alert("图表加载失败，请稍后重试！");
  }

  /**
   * 请求图表数据并渲染图表
   * 获取返回数据后调用 renderChart() 进行图表渲染
   */
  function fetchChartData() {
    const params = getChartQueryParams();
    params.set("chart_type", document.getElementById("chartType").value);

    console.log("fetchChartData called with params:", params.toString());

    fetch(`/api/analysis/chart?${params.toString()}`)
      .then((response) => {
        console.log("Response received:", response);
        if (!response.ok) throw new Error(`HTTP错误 ${response.status}`);
        return response.json();
      })
      .then((data) => {
        console.log("Data received:", data);
        // 将合计数据添加到 labels 和 datasets 中
        data.labels.push("合计"); // 将“合计”添加到 labels 数组

        // 确保合计数据添加到 datasets 的每个数据集中
        data.datasets.forEach((dataset, index) => {
          // 假设每个 dataset 的 data 数组中有与“合计”对应的统计数据
          // 这里直接将 aggregate 数据中的值添加到对应位置（如 index 1，3，5 等）
          dataset.data.push(data.aggregate[index * 2 + 1]); // 取合计值的数量部分
        });
        // 构造图表配置
        const config = {
          type: data.chart_type || "bar",
          data: {
            labels: data.labels, // 返回的 labels 数组中，最后一项为“合计”
            datasets: data.datasets,
          },
          options: getChartOptions(data.chart_type),
        };
        renderChart(config);
        // 不再需要调用 showAggregateInfo，因为合计数据已经作为普通分组在横坐标中展示
      })
      .catch(handleError)
      .finally(hideLoading);
  }

  function getChartOptions(chartType) {
    return {
      responsive: true,
      plugins: {
        title: { display: true, text: "视力统计图表" },
        tooltip: {
          callbacks: {
            label: (ctx) =>
              `${ctx.dataset.label}: ${ctx.raw}人 (${(
                (ctx.raw / ctx.dataset.data.reduce((a, b) => a + b)) *
                100
              ).toFixed(2)}%)`,
          },
        },
      },
    };
  }

  /**
   * 使用 Chart.js 渲染图表
   * 根据返回数据和图表类型选择值，在 canvas 上创建图表实例。
   * 针对饼图类型，添加自定义 CSS 类 "pie-chart" 以保证固定正方形尺寸和居中显示。
   *
   * @param {Object} config - Chart.js 配置对象
   */
  function renderChart(config) {
    console.log("renderChart: 开始渲染图表，配置参数：", config);

    const canvas = document.getElementById("analysisChart");
    if (!canvas) {
      console.error(
        "renderChart: 未找到 id 为 'analysisChart' 的 canvas 元素。"
      );
      return;
    }

    canvas.style.display = "block";
    canvas.style.width = "100%";
    canvas.style.height = "500px";

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      console.error("renderChart: 获取 canvas 2D 上下文失败。");
      return;
    }

    if (window.analysisChartInstance) {
      console.log("renderChart: 销毁现有图表实例。");
      window.analysisChartInstance.destroy();
    }

    try {
      window.analysisChartInstance = new Chart(ctx, config);
      console.log(
        "renderChart: 图表实例创建成功",
        window.analysisChartInstance
      );
    } catch (err) {
      console.error("renderChart: 创建图表实例时出错：", err);
    }
  }

  function clearQueryConditions() {
    console.log("clearQueryConditions called");
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
    const statTime = document.getElementById("statTime");
    if (statTime) {
      statTime.value = "";
    }
    const reportNameInput = document.getElementById("reportNameInput");
    if (reportNameInput) {
      reportNameInput.value = "";
    }
    const queryMode = document.getElementById("queryMode");
    if (queryMode) {
      queryMode.value = "template";
    }
    const templateSelect = document.getElementById("templateSelect");
    if (templateSelect) {
      templateSelect.value = "";
    }
    const comboConditions = document.getElementById("comboConditions");
    if (comboConditions) {
      comboConditions.value = "";
    }
    const advancedQueryContainer = document.getElementById(
      "advancedQueryContainer"
    );
    if (advancedQueryContainer) {
      advancedQueryContainer.innerHTML = "";
    }
    console.log("clearQueryConditions finished");
  }

  function initChartPage() {
    console.log("initChartPage executed");
    const reportSearchBtn = document.getElementById("reportSearchBtn");
    if (reportSearchBtn) {
      reportSearchBtn.addEventListener("click", function () {
        fetchChartData();
      });
    }
    const exportChartBtn = document.getElementById("exportChartBtn");
    if (exportChartBtn) {
      exportChartBtn.addEventListener("click", function () {
        console.log(
          "导出时 window.analysisChartInstance =",
          window.analysisChartInstance
        );
        if (analysisChart) {
          const imageUrl = window.analysisChartInstance.toBase64Image();
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
    const toReportBtn = document.getElementById("toReportBtn");
    if (toReportBtn) {
      toReportBtn.addEventListener("click", function () {
        const params = getChartQueryParams();
        window.location.href = "/report?" + params.toString();
      });
    }
    const chartTypeElement = document.getElementById("chartType");
    if (chartTypeElement) {
      chartTypeElement.addEventListener("change", function () {
        fetchChartData();
      });
    }
    const clearBtn = document.getElementById("clearBtn");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        clearQueryConditions();
      });
    }
    fetchChartData();
  }

  initChartPage();
});
