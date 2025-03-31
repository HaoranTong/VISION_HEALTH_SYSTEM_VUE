/*
文件名称: index.js
完整存储路径: frontend/static/js/index.js
功能说明:
    首页交互逻辑，利用 Chart.js 初始化并展示统计图表。该脚本在首页加载后自动执行，
    后续如需动态更新数据，可进一步扩展相应交互功能。
使用方法:
    在首页(index.html)中通过 <script> 标签引入该文件。
*/

/* 确保 DOM 加载完成后执行 */
document.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('visionChart');
    if (!canvas) {
        console.error("未找到用于展示图表的 canvas 元素！");
        return;
    }
    var ctx = canvas.getContext('2d');
    // 使用 Chart.js 初始化图表（示例数据，后续可替换为动态数据）
    var visionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['左眼', '右眼'],
            datasets: [{
                label: '平均裸眼视力',
                data: [1.2, 1.3],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
});
