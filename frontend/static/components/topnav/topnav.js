// 文件名称：topnav.js
// 完整存储路径：E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\frontend\static\components\topnav\topnav.js
// 功能说明：处理顶部导航栏的交互逻辑，包括全屏功能、用户下拉菜单和侧边栏折叠功能
// 使用方法：
// - 在 HTML 文件中引入此 JavaScript 文件，确保路径正确。
// - 使用相应的 ID 和类名来绑定事件。

document.addEventListener('DOMContentLoaded', () => {
    // 侧边栏折叠功能
    const toggleSidebarBtn = document.getElementById('toggleSidebar');
    toggleSidebarBtn.addEventListener('click', () => {
        document.dispatchEvent(new CustomEvent('toggleSidebar'));
    });

    // 全屏功能
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    fullscreenBtn.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    });

    // 用户头像下拉菜单功能
    const userMenu = document.querySelector('.user-menu');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    userMenu.addEventListener('click', () => {
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    });

    // 点击其他地方关闭下拉菜单
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-menu')) {
            dropdownMenu.style.display = 'none';
        }
    });
});