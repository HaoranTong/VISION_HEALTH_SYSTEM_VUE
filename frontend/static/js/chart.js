/*
文件名称: chart.js
完整存储路径: frontend/static/js/chart.js
功能说明:
    实现图示展示页面的前端交互逻辑，主要功能包括：
      - 收集固定查询区域和组合查询条件（由 comboQuery.js 模块存入隐藏输入框 comboConditions）的参数，
      - 调用后端图表数据接口 (/api/analysis/chart) 获取图表数据，
      - 使用 Chart.js 绘制柱状图展示统计数据，
      - 支持图表交互（如鼠标悬停显示 tooltip）和切换到统计报表页面。
使用说明:
    在 chart.html 中通过 <script> 标签引入本文件，确保页面中存在 <canvas id="analysisChart"> 元素以及必要的查询控件。
*/
document.addEventListener('DOMContentLoaded', function () {
  const chartCanvas = document.getElementById('analysisChart');
  let analysisChart;

  function getChartQueryParams() {
    const params = new URLSearchParams();
    const validParams = ['education_id', 'school', 'grade', 'class_name', 'data_year', 'name', 'gender', 'id_card'];
    validParams.forEach(param => {
      const element = document.getElementById(param);
      if (element) {
        const value = element.value.trim();
        if (value) params.append(param, value);
      }
    });
    // 读取组合查询条件
    const comboConditionsInput = document.getElementById('comboConditions');
    if (comboConditionsInput && comboConditionsInput.value.trim() !== "") {
      params.append('advanced_conditions', comboConditionsInput.value.trim());
    }
    // 图表专用参数 (示例：按学校分组、统计左眼干预效果)
    params.append('group_by', 'school');
    params.append('metric', 'left_interv_effect');
    return params;
  }

  function fetchChartData() {
    const params = getChartQueryParams();
    fetch('/api/analysis/chart?' + params.toString())
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert("图表数据错误: " + data.error);
          return;
        }
        renderChart(data);
      })
      .catch(err => {
        console.error("图表请求错误:", err);
        alert("图表请求错误，请检查控制台");
      });
  }

  function renderChart(data) {
    const ctx = chartCanvas.getContext('2d');
    if (analysisChart) {
      analysisChart.destroy();
    }
    analysisChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: data.datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                return context.dataset.label + ": " + context.parsed.y;
              }
            }
          }
        }
      }
    });
  }

  // 切换到统计报表页面按钮
  const toReportBtn = document.getElementById('toReportBtn');
  if (toReportBtn) {
    toReportBtn.addEventListener('click', function () {
      window.location.href = "/report";
    });
  }

  fetchChartData();
});
