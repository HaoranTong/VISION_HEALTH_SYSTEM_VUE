// 顶部导航栏交互逻辑
document.addEventListener('DOMContentLoaded', () => {
    // 全屏功能
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    fullscreenBtn.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    });

    // 用户菜单
    const userDropdown = new bootstrap.Dropdown(
        document.querySelector('.user-dropdown')
    );
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-dropdown')) userDropdown.hide();
    });
});