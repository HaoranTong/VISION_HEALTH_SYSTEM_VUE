// 文件名称：sidebar.js
// 完整存储路径：E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\frontend\static\components\sidebar\sidebar.js
// 功能说明：处理侧边栏的交互逻辑，包括折叠和展开功能
// 使用方法：
// - 在 HTML 文件中引入此 JavaScript 文件，确保路径正确。
// - 使用相应的 ID 和类名来绑定事件。

document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('toggleSidebar', () => {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
            const root = document.documentElement;
            if (sidebar.classList.contains('collapsed')) {
                root.style.setProperty('--sidebar-width', '60px');
            } else {
                root.style.setProperty('--sidebar-width', '250px');
            }
        } else {
            console.error('Sidebar element not found');
        }
    });
});